-- Test scan detection query
SELECT 
    origin,
    COUNT(*) as attacks,
    COUNT(DISTINCT 
        CASE 
            WHEN attacker_name LIKE '%SSH%' THEN 'SSH'
            WHEN attacker_name LIKE '%HTTP%' THEN 'HTTP'
            WHEN attacker_name LIKE '%FTP%' THEN 'FTP'
            WHEN attacker_name LIKE '%MySQL%' THEN 'MySQL'
            WHEN attacker_name LIKE '%Telnet%' THEN 'Telnet'
            ELSE 'Other'
        END
    ) as unique_services,
    EXTRACT(EPOCH FROM (MAX(created_at) - MIN(created_at))) as duration_sec,
    CASE 
        WHEN COUNT(*) > 5 
            AND EXTRACT(EPOCH FROM (MAX(created_at) - MIN(created_at))) < 120 
            AND COUNT(DISTINCT CASE WHEN attacker_name LIKE '%SSH%' THEN 'SSH' WHEN attacker_name LIKE '%HTTP%' THEN 'HTTP' WHEN attacker_name LIKE '%FTP%' THEN 'FTP' ELSE 'Other' END) >= 3
        THEN 'Port Scan'
        ELSE 'Real Attack'
    END as attack_type
FROM attack_sessions 
WHERE origin IS NOT NULL 
GROUP BY origin 
ORDER BY attacks DESC 
LIMIT 15;
