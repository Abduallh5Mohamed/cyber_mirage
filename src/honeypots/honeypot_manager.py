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

# Ensure parent directory is importable for ai_agent package
import sys

CURRENT_DIR = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(CURRENT_DIR, ".."))

from ai_agent import ActionType, DeceptionState, default_agent

HOST = "0.0.0.0"
HTTP_PORT = 8080
HONEY_PORTS = [22, 21, 80, 443, 3306, 5432, 502, 445, 139, 1025]
agent = default_agent()
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


def _flag_session_as_scan(session_id, reason):
    if not session_id:
        return
    sid = str(session_id)
    _remember_scan_session(sid)
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
        _flag_session_as_scan(session_id, reason)

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
                    _flag_session_as_scan(tracker['session_id'], tracker['scan_reason'])
                else:
                    _maybe_flag_scan(attacker_ip, tracker)
                
                logger.info(f"📎 Aggregated connection from {attacker_ip}:{port} to existing session {tracker['session_id']}")
                return tracker['session_id'], service
        
        # New IP or window expired - create new session
        IP_CONNECTION_TRACKER[attacker_ip] = {
            'first_seen': current_time,
            'last_seen': current_time,
            'ports': {port},
            'services': {service},
            'session_id': None,
            'commands_executed': 0,
            'scan_logged': False,
            'connections': 1
        }
        
        # Log to PostgreSQL
        conn = get_db_connection()
        session_id = None
        if conn:
            try:
                cursor = conn.cursor()
                # Insert session and return id so we can log actions
                try:
                    cursor.execute(
                        """
                        INSERT INTO attack_sessions 
                        (attacker_name, attacker_skill, origin, detected, start_time, honeypot_type)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        RETURNING id
                        """,
                        (
                            f"Attacker_{attacker_ip}_{service}",
                            1.0,
                            attacker_ip,
                            True,
                            datetime.now(),
                            service,
                        ),
                    )
                except Exception:
                    # Reset failed transaction then fallback without honeypot_type
                    try:
                        conn.rollback()
                    except Exception:
                        pass
                    cursor.execute(
                        """
                        INSERT INTO attack_sessions 
                        (attacker_name, attacker_skill, origin, detected, start_time)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING id
                        """,
                        (
                            f"Attacker_{attacker_ip}_{service}",
                            1.0,
                            attacker_ip,
                            True,
                            datetime.now(),
                        ),
                    )

                row = cursor.fetchone()
                if row:
                    session_id = row[0]
                conn.commit()
                cursor.close()
                conn.close()
                logger.info(f"✅ Logged {service} attack from {attacker_ip} to PostgreSQL (session {session_id})")
            except Exception as e:
                logger.error(f"PostgreSQL insert failed: {e}")
                try:
                    conn.rollback()
                except Exception:
                    pass
                try:
                    conn.close()
                except:
                    pass
        
        # Log to Redis
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
            IP_CONNECTION_TRACKER[attacker_ip]['session_id'] = session_id
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
        SESSION_STATE[session_id] = {
            "service": service,
            "command_count": 0,
            "data_attempts": 0,
            "auth_success": False,
            "start_time": time.time(),
            "last_command": "",
            "suspicion": 0.0,
            "lure_active": False,
            "is_scan": False,
            "ai_enabled": True,
        }
        # Determine if this session already flagged as scan and disable AI automation
        if _is_scan_session(session_id):
            SESSION_STATE[session_id]["is_scan"] = True
            SESSION_STATE[session_id]["ai_enabled"] = False

        state = build_state(session_id, service, 0, 0, False, SESSION_STATE[session_id]["start_time"], "", 0.0)
        action = ActionType.MAINTAIN
        metadata = {}
        if SESSION_STATE[session_id]["ai_enabled"]:
            action = agent.choose_action(state)
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
                        next_action = agent.choose_action(current_state)
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


def main():
    ensure_ai_tables()
    # Start HTTP health server
    t = threading.Thread(target=start_http, daemon=True)
    t.start()

    # Start lightweight TCP listeners for each honeypot port
    for p in HONEY_PORTS:
        th = threading.Thread(target=tcp_listener, args=(p,), daemon=True)
        th.start()

    # Keep main thread alive
    try:
        while True:
            threading.Event().wait(60)
    except KeyboardInterrupt:
        logger.info("Shutting down honeypot manager")


if __name__ == "__main__":
    main()
