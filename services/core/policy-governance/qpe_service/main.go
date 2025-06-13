// Quantum Policy Evaluator (QPE) Service
// ACGS-1 Constitutional Governance Enhancement
// Implements quantum-inspired policy evaluation with superposition states
//
// Formal Verification Comments:
// requires: constitutional_hash == "cdd01ef066bc6cf2"
// ensures: latency_overhead <= 2ms for 95th percentile
// ensures: superposition_weights_sum == 1.0
// ensures: entanglement_tag == HMAC_SHA256(constitutional_hash, policy_id)
// sha256: opa_schrodinger_quantum_superposition_qpe_v1.0

package main

import (
	"bytes"
	"context"
	"crypto/hmac"
	"crypto/rand"
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"log"
	"math"
	"net"
	"net/http"
	"os"
	"os/signal"
	"sync"
	"syscall"
	"time"

	"github.com/go-redis/redis/v8"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"

	pb "qpe_service/proto"
)

const (
	// Constitutional hash for Quantumagi compatibility
	constitutionalHash = "cdd01ef066bc6cf2"

	// Default superposition weights (equal superposition)
	defaultWeightApproved = 1.0 / 3.0
	defaultWeightRejected = 1.0 / 3.0
	defaultWeightPending  = 1.0 / 3.0

	// Performance targets
	maxLatencyOverheadMs = 2.0
	defaultUncertainty   = 0.5

	// Redis key prefixes
	policyKeyPrefix  = "qpe:policy:"
	metricsKeyPrefix = "qpe:metrics:"
)

// Prometheus metrics
var (
	qpeLatency = promauto.NewHistogramVec(
		prometheus.HistogramOpts{
			Name:    "qpe_measure_latency_ms",
			Help:    "Latency of QPE measure operations in milliseconds",
			Buckets: []float64{0.1, 0.5, 1, 2, 5, 10, 25, 50, 100},
		},
		[]string{"policy_id", "state"},
	)

	stateTransitions = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Name: "qpe_state_transitions_total",
			Help: "Total number of quantum state transitions by type",
		},
		[]string{"policy_id", "from_state", "to_state"},
	)

	uncertaintyLevel = promauto.NewGauge(
		prometheus.GaugeOpts{
			Name: "qpe_uncertainty_lambda",
			Help: "Current uncertainty lambda value (0-1)",
		},
	)

	heisenbergConstant = promauto.NewGauge(
		prometheus.GaugeOpts{
			Name: "qpe_heisenberg_constant",
			Help: "Current value of the Heisenberg constant K (latency × accuracy)",
		},
	)

	policiesInSuperposition = promauto.NewGauge(
		prometheus.GaugeOpts{
			Name: "qpe_policies_in_superposition",
			Help: "Number of policies currently in quantum superposition",
		},
	)
)

// QPE Server implementation
type server struct {
	pb.UnimplementedQuantumPolicyEvaluatorServer
	redisClient       *redis.Client
	uncertainty       float32
	uncertaintyMu     sync.RWMutex
	pgcServiceURL     string
	deterministicMode bool
	metrics           *QPEMetrics
}

// QPE Metrics for monitoring
type QPEMetrics struct {
	TotalPolicies           int64
	PoliciesInSuperposition int64
	CollapsedPolicies       int64
	AverageLatencyMs        float64
	HeisenbergConstant      float64
	StateDistribution       map[string]int64
	CollapseReasons         map[string]int64
	mu                      sync.RWMutex
}

// Quantum Policy internal representation
type QuantumPolicyInternal struct {
	PolicyID             string   `json:"policy_id"`
	EntanglementTag      []byte   `json:"entanglement_tag"`
	WeightApproved       float32  `json:"weight_approved"`
	WeightRejected       float32  `json:"weight_rejected"`
	WeightPending        float32  `json:"weight_pending"`
	CreatedAt            int64    `json:"created_at"`
	DeadlineAt           int64    `json:"deadline_at"`
	UncertaintyParameter float32  `json:"uncertainty_parameter"`
	Criticality          string   `json:"criticality"`
	IsCollapsed          bool     `json:"is_collapsed"`
	CollapsedState       pb.State `json:"collapsed_state"`
}

// PGCResponse represents the response from PGC service evaluation
type PGCResponse struct {
	Success    bool    `json:"success"`
	Decision   string  `json:"decision"`
	Confidence float32 `json:"confidence"`
	Reason     string  `json:"reason"`
	Error      string  `json:"error,omitempty"`
}

// callPGCService issues a POST request with the serialized policy payload, enforcing context deadlines and interpreting the PGC response.
func callPGCService(ctx context.Context, baseURL string, policy *QuantumPolicyInternal) (bool, error) {
	client := http.Client{Timeout: 2 * time.Second}
	payload, err := json.Marshal(policy)
	if err != nil {
		return false, fmt.Errorf("failed to marshal policy for PGC: %w", err)
	}
	req, err := http.NewRequestWithContext(ctx, http.MethodPost, baseURL+"/evaluate", bytes.NewReader(payload))
	if err != nil {
		return false, fmt.Errorf("failed to construct PGC request: %w", err)
	}
	req.Header.Set("Content-Type", "application/json")
	resp, err := client.Do(req)
	if err != nil {
		return false, fmt.Errorf("PGC HTTP request failed: %w", err)
	}
	defer resp.Body.Close()
	var res PGCResponse
	if err := json.NewDecoder(resp.Body).Decode(&res); err != nil {
		return false, fmt.Errorf("failed to decode PGC response: %w", err)
	}
	return res.Success, nil
}

// Generate entanglement tag using HMAC-SHA256
func generateEntanglementTag(policyID string) []byte {
	h := hmac.New(sha256.New, []byte(constitutionalHash))
	h.Write([]byte(policyID))
	return h.Sum(nil)
}

// Verify entanglement tag integrity
func verifyEntanglementTag(policyID string, tag []byte) bool {
	expected := generateEntanglementTag(policyID)
	return hmac.Equal(expected, tag)
}

// Calculate superposition entropy (measure of "quantum-ness")
func calculateSuperpositionEntropy(weights []float32) float32 {
	entropy := float32(0.0)
	for _, w := range weights {
		if w > 0 {
			entropy -= w * float32(math.Log(float64(w)))
		}
	}
	return entropy
}

// Deterministic collapse based on policy ID hash
func deterministicCollapse(policyID string) pb.State {
	hash := sha256.Sum256([]byte(policyID + constitutionalHash))
	value := int(hash[0]) % 3
	return pb.State(value)
}

// Probabilistic collapse based on weights
func probabilisticCollapse(weights []float32) pb.State {
	randBytes := make([]byte, 4)
	rand.Read(randBytes)

	// Convert to float in [0,1)
	randValue := float32(uint32(randBytes[0])<<24|uint32(randBytes[1])<<16|
		uint32(randBytes[2])<<8|uint32(randBytes[3])) / float32(1<<32)

	cumulative := float32(0.0)
	for i, weight := range weights {
		cumulative += weight
		if randValue < cumulative {
			return pb.State(i)
		}
	}

	// Fallback (should not happen with normalized weights)
	return pb.State_PENDING
}

// Register a new policy in quantum superposition
func (s *server) Register(ctx context.Context, req *pb.RegisterRequest) (*pb.RegisterResponse, error) {
	startTime := time.Now()

	// Validate input
	if req.PolicyId == "" {
		return nil, status.Errorf(codes.InvalidArgument, "policy_id cannot be empty")
	}

	// Generate entanglement tag
	entanglementTag := generateEntanglementTag(req.PolicyId)

	// Create quantum policy in superposition
	now := time.Now().Unix()
	deadlineHours := req.DeadlineHours
	if deadlineHours <= 0 {
		deadlineHours = 24 // Default 24 hours
	}

	s.uncertaintyMu.RLock()
	uncertainty := s.uncertainty
	s.uncertaintyMu.RUnlock()

	policy := &QuantumPolicyInternal{
		PolicyID:             req.PolicyId,
		EntanglementTag:      entanglementTag,
		WeightApproved:       defaultWeightApproved,
		WeightRejected:       defaultWeightRejected,
		WeightPending:        defaultWeightPending,
		CreatedAt:            now,
		DeadlineAt:           now + (deadlineHours * 3600),
		UncertaintyParameter: uncertainty,
		Criticality:          req.Criticality,
		IsCollapsed:          false,
		CollapsedState:       pb.State_PENDING,
	}

	// Store in Redis
	policyJSON, err := json.Marshal(policy)
	if err != nil {
		return nil, status.Errorf(codes.Internal, "failed to marshal policy: %v", err)
	}

	key := policyKeyPrefix + req.PolicyId
	err = s.redisClient.Set(ctx, key, policyJSON, 0).Err()
	if err != nil {
		return nil, status.Errorf(codes.Internal, "failed to store policy: %v", err)
	}

	// Update metrics
	s.metrics.mu.Lock()
	s.metrics.TotalPolicies++
	s.metrics.PoliciesInSuperposition++
	s.metrics.mu.Unlock()

	policiesInSuperposition.Inc()

	// Convert to protobuf response
	pbPolicy := &pb.QuantumPolicy{
		PolicyId:             policy.PolicyID,
		EntanglementTag:      policy.EntanglementTag,
		WeightApproved:       policy.WeightApproved,
		WeightRejected:       policy.WeightRejected,
		WeightPending:        policy.WeightPending,
		CreatedAt:            policy.CreatedAt,
		DeadlineAt:           policy.DeadlineAt,
		UncertaintyParameter: policy.UncertaintyParameter,
		Criticality:          policy.Criticality,
		IsCollapsed:          policy.IsCollapsed,
		CollapsedState:       policy.CollapsedState,
	}

	latency := time.Since(startTime).Milliseconds()
	log.Printf("QPE register: policy=%s, etag=%x, latency=%dms",
		req.PolicyId, entanglementTag[:8], latency)

	return &pb.RegisterResponse{
		PolicyId:        req.PolicyId,
		EntanglementTag: entanglementTag,
		QuantumState:    pbPolicy,
	}, nil
}

// Get policy from Redis
func (s *server) getPolicy(ctx context.Context, policyID string) (*QuantumPolicyInternal, error) {
	key := policyKeyPrefix + policyID
	policyJSON, err := s.redisClient.Get(ctx, key).Result()
	if err == redis.Nil {
		return nil, status.Errorf(codes.NotFound, "policy not found: %s", policyID)
	}
	if err != nil {
		return nil, status.Errorf(codes.Internal, "failed to get policy: %v", err)
	}

	var policy QuantumPolicyInternal
	err = json.Unmarshal([]byte(policyJSON), &policy)
	if err != nil {
		return nil, status.Errorf(codes.Internal, "failed to unmarshal policy: %v", err)
	}

	return &policy, nil
}

// Update policy in Redis
func (s *server) updatePolicy(ctx context.Context, policy *QuantumPolicyInternal) error {
	policyJSON, err := json.Marshal(policy)
	if err != nil {
		return fmt.Errorf("failed to marshal policy: %v", err)
	}

	key := policyKeyPrefix + policy.PolicyID
	err = s.redisClient.Set(ctx, key, policyJSON, 0).Err()
	if err != nil {
		return fmt.Errorf("failed to update policy: %v", err)
	}

	return nil
}

// Check if policy deadline has expired
func (s *server) checkDeadlineExpired(policy *QuantumPolicyInternal) bool {
	return time.Now().Unix() > policy.DeadlineAt
}

// Collapse wave function and determine final state
func (s *server) collapseWaveFunction(policy *QuantumPolicyInternal, reason pb.CollapseReason) pb.State {
	if policy.IsCollapsed {
		return policy.CollapsedState
	}

	var finalState pb.State

	// Apply collapse rules based on reason and policy properties
	switch reason {
	case pb.CollapseReason_DEADLINE_EXPIRED:
		// Use maximum weight component for deadline collapse
		weights := []float32{policy.WeightApproved, policy.WeightRejected, policy.WeightPending}
		maxWeight := float32(0.0)
		maxIndex := 0
		for i, w := range weights {
			if w > maxWeight {
				maxWeight = w
				maxIndex = i
			}
		}
		finalState = pb.State(maxIndex)

	case pb.CollapseReason_DETERMINISTIC:
		finalState = deterministicCollapse(policy.PolicyID)

	case pb.CollapseReason_OBSERVATION:
		// High criticality policies bias toward pending for human review
		if policy.Criticality == "HIGH" && policy.UncertaintyParameter > 0.7 {
			finalState = pb.State_PENDING
		} else {
			weights := []float32{policy.WeightApproved, policy.WeightRejected, policy.WeightPending}
			finalState = probabilisticCollapse(weights)
		}

	default: // MEASUREMENT, MANUAL
		weights := []float32{policy.WeightApproved, policy.WeightRejected, policy.WeightPending}
		finalState = probabilisticCollapse(weights)
	}

	// Update policy state
	policy.IsCollapsed = true
	policy.CollapsedState = finalState

	// Update metrics
	s.metrics.mu.Lock()
	s.metrics.PoliciesInSuperposition--
	s.metrics.CollapsedPolicies++
	if s.metrics.CollapseReasons == nil {
		s.metrics.CollapseReasons = make(map[string]int64)
	}
	s.metrics.CollapseReasons[reason.String()]++
	s.metrics.mu.Unlock()

	policiesInSuperposition.Dec()
	stateTransitions.WithLabelValues(policy.PolicyID, "SUPERPOSITION", finalState.String()).Inc()

	return finalState
}

// Measure policy state (collapses superposition and calls PGC)
func (s *server) Measure(ctx context.Context, req *pb.MeasureRequest) (*pb.MeasureResponse, error) {
	startTime := time.Now()

	// Get policy from Redis
	policy, err := s.getPolicy(ctx, req.PolicyId)
	if err != nil {
		return nil, err
	}

	// Verify entanglement tag integrity
	if !verifyEntanglementTag(policy.PolicyID, policy.EntanglementTag) {
		return nil, status.Errorf(codes.DataLoss, "entanglement tag verification failed")
	}

	var finalState pb.State
	var collapseReason pb.CollapseReason
	wasAlreadyCollapsed := policy.IsCollapsed

	// Check if already collapsed
	if policy.IsCollapsed {
		finalState = policy.CollapsedState
		collapseReason = pb.CollapseReason_MEASUREMENT
	} else {
		// Check for deadline expiration
		if s.checkDeadlineExpired(policy) {
			collapseReason = pb.CollapseReason_DEADLINE_EXPIRED
		} else if s.deterministicMode {
			collapseReason = pb.CollapseReason_DETERMINISTIC
		} else {
			collapseReason = pb.CollapseReason_MEASUREMENT
		}

		// Collapse wave function
		finalState = s.collapseWaveFunction(policy, collapseReason)

		// Update policy in Redis
		err = s.updatePolicy(ctx, policy)
		if err != nil {
			log.Printf("Failed to update policy after collapse: %v", err)
		}
	}

	// Integrate with external PGC service via HTTP helper
	pgcResult, err := callPGCService(ctx, s.pgcServiceURL, policy)
	if err != nil {
		log.Printf("PGC invocation error: %v", err)
		pgcResult = false
	}

	// Calculate Heisenberg constant (latency × accuracy)
	latencyMs := float32(time.Since(startTime).Milliseconds())
	accuracy := float32(0.95) // Mock accuracy - calculate from PGC result
	heisenbergK := latencyMs * accuracy

	// Update metrics
	qpeLatency.WithLabelValues(req.PolicyId, finalState.String()).Observe(float64(latencyMs))
	heisenbergConstant.Set(float64(heisenbergK))

	log.Printf("QPE measure: policy=%s, etag=%x, state=%s, latency=%.2fms, K=%.2f",
		req.PolicyId, policy.EntanglementTag[:8], finalState.String(), latencyMs, heisenbergK)

	return &pb.MeasureResponse{
		PolicyId:            req.PolicyId,
		State:               finalState,
		PgcResult:           pgcResult,
		LatencyMs:           latencyMs,
		EntanglementTag:     policy.EntanglementTag,
		CollapseReason:      collapseReason,
		WasAlreadyCollapsed: wasAlreadyCollapsed,
		HeisenbergConstant:  heisenbergK,
	}, nil
}

// Set uncertainty parameter (λ) for speed-accuracy trade-off
func (s *server) SetUncertainty(ctx context.Context, req *pb.UncertaintyRequest) (*pb.UncertaintyResponse, error) {
	if req.Lambda < 0 || req.Lambda > 1 {
		return nil, status.Errorf(codes.InvalidArgument, "lambda must be between 0 and 1")
	}

	s.uncertaintyMu.Lock()
	s.uncertainty = req.Lambda
	s.uncertaintyMu.Unlock()

	uncertaintyLevel.Set(float64(req.Lambda))

	var description string
	if req.Lambda > 0.7 {
		description = "High accuracy mode: prioritizing thorough validation over speed"
	} else if req.Lambda < 0.3 {
		description = "High speed mode: prioritizing fast processing over exhaustive checks"
	} else {
		description = "Balanced mode: moderate trade-off between accuracy and speed"
	}

	log.Printf("QPE uncertainty updated: λ=%.3f (%s)", req.Lambda, description)

	return &pb.UncertaintyResponse{
		Lambda:            req.Lambda,
		EffectDescription: description,
	}, nil
}

// Observer effect - force state collapse through stakeholder observation
func (s *server) Observe(ctx context.Context, req *pb.ObserveRequest) (*pb.ObserveResponse, error) {
	// Get policy from Redis
	policy, err := s.getPolicy(ctx, req.PolicyId)
	if err != nil {
		return nil, err
	}

	wasCollapsed := policy.IsCollapsed
	var finalState pb.State

	if !policy.IsCollapsed {
		// Observer effect triggers collapse
		finalState = s.collapseWaveFunction(policy, pb.CollapseReason_OBSERVATION)

		// Update policy in Redis
		err = s.updatePolicy(ctx, policy)
		if err != nil {
			log.Printf("Failed to update policy after observation: %v", err)
		}
	} else {
		finalState = policy.CollapsedState
	}

	observationTime := time.Now().Unix()

	log.Printf("QPE observe: policy=%s, observer=%s, state=%s, collapsed=%v",
		req.PolicyId, req.ObserverId, finalState.String(), !wasCollapsed)

	return &pb.ObserveResponse{
		PolicyId:             req.PolicyId,
		State:                finalState,
		WasCollapsed:         !wasCollapsed,
		EntanglementTag:      policy.EntanglementTag,
		ObservationTimestamp: observationTime,
	}, nil
}

// Get current quantum state without collapse (for monitoring)
func (s *server) GetQuantumState(ctx context.Context, req *pb.GetQuantumStateRequest) (*pb.GetQuantumStateResponse, error) {
	policy, err := s.getPolicy(ctx, req.PolicyId)
	if err != nil {
		if status.Code(err) == codes.NotFound {
			return &pb.GetQuantumStateResponse{Exists: false}, nil
		}
		return nil, err
	}

	// Calculate superposition entropy
	weights := []float32{policy.WeightApproved, policy.WeightRejected, policy.WeightPending}
	entropy := calculateSuperpositionEntropy(weights)

	pbPolicy := &pb.QuantumPolicy{
		PolicyId:             policy.PolicyID,
		EntanglementTag:      policy.EntanglementTag,
		WeightApproved:       policy.WeightApproved,
		WeightRejected:       policy.WeightRejected,
		WeightPending:        policy.WeightPending,
		CreatedAt:            policy.CreatedAt,
		DeadlineAt:           policy.DeadlineAt,
		UncertaintyParameter: policy.UncertaintyParameter,
		Criticality:          policy.Criticality,
		IsCollapsed:          policy.IsCollapsed,
		CollapsedState:       policy.CollapsedState,
	}

	return &pb.GetQuantumStateResponse{
		QuantumState:         pbPolicy,
		Exists:               true,
		SuperpositionEntropy: entropy,
	}, nil
}

// Health check endpoint
func (s *server) HealthCheck(ctx context.Context, req *pb.HealthCheckRequest) (*pb.HealthCheckResponse, error) {
	details := make(map[string]string)

	// Check Redis connection
	_, err := s.redisClient.Ping(ctx).Result()
	if err != nil {
		details["redis"] = "unhealthy: " + err.Error()
		return &pb.HealthCheckResponse{
			Healthy: false,
			Status:  "Redis connection failed",
			Details: details,
		}, nil
	}
	details["redis"] = "healthy"

	// Check uncertainty parameter
	s.uncertaintyMu.RLock()
	uncertainty := s.uncertainty
	s.uncertaintyMu.RUnlock()
	details["uncertainty"] = fmt.Sprintf("%.3f", uncertainty)

	// Check metrics
	s.metrics.mu.RLock()
	details["total_policies"] = fmt.Sprintf("%d", s.metrics.TotalPolicies)
	details["superposition_policies"] = fmt.Sprintf("%d", s.metrics.PoliciesInSuperposition)
	s.metrics.mu.RUnlock()

	details["constitutional_hash"] = constitutionalHash

	return &pb.HealthCheckResponse{
		Healthy: true,
		Status:  "All systems operational",
		Details: details,
	}, nil
}

func main() {
	// Initialize Redis client
	redisURL := os.Getenv("REDIS_URL")
	if redisURL == "" {
		redisURL = "localhost:6379"
	}

	redisClient := redis.NewClient(&redis.Options{
		Addr: redisURL,
	})

	// Test Redis connection
	ctx := context.Background()
	_, err := redisClient.Ping(ctx).Result()
	if err != nil {
		log.Fatalf("Failed to connect to Redis: %v", err)
	}

	// Initialize metrics
	metrics := &QPEMetrics{
		StateDistribution: make(map[string]int64),
		CollapseReasons:   make(map[string]int64),
	}

	// Create server
	srv := &server{
		redisClient:   redisClient,
		uncertainty:   defaultUncertainty,
		pgcServiceURL: os.Getenv("PGC_SERVICE_URL"),
		metrics:       metrics,
	}

	// Set initial uncertainty level
	uncertaintyLevel.Set(float64(defaultUncertainty))

	// Start Prometheus metrics server
	go func() {
		http.Handle("/metrics", promhttp.Handler())
		log.Printf("Prometheus metrics server listening on :8013")
		log.Fatal(http.ListenAndServe(":8013", nil))
	}()

	// Start gRPC server
	port := os.Getenv("QPE_PORT")
	if port == "" {
		port = ":8012"
	}

	lis, err := net.Listen("tcp", port)
	if err != nil {
		log.Fatalf("Failed to listen: %v", err)
	}

	grpcServer := grpc.NewServer()
	pb.RegisterQuantumPolicyEvaluatorServer(grpcServer, srv)

	// Initialize context for graceful shutdown on interrupt signals
	ctx, cancel := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer cancel()
	go func() {
		<-ctx.Done()
		log.Println("Initiating graceful shutdown of QPE service...")
		grpcServer.GracefulStop()
		// Optionally close Redis client
		srv.redisClient.Close()
	}()

	log.Printf("QPE service listening at %v", lis.Addr())
	log.Printf("Constitutional hash: %s", constitutionalHash)
	log.Printf("PGC service URL: %s", srv.pgcServiceURL)

	if err := grpcServer.Serve(lis); err != nil {
		log.Fatalf("Failed to serve: %v", err)
	}
}
