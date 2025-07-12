-- ACGS Database Initialization Script
-- Constitutional hash: cdd01ef066bc6cf2

-- Create databases for different services
CREATE DATABASE IF NOT EXISTS acgs_db;
CREATE DATABASE IF NOT EXISTS agent_hitl;

-- Create user with proper permissions
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'acgs_user') THEN
      
      CREATE ROLE acgs_user LOGIN PASSWORD 'acgs_password';
   END IF;
END
$do$;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE acgs_db TO acgs_user;
GRANT ALL PRIVILEGES ON DATABASE agent_hitl TO acgs_user;

-- Connect to acgs_db and create basic schema
\c acgs_db;

-- Create basic tables for constitutional compliance
CREATE TABLE IF NOT EXISTS constitutional_compliance (
    id SERIAL PRIMARY KEY,
    hash VARCHAR(255) NOT NULL DEFAULT 'cdd01ef066bc6cf2',
    service_name VARCHAR(255) NOT NULL,
    compliance_score DECIMAL(3,2) DEFAULT 1.0,
    validation_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    validated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    constitutional_hash VARCHAR(255) NOT NULL DEFAULT 'cdd01ef066bc6cf2',
    compliance_status BOOLEAN DEFAULT true
);

-- Insert initial compliance record
INSERT INTO constitutional_compliance (service_name, compliance_score) 
VALUES ('acgs_system', 1.0) 
ON CONFLICT DO NOTHING;
