-- PostgreSQL initialization script
-- Creates tables for Cyber Mirage

-- Create extension for UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Attack sessions table
CREATE TABLE IF NOT EXISTS attack_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    attacker_name VARCHAR(100) NOT NULL,
    attacker_skill FLOAT NOT NULL,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    total_steps INTEGER,
    total_reward FLOAT,
    detected BOOLEAN,
    data_collected FLOAT,
    final_suspicion FLOAT,
    mitre_tactics TEXT[],
    zero_days_used INTEGER,
    origin VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Attack actions table
CREATE TABLE IF NOT EXISTS attack_actions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES attack_sessions(id) ON DELETE CASCADE,
    step_number INTEGER NOT NULL,
    action_id INTEGER NOT NULL,
    reward FLOAT,
    suspicion FLOAT,
    data_collected FLOAT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- System metrics table
CREATE TABLE IF NOT EXISTS system_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name VARCHAR(100) NOT NULL,
    metric_value FLOAT NOT NULL,
    labels JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- API requests table
CREATE TABLE IF NOT EXISTS api_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    endpoint VARCHAR(200),
    method VARCHAR(10),
    status_code INTEGER,
    duration_ms FLOAT,
    client_ip VARCHAR(45),
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_sessions_attacker ON attack_sessions(attacker_name);
CREATE INDEX idx_sessions_start ON attack_sessions(start_time);
CREATE INDEX idx_actions_session ON attack_actions(session_id);
CREATE INDEX idx_metrics_name ON system_metrics(metric_name);
CREATE INDEX idx_metrics_timestamp ON system_metrics(timestamp);
CREATE INDEX idx_requests_endpoint ON api_requests(endpoint);
CREATE INDEX idx_requests_timestamp ON api_requests(timestamp);

-- Create views for analytics
CREATE OR REPLACE VIEW attack_statistics AS
SELECT 
    attacker_name,
    COUNT(*) as total_attacks,
    AVG(attacker_skill) as avg_skill,
    AVG(total_steps) as avg_steps,
    AVG(total_reward) as avg_reward,
    SUM(CASE WHEN detected THEN 1 ELSE 0 END) as times_detected,
    AVG(data_collected) as avg_data_collected
FROM attack_sessions
GROUP BY attacker_name
ORDER BY avg_reward DESC;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO honeypot;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO honeypot;
