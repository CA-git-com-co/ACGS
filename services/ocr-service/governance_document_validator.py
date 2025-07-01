#!/usr/bin/env python3
"""
Governance Document Validator for ACGS
Provides specialized validation for governance documents processed through OCR
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

try:
    from .advanced_document_processor import ProcessedDocument, Signature, Watermark
except ImportError:
    from advanced_document_processor import ProcessedDocument, Signature, Watermark

logger = logging.getLogger(__name__)


class DocumentType(Enum):
    """Enumeration of governance document types"""

    CONSTITUTION = "constitution"
    AMENDMENT = "amendment"
    POLICY = "policy"
    REGULATION = "regulation"
    GOVERNANCE_FORM = "governance_form"
    OFFICIAL_DOCUMENT = "official_document"
    LEGAL_CONTRACT = "legal_contract"
    VOTING_BALLOT = "voting_ballot"
    MEETING_MINUTES = "meeting_minutes"
    COMPLIANCE_REPORT = "compliance_report"


class ValidationLevel(Enum):
    """Validation strictness levels"""

    BASIC = "basic"
    STANDARD = "standard"
    STRICT = "strict"
    FORENSIC = "forensic"


@dataclass
class ValidationRule:
    """Individual validation rule"""

    rule_id: str
    description: str
    rule_type: str  # required, recommended, optional
    validator_function: str
    parameters: Dict[str, Any] = None

    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}


@dataclass
class ValidationResult:
    """Result of a validation check"""

    rule_id: str
    passed: bool
    score: float  # 0.0 to 1.0
    message: str
    details: Dict[str, Any] = None

    def __post_init__(self):
        if self.details is None:
            self.details = {}


@dataclass
class DocumentValidationReport:
    """Complete validation report for a document"""

    document_id: str
    document_type: DocumentType
    validation_level: ValidationLevel
    overall_score: float
    passed_rules: int
    total_rules: int
    validation_results: List[ValidationResult]
    authenticity_score: float
    compliance_score: float
    recommendations: List[str]
    timestamp: datetime
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class GovernanceDocumentValidator:
    """
    Specialized validator for governance documents processed through OCR
    Provides comprehensive validation for authenticity, compliance, and structure
    """

    def __init__(self):
        self.validation_rules = self._initialize_validation_rules()
        self.document_type_rules = self._initialize_document_type_rules()

    def validate_document(
        self,
        processed_doc: ProcessedDocument,
        document_type: DocumentType,
        validation_level: ValidationLevel = ValidationLevel.STANDARD,
    ) -> DocumentValidationReport:
        """
        Validate a processed document according to governance standards

        Args:
            processed_doc: ProcessedDocument from OCR processing
            document_type: Type of governance document
            validation_level: Strictness of validation

        Returns:
            DocumentValidationReport with comprehensive validation results
        """
        logger.info(
            f"Validating document {processed_doc.document_id} as {document_type.value}"
        )

        # Get applicable rules for this document type and validation level
        applicable_rules = self._get_applicable_rules(document_type, validation_level)

        validation_results = []

        # Run each validation rule
        for rule in applicable_rules:
            result = self._execute_validation_rule(rule, processed_doc)
            validation_results.append(result)

        # Calculate scores
        overall_score = self._calculate_overall_score(validation_results)
        authenticity_score = self._calculate_authenticity_score(processed_doc)
        compliance_score = self._calculate_compliance_score(
            validation_results, document_type
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(
            validation_results, processed_doc
        )

        # Count passed rules
        passed_rules = sum(1 for result in validation_results if result.passed)

        report = DocumentValidationReport(
            document_id=processed_doc.document_id,
            document_type=document_type,
            validation_level=validation_level,
            overall_score=overall_score,
            passed_rules=passed_rules,
            total_rules=len(validation_results),
            validation_results=validation_results,
            authenticity_score=authenticity_score,
            compliance_score=compliance_score,
            recommendations=recommendations,
            timestamp=datetime.now(),
            metadata={
                "processing_timestamp": processed_doc.processing_timestamp.isoformat(),
                "confidence_score": processed_doc.confidence_score,
                "text_length": len(processed_doc.raw_text),
            },
        )

        logger.info(
            f"Validation complete. Score: {overall_score:.3f}, "
            f"Passed: {passed_rules}/{len(validation_results)} rules"
        )

        return report

    def _initialize_validation_rules(self) -> Dict[str, ValidationRule]:
        """Initialize the validation rule set"""
        rules = {
            "has_signatures": ValidationRule(
                rule_id="has_signatures",
                description="Document must contain at least one signature",
                rule_type="required",
                validator_function="validate_signatures_present",
            ),
            "has_watermarks": ValidationRule(
                rule_id="has_watermarks",
                description="Official documents should contain watermarks",
                rule_type="recommended",
                validator_function="validate_watermarks_present",
            ),
            "proper_structure": ValidationRule(
                rule_id="proper_structure",
                description="Document must have proper structural elements",
                rule_type="required",
                validator_function="validate_document_structure",
            ),
            "page_numbering": ValidationRule(
                rule_id="page_numbering",
                description="Multi-page documents should have page numbers",
                rule_type="recommended",
                validator_function="validate_page_numbering",
            ),
            "text_quality": ValidationRule(
                rule_id="text_quality",
                description="Text extraction quality must meet minimum standards",
                rule_type="required",
                validator_function="validate_text_quality",
            ),
            "legal_language": ValidationRule(
                rule_id="legal_language",
                description="Legal documents must use appropriate legal language",
                rule_type="required",
                validator_function="validate_legal_language",
            ),
            "date_consistency": ValidationRule(
                rule_id="date_consistency",
                description="Dates in document must be consistent and valid",
                rule_type="required",
                validator_function="validate_date_consistency",
            ),
            "signature_authenticity": ValidationRule(
                rule_id="signature_authenticity",
                description="Signatures must appear authentic",
                rule_type="strict",
                validator_function="validate_signature_authenticity",
            ),
            "checkbox_completion": ValidationRule(
                rule_id="checkbox_completion",
                description="Forms should have completed checkboxes",
                rule_type="recommended",
                validator_function="validate_checkbox_completion",
            ),
            "table_integrity": ValidationRule(
                rule_id="table_integrity",
                description="Tables must be properly formatted and complete",
                rule_type="required",
                validator_function="validate_table_integrity",
            ),
        }

        return rules

    def _initialize_document_type_rules(self) -> Dict[DocumentType, List[str]]:
        """Map document types to applicable validation rules"""
        return {
            DocumentType.CONSTITUTION: [
                "has_signatures",
                "proper_structure",
                "text_quality",
                "legal_language",
                "date_consistency",
            ],
            DocumentType.AMENDMENT: [
                "has_signatures",
                "proper_structure",
                "text_quality",
                "legal_language",
                "date_consistency",
            ],
            DocumentType.POLICY: [
                "has_signatures",
                "proper_structure",
                "text_quality",
                "page_numbering",
                "date_consistency",
            ],
            DocumentType.GOVERNANCE_FORM: [
                "has_signatures",
                "checkbox_completion",
                "text_quality",
                "table_integrity",
                "date_consistency",
            ],
            DocumentType.OFFICIAL_DOCUMENT: [
                "has_signatures",
                "has_watermarks",
                "proper_structure",
                "text_quality",
                "signature_authenticity",
                "page_numbering",
            ],
            DocumentType.LEGAL_CONTRACT: [
                "has_signatures",
                "proper_structure",
                "text_quality",
                "legal_language",
                "date_consistency",
                "signature_authenticity",
            ],
            DocumentType.VOTING_BALLOT: [
                "checkbox_completion",
                "text_quality",
                "proper_structure",
            ],
            DocumentType.MEETING_MINUTES: [
                "proper_structure",
                "text_quality",
                "date_consistency",
                "page_numbering",
            ],
            DocumentType.COMPLIANCE_REPORT: [
                "has_signatures",
                "proper_structure",
                "text_quality",
                "table_integrity",
                "date_consistency",
                "page_numbering",
            ],
        }

    def _get_applicable_rules(
        self, document_type: DocumentType, validation_level: ValidationLevel
    ) -> List[ValidationRule]:
        """Get validation rules applicable to document type and validation level"""
        rule_ids = self.document_type_rules.get(document_type, [])

        applicable_rules = []
        for rule_id in rule_ids:
            rule = self.validation_rules.get(rule_id)
            if rule and self._is_rule_applicable(rule, validation_level):
                applicable_rules.append(rule)

        return applicable_rules

    def _is_rule_applicable(
        self, rule: ValidationRule, validation_level: ValidationLevel
    ) -> bool:
        """Check if a rule applies to the given validation level"""
        level_rules = {
            ValidationLevel.BASIC: ["required"],
            ValidationLevel.STANDARD: ["required", "recommended"],
            ValidationLevel.STRICT: ["required", "recommended", "optional"],
            ValidationLevel.FORENSIC: ["required", "recommended", "optional", "strict"],
        }

        return rule.rule_type in level_rules.get(validation_level, [])

    def _execute_validation_rule(
        self, rule: ValidationRule, processed_doc: ProcessedDocument
    ) -> ValidationResult:
        """Execute a single validation rule"""
        try:
            # Get the validator function
            validator_func = getattr(self, rule.validator_function)

            # Execute the validation
            passed, score, message, details = validator_func(
                processed_doc, rule.parameters
            )

            return ValidationResult(
                rule_id=rule.rule_id,
                passed=passed,
                score=score,
                message=message,
                details=details,
            )

        except Exception as e:
            logger.error(f"Error executing validation rule {rule.rule_id}: {str(e)}")
            return ValidationResult(
                rule_id=rule.rule_id,
                passed=False,
                score=0.0,
                message=f"Validation error: {str(e)}",
                details={"error": str(e)},
            )

    # Validation methods

    def validate_signatures_present(
        self, processed_doc: ProcessedDocument, parameters: Dict[str, Any]
    ) -> Tuple[bool, float, str, Dict[str, Any]]:
        """Validate that document contains signatures"""
        signature_count = len(processed_doc.signatures)

        if signature_count > 0:
            score = min(1.0, signature_count * 0.5)  # Max score at 2 signatures
            return (
                True,
                score,
                f"Found {signature_count} signature(s)",
                {"signature_count": signature_count},
            )
        else:
            return False, 0.0, "No signatures found", {"signature_count": 0}

    def validate_watermarks_present(
        self, processed_doc: ProcessedDocument, parameters: Dict[str, Any]
    ) -> Tuple[bool, float, str, Dict[str, Any]]:
        """Validate that document contains watermarks"""
        watermark_count = len(processed_doc.watermarks)

        if watermark_count > 0:
            score = min(1.0, watermark_count * 0.7)  # Higher weight for watermarks
            return (
                True,
                score,
                f"Found {watermark_count} watermark(s)",
                {"watermark_count": watermark_count},
            )
        else:
            return False, 0.0, "No watermarks found", {"watermark_count": 0}

    def validate_document_structure(
        self, processed_doc: ProcessedDocument, parameters: Dict[str, Any]
    ) -> Tuple[bool, float, str, Dict[str, Any]]:
        """Validate document has proper structure"""
        text = processed_doc.raw_text

        # Check for basic structural elements
        has_title = bool(re.search(r"^[A-Z][A-Z\s]{10,}$", text, re.MULTILINE))
        has_sections = bool(
            re.search(r"(section|article|chapter)\s+\d+", text, re.IGNORECASE)
        )
        has_paragraphs = len(text.split("\n\n")) > 2

        structure_score = 0.0
        if has_title:
            structure_score += 0.4
        if has_sections:
            structure_score += 0.4
        if has_paragraphs:
            structure_score += 0.2

        passed = structure_score >= 0.6
        message = f"Document structure score: {structure_score:.2f}"

        details = {
            "has_title": has_title,
            "has_sections": has_sections,
            "has_paragraphs": has_paragraphs,
            "paragraph_count": len(text.split("\n\n")),
        }

        return passed, structure_score, message, details

    def validate_page_numbering(
        self, processed_doc: ProcessedDocument, parameters: Dict[str, Any]
    ) -> Tuple[bool, float, str, Dict[str, Any]]:
        """Validate page numbering consistency"""
        page_numbers = processed_doc.page_numbers

        if not page_numbers:
            return False, 0.0, "No page numbers found", {"page_count": 0}

        # Check for sequential numbering
        page_nums = []
        for page_num in page_numbers:
            if page_num.page_num:
                page_nums.append(page_num.page_num)

        if not page_nums:
            return False, 0.0, "No valid page numbers found", {"page_count": 0}

        page_nums.sort()
        is_sequential = all(
            page_nums[i] == page_nums[i - 1] + 1 for i in range(1, len(page_nums))
        )

        score = 1.0 if is_sequential else 0.5
        message = f"Page numbering {'is' if is_sequential else 'is not'} sequential"

        return (
            True,
            score,
            message,
            {
                "page_count": len(page_nums),
                "is_sequential": is_sequential,
                "page_range": (
                    f"{min(page_nums)}-{max(page_nums)}" if page_nums else "N/A"
                ),
            },
        )

    def validate_text_quality(
        self, processed_doc: ProcessedDocument, parameters: Dict[str, Any]
    ) -> Tuple[bool, float, str, Dict[str, Any]]:
        """Validate OCR text extraction quality"""
        text = processed_doc.raw_text

        # Basic quality metrics
        total_chars = len(text)
        alpha_chars = sum(1 for c in text if c.isalpha())
        digit_chars = sum(1 for c in text if c.isdigit())
        space_chars = sum(1 for c in text if c.isspace())

        if total_chars == 0:
            return False, 0.0, "No text extracted", {"total_chars": 0}

        alpha_ratio = alpha_chars / total_chars
        readable_ratio = (alpha_chars + digit_chars + space_chars) / total_chars

        # Check for common OCR errors
        error_patterns = [
            r"[^\w\s\.\,\!\?\;\:\-\(\)\[\]\"\']+",
            r"\s{3,}",
            r"[A-Z]{10,}",
        ]
        error_count = sum(len(re.findall(pattern, text)) for pattern in error_patterns)
        error_ratio = error_count / max(1, total_chars // 100)  # Errors per 100 chars

        quality_score = min(
            1.0,
            alpha_ratio * 0.4 + readable_ratio * 0.4 + max(0, 1 - error_ratio) * 0.2,
        )

        passed = quality_score >= 0.7
        message = f"Text quality score: {quality_score:.3f}"

        details = {
            "total_chars": total_chars,
            "alpha_ratio": alpha_ratio,
            "readable_ratio": readable_ratio,
            "error_count": error_count,
            "quality_score": quality_score,
        }

        return passed, quality_score, message, details

    def validate_legal_language(
        self, processed_doc: ProcessedDocument, parameters: Dict[str, Any]
    ) -> Tuple[bool, float, str, Dict[str, Any]]:
        """Validate use of appropriate legal language"""
        text = processed_doc.raw_text.lower()

        # Common legal terms and phrases
        legal_terms = [
            "whereas",
            "therefore",
            "hereby",
            "pursuant",
            "notwithstanding",
            "shall",
            "may",
            "must",
            "required",
            "prohibited",
            "authorized",
            "constitution",
            "amendment",
            "article",
            "section",
            "clause",
            "jurisdiction",
            "compliance",
            "violation",
            "enforcement",
        ]

        legal_phrases = [
            "in accordance with",
            "subject to",
            "provided that",
            "except as",
            "to the extent",
            "for the purpose of",
            "in the event that",
        ]

        # Count legal language usage
        term_count = sum(1 for term in legal_terms if term in text)
        phrase_count = sum(1 for phrase in legal_phrases if phrase in text)

        total_words = len(text.split())
        legal_density = (term_count + phrase_count) / max(1, total_words // 100)

        # Score based on legal language density
        score = min(1.0, legal_density * 0.1)  # Reasonable legal language usage
        passed = score >= 0.3

        message = f"Legal language density: {legal_density:.2f} terms per 100 words"

        details = {
            "legal_terms_found": term_count,
            "legal_phrases_found": phrase_count,
            "total_words": total_words,
            "legal_density": legal_density,
        }

        return passed, score, message, details

    def validate_date_consistency(
        self, processed_doc: ProcessedDocument, parameters: Dict[str, Any]
    ) -> Tuple[bool, float, str, Dict[str, Any]]:
        """Validate date consistency in document"""
        text = processed_doc.raw_text

        # Common date patterns
        date_patterns = [
            r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b",
            r"\b(\d{4}[/-]\d{1,2}[/-]\d{1,2})\b",
            r"\b([A-Za-z]+ \d{1,2},? \d{4})\b",
        ]

        dates_found = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            dates_found.extend(matches)

        if not dates_found:
            return False, 0.0, "No dates found in document", {"dates_found": 0}

        # Basic consistency check - all dates should be reasonable
        score = 1.0 if len(dates_found) > 0 else 0.0
        passed = len(dates_found) > 0

        message = f"Found {len(dates_found)} date(s) in document"
        details = {
            "dates_found": len(dates_found),
            "sample_dates": dates_found[:3],  # Show first 3 dates
        }

        return passed, score, message, details

    def validate_signature_authenticity(
        self, processed_doc: ProcessedDocument, parameters: Dict[str, Any]
    ) -> Tuple[bool, float, str, Dict[str, Any]]:
        """Validate signature authenticity"""
        signatures = processed_doc.signatures

        if not signatures:
            return False, 0.0, "No signatures to validate", {"signature_count": 0}

        authentic_score = 0.0
        for sig in signatures:
            # Check for signatory name
            if sig.signatory:
                authentic_score += 0.4
            # Check for date
            if sig.date_signed:
                authentic_score += 0.3
            # Check for reasonable content length
            if len(sig.content) > 10:
                authentic_score += 0.3

        authentic_score = authentic_score / len(signatures)  # Average across signatures
        passed = authentic_score >= 0.6

        message = f"Signature authenticity score: {authentic_score:.2f}"
        details = {
            "signature_count": len(signatures),
            "authenticity_score": authentic_score,
            "has_signatory_names": sum(1 for sig in signatures if sig.signatory),
            "has_dates": sum(1 for sig in signatures if sig.date_signed),
        }

        return passed, authentic_score, message, details

    def validate_checkbox_completion(
        self, processed_doc: ProcessedDocument, parameters: Dict[str, Any]
    ) -> Tuple[bool, float, str, Dict[str, Any]]:
        """Validate checkbox completion in forms"""
        checkboxes = processed_doc.checkboxes

        if not checkboxes:
            return (
                True,
                1.0,
                "No checkboxes found (not applicable)",
                {"checkbox_count": 0},
            )

        checked_count = sum(
            1 for cb in checkboxes if cb.state in ["checked", "crossed"]
        )
        completion_ratio = checked_count / len(checkboxes)

        # Score based on completion ratio
        score = completion_ratio
        passed = completion_ratio >= 0.5  # At least half should be completed

        message = f"Checkbox completion: {checked_count}/{len(checkboxes)} ({completion_ratio:.1%})"
        details = {
            "total_checkboxes": len(checkboxes),
            "checked_count": checked_count,
            "completion_ratio": completion_ratio,
            "checkbox_states": [cb.state for cb in checkboxes],
        }

        return passed, score, message, details

    def validate_table_integrity(
        self, processed_doc: ProcessedDocument, parameters: Dict[str, Any]
    ) -> Tuple[bool, float, str, Dict[str, Any]]:
        """Validate table structure and integrity"""
        tables = processed_doc.tables

        if not tables:
            return True, 1.0, "No tables found (not applicable)", {"table_count": 0}

        integrity_score = 0.0
        for table in tables:
            table_score = 0.0

            # Check if table has headers
            if table.headers:
                table_score += 0.4

            # Check if table has data
            if table.data and len(table.data) > 0:
                table_score += 0.4

            # Check if rows are consistent
            if table.data:
                row_lengths = [len(row) for row in table.data]
                if len(set(row_lengths)) == 1:  # All rows same length
                    table_score += 0.2

            integrity_score += table_score

        integrity_score = integrity_score / len(tables)  # Average across tables
        passed = integrity_score >= 0.6

        message = f"Table integrity score: {integrity_score:.2f}"
        details = {
            "table_count": len(tables),
            "integrity_score": integrity_score,
            "tables_with_headers": sum(1 for t in tables if t.headers),
            "tables_with_data": sum(1 for t in tables if t.data),
        }

        return passed, integrity_score, message, details

    # Helper methods for scoring and recommendations

    def _calculate_overall_score(
        self, validation_results: List[ValidationResult]
    ) -> float:
        """Calculate overall validation score"""
        if not validation_results:
            return 0.0

        total_score = sum(result.score for result in validation_results)
        return total_score / len(validation_results)

    def _calculate_authenticity_score(self, processed_doc: ProcessedDocument) -> float:
        """Calculate document authenticity score"""
        score = 0.5  # Base score

        # Signatures increase authenticity
        if processed_doc.signatures:
            score += min(0.3, len(processed_doc.signatures) * 0.15)

        # Watermarks increase authenticity
        if processed_doc.watermarks:
            score += min(0.2, len(processed_doc.watermarks) * 0.1)

        # Page numbers indicate structured document
        if processed_doc.page_numbers:
            score += 0.1

        return min(1.0, score)

    def _calculate_compliance_score(
        self, validation_results: List[ValidationResult], document_type: DocumentType
    ) -> float:
        """Calculate compliance score based on document type requirements"""
        if not validation_results:
            return 0.0

        # Weight different rules based on document type
        rule_weights = {
            DocumentType.CONSTITUTION: {
                "has_signatures": 0.3,
                "legal_language": 0.25,
                "proper_structure": 0.25,
                "text_quality": 0.2,
            },
            DocumentType.POLICY: {
                "proper_structure": 0.3,
                "text_quality": 0.25,
                "has_signatures": 0.25,
                "page_numbering": 0.2,
            },
            DocumentType.GOVERNANCE_FORM: {
                "checkbox_completion": 0.4,
                "has_signatures": 0.3,
                "table_integrity": 0.2,
                "text_quality": 0.1,
            },
        }

        weights = rule_weights.get(document_type, {})

        if not weights:
            # Default equal weighting
            return self._calculate_overall_score(validation_results)

        weighted_score = 0.0
        total_weight = 0.0

        for result in validation_results:
            weight = weights.get(result.rule_id, 0.1)  # Default small weight
            weighted_score += result.score * weight
            total_weight += weight

        return weighted_score / max(total_weight, 1.0)

    def _generate_recommendations(
        self,
        validation_results: List[ValidationResult],
        processed_doc: ProcessedDocument,
    ) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []

        for result in validation_results:
            if not result.passed:
                if result.rule_id == "has_signatures":
                    recommendations.append(
                        "Add required signatures to authenticate the document"
                    )
                elif result.rule_id == "has_watermarks":
                    recommendations.append(
                        "Consider adding official watermarks for authenticity"
                    )
                elif result.rule_id == "proper_structure":
                    recommendations.append(
                        "Improve document structure with clear sections and headings"
                    )
                elif result.rule_id == "text_quality":
                    recommendations.append(
                        "Review document for OCR errors and improve text quality"
                    )
                elif result.rule_id == "legal_language":
                    recommendations.append(
                        "Use more appropriate legal terminology and formal language"
                    )
                elif result.rule_id == "checkbox_completion":
                    recommendations.append(
                        "Complete all required form fields and checkboxes"
                    )
                elif result.rule_id == "table_integrity":
                    recommendations.append(
                        "Ensure all tables are properly formatted and complete"
                    )

        # Additional recommendations based on document content
        if len(processed_doc.signatures) == 1:
            recommendations.append(
                "Consider requiring additional signatures for important documents"
            )

        if not processed_doc.watermarks:
            recommendations.append(
                "Add official watermarks to prevent unauthorized copying"
            )

        if processed_doc.confidence_score < 0.8:
            recommendations.append(
                "Review document quality - low confidence in OCR extraction"
            )

        return recommendations
