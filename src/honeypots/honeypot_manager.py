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


def log_agent_decision(session_id: str, action: ActionType, reason: str, state: DeceptionState, reward: float = 0.0):
    conn = get_db_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO agent_decisions (id, session_id, action, strategy, reward, state)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                str(uuid.uuid4()),
                str(session_id) if session_id else str(uuid.uuid4()),
                action.value,
                reason,
                reward,
                json.dumps(state.__dict__) if hasattr(state, '__dict__') else '{}',
            ),
        )
        conn.commit()
        cur.close()
    except Exception as e:
        logger.error(f"Failed logging agent decision: {e}")
    finally:
        conn.close()


def log_deception_event(session_id: str, action: ActionType, parameters: dict, executed: bool = True):
    conn = get_db_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO deception_events (id, session_id, action, parameters, executed)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                str(uuid.uuid4()),
                str(session_id) if session_id else str(uuid.uuid4()),
                action.value,
                json.dumps(parameters) if parameters else '{}',
                executed,
            ),
        )
        conn.commit()
        cur.close()
    except Exception as e:
        logger.error(f"Failed logging deception event: {e}")
    finally:
        conn.close()

def log_attack(port, attacker_ip, attacker_port):
    """Log attack to PostgreSQL and Redis"""
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
        
        # Log to PostgreSQL
        conn = get_db_connection()
        session_id = None
        if conn:
            try:
                cursor = conn.cursor()
                # Insert session and return id so we can log actions
                try:
                    cursor.execute("""
                        INSERT INTO attack_sessions 
                        (attacker_name, attacker_skill, origin, detected, start_time, honeypot_type)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """, (
                        f"Attacker_{attacker_ip}_{service}",
                        1.0,
                        attacker_ip,
                        True,
                        datetime.now(),
                        service
                    ))
                except Exception:
                    # Fallback without honeypot_type
                    cursor.execute("""
                        INSERT INTO attack_sessions 
                        (attacker_name, attacker_skill, origin, detected, start_time)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING id
                    """, (
                        f"Attacker_{attacker_ip}_{service}",
                        1.0,
                        attacker_ip,
                        True,
                        datetime.now()
                    ))

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
    except Exception as e:
        logger.error(f"Attack logging failed: {e}")

    return session_id, service


def get_ppo_metrics():
    """Get real PPO metrics from database."""
    metrics = {
        'agent_type': 'PPO Elite Agent v3.0',
        'total_decisions': 0,
        'unique_sessions': 0,
        'avg_reward': 0.0,
        'action_distribution': {},
        'status': 'active'
    }
    
    conn = get_db_connection()
    if not conn:
        return metrics
    
    try:
        cur = conn.cursor()
        
        # Total decisions
        cur.execute("SELECT COUNT(*) FROM agent_decisions")
        row = cur.fetchone()
        metrics['total_decisions'] = row[0] if row else 0
        
        # Unique sessions
        cur.execute("SELECT COUNT(DISTINCT session_id) FROM agent_decisions")
        row = cur.fetchone()
        metrics['unique_sessions'] = row[0] if row else 0
        
        # Average reward (last hour)
        cur.execute("""
            SELECT AVG(reward) FROM agent_decisions 
            WHERE created_at > NOW() - INTERVAL '1 hour'
        """)
        row = cur.fetchone()
        metrics['avg_reward'] = float(row[0]) if row and row[0] else 0.0
        
        # Action distribution
        cur.execute("""
            SELECT action, COUNT(*) as cnt 
            FROM agent_decisions 
            GROUP BY action 
            ORDER BY cnt DESC
        """)
        for row in cur.fetchall():
            metrics['action_distribution'][row[0]] = row[1]
        
        cur.close()
    except Exception as e:
        logger.error(f"Error getting PPO metrics: {e}")
    finally:
        conn.close()
    
    return metrics


def get_system_health():
    """Get real system health status."""
    health = {
        'postgres': {'status': 'disconnected', 'latency_ms': None},
        'redis': {'status': 'disconnected', 'latency_ms': None},
        'honeypots': {'status': 'active', 'ports': [], 'connections': 0},
        'timestamp': datetime.now().isoformat()
    }
    
    # Check PostgreSQL
    start = time.time()
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT 1")
            cur.close()
            health['postgres']['status'] = 'connected'
            health['postgres']['latency_ms'] = round((time.time() - start) * 1000, 2)
        except:
            pass
        finally:
            conn.close()
    
    # Check Redis
    start = time.time()
    r = get_redis_connection()
    if r:
        try:
            r.ping()
            health['redis']['status'] = 'connected'
            health['redis']['latency_ms'] = round((time.time() - start) * 1000, 2)
        except:
            pass
    
    # Honeypot status
    health['honeypots']['ports'] = HONEY_PORTS
    health['honeypots']['connections'] = len(SESSION_STATE)
    
    return health


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status": "ok"}\n')
        
        elif self.path == "/api/health/full":
            health = get_system_health()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = json.dumps({'success': True, 'health': health})
            self.wfile.write(response.encode())
        
        elif self.path == "/api/ppo/metrics":
            metrics = get_ppo_metrics()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = json.dumps({'success': True, 'metrics': metrics})
            self.wfile.write(response.encode())
        
        elif self.path == "/api/status":
            status = {
                'honeypots_active': len(HONEY_PORTS),
                'sessions': len(SESSION_STATE),
                'uptime': 'running',
                'agent': agent.__class__.__name__ if agent else 'None'
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = json.dumps({'success': True, 'status': status})
            self.wfile.write(response.encode())
        
        else:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error": "not found"}\n')

    def log_message(self, format, *args):
        # Only log non-health requests to reduce noise
        if "/health" not in self.path:
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
            safe_action_id = action_id if action_id is not None else step_number
            cur.execute("""
                INSERT INTO attack_actions (session_id, step_number, action_id, reward, suspicion, data_collected, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                str(session_id) if session_id else str(uuid.uuid4()),
                step_number,
                safe_action_id,
                0.0,
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


def calculate_action_reward(action: ActionType, state: DeceptionState, metadata: dict) -> float:
    """Calculate reward based on action effectiveness and context.
    
    Reward shaping based on:
    - Action appropriateness for the threat level
    - Intelligence gathering potential
    - Attacker engagement metrics
    """
    reward = 0.0
    
    # Base rewards by action category
    action_rewards = {
        # Session Control
        ActionType.MAINTAIN: 1.0,
        ActionType.DROP_SESSION: 2.0 if state.suspicion_score > 0.7 else -1.0,
        ActionType.THROTTLE_SESSION: 2.5,
        ActionType.REDIRECT_SESSION: 3.5,
        
        # Delay Tactics - effective against automated attacks
        ActionType.INJECT_DELAY: 2.0,
        ActionType.PROGRESSIVE_DELAY: 2.5,
        ActionType.RANDOM_DELAY: 2.0,
        
        # Banner Manipulation - increases deception
        ActionType.SWAP_SERVICE_BANNER: 3.0,
        ActionType.RANDOMIZE_BANNER: 2.5,
        ActionType.MIMIC_VULNERABLE: 4.0,
        
        # Lure & Deception - high intel value
        ActionType.PRESENT_LURE: 5.0,
        ActionType.DEPLOY_BREADCRUMB: 4.0,
        ActionType.INJECT_FAKE_CREDENTIALS: 4.5,
        ActionType.SIMULATE_VALUABLE_TARGET: 4.0,
        
        # Active Defense - forensic value
        ActionType.CAPTURE_TOOLS: 6.0,
        ActionType.LOG_ENHANCED: 2.0,
        ActionType.FINGERPRINT_ATTACKER: 3.5,
        
        # Advanced Tactics
        ActionType.TARPIT: 4.0,
        ActionType.HONEYPOT_UPGRADE: 3.0,
        ActionType.ALERT_AND_TRACK: 5.0 if state.suspicion_score > 0.5 else 1.0,
    }
    
    reward = action_rewards.get(action, 1.0)
    
    # Bonus for appropriate response to threat level
    if state.suspicion_score > 0.8 and action in [ActionType.DROP_SESSION, ActionType.ALERT_AND_TRACK, ActionType.CAPTURE_TOOLS]:
        reward += 3.0
    
    # Bonus for deception when attacker is engaged
    if state.command_count > 3 and action in [ActionType.PRESENT_LURE, ActionType.DEPLOY_BREADCRUMB, ActionType.INJECT_FAKE_CREDENTIALS]:
        reward += 2.0
    
    # Bonus for metadata success
    if metadata:
        if metadata.get("capture_enabled"):
            reward += 2.0
        if metadata.get("lure"):
            reward += 1.5
        if metadata.get("fingerprinting"):
            reward += 1.0
        if metadata.get("tarpit"):
            reward += 1.5
    
    return round(reward, 2)

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
    """Apply one of 20 elite deception actions."""
    
    # === Session Control Actions ===
    if action == ActionType.MAINTAIN:
        return {"maintained": True}
    
    if action == ActionType.DROP_SESSION:
        try:
            conn.sendall(b"421 Service closing control connection.\r\n")
        except Exception:
            pass
        conn.close()
        return {"dropped": True}
    
    if action == ActionType.THROTTLE_SESSION:
        time.sleep(2.0)
        return {"throttled": True, "delay": 2.0}
    
    if action == ActionType.REDIRECT_SESSION:
        return {"redirected": True, "target": "isolated_env"}
    
    # === Delay Tactics ===
    if action == ActionType.INJECT_DELAY:
        delay = 0.5 if service != "FTP" else 1.5
        time.sleep(delay)
        return {"delay": delay}
    
    if action == ActionType.PROGRESSIVE_DELAY:
        delay = min(SESSION_STATE.get(str(id(conn)), {}).get("delay_level", 0.5) * 1.5, 5.0)
        time.sleep(delay)
        return {"progressive_delay": delay}
    
    if action == ActionType.RANDOM_DELAY:
        import random
        delay = random.uniform(0.1, 3.0)
        time.sleep(delay)
        return {"random_delay": delay}
    
    # === Banner Manipulation ===
    if action == ActionType.SWAP_SERVICE_BANNER:
        banner = b"SSH-2.0-OpenSSH_9.3p1 Debian-1\r\n"
        try:
            conn.sendall(banner)
        except Exception:
            pass
        return {"banner": banner.decode(errors='ignore')}
    
    if action == ActionType.RANDOMIZE_BANNER:
        banners = [b"SSH-2.0-OpenSSH_8.9\r\n", b"SSH-2.0-dropbear_2022.83\r\n", b"220 ProFTPD 1.3.6\r\n"]
        import random
        banner = random.choice(banners)
        try:
            conn.sendall(banner)
        except Exception:
            pass
        return {"randomized_banner": banner.decode(errors='ignore')}
    
    if action == ActionType.MIMIC_VULNERABLE:
        vuln_banner = b"SSH-2.0-OpenSSH_4.3 (vulnerable)\r\n"
        try:
            conn.sendall(vuln_banner)
        except Exception:
            pass
        return {"mimic_vulnerable": True}
    
    # === Lure & Deception ===
    if action == ActionType.PRESENT_LURE:
        lure_name = "finance_Q4_backup.zip"
        return {"lure": True, "filename": lure_name}
    
    if action == ActionType.DEPLOY_BREADCRUMB:
        return {"breadcrumb": True, "trail": ["admin_notes.txt", "vpn_config.ovpn"]}
    
    if action == ActionType.INJECT_FAKE_CREDENTIALS:
        return {"fake_creds": True, "username": "svc_backup", "hint": "password in notes"}
    
    if action == ActionType.SIMULATE_VALUABLE_TARGET:
        return {"valuable_target": True, "type": "database_server"}
    
    # === Active Defense ===
    if action == ActionType.CAPTURE_TOOLS:
        return {"capture_enabled": True, "capture_path": "/app/data/captures/"}
    
    if action == ActionType.LOG_ENHANCED:
        return {"enhanced_logging": True, "level": "forensic"}
    
    if action == ActionType.FINGERPRINT_ATTACKER:
        return {"fingerprinting": True, "collect": ["user_agent", "timing", "commands"]}
    
    # === Advanced Tactics ===
    if action == ActionType.TARPIT:
        time.sleep(5.0)
        return {"tarpit": True, "hold_time": 5.0}
    
    if action == ActionType.HONEYPOT_UPGRADE:
        return {"upgraded": True, "interaction_level": "high"}
    
    if action == ActionType.ALERT_AND_TRACK:
        logger.warning(f"🚨 ALERT: High-threat attacker detected on {service}")
        return {"alert_sent": True, "tracking": True}
    
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
        }

        state = build_state(session_id, service, 0, 0, False, SESSION_STATE[session_id]["start_time"], "", 0.0)
        action = agent.choose_action(state)
        metadata = apply_action(conn, action, service)
        # Calculate initial reward based on action taken
        initial_reward = calculate_action_reward(action, state, metadata)
        log_agent_decision(session_id, action, agent.get_reason(action, state), state, initial_reward)
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
