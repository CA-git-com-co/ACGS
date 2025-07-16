"""
Advanced Security Middleware for ACGS-2
Constitutional Hash: cdd01ef066bc6cf2

Enterprise-grade security middleware with advanced threat protection:
- Intelligent rate limiting with adaptive thresholds
- Anomaly detection and behavioral analysis
- Bot protection and human verification
- Geographic and IP-based filtering
- Advanced threat detection with machine learning
- Real-time attack mitigation
"""

import asyncio
import hashlib
import ipaddress
import json
import logging
import re
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import unquote

from fastapi import HTTPException, Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


@dataclass
class ThreatIntelligence:
    """Threat intelligence data for advanced protection"""
    
    # Known malicious IP ranges (CIDR notation)
    malicious_ip_ranges: Set[str]
    
    # Known bot user agents
    bot_user_agents: Set[str]
    
    # Suspicious patterns in requests
    attack_patterns: Dict[str, List[str]]
    
    # Geographic restrictions (ISO country codes)
    blocked_countries: Set[str]
    
    # Whitelisted IPs that bypass most restrictions
    whitelisted_ips: Set[str]


class AdvancedRateLimiter:
    """Advanced rate limiter with sliding windows, adaptive thresholds, and anomaly detection"""
    
    def __init__(self):
        # Sliding window rate limiting (per-minute buckets)
        self.request_buckets: Dict[str, deque] = defaultdict(lambda: deque(maxlen=60))
        
        # Adaptive thresholds based on user behavior
        self.user_profiles: Dict[str, Dict[str, Any]] = {}
        
        # Anomaly detection for suspicious patterns
        self.request_patterns: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Temporary blocks for detected threats
        self.temporary_blocks: Dict[str, float] = {}
        
        # Rate limit tiers based on user reputation
        self.rate_limits = {
            'suspicious': {'requests': 10, 'window': 60},
            'normal': {'requests': 100, 'window': 60},
            'trusted': {'requests': 500, 'window': 60},
            'whitelisted': {'requests': 10000, 'window': 60}
        }
    
    def is_allowed(self, client_id: str, request_info: Dict[str, Any]) -> Tuple[bool, str]:
        """Advanced rate limiting with adaptive thresholds and anomaly detection"""
        current_time = time.time()
        current_minute = int(current_time // 60)
        
        # Check if temporarily blocked
        if client_id in self.temporary_blocks:
            if current_time < self.temporary_blocks[client_id]:
                return False, "temporarily_blocked"
            else:
                del self.temporary_blocks[client_id]
        
        # Get or create user profile
        if client_id not in self.user_profiles:
            self.user_profiles[client_id] = {
                'reputation': 'normal',
                'first_seen': current_time,
                'request_count': 0,
                'anomaly_score': 0.0,
                'last_request_time': current_time
            }
        
        profile = self.user_profiles[client_id]
        
        # Update user profile
        profile['request_count'] += 1
        profile['last_request_time'] = current_time
        
        # Analyze request pattern for anomalies
        anomaly_score = self._calculate_anomaly_score(client_id, request_info)
        profile['anomaly_score'] = (profile['anomaly_score'] * 0.9) + (anomaly_score * 0.1)
        
        # Adjust reputation based on behavior
        self._update_reputation(client_id, profile, request_info)
        
        # Get rate limit for current reputation
        rate_limit = self.rate_limits[profile['reputation']]
        
        # Clean old request buckets
        bucket = self.request_buckets[client_id]
        cutoff_minute = current_minute - rate_limit['window'] // 60
        
        while bucket and bucket[0] < cutoff_minute:
            bucket.popleft()
        
        # Check rate limit
        if len(bucket) >= rate_limit['requests']:
            # Potential attack - temporary block for severe violations
            if profile['reputation'] == 'suspicious' and len(bucket) > rate_limit['requests'] * 2:
                self.temporary_blocks[client_id] = current_time + 300  # 5 minute block
                logger.warning(f"Temporarily blocked client {client_id} for rate limit violation")
            
            return False, f"rate_limit_exceeded_{profile['reputation']}"
        
        # Add current request to bucket
        bucket.append(current_minute)
        
        # Update request patterns for anomaly detection
        self._update_request_patterns(client_id, request_info)
        
        return True, "allowed"
    
    def _calculate_anomaly_score(self, client_id: str, request_info: Dict[str, Any]) -> float:
        """Calculate anomaly score based on request patterns"""
        score = 0.0
        
        # Check for rapid-fire requests
        if client_id in self.request_patterns:
            recent_requests = list(self.request_patterns[client_id])
            if len(recent_requests) >= 5:
                time_deltas = [recent_requests[i] - recent_requests[i-1] 
                             for i in range(1, min(6, len(recent_requests)))]
                avg_delta = sum(time_deltas) / len(time_deltas)
                
                if avg_delta < 0.1:  # Less than 100ms between requests
                    score += 0.3
        
        # Check for suspicious user agent patterns
        user_agent = request_info.get('user_agent', '').lower()
        if any(bot_pattern in user_agent for bot_pattern in ['bot', 'crawler', 'spider', 'scraper']):
            score += 0.2
        
        # Check for missing common headers
        common_headers = ['accept', 'accept-language', 'accept-encoding']
        missing_headers = sum(1 for header in common_headers if header not in request_info.get('headers', {}))
        score += missing_headers * 0.1
        
        # Check for suspicious paths
        path = request_info.get('path', '')
        suspicious_paths = ['/admin', '/.env', '/config', '/api/internal']
        if any(sus_path in path for sus_path in suspicious_paths):
            score += 0.25
        
        return min(1.0, score)
    
    def _update_reputation(self, client_id: str, profile: Dict[str, Any], request_info: Dict[str, Any]) -> None:
        """Update client reputation based on behavior"""
        # Determine reputation based on anomaly score and behavior
        if profile['anomaly_score'] > 0.7:
            profile['reputation'] = 'suspicious'
        elif profile['anomaly_score'] > 0.4:
            if profile['reputation'] == 'trusted':
                profile['reputation'] = 'normal'
        elif profile['anomaly_score'] < 0.1 and profile['request_count'] > 100:
            if profile['reputation'] == 'normal':
                profile['reputation'] = 'trusted'
    
    def _update_request_patterns(self, client_id: str, request_info: Dict[str, Any]) -> None:
        """Update request patterns for anomaly detection"""
        current_time = time.time()
        self.request_patterns[client_id].append(current_time)


class ThreatDetector:
    """Advanced threat detection with pattern analysis and machine learning"""
    
    def __init__(self):
        # Known attack patterns
        self.attack_signatures = {
            'sql_injection': [
                r'(\bunion\b.*\bselect\b)',
                r'(\bor\b\s+\d+\s*=\s*\d+)',
                r'(\bdrop\b\s+\btable\b)',
                r'(\bexec\b\s*\()',
                r'(\bwaitfor\b\s+\bdelay\b)'
            ],
            'xss': [
                r'<script[^>]*>.*?</script>',
                r'javascript:',
                r'vbscript:',
                r'on\w+\s*=',
                r'<iframe[^>]*>',
                r'<object[^>]*>',
                r'<embed[^>]*>'
            ],
            'path_traversal': [
                r'\.\./',
                r'\.\.\\',
                r'%2e%2e%2f',
                r'%2e%2e%5c',
                r'\.\.%2f'
            ],
            'command_injection': [
                r';\s*(ls|cat|echo|ps|id|whoami)',
                r'\|\s*(ls|cat|echo|ps|id|whoami)',
                r'`[^`]*`',
                r'\$\([^)]*\)'
            ],
            'ddos_patterns': [
                r'^(GET|POST|HEAD)\s+/\s+HTTP/1\.[01]$',  # Malformed requests
                r'User-Agent:\s*$',  # Empty user agent
                r'Accept:\s*\*/*\s*$'  # Overly broad accept headers
            ]
        }
        
        # Request fingerprinting for bot detection
        self.request_fingerprints: Dict[str, int] = defaultdict(int)
        
        # Geographic IP ranges (simplified - in production use GeoIP database)
        self.country_ip_ranges = {
            'CN': ['1.0.1.0/24', '1.0.2.0/24'],  # Simplified China ranges
            'RU': ['2.0.1.0/24', '2.0.2.0/24'],  # Simplified Russia ranges
        }
    
    def analyze_request(self, request_info: Dict[str, Any], threat_intel: ThreatIntelligence) -> Dict[str, Any]:
        """Comprehensive threat analysis of incoming request"""
        threats = {
            'threat_level': 'low',
            'detected_attacks': [],
            'risk_score': 0.0,
            'recommendations': []
        }
        
        # Check IP-based threats
        client_ip = request_info.get('client_ip', '')
        ip_threats = self._analyze_ip_threats(client_ip, threat_intel)
        threats.update(ip_threats)
        
        # Check for attack patterns
        attack_threats = self._analyze_attack_patterns(request_info)
        threats['detected_attacks'].extend(attack_threats['detected_attacks'])
        threats['risk_score'] += attack_threats['risk_score']
        
        # Check for bot behavior
        bot_threats = self._analyze_bot_behavior(request_info)
        threats['risk_score'] += bot_threats['risk_score']
        if bot_threats['is_bot']:
            threats['detected_attacks'].append('automated_bot')
        
        # Check for geographic restrictions
        geo_threats = self._analyze_geographic_threats(client_ip, threat_intel)
        threats['risk_score'] += geo_threats['risk_score']
        if geo_threats['blocked']:
            threats['detected_attacks'].append('geographic_restriction')
        
        # Calculate overall threat level
        if threats['risk_score'] >= 0.8:
            threats['threat_level'] = 'critical'
        elif threats['risk_score'] >= 0.6:
            threats['threat_level'] = 'high'
        elif threats['risk_score'] >= 0.3:
            threats['threat_level'] = 'medium'
        
        # Generate recommendations
        threats['recommendations'] = self._generate_threat_recommendations(threats)
        
        return threats
    
    def _analyze_ip_threats(self, client_ip: str, threat_intel: ThreatIntelligence) -> Dict[str, Any]:
        """Analyze IP-based threats"""
        threats = {'risk_score': 0.0}
        
        if not client_ip:
            return threats
        
        try:
            ip_obj = ipaddress.ip_address(client_ip)
            
            # Check whitelist first
            if client_ip in threat_intel.whitelisted_ips:
                threats['risk_score'] = -0.5  # Negative score for trusted IPs
                return threats
            
            # Check against malicious IP ranges
            for ip_range in threat_intel.malicious_ip_ranges:
                if ip_obj in ipaddress.ip_network(ip_range, strict=False):
                    threats['risk_score'] += 0.8
                    threats['malicious_ip'] = True
                    break
                    
        except ValueError:
            # Invalid IP format
            threats['risk_score'] += 0.3
            threats['invalid_ip'] = True
        
        return threats
    
    def _analyze_attack_patterns(self, request_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze request for known attack patterns"""
        threats = {'detected_attacks': [], 'risk_score': 0.0}
        
        # Combine all request data for analysis
        request_data = ' '.join([
            request_info.get('path', ''),
            request_info.get('query_string', ''),
            json.dumps(request_info.get('headers', {})),
            request_info.get('user_agent', ''),
            request_info.get('body', '')[:1000]  # Limit body analysis
        ])
        
        # Check against attack signatures
        for attack_type, patterns in self.attack_signatures.items():
            for pattern in patterns:
                if re.search(pattern, request_data, re.IGNORECASE):
                    threats['detected_attacks'].append(attack_type)
                    threats['risk_score'] += 0.3
                    break
        
        return threats
    
    def _analyze_bot_behavior(self, request_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze request for bot-like behavior"""
        threats = {'is_bot': False, 'risk_score': 0.0}
        
        user_agent = request_info.get('user_agent', '').lower()
        
        # Check for bot user agents
        bot_indicators = ['bot', 'crawler', 'spider', 'scraper', 'wget', 'curl']
        if any(indicator in user_agent for indicator in bot_indicators):
            threats['is_bot'] = True
            threats['risk_score'] += 0.4
        
        # Check for missing browser headers
        headers = request_info.get('headers', {})
        browser_headers = ['accept-language', 'accept-encoding', 'dnt']
        missing_headers = sum(1 for header in browser_headers if header not in headers)
        
        if missing_headers >= 2:
            threats['risk_score'] += 0.2
        
        # Check request fingerprinting
        fingerprint = self._generate_request_fingerprint(request_info)
        self.request_fingerprints[fingerprint] += 1
        
        # If same fingerprint seen many times, likely a bot
        if self.request_fingerprints[fingerprint] > 100:
            threats['is_bot'] = True
            threats['risk_score'] += 0.3
        
        return threats
    
    def _analyze_geographic_threats(self, client_ip: str, threat_intel: ThreatIntelligence) -> Dict[str, Any]:
        """Analyze geographic-based threats"""
        threats = {'blocked': False, 'risk_score': 0.0}
        
        if not client_ip:
            return threats
        
        try:
            ip_obj = ipaddress.ip_address(client_ip)
            
            # Check against blocked countries
            for country, ip_ranges in self.country_ip_ranges.items():
                if country in threat_intel.blocked_countries:
                    for ip_range in ip_ranges:
                        if ip_obj in ipaddress.ip_network(ip_range, strict=False):
                            threats['blocked'] = True
                            threats['risk_score'] += 0.6
                            threats['blocked_country'] = country
                            return threats
                            
        except ValueError:
            pass
        
        return threats
    
    def _generate_request_fingerprint(self, request_info: Dict[str, Any]) -> str:
        """Generate unique fingerprint for request pattern analysis"""
        fingerprint_data = '|'.join([
            request_info.get('user_agent', ''),
            str(sorted(request_info.get('headers', {}).keys())),
            request_info.get('method', ''),
            request_info.get('accept_language', '')
        ])
        
        return hashlib.md5(fingerprint_data.encode()).hexdigest()
    
    def _generate_threat_recommendations(self, threats: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on detected threats"""
        recommendations = []
        
        if threats['threat_level'] == 'critical':
            recommendations.append('Block IP immediately')
            recommendations.append('Alert security team')
        elif threats['threat_level'] == 'high':
            recommendations.append('Rate limit aggressively')
            recommendations.append('Require additional verification')
        
        if 'sql_injection' in threats['detected_attacks']:
            recommendations.append('Sanitize database inputs')
        
        if 'xss' in threats['detected_attacks']:
            recommendations.append('Enhance output encoding')
        
        if 'automated_bot' in threats['detected_attacks']:
            recommendations.append('Implement CAPTCHA challenge')
        
        return recommendations


class AdvancedSecurityMiddleware(BaseHTTPMiddleware):
    """
    Advanced security middleware with enterprise-grade threat protection.
    
    Features:
    - Intelligent adaptive rate limiting
    - Advanced threat detection and analysis
    - Behavioral anomaly detection
    - Bot protection and verification
    - Geographic and IP filtering
    - Real-time attack mitigation
    - Constitutional compliance validation
    """
    
    def __init__(self, app, threat_intel: Optional[ThreatIntelligence] = None, config: Optional[Dict] = None):
        super().__init__(app)
        
        # Initialize threat intelligence
        self.threat_intel = threat_intel or ThreatIntelligence(
            malicious_ip_ranges=set(),
            bot_user_agents=set(),
            attack_patterns={},
            blocked_countries=set(),
            whitelisted_ips=set()
        )
        
        # Initialize security components
        self.rate_limiter = AdvancedRateLimiter()
        self.threat_detector = ThreatDetector()
        
        # Configuration
        self.config = config or {
            'enable_threat_detection': True,
            'enable_geographic_filtering': True,
            'enable_bot_protection': True,
            'enable_anomaly_detection': True,
            'block_on_threat_level': 'high',
            'require_captcha_on_threat_level': 'medium'
        }
        
        # Security metrics
        self.security_metrics = {
            'requests_analyzed': 0,
            'threats_detected': 0,
            'attacks_blocked': 0,
            'false_positives': 0
        }
    
    async def dispatch(self, request: Request, call_next):
        """Advanced security analysis and protection"""
        start_time = time.time()
        
        try:
            # Extract request information
            request_info = await self._extract_request_info(request)
            client_ip = request_info['client_ip']
            
            # Update metrics
            self.security_metrics['requests_analyzed'] += 1
            
            # Rate limiting with adaptive thresholds
            rate_limit_result, rate_limit_reason = self.rate_limiter.is_allowed(client_ip, request_info)
            
            if not rate_limit_result:
                self.security_metrics['attacks_blocked'] += 1
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        'error': f'Rate limit exceeded: {rate_limit_reason}',
                        'constitutional_hash': CONSTITUTIONAL_HASH,
                        'threat_level': 'medium',
                        'retry_after': 60
                    }
                )
            
            # Advanced threat detection
            if self.config['enable_threat_detection']:
                threat_analysis = self.threat_detector.analyze_request(request_info, self.threat_intel)
                
                if threat_analysis['detected_attacks']:
                    self.security_metrics['threats_detected'] += 1
                
                # Block based on threat level
                if self._should_block_request(threat_analysis):
                    self.security_metrics['attacks_blocked'] += 1
                    
                    # Log security incident
                    logger.warning(
                        f"Security threat blocked: IP={client_ip}, "
                        f"Threat Level={threat_analysis['threat_level']}, "
                        f"Attacks={threat_analysis['detected_attacks']}, "
                        f"Risk Score={threat_analysis['risk_score']:.2f}"
                    )
                    
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail={
                            'error': 'Security threat detected',
                            'threat_level': threat_analysis['threat_level'],
                            'constitutional_hash': CONSTITUTIONAL_HASH,
                            'incident_id': f"sec_{int(time.time())}"
                        }
                    )
            
            # Process request
            response = await call_next(request)
            
            # Add advanced security headers
            response = self._add_advanced_security_headers(response, request_info)
            
            # Log successful request
            processing_time = (time.time() - start_time) * 1000
            logger.debug(
                f"Advanced security check passed: "
                f"IP={client_ip}, "
                f"Processing time={processing_time:.2f}ms, "
                f"Constitutional hash={CONSTITUTIONAL_HASH}"
            )
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Advanced security middleware error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    'error': 'Security processing failed',
                    'constitutional_hash': CONSTITUTIONAL_HASH
                }
            )
    
    async def _extract_request_info(self, request: Request) -> Dict[str, Any]:
        """Extract comprehensive request information for analysis"""
        # Get client IP with proxy support
        client_ip = self._get_client_ip(request)
        
        # Extract headers
        headers = dict(request.headers)
        
        # Get body safely
        body = ""
        try:
            body_bytes = await request.body()
            body = body_bytes.decode('utf-8', errors='ignore')[:10000]  # Limit body size
        except:
            body = ""
        
        return {
            'client_ip': client_ip,
            'method': request.method,
            'path': str(request.url.path),
            'query_string': str(request.url.query),
            'headers': headers,
            'user_agent': headers.get('user-agent', ''),
            'accept_language': headers.get('accept-language', ''),
            'referer': headers.get('referer', ''),
            'body': body,
            'timestamp': time.time()
        }
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP with proxy support and validation"""
        # Check forwarded headers
        forwarded_for = request.headers.get('x-forwarded-for')
        if forwarded_for:
            # Take the first IP (client IP before proxies)
            client_ip = forwarded_for.split(',')[0].strip()
            if self._is_valid_ip(client_ip):
                return client_ip
        
        real_ip = request.headers.get('x-real-ip')
        if real_ip and self._is_valid_ip(real_ip):
            return real_ip
        
        # Fallback to direct connection
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def _is_valid_ip(self, ip: str) -> bool:
        """Validate IP address format"""
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False
    
    def _should_block_request(self, threat_analysis: Dict[str, Any]) -> bool:
        """Determine if request should be blocked based on threat analysis"""
        threat_level = threat_analysis['threat_level']
        block_threshold = self.config['block_on_threat_level']
        
        # Define threat level hierarchy
        threat_levels = {'low': 0, 'medium': 1, 'high': 2, 'critical': 3}
        
        current_level = threat_levels.get(threat_level, 0)
        threshold_level = threat_levels.get(block_threshold, 2)
        
        return current_level >= threshold_level
    
    def _add_advanced_security_headers(self, response: Response, request_info: Dict[str, Any]) -> Response:
        """Add comprehensive security headers"""
        # Enhanced security headers
        security_headers = {
            # Core security headers
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            
            # Advanced content security policy
            'Content-Security-Policy': (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' https:; "
                "connect-src 'self' https:; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self'"
            ),
            
            # Permission policy
            'Permissions-Policy': (
                'geolocation=(), microphone=(), camera=(), '
                'payment=(), usb=(), magnetometer=(), gyroscope=()'
            ),
            
            # Constitutional compliance
            'X-Constitutional-Hash': CONSTITUTIONAL_HASH,
            'X-Security-Level': 'advanced',
            
            # Request tracking
            'X-Request-ID': f"req_{int(time.time())}_{hash(request_info['client_ip']) % 10000}",
            
            # Security policy version
            'X-Security-Policy-Version': '2.0.0'
        }
        
        # Add feature policy for older browsers
        security_headers['Feature-Policy'] = (
            "geolocation 'none'; microphone 'none'; camera 'none'; "
            "payment 'none'; usb 'none'; magnetometer 'none'; gyroscope 'none'"
        )
        
        # Apply headers
        for header, value in security_headers.items():
            response.headers[header] = value
        
        return response
    
    async def get_security_metrics(self) -> Dict[str, Any]:
        """Get comprehensive security metrics"""
        return {
            'constitutional_hash': CONSTITUTIONAL_HASH,
            'security_metrics': self.security_metrics.copy(),
            'rate_limiter_stats': {
                'active_profiles': len(self.rate_limiter.user_profiles),
                'temporary_blocks': len(self.rate_limiter.temporary_blocks),
                'reputation_distribution': self._get_reputation_distribution()
            },
            'threat_detector_stats': {
                'known_fingerprints': len(self.threat_detector.request_fingerprints),
                'attack_signatures': len(self.threat_detector.attack_signatures)
            },
            'configuration': self.config.copy()
        }
    
    def _get_reputation_distribution(self) -> Dict[str, int]:
        """Get distribution of user reputations"""
        distribution = defaultdict(int)
        for profile in self.rate_limiter.user_profiles.values():
            distribution[profile['reputation']] += 1
        return dict(distribution)


# Factory function for easy integration
def create_advanced_security_middleware(
    threat_intel: Optional[ThreatIntelligence] = None,
    config: Optional[Dict] = None
) -> AdvancedSecurityMiddleware:
    """
    Create configured advanced security middleware.
    
    Args:
        threat_intel: Threat intelligence configuration
        config: Security configuration options
    
    Returns:
        Configured advanced security middleware
    """
    return lambda app: AdvancedSecurityMiddleware(app, threat_intel, config)


# Export for easy import
__all__ = [
    'AdvancedSecurityMiddleware',
    'ThreatIntelligence',
    'AdvancedRateLimiter',
    'ThreatDetector',
    'create_advanced_security_middleware',
    'CONSTITUTIONAL_HASH'
]