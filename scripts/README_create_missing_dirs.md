# ACGS Volume Mount Directory Creator

## Overview

The `create_missing_dirs.py` script is part of Step 3 in the ACGS volume mount triage process. It automatically creates missing host directories identified in the catalogue from Step 1 (`volume_mount_triage.yaml`).

## Constitutional Compliance

This script operates under constitutional hash: `cdd01ef066bc6cf2`

All created `.keep` files contain this constitutional hash to ensure compliance with ACGS governance principles.

## Features

- Reads the catalogue from `volume_mount_triage.yaml` (Step 1 output)
- Creates missing host directories using `mkdir -p` equivalent functionality
- Drops a `.keep` file in each created directory containing the constitutional hash
- Supports dry-run mode for safe preview of operations
- Comprehensive error handling and logging
- Full command-line interface with configurable options

## Usage

### Basic Usage
```bash
python scripts/create_missing_dirs.py
```

### With Custom Catalogue File
```bash
python scripts/create_missing_dirs.py --catalogue /path/to/volume_mount_triage.yaml
```

### Dry Run Mode (Recommended First)
```bash
python scripts/create_missing_dirs.py --dry-run
```

### Custom Base Path
```bash
python scripts/create_missing_dirs.py --base-path /custom/base/path
```

### Complete Example
```bash
python scripts/create_missing_dirs.py \
    --catalogue volume_mount_triage.yaml \
    --base-path . \
    --dry-run
```

## Command Line Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--catalogue` | `-c` | Path to the volume mount catalogue file | `volume_mount_triage.yaml` |
| `--base-path` | `-b` | Base directory path | `.` (current directory) |
| `--dry-run` | `-d` | Dry run mode - only show what would be created | `false` |
| `--help` | `-h` | Show help message and exit | - |

## Input Format

The script expects a YAML file with the following structure:

```yaml
broken_volume_mounts_by_compose_file:
  compose-file-1.yml:
    missing_host_directory:
      - container_path: /app/config
        full_mount: config:/app/config:ro
        host_path: config
        mount_options: ro
        recommended_action: 'Create directory: config'
      - container_path: /app/data
        full_mount: data:/app/data
        host_path: data
        mount_options: ''
        recommended_action: 'Create directory: data'
```

## Output

### Dry Run Mode
```
[DRY RUN] Would create directory: ./config
[DRY RUN] Would create .keep file: ./config/.keep
[DRY RUN] Would create directory: ./data
[DRY RUN] Would create .keep file: ./data/.keep

[DRY RUN] Would create 2 directories
```

### Normal Mode
```
Created directory: ./config
Created .keep file: ./config/.keep
Created directory: ./data
Created .keep file: ./data/.keep

Successfully created 2 directories
Constitutional hash used: cdd01ef066bc6cf2
```

## Error Handling

The script handles various error conditions:

- **File Not Found**: Missing catalogue file
- **Invalid YAML**: Malformed catalogue file
- **Permission Errors**: Insufficient permissions to create directories
- **Missing Data**: Invalid or incomplete catalogue entries

## Safety Features

1. **Dry Run Mode**: Always test with `--dry-run` first
2. **Existing Directory Handling**: Uses `mkdir -p` equivalent (won't fail if directory exists)
3. **Constitutional Compliance**: All operations include constitutional hash validation
4. **Comprehensive Logging**: Detailed output for all operations

## Testing

Run the unit tests to verify functionality:

```bash
python -m pytest tests/scripts/test_create_missing_dirs.py -v
```

## Constitutional Governance

This script is designed to operate within the ACGS constitutional framework:

- All created directories include constitutional compliance markers
- Operations are auditable through comprehensive logging
- Constitutional hash `cdd01ef066bc6cf2` is embedded in all `.keep` files
- Follows ACGS operational principles for infrastructure management

## Dependencies

- Python 3.6+
- PyYAML
- pathlib (standard library)
- argparse (standard library)

## Integration

This script is part of the larger ACGS volume mount triage process:

1. **Step 1**: Generate catalogue with volume mount analysis
2. **Step 2**: Review and validate catalogue entries
3. **Step 3**: **This script** - Create missing directories
4. **Step 4**: Validate and test volume mounts

## Example Workflow

```bash
# 1. Preview what would be created
python scripts/create_missing_dirs.py --dry-run

# 2. Review the output and verify correctness

# 3. Create the directories
python scripts/create_missing_dirs.py

# 4. Verify creation
find . -name ".keep" -exec grep -l "cdd01ef066bc6cf2" {} \;
```

## Troubleshooting

### Common Issues

1. **Permission Denied**: Ensure write permissions to target directories
2. **File Not Found**: Verify catalogue file path and existence
3. **Invalid YAML**: Validate catalogue file format

### Debug Mode

Add debug prints by modifying the script or use Python's built-in debugging:

```bash
python -v scripts/create_missing_dirs.py --dry-run
```

## Contributing

When modifying this script:

1. Maintain constitutional compliance (hash: `cdd01ef066bc6cf2`)
2. Update unit tests in `tests/scripts/test_create_missing_dirs.py`
3. Ensure all tests pass before committing
4. Follow ACGS coding standards and documentation practices

---

**Constitutional Hash**: `cdd01ef066bc6cf2`  
**ACGS Compliance**: Full  
**Last Updated**: Step 3 Implementation
