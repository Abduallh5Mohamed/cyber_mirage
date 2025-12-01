-- Delete ALL attack data to start fresh
DELETE FROM attack_actions;
DELETE FROM agent_decisions;
DELETE FROM attack_sessions;
DELETE FROM deception_events;

-- Verify deletion
SELECT 'attack_sessions' as table_name, COUNT(*) as remaining FROM attack_sessions
UNION ALL
SELECT 'agent_decisions', COUNT(*) FROM agent_decisions
UNION ALL
SELECT 'attack_actions', COUNT(*) FROM attack_actions;
