CREATE OR REPLACE FUNCTION control_api.room_collaboration(rid uuid,scope uuid,iid uuid,action text,
 expected integer,target uuid,request_key text) RETURNS jsonb
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog AS $$
DECLARE owner uuid; item control_api.room_invitations; desired text;
BEGIN
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
