#!/bin/bash
# Start containerized environment: integration_test
# Constitutional Hash: cdd01ef066bc6cf2

cd data/testing/integration_test
docker-compose up -d

echo "Waiting for services to be ready..."
sleep 10

echo "Containerized environment integration_test is ready"
echo "Constitutional Hash: cdd01ef066bc6cf2"
