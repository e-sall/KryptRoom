CREATE TABLE control_api.rooms (
    id uuid PRIMARY KEY,
    organization_id uuid NOT NULL REFERENCES control_api.organizations(id),
    created_by_user_id uuid NOT NULL REFERENCES control_api.users(id),
    display_name varchar(120) NOT NULL CHECK (length(btrim(display_name)) BETWEEN 1 AND 120),
    description varchar(1000) NOT NULL DEFAULT '',
    status varchar(16) NOT NULL DEFAULT 'DRAFT' CHECK (status='DRAFT'),
    head_state_id uuid CHECK (head_state_id IS NULL),
    version integer NOT NULL DEFAULT 1 CHECK (version>0),
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX rooms_organization_page ON control_api.rooms(organization_id,id);
CREATE TABLE control_api.room_creation_requests (
    user_id uuid NOT NULL REFERENCES control_api.users(id),
    organization_id uuid NOT NULL REFERENCES control_api.organizations(id),
    key varchar(128) NOT NULL CHECK (length(btrim(key)) BETWEEN 1 AND 128),
    request_hash varchar(64) NOT NULL CHECK (request_hash ~ '^[0-9a-f]{64}$'),
    response jsonb NOT NULL,
    PRIMARY KEY(user_id,organization_id,key)
);
-- Override migrator default SELECT grants before these tables become visible.
REVOKE ALL ON control_api.rooms, control_api.room_creation_requests FROM PUBLIC,
    kryptroom_app, kryptroom_operator, kryptroom_bff, kryptroom_auth_guard;
ALTER TABLE control_api.rooms ENABLE ROW LEVEL SECURITY;
ALTER TABLE control_api.rooms FORCE ROW LEVEL SECURITY;
CREATE POLICY room_read ON control_api.rooms FOR SELECT TO kryptroom_app
    USING (control_api.active_role(organization_id) IS NOT NULL);
CREATE POLICY room_create ON control_api.rooms FOR INSERT TO kryptroom_app
    WITH CHECK (control_api.active_role(organization_id) IN ('ORG_OWNER','ORG_ADMIN')
        AND created_by_user_id=control_api.current_actor() AND status='DRAFT'
        AND version=1 AND head_state_id IS NULL);
CREATE POLICY room_update ON control_api.rooms FOR UPDATE TO kryptroom_app
    USING (control_api.active_role(organization_id) IN ('ORG_OWNER','ORG_ADMIN'))
    WITH CHECK (control_api.active_role(organization_id) IN ('ORG_OWNER','ORG_ADMIN'));
GRANT SELECT ON control_api.rooms TO kryptroom_app;
GRANT INSERT(id,organization_id,created_by_user_id,display_name,description)
    ON control_api.rooms TO kryptroom_app;
GRANT UPDATE(display_name,description,version,updated_at) ON control_api.rooms TO kryptroom_app;
ALTER TABLE control_api.room_creation_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE control_api.room_creation_requests FORCE ROW LEVEL SECURITY;
CREATE POLICY room_request_read ON control_api.room_creation_requests FOR SELECT TO kryptroom_app
    USING (user_id=control_api.current_actor()
        AND control_api.active_role(organization_id) IN ('ORG_OWNER','ORG_ADMIN'));
CREATE POLICY room_request_create ON control_api.room_creation_requests FOR INSERT TO kryptroom_app
    WITH CHECK (user_id=control_api.current_actor()
        AND control_api.active_role(organization_id) IN ('ORG_OWNER','ORG_ADMIN'));
GRANT SELECT, INSERT ON control_api.room_creation_requests TO kryptroom_app;
