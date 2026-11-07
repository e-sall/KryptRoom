-- Application role is never owner, superuser or BYPASSRLS. No public functions.
GRANT CREATE ON SCHEMA control_api TO kryptroom_auth_guard;
REVOKE ALL ON ALL TABLES IN SCHEMA control_api FROM kryptroom_app;
GRANT SELECT ON control_api.alembic_version, control_api.foundation_metadata TO kryptroom_app;
REVOKE ALL ON SCHEMA bff_auth FROM PUBLIC;
REVOKE ALL ON ALL TABLES IN SCHEMA bff_auth FROM PUBLIC, kryptroom_app, kryptroom_operator;
GRANT USAGE ON SCHEMA bff_auth TO kryptroom_bff;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA bff_auth TO kryptroom_bff;
GRANT USAGE ON SCHEMA control_api TO kryptroom_operator;
GRANT SELECT ON control_api.users, control_api.identity_links, control_api.organizations,
    control_api.organization_memberships TO kryptroom_auth_guard;
GRANT INSERT, UPDATE ON control_api.users, control_api.identity_links TO kryptroom_auth_guard;

CREATE FUNCTION control_api.current_actor() RETURNS uuid
LANGUAGE sql STABLE SET search_path = pg_catalog AS $$
    SELECT nullif(current_setting('kryptroom.user_id', true), '')::uuid
$$;
REVOKE ALL ON FUNCTION control_api.current_actor() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION control_api.current_actor()
    TO kryptroom_app, kryptroom_operator, kryptroom_auth_guard;

-- Small, non-recursive membership predicate. Guard cannot log in and has only
-- the listed SELECT privileges; it is not a general-purpose query endpoint.
CREATE FUNCTION control_api.active_role(target uuid) RETURNS text
LANGUAGE sql STABLE SECURITY DEFINER SET search_path = pg_catalog AS $$
    SELECT m.role::text FROM control_api.organization_memberships m
    JOIN control_api.users u ON u.id=m.user_id
    JOIN control_api.organizations o ON o.id=m.organization_id
    WHERE m.organization_id=target AND m.user_id=control_api.current_actor()
      AND m.status='ACTIVE' AND u.status='ACTIVE' AND o.status='ACTIVE'
$$;
ALTER FUNCTION control_api.active_role(uuid) OWNER TO kryptroom_auth_guard;
REVOKE ALL ON FUNCTION control_api.active_role(uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION control_api.active_role(uuid) TO kryptroom_app;
CREATE FUNCTION control_api.active_owner_count(target uuid, excluded uuid) RETURNS bigint
LANGUAGE sql STABLE SECURITY DEFINER SET search_path = pg_catalog AS $$
    SELECT count(*) FROM control_api.organization_memberships m
    JOIN control_api.users u ON u.id=m.user_id
    WHERE m.organization_id=target AND m.role='ORG_OWNER' AND m.status='ACTIVE'
      AND m.user_id<>excluded
      AND u.status='ACTIVE' AND control_api.active_role(target)='ORG_OWNER'
$$;
ALTER FUNCTION control_api.active_owner_count(uuid,uuid) OWNER TO kryptroom_auth_guard;
REVOKE ALL ON FUNCTION control_api.active_owner_count(uuid,uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION control_api.active_owner_count(uuid,uuid) TO kryptroom_app;

CREATE FUNCTION control_api.resolve_identity(uid uuid, lid uuid, iss text, sub text,
    label text, email text) RETURNS uuid
LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog AS $$
DECLARE found_user uuid;
BEGIN
    IF length(iss) NOT BETWEEN 1 AND 512 OR length(sub) NOT BETWEEN 1 AND 255
       OR length(label)>120 OR length(email)>254 THEN
        RAISE EXCEPTION 'Invalid identity metadata';
    END IF;
    PERFORM pg_advisory_xact_lock(hashtextextended(iss || ':' || sub, 0));
    SELECT user_id INTO found_user FROM control_api.identity_links
        WHERE issuer=iss AND subject=sub;
    IF found_user IS NULL THEN
        INSERT INTO control_api.users(id,display_name,email_snapshot) VALUES(uid,label,email);
        INSERT INTO control_api.identity_links(id,user_id,issuer,subject) VALUES(lid,uid,iss,sub);
        found_user := uid;
    ELSE
        UPDATE control_api.identity_links SET last_authenticated_at=now()
            WHERE issuer=iss AND subject=sub;
        UPDATE control_api.users SET display_name=label,email_snapshot=email,updated_at=now(),
            version=version+1 WHERE id=found_user;
    END IF;
    RETURN found_user;
END $$;
ALTER FUNCTION control_api.resolve_identity(uuid,uuid,text,text,text,text)
    OWNER TO kryptroom_auth_guard;
REVOKE ALL ON FUNCTION control_api.resolve_identity(uuid,uuid,text,text,text,text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION control_api.resolve_identity(uuid,uuid,text,text,text,text) TO kryptroom_app;
CREATE FUNCTION control_api.lookup_identity(iss text, sub text) RETURNS uuid
LANGUAGE sql STABLE SECURITY DEFINER SET search_path = pg_catalog AS $$
    SELECT user_id FROM control_api.identity_links WHERE issuer=iss AND subject=sub
$$;
ALTER FUNCTION control_api.lookup_identity(text,text) OWNER TO kryptroom_auth_guard;
REVOKE ALL ON FUNCTION control_api.lookup_identity(text,text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION control_api.lookup_identity(text,text) TO kryptroom_app;
CREATE FUNCTION control_api.lock_current_user() RETURNS boolean
LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog AS $$
DECLARE active boolean;
BEGIN
    SELECT status='ACTIVE' INTO active FROM control_api.users
        WHERE id=control_api.current_actor() FOR SHARE;
    RETURN coalesce(active, false);
END $$;
ALTER FUNCTION control_api.lock_current_user() OWNER TO kryptroom_auth_guard;
REVOKE ALL ON FUNCTION control_api.lock_current_user() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION control_api.lock_current_user() TO kryptroom_app;

ALTER TABLE control_api.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE control_api.users FORCE ROW LEVEL SECURITY;
CREATE POLICY own_user ON control_api.users FOR SELECT TO kryptroom_app
    USING (id=control_api.current_actor());
CREATE POLICY operator_users ON control_api.users TO kryptroom_operator USING (true) WITH CHECK (true);
GRANT SELECT ON control_api.users TO kryptroom_app, kryptroom_operator;
GRANT UPDATE(status,updated_at,version) ON control_api.users TO kryptroom_operator;

ALTER TABLE control_api.identity_links ENABLE ROW LEVEL SECURITY;
ALTER TABLE control_api.identity_links FORCE ROW LEVEL SECURITY;
CREATE POLICY own_link ON control_api.identity_links FOR SELECT TO kryptroom_app
    USING (user_id=control_api.current_actor());
CREATE POLICY operator_links ON control_api.identity_links FOR SELECT TO kryptroom_operator USING (true);
GRANT SELECT ON control_api.identity_links TO kryptroom_app, kryptroom_operator;

ALTER TABLE control_api.organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE control_api.organizations FORCE ROW LEVEL SECURITY;
CREATE POLICY org_select ON control_api.organizations FOR SELECT TO kryptroom_app
    USING (control_api.active_role(id) IS NOT NULL OR requested_by_user_id=control_api.current_actor());
CREATE POLICY org_register ON control_api.organizations FOR INSERT TO kryptroom_app
    WITH CHECK (requested_by_user_id=control_api.current_actor() AND status='PENDING_REVIEW'
        AND verification_status='UNVERIFIED' AND review_reference IS NULL AND reviewed_at IS NULL);
CREATE POLICY org_update ON control_api.organizations FOR UPDATE TO kryptroom_app
    USING (control_api.active_role(id) IN ('ORG_OWNER','ORG_ADMIN'))
    WITH CHECK (control_api.active_role(id) IN ('ORG_OWNER','ORG_ADMIN'));
CREATE POLICY operator_org ON control_api.organizations TO kryptroom_operator USING (true) WITH CHECK (true);
GRANT SELECT, INSERT ON control_api.organizations TO kryptroom_app;
GRANT UPDATE(display_name,updated_at,version) ON control_api.organizations TO kryptroom_app;
GRANT SELECT ON control_api.organizations TO kryptroom_operator;
GRANT UPDATE(status,verification_status,review_reference,reviewed_at,updated_at,version)
    ON control_api.organizations TO kryptroom_operator;

ALTER TABLE control_api.organization_memberships ENABLE ROW LEVEL SECURITY;
ALTER TABLE control_api.organization_memberships FORCE ROW LEVEL SECURITY;
CREATE POLICY member_select ON control_api.organization_memberships FOR SELECT TO kryptroom_app
    USING (user_id=control_api.current_actor()
       OR control_api.active_role(organization_id) IN ('ORG_OWNER','ORG_ADMIN'));
CREATE POLICY member_register ON control_api.organization_memberships FOR INSERT TO kryptroom_app
    WITH CHECK (user_id=control_api.current_actor() AND role='ORG_OWNER' AND status='PENDING'
      AND EXISTS (SELECT 1 FROM control_api.organizations o WHERE o.id=organization_id
        AND o.status='PENDING_REVIEW' AND o.requested_by_user_id=control_api.current_actor()));
CREATE POLICY member_update ON control_api.organization_memberships FOR UPDATE TO kryptroom_app
    USING (control_api.active_role(organization_id)='ORG_OWNER'
        OR (control_api.active_role(organization_id)='ORG_ADMIN' AND role='ORG_MEMBER'))
    WITH CHECK (control_api.active_role(organization_id)='ORG_OWNER'
        OR (control_api.active_role(organization_id)='ORG_ADMIN' AND role='ORG_MEMBER'));
CREATE POLICY operator_member ON control_api.organization_memberships TO kryptroom_operator
    USING (true) WITH CHECK (true);
GRANT SELECT, INSERT ON control_api.organization_memberships TO kryptroom_app;
GRANT UPDATE(role,status,revoked_at,updated_at,version) ON control_api.organization_memberships TO kryptroom_app;
GRANT SELECT, INSERT ON control_api.organization_memberships TO kryptroom_operator;
GRANT UPDATE(status,activated_at,updated_at,version)
    ON control_api.organization_memberships TO kryptroom_operator;

ALTER TABLE control_api.idempotency_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE control_api.idempotency_records FORCE ROW LEVEL SECURITY;
CREATE POLICY own_idempotency ON control_api.idempotency_records TO kryptroom_app
    USING (user_id=control_api.current_actor()) WITH CHECK (user_id=control_api.current_actor());
GRANT SELECT, INSERT ON control_api.idempotency_records TO kryptroom_app;
ALTER TABLE control_api.organization_access_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE control_api.organization_access_events FORCE ROW LEVEL SECURITY;
CREATE POLICY event_append ON control_api.organization_access_events FOR INSERT TO kryptroom_app
    WITH CHECK (actor_user_id=control_api.current_actor() AND operator_reference IS NULL
        AND case_reference IS NULL);
CREATE POLICY operator_event ON control_api.organization_access_events FOR INSERT TO kryptroom_operator
    WITH CHECK (length(operator_reference)>0 AND length(case_reference)>0);
GRANT INSERT ON control_api.organization_access_events TO kryptroom_app, kryptroom_operator;
-- No UPDATE or DELETE grants on security events. Not cryptographic evidence.
REVOKE CREATE ON SCHEMA control_api FROM kryptroom_auth_guard;
