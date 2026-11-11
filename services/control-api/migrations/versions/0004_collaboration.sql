-- Temporary ownership transfer capability, removed in the same transaction.
GRANT CREATE ON SCHEMA control_api TO kryptroom_auth_guard;
CREATE TABLE control_api.room_invitations (
 id uuid PRIMARY KEY, room_id uuid NOT NULL REFERENCES control_api.rooms(id),
 owner_id uuid NOT NULL REFERENCES control_api.organizations(id),
 target_id uuid NOT NULL REFERENCES control_api.organizations(id),
 actor_id uuid NOT NULL REFERENCES control_api.users(id), request_key varchar(128) NOT NULL,
 status text NOT NULL CHECK(status IN ('PENDING','ACCEPTED','REJECTED','REVOKED','LEFT')),
 version integer NOT NULL DEFAULT 1 CHECK(version>0),
 CHECK(owner_id<>target_id), CONSTRAINT room_request_unique UNIQUE(room_id,actor_id,request_key)
);
CREATE UNIQUE INDEX room_one_partner ON control_api.room_invitations(room_id)
 WHERE status IN ('PENDING','ACCEPTED');
CREATE TABLE control_api.room_collaboration_events (
 id uuid PRIMARY KEY, invitation_id uuid NOT NULL REFERENCES control_api.room_invitations(id),
 actor_id uuid NOT NULL REFERENCES control_api.users(id), actor_org uuid NOT NULL,
 kind text NOT NULL, created_at timestamptz NOT NULL DEFAULT now()
);
REVOKE ALL ON control_api.room_invitations,control_api.room_collaboration_events
 FROM PUBLIC,kryptroom_app,kryptroom_operator,kryptroom_bff;
GRANT SELECT,INSERT,UPDATE ON control_api.room_invitations TO kryptroom_auth_guard;
GRANT SELECT,INSERT ON control_api.room_collaboration_events TO kryptroom_auth_guard;
GRANT SELECT,UPDATE(id) ON control_api.rooms TO kryptroom_auth_guard;
ALTER TABLE control_api.room_invitations ENABLE ROW LEVEL SECURITY;
ALTER TABLE control_api.room_invitations FORCE ROW LEVEL SECURITY;
ALTER TABLE control_api.room_collaboration_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE control_api.room_collaboration_events FORCE ROW LEVEL SECURITY;
CREATE POLICY invitation_read ON control_api.room_invitations FOR SELECT TO kryptroom_app
 USING (control_api.active_role(owner_id) IN ('ORG_OWNER','ORG_ADMIN')
     OR control_api.active_role(target_id) IN ('ORG_OWNER','ORG_ADMIN'));
GRANT SELECT ON control_api.room_invitations TO kryptroom_app;
-- No direct app writes, no public execution, no participant-data access.
CREATE FUNCTION control_api.room_access(rid uuid) RETURNS boolean
LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog AS $$
 SELECT EXISTS(SELECT 1 FROM control_api.rooms r
 JOIN control_api.organizations o ON o.id=r.organization_id AND o.status='ACTIVE'
 WHERE r.id=rid AND (control_api.active_role(r.organization_id) IS NOT NULL
 OR EXISTS(SELECT 1 FROM control_api.room_invitations i
 WHERE i.room_id=rid AND i.status='ACCEPTED' AND control_api.active_role(i.target_id) IS NOT NULL)))
$$;
ALTER FUNCTION control_api.room_access(uuid) OWNER TO kryptroom_auth_guard;
REVOKE ALL ON FUNCTION control_api.room_access(uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION control_api.room_access(uuid) TO kryptroom_app;
CREATE FUNCTION control_api.shared_room_ids(oid uuid) RETURNS SETOF uuid
LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog AS $$
 SELECT i.room_id FROM control_api.room_invitations i WHERE i.target_id=oid
 AND i.status='ACCEPTED' AND control_api.active_role(oid) IS NOT NULL
 AND control_api.room_access(i.room_id)
$$;
ALTER FUNCTION control_api.shared_room_ids(uuid) OWNER TO kryptroom_auth_guard;
REVOKE ALL ON FUNCTION control_api.shared_room_ids(uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION control_api.shared_room_ids(uuid) TO kryptroom_app;
CREATE FUNCTION control_api.room_participants(rid uuid) RETURNS SETOF uuid
LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog AS $$
 SELECT i.target_id FROM control_api.room_invitations i WHERE i.room_id=rid
 AND i.status='ACCEPTED' AND control_api.room_access(rid)
$$;
ALTER FUNCTION control_api.room_participants(uuid) OWNER TO kryptroom_auth_guard;
REVOKE ALL ON FUNCTION control_api.room_participants(uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION control_api.room_participants(uuid) TO kryptroom_app;
DROP POLICY room_read ON control_api.rooms;
CREATE POLICY room_read ON control_api.rooms FOR SELECT TO kryptroom_app
 USING(control_api.active_role(organization_id) IS NOT NULL OR control_api.room_access(id));
CREATE FUNCTION control_api.room_collaboration(rid uuid,scope uuid,iid uuid,action text,
 expected integer,target uuid,request_key text) RETURNS jsonb
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog AS $$
DECLARE owner uuid; item control_api.room_invitations; desired text;
BEGIN
 IF action IS NULL OR action NOT IN ('invite','accept','reject','leave','revoke') THEN
   RAISE EXCEPTION 'invalid_action' USING ERRCODE='22023';
 END IF;
 IF control_api.active_role(scope) NOT IN ('ORG_OWNER','ORG_ADMIN')
    OR control_api.active_role(scope) IS NULL THEN RAISE EXCEPTION 'permission_denied' USING ERRCODE='42501'; END IF;
 SELECT organization_id INTO owner FROM control_api.rooms WHERE id=rid FOR UPDATE;
 IF owner IS NULL THEN RAISE EXCEPTION 'resource_not_found' USING ERRCODE='P0002'; END IF;
 -- Recheck live organization state after a potentially blocking room lock.
 IF NOT coalesce(control_api.active_role(scope) IN ('ORG_OWNER','ORG_ADMIN'),false)
 OR NOT EXISTS(SELECT 1 FROM control_api.organizations WHERE id=owner AND status='ACTIVE')
 THEN RAISE EXCEPTION 'resource_not_found' USING ERRCODE='P0002'; END IF;
 IF action='invite' THEN
   IF owner<>scope THEN RAISE EXCEPTION 'resource_not_found' USING ERRCODE='P0002'; END IF;
   IF request_key IS NULL OR length(btrim(request_key)) NOT BETWEEN 1 AND 128 THEN
     RAISE EXCEPTION 'invalid_idempotency_key' USING ERRCODE='22023'; END IF;
   SELECT * INTO item FROM control_api.room_invitations i
     WHERE i.room_id=rid AND i.actor_id=control_api.current_actor() AND i.request_key=room_collaboration.request_key;
   IF FOUND THEN
     IF item.target_id<>target THEN RAISE EXCEPTION 'idempotency_conflict' USING ERRCODE='23505'; END IF;
     RETURN to_jsonb(item);
   END IF;
   IF target=owner OR NOT EXISTS(SELECT 1 FROM control_api.organizations WHERE id=target AND status='ACTIVE')
     THEN RAISE EXCEPTION 'target_unavailable' USING ERRCODE='22023'; END IF;
   INSERT INTO control_api.room_invitations VALUES(iid,rid,owner,target,control_api.current_actor(),request_key,'PENDING',1)
     RETURNING * INTO item;
 ELSE
   SELECT * INTO item FROM control_api.room_invitations WHERE id=iid AND room_id=rid FOR UPDATE;
   IF NOT FOUND OR (action='revoke' AND scope<>owner)
      OR (action IN ('accept','reject','leave') AND scope<>item.target_id)
      OR action NOT IN ('accept','reject','leave','revoke') THEN
     RAISE EXCEPTION 'resource_not_found' USING ERRCODE='P0002'; END IF;
   desired:=CASE action WHEN 'accept' THEN 'ACCEPTED' WHEN 'reject' THEN 'REJECTED'
     WHEN 'leave' THEN 'LEFT' ELSE 'REVOKED' END;
   IF expected IS NULL THEN RAISE EXCEPTION 'precondition_required' USING ERRCODE='22023'; END IF;
   IF item.status=desired THEN RETURN to_jsonb(item); END IF;
   IF item.version<>expected THEN RAISE EXCEPTION 'precondition_failed' USING ERRCODE='40001'; END IF;
   IF (action IN ('accept','reject') AND item.status<>'PENDING')
      OR (action='leave' AND item.status<>'ACCEPTED')
      OR (action='revoke' AND item.status NOT IN ('PENDING','ACCEPTED')) THEN
     RAISE EXCEPTION 'transition_conflict' USING ERRCODE='23505'; END IF;
   UPDATE control_api.room_invitations SET status=desired,version=version+1 WHERE id=iid RETURNING * INTO item;
 END IF;
 INSERT INTO control_api.room_collaboration_events VALUES(gen_random_uuid(),item.id,control_api.current_actor(),scope,action,now());
 RETURN to_jsonb(item);
END $$;
ALTER FUNCTION control_api.room_collaboration(uuid,uuid,uuid,text,integer,uuid,text) OWNER TO kryptroom_auth_guard;
REVOKE ALL ON FUNCTION control_api.room_collaboration(uuid,uuid,uuid,text,integer,uuid,text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION control_api.room_collaboration(uuid,uuid,uuid,text,integer,uuid,text) TO kryptroom_app;
REVOKE CREATE ON SCHEMA control_api FROM kryptroom_auth_guard;
