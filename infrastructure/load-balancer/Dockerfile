# Constitutional Hash: cdd01ef066bc6cf2
# HAProxy Load Balancer for ACGS-1 High Availability
# Enterprise-grade load balancing with health monitoring and failover

FROM haproxy:2.8-alpine

# Install additional tools for monitoring and management
RUN apk add --no-cache \
    curl \
    bash \
    openssl \
    ca-certificates \
    rsyslog \
    && rm -rf /var/cache/apk/*

# Create haproxy user and directories
RUN addgroup -g 1000 haproxy && \
    adduser -D -s /bin/bash -u 1000 -G haproxy haproxy

# Create necessary directories
RUN mkdir -p /var/run/haproxy \
    /etc/haproxy/errors \
    /etc/ssl/certs \
    /var/log/haproxy \
    && chown -R haproxy:haproxy /var/run/haproxy /var/log/haproxy

# Copy HAProxy configuration
COPY haproxy.cfg /usr/local/etc/haproxy/haproxy.cfg

# Copy custom error pages
COPY errors/ /etc/haproxy/errors/

# Copy SSL certificates (if available)
COPY ssl/ /etc/ssl/certs/

# Copy health check script
COPY scripts/health-check.sh /usr/local/bin/health-check.sh
RUN chmod +x /usr/local/bin/health-check.sh

# Copy monitoring scripts
COPY scripts/monitor.sh /usr/local/bin/monitor.sh
RUN chmod +x /usr/local/bin/monitor.sh

# Copy startup script
COPY scripts/start.sh /usr/local/bin/start.sh
RUN chmod +x /usr/local/bin/start.sh

# Set proper permissions
RUN chown -R haproxy:haproxy /usr/local/etc/haproxy/ /etc/haproxy/

# Expose ports
EXPOSE 80 443 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD /usr/local/bin/health-check.sh

# Switch to haproxy user
USER haproxy

# Start HAProxy with custom script
CMD ["/usr/local/bin/start.sh"]
