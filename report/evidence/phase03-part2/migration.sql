BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> 0001_sessions

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE anonymous_sessions (
    id VARCHAR(36) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    PRIMARY KEY (id)
);

CREATE INDEX ix_anonymous_sessions_expires_at ON anonymous_sessions (expires_at);

INSERT INTO alembic_version (version_num) VALUES ('0001_sessions') RETURNING alembic_version.version_num;

-- Running upgrade 0001_sessions -> 0002_content

CREATE TABLE reviews (
    id VARCHAR(40) NOT NULL,
    entity_type VARCHAR(30) NOT NULL,
    entity_id VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,
    reviewer VARCHAR(200) NOT NULL,
    reviewed_at TIMESTAMP WITH TIME ZONE NOT NULL,
    notes TEXT NOT NULL,
    content_hash VARCHAR(64) NOT NULL,
    previous_status VARCHAR(20) NOT NULL,
    PRIMARY KEY (id)
);

CREATE INDEX ix_reviews_entity_id ON reviews (entity_id);

CREATE INDEX ix_reviews_entity_type ON reviews (entity_type);

CREATE TABLE exhibits (
    title JSON NOT NULL,
    summary JSON NOT NULL,
    themes JSON NOT NULL,
    estimated_minutes INTEGER NOT NULL,
    id VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,
    review_id VARCHAR(40),
    PRIMARY KEY (id),
    CHECK (estimated_minutes BETWEEN 1 AND 60),
    FOREIGN KEY(review_id) REFERENCES reviews (id)
);

CREATE INDEX ix_exhibits_status ON exhibits (status);

CREATE TABLE regions (
    names JSON NOT NULL,
    approved_geometry_ref TEXT,
    id VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,
    review_id VARCHAR(40),
    PRIMARY KEY (id),
    CHECK (status IN ('draft','approved','rejected','withdrawn')),
    FOREIGN KEY(review_id) REFERENCES reviews (id)
);

CREATE INDEX ix_regions_status ON regions (status);

CREATE TABLE sources (
    institution VARCHAR(200) NOT NULL,
    title TEXT NOT NULL,
    canonical_url TEXT NOT NULL,
    fetched_at TIMESTAMP WITH TIME ZONE NOT NULL,
    external_id VARCHAR(100) NOT NULL,
    raw_hash VARCHAR(64) NOT NULL,
    raw_payload TEXT NOT NULL,
    rights_basis TEXT NOT NULL,
    id VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,
    review_id VARCHAR(40),
    PRIMARY KEY (id),
    FOREIGN KEY(review_id) REFERENCES reviews (id),
    UNIQUE (institution, external_id)
);

CREATE INDEX ix_sources_status ON sources (status);

CREATE TABLE artifacts (
    institution VARCHAR(200) NOT NULL,
    external_object_id VARCHAR(100) NOT NULL,
    source_id VARCHAR(100) NOT NULL,
    catalog_title TEXT NOT NULL,
    catalog_date TEXT NOT NULL,
    medium TEXT NOT NULL,
    origin JSON NOT NULL,
    current_location TEXT NOT NULL,
    id VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,
    review_id VARCHAR(40),
    PRIMARY KEY (id),
    FOREIGN KEY(review_id) REFERENCES reviews (id),
    FOREIGN KEY(source_id) REFERENCES sources (id),
    UNIQUE (institution, external_object_id)
);

CREATE INDEX ix_artifacts_source_id ON artifacts (source_id);

CREATE INDEX ix_artifacts_status ON artifacts (status);

CREATE TABLE claims (
    exhibit_id VARCHAR(100) NOT NULL,
    text TEXT NOT NULL,
    id VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,
    review_id VARCHAR(40),
    PRIMARY KEY (id),
    FOREIGN KEY(exhibit_id) REFERENCES exhibits (id),
    FOREIGN KEY(review_id) REFERENCES reviews (id)
);

CREATE INDEX ix_claims_exhibit_id ON claims (exhibit_id);

CREATE INDEX ix_claims_status ON claims (status);

CREATE TABLE exhibit_regions (
    exhibit_id VARCHAR(100) NOT NULL,
    region_id VARCHAR(100) NOT NULL,
    geographic_role VARCHAR(20) NOT NULL,
    PRIMARY KEY (exhibit_id, region_id),
    CHECK (geographic_role IN ('practice','origin','context')),
    FOREIGN KEY(exhibit_id) REFERENCES exhibits (id),
    FOREIGN KEY(region_id) REFERENCES regions (id)
);

CREATE TABLE passages (
    source_id VARCHAR(100) NOT NULL,
    text TEXT NOT NULL,
    language VARCHAR(8) NOT NULL,
    locator TEXT NOT NULL,
    rights_basis TEXT NOT NULL,
    rights_status VARCHAR(20) NOT NULL,
    embedding_version VARCHAR(100),
    id VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,
    review_id VARCHAR(40),
    PRIMARY KEY (id),
    FOREIGN KEY(review_id) REFERENCES reviews (id),
    FOREIGN KEY(source_id) REFERENCES sources (id)
);

CREATE INDEX ix_passages_source_id ON passages (source_id);

CREATE INDEX ix_passages_status ON passages (status);

CREATE TABLE artifact_exhibits (
    artifact_id VARCHAR(100) NOT NULL,
    exhibit_id VARCHAR(100) NOT NULL,
    evidence_passage_id VARCHAR(100) NOT NULL,
    PRIMARY KEY (artifact_id, exhibit_id, evidence_passage_id),
    FOREIGN KEY(artifact_id) REFERENCES artifacts (id),
    FOREIGN KEY(evidence_passage_id) REFERENCES passages (id),
    FOREIGN KEY(exhibit_id) REFERENCES exhibits (id)
);

CREATE TABLE claim_evidence (
    claim_id VARCHAR(100) NOT NULL,
    passage_id VARCHAR(100) NOT NULL,
    PRIMARY KEY (claim_id, passage_id),
    FOREIGN KEY(claim_id) REFERENCES claims (id),
    FOREIGN KEY(passage_id) REFERENCES passages (id)
);

CREATE TABLE media (
    source_id VARCHAR(100) NOT NULL,
    artifact_id VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL,
    url TEXT NOT NULL,
    hash VARCHAR(64),
    storage_key TEXT,
    rights_code VARCHAR(30) NOT NULL,
    rights_status VARCHAR(20) NOT NULL,
    rights_evidence JSON NOT NULL,
    id VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,
    review_id VARCHAR(40),
    PRIMARY KEY (id),
    FOREIGN KEY(artifact_id) REFERENCES artifacts (id),
    FOREIGN KEY(review_id) REFERENCES reviews (id),
    FOREIGN KEY(source_id) REFERENCES sources (id),
    UNIQUE (source_id, url)
);

CREATE INDEX ix_media_artifact_id ON media (artifact_id);

CREATE INDEX ix_media_source_id ON media (source_id);

CREATE INDEX ix_media_status ON media (status);

UPDATE alembic_version SET version_num='0002_content' WHERE alembic_version.version_num = '0001_sessions';

-- Running upgrade 0002_content -> 0003_gateway

CREATE TABLE gateway_lock (
    id SERIAL NOT NULL,
    PRIMARY KEY (id),
    CHECK (id = 1)
);

INSERT INTO gateway_lock (id) VALUES (1);

CREATE TABLE gateway_budgets (
    day VARCHAR(10) NOT NULL,
    charged_nano_usd BIGINT NOT NULL,
    PRIMARY KEY (day),
    CHECK (charged_nano_usd >= 0)
);

CREATE TABLE gateway_attempts (
    id VARCHAR(40) NOT NULL,
    day VARCHAR(10) NOT NULL,
    actor_hash VARCHAR(64),
    started_at FLOAT NOT NULL,
    lease_until FLOAT NOT NULL,
    model VARCHAR(40) NOT NULL,
    status VARCHAR(24) NOT NULL,
    charged_nano_usd BIGINT NOT NULL,
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    latency_ms INTEGER,
    PRIMARY KEY (id)
);

CREATE INDEX ix_gateway_attempts_day ON gateway_attempts (day);

CREATE INDEX ix_gateway_attempts_actor_hash ON gateway_attempts (actor_hash);

CREATE INDEX ix_gateway_attempts_started_at ON gateway_attempts (started_at);

UPDATE alembic_version SET version_num='0003_gateway' WHERE alembic_version.version_num = '0002_content';

COMMIT;
