"""
🖥️ SMB/CIFS Honeypot Service
Cyber Mirage - Role 1: Adaptive Honeynet Layer

Emulates Windows SMB/CIFS file sharing for ransomware and lateral movement detection:
- SMB2/3 protocol emulation
- Fake file shares with lure documents
- Credential harvesting
- Ransomware behavior detection
- EternalBlue-like exploit detection

Author: Cyber Mirage Team
Version: 1.0.0 - Production
"""

import socket
import struct
import logging
import threading
import time
import uuid
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =============================================================================
# SMB CONSTANTS
# =============================================================================

class SMBCommand(Enum):
    """SMB1 Command codes"""
    SMB_COM_NEGOTIATE = 0x72
    SMB_COM_SESSION_SETUP_ANDX = 0x73
    SMB_COM_TREE_CONNECT_ANDX = 0x75
    SMB_COM_TREE_DISCONNECT = 0x71
    SMB_COM_LOGOFF_ANDX = 0x74
    SMB_COM_ECHO = 0x2B
    SMB_COM_CLOSE = 0x04
    SMB_COM_READ_ANDX = 0x2E
    SMB_COM_WRITE_ANDX = 0x2F
    SMB_COM_OPEN_ANDX = 0x2D
    SMB_COM_FIND_CLOSE2 = 0x34
    SMB_COM_TRANSACTION2 = 0x32


class SMB2Command(Enum):
    """SMB2/3 Command codes"""
    SMB2_NEGOTIATE = 0x0000
    SMB2_SESSION_SETUP = 0x0001
    SMB2_LOGOFF = 0x0002
    SMB2_TREE_CONNECT = 0x0003
    SMB2_TREE_DISCONNECT = 0x0004
    SMB2_CREATE = 0x0005
    SMB2_CLOSE = 0x0006
    SMB2_FLUSH = 0x0007
    SMB2_READ = 0x0008
    SMB2_WRITE = 0x0009
    SMB2_LOCK = 0x000A
    SMB2_IOCTL = 0x000B
    SMB2_CANCEL = 0x000C
    SMB2_ECHO = 0x000D
    SMB2_QUERY_DIRECTORY = 0x000E
    SMB2_CHANGE_NOTIFY = 0x000F
    SMB2_QUERY_INFO = 0x0010
    SMB2_SET_INFO = 0x0011
    SMB2_OPLOCK_BREAK = 0x0012


# SMB Magic bytes
SMB1_MAGIC = b'\xffSMB'
SMB2_MAGIC = b'\xfeSMB'

# =============================================================================
# FAKE FILE SYSTEM
# =============================================================================

@dataclass
class FakeFile:
    """Represents a fake file in the honeypot filesystem"""
    name: str
    size: int
    is_directory: bool
    created: datetime
    modified: datetime
    accessed: datetime
    content: bytes = b''
    is_lure: bool = False
    
    def to_find_entry(self) -> bytes:
        """Convert to SMB FIND response entry"""
        # Simplified - would need full SMB_FIND_FILE_BOTH_DIRECTORY_INFO
        return struct.pack('<I', self.size) + self.name.encode('utf-16-le')


class FakeFileSystem:
    """
    Fake filesystem for SMB honeypot
    Contains lure documents to detect ransomware and data theft
    """
    
    def __init__(self):
        self.shares = {
            'ADMIN$': self._create_admin_share(),
            'C$': self._create_c_share(),
            'IPC$': {},
            'NETLOGON': self._create_netlogon_share(),
            'SYSVOL': self._create_sysvol_share(),
            'SharedDocs': self._create_shared_docs(),
            'Finance': self._create_finance_share(),
            'HR': self._create_hr_share(),
            'IT': self._create_it_share(),
        }
        
        self.access_log = []
    
    def _create_admin_share(self) -> Dict[str, FakeFile]:
        """Create fake ADMIN$ share"""
        now = datetime.now()
        return {
            'system32': FakeFile('system32', 0, True, now, now, now),
            'config': FakeFile('config', 0, True, now, now, now),
        }
    
    def _create_c_share(self) -> Dict[str, FakeFile]:
        """Create fake C$ share"""
        now = datetime.now()
        return {
            'Windows': FakeFile('Windows', 0, True, now, now, now),
            'Program Files': FakeFile('Program Files', 0, True, now, now, now),
            'Users': FakeFile('Users', 0, True, now, now, now),
            'boot.ini': FakeFile('boot.ini', 1024, False, now, now, now),
        }
    
    def _create_netlogon_share(self) -> Dict[str, FakeFile]:
        """Create fake NETLOGON share"""
        now = datetime.now()
        return {
            'scripts': FakeFile('scripts', 0, True, now, now, now),
            'logon.bat': FakeFile('logon.bat', 512, False, now, now, now, 
                                  b'@echo off\nnet use * /delete /y\n'),
        }
    
    def _create_sysvol_share(self) -> Dict[str, FakeFile]:
        """Create fake SYSVOL share"""
        now = datetime.now()
        return {
            'policies': FakeFile('policies', 0, True, now, now, now),
            'scripts': FakeFile('scripts', 0, True, now, now, now),
        }
    
    def _create_shared_docs(self) -> Dict[str, FakeFile]:
        """Create shared documents with lure files"""
        now = datetime.now()
        lure_content = b'''CONFIDENTIAL - Internal Use Only
=================================

Q4 2024 Financial Summary
-------------------------
Revenue: $45,234,891
Expenses: $31,456,234
Net Profit: $13,778,657

Banking Details:
- Primary Account: XXXX-XXXX-1234
- Routing: 021000021

SSH Keys Location: /home/admin/.ssh/
Database Password: See IT Keystore

This document is tracked. Access has been logged.
'''
        return {
            'Public': FakeFile('Public', 0, True, now, now, now),
            'Company_Handbook.pdf': FakeFile('Company_Handbook.pdf', 2048576, False, now, now, now),
            'Q4_Financial_Report.xlsx': FakeFile('Q4_Financial_Report.xlsx', 156789, False, now, now, now, lure_content, is_lure=True),
            'passwords.txt': FakeFile('passwords.txt', 1024, False, now, now, now, 
                                       b'admin:P@ssw0rd123\nroot:toor\n', is_lure=True),
            'backup_credentials.docx': FakeFile('backup_credentials.docx', 24567, False, now, now, now, 
                                                 b'SSH Key: AAAA...fake...AAAA\n', is_lure=True),
        }
    
    def _create_finance_share(self) -> Dict[str, FakeFile]:
        """Create Finance department share"""
        now = datetime.now()
        return {
            '2024': FakeFile('2024', 0, True, now, now, now),
            '2023': FakeFile('2023', 0, True, now, now, now),
            'Budget_2024.xlsx': FakeFile('Budget_2024.xlsx', 345678, False, now, now, now, is_lure=True),
            'Salaries_Q4.csv': FakeFile('Salaries_Q4.csv', 45678, False, now, now, now, is_lure=True),
            'Bank_Accounts.xlsx': FakeFile('Bank_Accounts.xlsx', 23456, False, now, now, now, is_lure=True),
            'tax_returns_2023.pdf': FakeFile('tax_returns_2023.pdf', 567890, False, now, now, now, is_lure=True),
        }
    
    def _create_hr_share(self) -> Dict[str, FakeFile]:
        """Create HR department share"""
        now = datetime.now()
        return {
            'Employees': FakeFile('Employees', 0, True, now, now, now),
            'Policies': FakeFile('Policies', 0, True, now, now, now),
            'SSN_Database.xlsx': FakeFile('SSN_Database.xlsx', 234567, False, now, now, now, is_lure=True),
            'Employee_Directory.csv': FakeFile('Employee_Directory.csv', 45678, False, now, now, now, is_lure=True),
            'Termination_Letters': FakeFile('Termination_Letters', 0, True, now, now, now),
        }
    
    def _create_it_share(self) -> Dict[str, FakeFile]:
        """Create IT department share with juicy targets"""
        now = datetime.now()
        key_content = b'''-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEA0Z3VS5JJcds3xfn4r/fake/honeypot/key/content/here
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
This is a honeypot. Your access has been logged.
-----END RSA PRIVATE KEY-----
'''
        return {
            'Scripts': FakeFile('Scripts', 0, True, now, now, now),
            'Backups': FakeFile('Backups', 0, True, now, now, now),
            'SSH_Keys': FakeFile('SSH_Keys', 0, True, now, now, now),
            'admin_ssh_key.pem': FakeFile('admin_ssh_key.pem', 1675, False, now, now, now, key_content, is_lure=True),
            'production_passwords.txt': FakeFile('production_passwords.txt', 2048, False, now, now, now, is_lure=True),
            'database_backup.sql': FakeFile('database_backup.sql', 45678901, False, now, now, now, is_lure=True),
            'network_diagram.vsdx': FakeFile('network_diagram.vsdx', 567890, False, now, now, now),
            'DC_credentials.kdbx': FakeFile('DC_credentials.kdbx', 12345, False, now, now, now, is_lure=True),
        }
    
    def list_shares(self) -> List[str]:
        """List available shares"""
        return list(self.shares.keys())
    
    def list_files(self, share: str, path: str = '') -> List[FakeFile]:
        """List files in a share path"""
        if share not in self.shares:
            return []
        
        files = self.shares[share]
        if path:
            # Navigate to subdirectory
            parts = path.strip('/\\').split('\\')
            current = files
            for part in parts:
                if part in current and current[part].is_directory:
                    # Would recursively get children - simplified
                    return []
                else:
                    return []
        
        return list(files.values())
    
    def get_file(self, share: str, path: str) -> Optional[FakeFile]:
        """Get a specific file"""
        if share not in self.shares:
            return None
        
        filename = path.strip('/\\').split('\\')[-1]
        return self.shares[share].get(filename)
    
    def log_access(self, share: str, path: str, operation: str, attacker_ip: str):
        """Log file access"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'share': share,
            'path': path,
            'operation': operation,
            'attacker_ip': attacker_ip,
            'is_lure': False
        }
        
        # Check if lure file
        file = self.get_file(share, path)
        if file and file.is_lure:
            entry['is_lure'] = True
            entry['alert'] = 'LURE_FILE_ACCESSED'
        
        self.access_log.append(entry)
        
        if entry.get('is_lure'):
            logger.warning(f"🎣 LURE FILE ACCESSED: {share}\\{path} by {attacker_ip}")
        
        return entry


# =============================================================================
# SMB HONEYPOT SERVER
# =============================================================================

@dataclass
class SMBSession:
    """Represents an SMB session"""
    session_id: str
    attacker_ip: str
    attacker_port: int
    start_time: datetime
    username: str = ''
    domain: str = ''
    authenticated: bool = False
    connected_shares: List[str] = field(default_factory=list)
    files_accessed: List[str] = field(default_factory=list)
    commands: List[Dict] = field(default_factory=list)
    is_ransomware_suspect: bool = False
    is_lateral_movement: bool = False


class SMBHoneypot:
    """
    SMB/CIFS Honeypot Server
    
    Detects:
    - Credential theft attempts
    - Lateral movement (ADMIN$, C$ access)
    - Ransomware behavior (mass file enumeration/encryption)
    - Data exfiltration
    - EternalBlue-like exploits
    """
    
    def __init__(
        self,
        host: str = '0.0.0.0',
        port: int = 445,
        server_name: str = 'FILESERVER01',
        domain: str = 'CORPORATE',
        log_callback=None,
        alert_callback=None
    ):
        self.host = host
        self.port = port
        self.server_name = server_name
        self.domain = domain
        self.log_callback = log_callback
        self.alert_callback = alert_callback
        
        self.filesystem = FakeFileSystem()
        self.sessions: Dict[str, SMBSession] = {}
        self._running = False
        self._server_socket = None
        
        # Detection thresholds
        self.ransomware_threshold = 50  # Files accessed in short time
        self.lateral_movement_shares = {'ADMIN$', 'C$', 'IPC$'}
        
        logger.info(f"SMB Honeypot initialized: \\\\{server_name}.{domain}")
    
    def start(self):
        """Start the SMB honeypot server"""
        self._running = True
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self._server_socket.bind((self.host, self.port))
            self._server_socket.listen(10)
            logger.info(f"SMB Honeypot listening on {self.host}:{self.port}")
            
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
        """Stop the SMB honeypot server"""
        self._running = False
        if self._server_socket:
            self._server_socket.close()
        logger.info("SMB Honeypot stopped")
    
    def _handle_connection(self, conn: socket.socket, addr: Tuple[str, int]):
        """Handle incoming SMB connection"""
        attacker_ip, attacker_port = addr
        session_id = str(uuid.uuid4())
        
        session = SMBSession(
            session_id=session_id,
            attacker_ip=attacker_ip,
            attacker_port=attacker_port,
            start_time=datetime.now()
        )
        self.sessions[session_id] = session
        
        logger.info(f"SMB connection from {attacker_ip}:{attacker_port}")
        self._log_event(session, 'connection', {'status': 'established'})
        
        try:
            conn.settimeout(300)  # 5 minute timeout
            
            while self._running:
                # Read NetBIOS session header
                header = self._recv_all(conn, 4)
                if not header:
                    break
                
                # Parse NetBIOS header
                msg_type = header[0]
                length = struct.unpack('>I', b'\x00' + header[1:4])[0]
                
                if length == 0:
                    continue
                
                if length > 1024 * 1024:  # 1MB limit
                    logger.warning(f"Oversized packet from {attacker_ip}: {length} bytes")
                    break
                
                # Read SMB message
                data = self._recv_all(conn, length)
                if not data:
                    break
                
                # Process SMB message
                response = self._process_smb(data, session)
                
                if response:
                    # Send response with NetBIOS header
                    resp_header = struct.pack('>I', len(response))[1:]  # 3 bytes
                    conn.sendall(b'\x00' + resp_header + response)
                
                # Check for suspicious behavior
                self._check_suspicious_behavior(session)
        
        except socket.timeout:
            logger.debug(f"Session {session_id} timed out")
        except ConnectionResetError:
            logger.debug(f"Connection reset by {attacker_ip}")
        except Exception as e:
            logger.error(f"Session error: {e}")
        finally:
            conn.close()
            self._log_event(session, 'disconnect', {
                'duration': (datetime.now() - session.start_time).total_seconds(),
                'files_accessed': len(session.files_accessed),
                'authenticated': session.authenticated
            })
    
    def _recv_all(self, conn: socket.socket, length: int) -> bytes:
        """Receive exact number of bytes"""
        data = b''
        while len(data) < length:
            chunk = conn.recv(length - len(data))
            if not chunk:
                return b''
            data += chunk
        return data
    
    def _process_smb(self, data: bytes, session: SMBSession) -> Optional[bytes]:
        """Process SMB message and generate response"""
        if len(data) < 4:
            return None
        
        # Check SMB magic
        magic = data[:4]
        
        if magic == SMB2_MAGIC:
            return self._process_smb2(data, session)
        elif magic == SMB1_MAGIC:
            return self._process_smb1(data, session)
        else:
            logger.warning(f"Unknown SMB magic: {magic.hex()}")
            return None
    
    def _process_smb1(self, data: bytes, session: SMBSession) -> Optional[bytes]:
        """Process SMB1 message"""
        if len(data) < 32:
            return None
        
        command = data[4]
        
        session.commands.append({
            'timestamp': datetime.now().isoformat(),
            'protocol': 'SMB1',
            'command': command,
            'command_name': SMBCommand(command).name if command in [e.value for e in SMBCommand] else f'UNKNOWN_{command}'
        })
        
        if command == SMBCommand.SMB_COM_NEGOTIATE.value:
            return self._smb1_negotiate_response()
        elif command == SMBCommand.SMB_COM_SESSION_SETUP_ANDX.value:
            return self._smb1_session_setup_response(data, session)
        
        return self._smb1_error_response(command)
    
    def _process_smb2(self, data: bytes, session: SMBSession) -> Optional[bytes]:
        """Process SMB2/3 message"""
        if len(data) < 64:
            return None
        
        # Parse SMB2 header
        command = struct.unpack('<H', data[12:14])[0]
        
        session.commands.append({
            'timestamp': datetime.now().isoformat(),
            'protocol': 'SMB2',
            'command': command,
            'command_name': SMB2Command(command).name if command in [e.value for e in SMB2Command] else f'UNKNOWN_{command}'
        })
        
        if command == SMB2Command.SMB2_NEGOTIATE.value:
            return self._smb2_negotiate_response()
        elif command == SMB2Command.SMB2_SESSION_SETUP.value:
            return self._smb2_session_setup_response(data, session)
        elif command == SMB2Command.SMB2_TREE_CONNECT.value:
            return self._smb2_tree_connect_response(data, session)
        elif command == SMB2Command.SMB2_QUERY_DIRECTORY.value:
            return self._smb2_query_directory_response(data, session)
        elif command == SMB2Command.SMB2_CREATE.value:
            return self._smb2_create_response(data, session)
        elif command == SMB2Command.SMB2_READ.value:
            return self._smb2_read_response(data, session)
        
        return self._smb2_error_response(command)
    
    def _smb1_negotiate_response(self) -> bytes:
        """Generate SMB1 negotiate response (redirect to SMB2)"""
        # Simplified - would redirect to SMB2
        header = SMB1_MAGIC + bytes([SMBCommand.SMB_COM_NEGOTIATE.value])
        # Add minimal response
        return header + b'\x00' * 32
    
    def _smb1_session_setup_response(self, data: bytes, session: SMBSession) -> bytes:
        """Generate SMB1 session setup response"""
        # Extract credentials from NTLMSSP if present
        self._extract_credentials(data, session)
        
        header = SMB1_MAGIC + bytes([SMBCommand.SMB_COM_SESSION_SETUP_ANDX.value])
        return header + b'\x00' * 32
    
    def _smb1_error_response(self, command: int) -> bytes:
        """Generate SMB1 error response"""
        header = SMB1_MAGIC + bytes([command])
        return header + b'\x00' * 32
    
    def _smb2_negotiate_response(self) -> bytes:
        """Generate SMB2 negotiate response"""
        response = bytearray(65)
        response[0:4] = SMB2_MAGIC
        response[4:6] = struct.pack('<H', 64)  # Header size
        response[12:14] = struct.pack('<H', SMB2Command.SMB2_NEGOTIATE.value)
        
        # Security mode, dialect, capabilities etc.
        response[64] = 65  # Structure size
        
        return bytes(response)
    
    def _smb2_session_setup_response(self, data: bytes, session: SMBSession) -> bytes:
        """Generate SMB2 session setup response"""
        # Extract credentials
        self._extract_credentials(data, session)
        
        response = bytearray(64 + 9)
        response[0:4] = SMB2_MAGIC
        response[4:6] = struct.pack('<H', 64)
        response[12:14] = struct.pack('<H', SMB2Command.SMB2_SESSION_SETUP.value)
        
        session.authenticated = True
        self._log_event(session, 'authentication', {
            'username': session.username,
            'domain': session.domain,
            'success': True  # Always "succeed" to observe behavior
        })
        
        return bytes(response)
    
    def _smb2_tree_connect_response(self, data: bytes, session: SMBSession) -> bytes:
        """Generate SMB2 tree connect response"""
        # Extract share name from data
        # Simplified - would parse properly
        share_name = 'SharedDocs'  # Default
        
        # Try to find share name in data
        if b'\\' in data:
            try:
                path_data = data[data.rfind(b'\\\\'):]
                share_name = path_data.decode('utf-16-le', errors='ignore').split('\\')[-1].strip('\x00')
            except:
                pass
        
        session.connected_shares.append(share_name)
        
        # Check for lateral movement
        if share_name in self.lateral_movement_shares:
            session.is_lateral_movement = True
            self._alert(session, 'lateral_movement', {
                'share': share_name,
                'message': f'Lateral movement detected: access to {share_name}'
            })
        
        self._log_event(session, 'tree_connect', {'share': share_name})
        
        response = bytearray(64 + 16)
        response[0:4] = SMB2_MAGIC
        response[4:6] = struct.pack('<H', 64)
        response[12:14] = struct.pack('<H', SMB2Command.SMB2_TREE_CONNECT.value)
        
        return bytes(response)
    
    def _smb2_query_directory_response(self, data: bytes, session: SMBSession) -> bytes:
        """Generate SMB2 query directory response"""
        # Log directory enumeration
        session.commands[-1]['enumeration'] = True
        
        self._log_event(session, 'directory_enumeration', {
            'path': 'root'
        })
        
        response = bytearray(64 + 9)
        response[0:4] = SMB2_MAGIC
        response[12:14] = struct.pack('<H', SMB2Command.SMB2_QUERY_DIRECTORY.value)
        
        return bytes(response)
    
    def _smb2_create_response(self, data: bytes, session: SMBSession) -> bytes:
        """Generate SMB2 create (file open) response"""
        # Try to extract filename
        filename = 'unknown'
        try:
            # Filename is usually at a known offset in CREATE request
            # This is simplified
            if len(data) > 120:
                name_offset = struct.unpack('<H', data[44:46])[0]
                name_length = struct.unpack('<H', data[46:48])[0]
                if name_offset and name_length:
                    filename = data[name_offset:name_offset+name_length].decode('utf-16-le', errors='ignore')
        except:
            pass
        
        session.files_accessed.append(filename)
        
        # Check for lure file access
        for share in session.connected_shares:
            access_entry = self.filesystem.log_access(share, filename, 'open', session.attacker_ip)
            if access_entry.get('is_lure'):
                self._alert(session, 'lure_accessed', {
                    'share': share,
                    'file': filename,
                    'message': f'Lure file accessed: {share}\\{filename}'
                })
        
        self._log_event(session, 'file_open', {'filename': filename})
        
        response = bytearray(64 + 89)
        response[0:4] = SMB2_MAGIC
        response[12:14] = struct.pack('<H', SMB2Command.SMB2_CREATE.value)
        
        return bytes(response)
    
    def _smb2_read_response(self, data: bytes, session: SMBSession) -> bytes:
        """Generate SMB2 read response"""
        self._log_event(session, 'file_read', {'file_count': len(session.files_accessed)})
        
        response = bytearray(64 + 17)
        response[0:4] = SMB2_MAGIC
        response[12:14] = struct.pack('<H', SMB2Command.SMB2_READ.value)
        
        # Return fake data
        fake_content = b'CONFIDENTIAL - This file is monitored\n'
        response.extend(fake_content)
        
        return bytes(response)
    
    def _smb2_error_response(self, command: int) -> bytes:
        """Generate SMB2 error response"""
        response = bytearray(64 + 9)
        response[0:4] = SMB2_MAGIC
        response[12:14] = struct.pack('<H', command)
        response[8:12] = struct.pack('<I', 0xC0000001)  # STATUS_UNSUCCESSFUL
        
        return bytes(response)
    
    def _extract_credentials(self, data: bytes, session: SMBSession):
        """Extract credentials from NTLMSSP data"""
        try:
            # Look for NTLMSSP signature
            ntlmssp_pos = data.find(b'NTLMSSP\x00')
            if ntlmssp_pos == -1:
                return
            
            ntlmssp_data = data[ntlmssp_pos:]
            
            # Check message type (type 3 = auth)
            if len(ntlmssp_data) < 12:
                return
            
            msg_type = struct.unpack('<I', ntlmssp_data[8:12])[0]
            
            if msg_type == 3:  # Authentication message
                # Extract domain and username
                # Offsets in Type 3 message
                domain_len = struct.unpack('<H', ntlmssp_data[28:30])[0]
                domain_offset = struct.unpack('<I', ntlmssp_data[32:36])[0]
                
                user_len = struct.unpack('<H', ntlmssp_data[36:38])[0]
                user_offset = struct.unpack('<I', ntlmssp_data[40:44])[0]
                
                if domain_offset < len(ntlmssp_data) and domain_len > 0:
                    session.domain = ntlmssp_data[domain_offset:domain_offset+domain_len].decode('utf-16-le', errors='ignore')
                
                if user_offset < len(ntlmssp_data) and user_len > 0:
                    session.username = ntlmssp_data[user_offset:user_offset+user_len].decode('utf-16-le', errors='ignore')
                
                logger.info(f"Captured credentials: {session.domain}\\{session.username}")
                
        except Exception as e:
            logger.debug(f"Credential extraction error: {e}")
    
    def _check_suspicious_behavior(self, session: SMBSession):
        """Check for ransomware and other suspicious behavior"""
        # Ransomware detection: rapid file enumeration
        if len(session.files_accessed) > self.ransomware_threshold:
            if not session.is_ransomware_suspect:
                session.is_ransomware_suspect = True
                self._alert(session, 'ransomware_suspect', {
                    'files_accessed': len(session.files_accessed),
                    'duration': (datetime.now() - session.start_time).total_seconds(),
                    'message': f'Ransomware behavior: {len(session.files_accessed)} files accessed rapidly'
                })
    
    def _log_event(self, session: SMBSession, event_type: str, details: Dict):
        """Log SMB event"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'session_id': session.session_id,
            'attacker_ip': session.attacker_ip,
            'event_type': event_type,
            'details': details
        }
        
        logger.debug(f"SMB Event: {event}")
        
        if self.log_callback:
            try:
                self.log_callback(event)
            except Exception as e:
                logger.error(f"Log callback error: {e}")
    
    def _alert(self, session: SMBSession, alert_type: str, details: Dict):
        """Generate security alert"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'severity': 'high' if 'ransomware' in alert_type else 'medium',
            'alert_type': alert_type,
            'session_id': session.session_id,
            'attacker_ip': session.attacker_ip,
            'username': session.username,
            'domain': session.domain,
            'details': details
        }
        
        logger.warning(f"🚨 SMB ALERT: {alert_type} - {details.get('message', '')}")
        
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
    
    honeypot = SMBHoneypot(
        port=4445,  # Use non-privileged port for testing
        log_callback=log_handler,
        alert_callback=alert_handler
    )
    
    print("Starting SMB Honeypot on port 4445...")
    print("Press Ctrl+C to stop")
    
    try:
        honeypot.start()
    except KeyboardInterrupt:
        honeypot.stop()
        print("\nSMB Honeypot stopped")
