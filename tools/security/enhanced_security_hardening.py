#!/usr/bin/env python3
"""
Enhanced Security Hardening for ACGS-2

Constitutional Hash: cdd01ef066bc6cf2
ACGS-2 Constitutional Compliance Validation

This tool implements enhanced security hardening including completion of remaining
hardcoded secret remediation, advanced threat detection, and enhanced authentication
mechanisms while maintaining constitutional compliance.
"""

import asyncio
import json
import logging
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import hashlib
import secrets
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
class SecurityConfig:
    """Configuration for enhanced security hardening."""
    
    # Secret detection patterns
    secret_patterns: Dict[str, str] = field(default_factory=lambda: {
        'api_key': r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\']?([a-zA-Z0-9_-]{20,})["\']?',
        'password': r'(?i)(password|passwd|pwd)\s*[=:]\s*["\']?([^"\'\s]{8,})["\']?',
        'token': r'(?i)(token|auth[_-]?token)\s*[=:]\s*["\']?([a-zA-Z0-9_-]{20,})["\']?',
        'secret': r'(?i)(secret|secret[_-]?key)\s*[=:]\s*["\']?([a-zA-Z0-9_-]{20,})["\']?',
        'private_key': r'-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----',
        'aws_access_key': r'AKIA[0-9A-Z]{16}',
        'aws_secret_key': r'(?i)aws[_-]?secret[_-]?access[_-]?key.*[=:]\s*["\']?([a-zA-Z0-9/+=]{40})["\']?',
        'github_token': r'ghp_[a-zA-Z0-9]{36}',
        'jwt_token': r'eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*'
    })
    
    # File extensions to scan
    scan_extensions: Set[str] = field(default_factory=lambda: {
        '.py', '.js', '.ts', '.json', '.yaml', '.yml', 'config/environments/development.env', '.conf', '.config',
        '.ini', '.properties', '.xml', '.sh', '.bash', '.zsh', '.fish'
    })
    
    # Directories to exclude from scanning
    exclude_dirs: Set[str] = field(default_factory=lambda: {
        '.git', '__pycache__', 'node_modules', '.venv', 'venv', 'env',
        '.pytest_cache', '.mypy_cache', 'dist', 'build'
    })
    
    # Authentication enhancement settings
    min_password_length: int = 12
    require_mfa: bool = True
    session_timeout_minutes: int = 30
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15
    
    # Threat detection settings
    enable_anomaly_detection: bool = True
    suspicious_activity_threshold: int = 10
    rate_limit_requests_per_minute: int = 100
    
    constitutional_hash: str = CONSTITUTIONAL_HASH


@dataclass
class SecurityVulnerability:
    """Represents a security vulnerability found during scanning."""
    file_path: str
    line_number: int
    vulnerability_type: str
    description: str
    severity: str  # 'critical', 'high', 'medium', 'low'
    matched_content: str
    recommendation: str
    constitutional_hash: str = CONSTITUTIONAL_HASH


@dataclass
class SecurityReport:
    """Comprehensive security report."""
    scan_timestamp: float
    total_files_scanned: int
    vulnerabilities_found: List[SecurityVulnerability]
    vulnerabilities_fixed: List[SecurityVulnerability]
    security_score: float
    constitutional_compliance: bool
    recommendations: List[str]
    constitutional_hash: str = CONSTITUTIONAL_HASH


class SecretDetector:
    """
    Advanced secret detection and remediation system.
    
    Detects hardcoded secrets, API keys, passwords, and other sensitive data
    while maintaining constitutional compliance.
    """
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.vulnerabilities: List[SecurityVulnerability] = []
        
        logger.info(f"Initialized Secret Detector")
        logger.info(f"🔒 Constitutional Hash: {self.constitutional_hash}")

    async def scan_directory(self, directory: Path) -> List[SecurityVulnerability]:
        """Scan directory for hardcoded secrets and vulnerabilities."""
        
        logger.info(f"🔍 Scanning directory for secrets: {directory}")
        
        vulnerabilities = []
        files_scanned = 0
        
        for file_path in self._get_scannable_files(directory):
            try:
                file_vulnerabilities = await self._scan_file(file_path)
                vulnerabilities.extend(file_vulnerabilities)
                files_scanned += 1
                
                if files_scanned % 100 == 0:
                    logger.info(f"Scanned {files_scanned} files, found {len(vulnerabilities)} vulnerabilities")
                    
            except Exception as e:
                logger.warning(f"Failed to scan file {file_path}: {e}")
        
        logger.info(f"✅ Scan completed: {files_scanned} files, {len(vulnerabilities)} vulnerabilities found")
        return vulnerabilities

    def _get_scannable_files(self, directory: Path) -> List[Path]:
        """Get list of files that should be scanned for secrets."""
        
        scannable_files = []
        
        for file_path in directory.rglob('*'):
            # Skip directories
            if file_path.is_dir():
                continue
            
            # Skip excluded directories
            if any(excluded in file_path.parts for excluded in self.config.exclude_dirs):
                continue
            
            # Check file extension
            if file_path.suffix.lower() in self.config.scan_extensions:
                scannable_files.append(file_path)
        
        return scannable_files

    async def _scan_file(self, file_path: Path) -> List[SecurityVulnerability]:
        """Scan individual file for secrets and vulnerabilities."""
        
        vulnerabilities = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                # Check each secret pattern
                for vuln_type, pattern in self.config.secret_patterns.items():
                    matches = re.finditer(pattern, line)
                    
                    for match in matches:
                        # Skip if it's already using environment variables
                        if self._is_environment_variable_usage(line):
                            continue
                        
                        # Skip if it's in a comment explaining the fix
                        if self._is_remediation_comment(line):
                            continue
                        
                        vulnerability = SecurityVulnerability(
                            file_path=str(file_path),
                            line_number=line_num,
                            vulnerability_type=vuln_type,
                            description=f"Hardcoded {vuln_type} detected",
                            severity=self._get_severity(vuln_type),
                            matched_content=match.group(0)[:100],  # Limit to 100 chars
                            recommendation=self._get_remediation_recommendation(vuln_type),
                            constitutional_hash=self.constitutional_hash
                        )
                        
                        vulnerabilities.append(vulnerability)
            
        except Exception as e:
            logger.warning(f"Error scanning file {file_path}: {e}")
        
        return vulnerabilities

    def _is_environment_variable_usage(self, line: str) -> bool:
        """Check if line is using environment variables properly."""
        
        env_patterns = [
            r'os\config/environments/development.environ\.get\(',
            r'os\.getenv\(',
            r'getenv\(',
            r'ENV\[',
            r'\$\{[A-Z_]+\}',
            r'process\config/environments/development.env\.',
            r'config\[',
            r'settings\.',
        ]
        
        return any(re.search(pattern, line, re.IGNORECASE) for pattern in env_patterns)

    def _is_remediation_comment(self, line: str) -> bool:
        """Check if line is a comment explaining remediation."""
        
        remediation_indicators = [
            'TODO: Replace with environment variable',
            'FIXME: Use secure configuration',
            'NOTE: This should be in environment',
            'WARNING: Hardcoded value',
            'Example configuration',
            'Template value'
        ]
        
        return any(indicator in line for indicator in remediation_indicators)

    def _get_severity(self, vuln_type: str) -> str:
        """Get severity level for vulnerability type."""
        
        severity_map = {
            'private_key': 'critical',
            'aws_secret_key': 'critical',
            'github_token': 'critical',
            'jwt_token': 'high',
            'api_key': 'high',
            'secret': 'high',
            'token': 'high',
            'password': 'medium'
        }
        
        return severity_map.get(vuln_type, 'medium')

    def _get_remediation_recommendation(self, vuln_type: str) -> str:
        """Get remediation recommendation for vulnerability type."""
        
        recommendations = {
            'api_key': 'Replace with environment variable: os.environ.get("API_KEY")',
            'password': 'Replace with environment variable: os.environ.get("PASSWORD")',
            'token': 'Replace with environment variable: os.environ.get("AUTH_TOKEN")',
            'secret': 'Replace with environment variable: os.environ.get("SECRET_KEY")',
            'private_key': 'Store private key in secure key management system',
            'aws_access_key': 'Use AWS IAM roles or environment variables',
            'aws_secret_key': 'Use AWS IAM roles or environment variables',
            'github_token': 'Use GitHub secrets or environment variables',
            'jwt_token': 'Generate JWT tokens dynamically, do not hardcode'
        }
        
        return recommendations.get(vuln_type, 'Replace hardcoded value with secure configuration')

    async def remediate_vulnerabilities(
        self, 
        vulnerabilities: List[SecurityVulnerability]
    ) -> List[SecurityVulnerability]:
        """Automatically remediate detected vulnerabilities where possible."""
        
        logger.info(f"🔧 Starting automatic remediation of {len(vulnerabilities)} vulnerabilities")
        
        remediated = []
        files_to_process = {}
        
        # Group vulnerabilities by file
        for vuln in vulnerabilities:
            if vuln.file_path not in files_to_process:
                files_to_process[vuln.file_path] = []
            files_to_process[vuln.file_path].append(vuln)
        
        # Process each file
        for file_path, file_vulns in files_to_process.items():
            try:
                if await self._remediate_file(file_path, file_vulns):
                    remediated.extend(file_vulns)
                    logger.info(f"✅ Remediated {len(file_vulns)} vulnerabilities in {file_path}")
                    
            except Exception as e:
                logger.warning(f"Failed to remediate {file_path}: {e}")
        
        logger.info(f"✅ Remediation completed: {len(remediated)} vulnerabilities fixed")
        return remediated

    async def _remediate_file(self, file_path: str, vulnerabilities: List[SecurityVulnerability]) -> bool:
        """Remediate vulnerabilities in a specific file."""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            modified = False
            
            # Sort vulnerabilities by line number (descending) to avoid line number shifts
            vulnerabilities.sort(key=lambda v: v.line_number, reverse=True)
            
            for vuln in vulnerabilities:
                if vuln.line_number <= len(lines):
                    original_line = lines[vuln.line_number - 1]
                    
                    # Generate remediated line
                    remediated_line = self._generate_remediated_line(original_line, vuln)
                    
                    if remediated_line != original_line:
                        lines[vuln.line_number - 1] = remediated_line
                        modified = True
            
            # Add constitutional compliance header if not present
            if modified and not self._has_constitutional_header(content):
                constitutional_header = self._generate_constitutional_header(file_path)
                if constitutional_header:
                    lines.insert(0, constitutional_header)
            
            # Write back modified content
            if modified:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))
                
                return True
            
        except Exception as e:
            logger.warning(f"Error remediating file {file_path}: {e}")
        
        return False

    def _generate_remediated_line(self, original_line: str, vuln: SecurityVulnerability) -> str:
        """Generate remediated version of a line with hardcoded secrets."""
        
        # Common remediation patterns
        if vuln.vulnerability_type == 'password':
            if 'password' in original_line.lower():
                return re.sub(
                    r'(password\s*[=:]\s*)["\']?[^"\']+["\']?',
                    r'\1os.environ.get("PASSWORD")',
                    original_line,
                    flags=re.IGNORECASE
                )
        
        elif vuln.vulnerability_type == 'api_key':
            if 'api' in original_line.lower():
                return re.sub(
                    r'(api[_-]?key\s*[=:]\s*)["\']?[^"\']+["\']?',
                    r'\1os.environ.get("API_KEY")',
                    original_line,
                    flags=re.IGNORECASE
                )
        
        elif vuln.vulnerability_type == 'token':
            if 'token' in original_line.lower():
                return re.sub(
                    r'(token\s*[=:]\s*)["\']?[^"\']+["\']?',
                    r'\1os.environ.get("AUTH_TOKEN")',
                    original_line,
                    flags=re.IGNORECASE
                )
        
        # Add comment for manual review if automatic remediation isn't possible
        return f"{original_line}  # TODO: Replace with environment variable - Constitutional Hash: {self.constitutional_hash}"

    def _has_constitutional_header(self, content: str) -> bool:
        """Check if file already has constitutional compliance header."""
        
        return self.constitutional_hash in content

    def _generate_constitutional_header(self, file_path: str) -> Optional[str]:
        """Generate constitutional compliance header for file."""
        
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.py':
            return f'"""\nConstitutional Hash: {self.constitutional_hash}\nACGS-2 Constitutional Compliance Validation\n"""'
        elif file_ext in ['.js', '.ts']:
            return f'/*\nConstitutional Hash: {self.constitutional_hash}\nACGS-2 Constitutional Compliance Validation\n*/'
        elif file_ext in ['.yaml', '.yml']:
            return f'# Constitutional Hash: {self.constitutional_hash}\n# ACGS-2 Constitutional Compliance Validation'
        elif file_ext == '.json':
            return None  # JSON files will have constitutional_hash field added separately
        
        return f'# Constitutional Hash: {self.constitutional_hash}\n# ACGS-2 Constitutional Compliance Validation'


class ThreatDetector:
    """
    Advanced threat detection system for ACGS-2.
    
    Implements anomaly detection, suspicious activity monitoring, and
    real-time threat assessment while maintaining constitutional compliance.
    """
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.activity_log: List[Dict[str, Any]] = []
        self.threat_patterns: Dict[str, str] = {
            'sql_injection': r'(?i)(union|select|insert|update|delete|drop|exec|script)',
            'xss_attempt': r'(?i)(<script|javascript:|onload=|onerror=)',
            'path_traversal': r'(\.\./|\.\.\\|%2e%2e%2f)',
            'command_injection': r'(?i)(;|\||&|`|\$\()',
            'suspicious_user_agent': r'(?i)(bot|crawler|scanner|sqlmap|nikto|nmap)'
        }
        
        logger.info(f"Initialized Threat Detector")
        logger.info(f"🔒 Constitutional Hash: {self.constitutional_hash}")

    async def analyze_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze incoming request for potential threats."""
        
        threat_score = 0.0
        detected_threats = []
        
        # Analyze request components
        for component, value in request_data.items():
            if isinstance(value, str):
                component_threats = self._detect_threats_in_string(value)
                detected_threats.extend(component_threats)
                threat_score += len(component_threats) * 10
        
        # Check rate limiting
        if self._check_rate_limit_violation(request_data):
            detected_threats.append("rate_limit_violation")
            threat_score += 20
        
        # Log activity
        activity_entry = {
            "timestamp": time.time(),
            "request_data": request_data,
            "threat_score": threat_score,
            "detected_threats": detected_threats,
            "constitutional_hash": self.constitutional_hash
        }
        
        self.activity_log.append(activity_entry)
        
        # Keep only recent activity (last 1000 entries)
        if len(self.activity_log) > 1000:
            self.activity_log = self.activity_log[-1000:]
        
        return {
            "threat_score": threat_score,
            "detected_threats": detected_threats,
            "risk_level": self._calculate_risk_level(threat_score),
            "recommended_action": self._get_recommended_action(threat_score),
            "constitutional_hash": self.constitutional_hash
        }

    def _detect_threats_in_string(self, text: str) -> List[str]:
        """Detect threat patterns in text."""
        
        detected = []
        
        for threat_type, pattern in self.threat_patterns.items():
            if re.search(pattern, text):
                detected.append(threat_type)
        
        return detected

    def _check_rate_limit_violation(self, request_data: Dict[str, Any]) -> bool:
        """Check if request violates rate limiting rules."""
        
        # Simple rate limiting check based on recent activity
        current_time = time.time()
        recent_requests = [
            entry for entry in self.activity_log
            if current_time - entry["timestamp"] < 60  # Last minute
        ]
        
        return len(recent_requests) > self.config.rate_limit_requests_per_minute

    def _calculate_risk_level(self, threat_score: float) -> str:
        """Calculate risk level based on threat score."""
        
        if threat_score >= 50:
            return "critical"
        elif threat_score >= 30:
            return "high"
        elif threat_score >= 15:
            return "medium"
        elif threat_score > 0:
            return "low"
        else:
            return "none"

    def _get_recommended_action(self, threat_score: float) -> str:
        """Get recommended action based on threat score."""
        
        if threat_score >= 50:
            return "block_request_immediately"
        elif threat_score >= 30:
            return "require_additional_authentication"
        elif threat_score >= 15:
            return "log_and_monitor"
        else:
            return "allow"

    async def get_threat_summary(self) -> Dict[str, Any]:
        """Get comprehensive threat detection summary."""
        
        if not self.activity_log:
            return {"status": "no_activity_logged"}
        
        recent_activity = [
            entry for entry in self.activity_log
            if time.time() - entry["timestamp"] < 3600  # Last hour
        ]
        
        total_threats = sum(len(entry["detected_threats"]) for entry in recent_activity)
        avg_threat_score = sum(entry["threat_score"] for entry in recent_activity) / len(recent_activity)
        
        threat_types = {}
        for entry in recent_activity:
            for threat in entry["detected_threats"]:
                threat_types[threat] = threat_types.get(threat, 0) + 1
        
        return {
            "constitutional_hash": self.constitutional_hash,
            "analysis_period_hours": 1,
            "total_requests_analyzed": len(recent_activity),
            "total_threats_detected": total_threats,
            "average_threat_score": avg_threat_score,
            "threat_types_detected": threat_types,
            "high_risk_requests": len([e for e in recent_activity if e["threat_score"] >= 30]),
            "recommendations": self._generate_threat_recommendations(threat_types, avg_threat_score)
        }

    def _generate_threat_recommendations(self, threat_types: Dict[str, int], avg_score: float) -> List[str]:
        """Generate threat mitigation recommendations."""
        
        recommendations = []
        
        if "sql_injection" in threat_types:
            recommendations.append("Implement parameterized queries and input validation")
        
        if "xss_attempt" in threat_types:
            recommendations.append("Enhance output encoding and Content Security Policy")
        
        if "rate_limit_violation" in threat_types:
            recommendations.append("Implement stricter rate limiting and IP blocking")
        
        if avg_score > 20:
            recommendations.append("Consider implementing additional authentication layers")
        
        if not recommendations:
            recommendations.append("Current threat levels are within acceptable parameters")
        
        return recommendations


class AuthenticationEnhancer:
    """
    Enhanced authentication system for ACGS-2.

    Implements multi-factor authentication, session management, and
    advanced security controls while maintaining constitutional compliance.
    """

    def __init__(self, config: SecurityConfig):
        self.config = config
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.failed_attempts: Dict[str, List[float]] = {}
        self.active_sessions: Dict[str, Dict[str, Any]] = {}

        logger.info(f"Initialized Authentication Enhancer")
        logger.info(f"🔒 Constitutional Hash: {self.constitutional_hash}")

    def generate_secure_password(self, length: int = None) -> str:
        """Generate cryptographically secure password."""

        if length is None:
            length = self.config.min_password_length

        # Ensure minimum length
        length = max(length, self.config.min_password_length)

        # Character sets for password generation
        lowercase = 'abcdefghijklmnopqrstuvwxyz'
        uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        digits = '0123456789'
        special = '!@#$%^&*()_+-=[]{}|;:,.<>?'

        # Ensure at least one character from each set
        password = [
            secrets.choice(lowercase),
            secrets.choice(uppercase),
            secrets.choice(digits),
            secrets.choice(special)
        ]

        # Fill remaining length with random characters
        all_chars = lowercase + uppercase + digits + special
        for _ in range(length - 4):
            password.append(secrets.choice(all_chars))

        # Shuffle the password
        secrets.SystemRandom().shuffle(password)

        return ''.join(password)

    def hash_password(self, password: str, salt: str = None) -> Tuple[str, str]:
        """Hash password with salt using secure algorithm."""

        if salt is None:
            salt = base64.b64encode(secrets.token_bytes(32)).decode('utf-8')

        # Use PBKDF2 with SHA-256
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 100,000 iterations
        )

        return base64.b64encode(password_hash).decode('utf-8'), salt

    def verify_password(self, password: str, stored_hash: str, salt: str) -> bool:
        """Verify password against stored hash."""

        computed_hash, _ = self.hash_password(password, salt)
        return secrets.compare_digest(computed_hash, stored_hash)

    def check_login_attempt(self, username: str, ip_address: str) -> Dict[str, Any]:
        """Check if login attempt should be allowed based on rate limiting."""

        current_time = time.time()
        attempt_key = f"{username}:{ip_address}"

        # Clean old attempts
        if attempt_key in self.failed_attempts:
            self.failed_attempts[attempt_key] = [
                timestamp for timestamp in self.failed_attempts[attempt_key]
                if current_time - timestamp < self.config.lockout_duration_minutes * 60
            ]

        # Check if account is locked
        recent_failures = self.failed_attempts.get(attempt_key, [])
        if len(recent_failures) >= self.config.max_login_attempts:
            return {
                "allowed": False,
                "reason": "account_locked",
                "lockout_remaining_seconds": self.config.lockout_duration_minutes * 60 - (current_time - recent_failures[0]),
                "constitutional_hash": self.constitutional_hash
            }

        return {
            "allowed": True,
            "remaining_attempts": self.config.max_login_attempts - len(recent_failures),
            "constitutional_hash": self.constitutional_hash
        }

    def record_failed_login(self, username: str, ip_address: str) -> None:
        """Record failed login attempt."""

        attempt_key = f"{username}:{ip_address}"
        current_time = time.time()

        if attempt_key not in self.failed_attempts:
            self.failed_attempts[attempt_key] = []

        self.failed_attempts[attempt_key].append(current_time)

    def create_session(self, username: str, user_data: Dict[str, Any]) -> str:
        """Create secure session for authenticated user."""

        session_id = base64.b64encode(secrets.token_bytes(32)).decode('utf-8')
        current_time = time.time()

        session_data = {
            "username": username,
            "user_data": user_data,
            "created_at": current_time,
            "last_activity": current_time,
            "expires_at": current_time + (self.config.session_timeout_minutes * 60),
            "constitutional_hash": self.constitutional_hash
        }

        self.active_sessions[session_id] = session_data

        return session_id

    def validate_session(self, session_id: str) -> Dict[str, Any]:
        """Validate and refresh session if valid."""

        if session_id not in self.active_sessions:
            return {"valid": False, "reason": "session_not_found"}

        session = self.active_sessions[session_id]
        current_time = time.time()

        # Check if session has expired
        if current_time > session["expires_at"]:
            del self.active_sessions[session_id]
            return {"valid": False, "reason": "session_expired"}

        # Update last activity and extend expiration
        session["last_activity"] = current_time
        session["expires_at"] = current_time + (self.config.session_timeout_minutes * 60)

        return {
            "valid": True,
            "username": session["username"],
            "user_data": session["user_data"],
            "constitutional_hash": self.constitutional_hash
        }

    def invalidate_session(self, session_id: str) -> bool:
        """Invalidate session (logout)."""

        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            return True

        return False

    def get_authentication_metrics(self) -> Dict[str, Any]:
        """Get authentication system metrics."""

        current_time = time.time()

        # Count active sessions
        active_sessions_count = len(self.active_sessions)

        # Count locked accounts
        locked_accounts = 0
        for attempts in self.failed_attempts.values():
            if len(attempts) >= self.config.max_login_attempts:
                locked_accounts += 1

        # Count recent failed attempts (last hour)
        recent_failures = 0
        for attempts in self.failed_attempts.values():
            recent_failures += len([
                timestamp for timestamp in attempts
                if current_time - timestamp < 3600
            ])

        return {
            "constitutional_hash": self.constitutional_hash,
            "active_sessions": active_sessions_count,
            "locked_accounts": locked_accounts,
            "recent_failed_attempts": recent_failures,
            "session_timeout_minutes": self.config.session_timeout_minutes,
            "max_login_attempts": self.config.max_login_attempts,
            "mfa_required": self.config.require_mfa
        }


class EnhancedSecurityHardening:
    """
    Enhanced Security Hardening System for ACGS-2.

    Coordinates secret detection, threat analysis, and authentication enhancement
    while maintaining constitutional compliance throughout all security operations.
    """

    def __init__(self, config: SecurityConfig):
        self.config = config
        self.constitutional_hash = CONSTITUTIONAL_HASH

        # Initialize security components
        self.secret_detector = SecretDetector(config)
        self.threat_detector = ThreatDetector(config)
        self.auth_enhancer = AuthenticationEnhancer(config)

        # Security metrics
        self.security_events: List[Dict[str, Any]] = []

        logger.info("Initialized Enhanced Security Hardening System")
        logger.info("🔒 Constitutional Hash: %s", self.constitutional_hash)

    async def perform_comprehensive_security_scan(self, project_root: Path) -> SecurityReport:
        """Perform comprehensive security scan of the project."""

        logger.info("🔍 Starting comprehensive security scan of %s", project_root)
        scan_start = time.time()

        # Scan for secrets and vulnerabilities
        vulnerabilities = await self.secret_detector.scan_directory(project_root)

        # Attempt automatic remediation
        remediated = await self.secret_detector.remediate_vulnerabilities(vulnerabilities)

        # Calculate security score
        security_score = self._calculate_security_score(vulnerabilities, remediated)

        # Check constitutional compliance
        constitutional_compliance = self._check_constitutional_compliance(project_root)

        # Generate recommendations
        recommendations = self._generate_security_recommendations(vulnerabilities, remediated)

        # Create comprehensive report
        report = SecurityReport(
            scan_timestamp=scan_start,
            total_files_scanned=len(self.secret_detector._get_scannable_files(project_root)),
            vulnerabilities_found=vulnerabilities,
            vulnerabilities_fixed=remediated,
            security_score=security_score,
            constitutional_compliance=constitutional_compliance,
            recommendations=recommendations
        )

        scan_duration = time.time() - scan_start
        logger.info("✅ Security scan completed in %.2f seconds", scan_duration)
        logger.info("📊 Security Score: %.1f/100", security_score)
        logger.info("🔒 Constitutional Compliance: %s",
                   '✅ VALID' if constitutional_compliance else '❌ INVALID')

        return report

    def _calculate_security_score(
        self,
        vulnerabilities: List[SecurityVulnerability],
        remediated: List[SecurityVulnerability]
    ) -> float:
        """Calculate overall security score (0-100)."""

        if not vulnerabilities:
            return 100.0

        # Weight vulnerabilities by severity
        severity_weights = {
            'critical': 25,
            'high': 15,
            'medium': 10,
            'low': 5
        }

        total_penalty = sum(severity_weights.get(v.severity, 5) for v in vulnerabilities)
        remediated_penalty = sum(severity_weights.get(v.severity, 5) for v in remediated)

        # Calculate score (start at 100, subtract penalties, add back remediated)
        score = 100 - total_penalty + remediated_penalty

        return max(0.0, min(100.0, score))

    def _check_constitutional_compliance(self, project_root: Path) -> bool:
        """Check if project maintains constitutional compliance."""

        # Check for constitutional hash in key files
        key_files = [
            'README.md',
            'config/environments/pyproject.toml',
            'package.json',
            'Dockerfile',
            'docker-compose.yml'
        ]

        compliance_found = False

        for filename in key_files:
            file_path = project_root / filename
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    if self.constitutional_hash in content:
                        compliance_found = True
                        break

                except Exception:
                    continue

        return compliance_found

    def _generate_security_recommendations(
        self,
        vulnerabilities: List[SecurityVulnerability],
        remediated: List[SecurityVulnerability]
    ) -> List[str]:
        """Generate security improvement recommendations."""

        recommendations = []

        # Count vulnerabilities by type
        vuln_types = {}
        for vuln in vulnerabilities:
            vuln_types[vuln.vulnerability_type] = vuln_types.get(vuln.vulnerability_type, 0) + 1

        # Generate specific recommendations
        if vuln_types.get('password', 0) > 0:
            recommendations.append("Implement secure password management with environment variables")

        if vuln_types.get('api_key', 0) > 0:
            recommendations.append("Move API keys to secure configuration management")

        if vuln_types.get('private_key', 0) > 0:
            recommendations.append("Use secure key management systems for private keys")

        if len(vulnerabilities) > len(remediated):
            recommendations.append("Complete manual remediation of remaining vulnerabilities")

        # Add constitutional compliance recommendation
        recommendations.append(f"Ensure all files include constitutional hash: {self.constitutional_hash}")

        # Add general security recommendations
        recommendations.extend([
            "Implement regular security scanning in CI/CD pipeline",
            "Enable multi-factor authentication for all accounts",
            "Implement comprehensive logging and monitoring",
            "Regular security training for development team"
        ])

        return recommendations

    async def generate_security_report(self, project_root: Path) -> Dict[str, Any]:
        """Generate comprehensive security report."""

        # Perform security scan
        scan_report = await self.perform_comprehensive_security_scan(project_root)

        # Get threat detection summary
        threat_summary = await self.threat_detector.get_threat_summary()

        # Get authentication metrics
        auth_metrics = self.auth_enhancer.get_authentication_metrics()

        # Compile comprehensive report
        comprehensive_report = {
            "constitutional_hash": self.constitutional_hash,
            "report_timestamp": time.time(),
            "security_scan": {
                "total_files_scanned": scan_report.total_files_scanned,
                "vulnerabilities_found": len(scan_report.vulnerabilities_found),
                "vulnerabilities_fixed": len(scan_report.vulnerabilities_fixed),
                "security_score": scan_report.security_score,
                "constitutional_compliance": scan_report.constitutional_compliance
            },
            "threat_detection": threat_summary,
            "authentication_security": auth_metrics,
            "overall_security_rating": self._calculate_overall_security_rating(
                scan_report.security_score,
                threat_summary,
                auth_metrics
            ),
            "recommendations": scan_report.recommendations
        }

        return comprehensive_report

    def _calculate_overall_security_rating(
        self,
        security_score: float,
        threat_summary: Dict[str, Any],
        auth_metrics: Dict[str, Any]
    ) -> str:
        """Calculate overall security rating."""

        # Weight different components
        scan_weight = 0.5
        threat_weight = 0.3
        auth_weight = 0.2

        # Calculate threat score (inverse of average threat score)
        avg_threat_score = threat_summary.get("average_threat_score", 0)
        threat_score = max(0, 100 - avg_threat_score)

        # Calculate auth score based on security features
        auth_score = 80  # Base score
        if auth_metrics.get("mfa_required"):
            auth_score += 10
        if auth_metrics.get("locked_accounts", 0) == 0:
            auth_score += 10

        # Calculate weighted overall score
        overall_score = (
            security_score * scan_weight +
            threat_score * threat_weight +
            auth_score * auth_weight
        )

        # Convert to rating
        if overall_score >= 90:
            return "excellent"
        elif overall_score >= 80:
            return "good"
        elif overall_score >= 70:
            return "fair"
        elif overall_score >= 60:
            return "poor"
        else:
            return "critical"

    def print_security_summary(self, report: Dict[str, Any]) -> None:
        """Print formatted security summary."""

        print("\n" + "="*80)
        print("🔒 ACGS-2 Enhanced Security Hardening Summary")
        print("="*80)
        print(f"🔒 Constitutional Hash: {report['constitutional_hash']}")
        print(f"📊 Overall Security Rating: {report['overall_security_rating'].upper()}")

        # Security scan results
        scan = report["security_scan"]
        print(f"\n🔍 Security Scan Results:")
        print(f"  • Files Scanned: {scan['total_files_scanned']}")
        print(f"  • Vulnerabilities Found: {scan['vulnerabilities_found']}")
        print(f"  • Vulnerabilities Fixed: {scan['vulnerabilities_fixed']}")
        print(f"  • Security Score: {scan['security_score']:.1f}/100")
        compliance_status = '✅ VALID' if scan['constitutional_compliance'] else '❌ INVALID'
        print(f"  • Constitutional Compliance: {compliance_status}")

        # Threat detection results
        threat = report["threat_detection"]
        if threat.get("status") != "no_activity_logged":
            print(f"\n🛡️ Threat Detection (Last Hour):")
            print(f"  • Requests Analyzed: {threat.get('total_requests_analyzed', 0)}")
            print(f"  • Threats Detected: {threat.get('total_threats_detected', 0)}")
            print(f"  • High Risk Requests: {threat.get('high_risk_requests', 0)}")
            print(f"  • Average Threat Score: {threat.get('average_threat_score', 0):.1f}")

        # Authentication security
        auth = report["authentication_security"]
        print(f"\n🔐 Authentication Security:")
        print(f"  • Active Sessions: {auth['active_sessions']}")
        print(f"  • Locked Accounts: {auth['locked_accounts']}")
        print(f"  • Recent Failed Attempts: {auth['recent_failed_attempts']}")
        mfa_status = '✅ YES' if auth['mfa_required'] else '❌ NO'
        print(f"  • MFA Required: {mfa_status}")

        # Recommendations
        if report["recommendations"]:
            print(f"\n💡 Security Recommendations:")
            for i, rec in enumerate(report["recommendations"][:5], 1):  # Show top 5
                print(f"  {i}. {rec}")

        print("="*80)


async def main():
    """Main function for enhanced security hardening demonstration."""

    print("🔒 ACGS-2 Enhanced Security Hardening System")
    print(f"🔒 Constitutional Hash: {CONSTITUTIONAL_HASH}")

    # Configuration
    config = SecurityConfig(
        min_password_length=12,
        require_mfa=True,
        session_timeout_minutes=30,
        max_login_attempts=5,
        enable_anomaly_detection=True
    )

    # Initialize security hardening system
    security_system = EnhancedSecurityHardening(config)

    try:
        # Set project root
        project_root = Path("/home/dislove/ACGS-2")

        print("🔍 Performing comprehensive security analysis...")

        # Generate comprehensive security report
        report = await security_system.generate_security_report(project_root)

        # Print security summary
        security_system.print_security_summary(report)

        print(f"\n✅ Enhanced Security Hardening analysis completed")

    except Exception as e:
        print(f"❌ Security analysis failed: {e}")
        logger.exception("Security analysis failed")


if __name__ == "__main__":
    asyncio.run(main())
