-- Frozen PR2 schema snapshot, generated once from reviewed metadata.
CREATE TYPE control_api.user_status AS ENUM ('ACTIVE', 'SUSPENDED');
CREATE TYPE control_api.organization_status AS ENUM ('PENDING_REVIEW', 'ACTIVE', 'SUSPENDED', 'REJECTED');
CREATE TYPE control_api.verification_status AS ENUM ('UNVERIFIED', 'REVIEWED');
CREATE TYPE control_api.organization_role AS ENUM ('ORG_OWNER', 'ORG_ADMIN', 'ORG_MEMBER');
CREATE TYPE control_api.membership_status AS ENUM ('PENDING', 'ACTIVE', 'REVOKED');

CREATE TABLE bff_auth.logout_replays (
	issuer VARCHAR(512) NOT NULL, 
	jti VARCHAR(255) NOT NULL, 
	expires_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_logout_replays PRIMARY KEY (issuer, jti)
)

;

CREATE TABLE bff_auth.oidc_transactions (
	state_hash VARCHAR(64) NOT NULL, 
	browser_hash VARCHAR(64) NOT NULL, 
	encrypted_payload TEXT NOT NULL, 
	expires_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_oidc_transactions PRIMARY KEY (state_hash)
)

;

CREATE TABLE bff_auth.sessions (
	id_hash VARCHAR(64) NOT NULL, 
	user_id UUID NOT NULL, 
	issuer VARCHAR(512) NOT NULL, 
	subject VARCHAR(255) NOT NULL, 
	provider_sid VARCHAR(255), 
	encrypted_access_token TEXT NOT NULL, 
	encrypted_refresh_token TEXT, 
	token_expires_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	last_seen_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	idle_expires_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	absolute_expires_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	revoked_at TIMESTAMP WITH TIME ZONE, 
	encryption_key_id VARCHAR(48) NOT NULL, 
	version BIGINT DEFAULT '1' NOT NULL, 
	CONSTRAINT pk_sessions PRIMARY KEY (id_hash)
)

;
CREATE INDEX ix_sessions_provider_sid ON bff_auth.sessions (issuer, provider_sid);

CREATE TABLE control_api.users (
	id UUID NOT NULL, 
	status control_api.user_status DEFAULT 'ACTIVE' NOT NULL, 
	display_name VARCHAR(120) NOT NULL, 
	email_snapshot VARCHAR(254), 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	version BIGINT DEFAULT '1' NOT NULL, 
	CONSTRAINT pk_users PRIMARY KEY (id), 
	CONSTRAINT ck_users_version CHECK (version > 0)
)

;

CREATE TABLE control_api.idempotency_records (
	user_id UUID NOT NULL, 
	key VARCHAR(128) NOT NULL, 
	request_hash VARCHAR(64) NOT NULL, 
	response JSONB NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_idempotency_records PRIMARY KEY (user_id, key), 
	CONSTRAINT fk_idempotency_records_user_id_users FOREIGN KEY(user_id) REFERENCES control_api.users (id)
)

;

CREATE TABLE control_api.identity_links (
	id UUID NOT NULL, 
	user_id UUID NOT NULL, 
	issuer VARCHAR(512) NOT NULL, 
	subject VARCHAR(255) NOT NULL, 
	linked_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	last_authenticated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_identity_links PRIMARY KEY (id), 
	CONSTRAINT uq_identity_links_issuer_subject UNIQUE (issuer, subject), 
	CONSTRAINT fk_identity_links_user_id_users FOREIGN KEY(user_id) REFERENCES control_api.users (id)
)

;

CREATE TABLE control_api.organizations (
	id UUID NOT NULL, 
	display_name VARCHAR(120) NOT NULL, 
	status control_api.organization_status DEFAULT 'PENDING_REVIEW' NOT NULL, 
	verification_status control_api.verification_status DEFAULT 'UNVERIFIED' NOT NULL, 
	requested_by_user_id UUID NOT NULL, 
	review_reference VARCHAR(120), 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	reviewed_at TIMESTAMP WITH TIME ZONE, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	version BIGINT DEFAULT '1' NOT NULL, 
	CONSTRAINT pk_organizations PRIMARY KEY (id), 
	CONSTRAINT ck_organizations_version CHECK (version > 0), 
	CONSTRAINT fk_organizations_requested_by_user_id_users FOREIGN KEY(requested_by_user_id) REFERENCES control_api.users (id)
)

;

CREATE TABLE control_api.organization_access_events (
	id UUID NOT NULL, 
	organization_id UUID, 
	actor_user_id UUID, 
	operator_reference VARCHAR(120), 
	case_reference VARCHAR(120), 
	kind VARCHAR(48) NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_organization_access_events PRIMARY KEY (id), 
	CONSTRAINT fk_organization_access_events_organization_id_organizations FOREIGN KEY(organization_id) REFERENCES control_api.organizations (id), 
	CONSTRAINT fk_organization_access_events_actor_user_id_users FOREIGN KEY(actor_user_id) REFERENCES control_api.users (id)
)

;

CREATE TABLE control_api.organization_memberships (
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	user_id UUID NOT NULL, 
	role control_api.organization_role NOT NULL, 
	status control_api.membership_status NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	activated_at TIMESTAMP WITH TIME ZONE, 
	revoked_at TIMESTAMP WITH TIME ZONE, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	version BIGINT DEFAULT '1' NOT NULL, 
	granted_by_user_id UUID, 
	CONSTRAINT pk_organization_memberships PRIMARY KEY (id), 
	CONSTRAINT uq_memberships_organization_user UNIQUE (organization_id, user_id), 
	CONSTRAINT ck_organization_memberships_version CHECK (version > 0), 
	CONSTRAINT fk_organization_memberships_organization_id_organizations FOREIGN KEY(organization_id) REFERENCES control_api.organizations (id), 
	CONSTRAINT fk_organization_memberships_user_id_users FOREIGN KEY(user_id) REFERENCES control_api.users (id), 
	CONSTRAINT fk_organization_memberships_granted_by_user_id_users FOREIGN KEY(granted_by_user_id) REFERENCES control_api.users (id)
)

;
CREATE INDEX ix_memberships_user_status ON control_api.organization_memberships (user_id, status);
