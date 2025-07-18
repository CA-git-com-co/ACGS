# Constitutional Hash: cdd01ef066bc6cf2
#!/bin/bash
set -e

echo "🚀 Deploying to staging environment..."

# SSH to staging server and deploy
ssh -o StrictHostKeyChecking=no $STAGING_USER@$STAGING_HOST << 'EOF'
    cd /opt/acgs-2

    # Pull latest images
    docker-compose -f config/docker/docker-compose.staging.yml pull

    # Create backup of current deployment
    docker-compose -f config/docker/docker-compose.staging.yml ps -q > /tmp/acgs-backup-containers.txt

    # Deploy new version
    docker-compose -f config/docker/docker-compose.staging.yml up -d

    # Wait for services to be ready
    sleep 30

    echo "✅ Staging deployment completed"
EOF

echo "✅ Staging deployment script completed"
