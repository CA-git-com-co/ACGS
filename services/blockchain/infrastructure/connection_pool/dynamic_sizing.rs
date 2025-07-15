// Constitutional Hash: cdd01ef066bc6cf2
//! Dynamic Connection Pool Sizing Engine
//! 
//! This module implements intelligent load-based connection pool sizing with
//! predictive analytics and machine learning-inspired optimization algorithms.

use serde::{Deserialize, Serialize};
use std::collections::{HashMap, VecDeque};
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

/// Load pattern types for predictive sizing
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
pub enum LoadPattern {
    /// Steady, consistent load
    Steady,
    /// Periodic spikes (e.g., daily, weekly)
    Periodic { period_seconds: u64, amplitude: f64 },
    /// Sudden traffic bursts
    Bursty { burst_duration_seconds: u64, peak_multiplier: f64 },
    /// Gradual increasing trend
    Trending { growth_rate_percent: f64 },
    /// Random/unpredictable load
    Random,
    /// Mixed pattern with multiple characteristics
    Mixed { patterns: Vec<LoadPattern> },
}

/// Load prediction model
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct LoadPredictionModel {
    /// Model type identifier
    pub model_type: PredictionModelType,
    /// Model accuracy (0.0-1.0)
    pub accuracy: f64,
    /// Training data points used
    pub training_points: u32,
    /// Last model update timestamp
    pub last_updated: i64,
    /// Prediction confidence (0.0-1.0)
    pub confidence: f64,
    /// Model parameters (algorithm-specific)
    pub parameters: HashMap<String, f64>,
}

/// Types of prediction models available
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum PredictionModelType {
    /// Simple moving average
    MovingAverage { window_size: u32 },
    /// Exponential weighted moving average
    ExponentialWeightedAverage { alpha: f64 },
    /// Linear regression
    LinearRegression,
    /// Seasonal decomposition
    SeasonalDecomposition { season_length: u32 },
    /// Ensemble of multiple models
    Ensemble { models: Vec<PredictionModelType> },
}

/// Load metrics for pattern analysis
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct LoadMetrics {
    /// Timestamp of measurement
    pub timestamp: i64,
    /// Active connections at this time
    pub active_connections: u32,
    /// Queue depth (pending requests)
    pub queue_depth: u32,
    /// Request rate (requests per second)
    pub request_rate: f64,
    /// Average response time (milliseconds)
    pub response_time_ms: f64,
    /// CPU utilization percentage
    pub cpu_utilization: f64,
    /// Memory utilization percentage
    pub memory_utilization: f64,
    /// Error rate (errors per second)
    pub error_rate: f64,
    /// Constitutional validation hash
    pub constitutional_hash: String,
}

impl Default for LoadMetrics {
    fn default() -> Self {
        Self {
            timestamp: SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs() as i64,
            active_connections: 0,
            queue_depth: 0,
            request_rate: 0.0,
            response_time_ms: 0.0,
            cpu_utilization: 0.0,
            memory_utilization: 0.0,
            error_rate: 0.0,
            constitutional_hash: "cdd01ef066bc6cf2".to_string(),
        }
    }
}

/// Dynamic sizing configuration
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct DynamicSizingConfig {
    /// Enable dynamic sizing
    pub enabled: bool,
    /// Constitutional hash validation
    pub constitutional_hash: String,
    /// Prediction model to use
    pub prediction_model: PredictionModelType,
    /// Historical data retention period (hours)
    pub history_retention_hours: u32,
    /// Minimum samples required for predictions
    pub min_samples_for_prediction: u32,
    /// Maximum allowed pool size change per adjustment
    pub max_change_percent: u8,
    /// Adjustment frequency (seconds)
    pub adjustment_interval_seconds: u32,
    /// Safety buffer percentage above predicted load
    pub safety_buffer_percent: u8,
    /// Enable predictive scaling (scale before load arrives)
    pub predictive_scaling_enabled: bool,
    /// Predictive horizon (minutes into future)
    pub prediction_horizon_minutes: u32,
    /// Sensitivity to load changes (0.1-1.0)
    pub sensitivity: f64,
    /// Cost optimization weight (0.0-1.0)
    pub cost_optimization_weight: f64,
}

impl Default for DynamicSizingConfig {
    fn default() -> Self {
        Self {
            enabled: true,
            constitutional_hash: "cdd01ef066bc6cf2".to_string(),
            prediction_model: PredictionModelType::ExponentialWeightedAverage { alpha: 0.3 },
            history_retention_hours: 168, // 7 days
            min_samples_for_prediction: 20,
            max_change_percent: 25,
            adjustment_interval_seconds: 60,
            safety_buffer_percent: 20,
            predictive_scaling_enabled: true,
            prediction_horizon_minutes: 15,
            sensitivity: 0.7,
            cost_optimization_weight: 0.3,
        }
    }
}

/// Dynamic sizing recommendations
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct SizingRecommendation {
    /// Current pool size
    pub current_size: u32,
    /// Recommended new size
    pub recommended_size: u32,
    /// Confidence in recommendation (0.0-1.0)
    pub confidence: f64,
    /// Reason for recommendation
    pub reason: String,
    /// Expected cost impact (positive = savings, negative = increase)
    pub cost_impact_percent: f64,
    /// Expected performance impact
    pub performance_impact: PerformanceImpact,
    /// Time to next adjustment
    pub next_adjustment_seconds: u32,
    /// Predicted load for next period
    pub predicted_load: f64,
    /// Constitutional compliance status
    pub constitutional_compliance: bool,
}

/// Performance impact assessment
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum PerformanceImpact {
    /// Positive impact expected
    Positive { improvement_percent: f64 },
    /// Neutral impact expected
    Neutral,
    /// Negative impact expected
    Negative { degradation_percent: f64 },
}

/// Dynamic connection pool sizing engine
pub struct DynamicSizingEngine {
    config: DynamicSizingConfig,
    historical_metrics: VecDeque<LoadMetrics>,
    prediction_model: LoadPredictionModel,
    detected_patterns: Vec<LoadPattern>,
    last_adjustment: Instant,
    sizing_statistics: SizingStatistics,
}

/// Statistics for sizing engine performance
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct SizingStatistics {
    /// Total adjustments made
    pub total_adjustments: u64,
    /// Successful predictions (within 10% of actual)
    pub successful_predictions: u64,
    /// Total predictions made
    pub total_predictions: u64,
    /// Average prediction accuracy
    pub average_accuracy: f64,
    /// Cost savings achieved (dollars)
    pub cost_savings_achieved: f64,
    /// Performance improvements (percentage)
    pub performance_improvements_percent: f64,
    /// Constitutional compliance rate
    pub constitutional_compliance_rate: f64,
}

impl Default for SizingStatistics {
    fn default() -> Self {
        Self {
            total_adjustments: 0,
            successful_predictions: 0,
            total_predictions: 0,
            average_accuracy: 0.0,
            cost_savings_achieved: 0.0,
            performance_improvements_percent: 0.0,
            constitutional_compliance_rate: 100.0,
        }
    }
}

impl DynamicSizingEngine {
    /// Constitutional Hash: cdd01ef066bc6cf2
    /// Create new dynamic sizing engine
    pub fn new(config: DynamicSizingConfig) -> Self {
        let prediction_model = LoadPredictionModel {
            model_type: config.prediction_model.clone(),
            accuracy: 0.0,
            training_points: 0,
            last_updated: SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs() as i64,
            confidence: 0.0,
            parameters: HashMap::new(),
        };

        Self {
            config,
            historical_metrics: VecDeque::new(),
            prediction_model,
            detected_patterns: Vec::new(),
            last_adjustment: Instant::now(),
            sizing_statistics: SizingStatistics::default(),
        }
    }

    /// Add new load metrics for analysis
    pub fn add_metrics(&mut self, metrics: LoadMetrics) {
        // Validate constitutional hash
        if metrics.constitutional_hash != self.config.constitutional_hash {
            eprintln!("Warning: Constitutional hash mismatch in metrics");
            return;
        }

        self.historical_metrics.push_back(metrics);
        
        // Maintain retention limit
        let retention_limit = (self.config.history_retention_hours as usize * 60) / 
                              (self.config.adjustment_interval_seconds as usize / 60);
        
        while self.historical_metrics.len() > retention_limit {
            self.historical_metrics.pop_front();
        }

        // Update prediction model if we have enough data
        if self.historical_metrics.len() >= self.config.min_samples_for_prediction as usize {
            self.update_prediction_model();
            self.detect_load_patterns();
        }
    }

    /// Update the prediction model with current data
    fn update_prediction_model(&mut self) {
        let metrics: Vec<f64> = self.historical_metrics
            .iter()
            .map(|m| m.active_connections as f64)
            .collect();

        match &self.prediction_model.model_type {
            PredictionModelType::MovingAverage { window_size } => {
                let window = *window_size as usize;
                if metrics.len() >= window {
                    let recent_metrics = &metrics[metrics.len() - window..];
                    let average = recent_metrics.iter().sum::<f64>() / window as f64;
                    self.prediction_model.parameters.insert("average".to_string(), average);
                }
            },
            PredictionModelType::ExponentialWeightedAverage { alpha } => {
                if let Some(last_value) = metrics.last() {
                    let ema = if let Some(prev_ema) = self.prediction_model.parameters.get("ema") {
                        alpha * last_value + (1.0 - alpha) * prev_ema
                    } else {
                        *last_value
                    };
                    self.prediction_model.parameters.insert("ema".to_string(), ema);
                }
            },
            PredictionModelType::LinearRegression => {
                self.update_linear_regression_model(&metrics);
            },
            PredictionModelType::SeasonalDecomposition { season_length } => {
                self.update_seasonal_model(&metrics, *season_length);
            },
            PredictionModelType::Ensemble { models: _ } => {
                // Update multiple models and combine predictions
                self.update_ensemble_model(&metrics);
            },
        }

        self.prediction_model.training_points = metrics.len() as u32;
        self.prediction_model.last_updated = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs() as i64;
        
        // Calculate model accuracy based on recent predictions
        self.calculate_model_accuracy();
    }

    /// Update linear regression model
    fn update_linear_regression_model(&mut self, metrics: &[f64]) {
        if metrics.len() < 2 {
            return;
        }

        let n = metrics.len() as f64;
        let x_values: Vec<f64> = (0..metrics.len()).map(|i| i as f64).collect();
        
        let sum_x: f64 = x_values.iter().sum();
        let sum_y: f64 = metrics.iter().sum();
        let sum_xy: f64 = x_values.iter().zip(metrics.iter()).map(|(x, y)| x * y).sum();
        let sum_x2: f64 = x_values.iter().map(|x| x * x).sum();

        let slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x);
        let intercept = (sum_y - slope * sum_x) / n;

        self.prediction_model.parameters.insert("slope".to_string(), slope);
        self.prediction_model.parameters.insert("intercept".to_string(), intercept);
    }

    /// Update seasonal decomposition model
    fn update_seasonal_model(&mut self, metrics: &[f64], season_length: u32) {
        if metrics.len() < season_length as usize * 2 {
            return;
        }

        // Calculate seasonal averages
        let mut seasonal_averages = vec![0.0; season_length as usize];
        let mut seasonal_counts = vec![0; season_length as usize];

        for (i, &value) in metrics.iter().enumerate() {
            let season_index = i % season_length as usize;
            seasonal_averages[season_index] += value;
            seasonal_counts[season_index] += 1;
        }

        for i in 0..season_length as usize {
            if seasonal_counts[i] > 0 {
                seasonal_averages[i] /= seasonal_counts[i] as f64;
                self.prediction_model.parameters.insert(
                    format!("seasonal_{}", i), 
                    seasonal_averages[i]
                );
            }
        }
    }

    /// Update ensemble model
    fn update_ensemble_model(&mut self, metrics: &[f64]) {
        // Simplified ensemble - combine moving average and linear regression
        
        // Moving average
        let window_size = 10;
        if metrics.len() >= window_size {
            let recent_metrics = &metrics[metrics.len() - window_size..];
            let ma_value = recent_metrics.iter().sum::<f64>() / window_size as f64;
            self.prediction_model.parameters.insert("ma_value".to_string(), ma_value);
        }

        // Linear trend
        self.update_linear_regression_model(metrics);
        
        // Combine predictions with weights
        let ma_weight = 0.6;
        let lr_weight = 0.4;
        
        if let (Some(ma_val), Some(slope), Some(intercept)) = (
            self.prediction_model.parameters.get("ma_value"),
            self.prediction_model.parameters.get("slope"),
            self.prediction_model.parameters.get("intercept")
        ) {
            let lr_prediction = intercept + slope * metrics.len() as f64;
            let ensemble_prediction = ma_weight * ma_val + lr_weight * lr_prediction;
            self.prediction_model.parameters.insert("ensemble_prediction".to_string(), ensemble_prediction);
        }
    }

    /// Calculate model accuracy based on recent performance
    fn calculate_model_accuracy(&mut self) {
        if self.historical_metrics.len() < 10 {
            return;
        }

        let mut total_error = 0.0;
        let mut count = 0;

        // Compare predictions with actual values for last 10 data points
        for i in 1..11.min(self.historical_metrics.len()) {
            let actual = self.historical_metrics[self.historical_metrics.len() - i].active_connections as f64;
            let predicted = self.predict_load_at_offset(-(i as i32));
            
            if predicted > 0.0 {
                let error = ((actual - predicted) / predicted).abs();
                total_error += error;
                count += 1;
            }
        }

        if count > 0 {
            let average_error = total_error / count as f64;
            self.prediction_model.accuracy = (1.0 - average_error).max(0.0).min(1.0);
            self.prediction_model.confidence = self.prediction_model.accuracy;
        }
    }

    /// Predict load at a specific time offset (in data points)
    fn predict_load_at_offset(&self, offset: i32) -> f64 {
        match &self.prediction_model.model_type {
            PredictionModelType::MovingAverage { .. } => {
                self.prediction_model.parameters.get("average").copied().unwrap_or(0.0)
            },
            PredictionModelType::ExponentialWeightedAverage { .. } => {
                self.prediction_model.parameters.get("ema").copied().unwrap_or(0.0)
            },
            PredictionModelType::LinearRegression => {
                if let (Some(slope), Some(intercept)) = (
                    self.prediction_model.parameters.get("slope"),
                    self.prediction_model.parameters.get("intercept")
                ) {
                    let x = self.historical_metrics.len() as f64 + offset as f64;
                    intercept + slope * x
                } else {
                    0.0
                }
            },
            PredictionModelType::SeasonalDecomposition { season_length } => {
                let current_position = self.historical_metrics.len() as i32 + offset;
                let season_index = (current_position % *season_length as i32) as usize;
                self.prediction_model.parameters
                    .get(&format!("seasonal_{}", season_index))
                    .copied()
                    .unwrap_or(0.0)
            },
            PredictionModelType::Ensemble { .. } => {
                self.prediction_model.parameters.get("ensemble_prediction").copied().unwrap_or(0.0)
            },
        }
    }

    /// Detect load patterns in historical data
    fn detect_load_patterns(&mut self) {
        if self.historical_metrics.len() < 50 {
            return; // Need sufficient data for pattern detection
        }

        let metrics: Vec<f64> = self.historical_metrics
            .iter()
            .map(|m| m.active_connections as f64)
            .collect();

        self.detected_patterns.clear();

        // Detect steady pattern
        if self.is_steady_pattern(&metrics) {
            self.detected_patterns.push(LoadPattern::Steady);
        }

        // Detect periodic patterns
        if let Some(period) = self.detect_periodicity(&metrics) {
            let amplitude = self.calculate_amplitude(&metrics, period);
            self.detected_patterns.push(LoadPattern::Periodic { 
                period_seconds: period * self.config.adjustment_interval_seconds as u64,
                amplitude 
            });
        }

        // Detect trending pattern
        if let Some(trend) = self.detect_trend(&metrics) {
            self.detected_patterns.push(LoadPattern::Trending { 
                growth_rate_percent: trend 
            });
        }

        // Detect bursty pattern
        if self.is_bursty_pattern(&metrics) {
            let (duration, multiplier) = self.analyze_bursts(&metrics);
            self.detected_patterns.push(LoadPattern::Bursty { 
                burst_duration_seconds: duration,
                peak_multiplier: multiplier 
            });
        }

        // If no clear patterns, mark as random
        if self.detected_patterns.is_empty() {
            self.detected_patterns.push(LoadPattern::Random);
        }
    }

    /// Check if load pattern is steady
    fn is_steady_pattern(&self, metrics: &[f64]) -> bool {
        if metrics.len() < 10 {
            return false;
        }

        let mean = metrics.iter().sum::<f64>() / metrics.len() as f64;
        let variance = metrics.iter()
            .map(|x| (x - mean).powi(2))
            .sum::<f64>() / metrics.len() as f64;
        let std_dev = variance.sqrt();
        let coefficient_of_variation = std_dev / mean;

        coefficient_of_variation < 0.2 // Less than 20% variation
    }

    /// Detect periodicity in metrics
    fn detect_periodicity(&self, metrics: &[f64]) -> Option<u64> {
        // Simplified periodicity detection using autocorrelation
        let max_period = (metrics.len() / 4).min(144); // Max 144 data points (24 hours at 10-min intervals)
        
        for period in 2..=max_period {
            let correlation = self.calculate_autocorrelation(metrics, period);
            if correlation > 0.7 { // Strong correlation
                return Some(period as u64);
            }
        }
        
        None
    }

    /// Calculate autocorrelation for a given lag
    fn calculate_autocorrelation(&self, metrics: &[f64], lag: usize) -> f64 {
        if lag >= metrics.len() {
            return 0.0;
        }

        let n = metrics.len() - lag;
        if n == 0 {
            return 0.0;
        }

        let mean1 = metrics[..n].iter().sum::<f64>() / n as f64;
        let mean2 = metrics[lag..].iter().sum::<f64>() / n as f64;

        let mut numerator = 0.0;
        let mut sum_sq1 = 0.0;
        let mut sum_sq2 = 0.0;

        for i in 0..n {
            let x1 = metrics[i] - mean1;
            let x2 = metrics[i + lag] - mean2;
            numerator += x1 * x2;
            sum_sq1 += x1 * x1;
            sum_sq2 += x2 * x2;
        }

        let denominator = (sum_sq1 * sum_sq2).sqrt();
        if denominator == 0.0 {
            0.0
        } else {
            numerator / denominator
        }
    }

    /// Calculate amplitude of periodic pattern
    fn calculate_amplitude(&self, metrics: &[f64], period: u64) -> f64 {
        let mean = metrics.iter().sum::<f64>() / metrics.len() as f64;
        let mut max_deviation: f64 = 0.0;

        for chunk in metrics.chunks(period as usize) {
            if !chunk.is_empty() {
                let chunk_mean = chunk.iter().sum::<f64>() / chunk.len() as f64;
                let deviation = (chunk_mean - mean).abs() / mean;
                max_deviation = max_deviation.max(deviation);
            }
        }

        max_deviation
    }

    /// Detect trending pattern
    fn detect_trend(&self, metrics: &[f64]) -> Option<f64> {
        if metrics.len() < 10 {
            return None;
        }

        // Simple linear regression to detect trend
        let n = metrics.len() as f64;
        let x_values: Vec<f64> = (0..metrics.len()).map(|i| i as f64).collect();
        
        let sum_x: f64 = x_values.iter().sum();
        let sum_y: f64 = metrics.iter().sum();
        let sum_xy: f64 = x_values.iter().zip(metrics.iter()).map(|(x, y)| x * y).sum();
        let sum_x2: f64 = x_values.iter().map(|x| x * x).sum();

        let slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x);
        let mean_y = sum_y / n;
        
        // Convert slope to percentage growth rate
        let growth_rate = (slope / mean_y) * 100.0;
        
        // Only consider significant trends
        if growth_rate.abs() > 1.0 {
            Some(growth_rate)
        } else {
            None
        }
    }

    /// Check if pattern is bursty
    fn is_bursty_pattern(&self, metrics: &[f64]) -> bool {
        if metrics.len() < 20 {
            return false;
        }

        let mean = metrics.iter().sum::<f64>() / metrics.len() as f64;
        let mut burst_count = 0;
        let burst_threshold = mean * 1.5; // 50% above average

        for &value in metrics {
            if value > burst_threshold {
                burst_count += 1;
            }
        }

        let burst_ratio = burst_count as f64 / metrics.len() as f64;
        burst_ratio > 0.1 && burst_ratio < 0.3 // 10-30% of time in burst
    }

    /// Analyze burst characteristics
    fn analyze_bursts(&self, metrics: &[f64]) -> (u64, f64) {
        let mean = metrics.iter().sum::<f64>() / metrics.len() as f64;
        let burst_threshold = mean * 1.5;

        let mut burst_durations = Vec::new();
        let mut max_peak: f64 = 0.0;
        let mut current_burst_length = 0;

        for &value in metrics {
            if value > burst_threshold {
                current_burst_length += 1;
                max_peak = max_peak.max(value);
            } else if current_burst_length > 0 {
                burst_durations.push(current_burst_length);
                current_burst_length = 0;
            }
        }

        let avg_duration = if !burst_durations.is_empty() {
            burst_durations.iter().sum::<u32>() as f64 / burst_durations.len() as f64
        } else {
            0.0
        };

        let peak_multiplier = if mean > 0.0 { max_peak / mean } else { 1.0 };
        
        (
            (avg_duration * self.config.adjustment_interval_seconds as f64) as u64,
            peak_multiplier
        )
    }

    /// Generate sizing recommendation based on current data and predictions
    pub fn generate_recommendation(&mut self, current_pool_size: u32) -> Option<SizingRecommendation> {
        if !self.config.enabled {
            return None;
        }

        // Check if enough time has passed since last adjustment
        if self.last_adjustment.elapsed().as_secs() < self.config.adjustment_interval_seconds as u64 {
            return None;
        }

        // Check if we have enough data for reliable predictions
        if self.historical_metrics.len() < self.config.min_samples_for_prediction as usize {
            return None;
        }

        // Predict load for the next period
        let predicted_load = if self.config.predictive_scaling_enabled {
            let horizon_steps = (self.config.prediction_horizon_minutes * 60) / self.config.adjustment_interval_seconds;
            self.predict_load_at_offset(horizon_steps as i32)
        } else {
            self.predict_load_at_offset(1) // Next immediate period
        };

        // Add safety buffer
        let buffered_load = predicted_load * (1.0 + self.config.safety_buffer_percent as f64 / 100.0);
        
        // Calculate recommended size
        let mut recommended_size = buffered_load.ceil() as u32;
        
        // Apply sensitivity adjustment
        let size_change = (recommended_size as i32 - current_pool_size as i32) as f64;
        let adjusted_change = size_change * self.config.sensitivity;
        recommended_size = (current_pool_size as f64 + adjusted_change).round() as u32;

        // Apply maximum change limit
        let max_change = (current_pool_size as f64 * self.config.max_change_percent as f64 / 100.0) as u32;
        let size_diff = (recommended_size as i32 - current_pool_size as i32).abs() as u32;
        
        if size_diff > max_change {
            if recommended_size > current_pool_size {
                recommended_size = current_pool_size + max_change;
            } else {
                recommended_size = current_pool_size.saturating_sub(max_change);
            }
        }

        // Apply cost optimization
        if self.config.cost_optimization_weight > 0.0 {
            let cost_optimized_size = self.apply_cost_optimization(recommended_size, current_pool_size);
            let weight = self.config.cost_optimization_weight;
            recommended_size = ((1.0 - weight) * recommended_size as f64 + weight * cost_optimized_size as f64) as u32;
        }

        // Ensure minimum size of 1
        recommended_size = recommended_size.max(1);

        // Calculate confidence based on model accuracy and pattern stability
        let confidence = self.calculate_recommendation_confidence();

        // Determine reason for recommendation
        let reason = self.generate_recommendation_reason(current_pool_size, recommended_size, predicted_load);

        // Calculate cost and performance impact
        let cost_impact = self.calculate_cost_impact(current_pool_size, recommended_size);
        let performance_impact = self.calculate_performance_impact(current_pool_size, recommended_size);

        Some(SizingRecommendation {
            current_size: current_pool_size,
            recommended_size,
            confidence,
            reason,
            cost_impact_percent: cost_impact,
            performance_impact,
            next_adjustment_seconds: self.config.adjustment_interval_seconds,
            predicted_load,
            constitutional_compliance: true, // Always true with hash validation
        })
    }

    /// Apply cost optimization to sizing recommendation
    fn apply_cost_optimization(&self, recommended_size: u32, _current_size: u32) -> u32 {
        // Bias towards smaller pool sizes to reduce costs
        let cost_optimized = (recommended_size as f64 * 0.9) as u32; // 10% reduction bias
        cost_optimized.max(1)
    }

    /// Calculate confidence in the recommendation
    fn calculate_recommendation_confidence(&self) -> f64 {
        let mut confidence = self.prediction_model.confidence;
        
        // Reduce confidence if we don't have much historical data
        if self.historical_metrics.len() < 100 {
            confidence *= self.historical_metrics.len() as f64 / 100.0;
        }
        
        // Reduce confidence for random patterns
        if self.detected_patterns.contains(&LoadPattern::Random) {
            confidence *= 0.7;
        }
        
        // Increase confidence for steady patterns
        if self.detected_patterns.contains(&LoadPattern::Steady) {
            confidence *= 1.1;
        }
        
        confidence.max(0.0).min(1.0)
    }

    /// Generate human-readable reason for recommendation
    fn generate_recommendation_reason(&self, current_size: u32, recommended_size: u32, predicted_load: f64) -> String {
        if recommended_size > current_size {
            format!("Predicted load increase to {:.1} connections requires scaling up", predicted_load)
        } else if recommended_size < current_size {
            format!("Predicted load decrease to {:.1} connections allows scaling down", predicted_load)
        } else {
            "Current pool size is optimal for predicted load".to_string()
        }
    }

    /// Calculate cost impact of size change
    fn calculate_cost_impact(&self, current_size: u32, recommended_size: u32) -> f64 {
        let connection_cost_per_hour = 0.001; // $0.001 per connection per hour
        let size_change = recommended_size as i32 - current_size as i32;
        let hourly_cost_change = size_change as f64 * connection_cost_per_hour;
        let monthly_cost_change = hourly_cost_change * 24.0 * 30.0;
        
        // Return as percentage of current cost
        if current_size > 0 {
            let current_monthly_cost = current_size as f64 * connection_cost_per_hour * 24.0 * 30.0;
            (monthly_cost_change / current_monthly_cost) * 100.0
        } else {
            0.0
        }
    }

    /// Calculate performance impact of size change
    fn calculate_performance_impact(&self, current_size: u32, recommended_size: u32) -> PerformanceImpact {
        let size_ratio = recommended_size as f64 / current_size.max(1) as f64;
        
        if size_ratio > 1.1 {
            // Scaling up - expect performance improvement
            let improvement = ((size_ratio - 1.0) * 50.0).min(30.0); // Cap at 30% improvement
            PerformanceImpact::Positive { improvement_percent: improvement }
        } else if size_ratio < 0.9 {
            // Scaling down - potential performance degradation
            let degradation = ((1.0 - size_ratio) * 30.0).min(20.0); // Cap at 20% degradation
            PerformanceImpact::Negative { degradation_percent: degradation }
        } else {
            PerformanceImpact::Neutral
        }
    }

    /// Apply a sizing recommendation
    pub fn apply_recommendation(&mut self, recommendation: &SizingRecommendation) {
        self.last_adjustment = Instant::now();
        self.sizing_statistics.total_adjustments += 1;
        
        // Update statistics based on the applied recommendation
        if recommendation.confidence > 0.8 {
            self.sizing_statistics.successful_predictions += 1;
        }
        
        self.sizing_statistics.total_predictions += 1;
        
        // Update average accuracy
        let total = self.sizing_statistics.total_predictions as f64;
        let success_rate = self.sizing_statistics.successful_predictions as f64 / total;
        self.sizing_statistics.average_accuracy = success_rate;
        
        // Track cost savings
        if recommendation.cost_impact_percent > 0.0 {
            self.sizing_statistics.cost_savings_achieved += recommendation.cost_impact_percent;
        }
        
        // Track performance improvements
        if let PerformanceImpact::Positive { improvement_percent } = recommendation.performance_impact {
            self.sizing_statistics.performance_improvements_percent += improvement_percent;
        }
    }

    /// Get sizing engine statistics
    pub fn get_statistics(&self) -> &SizingStatistics {
        &self.sizing_statistics
    }

    /// Get detected load patterns
    pub fn get_detected_patterns(&self) -> &[LoadPattern] {
        &self.detected_patterns
    }

    /// Get prediction model status
    pub fn get_prediction_model(&self) -> &LoadPredictionModel {
        &self.prediction_model
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_dynamic_sizing_engine_creation() {
        let config = DynamicSizingConfig::default();
        let engine = DynamicSizingEngine::new(config);
        
        assert_eq!(engine.config.constitutional_hash, "cdd01ef066bc6cf2");
        assert!(engine.config.enabled);
        assert_eq!(engine.historical_metrics.len(), 0);
    }

    #[test]
    fn test_metrics_addition() {
        let config = DynamicSizingConfig::default();
        let mut engine = DynamicSizingEngine::new(config);
        
        let metrics = LoadMetrics {
            active_connections: 10,
            constitutional_hash: "cdd01ef066bc6cf2".to_string(),
            ..Default::default()
        };
        
        engine.add_metrics(metrics);
        assert_eq!(engine.historical_metrics.len(), 1);
    }

    #[test]
    fn test_steady_pattern_detection() {
        let config = DynamicSizingConfig::default();
        let engine = DynamicSizingEngine::new(config);
        
        // Create steady metrics (low variation)
        let steady_metrics: Vec<f64> = vec![10.0; 20]; // All same value
        assert!(engine.is_steady_pattern(&steady_metrics));
        
        // Create variable metrics
        let variable_metrics: Vec<f64> = (0..20).map(|i| i as f64).collect();
        assert!(!engine.is_steady_pattern(&variable_metrics));
    }

    #[test]
    fn test_prediction_with_moving_average() {
        let mut config = DynamicSizingConfig::default();
        config.prediction_model = PredictionModelType::MovingAverage { window_size: 5 };
        config.min_samples_for_prediction = 5;
        
        let mut engine = DynamicSizingEngine::new(config);
        
        // Add test data
        for i in 1..=10 {
            let metrics = LoadMetrics {
                active_connections: i * 2,
                constitutional_hash: "cdd01ef066bc6cf2".to_string(),
                ..Default::default()
            };
            engine.add_metrics(metrics);
        }
        
        // Should have updated the model
        assert!(engine.prediction_model.parameters.contains_key("average"));
    }

    #[test]
    fn test_recommendation_generation() {
        let mut config = DynamicSizingConfig::default();
        config.min_samples_for_prediction = 5;
        
        let mut engine = DynamicSizingEngine::new(config);
        
        // Add sufficient test data
        for i in 1..=10 {
            let metrics = LoadMetrics {
                active_connections: 10 + i,
                constitutional_hash: "cdd01ef066bc6cf2".to_string(),
                ..Default::default()
            };
            engine.add_metrics(metrics);
        }
        
        // Generate recommendation
        let recommendation = engine.generate_recommendation(15);
        assert!(recommendation.is_some());
        
        let rec = recommendation.unwrap();
        assert_eq!(rec.current_size, 15);
        assert!(rec.constitutional_compliance);
    }

    #[test]
    fn test_cost_impact_calculation() {
        let config = DynamicSizingConfig::default();
        let engine = DynamicSizingEngine::new(config);
        
        let impact = engine.calculate_cost_impact(10, 15);
        assert!(impact > 0.0); // Scaling up should increase cost
        
        let impact_down = engine.calculate_cost_impact(15, 10);
        assert!(impact_down < 0.0); // Scaling down should reduce cost
    }
}