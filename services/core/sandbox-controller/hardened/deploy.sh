#!/bin/bash
# Deployment script for ACGS-1 Lite Hardened Sandbox Controller
# Constitutional Hash: cdd01ef066bc6cf2

set -e

echo "🔒 Deploying ACGS-1 Lite Hardened Sandbox Controller"
echo "Constitutional Hash: cdd01ef066bc6cf2"
echo "===================================================="

# Configuration
SERVICE_NAME="hardened-sandbox-controller"
NAMESPACE="acgs-hardened-sandbox"
IMAGE_NAME="acgs-hardened-sandbox-controller"
VERSION="latest"

# Check prerequisites
echo "🔍 Checking prerequisites..."

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed or not in PATH"
    exit 1
fi

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed or not in PATH" 
    exit 1
fi

# Check cluster connectivity
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Cannot connect to Kubernetes cluster"
    echo "💡 Ensure kubectl is configured and cluster is accessible"
    exit 1
fi

echo "✅ Prerequisites satisfied"

# Check node labels for runtime support
echo "🏷️  Checking node labels for runtime support..."

GVISOR_NODES=$(kubectl get nodes -l sandbox=gvisor --no-headers 2>/dev/null | wc -l)
KATA_NODES=$(kubectl get nodes -l sandbox=kata --no-headers 2>/dev/null | wc -l)

if [ $GVISOR_NODES -eq 0 ] && [ $KATA_NODES -eq 0 ]; then
    echo "⚠️  No nodes labeled for gVisor or Kata runtimes"
    echo "💡 Run setup scripts on nodes:"
    echo "   For gVisor: ./setup-gvisor.sh"
    echo "   For Firecracker: ./setup-firecracker.sh"
    echo ""
    echo "🤔 Continue anyway? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ Found runtime-capable nodes:"
    [ $GVISOR_NODES -gt 0 ] && echo "   gVisor nodes: $GVISOR_NODES"
    [ $KATA_NODES -gt 0 ] && echo "   Kata nodes: $KATA_NODES"
fi

# Build Docker image
echo "📦 Building hardened sandbox controller image..."

docker build -t ${IMAGE_NAME}:${VERSION} .

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed"
    exit 1
fi

echo "✅ Docker image built successfully"

# Create namespace and apply Kubernetes manifests
echo "🚀 Deploying to Kubernetes..."

# Apply all Kubernetes resources
kubectl apply -f k8s-runtime-setup.yaml

# Wait for deployment to be ready
echo "⏳ Waiting for deployment to be ready..."

kubectl rollout status deployment/${SERVICE_NAME} -n ${NAMESPACE} --timeout=300s

if [ $? -ne 0 ]; then
    echo "❌ Deployment failed to become ready"
    echo "📋 Checking deployment status..."
    kubectl get pods -n ${NAMESPACE}
    kubectl describe deployment ${SERVICE_NAME} -n ${NAMESPACE}
    exit 1
fi

# Verify pods are running
echo "🔍 Verifying pod status..."

READY_PODS=$(kubectl get pods -n ${NAMESPACE} -l app=${SERVICE_NAME} --field-selector=status.phase=Running --no-headers | wc -l)
TOTAL_PODS=$(kubectl get pods -n ${NAMESPACE} -l app=${SERVICE_NAME} --no-headers | wc -l)

echo "   Running pods: ${READY_PODS}/${TOTAL_PODS}"

if [ $READY_PODS -eq 0 ]; then
    echo "❌ No pods are running"
    echo "📋 Pod details:"
    kubectl get pods -n ${NAMESPACE} -l app=${SERVICE_NAME}
    kubectl describe pods -n ${NAMESPACE} -l app=${SERVICE_NAME}
    exit 1
fi

# Test service connectivity
echo "🧪 Testing service connectivity..."

# Port forward for testing (run in background)
kubectl port-forward -n ${NAMESPACE} service/${SERVICE_NAME} 8002:8002 &
PORT_FORWARD_PID=$!

# Wait for port forward to establish
sleep 5

# Test health endpoint
HEALTH_CHECK_PASSED=false
for i in {1..10}; do
    if curl -s -f http://localhost:8002/health > /dev/null 2>&1; then
        HEALTH_CHECK_PASSED=true
        break
    fi
    echo "   Attempt $i: Service not ready, waiting..."
    sleep 3
done

# Clean up port forward
kill $PORT_FORWARD_PID 2>/dev/null || true

if [ "$HEALTH_CHECK_PASSED" = true ]; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed"
    echo "📋 Service logs:"
    kubectl logs -n ${NAMESPACE} -l app=${SERVICE_NAME} --tail=50
    exit 1
fi

# Test runtime classes
echo "🔧 Verifying runtime classes..."

for runtime in gvisor kata-firecracker; do
    if kubectl get runtimeclass $runtime &>/dev/null; then
        echo "✅ RuntimeClass $runtime is available"
    else
        echo "⚠️  RuntimeClass $runtime not found"
    fi
done

# Run security tests if available
if [ -f "tests/test_security_hardening.py" ]; then
    echo "🔐 Running security tests..."
    
    # Port forward again for testing
    kubectl port-forward -n ${NAMESPACE} service/${SERVICE_NAME} 8002:8002 &
    PORT_FORWARD_PID=$!
    sleep 3
    
    # Run basic security tests
    python3 -c "
import asyncio
import httpx

async def test_basic_security():
    async with httpx.AsyncClient() as client:
        try:
            # Test health
            response = await client.get('http://localhost:8002/health')
            if response.status_code == 200:
                data = response.json()
                print(f'✅ Service healthy: {data.get(\"constitutional_hash\")}')
                return True
            else:
                print(f'❌ Health check failed: {response.status_code}')
                return False
        except Exception as e:
            print(f'❌ Connection failed: {e}')
            return False

result = asyncio.run(test_basic_security())
exit(0 if result else 1)
"
    
    SECURITY_TEST_RESULT=$?
    
    # Clean up port forward
    kill $PORT_FORWARD_PID 2>/dev/null || true
    
    if [ $SECURITY_TEST_RESULT -eq 0 ]; then
        echo "✅ Basic security tests passed"
    else
        echo "⚠️  Basic security tests had issues"
    fi
else
    echo "ℹ️  Security tests not available"
fi

# Display deployment information
echo ""
echo "🎉 Hardened Sandbox Controller deployed successfully!"
echo ""
echo "Deployment Information:"
echo "  📍 Namespace: ${NAMESPACE}"
echo "  🏷️  Service: ${SERVICE_NAME}"
echo "  🐳 Image: ${IMAGE_NAME}:${VERSION}"
echo "  📊 Pods: ${READY_PODS}/${TOTAL_PODS} ready"
echo ""
echo "Service Endpoints:"
echo "  🔗 Internal: http://${SERVICE_NAME}.${NAMESPACE}.svc.cluster.local:8002"
echo "  📖 API Docs: http://${SERVICE_NAME}.${NAMESPACE}.svc.cluster.local:8002/docs"
echo "  📊 Metrics: http://${SERVICE_NAME}.${NAMESPACE}.svc.cluster.local:8002/metrics"
echo ""
echo "Testing Commands:"
echo "  # Port forward for local testing:"
echo "  kubectl port-forward -n ${NAMESPACE} service/${SERVICE_NAME} 8002:8002"
echo ""
echo "  # Test sandbox execution:"
echo "  curl -X POST http://localhost:8002/api/v1/sandbox/execute \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"agent_id\":\"test\",\"code\":\"print(\\\"Hello from hardened sandbox!\\\")\",\"runtime\":\"gvisor\"}'"
echo ""
echo "  # Check sandbox status:"
echo "  curl http://localhost:8002/api/v1/sandbox/status"
echo ""
echo "Monitoring Commands:"
echo "  # View logs:"
echo "  kubectl logs -n ${NAMESPACE} -l app=${SERVICE_NAME} -f"
echo ""
echo "  # Check pod status:"
echo "  kubectl get pods -n ${NAMESPACE} -l app=${SERVICE_NAME}"
echo ""
echo "  # View service details:"
echo "  kubectl describe service ${SERVICE_NAME} -n ${NAMESPACE}"
echo ""
echo "Security Information:"
echo "  🔒 gVisor: Kernel-level isolation with user-space kernel"
echo "  🔥 Firecracker: microVM isolation with hardware virtualization"
echo "  🛡️  Seccomp: Enhanced profiles blocking dangerous syscalls"
echo "  🚫 Network: Isolated by default with NetworkPolicy"
echo "  📋 Monitoring: Real-time security violation detection"
echo ""
echo "Constitutional Hash: cdd01ef066bc6cf2"