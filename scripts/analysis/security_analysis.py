#!/usr/bin/env python3

"""
ACGS-2 Security Analysis with Constitutional AI Service Integration
Constitutional Hash: cdd01ef066bc6cf2
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple
import datetime
import ast

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# ACGS Constitutional AI Service port
CONSTITUTIONAL_AI_SERVICE_PORT = 8001

def analyze_constitutional_ai_integration() -> Dict[str, Any]:
    """Analyze integration with ACGS Constitutional AI Service (port 8001)."""
    integration_analysis = {
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "service_port": CONSTITUTIONAL_AI_SERVICE_PORT,
        "integration_points": [],
        "security_validations": 0,
        "constitutional_middleware": 0,
        "service_calls": []
    }
    
    # Search for Constitutional AI Service integration patterns
    integration_patterns = [
        rf'http://.*:{CONSTITUTIONAL_AI_SERVICE_PORT}',
        rf'localhost:{CONSTITUTIONAL_AI_SERVICE_PORT}',
        rf'constitutional.*ai.*service',
        rf'constitutional.*validation',
        rf'constitutional.*middleware'
    ]
    
    for py_file in Path('.').rglob('*.py'):
        if any(exclude in str(py_file) for exclude in ['.venv', '__pycache__', '.git']):
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Check for Constitutional AI Service integration
            for pattern in integration_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    integration_analysis["integration_points"].append({
                        "file": str(py_file),
                        "pattern": pattern,
                        "matches": len(matches)
                    })
                    
            # Count security validations
            if 'constitutional' in content.lower() and 'validation' in content.lower():
                integration_analysis["security_validations"] += 1
                
            # Count constitutional middleware
            if 'constitutional' in content.lower() and 'middleware' in content.lower():
                integration_analysis["constitutional_middleware"] += 1
                
        except Exception:
            continue
    
    return integration_analysis

def analyze_jwt_security() -> Dict[str, Any]:
    """Analyze JWT security implementations."""
    jwt_analysis = {
        "jwt_implementations": [],
        "token_validation": 0,
        "secret_management": 0,
        "constitutional_tokens": 0,
        "security_vulnerabilities": []
    }
    
    # JWT security patterns
    jwt_patterns = {
        "jwt_decode": r'jwt\.decode\(',
        "jwt_encode": r'jwt\.encode\(',
        "token_validation": r'verify.*token|validate.*token',
        "secret_management": r'JWT_SECRET|jwt.*secret',
        "constitutional_tokens": rf'{CONSTITUTIONAL_HASH}.*token|token.*{CONSTITUTIONAL_HASH}'
    }
    
    for py_file in Path('.').rglob('*.py'):
        if any(exclude in str(py_file) for exclude in ['.venv', '__pycache__', '.git']):
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Check for JWT patterns
            jwt_found = False
            for pattern_name, pattern in jwt_patterns.items():
                matches = len(re.findall(pattern, content, re.IGNORECASE))
                if matches > 0:
                    jwt_found = True
                    if pattern_name == "token_validation":
                        jwt_analysis["token_validation"] += matches
                    elif pattern_name == "secret_management":
                        jwt_analysis["secret_management"] += matches
                    elif pattern_name == "constitutional_tokens":
                        jwt_analysis["constitutional_tokens"] += matches
                        
            if jwt_found:
                jwt_analysis["jwt_implementations"].append({
                    "file": str(py_file),
                    "has_constitutional_hash": CONSTITUTIONAL_HASH in content
                })
                
            # Check for potential security vulnerabilities
            if 'jwt' in content.lower() and 'none' in content.lower():
                jwt_analysis["security_vulnerabilities"].append({
                    "file": str(py_file),
                    "issue": "Potential JWT 'none' algorithm vulnerability"
                })
                
        except Exception:
            continue
    
    return jwt_analysis

def analyze_authentication_security() -> Dict[str, Any]:
    """Analyze authentication and authorization security."""
    auth_analysis = {
        "auth_implementations": [],
        "password_security": 0,
        "session_management": 0,
        "role_based_access": 0,
        "constitutional_auth": 0,
        "security_issues": []
    }
    
    # Authentication patterns
    auth_patterns = {
        "password_hashing": r'bcrypt|scrypt|argon2|pbkdf2',
        "session_management": r'session|redis.*auth|auth.*session',
        "role_based_access": r'rbac|role.*based|permission|authorize',
        "constitutional_auth": rf'{CONSTITUTIONAL_HASH}.*auth|auth.*{CONSTITUTIONAL_HASH}'
    }
    
    for py_file in Path('.').rglob('*.py'):
        if any(exclude in str(py_file) for exclude in ['.venv', '__pycache__', '.git']):
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Check for authentication patterns
            auth_found = False
            for pattern_name, pattern in auth_patterns.items():
                matches = len(re.findall(pattern, content, re.IGNORECASE))
                if matches > 0:
                    auth_found = True
                    if pattern_name == "password_hashing":
                        auth_analysis["password_security"] += matches
                    elif pattern_name == "session_management":
                        auth_analysis["session_management"] += matches
                    elif pattern_name == "role_based_access":
                        auth_analysis["role_based_access"] += matches
                    elif pattern_name == "constitutional_auth":
                        auth_analysis["constitutional_auth"] += matches
                        
            if auth_found:
                auth_analysis["auth_implementations"].append({
                    "file": str(py_file),
                    "has_constitutional_hash": CONSTITUTIONAL_HASH in content
                })
                
            # Check for potential security issues
            if re.search(r'password.*=.*["\'][^"\']*["\']', content):
                auth_analysis["security_issues"].append({
                    "file": str(py_file),
                    "issue": "Potential hardcoded password"
                })
                
        except Exception:
            continue
    
    return auth_analysis

def analyze_encryption_security() -> Dict[str, Any]:
    """Analyze encryption and data protection."""
    encryption_analysis = {
        "encryption_implementations": [],
        "ssl_tls": 0,
        "data_encryption": 0,
        "key_management": 0,
        "constitutional_encryption": 0
    }
    
    # Encryption patterns
    encryption_patterns = {
        "ssl_tls": r'ssl|tls|https|certificate',
        "data_encryption": r'encrypt|decrypt|cipher|aes|rsa',
        "key_management": r'key.*management|vault|secrets',
        "constitutional_encryption": rf'{CONSTITUTIONAL_HASH}.*encrypt|encrypt.*{CONSTITUTIONAL_HASH}'
    }
    
    for py_file in Path('.').rglob('*.py'):
        if any(exclude in str(py_file) for exclude in ['.venv', '__pycache__', '.git']):
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Check for encryption patterns
            encryption_found = False
            for pattern_name, pattern in encryption_patterns.items():
                matches = len(re.findall(pattern, content, re.IGNORECASE))
                if matches > 0:
                    encryption_found = True
                    if pattern_name == "ssl_tls":
                        encryption_analysis["ssl_tls"] += matches
                    elif pattern_name == "data_encryption":
                        encryption_analysis["data_encryption"] += matches
                    elif pattern_name == "key_management":
                        encryption_analysis["key_management"] += matches
                    elif pattern_name == "constitutional_encryption":
                        encryption_analysis["constitutional_encryption"] += matches
                        
            if encryption_found:
                encryption_analysis["encryption_implementations"].append({
                    "file": str(py_file),
                    "has_constitutional_hash": CONSTITUTIONAL_HASH in content
                })
                
        except Exception:
            continue
    
    return encryption_analysis

def analyze_security_monitoring() -> Dict[str, Any]:
    """Analyze security monitoring and logging."""
    monitoring_analysis = {
        "security_logging": 0,
        "audit_trails": 0,
        "intrusion_detection": 0,
        "constitutional_monitoring": 0,
        "alert_configurations": []
    }
    
    # Security monitoring patterns
    monitoring_patterns = {
        "security_logging": r'security.*log|log.*security|audit.*log',
        "audit_trails": r'audit.*trail|security.*audit',
        "intrusion_detection": r'intrusion|anomaly.*detection|security.*alert',
        "constitutional_monitoring": rf'{CONSTITUTIONAL_HASH}.*monitor|monitor.*{CONSTITUTIONAL_HASH}'
    }
    
    for file_path in Path('.').rglob('*.py'):
        if any(exclude in str(file_path) for exclude in ['.venv', '__pycache__', '.git']):
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Check for monitoring patterns
            for pattern_name, pattern in monitoring_patterns.items():
                matches = len(re.findall(pattern, content, re.IGNORECASE))
                if matches > 0:
                    if pattern_name == "security_logging":
                        monitoring_analysis["security_logging"] += matches
                    elif pattern_name == "audit_trails":
                        monitoring_analysis["audit_trails"] += matches
                    elif pattern_name == "intrusion_detection":
                        monitoring_analysis["intrusion_detection"] += matches
                    elif pattern_name == "constitutional_monitoring":
                        monitoring_analysis["constitutional_monitoring"] += matches
                        
        except Exception:
            continue
    
    # Check for security alert configurations
    for config_file in Path('.').rglob('*alert*.yml'):
        try:
            with open(config_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            if 'security' in content.lower():
                monitoring_analysis["alert_configurations"].append({
                    "file": str(config_file),
                    "has_constitutional_hash": CONSTITUTIONAL_HASH in content
                })
                
        except Exception:
            continue
    
    return monitoring_analysis

def generate_security_recommendations(analysis_results: Dict[str, Any]) -> List[str]:
    """Generate security recommendations based on analysis."""
    recommendations = []
    
    # Constitutional AI Service integration
    const_ai = analysis_results["constitutional_ai_integration"]
    if len(const_ai["integration_points"]) < 5:
        recommendations.append("CRITICAL: Increase Constitutional AI Service (port 8001) integration points")
    
    # JWT security
    jwt = analysis_results["jwt_analysis"]
    if jwt["token_validation"] < 10:
        recommendations.append("HIGH: Implement more JWT token validation points")
    if jwt["constitutional_tokens"] < 5:
        recommendations.append("MEDIUM: Integrate constitutional hash into JWT tokens")
    
    # Authentication security
    auth = analysis_results["auth_analysis"]
    if auth["password_security"] < 5:
        recommendations.append("CRITICAL: Implement stronger password hashing (bcrypt/argon2)")
    if auth["role_based_access"] < 10:
        recommendations.append("HIGH: Implement more role-based access controls")
    
    # Encryption security
    encryption = analysis_results["encryption_analysis"]
    if encryption["data_encryption"] < 10:
        recommendations.append("HIGH: Implement more data encryption")
    if encryption["key_management"] < 3:
        recommendations.append("MEDIUM: Implement proper key management system")
    
    # Security monitoring
    monitoring = analysis_results["security_monitoring"]
    if monitoring["security_logging"] < 10:
        recommendations.append("HIGH: Implement comprehensive security logging")
    if monitoring["audit_trails"] < 5:
        recommendations.append("MEDIUM: Implement security audit trails")
    
    return recommendations

def main():
    """Main security analysis function."""
    print("Analyzing ACGS-2 Security with Constitutional AI Service Integration...")
    print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print(f"Constitutional AI Service Port: {CONSTITUTIONAL_AI_SERVICE_PORT}")
    print()
    
    # Run security analysis
    constitutional_ai_integration = analyze_constitutional_ai_integration()
    jwt_analysis = analyze_jwt_security()
    auth_analysis = analyze_authentication_security()
    encryption_analysis = analyze_encryption_security()
    monitoring_analysis = analyze_security_monitoring()
    
    # Combine results
    analysis_results = {
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "analysis_timestamp": datetime.datetime.now().isoformat(),
        "constitutional_ai_integration": constitutional_ai_integration,
        "jwt_analysis": jwt_analysis,
        "auth_analysis": auth_analysis,
        "encryption_analysis": encryption_analysis,
        "security_monitoring": monitoring_analysis
    }
    
    # Generate recommendations
    recommendations = generate_security_recommendations(analysis_results)
    analysis_results["recommendations"] = recommendations
    
    # Save results
    output_file = "security_analysis_results.json"
    with open(output_file, 'w') as f:
        json.dump(analysis_results, f, indent=2, default=str)
    
    print(f"Security analysis complete! Results saved to {output_file}")
    
    # Print summary
    print("\n" + "="*80)
    print("SECURITY ANALYSIS SUMMARY")
    print("="*80)
    print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print()
    
    # Constitutional AI Service integration
    print("CONSTITUTIONAL AI SERVICE INTEGRATION (Port 8001)")
    print("-" * 50)
    print(f"Integration Points: {len(constitutional_ai_integration['integration_points'])}")
    print(f"Security Validations: {constitutional_ai_integration['security_validations']}")
    print(f"Constitutional Middleware: {constitutional_ai_integration['constitutional_middleware']}")
    print()
    
    # JWT security
    print("JWT SECURITY")
    print("-" * 20)
    print(f"JWT Implementations: {len(jwt_analysis['jwt_implementations'])}")
    print(f"Token Validations: {jwt_analysis['token_validation']}")
    print(f"Secret Management: {jwt_analysis['secret_management']}")
    print(f"Constitutional Tokens: {jwt_analysis['constitutional_tokens']}")
    print(f"Security Vulnerabilities: {len(jwt_analysis['security_vulnerabilities'])}")
    print()
    
    # Authentication security
    print("AUTHENTICATION SECURITY")
    print("-" * 30)
    print(f"Auth Implementations: {len(auth_analysis['auth_implementations'])}")
    print(f"Password Security: {auth_analysis['password_security']}")
    print(f"Session Management: {auth_analysis['session_management']}")
    print(f"Role-Based Access: {auth_analysis['role_based_access']}")
    print(f"Constitutional Auth: {auth_analysis['constitutional_auth']}")
    print(f"Security Issues: {len(auth_analysis['security_issues'])}")
    print()
    
    # Encryption security
    print("ENCRYPTION SECURITY")
    print("-" * 25)
    print(f"Encryption Implementations: {len(encryption_analysis['encryption_implementations'])}")
    print(f"SSL/TLS: {encryption_analysis['ssl_tls']}")
    print(f"Data Encryption: {encryption_analysis['data_encryption']}")
    print(f"Key Management: {encryption_analysis['key_management']}")
    print(f"Constitutional Encryption: {encryption_analysis['constitutional_encryption']}")
    print()
    
    # Security monitoring
    print("SECURITY MONITORING")
    print("-" * 25)
    print(f"Security Logging: {monitoring_analysis['security_logging']}")
    print(f"Audit Trails: {monitoring_analysis['audit_trails']}")
    print(f"Intrusion Detection: {monitoring_analysis['intrusion_detection']}")
    print(f"Constitutional Monitoring: {monitoring_analysis['constitutional_monitoring']}")
    print(f"Alert Configurations: {len(monitoring_analysis['alert_configurations'])}")
    print()
    
    # Recommendations
    if recommendations:
        print("SECURITY RECOMMENDATIONS")
        print("-" * 30)
        for rec in recommendations:
            print(f"• {rec}")
    else:
        print("✅ Security posture is excellent!")
    
    print()
    
    return analysis_results

if __name__ == "__main__":
    main()