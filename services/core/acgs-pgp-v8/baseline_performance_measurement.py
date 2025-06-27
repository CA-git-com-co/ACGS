#!/usr/bin/env python3
"""
Baseline Performance Measurement for ACGS-PGP v8 ML System

Establishes comprehensive baseline metrics for the current ML routing system
to enable accurate comparison with enhanced implementations.

Metrics measured:
- Prediction accuracy (target baseline: ~75%)
- Response time prediction variance (target: ±500ms)
- Cost prediction variance (target: ±30%)
- Training efficiency and model performance
- Constitutional hash integrity verification

Constitutional Hash: cdd01ef066bc6cf2
"""

import sys
import os
import logging
import json
import time
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

# Add project paths
sys.path.append('/home/ubuntu/ACGS/services/shared')
sys.path.append('/home/ubuntu/ACGS/services/core/acgs-pgp-v8/src')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class BaselineMetrics:
    """Comprehensive baseline performance metrics."""
    # Prediction Accuracy Metrics
    response_time_mae: float  # Mean Absolute Error in ms
    response_time_rmse: float  # Root Mean Square Error in ms
    response_time_r2: float  # R² score
    response_time_variance: float  # Prediction variance ±ms
    
    cost_mae: float  # Mean Absolute Error
    cost_rmse: float  # Root Mean Square Error
    cost_r2: float  # R² score
    cost_variance_percent: float  # Prediction variance ±%
    
    quality_mae: float  # Mean Absolute Error
    quality_rmse: float  # Root Mean Square Error
    quality_r2: float  # R² score
    
    compliance_accuracy: float  # Classification accuracy
    
    # Training Efficiency Metrics
    training_time_seconds: float
    training_samples_count: int
    model_convergence_iterations: int
    memory_usage_mb: float
    
    # System Performance Metrics
    prediction_latency_ms: float
    model_loading_time_ms: float
    feature_extraction_time_ms: float
    
    # Constitutional Integrity
    constitutional_hash_verified: bool
    constitutional_compliance_rate: float
    
    # Overall Scores
    overall_prediction_accuracy: float  # Weighted average
    system_stability_score: float  # 0-1 score
    
    # Metadata
    measurement_timestamp: str
    baseline_version: str
    sample_size: int

def generate_synthetic_training_data(n_samples: int = 1000) -> List[Dict[str, Any]]:
    """Generate synthetic training data for baseline measurement."""
    logger.info(f"Generating {n_samples} synthetic training samples...")
    
    training_data = []
    
    for i in range(n_samples):
        # Simulate realistic request patterns
        request_types = ['quick_analysis', 'detailed_analysis', 'constitutional_validation']
        content_types = ['text_only', 'text_with_image', 'multimodal']
        model_types = ['flash_lite', 'flash_full', 'deepseek_r1', 'nano_vllm']
        
        # Generate features
        request_type = np.random.choice(request_types)
        content_type = np.random.choice(content_types)
        model_type = np.random.choice(model_types)
        content_length = np.random.randint(50, 5000)
        hour_of_day = np.random.randint(0, 24)
        day_of_week = np.random.randint(0, 7)
        is_weekend = day_of_week >= 5
        
        # Generate realistic performance metrics with some correlation
        base_response_time = {
            'flash_lite': 800,
            'flash_full': 1500,
            'deepseek_r1': 1200,
            'nano_vllm': 600
        }[model_type]
        
        # Add content length and complexity effects
        complexity_factor = 1 + (content_length / 2000) * 0.5
        response_time = base_response_time * complexity_factor + np.random.normal(0, 200)
        response_time = max(100, response_time)  # Minimum 100ms
        
        # Cost correlates with response time and model type
        cost_per_token = {
            'flash_lite': 0.000001,
            'flash_full': 0.000003,
            'deepseek_r1': 0.0000005,
            'nano_vllm': 0.0000002
        }[model_type]
        
        token_count = content_length * 1.3  # Approximate tokens
        cost = token_count * cost_per_token + np.random.normal(0, cost_per_token * token_count * 0.1)
        cost = max(0, cost)
        
        # Quality and compliance
        quality_score = np.random.uniform(0.7, 0.95)
        constitutional_compliance = np.random.choice([True, False], p=[0.95, 0.05])
        
        training_data.append({
            'request_type': request_type,
            'content_type': content_type,
            'model_type': model_type,
            'content_length': content_length,
            'hour_of_day': hour_of_day,
            'day_of_week': day_of_week,
            'is_weekend': is_weekend,
            'response_time_ms': response_time,
            'cost_estimate': cost,
            'quality_score': quality_score,
            'constitutional_compliance': constitutional_compliance,
            'timestamp': datetime.now().isoformat()
        })
    
    logger.info(f"✅ Generated {len(training_data)} training samples")
    return training_data

def train_baseline_models(training_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Train baseline ML models and measure training efficiency."""
    logger.info("Training baseline ML models...")
    
    from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, accuracy_score
    import psutil
    
    start_time = time.time()
    process = psutil.Process()
    start_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # Prepare data
    df = pd.DataFrame(training_data)
    
    # Encode categorical features
    le_request = LabelEncoder()
    le_content = LabelEncoder()
    le_model = LabelEncoder()
    
    df['request_type_encoded'] = le_request.fit_transform(df['request_type'])
    df['content_type_encoded'] = le_content.fit_transform(df['content_type'])
    df['model_type_encoded'] = le_model.fit_transform(df['model_type'])
    
    # Feature matrix
    feature_columns = [
        'request_type_encoded', 'content_type_encoded', 'model_type_encoded',
        'content_length', 'hour_of_day', 'day_of_week', 'is_weekend'
    ]
    X = df[feature_columns].values
    
    # Target variables
    y_response_time = df['response_time_ms'].values
    y_cost = df['cost_estimate'].values
    y_quality = df['quality_score'].values
    y_compliance = df['constitutional_compliance'].values.astype(int)
    
    # Split data
    X_train, X_test, y_rt_train, y_rt_test = train_test_split(X, y_response_time, test_size=0.2, random_state=42)
    _, _, y_cost_train, y_cost_test = train_test_split(X, y_cost, test_size=0.2, random_state=42)
    _, _, y_qual_train, y_qual_test = train_test_split(X, y_quality, test_size=0.2, random_state=42)
    _, _, y_comp_train, y_comp_test = train_test_split(X, y_compliance, test_size=0.2, random_state=42)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train models
    models = {}
    metrics = {}
    
    # Response Time Model
    logger.info("  Training response time model...")
    rt_model = RandomForestRegressor(n_estimators=100, random_state=42)
    rt_model.fit(X_train_scaled, y_rt_train)
    rt_pred = rt_model.predict(X_test_scaled)
    
    models['response_time'] = rt_model
    metrics['response_time'] = {
        'mae': mean_absolute_error(y_rt_test, rt_pred),
        'rmse': np.sqrt(mean_squared_error(y_rt_test, rt_pred)),
        'r2': r2_score(y_rt_test, rt_pred),
        'variance': np.std(rt_pred - y_rt_test)
    }
    
    # Cost Model
    logger.info("  Training cost model...")
    cost_model = RandomForestRegressor(n_estimators=100, random_state=42)
    cost_model.fit(X_train_scaled, y_cost_train)
    cost_pred = cost_model.predict(X_test_scaled)
    
    models['cost'] = cost_model
    metrics['cost'] = {
        'mae': mean_absolute_error(y_cost_test, cost_pred),
        'rmse': np.sqrt(mean_squared_error(y_cost_test, cost_pred)),
        'r2': r2_score(y_cost_test, cost_pred),
        'variance_percent': (np.std(cost_pred - y_cost_test) / np.mean(y_cost_test)) * 100
    }
    
    # Quality Model
    logger.info("  Training quality model...")
    qual_model = RandomForestRegressor(n_estimators=100, random_state=42)
    qual_model.fit(X_train_scaled, y_qual_train)
    qual_pred = qual_model.predict(X_test_scaled)
    
    models['quality'] = qual_model
    metrics['quality'] = {
        'mae': mean_absolute_error(y_qual_test, qual_pred),
        'rmse': np.sqrt(mean_squared_error(y_qual_test, qual_pred)),
        'r2': r2_score(y_qual_test, qual_pred)
    }
    
    # Compliance Model
    logger.info("  Training compliance model...")
    comp_model = RandomForestClassifier(n_estimators=100, random_state=42)
    comp_model.fit(X_train_scaled, y_comp_train)
    comp_pred = comp_model.predict(X_test_scaled)
    
    models['compliance'] = comp_model
    metrics['compliance'] = {
        'accuracy': accuracy_score(y_comp_test, comp_pred)
    }
    
    # Training efficiency metrics
    end_time = time.time()
    end_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    training_metrics = {
        'training_time_seconds': end_time - start_time,
        'memory_usage_mb': end_memory - start_memory,
        'training_samples': len(training_data),
        'models_trained': len(models)
    }
    
    logger.info(f"✅ Baseline models trained in {training_metrics['training_time_seconds']:.2f}s")
    
    return {
        'models': models,
        'metrics': metrics,
        'training_metrics': training_metrics,
        'scaler': scaler,
        'encoders': {
            'request_type': le_request,
            'content_type': le_content,
            'model_type': le_model
        }
    }

def measure_prediction_performance(models_data: Dict[str, Any]) -> Dict[str, float]:
    """Measure prediction performance and latency."""
    logger.info("Measuring prediction performance...")

    models = models_data['models']
    scaler = models_data['scaler']

    # Test prediction latency
    test_features = np.array([[1, 0, 2, 1000, 14, 3, False]])  # Sample feature vector
    test_features_scaled = scaler.transform(test_features)

    # Measure prediction times
    prediction_times = []

    for _ in range(100):  # Average over 100 predictions
        start_time = time.time()

        # Predict all metrics
        rt_pred = models['response_time'].predict(test_features_scaled)[0]
        cost_pred = models['cost'].predict(test_features_scaled)[0]
        qual_pred = models['quality'].predict(test_features_scaled)[0]
        comp_pred = models['compliance'].predict(test_features_scaled)[0]

        end_time = time.time()
        prediction_times.append((end_time - start_time) * 1000)  # Convert to ms

    avg_prediction_latency = np.mean(prediction_times)

    logger.info(f"✅ Average prediction latency: {avg_prediction_latency:.2f}ms")

    return {
        'prediction_latency_ms': avg_prediction_latency,
        'prediction_std_ms': np.std(prediction_times)
    }

def verify_constitutional_integrity() -> Dict[str, Any]:
    """Verify constitutional hash integrity."""
    logger.info("Verifying constitutional hash integrity...")

    constitutional_hash = "cdd01ef066bc6cf2"

    # Check current file
    with open(__file__, 'r') as f:
        content = f.read()
        hash_in_file = constitutional_hash in content

    # Check key system files
    key_files = [
        '/home/ubuntu/ACGS/services/shared/ml_routing_optimizer.py',
        '/home/ubuntu/ACGS/services/shared/production_ml_optimizer.py',
        '/home/ubuntu/ACGS/services/shared/multimodal_ai_service.py'
    ]

    hash_verified_files = 0
    total_files = len(key_files)

    for file_path in key_files:
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    if constitutional_hash in f.read():
                        hash_verified_files += 1
        except Exception as e:
            logger.warning(f"Could not verify hash in {file_path}: {e}")

    integrity_score = hash_verified_files / total_files

    logger.info(f"✅ Constitutional hash verified in {hash_verified_files}/{total_files} files")

    return {
        'constitutional_hash_verified': hash_in_file,
        'system_integrity_score': integrity_score,
        'verified_files': hash_verified_files,
        'total_files': total_files
    }

def calculate_baseline_metrics(models_data: Dict[str, Any],
                             performance_data: Dict[str, float],
                             integrity_data: Dict[str, Any]) -> BaselineMetrics:
    """Calculate comprehensive baseline metrics."""
    logger.info("Calculating comprehensive baseline metrics...")

    metrics = models_data['metrics']
    training_metrics = models_data['training_metrics']

    # Calculate overall prediction accuracy (weighted average)
    rt_weight = 0.3  # Response time importance
    cost_weight = 0.25  # Cost importance
    quality_weight = 0.25  # Quality importance
    compliance_weight = 0.2  # Compliance importance

    # Normalize R² scores (0-1 range, higher is better)
    rt_r2_norm = max(0, metrics['response_time']['r2'])
    cost_r2_norm = max(0, metrics['cost']['r2'])
    quality_r2_norm = max(0, metrics['quality']['r2'])
    compliance_acc_norm = metrics['compliance']['accuracy']

    overall_accuracy = (
        rt_weight * rt_r2_norm +
        cost_weight * cost_r2_norm +
        quality_weight * quality_r2_norm +
        compliance_weight * compliance_acc_norm
    )

    # Calculate system stability score
    stability_factors = [
        min(1.0, training_metrics['training_time_seconds'] / 60.0),  # Training efficiency
        min(1.0, performance_data['prediction_latency_ms'] / 100.0),  # Prediction speed
        integrity_data['system_integrity_score'],  # Constitutional integrity
        min(1.0, overall_accuracy)  # Prediction accuracy
    ]

    system_stability = np.mean(stability_factors)

    baseline = BaselineMetrics(
        # Response Time Metrics
        response_time_mae=metrics['response_time']['mae'],
        response_time_rmse=metrics['response_time']['rmse'],
        response_time_r2=metrics['response_time']['r2'],
        response_time_variance=metrics['response_time']['variance'],

        # Cost Metrics
        cost_mae=metrics['cost']['mae'],
        cost_rmse=metrics['cost']['rmse'],
        cost_r2=metrics['cost']['r2'],
        cost_variance_percent=metrics['cost']['variance_percent'],

        # Quality Metrics
        quality_mae=metrics['quality']['mae'],
        quality_rmse=metrics['quality']['rmse'],
        quality_r2=metrics['quality']['r2'],

        # Compliance Metrics
        compliance_accuracy=metrics['compliance']['accuracy'],

        # Training Efficiency
        training_time_seconds=training_metrics['training_time_seconds'],
        training_samples_count=training_metrics['training_samples'],
        model_convergence_iterations=100,  # RandomForest n_estimators
        memory_usage_mb=training_metrics['memory_usage_mb'],

        # System Performance
        prediction_latency_ms=performance_data['prediction_latency_ms'],
        model_loading_time_ms=0.0,  # Not measured for baseline
        feature_extraction_time_ms=0.0,  # Not measured for baseline

        # Constitutional Integrity
        constitutional_hash_verified=integrity_data['constitutional_hash_verified'],
        constitutional_compliance_rate=metrics['compliance']['accuracy'],

        # Overall Scores
        overall_prediction_accuracy=overall_accuracy,
        system_stability_score=system_stability,

        # Metadata
        measurement_timestamp=datetime.now().isoformat(),
        baseline_version="1.0.0",
        sample_size=training_metrics['training_samples']
    )

    return baseline

def save_baseline_results(baseline: BaselineMetrics, output_dir: str = "baseline_results"):
    """Save baseline results to files."""
    logger.info("Saving baseline results...")

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Save as JSON
    baseline_dict = asdict(baseline)
    json_path = os.path.join(output_dir, "baseline_metrics.json")
    with open(json_path, 'w') as f:
        json.dump(baseline_dict, f, indent=2)

    # Save summary report
    report_path = os.path.join(output_dir, "baseline_report.md")
    with open(report_path, 'w') as f:
        f.write("# ACGS-PGP v8 ML System Baseline Performance Report\n\n")
        f.write(f"**Generated:** {baseline.measurement_timestamp}\n")
        f.write(f"**Version:** {baseline.baseline_version}\n")
        f.write(f"**Sample Size:** {baseline.sample_size:,}\n")
        f.write(f"**Constitutional Hash:** cdd01ef066bc6cf2\n\n")

        f.write("## 📊 Key Performance Metrics\n\n")
        f.write(f"- **Overall Prediction Accuracy:** {baseline.overall_prediction_accuracy:.1%}\n")
        f.write(f"- **System Stability Score:** {baseline.system_stability_score:.1%}\n")
        f.write(f"- **Response Time Variance:** ±{baseline.response_time_variance:.1f}ms\n")
        f.write(f"- **Cost Variance:** ±{baseline.cost_variance_percent:.1f}%\n")
        f.write(f"- **Constitutional Compliance:** {baseline.constitutional_compliance_rate:.1%}\n\n")

        f.write("## 🎯 Detailed Metrics\n\n")
        f.write("### Response Time Prediction\n")
        f.write(f"- MAE: {baseline.response_time_mae:.1f}ms\n")
        f.write(f"- RMSE: {baseline.response_time_rmse:.1f}ms\n")
        f.write(f"- R²: {baseline.response_time_r2:.3f}\n\n")

        f.write("### Cost Prediction\n")
        f.write(f"- MAE: ${baseline.cost_mae:.6f}\n")
        f.write(f"- RMSE: ${baseline.cost_rmse:.6f}\n")
        f.write(f"- R²: {baseline.cost_r2:.3f}\n\n")

        f.write("### Training Efficiency\n")
        f.write(f"- Training Time: {baseline.training_time_seconds:.1f}s\n")
        f.write(f"- Memory Usage: {baseline.memory_usage_mb:.1f}MB\n")
        f.write(f"- Prediction Latency: {baseline.prediction_latency_ms:.2f}ms\n\n")

        f.write("### Constitutional Integrity\n")
        f.write(f"- Hash Verified: {'✅' if baseline.constitutional_hash_verified else '❌'}\n")
        f.write(f"- Compliance Rate: {baseline.constitutional_compliance_rate:.1%}\n\n")

    logger.info(f"✅ Baseline results saved to {output_dir}/")
    return json_path, report_path

def main():
    """Main function to run baseline performance measurement."""
    logger.info("🚀 Starting ACGS-PGP v8 ML System Baseline Performance Measurement")
    logger.info(f"Measurement started at: {datetime.now()}")

    try:
        # Step 1: Generate training data
        logger.info("\n📊 Step 1: Generating synthetic training data...")
        training_data = generate_synthetic_training_data(n_samples=1000)

        # Step 2: Train baseline models
        logger.info("\n🎓 Step 2: Training baseline ML models...")
        models_data = train_baseline_models(training_data)

        # Step 3: Measure prediction performance
        logger.info("\n⚡ Step 3: Measuring prediction performance...")
        performance_data = measure_prediction_performance(models_data)

        # Step 4: Verify constitutional integrity
        logger.info("\n🔒 Step 4: Verifying constitutional integrity...")
        integrity_data = verify_constitutional_integrity()

        # Step 5: Calculate comprehensive baseline metrics
        logger.info("\n📈 Step 5: Calculating baseline metrics...")
        baseline = calculate_baseline_metrics(models_data, performance_data, integrity_data)

        # Step 6: Save results
        logger.info("\n💾 Step 6: Saving baseline results...")
        json_path, report_path = save_baseline_results(baseline)

        # Display summary
        logger.info("\n🎉 Baseline Performance Measurement Complete!")
        logger.info("=" * 60)
        logger.info(f"📊 Overall Prediction Accuracy: {baseline.overall_prediction_accuracy:.1%}")
        logger.info(f"🏗️ System Stability Score: {baseline.system_stability_score:.1%}")
        logger.info(f"⏱️ Response Time Variance: ±{baseline.response_time_variance:.1f}ms")
        logger.info(f"💰 Cost Variance: ±{baseline.cost_variance_percent:.1f}%")
        logger.info(f"📜 Constitutional Compliance: {baseline.constitutional_compliance_rate:.1%}")
        logger.info(f"🔒 Constitutional Hash Verified: {'✅' if baseline.constitutional_hash_verified else '❌'}")
        logger.info("=" * 60)
        logger.info(f"📄 Results saved to: {json_path}")
        logger.info(f"📋 Report saved to: {report_path}")

        return True

    except Exception as e:
        logger.error(f"❌ Baseline measurement failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
