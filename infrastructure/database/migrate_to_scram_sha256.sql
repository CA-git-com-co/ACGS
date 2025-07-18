# Constitutional Hash: cdd01ef066bc6cf2
-- ACGS-1 Security Enhancement: MD5 to SCRAM-SHA-256 Migration Script
-- This script migrates PostgreSQL authentication from MD5 to SCRAM-SHA-256
-- Run this script as PostgreSQL superuser after updating configuration files

-- Enable SCRAM-SHA-256 authentication
ALTER SYSTEM SET password_encryption = 'scram-sha-256';
SELECT pg_reload_conf();

-- Reset passwords for all ACGS users to force SCRAM-SHA-256 hash generation
-- Note: Replace 'secure_password_here' with actual secure passwords

-- Main ACGS user
ALTER USER acgs_user PASSWORD 'secure_password_here';

-- PostgreSQL superuser (if needed)
-- ALTER USER postgres PASSWORD 'secure_postgres_password_here';

-- Service-specific users
ALTER USER auth_service PASSWORD 'secure_auth_service_password';
ALTER USER ac_service PASSWORD 'secure_ac_service_password';
ALTER USER integrity_service PASSWORD 'secure_integrity_service_password';
ALTER USER fv_service PASSWORD 'secure_fv_service_password';
ALTER USER gs_service PASSWORD 'secure_gs_service_password';
ALTER USER pgc_service PASSWORD 'secure_pgc_service_password';
ALTER USER ec_service PASSWORD 'secure_ec_service_password';

-- Read-only users
ALTER USER acgs_readonly PASSWORD 'secure_readonly_password';

-- Monitoring users
ALTER USER pgbouncer_monitor PASSWORD 'secure_monitor_password';
ALTER USER prometheus_user PASSWORD 'secure_prometheus_password';

-- Verify SCRAM-SHA-256 is being used
SELECT rolname, rolpassword 
FROM pg_authid 
WHERE rolname IN (
    'acgs_user', 'auth_service', 'ac_service', 'integrity_service',
    'fv_service', 'gs_service', 'pgc_service', 'ec_service',
    'acgs_readonly', 'pgbouncer_monitor', 'prometheus_user'
) 
AND rolpassword LIKE 'SCRAM-SHA-256%';

-- Update pg_hba.conf to use scram-sha-256 method
-- This should be done manually or via configuration management
-- Example entries:
-- host    acgs_db    acgs_user    0.0.0.0/0    scram-sha-256
-- host    all        all          127.0.0.1/32 scram-sha-256

COMMIT;
