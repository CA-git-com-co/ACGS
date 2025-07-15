// Constitutional Hash: cdd01ef066bc6cf2
//! ACGS-2 Constitutional Compliance Validation Library
//! 
//! This library provides unified constitutional compliance validation
//! across all ACGS-2 components (expert service and blockchain programs).

use serde::{Deserialize, Serialize};
use std::fmt;
use thiserror::Error;

/// The immutable constitutional hash for ACGS-2 compliance
pub const CONSTITUTIONAL_HASH: &str = "cdd01ef066bc6cf2";

/// Constitutional compliance validation errors
#[derive(Error, Debug, Clone, PartialEq)]
pub enum ConstitutionalError {
    #[error("Constitutional compliance violation: expected hash {expected}, got {actual}")]
    HashMismatch { expected: String, actual: String },
    
    #[error("Constitutional hash missing from data structure")]
    HashMissing,
    
    #[error("Constitutional principle violation: {principle}")]
    PrincipleViolation { principle: String },
    
    #[error("Constitutional validation failed: {reason}")]
    ValidationFailed { reason: String },
}

/// Trait for constitutional compliance validation
pub trait ConstitutionalCompliance {
    /// Validate constitutional compliance
    fn validate_constitutional_compliance(&self) -> Result<(), ConstitutionalError>;
    
    /// Get the constitutional hash
    fn constitutional_hash(&self) -> &str;
    
    /// Check if constitutionally compliant
    fn is_constitutionally_compliant(&self) -> bool {
        self.validate_constitutional_compliance().is_ok()
    }
}

/// Constitutional compliance metadata
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct ConstitutionalMetadata {
    pub hash: String,
    pub timestamp: i64,
    pub version: String,
    pub validator: String,
}

impl ConstitutionalMetadata {
    /// Create new constitutional metadata with current timestamp
    pub fn new(validator: impl Into<String>) -> Self {
        Self {
            hash: CONSTITUTIONAL_HASH.to_string(),
            timestamp: chrono::Utc::now().timestamp(),
            version: "1.0.0".to_string(),
            validator: validator.into(),
        }
    }
    
    /// Create constitutional metadata with specific timestamp
    pub fn with_timestamp(validator: impl Into<String>, timestamp: i64) -> Self {
        Self {
            hash: CONSTITUTIONAL_HASH.to_string(),
            timestamp,
            version: "1.0.0".to_string(),
            validator: validator.into(),
        }
    }
}

impl ConstitutionalCompliance for ConstitutionalMetadata {
    fn validate_constitutional_compliance(&self) -> Result<(), ConstitutionalError> {
        if self.hash != CONSTITUTIONAL_HASH {
            return Err(ConstitutionalError::HashMismatch {
                expected: CONSTITUTIONAL_HASH.to_string(),
                actual: self.hash.clone(),
            });
        }
        Ok(())
    }
    
    fn constitutional_hash(&self) -> &str {
        &self.hash
    }
}

/// Constitutional principle categories
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum PrincipleCategory {
    Core,
    Process,
    Ethics,
    Technical,
    Economic,
}

/// Constitutional principle definition
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct ConstitutionalPrinciple {
    pub id: String,
    pub name: String,
    pub description: String,
    pub category: PrincipleCategory,
    pub weight: f64,
    pub constitutional_metadata: ConstitutionalMetadata,
}

impl ConstitutionalPrinciple {
    /// Create a new constitutional principle
    pub fn new(
        id: impl Into<String>,
        name: impl Into<String>,
        description: impl Into<String>,
        category: PrincipleCategory,
        weight: f64,
    ) -> Self {
        Self {
            id: id.into(),
            name: name.into(),
            description: description.into(),
            category,
            weight,
            constitutional_metadata: ConstitutionalMetadata::new("acgs-system"),
        }
    }
}

impl ConstitutionalCompliance for ConstitutionalPrinciple {
    fn validate_constitutional_compliance(&self) -> Result<(), ConstitutionalError> {
        self.constitutional_metadata.validate_constitutional_compliance()
    }
    
    fn constitutional_hash(&self) -> &str {
        self.constitutional_metadata.constitutional_hash()
    }
}

/// Validate constitutional hash in any string field
pub fn validate_hash(hash: &str) -> Result<(), ConstitutionalError> {
    if hash != CONSTITUTIONAL_HASH {
        return Err(ConstitutionalError::HashMismatch {
            expected: CONSTITUTIONAL_HASH.to_string(),
            actual: hash.to_string(),
        });
    }
    Ok(())
}

/// Ensure constitutional compliance for any data structure
pub fn ensure_constitutional_compliance<T: ConstitutionalCompliance>(
    item: &T,
) -> Result<(), ConstitutionalError> {
    item.validate_constitutional_compliance()
}

/// Constitutional compliance validator utility
pub struct ConstitutionalValidator {
    strict_mode: bool,
}

impl ConstitutionalValidator {
    /// Create a new constitutional validator
    pub fn new(strict_mode: bool) -> Self {
        Self { strict_mode }
    }
    
    /// Validate multiple items for constitutional compliance
    pub fn validate_batch<T: ConstitutionalCompliance>(
        &self,
        items: &[T],
    ) -> Result<(), Vec<ConstitutionalError>> {
        let errors: Vec<ConstitutionalError> = items
            .iter()
            .filter_map(|item| item.validate_constitutional_compliance().err())
            .collect();
            
        if errors.is_empty() {
            Ok(())
        } else {
            Err(errors)
        }
    }
    
    /// Log constitutional compliance status
    pub fn log_compliance_status<T: ConstitutionalCompliance>(&self, item: &T, context: &str) {
        match item.validate_constitutional_compliance() {
            Ok(()) => {
                tracing::info!(
                    "✅ Constitutional compliance validated for {}: hash={}",
                    context,
                    item.constitutional_hash()
                );
            }
            Err(e) => {
                if self.strict_mode {
                    tracing::error!("❌ Constitutional compliance violation in {}: {}", context, e);
                } else {
                    tracing::warn!("⚠️ Constitutional compliance warning in {}: {}", context, e);
                }
            }
        }
    }
}

impl Default for ConstitutionalValidator {
    fn default() -> Self {
        Self::new(true) // Strict mode by default
    }
}

impl fmt::Display for ConstitutionalMetadata {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "ConstitutionalMetadata(hash={}, timestamp={}, validator={})",
            self.hash, self.timestamp, self.validator
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_constitutional_hash_validation() {
        assert!(validate_hash(CONSTITUTIONAL_HASH).is_ok());
        assert!(validate_hash("invalid_hash").is_err());
    }

    #[test]
    fn test_constitutional_metadata() {
        let metadata = ConstitutionalMetadata::new("test-validator");
        assert!(metadata.is_constitutionally_compliant());
        assert_eq!(metadata.constitutional_hash(), CONSTITUTIONAL_HASH);
    }

    #[test]
    fn test_constitutional_principle() {
        let principle = ConstitutionalPrinciple::new(
            "test-principle",
            "Test Principle",
            "A test constitutional principle",
            PrincipleCategory::Core,
            1.0,
        );
        assert!(principle.is_constitutionally_compliant());
    }

    #[test]
    fn test_constitutional_validator() {
        let validator = ConstitutionalValidator::new(true);
        let metadata = ConstitutionalMetadata::new("test");
        assert!(validator.validate_batch(&[metadata]).is_ok());
    }
}
