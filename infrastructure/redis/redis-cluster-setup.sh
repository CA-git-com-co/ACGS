# Constitutional Hash: cdd01ef066bc6cf2
#!/bin/bash
# Redis Cluster Setup for ACGS-1 Advanced Caching
# High Availability Configuration with Sentinel

set -e

PROJECT_ROOT="/home/dislove/ACGS-1"
REDIS_DIR="$PROJECT_ROOT/infrastructure/redis"
LOG_DIR="$PROJECT_ROOT/logs/redis"
DATA_DIR="$PROJECT_ROOT/data/redis"

# Create necessary directories
mkdir -p "$LOG_DIR" "$DATA_DIR" "$REDIS_DIR/cluster"

echo "🚀 Setting up Redis Cluster for ACGS-1 Advanced Caching..."

# Redis Master Configuration
cat > "$REDIS_DIR/cluster/redis-master.conf" << 'EOF'
# Redis Master Configuration
include /home/dislove/ACGS-1/infrastructure/redis/redis-production.conf

port 6379
pidfile /var/run/redis/redis-master.pid
logfile /home/dislove/ACGS-1/logs/redis/redis-master.log
dir /home/dislove/ACGS-1/data/redis/master

# Replication
replica-serve-stale-data yes
replica-read-only yes
repl-diskless-sync no
repl-diskless-sync-delay 5
repl-ping-replica-period 10
repl-timeout 60
repl-disable-tcp-nodelay no
repl-backlog-size 1mb
repl-backlog-ttl 3600

# Security
masterauth acgs_redis_production_2024_secure_cache_key
requirepass acgs_redis_production_2024_secure_cache_key
EOF

# Redis Replica Configuration
cat > "$REDIS_DIR/cluster/redis-replica.conf" << 'EOF'
# Redis Replica Configuration
include /home/dislove/ACGS-1/infrastructure/redis/redis-production.conf

port 6380
pidfile /var/run/redis/redis-replica.pid
logfile /home/dislove/ACGS-1/logs/redis/redis-replica.log
dir /home/dislove/ACGS-1/data/redis/replica

# Replication
replicaof 127.0.0.1 6379
masterauth acgs_redis_production_2024_secure_cache_key
requirepass acgs_redis_production_2024_secure_cache_key
EOF

# Redis Sentinel Configuration
cat > "$REDIS_DIR/cluster/redis-sentinel.conf" << 'EOF'
# Redis Sentinel Configuration for ACGS-1
port 26379
pidfile /var/run/redis/redis-sentinel.pid
logfile /home/dislove/ACGS-1/logs/redis/redis-sentinel.log
dir /home/dislove/ACGS-1/data/redis/sentinel

# Monitor master
sentinel monitor acgs-master 127.0.0.1 6379 1
sentinel auth-pass acgs-master acgs_redis_production_2024_secure_cache_key
sentinel down-after-milliseconds acgs-master 5000
sentinel parallel-syncs acgs-master 1
sentinel failover-timeout acgs-master 10000

# Security
requirepass acgs_redis_production_2024_secure_cache_key
EOF

echo "✅ Redis cluster configuration files created"

# Create systemd service files for host-based deployment
cat > "$REDIS_DIR/cluster/redis-master.service" << 'EOF'
[Unit]
Description=Redis Master Server for ACGS-1
After=network.target

[Service]
Type=notify
ExecStart=/usr/bin/redis-server /home/dislove/ACGS-1/infrastructure/redis/cluster/redis-master.conf
ExecStop=/bin/kill -s QUIT $MAINPID
TimeoutStopSec=0
Restart=always
User=redis
Group=redis

[Install]
WantedBy=multi-user.target
EOF

cat > "$REDIS_DIR/cluster/redis-replica.service" << 'EOF'
[Unit]
Description=Redis Replica Server for ACGS-1
After=network.target redis-master.service

[Service]
Type=notify
ExecStart=/usr/bin/redis-server /home/dislove/ACGS-1/infrastructure/redis/cluster/redis-replica.conf
ExecStop=/bin/kill -s QUIT $MAINPID
TimeoutStopSec=0
Restart=always
User=redis
Group=redis

[Install]
WantedBy=multi-user.target
EOF

cat > "$REDIS_DIR/cluster/redis-sentinel.service" << 'EOF'
[Unit]
Description=Redis Sentinel for ACGS-1
After=network.target redis-master.service

[Service]
Type=notify
ExecStart=/usr/bin/redis-sentinel /home/dislove/ACGS-1/infrastructure/redis/cluster/redis-sentinel.conf
ExecStop=/bin/kill -s QUIT $MAINPID
TimeoutStopSec=0
Restart=always
User=redis
Group=redis

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Systemd service files created"

# Create deployment script
cat > "$REDIS_DIR/deploy-cluster.sh" << 'EOF'
#!/bin/bash
# Deploy Redis Cluster for ACGS-1

set -e

echo "🚀 Deploying Redis Cluster for ACGS-1..."

# Create redis user if not exists
if ! id "redis" &>/dev/null; then
    sudo useradd --system --home /var/lib/redis --shell /bin/false redis
fi

# Create directories with proper permissions
sudo mkdir -p /var/lib/redis /var/log/redis /var/run/redis
sudo chown redis:redis /var/lib/redis /var/log/redis /var/run/redis
sudo chmod 755 /var/lib/redis /var/log/redis /var/run/redis

# Copy service files
sudo cp /home/dislove/ACGS-1/infrastructure/redis/cluster/*.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start services
sudo systemctl enable redis-master redis-replica redis-sentinel
sudo systemctl start redis-master

# Wait for master to start
sleep 5

sudo systemctl start redis-replica redis-sentinel

echo "✅ Redis cluster deployed successfully"
echo "📊 Cluster status:"
redis-cli -p 6379 -a acgs_redis_production_2024_secure_cache_key info replication
EOF

chmod +x "$REDIS_DIR/deploy-cluster.sh"

echo "✅ Redis cluster setup completed"
echo "📁 Configuration files created in: $REDIS_DIR/cluster/"
echo "🚀 To deploy: cd $REDIS_DIR && ./deploy-cluster.sh"
