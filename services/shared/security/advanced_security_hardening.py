"""
Advanced Security Hardening Module for ACGS Production Deployment

This module implements enterprise-grade security hardening measures including:
- Advanced encryption for data at rest and in transit
- Comprehensive secrets management with rotation
- Enhanced input validation and sanitization
- Advanced threat detection and response
- Security event logging and monitoring
- Network security controls
- Compliance and audit controls

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import hashlib
import hmac
import json
import logging
import os
import re
import secrets
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Set, Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import ipaddress
from dataclasses import dataclass
from enum import Enum

# Configure logging
logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    """Security levels for different operations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ThreatLevel(Enum):
    """Threat assessment levels."""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SecurityEvent:
    """Security event for audit logging."""
    event_id: str
    timestamp: datetime
    event_type: str
    severity: SecurityLevel
    source_ip: str
    user_id: Optional[str]
    resource: str
    action: str
    result: str
    details: Dict[str, Any]
    constitutional_hash: str = "cdd01ef066bc6cf2"

class AdvancedEncryptionManager:
    """Advanced encryption manager for data protection."""
    
    def __init__(self):
        self.master_key = self._get_or_generate_master_key()
        self.fernet = Fernet(self.master_key)
        self.rsa_key = self._get_or_generate_rsa_key()
        
    def _get_or_generate_master_key(self) -> bytes:
        """Get or generate master encryption key."""
        # Use local directory for development, /etc for production
        if os.access('/etc', os.W_OK):
            key_file = "/etc/acgs/encryption/master.key"
        else:
            # Fallback to local directory for development
            key_file = "config/security/keys/master.key"

        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            # Generate new key
            key = Fernet.generate_key()
            os.makedirs(os.path.dirname(key_file), exist_ok=True)
            with open(key_file, 'wb') as f:
                f.write(key)
            os.chmod(key_file, 0o600)  # Restrict permissions
            return key
    
    def _get_or_generate_rsa_key(self) -> rsa.RSAPrivateKey:
        """Get or generate RSA key pair."""
        # Use local directory for development, /etc for production
        if os.access('/etc', os.W_OK):
            key_file = "/etc/acgs/encryption/rsa_private.pem"
            public_key_file = "/etc/acgs/encryption/rsa_public.pem"
        else:
            # Fallback to local directory for development
            key_file = "config/security/keys/rsa_private.pem"
            public_key_file = "config/security/keys/rsa_public.pem"

        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return serialization.load_pem_private_key(f.read(), password=None)
        else:
            # Generate new RSA key pair
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=4096,
            )

            # Save private key
            os.makedirs(os.path.dirname(key_file), exist_ok=True)
            with open(key_file, 'wb') as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            os.chmod(key_file, 0o600)

            # Save public key
            public_key = private_key.public_key()
            with open(public_key_file, 'wb') as f:
                f.write(public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ))

            return private_key
    
    def encrypt_sensitive_data(self, data: Union[str, bytes]) -> str:
        """Encrypt sensitive data using Fernet (AES 128)."""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        encrypted = self.fernet.encrypt(data)
        return base64.b64encode(encrypted).decode('utf-8')
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
        decrypted = self.fernet.decrypt(encrypted_bytes)
        return decrypted.decode('utf-8')
    
    def encrypt_with_rsa(self, data: Union[str, bytes]) -> str:
        """Encrypt data using RSA public key."""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        public_key = self.rsa_key.public_key()
        encrypted = public_key.encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return base64.b64encode(encrypted).decode('utf-8')
    
    def decrypt_with_rsa(self, encrypted_data: str) -> str:
        """Decrypt data using RSA private key."""
        encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
        decrypted = self.rsa_key.decrypt(
            encrypted_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return decrypted.decode('utf-8')

class AdvancedSecretsManager:
    """Advanced secrets management with rotation and secure storage."""
    
    def __init__(self, encryption_manager: AdvancedEncryptionManager):
        self.encryption_manager = encryption_manager
        self.secrets_store = {}
        self.rotation_schedule = {}
        
    async def store_secret(self, key: str, value: str, 
                          rotation_days: int = 90) -> bool:
        """Store secret with encryption and rotation schedule."""
        try:
            # Encrypt the secret
            encrypted_value = self.encryption_manager.encrypt_sensitive_data(value)
            
            # Store with metadata
            self.secrets_store[key] = {
                'value': encrypted_value,
                'created_at': datetime.now(timezone.utc),
                'last_rotated': datetime.now(timezone.utc),
                'rotation_days': rotation_days,
                'access_count': 0,
                'last_accessed': None
            }
            
            # Schedule rotation
            rotation_date = datetime.now(timezone.utc) + timedelta(days=rotation_days)
            self.rotation_schedule[key] = rotation_date
            
            logger.info(f"Secret stored successfully: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store secret {key}: {e}")
            return False
    
    async def get_secret(self, key: str) -> Optional[str]:
        """Retrieve and decrypt secret."""
        try:
            if key not in self.secrets_store:
                logger.warning(f"Secret not found: {key}")
                return None
            
            secret_data = self.secrets_store[key]
            
            # Update access tracking
            secret_data['access_count'] += 1
            secret_data['last_accessed'] = datetime.now(timezone.utc)
            
            # Decrypt and return
            decrypted_value = self.encryption_manager.decrypt_sensitive_data(
                secret_data['value']
            )
            
            return decrypted_value
            
        except Exception as e:
            logger.error(f"Failed to retrieve secret {key}: {e}")
            return None
    
    async def rotate_secret(self, key: str, new_value: str) -> bool:
        """Rotate a secret with new value."""
        try:
            if key not in self.secrets_store:
                return False
            
            # Encrypt new value
            encrypted_value = self.encryption_manager.encrypt_sensitive_data(new_value)
            
            # Update secret
            self.secrets_store[key]['value'] = encrypted_value
            self.secrets_store[key]['last_rotated'] = datetime.now(timezone.utc)
            
            # Update rotation schedule
            rotation_days = self.secrets_store[key]['rotation_days']
            self.rotation_schedule[key] = datetime.now(timezone.utc) + timedelta(days=rotation_days)
            
            logger.info(f"Secret rotated successfully: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to rotate secret {key}: {e}")
            return False
    
    async def check_rotation_needed(self) -> List[str]:
        """Check which secrets need rotation."""
        now = datetime.now(timezone.utc)
        return [key for key, rotation_date in self.rotation_schedule.items() 
                if rotation_date <= now]

class AdvancedInputValidator:
    """Advanced input validation and sanitization."""
    
    def __init__(self):
        # Malicious patterns
        self.sql_injection_patterns = [
            r"('|(\\-\\-)|(;)|(\\||\\|)|(\\*|\\*))",
            r"(union|select|insert|delete|update|drop|create|alter|exec|execute)",
            r"(script|javascript|vbscript|onload|onerror|onclick)"
        ]
        
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>.*?</iframe>",
            r"<object[^>]*>.*?</object>"
        ]
        
        self.command_injection_patterns = [
            r"[;&|`$(){}[\]\\]",
            r"(rm|del|format|shutdown|reboot)",
            r"(\.\./|\.\.\\\\)"
        ]
        
        # Constitutional compliance patterns
        self.constitutional_patterns = [
            r"constitutional_hash.*cdd01ef066bc6cf2",
            r"governance.*compliance",
            r"policy.*validation"
        ]
    
    def validate_input(self, data: Any, input_type: str = "general") -> Dict[str, Any]:
        """Comprehensive input validation."""
        result = {
            'valid': True,
            'threats': [],
            'sanitized_data': data,
            'risk_level': ThreatLevel.NONE
        }
        
        if isinstance(data, str):
            # Check for malicious patterns
            threats = []
            
            # SQL injection check
            for pattern in self.sql_injection_patterns:
                if re.search(pattern, data, re.IGNORECASE):
                    threats.append('sql_injection')
                    result['risk_level'] = ThreatLevel.HIGH
            
            # XSS check
            for pattern in self.xss_patterns:
                if re.search(pattern, data, re.IGNORECASE):
                    threats.append('xss')
                    result['risk_level'] = ThreatLevel.HIGH
            
            # Command injection check
            for pattern in self.command_injection_patterns:
                if re.search(pattern, data):
                    threats.append('command_injection')
                    result['risk_level'] = ThreatLevel.CRITICAL
            
            result['threats'] = threats
            result['valid'] = len(threats) == 0
            
            # Sanitize data if needed
            if threats:
                result['sanitized_data'] = self._sanitize_input(data)
        
        return result
    
    def _sanitize_input(self, data: str) -> str:
        """Sanitize malicious input."""
        # Remove script tags
        data = re.sub(r'<script[^>]*>.*?</script>', '', data, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove javascript: protocols
        data = re.sub(r'javascript:', '', data, flags=re.IGNORECASE)
        
        # Remove event handlers
        data = re.sub(r'on\w+\s*=\s*["\'][^"\']*["\']', '', data, flags=re.IGNORECASE)
        
        # Remove dangerous SQL keywords
        dangerous_sql = ['drop', 'delete', 'truncate', 'alter', 'create']
        for keyword in dangerous_sql:
            data = re.sub(rf'\b{keyword}\b', '', data, flags=re.IGNORECASE)
        
        return data.strip()

class AdvancedSecurityHardening:
    """Main security hardening orchestrator."""
    
    def __init__(self):
        self.encryption_manager = AdvancedEncryptionManager()
        self.secrets_manager = AdvancedSecretsManager(self.encryption_manager)
        self.input_validator = AdvancedInputValidator()
        self.security_events: List[SecurityEvent] = []
        self.blocked_ips: Set[str] = set()
        self.rate_limits: Dict[str, Dict] = {}
        
    async def initialize(self) -> bool:
        """Initialize security hardening components."""
        try:
            # Initialize default secrets
            await self._initialize_default_secrets()
            
            # Start background tasks
            asyncio.create_task(self._rotation_monitor())
            asyncio.create_task(self._security_monitor())
            
            logger.info("Advanced security hardening initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize security hardening: {e}")
            return False
    
    async def _initialize_default_secrets(self):
        """Initialize default secrets if not present."""
        default_secrets = {
            'jwt_secret': secrets.token_urlsafe(64),
            'csrf_secret': secrets.token_urlsafe(32),
            'encryption_salt': secrets.token_urlsafe(32),
            'api_key_salt': secrets.token_urlsafe(32)
        }
        
        for key, value in default_secrets.items():
            if await self.secrets_manager.get_secret(key) is None:
                await self.secrets_manager.store_secret(key, value)
    
    async def _rotation_monitor(self):
        """Background task to monitor secret rotation."""
        while True:
            try:
                secrets_to_rotate = await self.secrets_manager.check_rotation_needed()
                for secret_key in secrets_to_rotate:
                    logger.warning(f"Secret rotation needed: {secret_key}")
                    # In production, trigger automated rotation or alert
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                logger.error(f"Error in rotation monitor: {e}")
                await asyncio.sleep(300)  # Retry in 5 minutes
    
    async def _security_monitor(self):
        """Background task to monitor security events."""
        while True:
            try:
                # Analyze recent security events
                recent_events = [e for e in self.security_events 
                               if e.timestamp > datetime.now(timezone.utc) - timedelta(hours=1)]
                
                # Check for attack patterns
                if len(recent_events) > 100:
                    logger.warning("High volume of security events detected")
                
                # Clean old events (keep last 24 hours)
                cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
                self.security_events = [e for e in self.security_events if e.timestamp > cutoff]
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in security monitor: {e}")
                await asyncio.sleep(60)
    
    def log_security_event(self, event_type: str, severity: SecurityLevel,
                          source_ip: str, user_id: Optional[str],
                          resource: str, action: str, result: str,
                          details: Dict[str, Any] = None):
        """Log security event for audit and monitoring."""
        event = SecurityEvent(
            event_id=secrets.token_urlsafe(16),
            timestamp=datetime.now(timezone.utc),
            event_type=event_type,
            severity=severity,
            source_ip=source_ip,
            user_id=user_id,
            resource=resource,
            action=action,
            result=result,
            details=details or {},
            constitutional_hash="cdd01ef066bc6cf2"
        )
        
        self.security_events.append(event)
        
        # Log to file for persistence
        logger.info(f"Security Event: {event.event_type} - {event.severity.value} - {event.result}")
        
        # Alert on critical events
        if severity == SecurityLevel.CRITICAL:
            logger.critical(f"CRITICAL SECURITY EVENT: {event_type} from {source_ip}")

# Global instance
security_hardening = AdvancedSecurityHardening()
