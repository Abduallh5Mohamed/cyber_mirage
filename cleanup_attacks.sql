-- Count attacks from the IP before deletion
SELECT COUNT(*) as attack_count FROM attack_sessions WHERE origin = '197.35.34.115';

-- Delete all attacks from this IP
DELETE FROM attack_sessions WHERE origin = '197.35.34.115';

-- Verify deletion
SELECT COUNT(*) as remaining FROM attack_sessions WHERE origin = '197.35.34.115';

-- Show remaining total attacks
SELECT COUNT(*) as total_attacks FROM attack_sessions;
