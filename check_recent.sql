-- Check recent attacks (last 10 minutes)
SELECT 
    origin, 
    COUNT(*) as attacks, 
    STRING_AGG(DISTINCT attacker_name, ', ') as services_hit, 
    COUNT(DISTINCT 
        CASE 
            WHEN attacker_name LIKE '%SSH%' THEN 'SSH'
            WHEN attacker_name LIKE '%FTP%' THEN 'FTP'
            WHEN attacker_name LIKE '%HTTP%' THEN 'HTTP'
            WHEN attacker_name LIKE '%MySQL%' THEN 'MySQL'
            WHEN attacker_name LIKE '%Telnet%' THEN 'Telnet'
            ELSE 'Other'
        END
    ) as unique_services,
    EXTRACT(EPOCH FROM (MAX(created_at) - MIN(created_at))) as duration_sec
FROM attack_sessions 
WHERE created_at > NOW() - INTERVAL '10 minutes'
GROUP BY origin 
ORDER BY attacks DESC;
