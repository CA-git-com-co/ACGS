<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

# ACGS-1 Monitoring Infrastructure Security Guide

## Overview

This comprehensive security guide provides detailed procedures for securing the ACGS-1 monitoring infrastructure in production environments, ensuring enterprise-grade security for constitutional governance monitoring systems.

## Table of Contents

1. [Security Architecture](#security-architecture)
2. [Authentication and Authorization](#authentication-authorization)
3. [Network Security](#network-security)
4. [Data Protection](#data-protection)
5. [Access Control](#access-control)
6. [Security Monitoring](#security-monitoring)
7. [Compliance and Auditing](#compliance-auditing)
8. [Incident Response](#incident-response)

## Security Architecture {#security-architecture}

### Security Principles

**Defense in Depth**:

- Multiple layers of security controls
- Network segmentation and isolation
- Application-level security measures
- Data encryption at rest and in transit

**Least Privilege Access**:

- Minimal required permissions for users and services
- Role-based access control (RBAC)
- Regular access reviews and audits
- Automated privilege escalation controls

**Zero Trust Model**:

- Verify every access request
- Continuous monitoring and validation
- Micro-segmentation of network traffic
- Identity-based security policies

### Security Components

**Network Security**:

- Firewall rules and network ACLs
- VPN access for remote administration
- Network intrusion detection systems
- Traffic encryption and monitoring

**Application Security**:

- Secure authentication mechanisms
- Input validation and sanitization
- Secure coding practices
- Regular security assessments

**Data Security**:

- Encryption at rest and in transit
- Secure key management
- Data classification and handling
- Backup encryption and integrity

## Authentication and Authorization {#authentication-authorization}

### Grafana Security Configuration

**Basic Authentication Setup**:

```ini
# /etc/grafana/grafana.ini
[security]
admin_user = acgs_admin
admin_password = ${GRAFANA_ADMIN_PASSWORD}
secret_key = ${GRAFANA_SECRET_KEY}
disable_gravatar = true
cookie_secure = true
cookie_samesite = strict
disable_brute_force_login_protection = false

[auth]
disable_login_form = false
disable_signout_menu = false
oauth_auto_login = false

[auth.anonymous]
enabled = false
org_name = ACGS
org_role = Viewer

[users]
allow_sign_up = false
allow_org_create = false
auto_assign_org = true
auto_assign_org_role = Viewer
default_theme = dark
```

**LDAP Integration** (Optional):

```ini
[auth.ldap]
enabled = true
config_file = /etc/grafana/ldap.toml
allow_sign_up = false

# /etc/grafana/ldap.toml
[[servers]]
host = "ldap.acgs.ai"
port = 636
use_ssl = true
start_tls = false
ssl_skip_verify = false
bind_dn = "cn=grafana,ou=services,dc=acgs,dc=ai"
bind_password = "${LDAP_BIND_PASSWORD}"
search_filter = "(uid=%s)"
search_base_dns = ["ou=users,dc=acgs,dc=ai"]

[servers.attributes]
name = "givenName"
surname = "sn"
username = "uid"
member_of = "memberOf"
email = "mail"

[[servers.group_mappings]]
group_dn = "cn=acgs-admins,ou=groups,dc=acgs,dc=ai"
org_role = "Admin"

[[servers.group_mappings]]
group_dn = "cn=acgs-operators,ou=groups,dc=acgs,dc=ai"
org_role = "Editor"
```

### Prometheus Security Configuration

**Basic Authentication**:

```yaml
# /etc/prometheus/prometheus.yml
global:
  external_labels:
    cluster: 'acgs-1-production'
    environment: 'production'

# Basic authentication
basic_auth_users:
  acgs_monitor: ${PROMETHEUS_PASSWORD_HASH}

# TLS configuration
tls_server_config:
  cert_file: /etc/prometheus/certs/prometheus.crt
  key_file: /etc/prometheus/certs/prometheus.key
  client_ca_file: /etc/prometheus/certs/ca.crt
  client_auth_type: RequireAndVerifyClientCert
```

**Web Configuration**:

```yaml
# /etc/prometheus/web.yml
tls_server_config:
  cert_file: /etc/prometheus/certs/prometheus.crt
  key_file: /etc/prometheus/certs/prometheus.key
  client_ca_file: /etc/prometheus/certs/ca.crt
  client_auth_type: RequireAndVerifyClientCert

basic_auth_users:
  acgs_monitor: ${PROMETHEUS_PASSWORD_HASH}
  acgs_readonly: ${READONLY_PASSWORD_HASH}
```

### Alertmanager Security Configuration

**Authentication and TLS**:

```yaml
# /etc/alertmanager/alertmanager.yml
global:
  smtp_smarthost: 'smtp.acgs.ai:587'
  smtp_from: 'acgs-alerts@acgs.ai'
  smtp_auth_username: '${SMTP_USERNAME}'
  smtp_auth_password: '${SMTP_PASSWORD}'
  smtp_require_tls: true

route:
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'acgs-alerts'

receivers:
  - name: 'acgs-alerts'
    email_configs:
      - to: 'ops@acgs.ai'
        subject: 'ACGS Alert: {{ .GroupLabels.alertname }}'
        body: |
          {{ range .Alerts }}
          Alert: {{ .Annotations.summary }}
          Description: {{ .Annotations.description }}
          {{ end }}
        headers:
          X-ACGS-Environment: '{{ .CommonLabels.environment }}'
```

## Network Security {#network-security}

### Firewall Configuration

**UFW Firewall Rules**:

```bash
#!/bin/bash
# Configure UFW firewall for ACGS monitoring

# Reset firewall
ufw --force reset

# Default policies
ufw default deny incoming
ufw default allow outgoing

# SSH access (restrict to specific IPs in production)
ufw allow from 10.0.0.0/8 to any port 22
ufw allow from 172.16.0.0/12 to any port 22
ufw allow from 192.168.0.0/16 to any port 22

# Monitoring services (internal network only)
ufw allow from 10.0.0.0/8 to any port 9090  # Prometheus
ufw allow from 10.0.0.0/8 to any port 3000  # Grafana
ufw allow from 10.0.0.0/8 to any port 9093  # Alertmanager
ufw allow from 10.0.0.0/8 to any port 9101  # HAProxy Exporter
ufw allow from 10.0.0.0/8 to any port 9100  # Node Exporter

# ACGS services (internal network only)
ufw allow from 10.0.0.0/8 to any port 8000:8006

# Enable firewall
ufw --force enable

# Show status
ufw status verbose
```

**iptables Rules** (Advanced):

```bash
#!/bin/bash
# Advanced iptables configuration

# Flush existing rules
iptables -F
iptables -X
iptables -t nat -F
iptables -t nat -X

# Default policies
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# Allow loopback
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT

# Allow established connections
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# SSH access (rate limited)
iptables -A INPUT -p tcp --dport 22 -m state --state NEW -m recent --set
iptables -A INPUT -p tcp --dport 22 -m state --state NEW -m recent --update --seconds 60 --hitcount 4 -j DROP
iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# Monitoring services (internal network only)
iptables -A INPUT -s 10.0.0.0/8 -p tcp --dport 9090 -j ACCEPT  # Prometheus
iptables -A INPUT -s 10.0.0.0/8 -p tcp --dport 3000 -j ACCEPT  # Grafana
iptables -A INPUT -s 10.0.0.0/8 -p tcp --dport 9093 -j ACCEPT  # Alertmanager

# Log dropped packets
iptables -A INPUT -j LOG --log-prefix "DROPPED: "
iptables -A INPUT -j DROP

# Save rules
iptables-save > /etc/iptables/rules.v4
```

### Network Segmentation

**Docker Network Configuration**:

```yaml
# docker-compose.monitoring.yml
version: '3.8'

networks:
  monitoring:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
    driver_opts:
      com.docker.network.bridge.enable_icc: 'false'
      com.docker.network.bridge.enable_ip_masquerade: 'true'

services:
  prometheus:
    networks:
      monitoring:
        ipv4_address: 172.20.0.10

  grafana:
    networks:
      monitoring:
        ipv4_address: 172.20.0.20

  alertmanager:
    networks:
      monitoring:
        ipv4_address: 172.20.0.30
```

## Data Protection {#data-protection}

### Encryption at Rest

**Prometheus Data Encryption**:

```bash
# Create encrypted volume for Prometheus data
cryptsetup luksFormat /dev/sdb1
cryptsetup luksOpen /dev/sdb1 prometheus_data
mkfs.ext4 /dev/mapper/prometheus_data
mount /dev/mapper/prometheus_data /var/lib/prometheus

# Add to /etc/fstab
echo "/dev/mapper/prometheus_data /var/lib/prometheus ext4 defaults 0 2" >> /etc/fstab

# Add to /etc/crypttab
echo "prometheus_data /dev/sdb1 none luks" >> /etc/crypttab
```

**Grafana Database Encryption**:

```ini
# /etc/grafana/grafana.ini
[database]
type = postgres
host = localhost:5432
name = grafana
user = grafana
password = ${GRAFANA_DB_PASSWORD}
ssl_mode = require
ca_cert_path = /etc/grafana/certs/ca.crt
client_cert_path = /etc/grafana/certs/client.crt
client_key_path = /etc/grafana/certs/client.key

[security]
encryption_provider = secretKey.v1
secret_key = ${GRAFANA_SECRET_KEY}
```

### Encryption in Transit

**TLS Certificate Generation**:

```bash
#!/bin/bash
# Generate TLS certificates for monitoring services

# Create CA
openssl genrsa -out ca.key 4096
openssl req -new -x509 -days 365 -key ca.key -out ca.crt \
    -subj "/C=US/ST=State/L=City/O=ACGS/CN=ACGS-CA"

# Generate server certificates
for service in prometheus grafana alertmanager; do
    # Generate private key
    openssl genrsa -out ${service}.key 2048

    # Generate certificate signing request
    openssl req -new -key ${service}.key -out ${service}.csr \
        -subj "/C=US/ST=State/L=City/O=ACGS/CN=${service}.acgs.ai"

    # Generate certificate
    openssl x509 -req -in ${service}.csr -CA ca.crt -CAkey ca.key \
        -CAcreateserial -out ${service}.crt -days 365 \
        -extensions v3_req -extfile <(
            echo '[v3_req]'
            echo 'keyUsage = keyEncipherment, dataEncipherment'
            echo 'extendedKeyUsage = serverAuth'
            echo "subjectAltName = DNS:${service}.acgs.ai,DNS:localhost,IP:127.0.0.1"
        )

    # Set permissions
    chmod 600 ${service}.key
    chmod 644 ${service}.crt
done
```

### Backup Security

**Encrypted Backup Script**:

```bash
#!/bin/bash
# Secure backup with encryption

BACKUP_DIR="/var/backups/acgs-monitoring/$(date +%Y%m%d_%H%M%S)"
ENCRYPTION_KEY="${BACKUP_ENCRYPTION_KEY}"

# Create backup
mkdir -p "$BACKUP_DIR"

# Backup Prometheus data
docker exec acgs_prometheus promtool tsdb snapshot /prometheus
cp -r /var/lib/docker/volumes/prometheus_data/_data/snapshots/latest "$BACKUP_DIR/prometheus"

# Backup Grafana data
docker exec acgs_grafana grafana-cli admin export-dashboard > "$BACKUP_DIR/grafana-dashboards.json"
cp -r /var/lib/docker/volumes/grafana_data/_data "$BACKUP_DIR/grafana"

# Backup configurations
cp -r /etc/prometheus "$BACKUP_DIR/"
cp -r /etc/alertmanager "$BACKUP_DIR/"
cp -r /etc/grafana "$BACKUP_DIR/"

# Create encrypted archive
tar -czf "$BACKUP_DIR.tar.gz" -C "$(dirname "$BACKUP_DIR")" "$(basename "$BACKUP_DIR")"
openssl enc -aes-256-cbc -salt -pbkdf2 -in "$BACKUP_DIR.tar.gz" -out "$BACKUP_DIR.tar.gz.enc" -k "$ENCRYPTION_KEY"

# Verify backup integrity
openssl enc -aes-256-cbc -d -pbkdf2 -in "$BACKUP_DIR.tar.gz.enc" -k "$ENCRYPTION_KEY" | tar -tzf - > /dev/null

# Clean up unencrypted files
rm -rf "$BACKUP_DIR" "$BACKUP_DIR.tar.gz"

# Set secure permissions
chmod 600 "$BACKUP_DIR.tar.gz.enc"
chown root:root "$BACKUP_DIR.tar.gz.enc"
```

## Access Control {#access-control}

### Role-Based Access Control

**Grafana RBAC Configuration**:

```json
{
  "roles": [
    {
      "name": "ACGS Administrator",
      "permissions": [
        "dashboards:read",
        "dashboards:write",
        "dashboards:delete",
        "users:read",
        "users:write",
        "orgs:read",
        "orgs:write"
      ]
    },
    {
      "name": "ACGS Operator",
      "permissions": ["dashboards:read", "dashboards:write", "alerts:read", "alerts:write"]
    },
    {
      "name": "ACGS Viewer",
      "permissions": ["dashboards:read", "alerts:read"]
    }
  ]
}
```

### Service Account Management

**Prometheus Service Account**:

```bash
# Create dedicated user for Prometheus
useradd -r -s /bin/false -d /var/lib/prometheus prometheus

# Set ownership
chown -R prometheus:prometheus /var/lib/prometheus
chown -R prometheus:prometheus /etc/prometheus

# Configure systemd service
cat > /etc/systemd/system/prometheus.service << EOF
[Unit]
Description=Prometheus
After=network.target

[Service]
User=prometheus
Group=prometheus
Type=simple
ExecStart=/usr/local/bin/prometheus \\
    --config.file=/etc/prometheus/prometheus.yml \\
    --storage.tsdb.path=/var/lib/prometheus/ \\
    --web.console.templates=/etc/prometheus/consoles \\
    --web.console.libraries=/etc/prometheus/console_libraries \\
    --web.listen-address=0.0.0.0:9090 \\
    --web.external-url=https://prometheus.acgs.ai \\
    --web.config.file=/etc/prometheus/web.yml

[Install]
WantedBy=multi-user.target
EOF
```

## Security Monitoring {#security-monitoring}

### Security Event Detection

**Failed Authentication Monitoring**:

```yaml
# Alert rule for failed authentication attempts
groups:
  - name: security_alerts
    rules:
      - alert: HighFailedLoginAttempts
        expr: increase(grafana_api_login_post_total{status="error"}[5m]) > 5
        for: 1m
        labels:
          severity: warning
          category: security
        annotations:
          summary: 'High number of failed login attempts'
          description: '{{ $value }} failed login attempts in the last 5 minutes'

      - alert: UnauthorizedPrometheusAccess
        expr: increase(prometheus_http_requests_total{code="401"}[5m]) > 3
        for: 1m
        labels:
          severity: warning
          category: security
        annotations:
          summary: 'Unauthorized Prometheus access attempts'
          description: '{{ $value }} unauthorized access attempts to Prometheus'
```

### Audit Logging

**Grafana Audit Configuration**:

```ini
# /etc/grafana/grafana.ini
[log]
mode = console file
level = info
format = json

[log.file]
log_rotate = true
max_lines = 1000000
max_size_shift = 28
daily_rotate = true
max_days = 7

[auditing]
enabled = true
log_dashboard_content = true
```

**System Audit with auditd**:

```bash
# Install auditd
apt-get install auditd audispd-plugins

# Configure audit rules
cat > /etc/audit/rules.d/acgs-monitoring.rules << EOF
# Monitor configuration file changes
-w /etc/prometheus/ -p wa -k prometheus_config
-w /etc/grafana/ -p wa -k grafana_config
-w /etc/alertmanager/ -p wa -k alertmanager_config

# Monitor service access
-w /usr/local/bin/prometheus -p x -k prometheus_exec
-w /usr/sbin/grafana-server -p x -k grafana_exec

# Monitor data directories
-w /var/lib/prometheus/ -p wa -k prometheus_data
-w /var/lib/grafana/ -p wa -k grafana_data
EOF

# Restart auditd
systemctl restart auditd
```

## Compliance and Auditing {#compliance-auditing}

### Compliance Requirements

**Data Retention Policies**:

- Monitoring data: 15 days minimum
- Audit logs: 90 days minimum
- Security events: 1 year minimum
- Configuration changes: 3 years minimum

**Access Control Requirements**:

- Multi-factor authentication for administrative access
- Regular access reviews (quarterly)
- Principle of least privilege
- Segregation of duties

### Audit Procedures

**Monthly Security Audit**:

```bash
#!/bin/bash
# Monthly security audit script

echo "ACGS-1 Monitoring Security Audit - $(date)"
echo "============================================"

# Check user accounts
echo "Active user accounts:"
cut -d: -f1 /etc/passwd | sort

# Check sudo access
echo "Users with sudo access:"
grep -Po '^sudo.+:\K.*$' /etc/group

# Check failed login attempts
echo "Failed login attempts (last 30 days):"
journalctl --since "30 days ago" | grep "Failed password" | wc -l

# Check certificate expiration
echo "Certificate expiration dates:"
for cert in /etc/acgs/certs/*.crt; do
    echo "$cert: $(openssl x509 -enddate -noout -in "$cert")"
done

# Check firewall status
echo "Firewall status:"
ufw status verbose

# Check running services
echo "Running monitoring services:"
docker-compose -f docker-compose.monitoring.yml ps
```

## Incident Response {#incident-response}

### Security Incident Response Plan

**Phase 1: Detection and Analysis**

1. Identify security event through monitoring alerts
2. Assess severity and potential impact
3. Document initial findings
4. Notify security team

**Phase 2: Containment**

1. Isolate affected systems
2. Preserve evidence
3. Implement temporary controls
4. Prevent further damage

**Phase 3: Eradication and Recovery**

1. Remove threat from environment
2. Patch vulnerabilities
3. Restore systems from clean backups
4. Implement additional controls

**Phase 4: Post-Incident Activities**

1. Document lessons learned
2. Update security procedures
3. Conduct post-incident review
4. Improve detection capabilities

### Emergency Response Procedures

**Security Breach Response**:

```bash
#!/bin/bash
# Emergency security response script

# Isolate affected systems
iptables -A INPUT -j DROP
iptables -A OUTPUT -j DROP

# Stop monitoring services
docker-compose -f docker-compose.monitoring.yml stop

# Preserve evidence
cp -r /var/log/acgs /tmp/incident-evidence-$(date +%Y%m%d_%H%M%S)

# Change all passwords
./scripts/emergency-password-rotation.sh

# Notify security team
curl -X POST https://api.security-system.com/incidents \
    -H "Content-Type: application/json" \
    -d '{"type": "security_breach", "severity": "high", "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}'
```

---

**Security Contacts**:

- **Security Team**: security@acgs.ai
- **Emergency Response**: +1-XXX-XXX-XXXX
- **Compliance Officer**: compliance@acgs.ai

**Additional Resources**:

- [Production Deployment Guide](PRODUCTION_DEPLOYMENT_GUIDE.md)
- [Operational Runbooks](OPERATIONAL_RUNBOOKS.md)
- [Training Guide](TRAINING_GUIDE.md)
