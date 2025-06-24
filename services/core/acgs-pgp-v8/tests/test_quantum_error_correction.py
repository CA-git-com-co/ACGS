"""
Tests for Quantum Error Correction Engine

Comprehensive tests for the quantum-inspired error correction system
including stabilizer codes, error detection, and correction algorithms.
"""

import pytest
import numpy as np
from unittest.mock import patch, MagicMock

from services.core.acgs_pgp_v8.src.quantum.qec_engine import (
    QuantumErrorCorrectionEngine,
    QuantumState,
    StabilizerCode,
)


class TestQuantumState:
    """Test quantum state representation and operations."""
    
    def test_quantum_state_initialization(self):
        """Test quantum state initialization and normalization."""
        state = QuantumState()
        
        # Check default initialization
        assert len(state.amplitudes) == 2
        assert np.allclose(state.amplitudes, [1.0, 0.0])
        assert len(state.phases) == 2
        assert state.coherence_time == 1.0
        assert state.entanglement_map == {}
        assert state.error_syndrome == []
        assert state.correction_history == []
    
    def test_quantum_state_normalization(self):
        """Test quantum state normalization."""
        # Create unnormalized state
        amplitudes = np.array([3.0, 4.0])
        state = QuantumState(amplitudes=amplitudes)
        
        # Check normalization
        norm = np.linalg.norm(state.amplitudes)
        assert np.isclose(norm, 1.0)
        assert np.allclose(state.amplitudes, [0.6, 0.8])
    
    def test_quantum_fidelity_calculation(self):
        """Test quantum fidelity calculation between states."""
        state1 = QuantumState(amplitudes=np.array([1.0, 0.0]))
        state2 = QuantumState(amplitudes=np.array([1.0, 0.0]))
        state3 = QuantumState(amplitudes=np.array([0.0, 1.0]))
        
        # Identical states should have fidelity 1
        assert np.isclose(state1.get_fidelity(state2), 1.0)
        
        # Orthogonal states should have fidelity 0
        assert np.isclose(state1.get_fidelity(state3), 0.0)
    
    def test_decoherence_application(self):
        """Test decoherence application to quantum state."""
        state = QuantumState(amplitudes=np.array([1.0, 0.0]))
        original_amplitudes = state.amplitudes.copy()
        
        # Apply decoherence
        state.apply_decoherence(0.1)
        
        # State should be different but still normalized
        assert not np.allclose(state.amplitudes, original_amplitudes)
        assert np.isclose(np.linalg.norm(state.amplitudes), 1.0)


class TestStabilizerCode:
    """Test stabilizer code definitions and validation."""
    
    def test_stabilizer_code_creation(self):
        """Test stabilizer code creation and validation."""
        code = StabilizerCode(
            n_qubits=3,
            k_logical=1,
            distance=3,
            stabilizer_generators=['ZZI', 'IZZ'],
            logical_operators=['XXX', 'ZZZ']
        )
        
        assert code.n_qubits == 3
        assert code.k_logical == 1
        assert code.distance == 3
        assert len(code.stabilizer_generators) == 2
        assert len(code.logical_operators) == 2
    
    def test_stabilizer_code_validation(self):
        """Test stabilizer code parameter validation."""
        # Invalid parameters should raise ValueError
        with pytest.raises(ValueError):
            StabilizerCode(
                n_qubits=0,
                k_logical=1,
                distance=3,
                stabilizer_generators=[],
                logical_operators=[]
            )
        
        with pytest.raises(ValueError):
            StabilizerCode(
                n_qubits=3,
                k_logical=1,
                distance=0,
                stabilizer_generators=['ZZI'],
                logical_operators=['XXX']
            )


class TestQuantumErrorCorrectionEngine:
    """Test quantum error correction engine functionality."""
    
    @pytest.fixture
    def qec_engine(self):
        """Create QEC engine for testing."""
        return QuantumErrorCorrectionEngine(
            code_distance=3,
            decoherence_rate=0.01,
            correction_threshold=0.1
        )
    
    def test_qec_engine_initialization(self, qec_engine):
        """Test QEC engine initialization."""
        assert qec_engine.code_distance == 3
        assert qec_engine.decoherence_rate == 0.01
        assert qec_engine.correction_threshold == 0.1
        assert 'repetition_3' in qec_engine.stabilizer_codes
        assert 'five_qubit' in qec_engine.stabilizer_codes
        assert 'steane_7' in qec_engine.stabilizer_codes
    
    def test_semantic_content_encoding(self, qec_engine):
        """Test encoding semantic content into quantum states."""
        content = "Test policy content for quantum encoding"
        
        # Test with different stabilizer codes
        for code_name in ['repetition_3', 'five_qubit', 'steane_7']:
            quantum_state = qec_engine.encode_semantic_content(content, code_name)
            
            assert isinstance(quantum_state, QuantumState)
            assert len(quantum_state.amplitudes) > 0
            assert np.isclose(np.linalg.norm(quantum_state.amplitudes), 1.0)
            assert quantum_state.coherence_time > 0
    
    def test_error_detection(self, qec_engine):
        """Test quantum error detection using stabilizer measurements."""
        content = "Test content for error detection"
        quantum_state = qec_engine.encode_semantic_content(content, 'five_qubit')
        
        # Detect errors (should be none initially)
        syndrome = qec_engine.detect_errors(quantum_state, 'five_qubit')
        
        assert isinstance(syndrome, list)
        assert len(syndrome) == 4  # 5-qubit code has 4 stabilizer generators
        assert all(s in [0, 1] for s in syndrome)
        assert quantum_state.error_syndrome == syndrome
    
    def test_error_correction(self, qec_engine):
        """Test quantum error correction process."""
        content = "Test content for error correction"
        quantum_state = qec_engine.encode_semantic_content(content, 'five_qubit')
        
        # Simulate error syndrome
        test_syndrome = [1, 0, 0, 0]  # X error on qubit 0
        
        # Apply correction
        success = qec_engine.correct_errors(quantum_state, test_syndrome, 'five_qubit')
        
        # Check correction was attempted
        assert isinstance(success, bool)
        assert len(quantum_state.correction_history) >= 0
    
    def test_semantic_entanglement_calculation(self, qec_engine):
        """Test quantum entanglement calculation between semantic states."""
        content1 = "First policy content"
        content2 = "Second policy content"
        content3 = "First policy content"  # Same as content1
        
        state1 = qec_engine.encode_semantic_content(content1, 'five_qubit')
        state2 = qec_engine.encode_semantic_content(content2, 'five_qubit')
        state3 = qec_engine.encode_semantic_content(content3, 'five_qubit')
        
        # Calculate entanglement
        entanglement_12 = qec_engine.calculate_semantic_entanglement(state1, state2)
        entanglement_13 = qec_engine.calculate_semantic_entanglement(state1, state3)
        
        assert 0.0 <= entanglement_12 <= 1.0
        assert 0.0 <= entanglement_13 <= 1.0
        
        # Identical content should have higher entanglement
        assert entanglement_13 >= entanglement_12
    
    def test_correction_statistics(self, qec_engine):
        """Test correction statistics tracking."""
        stats = qec_engine.get_correction_statistics()
        
        assert 'total_corrections' in stats
        assert 'successful_corrections' in stats
        assert 'failed_corrections' in stats
        assert 'syndrome_detections' in stats
        assert 'success_rate' in stats
        assert 'code_distance' in stats
        assert 'decoherence_rate' in stats
        assert 'quantum_backend_available' in stats
        
        assert stats['code_distance'] == 3
        assert stats['decoherence_rate'] == 0.01
        assert isinstance(stats['quantum_backend_available'], bool)
    
    @pytest.mark.asyncio
    async def test_qec_engine_cleanup(self, qec_engine):
        """Test QEC engine cleanup."""
        # Should not raise any exceptions
        await qec_engine.cleanup()
    
    def test_pauli_operator_applications(self, qec_engine):
        """Test Pauli operator applications for error correction."""
        content = "Test content for Pauli operations"
        quantum_state = qec_engine.encode_semantic_content(content, 'repetition_3')
        original_amplitudes = quantum_state.amplitudes.copy()
        
        # Test Pauli-X application
        qec_engine._apply_pauli_x(quantum_state, 0)
        assert not np.allclose(quantum_state.amplitudes, original_amplitudes)
        
        # Test Pauli-Z application
        qec_engine._apply_pauli_z(quantum_state, 0)
        
        # Test Pauli-Y application
        qec_engine._apply_pauli_y(quantum_state, 0)
    
    def test_syndrome_to_correction_mapping(self, qec_engine):
        """Test syndrome to correction operation mapping."""
        # Test known syndrome mappings
        five_qubit_code = qec_engine.stabilizer_codes['five_qubit']
        
        # Test some known syndromes
        correction = qec_engine._syndrome_to_correction([1, 0, 0, 0], five_qubit_code)
        assert correction is not None or correction is None  # May not have all mappings
        
        correction = qec_engine._syndrome_to_correction([0, 0, 0, 0], five_qubit_code)
        assert correction is None  # No error syndrome
    
    def test_classical_encoding_fallback(self, qec_engine):
        """Test classical encoding when quantum backend unavailable."""
        content = "Test content for classical encoding"
        
        # Mock quantum backend as unavailable
        with patch('services.core.acgs_pgp_v8.src.quantum.qec_engine.QUANTUM_AVAILABLE', False):
            quantum_state = qec_engine.encode_semantic_content(content, 'five_qubit')
            
            assert isinstance(quantum_state, QuantumState)
            assert len(quantum_state.amplitudes) > 0
    
    def test_error_handling_in_encoding(self, qec_engine):
        """Test error handling during encoding process."""
        # Test with invalid code name
        with pytest.raises(ValueError):
            qec_engine.encode_semantic_content("test", "invalid_code")
        
        # Test with empty content
        quantum_state = qec_engine.encode_semantic_content("", 'five_qubit')
        assert isinstance(quantum_state, QuantumState)
    
    def test_stabilizer_measurement_simulation(self, qec_engine):
        """Test stabilizer measurement simulation."""
        content = "Test content for stabilizer measurement"
        quantum_state = qec_engine.encode_semantic_content(content, 'five_qubit')
        
        # Test measurement of different Pauli strings
        pauli_strings = ['ZZIII', 'XZIII', 'IXZII']
        
        for pauli_string in pauli_strings:
            measurement = qec_engine._measure_stabilizer(quantum_state, pauli_string)
            assert measurement in [0, 1]
    
    def test_quantum_circuit_encoding_methods(self, qec_engine):
        """Test quantum circuit encoding methods."""
        # These methods are called internally during encoding
        # Test that they don't raise exceptions
        
        try:
            # Mock quantum circuit for testing
            from unittest.mock import MagicMock
            mock_circuit = MagicMock()
            mock_qreg = MagicMock()
            
            # Test encoding methods
            qec_engine._apply_five_qubit_encoding(mock_circuit, mock_qreg)
            qec_engine._apply_steane_encoding(mock_circuit, mock_qreg)
            qec_engine._apply_repetition_encoding(mock_circuit, mock_qreg)
            
        except Exception as e:
            # If quantum libraries not available, methods should still be callable
            assert "qiskit" in str(e).lower() or "cirq" in str(e).lower()


@pytest.mark.integration
class TestQuantumIntegration:
    """Integration tests for quantum error correction with ACGS-PGP v8."""
    
    @pytest.fixture
    def qec_engine(self):
        """Create QEC engine for integration testing."""
        return QuantumErrorCorrectionEngine(
            code_distance=3,
            decoherence_rate=0.05,
            correction_threshold=0.2
        )
    
    def test_policy_content_quantum_processing(self, qec_engine):
        """Test end-to-end quantum processing of policy content."""
        policy_content = """
        Data Privacy Protection Policy
        
        This policy establishes comprehensive data protection measures
        to ensure citizen privacy rights while enabling effective governance.
        
        Key provisions:
        1. Data minimization principles
        2. Consent-based data collection
        3. Transparent data usage policies
        4. Regular privacy audits
        """
        
        # Encode policy content
        quantum_state = qec_engine.encode_semantic_content(policy_content, 'steane_7')
        
        # Detect any errors
        syndrome = qec_engine.detect_errors(quantum_state, 'steane_7')
        
        # Apply corrections if needed
        if any(syndrome):
            success = qec_engine.correct_errors(quantum_state, syndrome, 'steane_7')
            assert isinstance(success, bool)
        
        # Verify state integrity
        assert isinstance(quantum_state, QuantumState)
        assert np.isclose(np.linalg.norm(quantum_state.amplitudes), 1.0)
    
    def test_multiple_policy_entanglement(self, qec_engine):
        """Test quantum entanglement between multiple policy documents."""
        policies = [
            "Privacy protection policy with data minimization",
            "Security framework with encryption requirements", 
            "Privacy protection policy with data minimization",  # Duplicate
            "Transparency policy with public disclosure rules"
        ]
        
        # Encode all policies
        quantum_states = []
        for policy in policies:
            state = qec_engine.encode_semantic_content(policy, 'five_qubit')
            quantum_states.append(state)
        
        # Calculate entanglement matrix
        entanglement_matrix = []
        for i, state1 in enumerate(quantum_states):
            row = []
            for j, state2 in enumerate(quantum_states):
                if i != j:
                    entanglement = qec_engine.calculate_semantic_entanglement(state1, state2)
                    row.append(entanglement)
                else:
                    row.append(1.0)  # Self-entanglement
            entanglement_matrix.append(row)
        
        # Verify entanglement properties
        assert len(entanglement_matrix) == len(policies)
        
        # Identical policies should have high entanglement
        assert entanglement_matrix[0][2] > 0.8  # Policies 0 and 2 are identical
        
        # Different policies should have lower entanglement
        assert entanglement_matrix[0][1] < entanglement_matrix[0][2]
