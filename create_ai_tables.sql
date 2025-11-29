CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS agent_decisions (
    id UUID PRIMARY KEY,
    session_id UUID,
    action VARCHAR(64),
    strategy VARCHAR(128),
    reward DOUBLE PRECISION,
    state JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS deception_events (
    id UUID PRIMARY KEY,
    session_id UUID,
    action VARCHAR(64),
    parameters JSONB,
    executed BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);
