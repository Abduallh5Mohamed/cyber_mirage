"""
📁 Enhanced Filesystem Emulation
Cyber Mirage - Role 2: Fake Service Simulation Engine

Provides realistic filesystem emulation for honeypots:
- Hierarchical directory structure
- Fake files with realistic metadata
- Lure documents for detecting data exfiltration
- Dynamic content generation
- Access logging and alerting

Author: Cyber Mirage Team
Version: 1.0.0 - Production
"""

import os
import random
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =============================================================================
# ENUMERATIONS
# =============================================================================

class FileType(Enum):
    """File types"""
    FILE = "file"
    DIRECTORY = "directory"
    SYMLINK = "symlink"
    DEVICE = "device"


class FileCategory(Enum):
    """File categories for classification"""
    SYSTEM = "system"
    CONFIG = "config"
    LOG = "log"
    DATA = "data"
    LURE = "lure"  # Honeypot lure files
    EXECUTABLE = "executable"
    DOCUMENT = "document"
    ARCHIVE = "archive"
    SCRIPT = "script"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class FileMetadata:
    """File metadata"""
    name: str
    path: str
    file_type: FileType
    category: FileCategory
    size: int
    permissions: str
    owner: str
    group: str
    created: datetime
    modified: datetime
    accessed: datetime
    is_lure: bool = False
    content_hash: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'path': self.path,
            'type': self.file_type.value,
            'category': self.category.value,
            'size': self.size,
            'permissions': self.permissions,
            'owner': self.owner,
            'group': self.group,
            'created': self.created.isoformat(),
            'modified': self.modified.isoformat(),
            'accessed': self.accessed.isoformat(),
            'is_lure': self.is_lure
        }
    
    def to_ls_line(self) -> str:
        """Generate ls -la style output"""
        type_char = 'd' if self.file_type == FileType.DIRECTORY else '-'
        size_str = str(self.size).rjust(10)
        date_str = self.modified.strftime("%b %d %H:%M")
        return f"{type_char}{self.permissions} 1 {self.owner:8} {self.group:8} {size_str} {date_str} {self.name}"


@dataclass
class FileContent:
    """File content with metadata"""
    path: str
    content: bytes
    is_dynamic: bool = False
    generator: Optional[str] = None


# =============================================================================
# FAKE FILESYSTEM
# =============================================================================

class FakeFilesystem:
    """
    Comprehensive fake filesystem for honeypots
    
    Features:
    - Realistic Linux/Unix directory structure
    - Windows-style paths support
    - Lure files with tracking
    - Dynamic content generation
    - Access logging
    """
    
    def __init__(
        self,
        system_type: str = "linux",
        hostname: str = "prod-server-01",
        log_callback=None,
        alert_callback=None
    ):
        self.system_type = system_type
        self.hostname = hostname
        self.log_callback = log_callback
        self.alert_callback = alert_callback
        
        # Filesystem storage
        self.files: Dict[str, FileMetadata] = {}
        self.content: Dict[str, FileContent] = {}
        
        # Access tracking
        self.access_log: List[Dict] = []
        self.lure_access_count: Dict[str, int] = {}
        
        # Initialize filesystem
        self._initialize_filesystem()
        
        logger.info(f"FakeFilesystem initialized: {system_type} - {hostname}")
    
    def _initialize_filesystem(self):
        """Initialize the fake filesystem"""
        if self.system_type == "linux":
            self._create_linux_filesystem()
        else:
            self._create_windows_filesystem()
    
    def _create_linux_filesystem(self):
        """Create realistic Linux filesystem"""
        now = datetime.now()
        boot_time = now - timedelta(days=random.randint(30, 180))
        
        # Root directories
        root_dirs = [
            "/", "/bin", "/boot", "/dev", "/etc", "/home",
            "/lib", "/lib64", "/media", "/mnt", "/opt",
            "/proc", "/root", "/run", "/sbin", "/srv",
            "/sys", "/tmp", "/usr", "/var"
        ]
        
        for path in root_dirs:
            self._add_directory(path, "root", "root", boot_time)
        
        # /etc - Configuration files
        self._create_etc_files(boot_time)
        
        # /home - User directories
        self._create_home_directories(now)
        
        # /var - Variable data
        self._create_var_files(now)
        
        # /root - Root home
        self._create_root_home(now)
        
        # /tmp - Temporary files
        self._create_tmp_files(now)
        
        # /opt - Optional software
        self._create_opt_files(boot_time)
        
        logger.info(f"Created {len(self.files)} filesystem entries")
    
    def _create_etc_files(self, boot_time: datetime):
        """Create /etc configuration files"""
        # passwd file
        passwd_content = """root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/usr/sbin/nologin
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
irc:x:39:39:ircd:/var/run/ircd:/usr/sbin/nologin
gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
systemd-network:x:100:102:systemd Network Management,,,:/run/systemd:/usr/sbin/nologin
systemd-resolve:x:101:103:systemd Resolver,,,:/run/systemd:/usr/sbin/nologin
syslog:x:102:106::/home/syslog:/usr/sbin/nologin
messagebus:x:103:107::/nonexistent:/usr/sbin/nologin
_apt:x:104:65534::/nonexistent:/usr/sbin/nologin
sshd:x:105:65534::/run/sshd:/usr/sbin/nologin
admin:x:1000:1000:Admin User,,,:/home/admin:/bin/bash
developer:x:1001:1001:Developer,,,:/home/developer:/bin/bash
dbadmin:x:1002:1002:Database Admin,,,:/home/dbadmin:/bin/bash
"""
        self._add_file("/etc/passwd", passwd_content.encode(), "root", "root", 
                       boot_time, "rw-r--r--", FileCategory.SYSTEM)
        
        # shadow file (fake hashes - LURE)
        shadow_content = """root:$6$rounds=5000$fakehash$AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA:18900:0:99999:7:::
admin:$6$rounds=5000$saltsalt$BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBbBBBB:18901:0:99999:7:::
developer:$6$rounds=5000$devsalt$CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC:18902:0:99999:7:::
dbadmin:$6$rounds=5000$dbsalt$DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD:18903:0:99999:7:::
"""
        self._add_file("/etc/shadow", shadow_content.encode(), "root", "shadow",
                       boot_time, "r--------", FileCategory.LURE, is_lure=True)
        
        # hosts file
        hosts_content = f"""127.0.0.1	localhost
127.0.1.1	{self.hostname}

# Production servers
10.0.1.10	db-master.internal
10.0.1.11	db-slave.internal
10.0.1.20	app-server-01.internal
10.0.1.21	app-server-02.internal
10.0.1.30	cache-01.internal

# Management
10.0.0.1	gateway.internal
10.0.0.5	monitoring.internal

# The following lines are desirable for IPv6 capable hosts
::1     ip6-localhost ip6-loopback
fe00::0 ip6-localnet
ff00::0 ip6-mcastprefix
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
"""
        self._add_file("/etc/hosts", hosts_content.encode(), "root", "root",
                       boot_time, "rw-r--r--", FileCategory.SYSTEM)
        
        # SSH config
        sshd_config = """# /etc/ssh/sshd_config
Port 22
ListenAddress 0.0.0.0
Protocol 2
HostKey /etc/ssh/ssh_host_rsa_key
HostKey /etc/ssh/ssh_host_ecdsa_key
HostKey /etc/ssh/ssh_host_ed25519_key
PermitRootLogin prohibit-password
PubkeyAuthentication yes
PasswordAuthentication yes
ChallengeResponseAuthentication no
UsePAM yes
X11Forwarding yes
PrintMotd no
AcceptEnv LANG LC_*
Subsystem sftp /usr/lib/openssh/sftp-server
"""
        self._add_file("/etc/ssh/sshd_config", sshd_config.encode(), "root", "root",
                       boot_time, "rw-r--r--", FileCategory.CONFIG)
        
        # MySQL config (LURE)
        mysql_config = """[mysqld]
user = mysql
port = 3306
datadir = /var/lib/mysql
socket = /var/run/mysqld/mysqld.sock
bind-address = 0.0.0.0

# Connection settings
max_connections = 500
connect_timeout = 10

# Production credentials - DO NOT SHARE
# Root password: Pr0d_R00t_2024!
# Replication user: repl_user / Repl1c@t10n#
"""
        self._add_file("/etc/mysql/mysql.conf.d/mysqld.cnf", mysql_config.encode(),
                       "root", "root", boot_time, "rw-r-----", FileCategory.LURE, is_lure=True)
        
        # Crontab (LURE)
        crontab_content = """# /etc/crontab: system-wide crontab
SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# m h dom mon dow user	command
17 *	* * *	root    cd / && run-parts --report /etc/cron.hourly
25 6	* * *	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.daily )
47 6	* * 7	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.weekly )
52 6	1 * *	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.monthly )

# Backup job - runs as dbadmin
0 2 * * * dbadmin /opt/scripts/backup.sh >> /var/log/backup.log 2>&1

# Sync to S3 - credentials in /root/.aws/credentials
30 3 * * * root aws s3 sync /var/backups s3://company-backups/prod/
"""
        self._add_file("/etc/crontab", crontab_content.encode(), "root", "root",
                       boot_time, "rw-r--r--", FileCategory.LURE, is_lure=True)
    
    def _create_home_directories(self, now: datetime):
        """Create user home directories"""
        users = ['admin', 'developer', 'dbadmin']
        
        for user in users:
            home_path = f"/home/{user}"
            self._add_directory(home_path, user, user, now - timedelta(days=90))
            self._add_directory(f"{home_path}/.ssh", user, user, now - timedelta(days=60))
            
            # SSH authorized_keys
            auth_keys = f"""# Authorized keys for {user}
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC7... {user}@workstation
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQD9... {user}@laptop
"""
            self._add_file(f"{home_path}/.ssh/authorized_keys", auth_keys.encode(),
                          user, user, now - timedelta(days=30), "rw-------", FileCategory.CONFIG)
            
            # Bash history (LURE)
            bash_history = f"""cd /var/www/html
vim config.php
mysql -u root -p'Pr0d_R00t_2024!'
mysqldump production > backup.sql
scp backup.sql admin@10.0.1.10:/backups/
cat /etc/shadow
sudo -l
ssh dbadmin@db-master.internal
psql -h localhost -U postgres
export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
"""
            self._add_file(f"{home_path}/.bash_history", bash_history.encode(),
                          user, user, now - timedelta(hours=2), "rw-------", 
                          FileCategory.LURE, is_lure=True)
        
        # Root home
        self._add_directory("/root", "root", "root", now - timedelta(days=180))
        self._add_directory("/root/.ssh", "root", "root", now - timedelta(days=90))
    
    def _create_root_home(self, now: datetime):
        """Create /root home directory with lures"""
        # SSH private key (LURE)
        fake_key = """-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEA0Z3VS5JJcds3xfn4rFakeKeyContentHereForHoneypotDete
ction0000000000000000000000000000000000000000000000000000000000000
THIS IS A HONEYPOT KEY - ACCESS HAS BEEN LOGGED
00000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000
-----END RSA PRIVATE KEY-----
"""
        self._add_file("/root/.ssh/id_rsa", fake_key.encode(), "root", "root",
                       now - timedelta(days=60), "rw-------", FileCategory.LURE, is_lure=True)
        
        # AWS credentials (LURE)
        aws_creds = """[default]
aws_access_key_id = AKIAFAKEACCESSKEYID
aws_secret_access_key = FakeSecretKey+Honeypot+Detection+12345678

[production]
aws_access_key_id = AKIAPRODACCESSKEY
aws_secret_access_key = ProductionFakeKey+ForHoneypot+87654321
"""
        self._add_file("/root/.aws/credentials", aws_creds.encode(), "root", "root",
                       now - timedelta(days=45), "rw-------", FileCategory.LURE, is_lure=True)
        
        # Notes file (LURE)
        notes = """=== Server Credentials ===
Last updated: 2024-11-01

Database:
- MySQL root: Pr0d_R00t_2024!
- PostgreSQL: postgres / P0stgr3s_Pr0d!
- MongoDB: admin / M0ng0_Adm1n_2024

SSH Keys:
- Production: /root/.ssh/prod_key
- Backup: /root/.ssh/backup_key
- AWS: See ~/.aws/credentials

API Keys:
- Stripe: [REDACTED_FAKE_KEY_HONEYPOT]
- Twilio: [REDACTED_FAKE_KEY_HONEYPOT]

VPN:
- OpenVPN config: /etc/openvpn/client.conf
- WireGuard: See /etc/wireguard/wg0.conf

Remember: Change passwords quarterly!
Next change: 2025-01-01
"""
        self._add_file("/root/notes.txt", notes.encode(), "root", "root",
                       now - timedelta(days=25), "rw-------", FileCategory.LURE, is_lure=True)
    
    def _create_var_files(self, now: datetime):
        """Create /var directory structure"""
        var_dirs = [
            "/var/log", "/var/lib", "/var/cache", "/var/run",
            "/var/spool", "/var/www", "/var/www/html", "/var/backups"
        ]
        
        for path in var_dirs:
            self._add_directory(path, "root", "root", now - timedelta(days=180))
        
        # Log files
        self._add_file("/var/log/syslog", b"", "syslog", "adm",
                       now, "rw-r-----", FileCategory.LOG)
        self._add_file("/var/log/auth.log", b"", "syslog", "adm",
                       now, "rw-r-----", FileCategory.LOG)
        
        # Backup file (LURE)
        backup_info = """Backup created: 2024-11-26
Database: production
Tables: users, orders, payments, api_keys
Size: 2.3 GB compressed

Restore command:
  mysql -u root -p production < /var/backups/prod_backup.sql

Encryption key: aes-256-cbc
Password: B4ckup_K3y_2024!
"""
        self._add_file("/var/backups/backup_info.txt", backup_info.encode(),
                       "root", "root", now - timedelta(hours=12), "rw-r-----",
                       FileCategory.LURE, is_lure=True)
    
    def _create_tmp_files(self, now: datetime):
        """Create /tmp files"""
        # Session file (LURE)
        session_data = json.dumps({
            "session_id": "abc123def456",
            "user": "admin",
            "role": "superuser",
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkFkbWluIFVzZXIiLCJpYXQiOjE1MTYyMzkwMjIsInJvbGUiOiJzdXBlcnVzZXIifQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
            "expires": (now + timedelta(hours=24)).isoformat()
        }, indent=2)
        self._add_file("/tmp/session_admin.json", session_data.encode(),
                       "www-data", "www-data", now - timedelta(minutes=30),
                       "rw-rw-r--", FileCategory.LURE, is_lure=True)
    
    def _create_opt_files(self, boot_time: datetime):
        """Create /opt directory structure"""
        self._add_directory("/opt/scripts", "root", "root", boot_time)
        self._add_directory("/opt/app", "www-data", "www-data", boot_time)
        
        # Deployment script (LURE)
        deploy_script = """#!/bin/bash
# Production deployment script
# Author: DevOps Team
# Last updated: 2024-11-01

# Credentials
DB_HOST="db-master.internal"
DB_USER="deploy_user"
DB_PASS="D3pl0y_P@ss_2024!"

# AWS
export AWS_ACCESS_KEY_ID="AKIAFAKEDEPLOYKEY"
export AWS_SECRET_ACCESS_KEY="DeploySecretKey+Honeypot+12345"

# Deploy
echo "Deploying to production..."
rsync -avz /opt/app/ prod-server:/var/www/html/
ssh prod-server "sudo systemctl restart nginx"

echo "Done!"
"""
        self._add_file("/opt/scripts/deploy.sh", deploy_script.encode(),
                       "root", "root", boot_time, "rwxr-x---",
                       FileCategory.LURE, is_lure=True)
    
    def _create_windows_filesystem(self):
        """Create Windows-style filesystem"""
        now = datetime.now()
        
        # Windows directories
        win_dirs = [
            "C:\\", "C:\\Windows", "C:\\Windows\\System32",
            "C:\\Program Files", "C:\\Program Files (x86)",
            "C:\\Users", "C:\\Users\\Administrator",
            "C:\\Users\\Administrator\\Desktop",
            "C:\\Users\\Administrator\\Documents"
        ]
        
        for path in win_dirs:
            self._add_directory(path, "SYSTEM", "SYSTEM", now)
        
        # Desktop lures
        pwd_content = """=== Company Passwords ===
Updated: November 2024

Domain Admin: Admin@Company123!
SQL Server SA: SA_P@ssw0rd_2024
VPN: CompanyVPN#2024
WiFi: Company_Wifi_123

Do not share!
"""
        self._add_file("C:\\Users\\Administrator\\Desktop\\passwords.txt",
                       pwd_content.encode(), "Administrator", "Users",
                       now, "rw-r--r--", FileCategory.LURE, is_lure=True)
    
    def _add_directory(
        self,
        path: str,
        owner: str,
        group: str,
        created: datetime,
        permissions: str = "rwxr-xr-x"
    ):
        """Add a directory to the filesystem"""
        name = os.path.basename(path) or path
        
        self.files[path] = FileMetadata(
            name=name,
            path=path,
            file_type=FileType.DIRECTORY,
            category=FileCategory.SYSTEM,
            size=4096,
            permissions=permissions,
            owner=owner,
            group=group,
            created=created,
            modified=created,
            accessed=datetime.now()
        )
    
    def _add_file(
        self,
        path: str,
        content: bytes,
        owner: str,
        group: str,
        modified: datetime,
        permissions: str = "rw-r--r--",
        category: FileCategory = FileCategory.DATA,
        is_lure: bool = False
    ):
        """Add a file to the filesystem"""
        name = os.path.basename(path)
        
        # Ensure parent directory exists
        parent = os.path.dirname(path)
        if parent and parent not in self.files:
            self._add_directory(parent, owner, group, modified - timedelta(days=1))
        
        self.files[path] = FileMetadata(
            name=name,
            path=path,
            file_type=FileType.FILE,
            category=category,
            size=len(content),
            permissions=permissions,
            owner=owner,
            group=group,
            created=modified - timedelta(days=random.randint(1, 30)),
            modified=modified,
            accessed=datetime.now(),
            is_lure=is_lure,
            content_hash=hashlib.sha256(content).hexdigest()
        )
        
        self.content[path] = FileContent(
            path=path,
            content=content,
            is_dynamic=False
        )
        
        if is_lure:
            self.lure_access_count[path] = 0
    
    # =========================================================================
    # PUBLIC API
    # =========================================================================
    
    def list_directory(self, path: str, attacker_ip: str = "unknown") -> List[FileMetadata]:
        """List directory contents"""
        self._log_access(path, "list", attacker_ip)
        
        # Normalize path
        if not path.endswith('/'):
            path = path + '/'
        if path == '//':
            path = '/'
        
        results = []
        for file_path, metadata in self.files.items():
            # Check if file is in this directory
            parent = os.path.dirname(file_path)
            if parent == path.rstrip('/') or (path == '/' and parent == ''):
                results.append(metadata)
        
        return sorted(results, key=lambda x: x.name)
    
    def get_file(self, path: str, attacker_ip: str = "unknown") -> Optional[Tuple[FileMetadata, bytes]]:
        """Get file metadata and content"""
        self._log_access(path, "read", attacker_ip)
        
        if path not in self.files:
            return None
        
        metadata = self.files[path]
        
        # Check if lure file
        if metadata.is_lure:
            self._trigger_lure_alert(path, attacker_ip)
        
        # Get content
        content = b''
        if path in self.content:
            content = self.content[path].content
        
        return (metadata, content)
    
    def file_exists(self, path: str) -> bool:
        """Check if file exists"""
        return path in self.files
    
    def is_directory(self, path: str) -> bool:
        """Check if path is a directory"""
        if path in self.files:
            return self.files[path].file_type == FileType.DIRECTORY
        return False
    
    def get_cwd_listing(self, cwd: str, attacker_ip: str = "unknown") -> str:
        """Get ls -la style listing for current directory"""
        files = self.list_directory(cwd, attacker_ip)
        
        lines = [f"total {len(files)}"]
        for f in files:
            lines.append(f.to_ls_line())
        
        return '\n'.join(lines)
    
    def cat_file(self, path: str, attacker_ip: str = "unknown") -> str:
        """Get file content as string"""
        result = self.get_file(path, attacker_ip)
        if result:
            metadata, content = result
            return content.decode('utf-8', errors='replace')
        return f"cat: {path}: No such file or directory"
    
    def get_file_info(self, path: str) -> Optional[Dict]:
        """Get file information (stat-like)"""
        if path not in self.files:
            return None
        
        metadata = self.files[path]
        return metadata.to_dict()
    
    # =========================================================================
    # LOGGING AND ALERTING
    # =========================================================================
    
    def _log_access(self, path: str, operation: str, attacker_ip: str):
        """Log file access"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'path': path,
            'operation': operation,
            'attacker_ip': attacker_ip,
            'is_lure': path in self.files and self.files[path].is_lure
        }
        
        self.access_log.append(entry)
        
        if self.log_callback:
            try:
                self.log_callback(entry)
            except Exception as e:
                logger.error(f"Log callback error: {e}")
    
    def _trigger_lure_alert(self, path: str, attacker_ip: str):
        """Trigger alert for lure file access"""
        self.lure_access_count[path] = self.lure_access_count.get(path, 0) + 1
        
        alert = {
            'timestamp': datetime.now().isoformat(),
            'alert_type': 'lure_file_accessed',
            'severity': 'high',
            'path': path,
            'attacker_ip': attacker_ip,
            'access_count': self.lure_access_count[path],
            'message': f"Lure file accessed: {path}"
        }
        
        logger.warning(f"🎣 LURE ACCESSED: {path} by {attacker_ip}")
        
        if self.alert_callback:
            try:
                self.alert_callback(alert)
            except Exception as e:
                logger.error(f"Alert callback error: {e}")
    
    def get_access_stats(self) -> Dict[str, Any]:
        """Get filesystem access statistics"""
        return {
            'total_files': len(self.files),
            'total_lures': len([f for f in self.files.values() if f.is_lure]),
            'total_accesses': len(self.access_log),
            'lure_accesses': sum(self.lure_access_count.values()),
            'lure_access_details': dict(self.lure_access_count)
        }


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    def log_handler(event):
        print(f"LOG: {event['operation']} {event['path']}")
    
    def alert_handler(alert):
        print(f"🚨 ALERT: {alert['message']}")
    
    fs = FakeFilesystem(
        system_type="linux",
        hostname="prod-server-01",
        log_callback=log_handler,
        alert_callback=alert_handler
    )
    
    print("📁 Fake Filesystem Initialized")
    print(f"   Total files: {len(fs.files)}")
    print(f"   Lure files: {len([f for f in fs.files.values() if f.is_lure])}")
    
    print("\n📂 Root directory listing:")
    print(fs.get_cwd_listing("/", "test"))
    
    print("\n📂 /etc directory:")
    print(fs.get_cwd_listing("/etc", "test"))
    
    print("\n📄 Reading lure file /etc/shadow:")
    result = fs.get_file("/etc/shadow", "192.168.1.100")
    if result:
        meta, content = result
        print(f"   Size: {meta.size} bytes")
        print(f"   Is Lure: {meta.is_lure}")
    
    print("\n📊 Access Statistics:")
    stats = fs.get_access_stats()
    print(f"   Total accesses: {stats['total_accesses']}")
    print(f"   Lure accesses: {stats['lure_accesses']}")
