#!/bin/bash
set -e

ENVIRONMENT=staging
ROLLBACK_VERSION=${2:-previous}

echo "🔄 Rolling back $ENVIRONMENT environment to $ROLLBACK_VERSION..."

if [ "$ENVIRONMENT" = "staging" ]; then
    HOST=$STAGING_HOST
    USER=$STAGING_USER
else
    HOST=$PRODUCTION_HOST
    USER=$PRODUCTION_USER
fi

# SSH to server and rollback
ssh -o StrictHostKeyChecking=no $USER@$HOST << EOF
    cd /opt/acgs-2

    echo "Stopping current services..."
    docker-compose -f docker-compose.$ENVIRONMENT.yml down

    if [ "$ROLLBACK_VERSION" = "previous" ]; then
        echo "Rolling back to previous containers..."
        if [ -f /tmp/acgs-backup-containers.txt ]; then
            while read container_id; do
                docker start \$container_id
            done < /tmp/acgs-backup-containers.txt
        else
            echo "No backup containers found, deploying last known good version..."
            docker-compose -f docker-compose.$ENVIRONMENT.yml up -d
        fi
    else
        echo "Rolling back to version $ROLLBACK_VERSION..."
        # Update image tags to rollback version
        sed -i "s/:latest/:$ROLLBACK_VERSION/g" docker-compose.$ENVIRONMENT.yml
        docker-compose -f docker-compose.$ENVIRONMENT.yml up -d
    fi

    echo "✅ Rollback completed"
EOF

echo "✅ Rollback script completed"
