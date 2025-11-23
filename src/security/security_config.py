"""
🔒 Security Configuration & Hardening
"""

import os
from cryptography.fernet import Fernet
from passlib.context import CryptContext
import secrets
import re

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SecurityConfig:
    """Security configuration"""
    
    # Generate or load encryption key
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", Fernet.generate_key())
    cipher = Fernet(ENCRYPTION_KEY)
    
    # JWT settings
    SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE = 60
    RATE_LIMIT_PER_HOUR = 1000
    
    # CORS
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    
    # API keys (hashed)
    VALID_API_KEYS = set(os.getenv("API_KEYS", "").split(","))
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        """Verify password"""
        return pwd_context.verify(plain, hashed)
    
    @staticmethod
    def encrypt_data(data: str) -> bytes:
        """Encrypt sensitive data"""
        return SecurityConfig.cipher.encrypt(data.encode())
    
    @staticmethod
    def decrypt_data(encrypted: bytes) -> str:
        """Decrypt data"""
        return SecurityConfig.cipher.decrypt(encrypted).decode()
    
    @staticmethod
    def validate_input(text: str, max_length: int = 1000) -> bool:
        """Validate user input against injection attacks"""
        if len(text) > max_length:
            return False
        
        # Check for SQL injection patterns
        sql_patterns = [
            r"(\bUNION\b.*\bSELECT\b)",
            r"(\bDROP\b.*\bTABLE\b)",
            r"(\bINSERT\b.*\bINTO\b)",
            r"(\bDELETE\b.*\bFROM\b)",
            r"(--|#|/\*|\*/)",
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return False
        
        # Check for XSS patterns
        xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"onerror\s*=",
            r"onload\s*=",
        ]
        
        for pattern in xss_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return False
        
        return True
    
    @staticmethod
    def generate_api_key() -> str:
        """Generate secure API key"""
        return secrets.token_urlsafe(32)


class InputValidator:
    """Validate all inputs"""
    
    @staticmethod
    def validate_attacker_name(name: str) -> bool:
        """Validate attacker name"""
        if not name or len(name) > 100:
            return False
        # Only alphanumeric, underscore, hyphen
        return bool(re.match(r'^[a-zA-Z0-9_-]+$', name))
    
    @staticmethod
    def validate_max_steps(steps: int) -> bool:
        """Validate max steps"""
        return 1 <= steps <= 10000
    
    @staticmethod
    def sanitize_string(text: str) -> str:
        """Sanitize string input"""
        # Remove any HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Remove any null bytes
        text = text.replace('\x00', '')
        return text.strip()


# Security headers
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}


def get_security_headers():
    """Get security headers for responses"""
    return SECURITY_HEADERS
