#!/usr/bin/env python3
"""Minimal honeypot manager used for local/dev runs.

Provides a simple HTTP /health endpoint and lightweight TCP listeners
on the ports declared in `docker-compose.production.yml` so the container
stays up and reports healthy. This is intentionally simple and safe.
"""
import json
import logging
import os
import socket
import threading
import time
import uuid
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

import psycopg2
import redis
from flask import Flask, jsonify
from flask_cors import CORS

# Ensure parent directory is importable for ai_agent package
import sys

CURRENT_DIR = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(CURRENT_DIR, ".."))

from ai_agent import ActionType, DeceptionState, default_agent, USE_PPO, create_ppo_agent

# Create Flask app for APIs
flask_app = Flask(__name__)
CORS(flask_app)  # Enable CORS for dashboard access

HOST = "0.0.0.0"
HTTP_PORT = 8080
API_PORT = 8081
HONEY_PORTS = [22, 21, 80, 443, 3306, 5432, 502, 445, 139, 1025]

# Use PPO agent if available, otherwise fallback to Q-learning
if USE_PPO:
    try:
        agent = create_ppo_agent()
        logger = logging.getLogger("honeypot_manager")
        logger.info("🚀 Using advanced PPO agent for elite-level deception")
    except Exception as e:
        agent = default_agent()
        logger = logging.getLogger("honeypot_manager")
        logger.warning(f"PPO agent failed to initialize, using Q-learning: {e}")
else:
    agent = default_agent()
    logger = logging.getLogger("honeypot_manager")
    logger.info("Using Q-learning agent (PPO not available)")

SESSION_STATE = {}
SCAN_SESSIONS = set()

# Scan classification thresholds
SCAN_MULTI_SERVICE_THRESHOLD = 2  # different services within short window
SCAN_DURATION_WINDOW = 180  # seconds to consider multi-service scan
SCAN_RATE_THRESHOLD = 1.0  # connections per second considered a scan
SCAN_RATE_MIN_CONNECTIONS = 10  # need at least this many hits to check rate

# Connection aggregation settings - to prevent port scans from counting as many attacks
CONNECTION_AGGREGATION_WINDOW = 60  # seconds - connections from same IP within this window are grouped
IP_CONNECTION_TRACKER = {}  # {ip: {'first_seen': timestamp, 'ports': set(), 'session_id': id, 'commands_executed': int}}
SCAN_THRESHOLD = 3  # If IP connects to >= this many ports without commands, it's a scan

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("honeypot_manager")

# Database connection
DB_HOST = os.getenv('POSTGRES_HOST', 'postgres')
DB_NAME = os.getenv('POSTGRES_DB', 'cyber_mirage')
DB_USER = os.getenv('POSTGRES_USER', 'cybermirage')
DB_PASS = os.getenv('POSTGRES_PASSWORD', 'SecurePass123!')

# Redis connection
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_PASS = os.getenv('REDIS_PASSWORD', 'changeme123')

def get_db_connection():
    """Create PostgreSQL connection"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return None

def get_redis_connection():
    """Create Redis connection"""
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASS, decode_responses=True)
        r.ping()
        return r
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        return None


def ensure_ai_tables():
    conn = get_db_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS agent_decisions (
                id UUID PRIMARY KEY,
                session_id UUID,
                action VARCHAR(64),
                strategy VARCHAR(128),
                reward DOUBLE PRECISION,
                state JSONB,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS deception_events (
                id UUID PRIMARY KEY,
                session_id UUID,
                action VARCHAR(64),
                parameters JSONB,
                executed BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        conn.commit()
        cur.close()
    except Exception as e:
        logger.error(f"Failed ensuring AI tables: {e}")
    finally:
        conn.close()


def _get_session_state(session_id):
    """Return a mutable session state regardless of key type."""
    if session_id is None:
        return None
    state = SESSION_STATE.get(session_id)
    if state:
        return state
    sid_str = str(session_id)
    state = SESSION_STATE.get(sid_str)
    if state:
        return state
    try:
        candidate = uuid.UUID(sid_str)
        return SESSION_STATE.get(candidate)
    except Exception:
        return None


def _remember_scan_session(session_id):
    if not session_id:
        return
    sid = str(session_id)
    SCAN_SESSIONS.add(sid)
    state = _get_session_state(session_id)
    if state is not None:
        state["is_scan"] = True
        state["ai_enabled"] = False


def _is_scan_session(session_id) -> bool:
    if not session_id:
        return False
    sid = str(session_id)
    if sid in SCAN_SESSIONS:
        return True
    state = _get_session_state(session_id)
    if state and state.get("is_scan"):
        SCAN_SESSIONS.add(sid)
        return True
    conn = get_db_connection()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.execute("SELECT is_scan FROM attack_sessions WHERE id = %s", (sid,))
        row = cur.fetchone()
        cur.close()
        if row and row[0]:
            SCAN_SESSIONS.add(sid)
            return True
    except Exception:
        pass
    finally:
        conn.close()
    return False


def _flag_session_as_scan(session_id, reason, tracker=None):
    """Flag a session as scan. If session is pending DB insert, DON'T insert it at all."""
    if not session_id:
        return
    sid = str(session_id)
    _remember_scan_session(sid)
    
    # Disable AI for this session if it's currently active
    if sid in SESSION_STATE:
        SESSION_STATE[sid]["is_scan"] = True
        SESSION_STATE[sid]["ai_enabled"] = False
    
    # If session was pending insert, just mark it and DON'T insert to DB
    if tracker and tracker.get('pending_db_insert'):
        tracker['pending_db_insert'] = False  # Cancel insertion
        tracker['scan_logged'] = True
        logger.info(f"🛡️ Prevented scan session {sid[:8]} from being logged ({reason})")
        return
    
    # Session already in DB - update it
    conn = get_db_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE attack_sessions
            SET is_scan = TRUE,
                scan_reason = %s,
                attacker_skill = 0.1
            WHERE id = %s
            """,
            (reason, sid)
        )
        cur.execute("DELETE FROM agent_decisions WHERE session_id = %s", (sid,))
        cur.execute("DELETE FROM deception_events WHERE session_id = %s", (sid,))
        conn.commit()
        cur.close()
        logger.info(f"🛡️ Marked session {sid[:8]} as port scan ({reason})")
    except Exception as e:
        logger.error(f"Failed to flag port scan session: {e}")
    finally:
        conn.close()


def _maybe_flag_scan(attacker_ip: str, tracker: dict):
    if not tracker or tracker.get('scan_logged'):
        return
    session_id = tracker.get('session_id')
    if not session_id:
        return
    duration = max(tracker.get('last_seen', time.time()) - tracker.get('first_seen', time.time()), 0.001)
    services = tracker.get('services', set())
    connections = tracker.get('connections', len(tracker.get('ports', [])))
    reason = None
    if len(services) >= SCAN_MULTI_SERVICE_THRESHOLD and duration <= SCAN_DURATION_WINDOW:
        reason = f"{len(services)} services in {int(duration)}s"
    elif connections >= SCAN_RATE_MIN_CONNECTIONS and (connections / duration) >= SCAN_RATE_THRESHOLD:
        reason = f"{connections} hits in {int(duration)}s"
    if reason:
        tracker['scan_logged'] = True
        tracker['scan_reason'] = reason
        _flag_session_as_scan(session_id, reason, tracker)

def log_agent_decision(session_id, action: ActionType, reason: str, state: DeceptionState, reward: float = 0.0):
    if _is_scan_session(session_id):
        logger.debug("Skipping AI decision logging for scan session %s", session_id)
        return
    conn = get_db_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        # Convert UUIDs to strings for PostgreSQL compatibility
        decision_id = str(uuid.uuid4())
        session_id_str = str(session_id) if session_id else str(uuid.uuid4())
        cur.execute(
            """
            INSERT INTO agent_decisions (id, session_id, action, strategy, reward, state)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                decision_id,
                session_id_str,
                action.value,
                reason,
                reward,
                json.dumps(state.__dict__),
            ),
        )
        conn.commit()
        cur.close()
        logger.info(f"✅ AI Decision logged: {action.value} for session {session_id_str[:8]}...")
    except Exception as e:
        logger.error(f"Failed logging agent decision: {e}")
    finally:
        conn.close()


def log_deception_event(session_id: str, action: ActionType, parameters: dict, executed: bool = True):
    """Log a deception event when an active action is taken."""
    # Only log active deception actions (not MAINTAIN)
    if action == ActionType.MAINTAIN:
        return
    if _is_scan_session(session_id):
        logger.debug("Skipping deception event for scan session %s", session_id)
        return
    
    conn = get_db_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        # Convert UUIDs to strings for PostgreSQL compatibility
        event_id = str(uuid.uuid4())
        session_id_str = str(session_id) if session_id else str(uuid.uuid4())
        cur.execute(
            """
            INSERT INTO deception_events (id, session_id, action, parameters, executed)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                event_id,
                session_id_str,
                action.value,
                json.dumps(parameters),
                executed,
            ),
        )
        conn.commit()
        cur.close()
        logger.info(f"🎭 Deception Event logged: {action.value} for session {session_id_str[:8]}...")
    except Exception as e:
        logger.error(f"Failed logging deception event: {e}")
    finally:
        conn.close()


def _commit_session_to_db(tracker):
    """Insert a pending session to database after confirming it's a legitimate attack."""
    if not tracker or not tracker.get('pending_db_insert'):
        return  # Already inserted or not pending
    
    session_id = tracker.get('session_id')
    attacker_ip = tracker.get('attacker_ip')
    service = tracker.get('initial_service', 'Unknown')
    
    if not session_id or not attacker_ip:
        return
    
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        # Use the temp UUID as the actual session ID
        try:
            cursor.execute(
                """
                INSERT INTO attack_sessions 
                (id, attacker_name, attacker_skill, origin, detected, start_time, honeypot_type, is_scan)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    session_id,
                    f"Attacker_{attacker_ip}_{service}",
                    1.0,
                    attacker_ip,
                    True,
                    datetime.fromtimestamp(tracker['first_seen']),
                    service,
                    False  # Explicitly NOT a scan
                ),
            )
        except Exception as e:
            # Fallback without honeypot_type if column doesn't exist
            conn.rollback()
            cursor.execute(
                """
                INSERT INTO attack_sessions 
                (id, attacker_name, attacker_skill, origin, detected, start_time, is_scan)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    session_id,
                    f"Attacker_{attacker_ip}_{service}",
                    1.0,
                    attacker_ip,
                    True,
                    datetime.fromtimestamp(tracker['first_seen']),
                    False
                ),
            )
        
        conn.commit()
        cursor.close()
        tracker['pending_db_insert'] = False
        logger.info(f"✅ Committed legitimate attack session {session_id[:8]} to database")
    except Exception as e:
        logger.error(f"Failed to commit session to DB: {e}")
        try:
            conn.rollback()
        except:
            pass
    finally:
        conn.close()


def log_attack(port, attacker_ip, attacker_port):
    """Log attack to PostgreSQL and Redis with connection aggregation.
    
    This prevents port scans from being counted as many separate attacks.
    Connections from the same IP within CONNECTION_AGGREGATION_WINDOW seconds
    are grouped together as a single session.
    """
    global IP_CONNECTION_TRACKER
    
    try:
        # Determine service type
        service_map = {
            22: 'SSH',
            21: 'FTP',
            80: 'HTTP',
            443: 'HTTPS',
            3306: 'MySQL',
            5432: 'PostgreSQL',
            502: 'Modbus',
            445: 'SMB',
            139: 'NetBIOS',
            1025: 'SMTP'
        }
        service = service_map.get(port, 'Unknown')
        
        current_time = time.time()
        
        # Check if we have a recent session for this IP (connection aggregation)
        if attacker_ip in IP_CONNECTION_TRACKER:
            tracker = IP_CONNECTION_TRACKER[attacker_ip]
            time_since_first = current_time - tracker['first_seen']
            
            if time_since_first < CONNECTION_AGGREGATION_WINDOW:
                # Same session - just add this port to the list
                tracker['ports'].add(port)
                tracker.setdefault('services', set()).add(service)
                tracker['last_seen'] = current_time
                tracker['connections'] = tracker.get('connections', 1) + 1
                
                # Update Redis count for this service, but don't create new attack session
                r = get_redis_connection()
                if r:
                    try:
                        key = f"threat:{attacker_ip}"
                        r.hset(key, 'last_seen', datetime.now().isoformat())
                        r.hset(key, 'ports_scanned', ','.join(map(str, tracker['ports'])))
                    except Exception as e:
                        logger.error(f"Redis update failed: {e}")
                
                num_ports = len(tracker['ports'])
                if num_ports >= SCAN_THRESHOLD and not tracker.get('scan_logged'):
                    logger.info(f"🔍 Port scan detected from {attacker_ip} ({num_ports} ports)")
                    tracker['scan_logged'] = True
                    tracker['scan_reason'] = f"{num_ports} unique ports"
                    _flag_session_as_scan(tracker['session_id'], tracker['scan_reason'], tracker)
                else:
                    _maybe_flag_scan(attacker_ip, tracker)
                
                logger.info(f"📎 Aggregated connection from {attacker_ip}:{port} to existing session {tracker['session_id']}")
                return tracker['session_id'], service
        
        # New IP or window expired - create TEMPORARY session (don't insert to DB yet)
        # We'll only insert if it's a real attack, not a scan
        temp_session_id = str(uuid.uuid4())
        
        IP_CONNECTION_TRACKER[attacker_ip] = {
            'first_seen': current_time,
            'last_seen': current_time,
            'ports': {port},
            'services': {service},
            'session_id': temp_session_id,
            'commands_executed': 0,
            'scan_logged': False,
            'connections': 1,
            'pending_db_insert': True,  # Mark as not yet inserted to DB
            'attacker_ip': attacker_ip,
            'initial_service': service
        }
        
        # DON'T insert to database yet - wait to confirm it's not a scan
        session_id = temp_session_id
        
        # Log to Redis for threat intel (lightweight)
        r = get_redis_connection()
        if r:
            try:
                key = f"threat:{attacker_ip}"
                r.hincrby(key, 'count', 1)
                r.hset(key, 'last_seen', datetime.now().isoformat())
                r.hset(key, 'service', service)
                logger.info(f"✅ Logged threat intel to Redis for {attacker_ip}")
            except Exception as e:
                logger.error(f"Redis update failed: {e}")
        
        # Store session_id in tracker for aggregation
        if attacker_ip in IP_CONNECTION_TRACKER:
            _maybe_flag_scan(attacker_ip, IP_CONNECTION_TRACKER[attacker_ip])
            
    except Exception as e:
        logger.error(f"Attack logging failed: {e}")

    return session_id, service


def cleanup_old_trackers():
    """Clean up old connection trackers to prevent memory buildup."""
    global IP_CONNECTION_TRACKER
    current_time = time.time()
    expired_ips = []
    
    for ip, tracker in IP_CONNECTION_TRACKER.items():
        if current_time - tracker['last_seen'] > CONNECTION_AGGREGATION_WINDOW * 2:
            expired_ips.append(ip)
    
    for ip in expired_ips:
        del IP_CONNECTION_TRACKER[ip]
    
    if expired_ips:
        logger.debug(f"🧹 Cleaned up {len(expired_ips)} expired connection trackers")


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b"{\"status\": \"ok\"}\n")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        logger.info("HTTP %s - %s" % (self.path, format % args))


def start_http():
    server = HTTPServer((HOST, HTTP_PORT), HealthHandler)
    logger.info(f"HTTP health server listening on {HOST}:{HTTP_PORT}")
    try:
        server.serve_forever()
    except Exception:
        server.server_close()


def tcp_listener(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind((HOST, port))
        sock.listen(5)
        logger.info(f"TCP honeypot listening on {HOST}:{port}")
        while True:
            conn, addr = sock.accept()
            attacker_ip, attacker_port = addr
            logger.info(f"Connection on port {port} from {addr}")

            # Handle each connection in its own thread so listener stays responsive
            th = threading.Thread(target=handle_connection, args=(conn, port, attacker_ip, attacker_port), daemon=True)
            th.start()
    except PermissionError:
        logger.warning(f"Permission denied binding to port {port}; continuing")
    except Exception as e:
        logger.exception(f"Listener on port {port} failed: {e}")
    finally:
        try:
            sock.close()
        except Exception:
            pass


def insert_attack_action(session_id, step_number, action_id, action_text, suspicion=0.0, data_collected=0.0):
    """Insert an action row tied to a session."""
    try:
        conn = get_db_connection()
        if not conn:
            return
        cur = conn.cursor()
        try:
            # Ensure action_id is not null - use step_number as fallback
            actual_action_id = action_id if action_id is not None else step_number
            session_id_str = str(session_id) if session_id else str(uuid.uuid4())
            cur.execute("""
                INSERT INTO attack_actions (session_id, step_number, action_id, reward, suspicion, data_collected, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                session_id_str,
                step_number,
                actual_action_id,
                None,
                suspicion,
                data_collected,
                datetime.now()
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Failed inserting attack action: {e}")
        finally:
            cur.close()
            conn.close()
    except Exception as e:
        logger.error(f"insert_attack_action error: {e}")


def _commit_pending_session(session_id):
    """Helper to commit a pending session when legitimate activity detected."""
    if not session_id:
        return
    
    # Find the tracker for this session
    for ip, tracker in IP_CONNECTION_TRACKER.items():
        if tracker.get('session_id') == session_id and tracker.get('pending_db_insert'):
            _commit_session_to_db(tracker)
            return


def build_state(session_id: str, service: str, command_count: int, data_attempts: int, auth_success: bool, start_time: float, last_command: str, suspicion: float) -> DeceptionState:
    duration = max(time.time() - start_time, 0.0)
    return DeceptionState(
        service=service,
        command_count=command_count,
        data_exfil_attempts=data_attempts,
        auth_success=auth_success,
        duration_seconds=duration,
        last_command=last_command,
        suspicion_score=suspicion,
    )


def apply_action(conn, action: ActionType, service: str):
    if action == ActionType.INJECT_DELAY:
        delay = 0.5 if service != "FTP" else 1.5
        time.sleep(delay)
        return {"delay": delay}
    if action == ActionType.SWAP_SERVICE_BANNER and service == "SSH":
        banner = b"SSH-2.0-OpenSSH_9.3p1 Debian-1\r\n"
        try:
            conn.sendall(banner)
        except Exception:
            pass
        return {"banner": banner.decode(errors='ignore')}
    if action == ActionType.PRESENT_LURE:
        lure_name = "finance_Q4_backup.zip"
        return {"lure": True, "filename": lure_name}
    if action == ActionType.DROP_SESSION:
        try:
            conn.sendall(b"421 Service closing control connection.\r\n")
        except Exception:
            pass
        conn.close()
        return {"dropped": True}
    return {}


def handle_connection(conn, port, attacker_ip, attacker_port):
    """Handle an accepted connection with protocol emulation and logging."""
    session_id = None
    try:
        session_id, service = log_attack(port, attacker_ip, attacker_port)
        if not session_id:
            session_id = str(uuid.uuid4())
            service = service or "Unknown"
        
        # Check if session is already marked as scan BEFORE doing anything
        is_scan = _is_scan_session(session_id)
        
        SESSION_STATE[session_id] = {
            "service": service,
            "command_count": 0,
            "data_attempts": 0,
            "auth_success": False,
            "start_time": time.time(),
            "last_command": "",
            "suspicion": 0.0,
            "lure_active": False,
            "is_scan": is_scan,
            "ai_enabled": not is_scan,  # Disable AI if it's already a scan
        }

        state = build_state(session_id, service, 0, 0, False, SESSION_STATE[session_id]["start_time"], "", 0.0)
        action = ActionType.MAINTAIN
        metadata = {}
        
        # ONLY run AI if this is NOT a scan session
        if not is_scan:
            action_result = agent.choose_action(state)
            # Handle both Q-learning (returns action) and PPO (returns tuple)
            if isinstance(action_result, tuple):
                action, log_prob, value = action_result
                SESSION_STATE[session_id]["last_log_prob"] = log_prob
                SESSION_STATE[session_id]["last_value"] = value
            else:
                action = action_result
            metadata = apply_action(conn, action, service)
            log_agent_decision(session_id, action, agent.get_reason(action, state), state, 0.0)
            if metadata:
                log_deception_event(session_id, action, metadata)
                if metadata.get("lure"):
                    SESSION_STATE[session_id]["lure_active"] = True
                if metadata.get("dropped"):
                    return

        # Prepare banners
        service_banners = {
            22: b"SSH-2.0-OpenSSH_7.6p1 Ubuntu-4ubuntu0.3\r\n",
            21: b"220 (vsFTPd 3.0.3)\r\n",
            80: None,
            443: None,
            3306: None,
            445: None,  # SMB uses binary protocol
            139: None,  # NetBIOS uses binary protocol
            502: b"Modbus/TCP proxy\r\n",
            1025: b"220 smtpd (Postfix) ready\r\n"
        }

        # Send initial banner / response
        if port == 80:
            _commit_pending_session(session_id)  # HTTP request = legitimate
            body = b"<html><body><h1>Welcome</h1><p>Apache/2.4.29 (Ubuntu)</p></body></html>"
            resp = (
                b"HTTP/1.1 200 OK\r\n"
                b"Content-Type: text/html; charset=UTF-8\r\n"
                b"Content-Length: " + str(len(body)).encode() + b"\r\n"
                b"Connection: close\r\n\r\n" + body
            )
            try:
                conn.sendall(resp)
            except Exception:
                pass

        else:
            banner = service_banners.get(port)
            if banner is None:
                try:
                    conn.sendall(f"220 {port} service ready\r\n".encode())
                except Exception:
                    pass
            else:
                try:
                    conn.sendall(banner)
                except Exception:
                    pass

        # Protocol-specific handling
        if port == 21:
            # Simple FTP interactive emulation
            try:
                conn.settimeout(300)
                step = 1
                logged_user = None
                while True:
                    data = b""
                    # read a line
                    while not data.endswith(b"\n"):
                        chunk = conn.recv(1024)
                        if not chunk:
                            raise ConnectionResetError()
                        data += chunk
                    line = data.decode(errors='ignore').strip()
                    if not line:
                        break
                    cmd = line.split(' ')[0].upper()
                    SESSION_STATE[session_id]["command_count"] += 1
                    
                    # First real command - commit session to DB as legitimate attack
                    if SESSION_STATE[session_id]["command_count"] == 1:
                        _commit_pending_session(session_id)
                    
                    if cmd in ("RETR", "STOR"):
                        SESSION_STATE[session_id]["data_attempts"] += 1
                    if cmd == "PASS":
                        SESSION_STATE[session_id]["auth_success"] = True
                    SESSION_STATE[session_id]["last_command"] = line
                    suspicion = 0.2 * SESSION_STATE[session_id]["command_count"]
                    SESSION_STATE[session_id]["suspicion"] = suspicion
                    insert_attack_action(session_id, step, None, line, suspicion=suspicion, data_collected=len(line))
                    current_state = build_state(
                        session_id,
                        service,
                        SESSION_STATE[session_id]["command_count"],
                        SESSION_STATE[session_id]["data_attempts"],
                        SESSION_STATE[session_id]["auth_success"],
                        SESSION_STATE[session_id]["start_time"],
                        line,
                        suspicion,
                    )
                    if SESSION_STATE[session_id]["ai_enabled"]:
                        reward = agent.compute_reward(line, SESSION_STATE[session_id]["auth_success"], len(line), False)
                        
                        # Store transition for PPO if applicable
                        if hasattr(agent, 'store_transition'):
                            agent.store_transition(
                                state, action, reward,
                                SESSION_STATE[session_id].get("last_log_prob", 0.0),
                                SESSION_STATE[session_id].get("last_value", 0.0),
                                False
                            )
                        
                        next_action_result = agent.choose_action(current_state)
                        if isinstance(next_action_result, tuple):
                            next_action, log_prob, value = next_action_result
                            SESSION_STATE[session_id]["last_log_prob"] = log_prob
                            SESSION_STATE[session_id]["last_value"] = value
                        else:
                            next_action = next_action_result
                        
                        # Update Q-learning agent if applicable
                        if hasattr(agent, 'update') and not hasattr(agent, 'store_transition'):
                            agent.update(state, action, reward, current_state)
                        
                        log_agent_decision(session_id, next_action, agent.get_reason(next_action, current_state), current_state, reward)
                        action = next_action
                        state = current_state
                        metadata = apply_action(conn, action, service)
                        if metadata:
                            log_deception_event(session_id, action, metadata)
                            if metadata.get("lure"):
                                SESSION_STATE[session_id]["lure_active"] = True
                            if metadata.get("dropped"):
                                break
                    step += 1

                    if cmd == 'USER':
                        try:
                            conn.sendall(b"331 Please specify the password.\r\n")
                        except Exception:
                            pass
                    elif cmd == 'PASS':
                        logged_user = True
                        try:
                            conn.sendall(b"230 Login successful.\r\n")
                        except Exception:
                            pass
                    elif cmd == 'LIST' or cmd == 'NLST':
                        listing = b"-rw-r--r-- 1 root root 1024 Nov 26 2025 secrets.txt\r\n"
                        if SESSION_STATE[session_id].get("lure_active"):
                            listing += b"-rw-r--r-- 1 root root 4096 Nov 20 2025 finance_Q4_backup.zip\r\n"
                        try:
                            conn.sendall(b"150 Here comes the directory listing.\r\n")
                            conn.sendall(listing)
                            conn.sendall(b"226 Directory send OK.\r\n")
                        except Exception:
                            pass
                    elif cmd in ('RETR', 'STOR'):
                        if SESSION_STATE[session_id].get("lure_active") and cmd == 'RETR':
                            try:
                                conn.sendall(b"150 Opening data connection.\r\n")
                                conn.sendall(b"Fake financial data -- classified\r\n")
                                conn.sendall(b"226 Transfer complete.\r\n")
                            except Exception:
                                pass
                            continue
                        try:
                            conn.sendall(b"550 Permission denied.\r\n")
                        except Exception:
                            pass
                    elif cmd in ('QUIT', 'BYE', 'EXIT'):
                        try:
                            conn.sendall(b"221 Goodbye.\r\n")
                        except Exception:
                            pass
                        break
                    else:
                        # Generic response
                        try:
                            conn.sendall(b"200 OK\r\n")
                        except Exception:
                            pass
            except Exception:
                pass

        elif port == 22:
            # Minimal SSH capture: read initial client bytes (if any) to avoid revealing honeypot
            try:
                conn.settimeout(2.0)
                try:
                    data = conn.recv(4096)
                    if data:
                        _commit_pending_session(session_id)  # Commit as legitimate
                        insert_attack_action(session_id, 1, None, data.hex(), suspicion=0.0, data_collected=len(data))
                except Exception:
                    pass
            finally:
                # wait a short moment so logs capture
                try:
                    threading.Event().wait(0.2)
                except:
                    pass

        else:
            # For other ports we attempt a short read to capture probes
            try:
                conn.settimeout(1.0)
                try:
                    data = conn.recv(2048)
                    if data:
                        _commit_pending_session(session_id)  # Commit as legitimate
                        insert_attack_action(session_id, 1, None, data.decode(errors='ignore'), suspicion=0.0, data_collected=len(data))
                except Exception:
                    pass
            except Exception:
                pass

    except Exception as e:
        logger.error(f"Connection handler error for {attacker_ip}:{attacker_port} on port {port}: {e}")
    finally:
        try:
            # update end_time for session
            if session_id:
                conn_db = get_db_connection()
                if conn_db:
                    cur = conn_db.cursor()
                    try:
                        cur.execute("UPDATE attack_sessions SET end_time = %s WHERE id = %s", (datetime.now(), session_id))
                        conn_db.commit()
                    except Exception:
                        pass
                    finally:
                        cur.close()
                        conn_db.close()
        except Exception:
            pass
        SESSION_STATE.pop(session_id, None)
        try:
            conn.close()
        except Exception:
            pass


# Flask API Endpoints
@flask_app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'honeypots'}), 200

@flask_app.route('/api/ppo/status', methods=['GET'])
def ppo_status():
    """Get PPO agent status."""
    try:
        if USE_PPO and hasattr(agent, 'actor'):
            return jsonify({
                'success': True,
                'agent_type': 'PPO',
                'active': True,
                'device': str(agent.device) if hasattr(agent, 'device') else 'cpu'
            }), 200
        else:
            return jsonify({
                'success': True,
                'agent_type': 'Q-Learning',
                'active': True,
                'fallback': True
            }), 200
    except Exception as e:
        logger.error(f"Error getting PPO status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@flask_app.route('/api/ppo/metrics', methods=['GET'])
def ppo_metrics():
    """Get PPO metrics from database."""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database unavailable'}), 500
        
        cur = conn.cursor()
        
        # Get decision statistics
        cur.execute("""
            SELECT 
                COUNT(*) as total_decisions,
                AVG(reward) as avg_reward,
                COUNT(DISTINCT session_id) as unique_sessions
            FROM agent_decisions
            WHERE created_at >= NOW() - INTERVAL '1 hour'
        """)
        stats = cur.fetchone()
        
        # Get action distribution
        cur.execute("""
            SELECT action, COUNT(*) as count
            FROM agent_decisions
            WHERE created_at >= NOW() - INTERVAL '1 hour'
            GROUP BY action
        """)
        actions = {row[0]: row[1] for row in cur.fetchall()}
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'metrics': {
                'total_decisions': stats[0] if stats else 0,
                'avg_reward': float(stats[1]) if stats and stats[1] else 0.0,
                'unique_sessions': stats[2] if stats else 0,
                'action_distribution': actions,
                'agent_type': 'PPO' if USE_PPO else 'Q-Learning'
            }
        }), 200
    except Exception as e:
        logger.error(f"Error getting PPO metrics: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def run_flask_api():
    """Run Flask API server in separate thread."""
    try:
        flask_app.run(host='0.0.0.0', port=API_PORT, debug=False, use_reloader=False)
    except Exception as e:
        logger.error(f"Flask API error: {e}")

def periodic_ppo_training():
    """Periodically train PPO agent and save checkpoint."""
    while True:
        try:
            threading.Event().wait(300)  # Every 5 minutes
            if hasattr(agent, 'update') and hasattr(agent, 'store_transition'):
                agent.update()  # Train PPO
                # Save checkpoint every 10 training cycles
                if agent.training_step % 10 == 0:
                    agent.save('/app/data/models/ppo_checkpoint.pt')
        except Exception as e:
            logger.error(f"PPO training error: {e}")


def main():
    ensure_ai_tables()
    
    # Start Flask API server
    api_thread = threading.Thread(target=run_flask_api, daemon=True)
    api_thread.start()
    logger.info(f"🌐 Flask API server started on port {API_PORT}")
    
    # Start PPO training thread if using PPO
    if hasattr(agent, 'store_transition'):
        training_thread = threading.Thread(target=periodic_ppo_training, daemon=True)
        training_thread.start()
        logger.info("🎯 PPO training thread started")
    
    # Start HTTP health server
    t = threading.Thread(target=start_http, daemon=True)
    t.start()

    # Start lightweight TCP listeners for each honeypot port
    for p in HONEY_PORTS:
        th = threading.Thread(target=tcp_listener, args=(p,), daemon=True)
        th.start()

    # Cleanup old connection trackers periodically
    def cleanup_loop():
        while True:
            try:
                threading.Event().wait(CONNECTION_AGGREGATION_WINDOW)
                cleanup_old_trackers()
            except Exception:
                pass
    
    cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
    cleanup_thread.start()

    # Keep main thread alive
    try:
        while True:
            threading.Event().wait(60)
    except KeyboardInterrupt:
        logger.info("Shutting down honeypot manager")


if __name__ == "__main__":
    main()
