# Constitutional Hash: cdd01ef066bc6cf2
# ACGS-2 Constitutional Compliance Validation
#!/bin/bash
# PostgreSQL Research Papers Knowledge Base Setup Script

set -e

# Configuration
DB_NAME="acgs_research_kb"
DB_USER="acgs_user"
DB_PASSWORD=os.environ.get("PASSWORD")
DB_HOST="localhost"
DB_PORT="5432"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}ACGS Research Papers Knowledge Base Setup${NC}"
echo "========================================"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2

# Function to check if PostgreSQL is running
check_postgresql() {
    if ! systemctl is-active --quiet postgresql; then
        echo -e "${YELLOW}PostgreSQL is not running. Starting...${NC}"
        sudo systemctl start postgresql
    fi
    echo -e "${GREEN}✓ PostgreSQL is running${NC}"
}

# Function to create database and user
setup_database() {
    echo -e "${YELLOW}Setting up database and user...${NC}"
    
    # Switch to postgres user and create database/user
    sudo -u postgres psql -c "CREATE DATABASE ${DB_NAME};" 2>/dev/null || echo "Database ${DB_NAME} already exists"
    sudo -u postgres psql -c "CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASSWORD}';" 2>/dev/null || echo "User ${DB_USER} already exists"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};"
    sudo -u postgres psql -c "ALTER USER ${DB_USER} CREATEDB;"
    
    # Grant schema permissions
    sudo -u postgres psql -d "${DB_NAME}" -c "GRANT ALL ON SCHEMA public TO ${DB_USER};"
    sudo -u postgres psql -d "${DB_NAME}" -c "GRANT CREATE ON SCHEMA public TO ${DB_USER};"
    sudo -u postgres psql -d "${DB_NAME}" -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ${DB_USER};"
    sudo -u postgres psql -d "${DB_NAME}" -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO ${DB_USER};"
    
    echo -e "${GREEN}✓ Database and user created${NC}"
}

# Function to create schema
create_schema() {
    echo -e "${YELLOW}Creating database schema...${NC}"
    
    PGPASSWORD="${DB_PASSWORD}" psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" -f "$(dirname "$0")/schema/research_papers_schema.sql"
    
    echo -e "${GREEN}✓ Schema created successfully${NC}"
}

# Function to insert initial data
insert_initial_data() {
    echo -e "${YELLOW}Inserting initial categories and keywords...${NC}"
    
    PGPASSWORD="${DB_PASSWORD}" psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" -f "$(dirname "$0")/data/initial_data.sql"
    
    echo -e "${GREEN}✓ Initial data inserted${NC}"
}

# Function to create environment file
create_env_file() {
    cat > "$(dirname "$0")/config/environments/development.env" << EOF
# Database Configuration
DB_HOST=${DB_HOST}
DB_PORT=${DB_PORT}
DB_NAME=${DB_NAME}
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}

# Database URL for applications
DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}
EOF
    
    chmod 600 "$(dirname "$0")/config/environments/development.env"
    echo -e "${GREEN}✓ Environment file created${NC}"
}

# Function to test connection
test_connection() {
    echo -e "${YELLOW}Testing database connection...${NC}"
    
    PGPASSWORD="${DB_PASSWORD}" psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" -c "SELECT COUNT(*) FROM papers;" > /dev/null
    
    echo -e "${GREEN}✓ Database connection successful${NC}"
}

# Main execution
main() {
    echo "Starting setup process..."
    
    check_postgresql
    setup_database
    create_schema
    insert_initial_data
    create_env_file
    test_connection
    
    echo ""
    echo -e "${GREEN}🎉 Database setup completed successfully!${NC}"
    echo ""
    echo "Database Details:"
    echo "  Host: ${DB_HOST}"
    echo "  Port: ${DB_PORT}"
    echo "  Database: ${DB_NAME}"
    echo "  User: ${DB_USER}"
    echo ""
    echo "Next steps:"
    echo "1. Run the paper import script: ./tools/import_papers.py"
    echo "2. Start the knowledge base API: python database/api/kb_api.py"
    echo "3. Use the CLI tool: python database/cli/kb_cli.py"
}

# Check if running as script
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
