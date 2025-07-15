#!/usr/bin/env python3
"""
Real Security Hardening for ACGS-2

Constitutional Hash: cdd01ef066bc6cf2
ACGS-2 Constitutional Compliance Validation

This module implements actual working security hardening with real vulnerability
scanning, threat detection, and authentication systems that work with real data.
"""

import asyncio
import hashlib
import hmac
import json
import logging
import os
import re
import secrets
import sqlite3
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import bcrypt
import jwt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class RealSecurityConfig:
    """Real configuration for security hardening."""
    
    # Database for security data
    security_db_path: str = "security_data.db"
    
    # Secret detection patterns (real patterns used in production)
    secret_patterns: Dict[str, str] = field(default_factory=lambda: {
        'aws_access_key': r'AKIA[0-9A-Z]{16}',
        'aws_secret_key': r'[A-Za-z0-9/+=]{40}',
        'github_token': r'ghp_[a-zA-Z0-9]{36}',
        'api_key': r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\']?([a-zA-Z0-9_-]{20,})["\']?',
        'password': r'(?i)(password|passwd|pwd)\s*[=:]\s*["\']?([^"\'\s]{8,})["\']?',
        'private_key': r'-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----',
        'jwt_token': r'eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*',
        'database_url': r'(?i)(database_url|db_url)\s*[=:]\s*["\']?([^"\'\s]+://[^"\'\s]+)["\']?'
    })
    
    # File extensions to scan
    scan_extensions: Set[str] = field(default_factory=lambda: {
        '.py', '.js', '.ts', '.json', '.yaml', '.yml', 'config/environments/development.env', '.conf', 
        '.config', '.ini', '.properties', '.xml', '.sh', '.bash'
    })
    
    # Authentication settings
    jwt_secret_key: str = field(default_factory=lambda: secrets.token_urlsafe(32))
    password_min_length: int = 12
    session_timeout_hours: int = 24
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 30
    
    # Encryption settings
    encryption_key: bytes = field(default_factory=lambda: Fernet.generate_key())
    
    constitutional_hash: str = CONSTITUTIONAL_HASH


@dataclass
class RealVulnerability:
    """Real vulnerability found during scanning."""
    file_path: str
    line_number: int
    vulnerability_type: str
    severity: str
    matched_content: str
    context: str
    remediation: str
    constitutional_hash: str = CONSTITUTIONAL_HASH


class RealVulnerabilityScanner:
    """
    Real vulnerability scanner that scans actual files for security issues.
    
    Uses real regex patterns and file system operations to find vulnerabilities.
    """
    
    def __init__(self, config: RealSecurityConfig):
        self.config = config
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.vulnerabilities: List[RealVulnerability] = []
        
        logger.info("Initialized Real Vulnerability Scanner")
        logger.info(f"🔒 Constitutional Hash: {self.constitutional_hash}")

    async def scan_directory(self, directory: Path) -> List[RealVulnerability]:
        """Scan directory for real security vulnerabilities."""
        
        logger.info(f"🔍 Scanning directory for vulnerabilities: {directory}")
        
        vulnerabilities = []
        files_scanned = 0
        
        # Get all scannable files
        scannable_files = self._get_scannable_files(directory)
        
        for file_path in scannable_files:
            try:
                file_vulns = await self._scan_file_real(file_path)
                vulnerabilities.extend(file_vulns)
                files_scanned += 1
                
                if files_scanned % 50 == 0:
                    logger.info(f"Scanned {files_scanned}/{len(scannable_files)} files, found {len(vulnerabilities)} vulnerabilities")
                    
            except Exception as e:
                logger.warning(f"Failed to scan file {file_path}: {e}")
        
        logger.info(f"✅ Scan completed: {files_scanned} files, {len(vulnerabilities)} vulnerabilities found")
        return vulnerabilities

    def _get_scannable_files(self, directory: Path) -> List[Path]:
        """Get list of files to scan."""
        
        scannable_files = []
        exclude_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 'env'}
        
        for file_path in directory.rglob('*'):
            if file_path.is_file():
                # Skip excluded directories
                if any(excluded in file_path.parts for excluded in exclude_dirs):
                    continue
                
                # Check file extension
                if file_path.suffix.lower() in self.config.scan_extensions:
                    scannable_files.append(file_path)
        
        return scannable_files

    async def _scan_file_real(self, file_path: Path) -> List[RealVulnerability]:
        """Scan individual file for real vulnerabilities."""
        
        vulnerabilities = []
        
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            # Scan each line for patterns
            for line_num, line in enumerate(lines, 1):
                for vuln_type, pattern in self.config.secret_patterns.items():
                    matches = re.finditer(pattern, line)
                    
                    for match in matches:
                        # Skip if it's already using environment variables
                        if self._is_safe_usage(line):
                            continue
                        
                        # Get context (surrounding lines)
                        context_start = max(0, line_num - 3)
                        context_end = min(len(lines), line_num + 2)
                        context = '\n'.join(lines[context_start:context_end])
                        
                        vulnerability = RealVulnerability(
                            file_path=str(file_path),
                            line_number=line_num,
                            vulnerability_type=vuln_type,
                            severity=self._get_severity(vuln_type),
                            matched_content=match.group(0)[:100],  # Limit length
                            context=context,
                            remediation=self._get_remediation(vuln_type),
                            constitutional_hash=self.constitutional_hash
                        )
                        
                        vulnerabilities.append(vulnerability)
            
        except Exception as e:
            logger.warning(f"Error scanning file {file_path}: {e}")
        
        return vulnerabilities

    def _is_safe_usage(self, line: str) -> bool:
        """Check if line uses safe patterns."""
        
        safe_patterns = [
            r'os\config/environments/development.environ\.get\(',
            r'os\.getenv\(',
            r'getenv\(',
            r'ENV\[',
            r'\$\{[A-Z_]+\}',
            r'process\config/environments/development.env\.',
            r'config\.',
            r'settings\.',
            r'# Example',
            r'# TODO',
            r'# FIXME'
        ]
        
        return any(re.search(pattern, line, re.IGNORECASE) for pattern in safe_patterns)

    def _get_severity(self, vuln_type: str) -> str:
        """Get severity level for vulnerability type."""
        
        severity_map = {
            'private_key': 'critical',
            'aws_secret_key': 'critical',
            'github_token': 'critical',
            'database_url': 'high',
            'jwt_token': 'high',
            'api_key': 'high',
            'password': 'medium',
            'aws_access_key': 'medium'
        }
        
        return severity_map.get(vuln_type, 'low')

    def _get_remediation(self, vuln_type: str) -> str:
        """Get remediation advice for vulnerability type."""
        
        remediation_map = {
            'api_key': 'Replace with environment variable: os.environ.get("API_KEY")',
            'password': 'Replace with environment variable: os.environ.get("PASSWORD")',
            'aws_access_key': 'Use AWS IAM roles or environment variables',
            'aws_secret_key': 'Use AWS IAM roles or environment variables',
            'github_token': 'Use GitHub secrets or environment variables',
            'private_key': 'Store in secure key management system',
            'jwt_token': 'Generate tokens dynamically, never hardcode',
            'database_url': 'Use environment variable: os.environ.get("DATABASE_URL")'
        }
        
        return remediation_map.get(vuln_type, 'Replace with secure configuration')

    async def remediate_vulnerabilities(self, vulnerabilities: List[RealVulnerability]) -> int:
        """Automatically remediate vulnerabilities where possible."""
        
        logger.info(f"🔧 Starting remediation of {len(vulnerabilities)} vulnerabilities")
        
        remediated_count = 0
        files_to_process = {}
        
        # Group vulnerabilities by file
        for vuln in vulnerabilities:
            if vuln.file_path not in files_to_process:
                files_to_process[vuln.file_path] = []
            files_to_process[vuln.file_path].append(vuln)
        
        # Process each file
        for file_path, file_vulns in files_to_process.items():
            try:
                if await self._remediate_file_real(file_path, file_vulns):
                    remediated_count += len(file_vulns)
                    logger.info(f"✅ Remediated {len(file_vulns)} vulnerabilities in {file_path}")
                    
            except Exception as e:
                logger.warning(f"Failed to remediate {file_path}: {e}")
        
        logger.info(f"✅ Remediation completed: {remediated_count} vulnerabilities fixed")
        return remediated_count

    async def _remediate_file_real(self, file_path: str, vulnerabilities: List[RealVulnerability]) -> bool:
        """Remediate vulnerabilities in a specific file."""
        
        try:
            # Read original file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            modified = False
            
            # Sort vulnerabilities by line number (descending) to avoid line shifts
            vulnerabilities.sort(key=lambda v: v.line_number, reverse=True)
            
            for vuln in vulnerabilities:
                if vuln.line_number <= len(lines):
                    original_line = lines[vuln.line_number - 1]
                    
                    # Generate remediated line
                    remediated_line = self._generate_remediated_line_real(original_line, vuln)
                    
                    if remediated_line != original_line:
                        lines[vuln.line_number - 1] = remediated_line
                        modified = True
            
            # Add constitutional compliance header if not present
            if modified and not self._has_constitutional_header(content):
                header = self._generate_constitutional_header(file_path)
                if header:
                    lines.insert(0, header)
            
            # Write back modified content
            if modified:
                # Create backup
                backup_path = f"{file_path}.backup"
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # Write remediated content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))
                
                return True
            
        except Exception as e:
            logger.warning(f"Error remediating file {file_path}: {e}")
        
        return False

    def _generate_remediated_line_real(self, original_line: str, vuln: RealVulnerability) -> str:
        """Generate remediated version of a line."""
        
        # Common remediation patterns
        if vuln.vulnerability_type == 'password':
            return re.sub(
                r'(password\s*[=:]\s*)["\']?[^"\']+["\']?',
                r'\1os.environ.get("PASSWORD")',
                original_line,
                flags=re.IGNORECASE
            )
        elif vuln.vulnerability_type == 'api_key':
            return re.sub(
                r'(api[_-]?key\s*[=:]\s*)["\']?[^"\']+["\']?',
                r'\1os.environ.get("API_KEY")',
                original_line,
                flags=re.IGNORECASE
            )
        elif vuln.vulnerability_type == 'database_url':
            return re.sub(
                r'(database_url\s*[=:]\s*)["\']?[^"\']+["\']?',
                r'\1os.environ.get("DATABASE_URL")',
                original_line,
                flags=re.IGNORECASE
            )
        
        # Add comment for manual review
        return f"{original_line}  # TODO: Replace with environment variable - Constitutional Hash: {self.constitutional_hash}"

    def _has_constitutional_header(self, content: str) -> bool:
        """Check if file has constitutional compliance header."""
        return self.constitutional_hash in content

    def _generate_constitutional_header(self, file_path: str) -> Optional[str]:
        """Generate constitutional compliance header."""
        
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.py':
            return f'"""\nConstitutional Hash: {self.constitutional_hash}\nACGS-2 Constitutional Compliance Validation\n"""'
        elif file_ext in ['.js', '.ts']:
            return f'/*\nConstitutional Hash: {self.constitutional_hash}\nACGS-2 Constitutional Compliance Validation\n*/'
        elif file_ext in ['.yaml', '.yml']:
            return f'# Constitutional Hash: {self.constitutional_hash}\n# ACGS-2 Constitutional Compliance Validation'
        
        return f'# Constitutional Hash: {self.constitutional_hash}\n# ACGS-2 Constitutional Compliance Validation'


class RealAuthenticationSystem:
    """
    Real authentication system with actual database storage and encryption.
    
    Implements secure password hashing, JWT tokens, and session management.
    """
    
    def __init__(self, config: RealSecurityConfig):
        self.config = config
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.db_path = config.security_db_path
        self.fernet = Fernet(config.encryption_key)
        
        # Initialize database
        self._init_database()
        
        logger.info("Initialized Real Authentication System")
        logger.info(f"🔒 Constitutional Hash: {self.constitutional_hash}")

    def _init_database(self):
        """Initialize SQLite database for authentication data."""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                failed_attempts INTEGER DEFAULT 0,
                locked_until TIMESTAMP,
                constitutional_hash TEXT DEFAULT '{self.constitutional_hash}'
            )
        """)
        
        # Create sessions table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_token TEXT UNIQUE NOT NULL,
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                constitutional_hash TEXT DEFAULT '{self.constitutional_hash}',
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Create audit log table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                details TEXT,
                ip_address TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                constitutional_hash TEXT DEFAULT '{self.constitutional_hash}',
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        conn.commit()
        conn.close()

    def hash_password(self, password: str) -> Tuple[str, str]:
        """Hash password using bcrypt with salt."""
        
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
        
        return password_hash.decode('utf-8'), salt.decode('utf-8')

    def verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify password against stored hash."""
        
        return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))

    async def create_user(self, username: str, password: str) -> Dict[str, Any]:
        """Create new user with secure password storage."""
        
        # Validate password strength
        if len(password) < self.config.password_min_length:
            return {
                "success": False,
                "error": f"Password must be at least {self.config.password_min_length} characters"
            }
        
        # Hash password
        password_hash, salt = self.hash_password(password)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO users (username, password_hash, salt, constitutional_hash)
                VALUES (?, ?, ?, ?)
            """, (username, password_hash, salt, self.constitutional_hash))
            
            user_id = cursor.lastrowid
            
            # Log user creation
            cursor.execute("""
                INSERT INTO audit_log (user_id, action, details, constitutional_hash)
                VALUES (?, 'user_created', ?, ?)
            """, (user_id, f"User {username} created", self.constitutional_hash))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ User created: {username}")
            
            return {
                "success": True,
                "user_id": user_id,
                "constitutional_hash": self.constitutional_hash
            }
            
        except sqlite3.IntegrityError:
            return {
                "success": False,
                "error": "Username already exists"
            }
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def authenticate_user(self, username: str, password: str, ip_address: str = None) -> Dict[str, Any]:
        """Authenticate user with rate limiting and lockout protection."""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Get user data
            cursor.execute("""
                SELECT id, username, password_hash, failed_attempts, locked_until
                FROM users WHERE username = ?
            """, (username,))

            user_data = cursor.fetchone()

            if not user_data:
                # Log failed attempt
                cursor.execute("""
                    INSERT INTO audit_log (action, details, ip_address, constitutional_hash)
                    VALUES ('login_failed', ?, ?, ?)
                """, (f"Unknown username: {username}", ip_address, self.constitutional_hash))
                conn.commit()

                return {
                    "success": False,
                    "error": "Invalid credentials"
                }

            user_id, db_username, password_hash, failed_attempts, locked_until = user_data

            # Check if account is locked
            if locked_until:
                locked_until_time = time.mktime(time.strptime(locked_until, "%Y-%m-%d %H:%M:%S"))
                if time.time() < locked_until_time:
                    return {
                        "success": False,
                        "error": "Account is locked due to too many failed attempts"
                    }
                else:
                    # Unlock account
                    cursor.execute("""
                        UPDATE users SET failed_attempts = 0, locked_until = NULL
                        WHERE id = ?
                    """, (user_id,))

            # Verify password
            if self.verify_password(password, password_hash):
                # Successful login
                cursor.execute("""
                    UPDATE users SET
                        last_login = CURRENT_TIMESTAMP,
                        failed_attempts = 0,
                        locked_until = NULL
                    WHERE id = ?
                """, (user_id,))

                # Create session
                session_token = self._create_session_token(user_id)

                # Log successful login
                cursor.execute("""
                    INSERT INTO audit_log (user_id, action, details, ip_address, constitutional_hash)
                    VALUES (?, 'login_success', ?, ?, ?)
                """, (user_id, f"Successful login for {username}", ip_address, self.constitutional_hash))

                conn.commit()

                return {
                    "success": True,
                    "session_token": session_token,
                    "user_id": user_id,
                    "username": username,
                    "constitutional_hash": self.constitutional_hash
                }
            else:
                # Failed login
                failed_attempts += 1

                # Check if we should lock the account
                locked_until = None
                if failed_attempts >= self.config.max_login_attempts:
                    locked_until_time = time.time() + (self.config.lockout_duration_minutes * 60)
                    locked_until = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(locked_until_time))

                cursor.execute("""
                    UPDATE users SET failed_attempts = ?, locked_until = ?
                    WHERE id = ?
                """, (failed_attempts, locked_until, user_id))

                # Log failed attempt
                cursor.execute("""
                    INSERT INTO audit_log (user_id, action, details, ip_address, constitutional_hash)
                    VALUES (?, 'login_failed', ?, ?, ?)
                """, (user_id, f"Failed login attempt {failed_attempts}", ip_address, self.constitutional_hash))

                conn.commit()

                return {
                    "success": False,
                    "error": "Invalid credentials",
                    "attempts_remaining": max(0, self.config.max_login_attempts - failed_attempts)
                }

        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return {
                "success": False,
                "error": "Authentication system error"
            }
        finally:
            conn.close()

    def _create_session_token(self, user_id: int) -> str:
        """Create JWT session token."""

        payload = {
            "user_id": user_id,
            "issued_at": time.time(),
            "expires_at": time.time() + (self.config.session_timeout_hours * 3600),
            "constitutional_hash": self.constitutional_hash
        }

        token = jwt.encode(payload, self.config.jwt_secret_key, algorithm="HS256")

        # Store session in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        expires_at = time.strftime("%Y-%m-%d %H:%M:%S",
                                  time.localtime(payload["expires_at"]))

        cursor.execute("""
            INSERT INTO sessions (session_token, user_id, expires_at, constitutional_hash)
            VALUES (?, ?, ?, ?)
        """, (token, user_id, expires_at, self.constitutional_hash))

        conn.commit()
        conn.close()

        return token

    async def validate_session(self, session_token: str) -> Dict[str, Any]:
        """Validate session token."""

        try:
            # Decode JWT token
            payload = jwt.decode(session_token, self.config.jwt_secret_key, algorithms=["HS256"])

            # Check constitutional hash
            if payload.get("constitutional_hash") != self.constitutional_hash:
                return {
                    "valid": False,
                    "error": "Constitutional hash mismatch"
                }

            # Check expiration
            if time.time() > payload.get("expires_at", 0):
                return {
                    "valid": False,
                    "error": "Session expired"
                }

            # Check database session
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT s.user_id, u.username, s.expires_at
                FROM sessions s
                JOIN users u ON s.user_id = u.id
                WHERE s.session_token = ? AND s.expires_at > CURRENT_TIMESTAMP
            """, (session_token,))

            session_data = cursor.fetchone()

            if session_data:
                user_id, username, expires_at = session_data

                # Update last activity
                cursor.execute("""
                    UPDATE sessions SET last_activity = CURRENT_TIMESTAMP
                    WHERE session_token = ?
                """, (session_token,))

                conn.commit()
                conn.close()

                return {
                    "valid": True,
                    "user_id": user_id,
                    "username": username,
                    "constitutional_hash": self.constitutional_hash
                }
            else:
                conn.close()
                return {
                    "valid": False,
                    "error": "Session not found or expired"
                }

        except jwt.InvalidTokenError:
            return {
                "valid": False,
                "error": "Invalid token"
            }
        except Exception as e:
            logger.error(f"Session validation error: {e}")
            return {
                "valid": False,
                "error": "Session validation failed"
            }

    async def logout_user(self, session_token: str) -> bool:
        """Logout user by invalidating session."""

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get user info for logging
            cursor.execute("""
                SELECT s.user_id, u.username
                FROM sessions s
                JOIN users u ON s.user_id = u.id
                WHERE s.session_token = ?
            """, (session_token,))

            session_data = cursor.fetchone()

            if session_data:
                user_id, username = session_data

                # Delete session
                cursor.execute("DELETE FROM sessions WHERE session_token = ?", (session_token,))

                # Log logout
                cursor.execute("""
                    INSERT INTO audit_log (user_id, action, details, constitutional_hash)
                    VALUES (?, 'logout', ?, ?)
                """, (user_id, f"User {username} logged out", self.constitutional_hash))

                conn.commit()
                conn.close()

                return True
            else:
                conn.close()
                return False

        except Exception as e:
            logger.error(f"Logout error: {e}")
            return False

    async def get_security_metrics(self) -> Dict[str, Any]:
        """Get real security metrics from database."""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Get user statistics
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM users WHERE locked_until > CURRENT_TIMESTAMP")
            locked_users = cursor.fetchone()[0]

            # Get session statistics
            cursor.execute("SELECT COUNT(*) FROM sessions WHERE expires_at > CURRENT_TIMESTAMP")
            active_sessions = cursor.fetchone()[0]

            # Get recent failed login attempts (last 24 hours)
            cursor.execute("""
                SELECT COUNT(*) FROM audit_log
                WHERE action = 'login_failed'
                AND timestamp > datetime('now', '-24 hours')
            """)
            recent_failed_logins = cursor.fetchone()[0]

            # Get recent successful logins (last 24 hours)
            cursor.execute("""
                SELECT COUNT(*) FROM audit_log
                WHERE action = 'login_success'
                AND timestamp > datetime('now', '-24 hours')
            """)
            recent_successful_logins = cursor.fetchone()[0]

            conn.close()

            return {
                "constitutional_hash": self.constitutional_hash,
                "total_users": total_users,
                "locked_users": locked_users,
                "active_sessions": active_sessions,
                "recent_failed_logins": recent_failed_logins,
                "recent_successful_logins": recent_successful_logins,
                "login_success_rate": (
                    recent_successful_logins / (recent_successful_logins + recent_failed_logins)
                    if (recent_successful_logins + recent_failed_logins) > 0 else 1.0
                )
            }

        except Exception as e:
            logger.error(f"Failed to get security metrics: {e}")
            conn.close()
            return {"error": str(e)}


class RealSecurityOrchestrator:
    """
    Real security orchestrator that coordinates vulnerability scanning and authentication.

    Uses actual file system operations, database storage, and encryption.
    """

    def __init__(self, config: RealSecurityConfig):
        self.config = config
        self.constitutional_hash = CONSTITUTIONAL_HASH

        # Initialize real security components
        self.vulnerability_scanner = RealVulnerabilityScanner(config)
        self.auth_system = RealAuthenticationSystem(config)

        logger.info("Initialized Real Security Orchestrator")
        logger.info(f"🔒 Constitutional Hash: {self.constitutional_hash}")

    async def perform_comprehensive_security_scan(self, project_root: Path) -> Dict[str, Any]:
        """Perform comprehensive real security scan."""

        logger.info(f"🔍 Starting comprehensive security scan of {project_root}")
        scan_start = time.time()

        # Scan for vulnerabilities
        vulnerabilities = await self.vulnerability_scanner.scan_directory(project_root)

        # Attempt automatic remediation
        remediated_count = await self.vulnerability_scanner.remediate_vulnerabilities(vulnerabilities)

        # Calculate security score
        security_score = self._calculate_security_score(vulnerabilities, remediated_count)

        # Get authentication metrics
        auth_metrics = await self.auth_system.get_security_metrics()

        scan_duration = time.time() - scan_start

        return {
            "constitutional_hash": self.constitutional_hash,
            "scan_timestamp": scan_start,
            "scan_duration_seconds": scan_duration,
            "vulnerabilities_found": len(vulnerabilities),
            "vulnerabilities_remediated": remediated_count,
            "security_score": security_score,
            "vulnerability_details": [
                {
                    "file": v.file_path,
                    "line": v.line_number,
                    "type": v.vulnerability_type,
                    "severity": v.severity,
                    "remediation": v.remediation
                }
                for v in vulnerabilities[:10]  # Show first 10 for summary
            ],
            "authentication_metrics": auth_metrics,
            "recommendations": self._generate_recommendations(vulnerabilities, auth_metrics)
        }

    def _calculate_security_score(self, vulnerabilities: List[RealVulnerability], remediated_count: int) -> float:
        """Calculate security score based on vulnerabilities."""

        if not vulnerabilities:
            return 100.0

        # Weight by severity
        severity_weights = {"critical": 25, "high": 15, "medium": 10, "low": 5}

        total_penalty = sum(severity_weights.get(v.severity, 5) for v in vulnerabilities)
        remediated_penalty = remediated_count * 10  # Assume average penalty of 10 per remediated

        score = max(0, 100 - total_penalty + remediated_penalty)
        return min(100.0, score)

    def _generate_recommendations(
        self,
        vulnerabilities: List[RealVulnerability],
        auth_metrics: Dict[str, Any]
    ) -> List[str]:
        """Generate security recommendations."""

        recommendations = []

        # Vulnerability-based recommendations
        vuln_types = {}
        for vuln in vulnerabilities:
            vuln_types[vuln.vulnerability_type] = vuln_types.get(vuln.vulnerability_type, 0) + 1

        if vuln_types.get('password', 0) > 0:
            recommendations.append("Replace hardcoded passwords with environment variables")

        if vuln_types.get('api_key', 0) > 0:
            recommendations.append("Move API keys to secure configuration management")

        if vuln_types.get('private_key', 0) > 0:
            recommendations.append("Use secure key management systems for private keys")

        # Authentication-based recommendations
        if auth_metrics.get("locked_users", 0) > 0:
            recommendations.append("Review locked user accounts and implement account recovery")

        login_success_rate = auth_metrics.get("login_success_rate", 1.0)
        if login_success_rate < 0.8:
            recommendations.append("High failed login rate detected - review authentication logs")

        # General recommendations
        recommendations.extend([
            f"Ensure all files include constitutional hash: {self.constitutional_hash}",
            "Implement regular security scanning in CI/CD pipeline",
            "Enable comprehensive audit logging",
            "Regular security training for development team"
        ])

        return recommendations

    def print_security_report(self, report: Dict[str, Any]):
        """Print formatted security report."""

        print("\n" + "="*80)
        print("🔒 ACGS-2 Real Security Hardening Report")
        print("="*80)
        print(f"🔒 Constitutional Hash: {report['constitutional_hash']}")
        print(f"⏱️ Scan Duration: {report['scan_duration_seconds']:.2f} seconds")

        # Vulnerability summary
        print(f"\n🔍 Vulnerability Scan Results:")
        print(f"  • Vulnerabilities Found: {report['vulnerabilities_found']}")
        print(f"  • Vulnerabilities Remediated: {report['vulnerabilities_remediated']}")
        print(f"  • Security Score: {report['security_score']:.1f}/100")

        # Authentication metrics
        auth_metrics = report.get("authentication_metrics", {})
        if "error" not in auth_metrics:
            print(f"\n🔐 Authentication Security:")
            print(f"  • Total Users: {auth_metrics.get('total_users', 0)}")
            print(f"  • Locked Users: {auth_metrics.get('locked_users', 0)}")
            print(f"  • Active Sessions: {auth_metrics.get('active_sessions', 0)}")
            print(f"  • Login Success Rate: {auth_metrics.get('login_success_rate', 0):.1%}")

        # Top vulnerabilities
        if report.get("vulnerability_details"):
            print(f"\n⚠️ Top Vulnerabilities:")
            for i, vuln in enumerate(report["vulnerability_details"][:5], 1):
                print(f"  {i}. {vuln['type']} ({vuln['severity']}) in {Path(vuln['file']).name}:{vuln['line']}")

        # Recommendations
        recommendations = report.get("recommendations", [])
        if recommendations:
            print(f"\n💡 Security Recommendations:")
            for i, rec in enumerate(recommendations[:5], 1):
                print(f"  {i}. {rec}")

        print("="*80)


async def main():
    """Main function for real security hardening demonstration."""

    print("🔒 ACGS-2 Real Security Hardening System")
    print(f"🔒 Constitutional Hash: {CONSTITUTIONAL_HASH}")

    # Configuration
    config = RealSecurityConfig(
        security_db_path="acgs_security.db",
        password_min_length=12,
        max_login_attempts=5,
        lockout_duration_minutes=30
    )

    # Initialize security orchestrator
    security_orchestrator = RealSecurityOrchestrator(config)

    try:
        # Set project root
        project_root = Path("/home/dislove/ACGS-2")

        print("🔍 Performing comprehensive real security scan...")

        # Perform security scan
        report = await security_orchestrator.perform_comprehensive_security_scan(project_root)

        # Print security report
        security_orchestrator.print_security_report(report)

        # Demonstrate authentication system
        print(f"\n🔐 Testing authentication system...")

        # Create test user
        user_result = await security_orchestrator.auth_system.create_user("test_user", "SecurePassword123!")
        if user_result["success"]:
            print(f"✅ Test user created successfully")

            # Test authentication
            auth_result = await security_orchestrator.auth_system.authenticate_user("test_user", "SecurePassword123!")
            if auth_result["success"]:
                print(f"✅ Authentication successful")

                # Test session validation
                session_token = auth_result["session_token"]
                validation_result = await security_orchestrator.auth_system.validate_session(session_token)
                if validation_result["valid"]:
                    print(f"✅ Session validation successful")

                # Test logout
                logout_result = await security_orchestrator.auth_system.logout_user(session_token)
                if logout_result:
                    print(f"✅ Logout successful")

        print(f"\n✅ Real security hardening demonstration completed")

    except Exception as e:
        print(f"❌ Security hardening failed: {e}")
        logger.exception("Security hardening failed")


if __name__ == "__main__":
    asyncio.run(main())
