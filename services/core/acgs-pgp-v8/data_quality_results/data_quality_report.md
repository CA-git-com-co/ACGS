# Data Quality Assessment Report

**Generated:** 2025-06-27T18:30:08.778097
**Sample Size:** 1,000
**Features Analyzed:** 10
**Constitutional Hash:** cdd01ef066bc6cf2

## 🎯 Overall Quality Score

**🟡 Quality Score: 71.1%**
Target: >80% ❌ NOT ACHIEVED

## 📊 Detailed Quality Metrics

### Missing Values

- **Missing Rate:** 0.5%
- **Status:** ✅ Good

### Outliers

- **Outlier Rate:** 4.7%
- **Affected Features:** 0
- **Status:** ✅ Good

### Class Balance

- **Imbalance Ratio:** 0.153
- **Status:** ⚠️ Imbalanced

### Feature Correlation

- **Max Correlation:** 0.995
- **High Correlation Pairs:** 1
- **Status:** ⚠️ High Multicollinearity

### Data Freshness

- **Hours Since Update:** 0.0
- **Stale Data Rate:** 66.4%
- **Status:** ✅ Fresh

### Data Consistency

- **Duplicate Rate:** 1.0%
- **Inconsistency Rate:** 0.0%
- **Status:** ✅ Consistent

### Data Completeness

- **Completeness Score:** 99.5%
- **Status:** ✅ Complete

## 🔧 Recommendations

⚠️ **Data quality improvements needed:**

- Use SMOTE or other balancing techniques
- Remove highly correlated features
