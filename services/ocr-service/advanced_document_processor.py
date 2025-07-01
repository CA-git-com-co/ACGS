#!/usr/bin/env python3
"""
Advanced Document Processing Pipeline for ACGS
Leverages Nanonets-OCR-s capabilities for comprehensive document analysis
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class DocumentElement:
    """Base class for document elements"""

    element_type: str
    content: str
    position: int
    confidence: float = 1.0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class Signature(DocumentElement):
    """Signature element with authentication details"""

    signatory: Optional[str] = None
    date_signed: Optional[str] = None
    signature_type: str = "handwritten"  # handwritten, digital, stamp


@dataclass
class Watermark(DocumentElement):
    """Watermark element for document authenticity"""

    watermark_type: str = "text"  # text, image, logo
    authenticity_level: str = "official"  # official, draft, copy


@dataclass
class LaTeXEquation(DocumentElement):
    """LaTeX equation with mathematical content"""

    equation_type: str = "inline"  # inline, display, numbered
    variables: List[str] = None

    def __post_init__(self):
        super().__post_init__()
        if self.variables is None:
            self.variables = []


@dataclass
class Table(DocumentElement):
    """Table element with structured data"""

    rows: int = 0
    columns: int = 0
    headers: List[str] = None
    data: List[List[str]] = None
    format_type: str = "html"  # html, markdown

    def __post_init__(self):
        super().__post_init__()
        if self.headers is None:
            self.headers = []
        if self.data is None:
            self.data = []


@dataclass
class Checkbox(DocumentElement):
    """Checkbox element with state information"""

    state: str = "unchecked"  # unchecked, checked, crossed
    label: Optional[str] = None
    form_field: Optional[str] = None


@dataclass
class Image(DocumentElement):
    """Image element with description"""

    description: str = ""
    caption: Optional[str] = None
    image_type: str = "embedded"  # embedded, referenced


@dataclass
class PageNumber(DocumentElement):
    """Page number element"""

    page_num: int = 1
    total_pages: Optional[int] = None
    format_style: str = "simple"  # simple, fraction


@dataclass
class ProcessedDocument:
    """Complete processed document with all extracted elements"""

    document_id: str
    raw_text: str
    processing_timestamp: datetime
    signatures: List[Signature]
    watermarks: List[Watermark]
    equations: List[LaTeXEquation]
    tables: List[Table]
    checkboxes: List[Checkbox]
    images: List[Image]
    page_numbers: List[PageNumber]
    metadata: Dict[str, Any]
    confidence_score: float = 0.0


class AdvancedDocumentProcessor:
    """
    Advanced document processor leveraging Nanonets-OCR-s capabilities
    Provides comprehensive parsing and structuring of document elements
    """

    def __init__(self):
        self.element_extractors = {
            "signature": self._extract_signatures,
            "watermark": self._extract_watermarks,
            "equation": self._extract_equations,
            "table": self._extract_tables,
            "checkbox": self._extract_checkboxes,
            "image": self._extract_images,
            "page_number": self._extract_page_numbers,
        }

    def process_document(
        self, raw_text: str, document_id: str = None
    ) -> ProcessedDocument:
        """
        Process a document and extract all structured elements

        Args:
            raw_text: Raw OCR output from Nanonets-OCR-s
            document_id: Optional document identifier

        Returns:
            ProcessedDocument with all extracted elements
        """
        if document_id is None:
            document_id = f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        logger.info(f"Processing document {document_id}")

        # Extract all element types
        signatures = self._extract_signatures(raw_text)
        watermarks = self._extract_watermarks(raw_text)
        equations = self._extract_equations(raw_text)
        tables = self._extract_tables(raw_text)
        checkboxes = self._extract_checkboxes(raw_text)
        images = self._extract_images(raw_text)
        page_numbers = self._extract_page_numbers(raw_text)

        # Calculate overall confidence score
        confidence_score = self._calculate_confidence_score(
            signatures, watermarks, equations, tables, checkboxes, images, page_numbers
        )

        # Extract metadata
        metadata = self._extract_metadata(raw_text)

        processed_doc = ProcessedDocument(
            document_id=document_id,
            raw_text=raw_text,
            processing_timestamp=datetime.now(),
            signatures=signatures,
            watermarks=watermarks,
            equations=equations,
            tables=tables,
            checkboxes=checkboxes,
            images=images,
            page_numbers=page_numbers,
            metadata=metadata,
            confidence_score=confidence_score,
        )

        logger.info(
            f"Document {document_id} processed successfully. "
            f"Found: {len(signatures)} signatures, {len(watermarks)} watermarks, "
            f"{len(equations)} equations, {len(tables)} tables, "
            f"{len(checkboxes)} checkboxes, {len(images)} images"
        )

        return processed_doc

    def _extract_signatures(self, text: str) -> List[Signature]:
        """Extract signature elements from text"""
        signatures = []

        # Pattern for signature tags
        signature_pattern = r"<signature>(.*?)</signature>"
        matches = re.finditer(signature_pattern, text, re.DOTALL | re.IGNORECASE)

        for match in matches:
            content = match.group(1).strip()
            position = match.start()

            # Try to extract signatory name and date
            signatory = self._extract_signatory_name(content)
            date_signed = self._extract_signature_date(content)

            signature = Signature(
                element_type="signature",
                content=content,
                position=position,
                signatory=signatory,
                date_signed=date_signed,
                metadata={"raw_match": match.group(0)},
            )
            signatures.append(signature)

        return signatures

    def _extract_watermarks(self, text: str) -> List[Watermark]:
        """Extract watermark elements from text"""
        watermarks = []

        # Pattern for watermark tags
        watermark_pattern = r"<watermark>(.*?)</watermark>"
        matches = re.finditer(watermark_pattern, text, re.DOTALL | re.IGNORECASE)

        for match in matches:
            content = match.group(1).strip()
            position = match.start()

            # Determine authenticity level based on content
            authenticity_level = (
                "official"
                if any(
                    keyword in content.lower()
                    for keyword in ["official", "certified", "authentic", "original"]
                )
                else "draft"
            )

            watermark = Watermark(
                element_type="watermark",
                content=content,
                position=position,
                authenticity_level=authenticity_level,
                metadata={"raw_match": match.group(0)},
            )
            watermarks.append(watermark)

        return watermarks

    def _extract_equations(self, text: str) -> List[LaTeXEquation]:
        """Extract LaTeX equations from text"""
        equations = []

        # Patterns for different equation types
        equation_patterns = [
            (r"\$\$(.*?)\$\$", "display"),  # Display equations
            (r"\$(.*?)\$", "inline"),  # Inline equations
            (
                r"\\begin\{equation\}(.*?)\\end\{equation\}",
                "numbered",
            ),  # Numbered equations
        ]

        for pattern, eq_type in equation_patterns:
            matches = re.finditer(pattern, text, re.DOTALL)

            for match in matches:
                content = match.group(1).strip()
                position = match.start()

                # Extract variables from equation
                variables = self._extract_equation_variables(content)

                equation = LaTeXEquation(
                    element_type="equation",
                    content=content,
                    position=position,
                    equation_type=eq_type,
                    variables=variables,
                    metadata={"raw_match": match.group(0)},
                )
                equations.append(equation)

        return equations

    def _extract_tables(self, text: str) -> List[Table]:
        """Extract HTML tables from text"""
        tables = []

        # Pattern for HTML tables
        table_pattern = r"<table[^>]*>(.*?)</table>"
        matches = re.finditer(table_pattern, text, re.DOTALL | re.IGNORECASE)

        for match in matches:
            content = match.group(1).strip()
            position = match.start()

            # Parse table structure
            rows, columns, headers, data = self._parse_html_table(content)

            table = Table(
                element_type="table",
                content=match.group(0),
                position=position,
                rows=rows,
                columns=columns,
                headers=headers,
                data=data,
                format_type="html",
                metadata={"raw_match": match.group(0)},
            )
            tables.append(table)

        return tables

    def _extract_checkboxes(self, text: str) -> List[Checkbox]:
        """Extract checkbox elements from text"""
        checkboxes = []

        # Checkbox patterns with their states
        checkbox_patterns = [
            (r"☐", "unchecked"),
            (r"☑", "checked"),
            (r"☒", "crossed"),
            (r"\[ \]", "unchecked"),
            (r"\[x\]", "checked"),
            (r"\[X\]", "checked"),
        ]

        for pattern, state in checkbox_patterns:
            matches = re.finditer(pattern, text)

            for match in matches:
                position = match.start()

                # Extract label/context around checkbox
                label = self._extract_checkbox_label(text, position)

                checkbox = Checkbox(
                    element_type="checkbox",
                    content=match.group(0),
                    position=position,
                    state=state,
                    label=label,
                    metadata={"symbol": match.group(0)},
                )
                checkboxes.append(checkbox)

        return checkboxes

    def _extract_images(self, text: str) -> List[Image]:
        """Extract image elements from text"""
        images = []

        # Pattern for image tags
        image_pattern = r"<img[^>]*>(.*?)</img>"
        matches = re.finditer(image_pattern, text, re.DOTALL | re.IGNORECASE)

        for match in matches:
            content = match.group(1).strip()
            position = match.start()

            # Determine if it's a caption or description
            caption = content if len(content) < 100 else None
            description = content if len(content) >= 100 else content

            image = Image(
                element_type="image",
                content=content,
                position=position,
                description=description,
                caption=caption,
                metadata={"raw_match": match.group(0)},
            )
            images.append(image)

        return images

    def _extract_page_numbers(self, text: str) -> List[PageNumber]:
        """Extract page number elements from text"""
        page_numbers = []

        # Pattern for page number tags
        page_pattern = r"<page_number>(.*?)</page_number>"
        matches = re.finditer(page_pattern, text, re.DOTALL | re.IGNORECASE)

        for match in matches:
            content = match.group(1).strip()
            position = match.start()

            # Parse page number format
            page_num, total_pages, format_style = self._parse_page_number(content)

            page_number = PageNumber(
                element_type="page_number",
                content=content,
                position=position,
                page_num=page_num,
                total_pages=total_pages,
                format_style=format_style,
                metadata={"raw_match": match.group(0)},
            )
            page_numbers.append(page_number)

        return page_numbers

    # Helper methods for parsing specific elements

    def _extract_signatory_name(self, signature_content: str) -> Optional[str]:
        """Extract signatory name from signature content"""
        # Look for common patterns like "Signed by: Name" or just extract text
        patterns = [
            r"signed by:?\s*([^\n]+)",
            r"signature of:?\s*([^\n]+)",
            r"^([A-Z][a-z]+ [A-Z][a-z]+)",  # First Last name pattern
        ]

        for pattern in patterns:
            match = re.search(pattern, signature_content, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        # If no pattern matches, return the first line if it looks like a name
        first_line = signature_content.split("\n")[0].strip()
        if len(first_line) < 50 and " " in first_line:
            return first_line

        return None

    def _extract_signature_date(self, signature_content: str) -> Optional[str]:
        """Extract signature date from signature content"""
        # Common date patterns
        date_patterns = [
            r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b",
            r"\b(\d{4}[/-]\d{1,2}[/-]\d{1,2})\b",
            r"\b([A-Za-z]+ \d{1,2},? \d{4})\b",
        ]

        for pattern in date_patterns:
            match = re.search(pattern, signature_content)
            if match:
                return match.group(1)

        return None

    def _extract_equation_variables(self, equation_content: str) -> List[str]:
        """Extract variables from LaTeX equation"""
        # Simple variable extraction - single letters that aren't functions
        variable_pattern = r"\b([a-zA-Z])\b"
        variables = re.findall(variable_pattern, equation_content)

        # Filter out common LaTeX functions
        latex_functions = {"sin", "cos", "tan", "log", "ln", "exp", "max", "min"}
        variables = [v for v in variables if v not in latex_functions]

        return list(set(variables))  # Remove duplicates

    def _parse_html_table(
        self, table_content: str
    ) -> Tuple[int, int, List[str], List[List[str]]]:
        """Parse HTML table content to extract structure"""
        # Extract table rows
        row_pattern = r"<tr[^>]*>(.*?)</tr>"
        rows = re.findall(row_pattern, table_content, re.DOTALL | re.IGNORECASE)

        headers = []
        data = []

        for i, row in enumerate(rows):
            # Extract cells (th or td)
            cell_pattern = r"<t[hd][^>]*>(.*?)</t[hd]>"
            cells = re.findall(cell_pattern, row, re.DOTALL | re.IGNORECASE)

            # Clean cell content
            cells = [re.sub(r"<[^>]+>", "", cell).strip() for cell in cells]

            if i == 0:  # First row might be headers
                # Check if first row contains th tags
                if "<th" in row.lower():
                    headers = cells
                else:
                    data.append(cells)
            else:
                data.append(cells)

        num_rows = len(data)
        num_columns = max(len(row) for row in data) if data else 0

        return num_rows, num_columns, headers, data

    def _extract_checkbox_label(
        self, text: str, checkbox_position: int
    ) -> Optional[str]:
        """Extract label text associated with a checkbox"""
        # Look for text after the checkbox (next 100 characters)
        start = checkbox_position + 1
        end = min(len(text), start + 100)
        context = text[start:end]

        # Extract the first line or sentence
        lines = context.split("\n")
        if lines:
            label = lines[0].strip()
            # Remove common prefixes and clean up
            label = re.sub(r"^[:\-\s]+", "", label)
            if len(label) > 0 and len(label) < 80:
                return label

        return None

    def _parse_page_number(self, page_content: str) -> Tuple[int, Optional[int], str]:
        """Parse page number content to extract page info"""
        # Handle formats like "5", "5/10", "Page 5 of 10"

        # Try fraction format first
        fraction_match = re.search(r"(\d+)/(\d+)", page_content)
        if fraction_match:
            page_num = int(fraction_match.group(1))
            total_pages = int(fraction_match.group(2))
            return page_num, total_pages, "fraction"

        # Try "Page X of Y" format
        of_match = re.search(r"page\s+(\d+)\s+of\s+(\d+)", page_content, re.IGNORECASE)
        if of_match:
            page_num = int(of_match.group(1))
            total_pages = int(of_match.group(2))
            return page_num, total_pages, "verbose"

        # Try simple number
        number_match = re.search(r"(\d+)", page_content)
        if number_match:
            page_num = int(number_match.group(1))
            return page_num, None, "simple"

        return 1, None, "simple"

    def _calculate_confidence_score(self, *element_lists) -> float:
        """Calculate overall confidence score based on extracted elements"""
        total_elements = sum(len(elements) for elements in element_lists)

        if total_elements == 0:
            return 0.5  # Neutral confidence if no structured elements found

        # Base confidence increases with number of structured elements found
        base_confidence = min(0.9, 0.5 + (total_elements * 0.05))

        # Adjust based on element types
        confidence_adjustments = 0.0

        # Signatures and watermarks increase confidence (authenticity indicators)
        signatures, watermarks = element_lists[0], element_lists[1]
        if signatures:
            confidence_adjustments += 0.1
        if watermarks:
            confidence_adjustments += 0.05

        # Tables and equations indicate structured content
        tables, equations = element_lists[3], element_lists[2]
        if tables:
            confidence_adjustments += 0.05
        if equations:
            confidence_adjustments += 0.05

        final_confidence = min(1.0, base_confidence + confidence_adjustments)
        return round(final_confidence, 3)

    def _extract_metadata(self, text: str) -> Dict[str, Any]:
        """Extract document metadata from text"""
        metadata = {
            "text_length": len(text),
            "processing_timestamp": datetime.now().isoformat(),
            "has_structured_elements": self._has_structured_elements(text),
            "document_language": self._detect_language(text),
            "estimated_pages": self._estimate_page_count(text),
        }

        return metadata

    def _has_structured_elements(self, text: str) -> bool:
        """Check if text contains structured elements"""
        structured_patterns = [
            r"<signature>",
            r"<watermark>",
            r"<table[^>]*>",
            r"\$.*?\$",
            r"☐|☑|☒",
            r"<img[^>]*>",
            r"<page_number>",
        ]

        return any(
            re.search(pattern, text, re.IGNORECASE) for pattern in structured_patterns
        )

    def _detect_language(self, text: str) -> str:
        """Simple language detection based on common words"""
        # Very basic language detection - could be enhanced with proper libraries
        english_indicators = ["the", "and", "or", "of", "to", "in", "for", "with"]

        text_lower = text.lower()
        english_count = sum(1 for word in english_indicators if word in text_lower)

        return "english" if english_count >= 3 else "unknown"

    def _estimate_page_count(self, text: str) -> int:
        """Estimate number of pages based on text length and page number tags"""
        # Check for explicit page numbers first
        page_numbers = re.findall(r"<page_number>(\d+)(?:/(\d+))?</page_number>", text)
        if page_numbers:
            max_page = max(int(match[0]) for match in page_numbers)
            return max_page

        # Estimate based on text length (rough approximation)
        # Assume ~500 words per page, ~5 characters per word
        estimated_pages = max(1, len(text) // 2500)
        return estimated_pages

    def to_dict(self, processed_doc: ProcessedDocument) -> Dict[str, Any]:
        """Convert ProcessedDocument to dictionary for serialization"""
        return asdict(processed_doc)

    def to_json(self, processed_doc: ProcessedDocument) -> str:
        """Convert ProcessedDocument to JSON string"""
        doc_dict = self.to_dict(processed_doc)
        # Handle datetime serialization
        doc_dict["processing_timestamp"] = doc_dict["processing_timestamp"].isoformat()
        return json.dumps(doc_dict, indent=2, ensure_ascii=False)
