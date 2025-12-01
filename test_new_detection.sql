-- Test new scan detection logic
SELECT 
    origin,
    COUNT(*) as attack_count,
    COUNT(DISTINCT 
        CASE 
            WHEN attacker_name LIKE '%SSH%' THEN 'SSH'
            WHEN attacker_name LIKE '%FTP%' THEN 'FTP'
            WHEN attacker_name LIKE '%HTTP%' THEN 'HTTP'
            WHEN attacker_name LIKE '%MySQL%' THEN 'MySQL'
            WHEN attacker_name LIKE '%PostgreSQL%' THEN 'PostgreSQL'
            WHEN attacker_name LIKE '%Telnet%' THEN 'Telnet'
            ELSE 'Other'
        END
    ) as unique_services,
    EXTRACT(EPOCH FROM (MAX(created_at) - MIN(created_at))) as duration_sec,
    ROUND(COUNT(*)::numeric / GREATEST(EXTRACT(EPOCH FROM (MAX(created_at) - MIN(created_at))), 1), 2) as attack_rate,
    CASE 
        -- Multiple services in short time = scan
        WHEN COUNT(DISTINCT CASE WHEN attacker_name LIKE '%SSH%' THEN 'SSH' WHEN attacker_name LIKE '%FTP%' THEN 'FTP' WHEN attacker_name LIKE '%HTTP%' THEN 'HTTP' WHEN attacker_name LIKE '%MySQL%' THEN 'MySQL' ELSE 'Other' END) >= 2 
            AND EXTRACT(EPOCH FROM (MAX(created_at) - MIN(created_at))) < 180 
        THEN '🔍 Port Scan'
        -- High attack rate = scan
        WHEN COUNT(*)::numeric / GREATEST(EXTRACT(EPOCH FROM (MAX(created_at) - MIN(created_at))), 1) > 1.0 
            AND COUNT(*) > 10 
        THEN '🔍 Port Scan'
        -- Many attacks, short duration, multiple services
        WHEN COUNT(*) > 20 
            AND EXTRACT(EPOCH FROM (MAX(created_at) - MIN(created_at))) < 60 
            AND COUNT(DISTINCT CASE WHEN attacker_name LIKE '%SSH%' THEN 'SSH' WHEN attacker_name LIKE '%FTP%' THEN 'FTP' ELSE 'Other' END) >= 2
        THEN '🔍 Port Scan'
        ELSE '⚔️ Attack'
    END as attack_type
FROM attack_sessions 
WHERE origin IS NOT NULL 
GROUP BY origin 
ORDER BY attack_count DESC 
LIMIT 15;
