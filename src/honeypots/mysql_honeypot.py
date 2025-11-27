"""
🗄️ MySQL Honeypot Service
Cyber Mirage - Role 1: Adaptive Honeynet Layer

Emulates MySQL database server for detecting:
- SQL injection attempts
- Database credential theft
- Data exfiltration
- Privilege escalation attempts
- Malicious stored procedures

Author: Cyber Mirage Team
Version: 1.0.0 - Production
"""

import socket
import struct
import hashlib
import logging
import threading
import time
import uuid
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =============================================================================
# MYSQL PROTOCOL CONSTANTS
# =============================================================================

class MySQLCommand(Enum):
    """MySQL command types"""
    COM_QUIT = 0x01
    COM_INIT_DB = 0x02
    COM_QUERY = 0x03
    COM_FIELD_LIST = 0x04
    COM_CREATE_DB = 0x05
    COM_DROP_DB = 0x06
    COM_REFRESH = 0x07
    COM_SHUTDOWN = 0x08
    COM_STATISTICS = 0x09
    COM_PROCESS_INFO = 0x0A
    COM_CONNECT = 0x0B
    COM_PROCESS_KILL = 0x0C
    COM_DEBUG = 0x0D
    COM_PING = 0x0E
    COM_TIME = 0x0F
    COM_DELAYED_INSERT = 0x10
    COM_CHANGE_USER = 0x11
    COM_STMT_PREPARE = 0x16
    COM_STMT_EXECUTE = 0x17
    COM_STMT_CLOSE = 0x19


class MySQLCapability:
    """MySQL capability flags"""
    CLIENT_LONG_PASSWORD = 0x00000001
    CLIENT_FOUND_ROWS = 0x00000002
    CLIENT_LONG_FLAG = 0x00000004
    CLIENT_CONNECT_WITH_DB = 0x00000008
    CLIENT_NO_SCHEMA = 0x00000010
    CLIENT_COMPRESS = 0x00000020
    CLIENT_ODBC = 0x00000040
    CLIENT_LOCAL_FILES = 0x00000080
    CLIENT_IGNORE_SPACE = 0x00000100
    CLIENT_PROTOCOL_41 = 0x00000200
    CLIENT_INTERACTIVE = 0x00000400
    CLIENT_SSL = 0x00000800
    CLIENT_IGNORE_SIGPIPE = 0x00001000
    CLIENT_TRANSACTIONS = 0x00002000
    CLIENT_RESERVED = 0x00004000
    CLIENT_SECURE_CONNECTION = 0x00008000
    CLIENT_MULTI_STATEMENTS = 0x00010000
    CLIENT_MULTI_RESULTS = 0x00020000
    CLIENT_PLUGIN_AUTH = 0x00080000


# =============================================================================
# FAKE DATABASE SCHEMA
# =============================================================================

class FakeDatabase:
    """
    Fake MySQL database with lure data
    Contains sensitive-looking tables to attract attackers
    """
    
    def __init__(self):
        self.databases = {
            'information_schema': self._create_information_schema(),
            'mysql': self._create_mysql_db(),
            'production': self._create_production_db(),
            'customers': self._create_customers_db(),
            'internal': self._create_internal_db(),
        }
        
        self.current_db = 'production'
        self.access_log = []
    
    def _create_information_schema(self) -> Dict:
        """Create fake information_schema"""
        return {
            'tables': {
                'TABLES': [
                    {'TABLE_SCHEMA': 'production', 'TABLE_NAME': 'users', 'TABLE_ROWS': 15234},
                    {'TABLE_SCHEMA': 'production', 'TABLE_NAME': 'orders', 'TABLE_ROWS': 892456},
                    {'TABLE_SCHEMA': 'production', 'TABLE_NAME': 'products', 'TABLE_ROWS': 4532},
                    {'TABLE_SCHEMA': 'customers', 'TABLE_NAME': 'accounts', 'TABLE_ROWS': 45678},
                    {'TABLE_SCHEMA': 'customers', 'TABLE_NAME': 'credit_cards', 'TABLE_ROWS': 34521},
                    {'TABLE_SCHEMA': 'internal', 'TABLE_NAME': 'employees', 'TABLE_ROWS': 234},
                    {'TABLE_SCHEMA': 'internal', 'TABLE_NAME': 'salaries', 'TABLE_ROWS': 234},
                ],
                'COLUMNS': [
                    {'TABLE_NAME': 'users', 'COLUMN_NAME': 'id', 'DATA_TYPE': 'int'},
                    {'TABLE_NAME': 'users', 'COLUMN_NAME': 'username', 'DATA_TYPE': 'varchar'},
                    {'TABLE_NAME': 'users', 'COLUMN_NAME': 'password', 'DATA_TYPE': 'varchar'},
                    {'TABLE_NAME': 'users', 'COLUMN_NAME': 'email', 'DATA_TYPE': 'varchar'},
                    {'TABLE_NAME': 'credit_cards', 'COLUMN_NAME': 'card_number', 'DATA_TYPE': 'varchar'},
                    {'TABLE_NAME': 'credit_cards', 'COLUMN_NAME': 'cvv', 'DATA_TYPE': 'varchar'},
                    {'TABLE_NAME': 'credit_cards', 'COLUMN_NAME': 'expiry', 'DATA_TYPE': 'date'},
                ],
                'SCHEMATA': [
                    {'SCHEMA_NAME': 'information_schema'},
                    {'SCHEMA_NAME': 'mysql'},
                    {'SCHEMA_NAME': 'production'},
                    {'SCHEMA_NAME': 'customers'},
                    {'SCHEMA_NAME': 'internal'},
                ]
            }
        }
    
    def _create_mysql_db(self) -> Dict:
        """Create fake mysql system database"""
        return {
            'tables': {
                'user': [
                    {'User': 'root', 'Host': 'localhost', 'Password': '*81F5E21E35407D884A6CD4A731AEBFB6AF209E1B'},
                    {'User': 'admin', 'Host': '%', 'Password': '*2470C0C06DEE42FD1618BB99005ADCA2EC9D1E19'},
                    {'User': 'backup', 'Host': 'localhost', 'Password': '*6BB4837EB74329105EE4568DDA7DC67ED2CA2AD9'},
                    {'User': 'app_user', 'Host': '192.168.%', 'Password': '*A4B6157319038724E3560894F7F932C8886EBFCF'},
                ],
                'db': [
                    {'Db': 'production', 'User': 'app_user'},
                    {'Db': 'customers', 'User': 'admin'},
                ]
            }
        }
    
    def _create_production_db(self) -> Dict:
        """Create fake production database with lure data"""
        return {
            'tables': {
                'users': [
                    {'id': 1, 'username': 'admin', 'password': 'admin123', 'email': 'admin@company.com', 'role': 'superadmin'},
                    {'id': 2, 'username': 'jsmith', 'password': 'J0hnSm1th!', 'email': 'john.smith@company.com', 'role': 'user'},
                    {'id': 3, 'username': 'mjohnson', 'password': 'Mary2024$', 'email': 'mary.johnson@company.com', 'role': 'manager'},
                    {'id': 4, 'username': 'dbadmin', 'password': 'DbR00t@123', 'email': 'dba@company.com', 'role': 'dba'},
                ],
                'orders': [
                    {'id': 1, 'user_id': 2, 'total': 234.56, 'status': 'completed'},
                    {'id': 2, 'user_id': 3, 'total': 1234.00, 'status': 'pending'},
                ],
                'api_keys': [
                    {'id': 1, 'name': 'Production API', 'key': 'sk-prod-FAKE-API-KEY-12345', 'active': True},
                    {'id': 2, 'name': 'Payment Gateway', 'key': 'pk-live-FAKE-PAYMENT-67890', 'active': True},
                ],
                'config': [
                    {'key': 'aws_access_key', 'value': 'AKIAFAKEACCESSKEY123'},
                    {'key': 'aws_secret_key', 'value': 'FAKE+SECRET+KEY+abcdefghijklmn'},
                    {'key': 'database_backup_path', 'value': '/var/backups/db'},
                    {'key': 'admin_email', 'value': 'admin@company.com'},
                ]
            }
        }
    
    def _create_customers_db(self) -> Dict:
        """Create fake customers database with sensitive lure data"""
        return {
            'tables': {
                'accounts': [
                    {'id': 1, 'name': 'John Doe', 'ssn': '123-45-6789', 'dob': '1985-03-15'},
                    {'id': 2, 'name': 'Jane Smith', 'ssn': '987-65-4321', 'dob': '1990-07-22'},
                    {'id': 3, 'name': 'Bob Wilson', 'ssn': '456-78-9012', 'dob': '1978-11-30'},
                ],
                'credit_cards': [
                    {'id': 1, 'account_id': 1, 'card_number': '4111111111111111', 'cvv': '123', 'expiry': '12/25'},
                    {'id': 2, 'account_id': 2, 'card_number': '5500000000000004', 'cvv': '456', 'expiry': '06/26'},
                    {'id': 3, 'account_id': 3, 'card_number': '340000000000009', 'cvv': '7890', 'expiry': '03/24'},
                ],
                'transactions': [
                    {'id': 1, 'card_id': 1, 'amount': 99.99, 'merchant': 'Amazon', 'date': '2024-11-01'},
                    {'id': 2, 'card_id': 2, 'amount': 250.00, 'merchant': 'BestBuy', 'date': '2024-11-05'},
                ]
            }
        }
    
    def _create_internal_db(self) -> Dict:
        """Create fake internal HR database"""
        return {
            'tables': {
                'employees': [
                    {'id': 1, 'name': 'Alice CEO', 'position': 'CEO', 'department': 'Executive'},
                    {'id': 2, 'name': 'Bob CTO', 'position': 'CTO', 'department': 'Technology'},
                    {'id': 3, 'name': 'Charlie CFO', 'position': 'CFO', 'department': 'Finance'},
                ],
                'salaries': [
                    {'employee_id': 1, 'salary': 500000, 'bonus': 100000},
                    {'employee_id': 2, 'salary': 350000, 'bonus': 75000},
                    {'employee_id': 3, 'salary': 400000, 'bonus': 80000},
                ],
                'ssh_keys': [
                    {'id': 1, 'server': 'prod-db-01', 'username': 'dbadmin', 'key': 'ssh-rsa AAAA...FAKE...'},
                    {'id': 2, 'server': 'backup-srv', 'username': 'backup', 'key': 'ssh-rsa BBBB...FAKE...'},
                ]
            }
        }
    
    def execute_query(self, query: str, attacker_ip: str) -> Dict:
        """Execute a fake query and return results"""
        query_upper = query.upper().strip()
        
        # Log the query
        self.access_log.append({
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'attacker_ip': attacker_ip
        })
        
        # Detect SQL injection attempts
        injection_patterns = [
            r"UNION\s+SELECT",
            r"OR\s+1\s*=\s*1",
            r"AND\s+1\s*=\s*1",
            r"'\s*OR\s*'",
            r"--\s*$",
            r";\s*DROP",
            r";\s*DELETE",
            r"SLEEP\s*\(",
            r"BENCHMARK\s*\(",
            r"LOAD_FILE\s*\(",
            r"INTO\s+OUTFILE",
            r"INTO\s+DUMPFILE",
        ]
        
        is_injection = any(re.search(p, query_upper) for p in injection_patterns)
        
        result = {
            'success': True,
            'is_injection': is_injection,
            'is_sensitive': False,
            'rows': [],
            'columns': [],
            'affected_rows': 0,
            'warning': None
        }
        
        # Check for sensitive data access
        sensitive_tables = ['credit_cards', 'salaries', 'ssh_keys', 'api_keys', 'config']
        for table in sensitive_tables:
            if table.upper() in query_upper:
                result['is_sensitive'] = True
                result['warning'] = f'ALERT: Access to sensitive table: {table}'
        
        # Parse and "execute" queries
        if query_upper.startswith('SELECT'):
            result = self._handle_select(query, result)
        elif query_upper.startswith('SHOW DATABASES'):
            result['columns'] = ['Database']
            result['rows'] = [{'Database': db} for db in self.databases.keys()]
        elif query_upper.startswith('SHOW TABLES'):
            if self.current_db in self.databases:
                tables = self.databases[self.current_db].get('tables', {}).keys()
                result['columns'] = ['Tables_in_' + self.current_db]
                result['rows'] = [{f'Tables_in_{self.current_db}': t} for t in tables]
        elif query_upper.startswith('USE '):
            db_name = query.split()[1].strip('`').strip(';')
            if db_name in self.databases:
                self.current_db = db_name
                result['affected_rows'] = 0
            else:
                result['success'] = False
                result['error'] = f"Unknown database '{db_name}'"
        elif query_upper.startswith('DESCRIBE') or query_upper.startswith('DESC'):
            result = self._handle_describe(query, result)
        
        return result
    
    def _handle_select(self, query: str, result: Dict) -> Dict:
        """Handle SELECT queries"""
        query_upper = query.upper()
        
        # Extract table name (simplified)
        if 'FROM' in query_upper:
            parts = query_upper.split('FROM')
            if len(parts) > 1:
                table_part = parts[1].strip().split()[0].strip('`').lower()
                
                # Check each database for the table
                for db_name, db_data in self.databases.items():
                    tables = db_data.get('tables', {})
                    if table_part in tables:
                        rows = tables[table_part]
                        if rows:
                            result['columns'] = list(rows[0].keys())
                            result['rows'] = rows[:100]  # Limit rows
                        return result
        
        # Handle version() and other functions
        if 'VERSION()' in query_upper:
            result['columns'] = ['VERSION()']
            result['rows'] = [{'VERSION()': '5.7.38-log'}]
        elif 'DATABASE()' in query_upper:
            result['columns'] = ['DATABASE()']
            result['rows'] = [{'DATABASE()': self.current_db}]
        elif 'USER()' in query_upper:
            result['columns'] = ['USER()']
            result['rows'] = [{'USER()': 'app_user@192.168.1.%'}]
        elif '@@HOSTNAME' in query_upper:
            result['columns'] = ['@@hostname']
            result['rows'] = [{'@@hostname': 'db-prod-01.internal'}]
        
        return result
    
    def _handle_describe(self, query: str, result: Dict) -> Dict:
        """Handle DESCRIBE queries"""
        parts = query.split()
        if len(parts) >= 2:
            table_name = parts[1].strip('`').strip(';').lower()
            
            result['columns'] = ['Field', 'Type', 'Null', 'Key', 'Default', 'Extra']
            
            # Return fake schema
            common_columns = {
                'id': {'Type': 'int(11)', 'Key': 'PRI', 'Extra': 'auto_increment'},
                'username': {'Type': 'varchar(255)', 'Key': '', 'Extra': ''},
                'password': {'Type': 'varchar(255)', 'Key': '', 'Extra': ''},
                'email': {'Type': 'varchar(255)', 'Key': 'UNI', 'Extra': ''},
                'card_number': {'Type': 'varchar(20)', 'Key': '', 'Extra': ''},
                'cvv': {'Type': 'varchar(4)', 'Key': '', 'Extra': ''},
                'ssn': {'Type': 'varchar(11)', 'Key': '', 'Extra': ''},
                'salary': {'Type': 'decimal(10,2)', 'Key': '', 'Extra': ''},
            }
            
            result['rows'] = [
                {'Field': col, 'Type': info.get('Type', 'varchar(255)'), 
                 'Null': 'YES', 'Key': info.get('Key', ''), 
                 'Default': 'NULL', 'Extra': info.get('Extra', '')}
                for col, info in common_columns.items()
            ][:5]
        
        return result


# =============================================================================
# MYSQL HONEYPOT SESSION
# =============================================================================

@dataclass
class MySQLSession:
    """Represents a MySQL honeypot session"""
    session_id: str
    attacker_ip: str
    attacker_port: int
    start_time: datetime
    username: str = ''
    authenticated: bool = False
    current_db: str = ''
    queries: List[Dict] = field(default_factory=list)
    injection_attempts: int = 0
    sensitive_access: int = 0
    packet_sequence: int = 0


# =============================================================================
# MYSQL HONEYPOT SERVER
# =============================================================================

class MySQLHoneypot:
    """
    MySQL Database Honeypot Server
    
    Detects:
    - SQL injection attempts
    - Credential theft
    - Data exfiltration
    - Privilege escalation
    - Automated attack tools
    """
    
    def __init__(
        self,
        host: str = '0.0.0.0',
        port: int = 3306,
        server_version: str = '5.7.38-log',
        log_callback=None,
        alert_callback=None
    ):
        self.host = host
        self.port = port
        self.server_version = server_version
        self.log_callback = log_callback
        self.alert_callback = alert_callback
        
        self.database = FakeDatabase()
        self.sessions: Dict[str, MySQLSession] = {}
        self._running = False
        self._server_socket = None
        
        # Server capabilities
        self.server_capabilities = (
            MySQLCapability.CLIENT_LONG_PASSWORD |
            MySQLCapability.CLIENT_FOUND_ROWS |
            MySQLCapability.CLIENT_LONG_FLAG |
            MySQLCapability.CLIENT_CONNECT_WITH_DB |
            MySQLCapability.CLIENT_PROTOCOL_41 |
            MySQLCapability.CLIENT_SECURE_CONNECTION |
            MySQLCapability.CLIENT_PLUGIN_AUTH
        )
        
        # Salt for auth
        self.auth_salt = os.urandom(20)
        
        logger.info(f"MySQL Honeypot initialized: {server_version}")
    
    def start(self):
        """Start MySQL honeypot server"""
        self._running = True
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self._server_socket.bind((self.host, self.port))
            self._server_socket.listen(10)
            logger.info(f"MySQL Honeypot listening on {self.host}:{self.port}")
            
            while self._running:
                try:
                    self._server_socket.settimeout(1.0)
                    conn, addr = self._server_socket.accept()
                    thread = threading.Thread(
                        target=self._handle_connection,
                        args=(conn, addr),
                        daemon=True
                    )
                    thread.start()
                except socket.timeout:
                    continue
                except Exception as e:
                    if self._running:
                        logger.error(f"Accept error: {e}")
        
        except PermissionError:
            logger.error(f"Permission denied binding to port {self.port}")
        except Exception as e:
            logger.error(f"Server error: {e}")
        finally:
            if self._server_socket:
                self._server_socket.close()
    
    def stop(self):
        """Stop MySQL honeypot server"""
        self._running = False
        if self._server_socket:
            self._server_socket.close()
        logger.info("MySQL Honeypot stopped")
    
    def _handle_connection(self, conn: socket.socket, addr: Tuple[str, int]):
        """Handle incoming MySQL connection"""
        attacker_ip, attacker_port = addr
        session_id = str(uuid.uuid4())
        
        session = MySQLSession(
            session_id=session_id,
            attacker_ip=attacker_ip,
            attacker_port=attacker_port,
            start_time=datetime.now()
        )
        self.sessions[session_id] = session
        
        logger.info(f"MySQL connection from {attacker_ip}:{attacker_port}")
        self._log_event(session, 'connection', {'status': 'established'})
        
        try:
            conn.settimeout(300)
            
            # Send initial handshake
            handshake = self._build_handshake_packet(session)
            conn.sendall(handshake)
            
            # Receive auth response
            auth_response = self._recv_packet(conn)
            if auth_response:
                self._process_auth(auth_response, session)
                
                # Send OK packet
                ok_packet = self._build_ok_packet(session)
                conn.sendall(ok_packet)
                
                session.authenticated = True
                self._log_event(session, 'authentication', {
                    'username': session.username,
                    'success': True
                })
            
            # Main command loop
            while self._running and session.authenticated:
                try:
                    packet = self._recv_packet(conn)
                    if not packet:
                        break
                    
                    response = self._process_command(packet, session)
                    if response:
                        conn.sendall(response)
                    
                    # Check for suspicious activity
                    self._check_suspicious_activity(session)
                    
                except socket.timeout:
                    continue
                except ConnectionResetError:
                    break
        
        except Exception as e:
            logger.error(f"Session error: {e}")
        finally:
            conn.close()
            self._log_event(session, 'disconnect', {
                'duration': (datetime.now() - session.start_time).total_seconds(),
                'queries': len(session.queries),
                'injection_attempts': session.injection_attempts
            })
    
    def _recv_packet(self, conn: socket.socket) -> Optional[bytes]:
        """Receive MySQL packet"""
        try:
            # Read 4-byte header
            header = b''
            while len(header) < 4:
                chunk = conn.recv(4 - len(header))
                if not chunk:
                    return None
                header += chunk
            
            # Parse header
            length = struct.unpack('<I', header[:3] + b'\x00')[0]
            sequence = header[3]
            
            if length == 0:
                return b''
            
            if length > 16 * 1024 * 1024:  # 16MB limit
                logger.warning(f"Oversized packet: {length} bytes")
                return None
            
            # Read payload
            payload = b''
            while len(payload) < length:
                chunk = conn.recv(length - len(payload))
                if not chunk:
                    return None
                payload += chunk
            
            return payload
            
        except Exception as e:
            logger.debug(f"Recv error: {e}")
            return None
    
    def _build_packet(self, payload: bytes, sequence: int) -> bytes:
        """Build MySQL packet with header"""
        length = len(payload)
        header = struct.pack('<I', length)[:3] + bytes([sequence])
        return header + payload
    
    def _build_handshake_packet(self, session: MySQLSession) -> bytes:
        """Build MySQL handshake packet"""
        payload = bytearray()
        
        # Protocol version
        payload.append(10)
        
        # Server version (null-terminated)
        payload.extend(self.server_version.encode() + b'\x00')
        
        # Connection ID
        payload.extend(struct.pack('<I', 1))
        
        # Auth plugin data part 1 (8 bytes)
        payload.extend(self.auth_salt[:8])
        
        # Filler
        payload.append(0x00)
        
        # Capability flags (lower 2 bytes)
        payload.extend(struct.pack('<H', self.server_capabilities & 0xFFFF))
        
        # Character set
        payload.append(33)  # utf8_general_ci
        
        # Status flags
        payload.extend(struct.pack('<H', 0x0002))
        
        # Capability flags (upper 2 bytes)
        payload.extend(struct.pack('<H', (self.server_capabilities >> 16) & 0xFFFF))
        
        # Auth plugin data length
        payload.append(21)
        
        # Reserved
        payload.extend(b'\x00' * 10)
        
        # Auth plugin data part 2 (12 bytes + null)
        payload.extend(self.auth_salt[8:20])
        payload.append(0x00)
        
        # Auth plugin name
        payload.extend(b'mysql_native_password\x00')
        
        session.packet_sequence = 0
        return self._build_packet(bytes(payload), 0)
    
    def _process_auth(self, packet: bytes, session: MySQLSession):
        """Process authentication packet"""
        try:
            if len(packet) < 32:
                return
            
            pos = 0
            
            # Client capabilities (4 bytes)
            capabilities = struct.unpack('<I', packet[pos:pos+4])[0]
            pos += 4
            
            # Max packet size (4 bytes)
            pos += 4
            
            # Character set (1 byte)
            pos += 1
            
            # Reserved (23 bytes)
            pos += 23
            
            # Username (null-terminated)
            username_end = packet.find(b'\x00', pos)
            if username_end != -1:
                session.username = packet[pos:username_end].decode('utf-8', errors='ignore')
                pos = username_end + 1
            
            logger.info(f"MySQL auth attempt: {session.username} from {session.attacker_ip}")
            
        except Exception as e:
            logger.debug(f"Auth parse error: {e}")
    
    def _build_ok_packet(self, session: MySQLSession) -> bytes:
        """Build OK response packet"""
        payload = bytearray()
        
        # Header (OK)
        payload.append(0x00)
        
        # Affected rows
        payload.append(0x00)
        
        # Last insert ID
        payload.append(0x00)
        
        # Status flags
        payload.extend(struct.pack('<H', 0x0002))
        
        # Warnings
        payload.extend(struct.pack('<H', 0))
        
        session.packet_sequence += 1
        return self._build_packet(bytes(payload), session.packet_sequence)
    
    def _build_error_packet(self, session: MySQLSession, error_code: int, message: str) -> bytes:
        """Build error response packet"""
        payload = bytearray()
        
        # Header (ERR)
        payload.append(0xFF)
        
        # Error code
        payload.extend(struct.pack('<H', error_code))
        
        # SQL state marker
        payload.append(ord('#'))
        
        # SQL state (5 chars)
        payload.extend(b'42000')
        
        # Error message
        payload.extend(message.encode('utf-8'))
        
        session.packet_sequence += 1
        return self._build_packet(bytes(payload), session.packet_sequence)
    
    def _process_command(self, packet: bytes, session: MySQLSession) -> Optional[bytes]:
        """Process MySQL command"""
        if not packet:
            return None
        
        command = packet[0]
        data = packet[1:] if len(packet) > 1 else b''
        
        if command == MySQLCommand.COM_QUIT.value:
            logger.debug(f"Session {session.session_id} quit")
            return None
        
        elif command == MySQLCommand.COM_PING.value:
            return self._build_ok_packet(session)
        
        elif command == MySQLCommand.COM_INIT_DB.value:
            db_name = data.decode('utf-8', errors='ignore').strip()
            session.current_db = db_name
            self.database.current_db = db_name
            self._log_event(session, 'use_database', {'database': db_name})
            return self._build_ok_packet(session)
        
        elif command == MySQLCommand.COM_QUERY.value:
            query = data.decode('utf-8', errors='ignore').strip()
            return self._handle_query(query, session)
        
        elif command == MySQLCommand.COM_FIELD_LIST.value:
            return self._build_ok_packet(session)
        
        return self._build_ok_packet(session)
    
    def _handle_query(self, query: str, session: MySQLSession) -> bytes:
        """Handle SQL query"""
        logger.info(f"Query from {session.attacker_ip}: {query[:100]}...")
        
        # Execute against fake database
        result = self.database.execute_query(query, session.attacker_ip)
        
        # Record query
        session.queries.append({
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'is_injection': result.get('is_injection', False),
            'is_sensitive': result.get('is_sensitive', False)
        })
        
        # Update counters
        if result.get('is_injection'):
            session.injection_attempts += 1
            self._alert(session, 'sql_injection', {
                'query': query,
                'message': 'SQL injection attempt detected'
            })
        
        if result.get('is_sensitive'):
            session.sensitive_access += 1
            self._alert(session, 'sensitive_access', {
                'query': query,
                'message': 'Access to sensitive data detected'
            })
        
        self._log_event(session, 'query', {
            'query': query[:500],
            'is_injection': result.get('is_injection'),
            'is_sensitive': result.get('is_sensitive')
        })
        
        # Build result set response
        if result.get('rows'):
            return self._build_resultset(result, session)
        else:
            return self._build_ok_packet(session)
    
    def _build_resultset(self, result: Dict, session: MySQLSession) -> bytes:
        """Build MySQL result set response"""
        packets = []
        
        columns = result.get('columns', [])
        rows = result.get('rows', [])
        
        # Column count packet
        session.packet_sequence += 1
        count_payload = self._encode_length(len(columns))
        packets.append(self._build_packet(count_payload, session.packet_sequence))
        
        # Column definition packets
        for col in columns:
            session.packet_sequence += 1
            col_payload = self._build_column_def(col)
            packets.append(self._build_packet(col_payload, session.packet_sequence))
        
        # EOF packet after columns
        session.packet_sequence += 1
        eof_payload = bytes([0xFE, 0x00, 0x00, 0x02, 0x00])
        packets.append(self._build_packet(eof_payload, session.packet_sequence))
        
        # Row data packets
        for row in rows[:100]:  # Limit rows
            session.packet_sequence += 1
            row_payload = self._build_row(columns, row)
            packets.append(self._build_packet(row_payload, session.packet_sequence))
        
        # Final EOF packet
        session.packet_sequence += 1
        packets.append(self._build_packet(eof_payload, session.packet_sequence))
        
        return b''.join(packets)
    
    def _encode_length(self, length: int) -> bytes:
        """Encode length-encoded integer"""
        if length < 251:
            return bytes([length])
        elif length < 65536:
            return bytes([0xFC]) + struct.pack('<H', length)
        elif length < 16777216:
            return bytes([0xFD]) + struct.pack('<I', length)[:3]
        else:
            return bytes([0xFE]) + struct.pack('<Q', length)
    
    def _build_column_def(self, name: str) -> bytes:
        """Build column definition packet"""
        payload = bytearray()
        
        # Catalog
        payload.extend(self._encode_length(3))
        payload.extend(b'def')
        
        # Schema
        payload.extend(self._encode_length(0))
        
        # Table
        payload.extend(self._encode_length(0))
        
        # Org table
        payload.extend(self._encode_length(0))
        
        # Name
        name_bytes = name.encode('utf-8')
        payload.extend(self._encode_length(len(name_bytes)))
        payload.extend(name_bytes)
        
        # Org name
        payload.extend(self._encode_length(len(name_bytes)))
        payload.extend(name_bytes)
        
        # Length of fixed fields
        payload.append(0x0C)
        
        # Character set
        payload.extend(struct.pack('<H', 33))  # utf8
        
        # Column length
        payload.extend(struct.pack('<I', 255))
        
        # Column type (VARCHAR)
        payload.append(253)
        
        # Flags
        payload.extend(struct.pack('<H', 0))
        
        # Decimals
        payload.append(0)
        
        # Filler
        payload.extend(b'\x00\x00')
        
        return bytes(payload)
    
    def _build_row(self, columns: List[str], row: Dict) -> bytes:
        """Build row data packet"""
        payload = bytearray()
        
        for col in columns:
            value = str(row.get(col, ''))
            value_bytes = value.encode('utf-8')
            payload.extend(self._encode_length(len(value_bytes)))
            payload.extend(value_bytes)
        
        return bytes(payload)
    
    def _check_suspicious_activity(self, session: MySQLSession):
        """Check for suspicious activity patterns"""
        # Too many injection attempts
        if session.injection_attempts >= 5:
            self._alert(session, 'attack_pattern', {
                'type': 'sql_injection_campaign',
                'attempts': session.injection_attempts,
                'message': 'Multiple SQL injection attempts detected'
            })
        
        # Accessing multiple sensitive tables
        if session.sensitive_access >= 3:
            self._alert(session, 'data_exfiltration', {
                'tables_accessed': session.sensitive_access,
                'message': 'Potential data exfiltration in progress'
            })
    
    def _log_event(self, session: MySQLSession, event_type: str, details: Dict):
        """Log MySQL event"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'session_id': session.session_id,
            'attacker_ip': session.attacker_ip,
            'username': session.username,
            'event_type': event_type,
            'details': details
        }
        
        logger.debug(f"MySQL Event: {event_type}")
        
        if self.log_callback:
            try:
                self.log_callback(event)
            except Exception as e:
                logger.error(f"Log callback error: {e}")
    
    def _alert(self, session: MySQLSession, alert_type: str, details: Dict):
        """Generate security alert"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'severity': 'high' if 'injection' in alert_type else 'medium',
            'alert_type': f'mysql_{alert_type}',
            'session_id': session.session_id,
            'attacker_ip': session.attacker_ip,
            'username': session.username,
            'details': details
        }
        
        logger.warning(f"🚨 MySQL ALERT: {alert_type} - {details.get('message', '')}")
        
        if self.alert_callback:
            try:
                self.alert_callback(alert)
            except Exception as e:
                logger.error(f"Alert callback error: {e}")


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    def log_handler(event):
        print(f"LOG: {event['event_type']} from {event['attacker_ip']}")
    
    def alert_handler(alert):
        print(f"🚨 ALERT: {alert['alert_type']} - {alert['details'].get('message', '')}")
    
    honeypot = MySQLHoneypot(
        port=33306,  # Non-privileged port for testing
        log_callback=log_handler,
        alert_callback=alert_handler
    )
    
    print("Starting MySQL Honeypot on port 33306...")
    print("Connect with: mysql -h 127.0.0.1 -P 33306 -u admin -p")
    print("Press Ctrl+C to stop")
    
    try:
        honeypot.start()
    except KeyboardInterrupt:
        honeypot.stop()
        print("\nMySQL Honeypot stopped")
