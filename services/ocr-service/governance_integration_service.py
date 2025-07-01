#!/usr/bin/env python3
"""
Governance Integration Service for ACGS
Provides high-level integration between OCR processing and governance workflows
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

try:
    from .advanced_document_processor import (
        AdvancedDocumentProcessor,
        ProcessedDocument,
    )
    from .governance_document_validator import (
        GovernanceDocumentValidator,
        DocumentType,
        ValidationLevel,
        DocumentValidationReport,
    )
    from .ocr_integration import EnhancedOCRIntegration
except ImportError:
    from advanced_document_processor import AdvancedDocumentProcessor, ProcessedDocument
    from governance_document_validator import (
        GovernanceDocumentValidator,
        DocumentType,
        ValidationLevel,
        DocumentValidationReport,
    )
    from ocr_integration import EnhancedOCRIntegration

logger = logging.getLogger(__name__)


class GovernanceIntegrationService:
    """
    High-level service that integrates OCR processing with governance workflows
    Provides a unified interface for document processing, validation, and analysis
    """

    def __init__(self, ocr_host: str = None, ocr_port: int = None):
        """Initialize the governance integration service"""
        self.ocr_integration = EnhancedOCRIntegration(ocr_host, ocr_port)
        self.document_processor = AdvancedDocumentProcessor()
        self.validator = GovernanceDocumentValidator()

        logger.info("Governance Integration Service initialized")

    def process_governance_document(
        self,
        image_data: Any,
        document_type: str = "general",
        validation_level: str = "standard",
        include_validation: bool = True,
    ) -> Dict[str, Any]:
        """
        Complete governance document processing pipeline

        Args:
            image_data: Document image data (path, URL, or bytes)
            document_type: Type of governance document
            validation_level: Level of validation to perform
            include_validation: Whether to include validation in results

        Returns:
            Complete processing and validation results
        """
        start_time = datetime.now()

        try:
            # Step 1: OCR Processing
            logger.info(f"Processing {document_type} document with OCR")
            ocr_result = self.ocr_integration.analyze_document(
                image_data, document_type
            )

            if not ocr_result.get("success", False):
                return {
                    "success": False,
                    "error": "OCR processing failed",
                    "details": ocr_result,
                }

            # Step 2: Extract structured elements
            processed_doc = self.ocr_integration.extract_structured_elements(
                image_data, document_type
            )

            # Step 3: Validation (if requested)
            validation_report = None
            if include_validation:
                try:
                    doc_type = (
                        DocumentType(document_type)
                        if document_type in [dt.value for dt in DocumentType]
                        else DocumentType.OFFICIAL_DOCUMENT
                    )
                    val_level = (
                        ValidationLevel(validation_level)
                        if validation_level in [vl.value for vl in ValidationLevel]
                        else ValidationLevel.STANDARD
                    )

                    logger.info(
                        f"Validating document as {doc_type.value} with {val_level.value} level"
                    )
                    validation_report = self.validator.validate_document(
                        processed_doc, doc_type, val_level
                    )

                except Exception as e:
                    logger.warning(f"Validation failed: {str(e)}")
                    validation_report = None

            # Step 4: Compile results
            processing_time = (datetime.now() - start_time).total_seconds()

            result = {
                "success": True,
                "processing_time": processing_time,
                "document_info": {
                    "document_id": processed_doc.document_id,
                    "document_type": document_type,
                    "confidence_score": processed_doc.confidence_score,
                    "text_length": len(processed_doc.raw_text),
                },
                "ocr_results": {
                    "raw_text": processed_doc.raw_text,
                    "structured_elements": {
                        "signatures": len(processed_doc.signatures),
                        "watermarks": len(processed_doc.watermarks),
                        "equations": len(processed_doc.equations),
                        "tables": len(processed_doc.tables),
                        "checkboxes": len(processed_doc.checkboxes),
                        "images": len(processed_doc.images),
                        "page_numbers": len(processed_doc.page_numbers),
                    },
                },
                "processed_document": self.document_processor.to_dict(processed_doc),
                "metadata": {
                    "processing_timestamp": datetime.now().isoformat(),
                    "service_version": "1.0.0",
                    "ocr_model": "nanonets/Nanonets-OCR-s",
                },
            }

            # Add validation results if available
            if validation_report:
                result["validation"] = {
                    "overall_score": validation_report.overall_score,
                    "authenticity_score": validation_report.authenticity_score,
                    "compliance_score": validation_report.compliance_score,
                    "passed_rules": validation_report.passed_rules,
                    "total_rules": validation_report.total_rules,
                    "recommendations": validation_report.recommendations,
                    "validation_level": validation_report.validation_level.value,
                    "detailed_results": [
                        {
                            "rule_id": vr.rule_id,
                            "passed": vr.passed,
                            "score": vr.score,
                            "message": vr.message,
                        }
                        for vr in validation_report.validation_results
                    ],
                }

            logger.info(f"Document processing completed in {processing_time:.2f}s")
            return result

        except Exception as e:
            logger.error(f"Error in governance document processing: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "processing_time": (datetime.now() - start_time).total_seconds(),
            }

    def analyze_document_authenticity(self, image_data: Any) -> Dict[str, Any]:
        """
        Specialized analysis for document authenticity

        Args:
            image_data: Document image data

        Returns:
            Authenticity analysis results
        """
        try:
            # Use official document processing for authenticity analysis
            authenticity_result = self.ocr_integration.get_document_authenticity_score(
                image_data
            )

            # Get detailed structured analysis
            processed_doc = self.ocr_integration.extract_structured_elements(
                image_data, "official_document"
            )

            # Enhanced authenticity analysis
            authenticity_factors = {
                "signature_analysis": {
                    "count": len(processed_doc.signatures),
                    "signatures": [
                        {
                            "content": sig.content,
                            "signatory": sig.signatory,
                            "date_signed": sig.date_signed,
                            "signature_type": sig.signature_type,
                        }
                        for sig in processed_doc.signatures
                    ],
                },
                "watermark_analysis": {
                    "count": len(processed_doc.watermarks),
                    "watermarks": [
                        {
                            "content": wm.content,
                            "authenticity_level": wm.authenticity_level,
                            "watermark_type": wm.watermark_type,
                        }
                        for wm in processed_doc.watermarks
                    ],
                },
                "document_integrity": {
                    "page_numbering": len(processed_doc.page_numbers) > 0,
                    "structured_content": processed_doc.confidence_score > 0.8,
                    "text_quality": len(processed_doc.raw_text) > 100,
                },
            }

            return {
                "success": True,
                "authenticity_score": authenticity_result["authenticity_score"],
                "confidence": authenticity_result["confidence"],
                "authenticity_factors": authenticity_factors,
                "recommendations": self._generate_authenticity_recommendations(
                    authenticity_factors
                ),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error in authenticity analysis: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def extract_governance_metadata(
        self, image_data: Any, document_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Extract governance-specific metadata from document

        Args:
            image_data: Document image data
            document_type: Type of governance document

        Returns:
            Governance metadata
        """
        try:
            processed_doc = self.ocr_integration.extract_structured_elements(
                image_data, document_type
            )

            # Extract governance-specific information
            governance_metadata = {
                "document_classification": {
                    "type": document_type,
                    "confidence": processed_doc.confidence_score,
                    "estimated_pages": processed_doc.metadata.get("estimated_pages", 1),
                },
                "authority_markers": {
                    "signatures": len(processed_doc.signatures),
                    "official_seals": (
                        len(processed_doc.seals)
                        if hasattr(processed_doc, "seals")
                        else 0
                    ),
                    "watermarks": len(processed_doc.watermarks),
                },
                "content_analysis": {
                    "has_legal_language": self._detect_legal_language(
                        processed_doc.raw_text
                    ),
                    "has_policy_structure": self._detect_policy_structure(
                        processed_doc.raw_text
                    ),
                    "has_voting_elements": len(processed_doc.checkboxes) > 0,
                    "has_tabular_data": len(processed_doc.tables) > 0,
                },
                "compliance_indicators": {
                    "proper_formatting": processed_doc.confidence_score > 0.7,
                    "complete_signatures": len(processed_doc.signatures) > 0,
                    "official_authentication": len(processed_doc.watermarks) > 0,
                },
            }

            return {
                "success": True,
                "governance_metadata": governance_metadata,
                "document_id": processed_doc.document_id,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error extracting governance metadata: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def _generate_authenticity_recommendations(
        self, authenticity_factors: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on authenticity analysis"""
        recommendations = []

        sig_count = authenticity_factors["signature_analysis"]["count"]
        wm_count = authenticity_factors["watermark_analysis"]["count"]

        if sig_count == 0:
            recommendations.append(
                "Document lacks signatures - verify authenticity through alternative means"
            )
        elif sig_count == 1:
            recommendations.append(
                "Single signature present - consider requiring additional authorization"
            )

        if wm_count == 0:
            recommendations.append(
                "No watermarks detected - verify document is from official source"
            )

        if not authenticity_factors["document_integrity"]["page_numbering"]:
            recommendations.append(
                "Missing page numbers - verify document completeness"
            )

        if not authenticity_factors["document_integrity"]["structured_content"]:
            recommendations.append(
                "Low confidence in content structure - manual review recommended"
            )

        return recommendations

    def _detect_legal_language(self, text: str) -> bool:
        """Detect presence of legal language patterns"""
        legal_indicators = [
            "whereas",
            "therefore",
            "hereby",
            "pursuant",
            "notwithstanding",
            "shall",
            "constitution",
            "amendment",
            "article",
            "section",
        ]

        text_lower = text.lower()
        return sum(1 for indicator in legal_indicators if indicator in text_lower) >= 3

    def _detect_policy_structure(self, text: str) -> bool:
        """Detect policy document structure"""
        policy_indicators = [
            "policy",
            "procedure",
            "guideline",
            "standard",
            "requirement",
            "compliance",
            "implementation",
            "enforcement",
            "violation",
        ]

        text_lower = text.lower()
        return sum(1 for indicator in policy_indicators if indicator in text_lower) >= 2
