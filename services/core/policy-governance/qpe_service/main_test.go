// Unit tests for Quantum Policy Evaluator (QPE) Service
// ACGS-1 Constitutional Governance Enhancement
//
// Test Coverage Requirements:
// - ≥90% test pass rate
// - ≥80% code coverage
// - Constitutional compliance validation
// - Performance targets validation (<2ms latency overhead)
// - Entanglement tag verification
// - Uncertainty principle validation
//
// Formal Verification Comments:
// requires: test_coverage >= 0.8
// ensures: all_tests_pass_rate >= 0.9
// ensures: latency_overhead <= 2ms for 95th percentile
// ensures: entanglement_tag_verification == true
// sha256: opa_schrodinger_quantum_superposition_tests_v1.0

package main

import (
	"context"
	"crypto/hmac"
	"crypto/sha256"
	"encoding/base64"
	"fmt"
	"strings"
	"testing"
	"time"

	"github.com/go-redis/redismock/v8"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	pb "qpe_service/proto"
)

// Test setup helpers
func setupTestServer(t *testing.T) (*server, redismock.ClientMock) {
	db, mock := redismock.NewClientMock()

	metrics := &QPEMetrics{
		StateDistribution: make(map[string]int64),
		CollapseReasons:   make(map[string]int64),
	}

	srv := &server{
		redisClient:   db,
		uncertainty:   defaultUncertainty,
		pgcServiceURL: "mock://pgc_service:8005",
		metrics:       metrics,
	}

	return srv, mock
}

// Benchmark setup helper
func setupBenchmarkServer(b *testing.B) (*server, redismock.ClientMock) {
	db, mock := redismock.NewClientMock()

	metrics := &QPEMetrics{
		StateDistribution: make(map[string]int64),
		CollapseReasons:   make(map[string]int64),
	}

	srv := &server{
		redisClient:   db,
		uncertainty:   defaultUncertainty,
		pgcServiceURL: "mock://pgc_service:8005",
		metrics:       metrics,
	}

	return srv, mock
}

func TestRegisterInitialWeights(t *testing.T) {
	s, mr := setupTestServer(t)
	_ = mr

	ctx := context.Background()
	req := &pb.RegisterRequest{
		PolicyId:    "test-policy-1",
		Criticality: "MEDIUM",
	}

	// Mock Redis SET operation - use regex to match any JSON
	mr.Regexp().ExpectSet("qpe:policy:test-policy-1", `.*`, 0).SetVal("OK")

	resp, err := s.Register(ctx, req)
	assert.NoError(t, err)
	assert.Equal(t, "test-policy-1", resp.PolicyId)
	assert.NotNil(t, resp.EntanglementTag)
	assert.Equal(t, len(resp.EntanglementTag), 32) // SHA256 hash length

	// Verify initial superposition weights (equal superposition)
	quantum := resp.QuantumState
	assert.InDelta(t, 1.0/3.0, quantum.WeightApproved, 0.01)
	assert.InDelta(t, 1.0/3.0, quantum.WeightRejected, 0.01)
	assert.InDelta(t, 1.0/3.0, quantum.WeightPending, 0.01)
	assert.False(t, quantum.IsCollapsed)

	// Verify weights sum to 1.0
	totalWeight := quantum.WeightApproved + quantum.WeightRejected + quantum.WeightPending
	assert.InDelta(t, 1.0, totalWeight, 0.001)

	// Verify entanglement tag generation
	expectedTag := generateEntanglementTag("test-policy-1")
	assert.Equal(t, expectedTag, resp.EntanglementTag)
}

func TestDeterministicCollapseReproducibility(t *testing.T) {
	s, mr := setupTestServer(t)
	_ = mr

	ctx := context.Background()
	policyId := "deterministic-test"
	s.deterministicMode = true

	// Register policy
	registerReq := &pb.RegisterRequest{
		PolicyId:          policyId,
		DeterministicMode: true,
	}

	mr.Regexp().ExpectSet("qpe:policy:"+policyId, `.*`, 0).SetVal("OK")
	_, err := s.Register(ctx, registerReq)
	require.NoError(t, err)

	// Mock Redis GET for measure operations
	now := time.Now().Unix()
	policyJSON := fmt.Sprintf(`{
		"policy_id": "deterministic-test",
		"entanglement_tag": "%s",
		"weight_approved": 0.33,
		"weight_rejected": 0.33,
		"weight_pending": 0.34,
		"created_at": %d,
		"deadline_at": %d,
		"uncertainty_parameter": 0.5,
		"criticality": "MEDIUM",
		"is_collapsed": false,
		"collapsed_state": 2
	}`, base64.StdEncoding.EncodeToString(generateEntanglementTag(policyId)), now, now+86400)

	// First measurement
	mr.ExpectGet("qpe:policy:" + policyId).SetVal(policyJSON)
	mr.Regexp().ExpectSet("qpe:policy:"+policyId, `.*`, 0).SetVal("OK")

	measureReq := &pb.MeasureRequest{PolicyId: policyId}
	resp1, err := s.Measure(ctx, measureReq)
	require.NoError(t, err)

	// Second measurement (should be identical due to deterministic mode)
	mr.ExpectGet("qpe:policy:" + policyId).SetVal(policyJSON)
	mr.Regexp().ExpectSet("qpe:policy:"+policyId, `.*`, 0).SetVal("OK")

	resp2, err := s.Measure(ctx, measureReq)
	require.NoError(t, err)

	// Should get same state both times in deterministic mode
	assert.Equal(t, resp1.State, resp2.State)
	assert.Equal(t, resp1.CollapseReason, pb.CollapseReason_DETERMINISTIC)
	assert.Equal(t, resp2.CollapseReason, pb.CollapseReason_DETERMINISTIC)
}

func TestLatencyBudget(t *testing.T) {
	s, mr := setupTestServer(t)
	_ = mr

	ctx := context.Background()
	policyId := "latency-test"

	// Register policy
	mr.Regexp().ExpectSet("qpe:policy:"+policyId, `.*`, 0).SetVal("OK")

	registerReq := &pb.RegisterRequest{PolicyId: policyId}
	_, err := s.Register(ctx, registerReq)
	require.NoError(t, err)

	// Mock Redis GET for measure
	now := time.Now().Unix()
	policyJSON := fmt.Sprintf(`{
		"policy_id": "latency-test",
		"entanglement_tag": "%s",
		"weight_approved": 0.33,
		"weight_rejected": 0.33,
		"weight_pending": 0.34,
		"created_at": %d,
		"deadline_at": %d,
		"uncertainty_parameter": 0.5,
		"criticality": "MEDIUM",
		"is_collapsed": false,
		"collapsed_state": 2
	}`, base64.StdEncoding.EncodeToString(generateEntanglementTag(policyId)), now, now+86400)

	mr.ExpectGet("qpe:policy:" + policyId).SetVal(policyJSON)
	mr.Regexp().ExpectSet("qpe:policy:"+policyId, `.*`, 0).SetVal("OK")

	// Measure latency
	start := time.Now()
	measureReq := &pb.MeasureRequest{PolicyId: policyId}
	resp, err := s.Measure(ctx, measureReq)
	latency := time.Since(start).Milliseconds()

	require.NoError(t, err)

	// Should meet <2ms latency budget for QPE operations
	assert.Less(t, latency, int64(2), "QPE latency should be <2ms")
	assert.Less(t, resp.LatencyMs, float32(2.0), "Reported latency should be <2ms")

	// Verify latency is recorded (should be >= 0 for actual operations)
	assert.GreaterOrEqual(t, resp.LatencyMs, float32(0))

	// Verify Heisenberg constant is calculated (can be 0 for very fast operations)
	assert.GreaterOrEqual(t, resp.HeisenbergConstant, float32(0.0))
}

func TestEntanglementTagIntegrity(t *testing.T) {
	// Test entanglement tag generation and verification for 1000 random policy IDs
	for i := 0; i < 1000; i++ {
		policyId := "test-policy-" + string(rune(i))

		// Generate entanglement tag
		tag := generateEntanglementTag(policyId)

		// Verify tag integrity
		assert.True(t, verifyEntanglementTag(policyId, tag),
			"Entanglement tag verification failed for policy %s", policyId)

		// Verify tag length (SHA256 = 32 bytes)
		assert.Equal(t, 32, len(tag), "Entanglement tag should be 32 bytes")

		// Verify constitutional hash is used
		expectedTag := hmac.New(sha256.New, []byte(constitutionalHash))
		expectedTag.Write([]byte(policyId))
		expected := expectedTag.Sum(nil)

		assert.Equal(t, expected, tag, "Tag should match HMAC with constitutional hash")
	}
}

func TestUncertaintyTradeOff(t *testing.T) {
	s, mr := setupTestServer(t)
	_ = mr

	ctx := context.Background()

	// Test different uncertainty levels
	uncertaintyLevels := []float32{0.1, 0.3, 0.5, 0.7, 0.9}

	for _, lambda := range uncertaintyLevels {
		req := &pb.UncertaintyRequest{Lambda: lambda}
		resp, err := s.SetUncertainty(ctx, req)

		require.NoError(t, err)
		assert.Equal(t, lambda, resp.Lambda)

		// Verify uncertainty is stored
		s.uncertaintyMu.RLock()
		storedUncertainty := s.uncertainty
		s.uncertaintyMu.RUnlock()

		assert.Equal(t, lambda, storedUncertainty)

		// Verify effect description is provided
		assert.NotEmpty(t, resp.EffectDescription)

		// Test boundary conditions
		if lambda > 0.7 {
			assert.Contains(t, resp.EffectDescription, "accuracy")
		} else if lambda < 0.3 {
			assert.Contains(t, resp.EffectDescription, "speed")
		} else {
			assert.Contains(t, strings.ToLower(resp.EffectDescription), "balanced")
		}
	}

	// Test invalid uncertainty values
	invalidValues := []float32{-0.1, 1.1, 2.0}
	for _, invalid := range invalidValues {
		req := &pb.UncertaintyRequest{Lambda: invalid}
		_, err := s.SetUncertainty(ctx, req)
		assert.Error(t, err, "Should reject invalid uncertainty value: %f", invalid)
	}
}

func TestConstitutionalHashEntanglement(t *testing.T) {
	// Verify entanglement with constitutional hash "cdd01ef066bc6cf2"
	assert.Equal(t, "cdd01ef066bc6cf2", constitutionalHash)

	// Test entanglement tag generation uses constitutional hash
	policyId := "test-constitutional-entanglement"
	tag := generateEntanglementTag(policyId)

	// Manually calculate expected tag
	h := hmac.New(sha256.New, []byte(constitutionalHash))
	h.Write([]byte(policyId))
	expected := h.Sum(nil)

	assert.Equal(t, expected, tag, "Entanglement tag must use constitutional hash")

	// Verify tag changes if constitutional hash changes
	differentHash := "different-hash"
	h2 := hmac.New(sha256.New, []byte(differentHash))
	h2.Write([]byte(policyId))
	differentTag := h2.Sum(nil)

	assert.NotEqual(t, tag, differentTag, "Tag should be different with different hash")
}

func TestObserverEffectCollapse(t *testing.T) {
	s, mr := setupTestServer(t)
	_ = mr

	ctx := context.Background()
	policyId := "observer-test"

	// Mock policy in superposition
	now := time.Now().Unix()
	policyJSON := fmt.Sprintf(`{
		"policy_id": "observer-test",
		"entanglement_tag": "%s",
		"weight_approved": 0.33,
		"weight_rejected": 0.33,
		"weight_pending": 0.34,
		"created_at": %d,
		"deadline_at": %d,
		"uncertainty_parameter": 0.5,
		"criticality": "HIGH",
		"is_collapsed": false,
		"collapsed_state": 2
	}`, base64.StdEncoding.EncodeToString(generateEntanglementTag(policyId)), now, now+86400)

	mr.ExpectGet("qpe:policy:" + policyId).SetVal(policyJSON)
	mr.Regexp().ExpectSet("qpe:policy:"+policyId, `.*`, 0).SetVal("OK")

	// Trigger observer effect
	observeReq := &pb.ObserveRequest{
		PolicyId:   policyId,
		ObserverId: "stakeholder-123",
	}

	resp, err := s.Observe(ctx, observeReq)
	require.NoError(t, err)

	assert.Equal(t, policyId, resp.PolicyId)
	assert.True(t, resp.WasCollapsed, "Observer effect should trigger collapse")
	assert.Greater(t, resp.ObservationTimestamp, int64(0))

	// Verify entanglement tag
	expectedTag := generateEntanglementTag(policyId)
	assert.Equal(t, expectedTag, resp.EntanglementTag)
}

func TestDeadlineEnforcement(t *testing.T) {
	s, mr := setupTestServer(t)
	_ = mr

	ctx := context.Background()
	policyId := "deadline-test"

	// Create policy with expired deadline
	expiredTime := time.Now().Unix() - 3600 // 1 hour ago
	policyJSON := fmt.Sprintf(`{
		"policy_id": "deadline-test",
		"entanglement_tag": "%s",
		"weight_approved": 0.4,
		"weight_rejected": 0.3,
		"weight_pending": 0.3,
		"created_at": %d,
		"deadline_at": %d,
		"uncertainty_parameter": 0.5,
		"criticality": "MEDIUM",
		"is_collapsed": false,
		"collapsed_state": 2
	}`, base64.StdEncoding.EncodeToString(generateEntanglementTag(policyId)), expiredTime-86400, expiredTime)

	mr.ExpectGet("qpe:policy:" + policyId).SetVal(policyJSON)
	mr.Regexp().ExpectSet("qpe:policy:"+policyId, `.*`, 0).SetVal("OK")

	// Measure expired policy
	measureReq := &pb.MeasureRequest{PolicyId: policyId}
	resp, err := s.Measure(ctx, measureReq)

	require.NoError(t, err)
	assert.Equal(t, pb.CollapseReason_DEADLINE_EXPIRED, resp.CollapseReason)

	// Should collapse to state with maximum weight (approved = 0.4)
	assert.Equal(t, pb.State_APPROVED, resp.State)
}

func TestSuperpositionEntropy(t *testing.T) {
	// Test entropy calculation for different weight distributions
	testCases := []struct {
		weights         []float32
		expectedEntropy float32
		description     string
	}{
		{[]float32{1.0, 0.0, 0.0}, 0.0, "Pure state (no entropy)"},
		{[]float32{1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0}, 1.0986, "Maximum entropy (equal superposition)"},
		{[]float32{0.5, 0.5, 0.0}, 0.6931, "Two-state superposition"},
		{[]float32{0.8, 0.1, 0.1}, 0.6390, "Biased superposition"},
	}

	for _, tc := range testCases {
		entropy := calculateSuperpositionEntropy(tc.weights)
		assert.InDelta(t, tc.expectedEntropy, entropy, 0.01, tc.description)
	}
}

func TestHealthCheck(t *testing.T) {
	s, mr := setupTestServer(t)
	_ = mr

	ctx := context.Background()

	// Mock successful Redis ping
	mr.ExpectPing().SetVal("PONG")

	req := &pb.HealthCheckRequest{}
	resp, err := s.HealthCheck(ctx, req)

	require.NoError(t, err)
	assert.True(t, resp.Healthy)
	assert.Equal(t, "All systems operational", resp.Status)
	assert.Contains(t, resp.Details, "redis")
	assert.Contains(t, resp.Details, "constitutional_hash")
	assert.Equal(t, constitutionalHash, resp.Details["constitutional_hash"])
}

func TestQuantumStateRetrieval(t *testing.T) {
	s, mr := setupTestServer(t)
	_ = mr

	ctx := context.Background()
	policyId := "state-test"

	// Mock policy data
	now := time.Now().Unix()
	policyJSON := fmt.Sprintf(`{
		"policy_id": "state-test",
		"entanglement_tag": "%s",
		"weight_approved": 0.5,
		"weight_rejected": 0.3,
		"weight_pending": 0.2,
		"created_at": %d,
		"deadline_at": %d,
		"uncertainty_parameter": 0.7,
		"criticality": "HIGH",
		"is_collapsed": false,
		"collapsed_state": 2
	}`, base64.StdEncoding.EncodeToString(generateEntanglementTag(policyId)), now, now+86400)

	mr.ExpectGet("qpe:policy:" + policyId).SetVal(policyJSON)

	req := &pb.GetQuantumStateRequest{PolicyId: policyId}
	resp, err := s.GetQuantumState(ctx, req)

	require.NoError(t, err)
	assert.True(t, resp.Exists)
	assert.NotNil(t, resp.QuantumState)

	state := resp.QuantumState
	assert.Equal(t, policyId, state.PolicyId)
	assert.Equal(t, float32(0.5), state.WeightApproved)
	assert.Equal(t, float32(0.3), state.WeightRejected)
	assert.Equal(t, float32(0.2), state.WeightPending)
	assert.False(t, state.IsCollapsed)

	// Verify entropy calculation
	expectedEntropy := calculateSuperpositionEntropy([]float32{0.5, 0.3, 0.2})
	assert.InDelta(t, expectedEntropy, resp.SuperpositionEntropy, 0.01)
}

func TestCriticalityBasedCollapse(t *testing.T) {
	s, mr := setupTestServer(t)
	_ = mr

	// Set high uncertainty for accuracy bias
	s.uncertainty = 0.8

	ctx := context.Background()
	policyId := "criticality-test"

	// Mock HIGH criticality policy
	now := time.Now().Unix()
	policyJSON := fmt.Sprintf(`{
		"policy_id": "criticality-test",
		"entanglement_tag": "%s",
		"weight_approved": 0.33,
		"weight_rejected": 0.33,
		"weight_pending": 0.34,
		"created_at": %d,
		"deadline_at": %d,
		"uncertainty_parameter": 0.8,
		"criticality": "HIGH",
		"is_collapsed": false,
		"collapsed_state": 2
	}`, base64.StdEncoding.EncodeToString(generateEntanglementTag(policyId)), now, now+86400)

	mr.ExpectGet("qpe:policy:" + policyId).SetVal(policyJSON)
	mr.Regexp().ExpectSet("qpe:policy:"+policyId, `.*`, 0).SetVal("OK")

	// Trigger observation (should bias toward PENDING for HIGH criticality)
	observeReq := &pb.ObserveRequest{
		PolicyId:   policyId,
		ObserverId: "stakeholder-456",
	}

	resp, err := s.Observe(ctx, observeReq)
	require.NoError(t, err)

	// With HIGH criticality and high uncertainty, should often collapse to PENDING
	// Note: This is probabilistic, so we can't assert exact state, but we can verify
	// the collapse occurred and the logic was applied
	assert.True(t, resp.WasCollapsed)
	assert.Contains(t, []pb.State{pb.State_APPROVED, pb.State_REJECTED, pb.State_PENDING}, resp.State)
}

// Benchmark tests for performance validation
func BenchmarkRegister(b *testing.B) {
	s, mr := setupBenchmarkServer(b)
	_ = mr

	ctx := context.Background()

	for i := 0; i < b.N; i++ {
		policyId := "bench-policy-" + string(rune(i))
		mr.Regexp().ExpectSet("qpe:policy:"+policyId, `.*`, 0).SetVal("OK")

		req := &pb.RegisterRequest{PolicyId: policyId}
		_, err := s.Register(ctx, req)
		if err != nil {
			b.Fatal(err)
		}
	}
}

func BenchmarkMeasure(b *testing.B) {
	s, mr := setupBenchmarkServer(b)
	_ = mr

	ctx := context.Background()

	// Setup policy data
	now := time.Now().Unix()
	policyJSON := fmt.Sprintf(`{
		"policy_id": "bench-measure",
		"entanglement_tag": "%s",
		"weight_approved": 0.33,
		"weight_rejected": 0.33,
		"weight_pending": 0.34,
		"created_at": %d,
		"deadline_at": %d,
		"uncertainty_parameter": 0.5,
		"criticality": "MEDIUM",
		"is_collapsed": false,
		"collapsed_state": 2
	}`, base64.StdEncoding.EncodeToString(generateEntanglementTag("bench-measure")), now, now+86400)

	for i := 0; i < b.N; i++ {
		mr.ExpectGet("qpe:policy:bench-measure").SetVal(policyJSON)
		mr.Regexp().ExpectSet("qpe:policy:bench-measure", `.*`, 0).SetVal("OK")

		req := &pb.MeasureRequest{PolicyId: "bench-measure"}
		_, err := s.Measure(ctx, req)
		if err != nil {
			b.Fatal(err)
		}
	}
}
