-- ACGS-1 Database Initialization Script
-- Creates necessary databases and users for containerized deployment

-- Create additional databases if needed
CREATE DATABASE IF NOT EXISTS acgs_test;
CREATE DATABASE IF NOT EXISTS acgs_dev;

-- Create extensions for enhanced functionality
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Performance optimization settings
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET effective_io_concurrency = 200;

-- Create indexes for common queries
-- These will be created by Alembic migrations, but we prepare the database

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON DATABASE acgs_db TO acgs_user;
GRANT ALL PRIVILEGES ON DATABASE acgs_test TO acgs_user;
GRANT ALL PRIVILEGES ON DATABASE acgs_dev TO acgs_user;

-- Create schema for constitutional governance
CREATE SCHEMA IF NOT EXISTS constitutional;
CREATE SCHEMA IF NOT EXISTS governance;
CREATE SCHEMA IF NOT EXISTS compliance;

-- Grant schema permissions
GRANT ALL ON SCHEMA constitutional TO acgs_user;
GRANT ALL ON SCHEMA governance TO acgs_user;
GRANT ALL ON SCHEMA compliance TO acgs_user;

-- Log successful initialization
INSERT INTO pg_stat_statements_info (dealloc) VALUES (0) ON CONFLICT DO NOTHING;
