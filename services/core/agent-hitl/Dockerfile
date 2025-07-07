# Agent HITL Service Dockerfile
# Constitutional hash: cdd01ef066bc6cf2

FROM python:3.11-slim

WORKDIR /app

# Install basic health check tools
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Create health endpoint
RUN echo '#!/bin/bash\necho "{\"status\":\"healthy\",\"constitutional_hash\":\"cdd01ef066bc6cf2\"}"' > /app/health_check.sh && chmod +x /app/health_check.sh

# Basic Python server for health checks
RUN echo 'from http.server import HTTPServer, BaseHTTPRequestHandler\nimport json\n\nclass HealthHandler(BaseHTTPRequestHandler):\n    def do_GET(self):\n        if self.path == "/health":\n            self.send_response(200)\n            self.send_header("Content-type", "application/json")\n            self.end_headers()\n            response = {"status": "healthy", "constitutional_hash": "cdd01ef066bc6cf2"}\n            self.wfile.write(json.dumps(response).encode())\n        else:\n            self.send_response(404)\n            self.end_headers()\n\nif __name__ == "__main__":\n    server = HTTPServer(("0.0.0.0", 8008), HealthHandler)\n    print("Agent HITL service starting on port 8008")\n    server.serve_forever()' > /app/main.py

EXPOSE 8008

CMD ["python", "/app/main.py"]
