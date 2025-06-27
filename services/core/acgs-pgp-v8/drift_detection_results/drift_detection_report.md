# Data Drift Detection Report

**Generated:** 2025-06-27T18:57:12.770356
**Constitutional Hash:** cdd01ef066bc6cf2

## 🎯 Executive Summary

**🔴 Drift Status:** HIGH
**Drift Score:** 0.706
**Retraining Required:** ✅ YES
**Urgency Level:** HIGH

## 📊 Dataset Information

- **Reference Period:** baseline
- **Current Period:** current
- **Reference Samples:** 1,500
- **Current Samples:** 1,500

## 🔍 Drift Analysis Results

### Kolmogorov-Smirnov Test Results

| Feature | KS Statistic | P-Value | Drift Detected |
|---------|--------------|---------|----------------|
| response_time_ms | 0.2293 | 0.0000 | ✅ YES |
| cost_estimate | 0.1033 | 0.0000 | ✅ YES |
| quality_score | 0.0793 | 0.0002 | ✅ YES |
| complexity_score | 0.1427 | 0.0000 | ✅ YES |
| content_length | 0.9987 | 0.0000 | ✅ YES |
| hour_of_day | 0.0787 | 0.0002 | ✅ YES |
| is_weekend | 0.0267 | 0.6606 | ❌ NO |
| constitutional_compliance | 0.0267 | 0.6606 | ❌ NO |

### Population Stability Index (PSI) Results

| Feature | PSI Value | Drift Level |
|---------|-----------|-------------|
| response_time_ms | 0.2747 | 🔴 High |
| cost_estimate | 0.0687 | 🟢 Low |
| quality_score | 0.0370 | 🟢 Low |
| complexity_score | 0.0896 | 🟢 Low |
| content_length | 18.9200 | 🔴 High |
| hour_of_day | 0.0915 | 🟢 Low |
| is_weekend | 0.0000 | 🟢 Low |
| constitutional_compliance | 0.0000 | 🟢 Low |

## ⚠️ Affected Features

Features showing significant drift:
- **cost_estimate**
- **response_time_ms**
- **hour_of_day**
- **quality_score**
- **content_length**
- **complexity_score**

## 🔄 Retraining Recommendations

**🚨 RETRAINING REQUIRED - HIGH PRIORITY**

**Immediate Actions Required:**
1. Initiate emergency retraining pipeline
2. Collect fresh training data
3. Validate model performance
4. Deploy updated model within 24 hours

## 🔧 Technical Configuration

### Detection Parameters
- **KS Test Threshold:** 0.05 (p-value)
- **PSI Low Threshold:** 0.1
- **PSI Medium Threshold:** 0.2
- **PSI High Threshold:** 0.2
- **Constitutional Hash:** cdd01ef066bc6cf2

### Automated Triggers
- **High Priority:** Immediate retraining pipeline activation
- **Medium Priority:** Scheduled retraining within 72 hours
- **Low Priority:** Enhanced monitoring and preparation
