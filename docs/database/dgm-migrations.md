# DGM Database Migrations

## Overview

The Darwin Gödel Machine (DGM) service uses a comprehensive database migration system built on Alembic with enhanced rollback capabilities and data integrity checks. This system ensures safe, reliable database schema evolution while maintaining constitutional compliance and operational safety.

## Migration Architecture

### Components

1. **Alembic Integration**: Standard Alembic migrations for schema versioning
2. **Custom Migration Runner**: Enhanced runner with backup and rollback capabilities
3. **Data Integrity Checks**: Comprehensive validation and verification
4. **Constitutional Compliance**: Built-in governance and compliance validation
5. **Safety Mechanisms**: Automatic backups and rollback procedures

### Migration Files

The DGM migration system consists of four core migration files:

#### 001_create_dgm_schema.py
- Creates the `dgm` schema and core tables
- Establishes enum types for status tracking
- Creates `dgm_archive`, `performance_metrics`, and `constitutional_compliance_logs` tables
- Includes data integrity constraints and constitutional compliance checks

#### 002_create_dgm_bandit_workspace_config.py
- Creates bandit algorithm state tracking tables
- Establishes improvement workspace management
- Creates system configuration storage
- Includes metric aggregation tables for performance optimization

#### 003_create_dgm_indexes.py
- Creates performance-optimized indexes
- Establishes database triggers for automatic timestamp updates
- Implements constitutional compliance validation triggers
- Includes GIN indexes for JSONB column optimization

#### 004_insert_dgm_default_data.py
- Inserts default system configurations
- Creates initial bandit algorithm states
- Establishes baseline metric aggregation windows
- Includes constitutional compliance defaults

## Usage

### Prerequisites

Before running migrations, ensure:

1. PostgreSQL 15+ is running and accessible
2. Database user has schema creation privileges
3. Alembic is installed and configured
4. All migration files are present
5. `DATABASE_URL` environment variable is set

### Running Migrations

#### Using the Migration Runner (Recommended)

```bash
# Set database URL
export DATABASE_URL="postgresql://user:password@localhost:5432/acgs_db"

# Run migrations with comprehensive checks
python scripts/dgm-migration-runner.py
```

#### Using Alembic Directly

```bash
# Navigate to project root
cd /path/to/acgs

# Run migrations
alembic -c migrations/alembic.ini upgrade head
```

### Rollback Procedures

#### Automatic Rollback

The migration runner automatically creates backups and can rollback on failure:

```python
from scripts.dgm_migration_runner import DGMMigrationRunner

runner = DGMMigrationRunner(database_url)
runner.initialize()

# Rollback to specific revision
rollback_result = runner.rollback_migration("002_create_dgm_bandit_workspace_config")

# Rollback to base (remove all DGM tables)
rollback_result = runner.rollback_migration("base")
```

#### Manual Rollback

```bash
# Rollback to specific revision
alembic -c migrations/alembic.ini downgrade 002_create_dgm_bandit_workspace_config

# Rollback all DGM migrations
alembic -c migrations/alembic.ini downgrade base
```

## Safety Features

### Automatic Backups

The migration runner automatically creates backups before applying migrations:

- Backup schema: `dgm_backups.dgm_backup_YYYYMMDD_HHMMSS`
- All existing DGM tables are backed up
- Backup metadata is tracked for recovery

### Data Integrity Checks

#### Constitutional Compliance Validation

```sql
-- Automatic validation trigger
CREATE TRIGGER trigger_validate_dgm_archive_compliance
BEFORE INSERT OR UPDATE ON dgm.dgm_archive
FOR EACH ROW
EXECUTE FUNCTION dgm.validate_constitutional_compliance();
```

#### Constraint Validation

- Compliance scores must be between 0.0 and 1.0
- Safety thresholds must be within valid ranges
- Constitutional hashes cannot be empty
- Required fields are enforced

### Rollback Safety

Each migration includes comprehensive `downgrade()` functions:

- Tables are dropped in reverse dependency order
- Enum types are cleaned up properly
- Schema is removed only when empty
- Backup data is preserved

## Monitoring and Verification

### Migration Verification

The system includes comprehensive verification:

```python
verification_result = runner.verify_migration()

# Checks include:
# - Schema existence
# - Table creation
# - Index creation
# - Data integrity
# - Constitutional compliance
# - Default data presence
```

### Health Checks

Post-migration health checks verify:

1. **Schema Structure**: All tables and indexes exist
2. **Data Integrity**: Constraints and triggers are active
3. **Constitutional Compliance**: Governance settings are correct
4. **Performance**: Indexes are optimized for expected queries
5. **Safety**: Rollback mechanisms are functional

## Troubleshooting

### Common Issues

#### Migration Timeout
```bash
# Increase timeout in migration runner
# Default: 300 seconds (5 minutes)
```

#### Permission Errors
```sql
-- Grant necessary permissions
GRANT CREATE ON DATABASE acgs_db TO dgm_user;
GRANT USAGE, CREATE ON SCHEMA public TO dgm_user;
```

#### Constraint Violations
```sql
-- Check existing data before migration
SELECT * FROM existing_table WHERE compliance_score > 1.0;
```

### Recovery Procedures

#### Failed Migration Recovery

1. **Check Migration Status**
   ```bash
   alembic -c migrations/alembic.ini current
   alembic -c migrations/alembic.ini history
   ```

2. **Restore from Backup**
   ```sql
   -- List available backups
   SELECT schema_name FROM information_schema.schemata 
   WHERE schema_name LIKE 'dgm_backups%';
   
   -- Restore specific table
   INSERT INTO dgm.table_name 
   SELECT * FROM dgm_backups.backup_name.table_name;
   ```

3. **Manual Cleanup**
   ```sql
   -- Remove partial migration artifacts
   DROP SCHEMA IF EXISTS dgm CASCADE;
   
   -- Clean Alembic version table
   DELETE FROM alembic_version WHERE version_num LIKE '00%_create_dgm%';
   ```

## Best Practices

### Development

1. **Test Migrations**: Always test on development database first
2. **Backup Production**: Create manual backups before production migrations
3. **Monitor Performance**: Check migration execution time and resource usage
4. **Validate Data**: Verify data integrity after migration completion

### Production Deployment

1. **Maintenance Window**: Schedule migrations during low-traffic periods
2. **Rollback Plan**: Have tested rollback procedures ready
3. **Monitoring**: Monitor application health during and after migration
4. **Communication**: Notify stakeholders of migration schedule

### Constitutional Compliance

1. **Hash Validation**: Ensure constitutional hash consistency
2. **Compliance Scoring**: Validate compliance score calculations
3. **Governance Integration**: Verify integration with AC Service
4. **Audit Trail**: Maintain complete audit trail of changes

## Integration with ACGS

### Service Dependencies

The DGM migration system integrates with:

- **Auth Service (8000)**: User authentication and authorization
- **AC Service (8001)**: Constitutional compliance validation
- **GS Service (8002)**: Governance synthesis integration
- **Monitoring Stack**: Prometheus metrics and Grafana dashboards

### Configuration Management

System configurations are managed through the database:

```sql
-- View current configurations
SELECT key, value, category FROM dgm.system_configurations 
ORDER BY category, key;

-- Update configuration
UPDATE dgm.system_configurations 
SET value = '0.9' 
WHERE key = 'safety_threshold';
```

### Performance Optimization

The migration system includes performance optimizations:

- **Concurrent Indexes**: Created without blocking operations
- **Partitioning Ready**: Tables designed for future partitioning
- **Query Optimization**: Indexes optimized for expected query patterns
- **Metric Aggregation**: Pre-computed aggregations for dashboard queries

## Future Enhancements

### Planned Features

1. **Automated Testing**: Integration with CI/CD pipeline
2. **Blue-Green Deployments**: Zero-downtime migration support
3. **Cross-Service Coordination**: Coordinated migrations across services
4. **Advanced Monitoring**: Real-time migration progress tracking
5. **Compliance Automation**: Automated constitutional compliance checks
