# Hunyuan Model Deployment Monitoring

## Deployment Timeline

### Expected Duration

- **Image pull**: 5-15 minutes (depending on connection)
- **Model download**: 10-30 minutes (model weights ~13-20GB)
- **Service startup**: 2-5 minutes
- **Total**: 15-50 minutes for first deployment

## Monitoring Commands

### Check Container Status

```bash
docker-compose -f docker-compose.hunyuan.yml ps
```

### View Real-time Logs

```bash
docker-compose -f docker-compose.hunyuan.yml logs -f hunyuan-a13b
```

### Health Check

```bash
curl http://localhost:8000/health
```

## Integration with ACGS-PGP

### Constitutional Compliance Check

```bash
# Verify constitutional hash in deployment
curl http://localhost:8000/health | jq '.constitutional_hash'

# Expected response: "cdd01ef066bc6cf2"
```

### Performance Monitoring

```bash
# Check response times (should be <2s for ACGS-PGP compliance)
time curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "hunyuan",
    "messages": [{"role": "user", "content": "Test constitutional compliance"}],
    "max_tokens": 100
  }'
```

### Load Testing Integration

```bash
# Run ACGS-PGP load tests against Hunyuan endpoint
cd /path/to/ACGS
python3 scripts/load_test_mlops.py \
  --endpoint http://localhost:8000 \
  --requests 100 \
  --workers 10 \
  --duration 30
```

## Troubleshooting

### Common Issues

1. **Slow download**: Check network bandwidth
2. **Memory issues**: Ensure sufficient RAM (>32GB recommended)
3. **Port conflicts**: Verify port 8000 is available

### Recovery Commands

```bash
# Restart services
docker-compose -f docker-compose.hunyuan.yml restart

# Clean restart
docker-compose -f docker-compose.hunyuan.yml down
docker-compose -f docker-compose.hunyuan.yml up -d

# Check resource usage
docker stats hunyuan-a13b
```
