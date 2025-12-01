#!/bin/bash
# Script to fix false positive attack counts
# This consolidates port scan connections into single reconnaissance sessions

echo "🔧 Fixing false positive attack counts..."

cd /home/ubuntu/cyber_mirage

# Option 1: Delete all attacks from a specific IP
if [ "$1" == "--delete-ip" ] && [ -n "$2" ]; then
    echo "Deleting all attacks from IP: $2"
    sudo docker compose -f docker-compose.production.yml exec -T postgres psql -U cybermirage -d cyber_mirage <<SQL
    BEGIN;
    -- Delete related actions first
    DELETE FROM attack_actions WHERE session_id IN (
        SELECT id::text FROM attack_sessions WHERE origin = '$2'
    );
    DELETE FROM agent_decisions WHERE session_id IN (
        SELECT id FROM attack_sessions WHERE origin = '$2'
    );
    DELETE FROM deception_events WHERE session_id IN (
        SELECT id FROM attack_sessions WHERE origin = '$2'
    );
    -- Now delete the sessions
    DELETE FROM attack_sessions WHERE origin = '$2';
    COMMIT;
    SELECT 'Deleted all attacks from IP: $2' as result;
SQL
    exit 0
fi

# Option 2: Consolidate port scans into single sessions
if [ "$1" == "--consolidate-scans" ]; then
    echo "Consolidating port scans into single sessions..."
    sudo docker compose -f docker-compose.production.yml exec -T postgres psql -U cybermirage -d cyber_mirage <<'SQL'
    BEGIN;
    
    -- Find IPs that have many quick connections (likely port scans)
    -- and keep only one session per IP per minute
    WITH scan_candidates AS (
        SELECT 
            origin,
            DATE_TRUNC('minute', start_time) as scan_minute,
            MIN(id) as keep_id,
            COUNT(*) as connection_count,
            STRING_AGG(DISTINCT honeypot_type, ', ') as services_scanned
        FROM attack_sessions
        WHERE origin IS NOT NULL 
        AND origin != ''
        GROUP BY origin, DATE_TRUNC('minute', start_time)
        HAVING COUNT(*) > 3  -- More than 3 connections in same minute = likely scan
    ),
    sessions_to_delete AS (
        SELECT s.id
        FROM attack_sessions s
        JOIN scan_candidates sc ON s.origin = sc.origin 
            AND DATE_TRUNC('minute', s.start_time) = sc.scan_minute
            AND s.id != sc.keep_id
    )
    -- Delete related data
    DELETE FROM attack_actions WHERE session_id IN (SELECT id::text FROM sessions_to_delete);
    DELETE FROM agent_decisions WHERE session_id IN (SELECT id FROM sessions_to_delete);
    DELETE FROM deception_events WHERE session_id IN (SELECT id FROM sessions_to_delete);
    DELETE FROM attack_sessions WHERE id IN (SELECT id FROM sessions_to_delete);
    
    -- Update remaining scan sessions
    UPDATE attack_sessions s
    SET attacker_name = 'PortScan_' || sc.connection_count || '_connections',
        attacker_skill = 0.3
    FROM scan_candidates sc
    WHERE s.id = sc.keep_id;
    
    COMMIT;
    
    SELECT 'Consolidated port scans successfully' as result;
SQL
    exit 0
fi

# Option 3: Show attack summary by IP
if [ "$1" == "--show-summary" ]; then
    echo "Attack summary by IP:"
    sudo docker compose -f docker-compose.production.yml exec -T postgres psql -U cybermirage -d cyber_mirage <<'SQL'
    SELECT 
        origin as "IP",
        COUNT(*) as "Total Attacks",
        STRING_AGG(DISTINCT honeypot_type, ', ') as "Services",
        MIN(start_time) as "First Seen",
        MAX(start_time) as "Last Seen",
        EXTRACT(EPOCH FROM (MAX(start_time) - MIN(start_time))) as "Duration (sec)"
    FROM attack_sessions
    WHERE origin IS NOT NULL AND origin != ''
    GROUP BY origin
    ORDER BY COUNT(*) DESC
    LIMIT 20;
SQL
    exit 0
fi

# Default: Show help
echo "Usage:"
echo "  $0 --delete-ip <IP>       Delete all attacks from specific IP"
echo "  $0 --consolidate-scans    Consolidate port scans into single sessions"  
echo "  $0 --show-summary         Show attack summary by IP"
echo ""
echo "Example:"
echo "  $0 --delete-ip 197.35.34.115"
echo "  $0 --consolidate-scans"
