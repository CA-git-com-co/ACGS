# ACGS Dependency Management
**Constitutional Hash: cdd01ef066bc6cf2**


## Overview
All dependencies are now consolidated in `pyproject.toml` with clear dependency groups for different use cases.

## Installation Options

### Basic Runtime (Core Services Only)
```bash
pip install -e .
```

### Development Environment (Recommended)
```bash
pip install -e ".[ai,dev,test]"
```

### Complete Environment (All Features)
```bash
pip install -e ".[all]"
```

### Specific Feature Sets

#### AI Models and Machine Learning
```bash
pip install -e ".[ai]"
```

#### Testing and Quality Assurance
```bash
pip install -e ".[dev,test]"
```

#### Performance Testing
```bash
pip install -e ".[performance]"
```

#### Multi-Agent Coordination
```bash
pip install -e ".[coordination]"
```

#### Production Deployment
```bash
pip install -e ".[prod]"
```

## Dependency Groups

- **Core**: Essential runtime dependencies (automatically included)
- **ai**: AI/ML models (OpenAI, Anthropic, Groq, Transformers, etc.)
- **dev**: Development tools (linting, formatting, type checking)
- **test**: Testing framework and utilities
- **performance**: Load testing and performance monitoring
- **coordination**: Multi-agent messaging and coordination
- **vector**: Vector databases and search
- **ml**: Advanced ML features (optional)
- **blockchain**: Blockchain integration (optional)
- **docs**: Documentation generation
- **prod**: Production deployment tools

## Migration from requirements.txt

The old requirements.txt files have been consolidated. If you have existing installations:

```bash
# Remove old virtual environment
rm -rf .venv

# Create new environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install with desired features
pip install -e ".[ai,dev,test]"
```

## Constitutional Hash
All dependencies maintain compatibility with constitutional hash: `cdd01ef066bc6cf2`

## Implementation Status

- ✅ **Constitutional Hash Validation**: Active enforcement of `cdd01ef066bc6cf2`
- 🔄 **Performance Monitoring**: Continuous validation of targets
- ✅ **Documentation Standards**: Compliant with ACGS-2 requirements
- 🔄 **Cross-Reference Validation**: Ongoing link integrity maintenance

**Overall Status**: 🔄 IN PROGRESS - Systematic enhancement implementation

## Performance Targets

This component maintains the following performance requirements:

- **P99 Latency**: <5ms (constitutional requirement)
- **Throughput**: >100 RPS (minimum operational standard)
- **Cache Hit Rate**: >85% (efficiency requirement)
- **Constitutional Compliance**: 100% (hash: cdd01ef066bc6cf2)

These targets are validated continuously and must be maintained across all operations.
