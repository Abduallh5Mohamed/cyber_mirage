-- Migration: add honeypot_type + scan flags to attack_sessions
ALTER TABLE attack_sessions
    ADD COLUMN IF NOT EXISTS honeypot_type VARCHAR(50);

ALTER TABLE attack_sessions
    ADD COLUMN IF NOT EXISTS is_scan BOOLEAN DEFAULT FALSE;

ALTER TABLE attack_sessions
    ADD COLUMN IF NOT EXISTS scan_reason TEXT;

CREATE INDEX IF NOT EXISTS idx_sessions_origin ON attack_sessions(origin);
CREATE INDEX IF NOT EXISTS idx_sessions_is_scan ON attack_sessions(is_scan);
