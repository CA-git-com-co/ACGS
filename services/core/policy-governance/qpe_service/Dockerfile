# Constitutional Hash: cdd01ef066bc6cf2
# Quantum Policy Evaluator (QPE) Service Dockerfile
# ACGS-1 Constitutional Governance Enhancement

FROM golang:1.21-alpine AS builder

# Install dependencies
RUN apk add --no-cache git protobuf-dev

# Set working directory
WORKDIR /app

# Copy go mod files
COPY go.mod go.sum ./

# Download dependencies
RUN go mod download

# Copy source code
COPY . .

# Generate protobuf files
RUN protoc --go_out=. --go-grpc_out=. proto/qpe.proto

# Build the application
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o qpe_service .

# Final stage
FROM alpine:latest

# Install ca-certificates for HTTPS calls
RUN apk --no-cache add ca-certificates

WORKDIR /root/

# Copy the binary from builder stage
COPY --from=builder /app/qpe_service .

# Expose ports
EXPOSE 8012 8013

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD grpc_health_probe -addr=:8012 || exit 1

# Run the service
CMD ["./qpe_service"]
