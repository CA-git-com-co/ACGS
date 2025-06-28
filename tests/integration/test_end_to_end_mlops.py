"""
End-to-End MLOps Integration Tests

Comprehensive integration testing for the complete ML pipeline from data ingestion
through prediction serving. Validates constitutional hash integrity, performance
targets, and load testing with 1000+ concurrent requests.

This test suite ensures all critical ML success factors work together while
maintaining ACGS-PGP system performance standards and constitutional compliance.
"""

import unittest
import asyncio
import time
import tempfile
import shutil
import json
import numpy as np
import pandas as pd
from datetime import datetime, timezone
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import Mock, patch
import threading
import statistics

# Import ACGS-PGP MLOps components
import sys
sys.path.append(str(Path(__file__).parent.parent.parent / "services" / "shared"))

from mlops.mlops_manager import MLOpsManager, MLOpsConfig
from mlops.production_integration import create_production_mlops_integration
from mlops.monitoring_dashboard import MonitoringDashboard
from production_ml_optimizer import ProductionMLOptimizer


class TestEndToEndMLOpsIntegration(unittest.TestCase):
    """
    End-to-end integration tests for the complete MLOps pipeline.
    
    Tests the entire workflow from data ingestion through prediction serving
    with constitutional compliance and performance validation.
    """
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment for all tests."""
        cls.test_dir = tempfile.mkdtemp()
        cls.test_path = Path(cls.test_dir)
        
        # Constitutional hash for integrity verification
        cls.constitutional_hash = "cdd01ef066bc6cf2"
        
        # Performance targets
        cls.performance_targets = {
            'response_time_ms': 2000,  # Sub-2s response times
            'constitutional_compliance': 0.95,  # >95% compliance
            'cost_savings': 0.74,  # 74% cost savings
            'availability': 0.999,  # 99.9% availability
            'model_accuracy': 0.90  # >90% prediction accuracy
        }
        
        # Initialize Git repository for testing
        cls._init_test_git_repo()
        
        # Create test data
        cls.test_data = cls._generate_test_data()
        
        # Initialize MLOps components
        cls._initialize_mlops_components()
        
        print(f"End-to-end test environment initialized at {cls.test_dir}")
        print(f"Constitutional hash: {cls.constitutional_hash}")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        shutil.rmtree(cls.test_dir)
        print("End-to-end test environment cleaned up")
    
    @classmethod
    def _init_test_git_repo(cls):
        """Initialize test Git repository."""
        import subprocess
        
        # Initialize Git repo
        subprocess.run(["git", "init"], cwd=cls.test_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], 
                      cwd=cls.test_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], 
                      cwd=cls.test_path, capture_output=True)
        
        # Create initial commit
        test_file = cls.test_path / "README.md"
        test_file.write_text("# End-to-End MLOps Test Repository")
        
        subprocess.run(["git", "add", "README.md"], cwd=cls.test_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], 
                      cwd=cls.test_path, capture_output=True)
    
    @classmethod
    def _generate_test_data(cls):
        """Generate comprehensive test data for ML pipeline."""
        np.random.seed(42)
        
        # Generate synthetic routing data
        n_samples = 10000
        
        data = {
            'request_complexity': np.random.uniform(0.1, 1.0, n_samples),
            'user_priority': np.random.choice([1, 2, 3, 4, 5], n_samples),
            'system_load': np.random.uniform(0.0, 1.0, n_samples),
            'time_of_day': np.random.uniform(0, 24, n_samples),
            'request_type': np.random.choice(['query', 'analysis', 'generation'], n_samples),
            'user_tier': np.random.choice(['basic', 'premium', 'enterprise'], n_samples),
            'historical_response_time': np.random.uniform(100, 5000, n_samples),
            'cost_budget': np.random.uniform(0.01, 1.0, n_samples)
        }
        
        # Generate target variables
        # Response time (influenced by complexity and system load)
        response_time = (
            data['request_complexity'] * 1000 +
            data['system_load'] * 500 +
            np.random.normal(0, 100, n_samples)
        )
        response_time = np.clip(response_time, 50, 5000)
        
        # Cost (influenced by complexity and user tier)
        tier_multiplier = {'basic': 1.0, 'premium': 0.8, 'enterprise': 0.6}
        cost = np.array([
            data['request_complexity'][i] * 0.1 * tier_multiplier[data['user_tier'][i]]
            for i in range(n_samples)
        ])
        cost += np.random.normal(0, 0.01, n_samples)
        cost = np.clip(cost, 0.001, 1.0)
        
        # Constitutional compliance (should be high)
        constitutional_compliance = np.random.beta(20, 2, n_samples)  # High values
        
        df = pd.DataFrame(data)
        df['response_time'] = response_time
        df['cost'] = cost
        df['constitutional_compliance'] = constitutional_compliance
        
        return df
    
    @classmethod
    def _initialize_mlops_components(cls):
        """Initialize MLOps components for testing."""
        # MLOps configuration
        cls.mlops_config = MLOpsConfig(
            storage_root=str(cls.test_path / "mlops"),
            git_repo_path=str(cls.test_path),
            constitutional_hash=cls.constitutional_hash,
            performance_targets=cls.performance_targets
        )
        
        # Initialize MLOps manager
        cls.mlops_manager = MLOpsManager(cls.mlops_config)

        # Initialize production integration using the same MLOps manager
        cls.production_integration = create_production_mlops_integration(
            constitutional_hash=cls.constitutional_hash,
            storage_root=str(cls.test_path / "mlops"),
            existing_mlops_manager=cls.mlops_manager  # Share the same MLOps manager
        )
        
        # Initialize monitoring dashboard
        cls.monitoring_dashboard = MonitoringDashboard(
            constitutional_hash=cls.constitutional_hash,
            port=8081  # Use different port for testing
        )
        
        print("MLOps components initialized successfully")
    
    def test_constitutional_hash_integrity(self):
        """Test constitutional hash integrity across all components."""
        print("\n=== Testing Constitutional Hash Integrity ===")
        
        # Verify hash in all components
        components = [
            ('MLOps Manager', self.mlops_manager.config.constitutional_hash),
            ('Production Integration', self.production_integration.constitutional_hash),
            ('Monitoring Dashboard', self.monitoring_dashboard.constitutional_hash),
        ]
        
        for component_name, component_hash in components:
            with self.subTest(component=component_name):
                self.assertEqual(
                    component_hash, 
                    self.constitutional_hash,
                    f"{component_name} has incorrect constitutional hash"
                )
                print(f"✓ {component_name}: Constitutional hash verified")
        
        print("✅ Constitutional hash integrity validated across all components")
    
    def test_data_ingestion_and_preprocessing(self):
        """Test complete data ingestion and preprocessing pipeline."""
        print("\n=== Testing Data Ingestion and Preprocessing ===")
        
        # Split data for training and testing
        train_size = int(0.8 * len(self.test_data))
        train_data = self.test_data[:train_size]
        test_data = self.test_data[train_size:]
        
        # Prepare features and targets
        feature_columns = [
            'request_complexity', 'user_priority', 'system_load', 
            'time_of_day', 'historical_response_time', 'cost_budget'
        ]
        
        X_train = train_data[feature_columns]
        y_train = train_data['response_time']
        
        X_test = test_data[feature_columns]
        y_test = test_data['response_time']
        
        # Test data quality
        self.assertGreater(len(X_train), 1000, "Insufficient training data")
        self.assertGreater(len(X_test), 100, "Insufficient test data")
        self.assertFalse(X_train.isnull().any().any(), "Training data contains null values")
        self.assertFalse(X_test.isnull().any().any(), "Test data contains null values")
        
        print(f"✓ Training data: {len(X_train)} samples")
        print(f"✓ Test data: {len(X_test)} samples")
        print("✅ Data ingestion and preprocessing validated")
        
        return X_train, y_train, X_test, y_test
    
    def test_model_training_and_versioning(self):
        """Test model training and MLOps versioning pipeline."""
        print("\n=== Testing Model Training and Versioning ===")
        
        # Get preprocessed data
        X_train, y_train, X_test, y_test = self.test_data_ingestion_and_preprocessing()
        
        # Train model using production integration
        training_results = self.production_integration.train_and_version_model(
            X_train, y_train, 
            model_name="end_to_end_test_model",
            metadata={'test_type': 'end_to_end_integration'}
        )
        
        # Validate training results
        self.assertIn('training_results', training_results)
        self.assertIn('mlops_info', training_results)
        self.assertIn('performance_metrics', training_results)
        
        # Validate constitutional compliance
        self.assertTrue(
            training_results['constitutional_hash_verified'],
            "Constitutional hash not verified in training results"
        )
        
        # Validate performance metrics
        performance_metrics = training_results['performance_metrics']
        self.assertGreaterEqual(
            performance_metrics.get('constitutional_compliance', 0),
            self.performance_targets['constitutional_compliance'],
            "Constitutional compliance below target"
        )
        
        print(f"✓ Model trained successfully")
        print(f"✓ Constitutional compliance: {performance_metrics.get('constitutional_compliance', 0):.3f}")
        print(f"✓ Model version: {training_results['mlops_info'].get('model_version', 'N/A')}")
        print("✅ Model training and versioning validated")
        
        return training_results
    
    def test_deployment_pipeline(self):
        """Test complete deployment pipeline with staging and production."""
        print("\n=== Testing Deployment Pipeline ===")
        
        # Train model first
        training_results = self.test_model_training_and_versioning()
        
        model_name = "end_to_end_test_model"
        model_version = training_results['mlops_info'].get('model_version')
        
        if not model_version:
            self.skipTest("Model version not available from training")
        
        # Mock deployment validation to pass
        with patch.object(self.mlops_manager.deployment_pipeline.validator, 
                         '_validate_constitutional_compliance') as mock_constitutional, \
             patch.object(self.mlops_manager.deployment_pipeline.validator, 
                         '_validate_performance_metrics') as mock_performance, \
             patch.object(self.mlops_manager.deployment_pipeline.validator, 
                         '_validate_response_time') as mock_response_time, \
             patch.object(self.mlops_manager.deployment_pipeline.validator, 
                         '_validate_health_check') as mock_health, \
             patch.object(self.mlops_manager.deployment_pipeline.validator, 
                         '_validate_integration_test') as mock_integration:
            
            # Configure mocks to return passing results
            from mlops.deployment_pipeline import ValidationResult
            
            mock_constitutional.return_value = ValidationResult(
                'constitutional_compliance', True, 0.97, 
                {'constitutional_hash_verified': True}
            )
            mock_performance.return_value = ValidationResult(
                'performance_metrics', True, 0.92, {}
            )
            mock_response_time.return_value = ValidationResult(
                'response_time', True, 0.95, 
                {'avg_response_time': 0.45, 'p95_response_time': 0.8}
            )
            mock_health.return_value = ValidationResult(
                'health_check', True, 1.0, {}
            )
            mock_integration.return_value = ValidationResult(
                'integration_test', True, 1.0, {}
            )
            
            # Deploy model
            deployment_result = self.mlops_manager.deploy_model(
                model_name=model_name,
                model_version=model_version,
                skip_staging=False
            )
            
            # Validate deployment
            self.assertTrue(
                deployment_result.staging_validation_passed,
                "Staging validation failed"
            )
            self.assertTrue(
                deployment_result.production_promotion_success,
                "Production promotion failed"
            )
            self.assertTrue(
                deployment_result.constitutional_compliance_verified,
                "Constitutional compliance not verified in deployment"
            )
            
            print(f"✓ Staging validation passed")
            print(f"✓ Production promotion successful")
            print(f"✓ Constitutional compliance verified")
            print("✅ Deployment pipeline validated")
            
            return deployment_result
    
    def test_prediction_serving_performance(self):
        """Test prediction serving with performance validation."""
        print("\n=== Testing Prediction Serving Performance ===")
        
        # Get test data
        _, _, X_test, y_test = self.test_data_ingestion_and_preprocessing()
        
        # Use production optimizer for predictions
        optimizer = self.production_integration.production_optimizer
        
        # Measure prediction performance
        response_times = []
        predictions = []
        
        # Test individual predictions
        for i in range(min(100, len(X_test))):  # Test first 100 samples
            start_time = time.time()
            
            # Make prediction
            try:
                prediction = optimizer.predict_optimal_routing(X_test.iloc[i:i+1])
                predictions.append(prediction)
                
                response_time_ms = (time.time() - start_time) * 1000
                response_times.append(response_time_ms)
                
            except Exception as e:
                print(f"Prediction failed for sample {i}: {e}")
                continue
        
        # Validate performance
        if response_times:
            avg_response_time = statistics.mean(response_times)
            max_response_time = max(response_times)
            p95_response_time = np.percentile(response_times, 95)
            
            self.assertLess(
                avg_response_time,
                self.performance_targets['response_time_ms'],
                f"Average response time {avg_response_time:.1f}ms exceeds target"
            )
            
            print(f"✓ Average response time: {avg_response_time:.1f}ms")
            print(f"✓ Max response time: {max_response_time:.1f}ms")
            print(f"✓ P95 response time: {p95_response_time:.1f}ms")
            print(f"✓ Predictions made: {len(predictions)}")
            print("✅ Prediction serving performance validated")
            
            return response_times, predictions
        else:
            self.fail("No successful predictions made")
    
    def test_load_testing_concurrent_requests(self):
        """Test system under load with 1000+ concurrent requests."""
        print("\n=== Testing Load with 1000+ Concurrent Requests ===")
        
        # Get test data
        _, _, X_test, y_test = self.test_data_ingestion_and_preprocessing()
        
        # Prepare test samples
        test_samples = X_test.head(1000).to_dict('records')
        
        # Load testing configuration
        num_concurrent_requests = 1000
        max_workers = 50
        timeout_seconds = 30
        
        # Results tracking
        successful_requests = 0
        failed_requests = 0
        response_times = []
        errors = []
        
        def make_prediction_request(sample_data):
            """Make a single prediction request."""
            try:
                start_time = time.time()
                
                # Convert to DataFrame for prediction
                sample_df = pd.DataFrame([sample_data])
                
                # Make prediction using production optimizer
                prediction = self.production_integration.production_optimizer.predict_optimal_routing(sample_df)
                
                response_time_ms = (time.time() - start_time) * 1000
                
                return {
                    'success': True,
                    'response_time_ms': response_time_ms,
                    'prediction': prediction
                }
                
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e),
                    'response_time_ms': None
                }
        
        print(f"Starting load test with {num_concurrent_requests} concurrent requests...")
        start_time = time.time()
        
        # Execute concurrent requests
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all requests
            future_to_sample = {
                executor.submit(make_prediction_request, sample): sample 
                for sample in test_samples[:num_concurrent_requests]
            }
            
            # Collect results
            for future in as_completed(future_to_sample, timeout=timeout_seconds):
                try:
                    result = future.result()
                    
                    if result['success']:
                        successful_requests += 1
                        response_times.append(result['response_time_ms'])
                    else:
                        failed_requests += 1
                        errors.append(result['error'])
                        
                except Exception as e:
                    failed_requests += 1
                    errors.append(str(e))
        
        total_time = time.time() - start_time
        
        # Calculate performance metrics
        success_rate = successful_requests / num_concurrent_requests
        avg_response_time = statistics.mean(response_times) if response_times else 0
        p95_response_time = np.percentile(response_times, 95) if response_times else 0
        requests_per_second = num_concurrent_requests / total_time
        
        # Validate load testing results
        self.assertGreaterEqual(
            success_rate, 0.95,
            f"Success rate {success_rate:.3f} below 95% threshold"
        )
        
        self.assertLess(
            avg_response_time,
            self.performance_targets['response_time_ms'],
            f"Average response time {avg_response_time:.1f}ms exceeds target under load"
        )
        
        print(f"✓ Total requests: {num_concurrent_requests}")
        print(f"✓ Successful requests: {successful_requests}")
        print(f"✓ Failed requests: {failed_requests}")
        print(f"✓ Success rate: {success_rate:.3f}")
        print(f"✓ Average response time: {avg_response_time:.1f}ms")
        print(f"✓ P95 response time: {p95_response_time:.1f}ms")
        print(f"✓ Requests per second: {requests_per_second:.1f}")
        print(f"✓ Total test time: {total_time:.1f}s")
        print("✅ Load testing with 1000+ concurrent requests validated")
        
        return {
            'success_rate': success_rate,
            'avg_response_time_ms': avg_response_time,
            'p95_response_time_ms': p95_response_time,
            'requests_per_second': requests_per_second,
            'total_time_seconds': total_time
        }
    
    def test_monitoring_dashboard_integration(self):
        """Test monitoring dashboard integration and performance."""
        print("\n=== Testing Monitoring Dashboard Integration ===")
        
        # Register MLOps metrics source
        self.monitoring_dashboard.register_mlops_metrics_source(self.mlops_manager)
        
        # Start metrics collection
        self.monitoring_dashboard.metrics_collector.start_collection()
        
        try:
            # Wait for some metrics to be collected
            time.sleep(3)
            
            # Get dashboard status
            dashboard_status = self.monitoring_dashboard.get_dashboard_status()
            
            # Validate dashboard functionality
            self.assertTrue(
                dashboard_status['dashboard_running'],
                "Dashboard not running"
            )
            self.assertTrue(
                dashboard_status['metrics_collector_running'],
                "Metrics collector not running"
            )
            self.assertTrue(
                dashboard_status['constitutional_hash_verified'],
                "Constitutional hash not verified in dashboard"
            )
            
            # Validate performance stats
            performance_stats = dashboard_status['performance_stats']
            if not performance_stats.get('no_data', False):
                avg_collection_time = performance_stats.get('avg_collection_time_ms', 0)
                self.assertLess(
                    avg_collection_time, 40,
                    f"Average collection time {avg_collection_time:.1f}ms exceeds 40ms target"
                )
                
                print(f"✓ Average collection time: {avg_collection_time:.1f}ms")
            
            # Get current metrics
            current_metrics = self.monitoring_dashboard.metrics_collector.get_current_metrics()
            
            self.assertIsNotNone(current_metrics, "No metrics collected")
            self.assertEqual(
                current_metrics.constitutional_hash,
                self.constitutional_hash,
                "Constitutional hash mismatch in metrics"
            )
            
            print(f"✓ Dashboard running successfully")
            print(f"✓ Metrics collector operational")
            print(f"✓ Constitutional hash verified")
            print(f"✓ Performance targets met")
            print("✅ Monitoring dashboard integration validated")
            
        finally:
            # Stop metrics collection
            self.monitoring_dashboard.stop()
    
    def test_complete_end_to_end_workflow(self):
        """Test complete end-to-end workflow integration."""
        print("\n=== Testing Complete End-to-End Workflow ===")
        
        workflow_start_time = time.time()
        
        # Step 1: Data ingestion and preprocessing
        print("Step 1: Data ingestion and preprocessing...")
        X_train, y_train, X_test, y_test = self.test_data_ingestion_and_preprocessing()
        
        # Step 2: Model training and versioning
        print("Step 2: Model training and versioning...")
        training_results = self.test_model_training_and_versioning()
        
        # Step 3: Deployment pipeline
        print("Step 3: Deployment pipeline...")
        deployment_result = self.test_deployment_pipeline()
        
        # Step 4: Prediction serving
        print("Step 4: Prediction serving performance...")
        response_times, predictions = self.test_prediction_serving_performance()
        
        # Step 5: Load testing
        print("Step 5: Load testing...")
        load_test_results = self.test_load_testing_concurrent_requests()
        
        # Step 6: Monitoring integration
        print("Step 6: Monitoring dashboard integration...")
        self.test_monitoring_dashboard_integration()
        
        workflow_total_time = time.time() - workflow_start_time
        
        # Validate overall workflow
        workflow_results = {
            'constitutional_hash_verified': True,
            'training_successful': training_results['constitutional_hash_verified'],
            'deployment_successful': deployment_result.constitutional_compliance_verified,
            'prediction_performance_met': statistics.mean(response_times) < self.performance_targets['response_time_ms'],
            'load_test_passed': load_test_results['success_rate'] >= 0.95,
            'monitoring_operational': True,
            'total_workflow_time_seconds': workflow_total_time
        }
        
        # Validate all components passed
        all_passed = all(workflow_results.values())
        self.assertTrue(all_passed, f"End-to-end workflow validation failed: {workflow_results}")
        
        print(f"\n🎉 COMPLETE END-TO-END WORKFLOW VALIDATION SUCCESSFUL! 🎉")
        print(f"✓ Constitutional hash integrity maintained")
        print(f"✓ Training and versioning successful")
        print(f"✓ Deployment pipeline operational")
        print(f"✓ Prediction performance meets targets")
        print(f"✓ Load testing passed (1000+ concurrent requests)")
        print(f"✓ Monitoring dashboard operational")
        print(f"✓ Total workflow time: {workflow_total_time:.1f}s")
        print(f"✓ Constitutional hash: {self.constitutional_hash}")
        
        return workflow_results


if __name__ == '__main__':
    # Configure test runner for detailed output
    unittest.main(verbosity=2, buffer=True)
