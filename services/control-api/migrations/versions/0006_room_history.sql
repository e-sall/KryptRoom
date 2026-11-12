GRANT CREATE ON SCHEMA control_api TO kryptroom_auth_guard;
CREATE TABLE control_api.room_operational_events (
 id uuid PRIMARY KEY,
 room_id uuid NOT NULL REFERENCES control_api.rooms(id),
 actor_org uuid NOT NULL REFERENCES control_api.organizations(id),
 actor_user_id uuid NOT NULL REFERENCES control_api.users(id),
 invitation_id uuid REFERENCES control_api.room_invitations(id),
 kind text NOT NULL CHECK(kind IN ('room_created','room_metadata_updated',
   'invitation_invite','invitation_accept','invitation_reject','invitation_leave','invitation_revoke')),
 created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX room_operational_page ON control_api.room_operational_events(room_id,created_at,id);
REVOKE ALL ON control_api.room_operational_events FROM PUBLIC,kryptroom_app,
 kryptroom_operator,kryptroom_bff,kryptroom_auth_guard;
ALTER TABLE control_api.room_operational_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE control_api.room_operational_events FORCE ROW LEVEL SECURITY;
GRANT SELECT,INSERT ON control_api.room_operational_events TO kryptroom_auth_guard;
-- Preserve original IDs and times; do not invent historical Room create/update events.
SET LOCAL ROLE kryptroom_auth_guard;
INSERT INTO control_api.room_operational_events
 SELECT e.id,i.room_id,e.actor_org,e.actor_id,i.id,'invitation_'||e.kind,e.created_at
 FROM control_api.room_collaboration_events e
 JOIN control_api.room_invitations i ON i.id=e.invitation_id;
RESET ROLE;
CREATE FUNCTION control_api.append_room_history() RETURNS trigger
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog AS $$
DECLARE rid uuid; oid uuid; uid uuid; iid uuid; event_id uuid; event_kind text; event_time timestamptz;
BEGIN
 IF TG_TABLE_NAME='rooms' THEN
   rid:=NEW.id; oid:=NEW.organization_id; uid:=control_api.current_actor();
   event_id:=gen_random_uuid(); event_time:=clock_timestamp();
   event_kind:=CASE TG_OP WHEN 'INSERT' THEN 'room_created' ELSE 'room_metadata_updated' END;
 ELSE
   SELECT room_id INTO rid FROM control_api.room_invitations WHERE id=NEW.invitation_id;
   oid:=NEW.actor_org; uid:=NEW.actor_id; iid:=NEW.invitation_id;
   event_id:=NEW.id; event_kind:='invitation_'||NEW.kind; event_time:=clock_timestamp();
 END IF;
 INSERT INTO control_api.room_operational_events
 VALUES(event_id,rid,oid,uid,iid,event_kind,event_time);
 RETURN NEW;
END $$;
ALTER FUNCTION control_api.append_room_history() OWNER TO kryptroom_auth_guard;
REVOKE ALL ON FUNCTION control_api.append_room_history() FROM PUBLIC,kryptroom_app,
 kryptroom_operator,kryptroom_bff;
CREATE TRIGGER room_history_append AFTER INSERT OR UPDATE ON control_api.rooms
 FOR EACH ROW EXECUTE FUNCTION control_api.append_room_history();
CREATE TRIGGER collaboration_history_append AFTER INSERT ON control_api.room_collaboration_events
 FOR EACH ROW EXECUTE FUNCTION control_api.append_room_history();
CREATE FUNCTION control_api.room_history(rid uuid,after_id uuid,page_size integer)
RETURNS TABLE(id uuid,kind text,actor_organization_id uuid,created_at timestamptz)
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog AS $$
DECLARE owner uuid; own_manager boolean; partner_invitation uuid; accepted_at timestamptz;
 cursor_time timestamptz;
BEGIN
 IF page_size IS NULL OR page_size NOT BETWEEN 1 AND 101 THEN
   RAISE EXCEPTION 'invalid_page' USING ERRCODE='22023'; END IF;
 SELECT organization_id INTO owner FROM control_api.rooms WHERE rooms.id=rid;
 own_manager:=coalesce(control_api.active_role(owner) IN ('ORG_OWNER','ORG_ADMIN'),false);
 IF NOT own_manager THEN
   SELECT i.id,min(e.created_at) INTO partner_invitation,accepted_at
   FROM control_api.room_invitations i JOIN control_api.room_operational_events e
     ON e.invitation_id=i.id AND e.kind='invitation_accept'
   WHERE i.room_id=rid AND i.status='ACCEPTED'
     AND control_api.active_role(i.target_id) IN ('ORG_OWNER','ORG_ADMIN')
   GROUP BY i.id;
 END IF;
 IF NOT coalesce(control_api.room_access(rid),false)
    OR (NOT own_manager AND partner_invitation IS NULL) THEN
   RAISE EXCEPTION 'permission_denied' USING ERRCODE='42501'; END IF;
 IF after_id IS NOT NULL THEN
   SELECT h.created_at INTO cursor_time FROM control_api.room_operational_events h
   WHERE h.id=after_id AND h.room_id=rid AND (own_manager OR (h.created_at>=accepted_at
     AND (h.invitation_id IS NULL OR h.invitation_id=partner_invitation)));
   IF NOT FOUND THEN RAISE EXCEPTION 'invalid_page' USING ERRCODE='22023'; END IF;
 END IF;
 RETURN QUERY SELECT h.id,h.kind,h.actor_org,h.created_at
 FROM control_api.room_operational_events h
 WHERE h.room_id=rid AND (after_id IS NULL OR (h.created_at,h.id)>(cursor_time,after_id))
   AND (own_manager OR (h.created_at>=accepted_at
       AND (h.invitation_id IS NULL OR h.invitation_id=partner_invitation)))
 ORDER BY h.created_at,h.id LIMIT page_size;
END $$;
ALTER FUNCTION control_api.room_history(uuid,uuid,integer) OWNER TO kryptroom_auth_guard;
REVOKE ALL ON FUNCTION control_api.room_history(uuid,uuid,integer) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION control_api.room_history(uuid,uuid,integer) TO kryptroom_app;
REVOKE CREATE ON SCHEMA control_api FROM kryptroom_auth_guard;
