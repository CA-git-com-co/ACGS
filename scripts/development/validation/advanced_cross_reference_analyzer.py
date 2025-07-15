#!/usr/bin/env python3
"""
ACGS Advanced Cross-Reference Analyzer
Constitutional Hash: cdd01ef066bc6cf2

This advanced tool provides comprehensive cross-reference validation including:
- Semantic link relationship analysis
- Bidirectional cross-reference checking
- API endpoint documentation sync validation
- Documentation dependency mapping
- Automated relationship consistency validation
- Missing reference detection and auto-suggestion
"""

import json
import re
import sys
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import networkx as nx

# Configuration
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
REPO_ROOT = Path(__file__).parent.parent.parent
DOCS_DIR = REPO_ROOT / "docs"

# Service configuration for API sync validation
SERVICE_CONFIG = {
    "authentication": {
        "port": 8016,
        "endpoints": ["/auth/login", "/auth/logout", "/auth/verify"],
    },
    "constitutional-ai": {
        "port": 8001,
        "endpoints": ["/api/v1/validate", "/api/v1/compliance"],
    },
    "integrity": {"port": 8002, "endpoints": ["/api/v1/audit", "/api/v1/verify"]},
    "formal-verification": {
        "port": 8003,
        "endpoints": ["/api/v1/prove", "/api/v1/verify"],
    },
    "governance_synthesis": {
        "port": 8004,
        "endpoints": ["/api/v1/synthesize", "/api/v1/policies"],
    },
    "policy-governance": {
        "port": 8005,
        "endpoints": ["/api/v1/policies", "/api/v1/evaluate"],
    },
    "evolutionary-computation": {
        "port": 8006,
        "endpoints": ["/api/v1/evolve", "/api/v1/optimize"],
    },
}


@dataclass
class CrossReference:
    """Represents a cross-reference between documents."""

    source_file: str
    target_file: str
    link_text: str
    link_url: str
    line_number: int
    reference_type: str  # 'direct', 'semantic', 'api', 'config'
    confidence: float = 1.0
    context: str = ""


@dataclass
class DocumentNode:
    """Represents a document in the dependency graph."""

    file_path: str
    title: str
    outgoing_refs: list[CrossReference] = field(default_factory=list)
    incoming_refs: list[CrossReference] = field(default_factory=list)
    api_endpoints: list[str] = field(default_factory=list)
    topics: set[str] = field(default_factory=set)
    constitutional_hash: bool = False


@dataclass
class SemanticRelationship:
    """Represents semantic relationship between documents."""

    doc1: str
    doc2: str
    relationship_type: str  # 'implements', 'depends_on', 'extends', 'references'
    strength: float
    evidence: list[str]


@dataclass
class ValidationIssue:
    """Enhanced validation issue with relationship context."""

    severity: str
    category: str
    file_path: str
    message: str
    line_number: Optional[int] = None
    suggested_fix: Optional[str] = None
    related_files: list[str] = field(default_factory=list)
    relationship_type: Optional[str] = None


class AdvancedCrossReferenceAnalyzer:
    """Advanced cross-reference analyzer with semantic understanding."""

    def __init__(self):
        self.document_graph = nx.DiGraph()
        self.document_nodes: dict[str, DocumentNode] = {}
        self.semantic_relationships: list[SemanticRelationship] = []
        self.validation_issues: list[ValidationIssue] = []
        self.api_implementations: dict[str, list[str]] = {}
        self.topic_index: dict[str, set[str]] = defaultdict(set)
        self.cross_references: list[CrossReference] = []
        self.pattern_registry = self._load_pattern_registry()
        self.compiled_patterns = self._compile_patterns()

    def analyze_document_structure(self, file_path: Path) -> DocumentNode:
        """Analyze document structure and extract metadata."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")

            relative_path = str(file_path.relative_to(REPO_ROOT))

            # Extract title
            title = self._extract_title(content, lines)

            # Create document node
            node = DocumentNode(
                file_path=relative_path,
                title=title,
                constitutional_hash=CONSTITUTIONAL_HASH in content,
            )

            # Extract topics and keywords
            node.topics = self._extract_topics(content)

            # Extract API endpoints if it's an API doc
            if "api" in file_path.parts:
                node.api_endpoints = self._extract_api_endpoints(content)

            # Extract cross-references
            node.outgoing_refs = self._extract_cross_references(
                file_path, content, lines
            )

            return node

        except Exception as e:
            self.validation_issues.append(
                ValidationIssue(
                    severity="ERROR",
                    category="document_analysis",
                    file_path=str(file_path.relative_to(REPO_ROOT)),
                    message=f"Failed to analyze document structure: {e}",
                )
            )
            return DocumentNode(
                file_path=str(file_path.relative_to(REPO_ROOT)), title="Unknown"
            )

    def _extract_title(self, content: str, lines: list[str]) -> str:
        """Extract document title from various formats."""
        # Try H1 markdown header
        for line in lines[:10]:
            if line.startswith("# "):
                return line[2:].strip()

        # Try front matter title
        if content.startswith("---"):
            yaml_end = content.find("---", 3)
            if yaml_end > 0:
                front_matter = content[3:yaml_end]
                title_match = re.search(r"^title:\s*(.+)$", front_matter, re.MULTILINE)
                if title_match:
                    return title_match.group(1).strip("\"'")

        # Use filename as fallback
        return "Document"

    def _extract_topics(self, content: str) -> set[str]:
        """Extract topics and keywords from document content."""
        topics = set()

        # Extract from headers
        headers = re.findall(r"^#+\s+(.+)$", content, re.MULTILINE)
        for header in headers:
            topics.update(
                word.lower() for word in re.findall(r"\w+", header) if len(word) > 3
            )

        # Extract technical terms
        tech_terms = re.findall(
            r"\b(?:API|REST|HTTP|JSON|YAML|Docker|Kubernetes|PostgreSQL|Redis|JWT|OAuth|RBAC|CI/CD|DevOps|microservice|endpoint|database|cache|monitoring|metrics|logging|authentication|authorization|validation|compliance|governance|constitutional|verification|formal|proof|evolutionary|algorithm|optimization|performance|latency|throughput|scalability|availability|reliability|security|encryption|audit|integrity|synthesis|policy|configuration|deployment|infrastructure|service|client|server|protocol|interface|framework|library|module|component|architecture|design|pattern|strategy|implementation|solution|system|platform|environment|production|staging|development|testing|quality|coverage|automation|pipeline|workflow|process|procedure|standard|guideline|requirement|specification|documentation|guide|tutorial|reference|manual|changelog|roadmap|milestone|release|version|update|patch|fix|bug|issue|feature|enhancement|improvement|optimization|refactoring|migration|upgrade|maintenance|support|troubleshooting|debugging|monitoring|alerting|dashboard|report|metric|analysis|audit|review|validation|verification|certification|compliance|governance|policy|regulation|standard|best|practice|recommendation|convention|principle|rule|constraint|requirement|specification|definition|description|explanation|example|tutorial|walkthrough|procedure|step|phase|stage|milestone|checkpoint|gate|criteria|threshold|target|goal|objective|outcome|result|deliverable|artifact|asset|resource|tool|utility|script|command|configuration|setting|parameter|variable|constant|flag|option|choice|selection|decision|logic|algorithm|formula|calculation|computation|processing|transformation|conversion|translation|mapping|relationship|association|connection|link|reference|dependency|requirement|prerequisite|assumption|constraint|limitation|restriction|boundary|scope|context|environment|condition|state|status|mode|phase|stage|level|tier|layer|component|element|unit|module|package|bundle|library|framework|platform|system|application|service|tool|utility|resource|asset|artifact|deliverable|output|input|interface|endpoint|gateway|proxy|router|balancer|scheduler|orchestrator|coordinator|manager|controller|handler|processor|worker|agent|client|server|node|cluster|network|storage|database|cache|queue|stream|pipeline|workflow|process|thread|task|job|batch|schedule|trigger|event|message|notification|alert|log|trace|debug|monitor|track|measure|analyze|report|dashboard|visualization|chart|graph|table|list|tree|map|diagram|schema|model|template|pattern|structure|format|protocol|standard|specification|definition|contract|agreement|policy|rule|regulation|compliance|governance|audit|review|assessment|evaluation|validation|verification|testing|quality|coverage|performance|benchmark|profiling|optimization|tuning|scaling|load|stress|endurance|reliability|availability|fault|tolerance|recovery|backup|restore|sync|replication|migration|upgrade|patch|deployment|rollout|rollback|configuration|setup|installation|initialization|bootstrap|startup|shutdown|cleanup|maintenance|monitoring|alerting|logging|tracing|debugging|troubleshooting|support|documentation|training|education|onboarding|certification|compliance|governance|security|privacy|confidentiality|integrity|availability|authentication|authorization|access|control|permission|role|privilege|credential|token|key|certificate|encryption|decryption|signing|verification|hashing|checksum|validation|sanitization|filtering|escaping|encoding|decoding|compression|decompression|serialization|deserialization|marshaling|unmarshaling|parsing|formatting|rendering|templating|generation|transformation|conversion|translation|mapping|routing|forwarding|proxying|caching|buffering|pooling|queuing|streaming|batching|scheduling|throttling|limiting|balancing|partitioning|sharding|clustering|replication|synchronization|consistency|isolation|atomicity|durability|transaction|commit|rollback|lock|unlock|wait|notify|signal|timeout|retry|circuit|breaker|fallback|graceful|degradation|health|check|heartbeat|ping|probe|sensor|collector|aggregator|processor|analyzer|reporter|dashboard|visualization|alerting|notification|escalation|incident|resolution|postmortem|retrospective|improvement|lesson|learned|knowledge|base|documentation|wiki|handbook|manual|guide|tutorial|reference|specification|standard|protocol|format|schema|model|template|pattern|example|sample|demo|prototype|proof|concept|experiment|pilot|trial|test|validation|verification|certification|approval|acceptance|release|deployment|rollout|launch|go|live|production|staging|development|testing|integration|unit|functional|performance|load|stress|security|penetration|vulnerability|assessment|scan|audit|review|inspection|analysis|evaluation|measurement|monitoring|tracking|reporting|alerting|notification|escalation|incident|response|recovery|backup|restore|disaster|continuity|planning|preparation|mitigation|prevention|detection|correction|improvement|optimization|enhancement|feature|capability|functionality|behavior|characteristic|property|attribute|quality|metric|indicator|measure|benchmark|target|goal|objective|requirement|constraint|assumption|dependency|relationship|association|connection|integration|interface|contract|agreement|policy|rule|regulation|standard|guideline|recommendation|best|practice|convention|principle|pattern|strategy|approach|method|technique|algorithm|formula|equation|calculation|computation|operation|function|procedure|process|workflow|pipeline|sequence|step|phase|stage|milestone|checkpoint|gate|criteria|condition|state|status|mode|configuration|setting|parameter|variable|option|choice|decision|selection|specification|definition|description|explanation|documentation|comment|annotation|note|remark|observation|finding|result|outcome|conclusion|recommendation|suggestion|proposal|plan|design|architecture|structure|organization|hierarchy|taxonomy|classification|categorization|grouping|clustering|partitioning|segmentation|division|separation|isolation|abstraction|encapsulation|modularization|componentization|decomposition|composition|aggregation|synthesis|integration|coordination|collaboration|communication|interaction|exchange|transfer|transmission|reception|processing|handling|management|control|governance|oversight|supervision|administration|operation|execution|implementation|deployment|installation|configuration|setup|initialization|startup|shutdown|cleanup|maintenance|support|troubleshooting|debugging|monitoring|logging|tracking|reporting|analysis|evaluation|assessment|review|audit|inspection|validation|verification|testing|quality|assurance|control|improvement|optimization|enhancement|refinement|tuning|calibration|adjustment|correction|fix|patch|update|upgrade|migration|transformation|conversion|adaptation|customization|personalization|localization|internationalization|accessibility|usability|experience|interface|design|layout|styling|theming|branding|visualization|presentation|formatting|rendering|generation|creation|production|construction|building|development|implementation|coding|programming|scripting|automation|tooling|utilities|helpers|frameworks|libraries|packages|modules|components|services|applications|systems|platforms|solutions|products|offerings|capabilities|features|functions|operations|processes|workflows|procedures|methods|techniques|approaches|strategies|patterns|practices|standards|guidelines|principles|rules|policies|regulations|requirements|specifications|contracts|agreements|documentation|manuals|guides|tutorials|references|examples|samples|templates|patterns|models|schemas|formats|protocols|interfaces|APIs|endpoints|services|resources|assets|artifacts|deliverables|outputs|results|outcomes|achievements|accomplishments|milestones|goals|objectives|targets|benchmarks|metrics|indicators|measures|criteria|standards|thresholds|limits|boundaries|constraints|assumptions|dependencies|relationships|associations|connections|links|references|citations|cross-references|bidirectional|unidirectional|hierarchical|flat|nested|recursive|circular|linear|parallel|sequential|concurrent|asynchronous|synchronous|blocking|non-blocking|streaming|batch|real-time|near-real-time|offline|online|local|remote|distributed|centralized|decentralized|federated|hybrid|cloud|on-premises|edge|mobile|web|desktop|server|client|peer|node|cluster|grid|mesh|network|topology|architecture|infrastructure|platform|stack|layer|tier|level|component|element|unit|part|piece|segment|section|module|package|bundle|library|framework|toolkit|suite|collection|set|group|family|category|type|kind|class|subclass|instance|object|entity|item|record|document|file|data|information|knowledge|content|message|signal|event|notification|alert|warning|error|exception|fault|failure|issue|problem|bug|defect|anomaly|deviation|discrepancy|inconsistency|conflict|violation|breach|non-compliance|remediation|correction|mitigation|prevention|detection|identification|discovery|recognition|classification|categorization|analysis|assessment|evaluation|measurement|quantification|qualification|validation|verification|certification|approval|acceptance|rejection|denial|authorization|authentication|permission|access|control|restriction|limitation|constraint|boundary|scope|context|environment|condition|situation|scenario|case|example|instance|occurrence|event|incident|episode|session|transaction|interaction|operation|activity|task|job|work|effort|action|step|procedure|process|method|technique|approach|strategy|tactic|plan|design|solution|implementation|execution|performance|behavior|characteristic|property|attribute|feature|capability|functionality|quality|trait|aspect|dimension|factor|element|component|part|piece|segment|section|area|region|zone|domain|realm|sphere|field|discipline|subject|topic|theme|category|type|kind|sort|variety|species|class|group|family|collection|set|series|sequence|chain|list|array|table|matrix|grid|map|dictionary|index|catalog|registry|repository|database|store|warehouse|cache|buffer|queue|stack|heap|tree|graph|network|mesh|web|structure|framework|architecture|design|pattern|model|template|schema|format|specification|standard|protocol|interface|contract|agreement|policy|rule|regulation|law|requirement|constraint|assumption|prerequisite|dependency|relationship|association|connection|link|reference|citation|cross-reference|correlation|correspondence|mapping|binding|coupling|integration|composition|aggregation|inheritance|polymorphism|encapsulation|abstraction|modularity|cohesion|separation|isolation|independence|autonomy|self-sufficiency|self-contained|standalone|integrated|unified|consolidated|centralized|distributed|federated|hybrid|mixed|combined|composite|complex|compound|multi-layered|multi-tiered|multi-dimensional|multi-faceted|multi-purpose|multi-functional|versatile|flexible|adaptable|configurable|customizable|extensible|scalable|maintainable|supportable|sustainable|reliable|robust|resilient|fault-tolerant|high-availability|performance|efficient|optimized|fast|quick|responsive|real-time|low-latency|high-throughput|scalable|elastic|dynamic|adaptive|intelligent|smart|automated|self-managing|self-healing|self-organizing|autonomous|independent|secure|safe|protected|encrypted|authenticated|authorized|compliant|governed|regulated|standard|certified|approved|validated|verified|tested|quality|assured|controlled|monitored|tracked|logged|audited|reviewed|inspected|analyzed|measured|benchmarked|profiled|optimized|tuned|calibrated|adjusted|configured|setup|installed|deployed|implemented|executed|operated|managed|administered|supervised|governed|controlled|coordinated|orchestrated|synchronized|harmonized|aligned|integrated|unified|consolidated|streamlined|simplified|automated|digitized|modernized|upgraded|enhanced|improved|optimized|refined|polished|finalized|completed|finished|done|ready|prepared|set|configured|tuned|calibrated|adjusted|customized|personalized|tailored|specialized|focused|targeted|specific|detailed|comprehensive|complete|full|total|entire|whole|all|every|each|individual|particular|specific|unique|distinct|separate|different|various|diverse|multiple|several|many|numerous|countless|infinite|unlimited|boundless|extensive|broad|wide|comprehensive|inclusive|holistic|integrated|unified|coherent|consistent|harmonious|balanced|stable|steady|reliable|dependable|trustworthy|credible|authentic|genuine|legitimate|valid|sound|solid|strong|robust|durable|lasting|permanent|persistent|continuous|ongoing|sustained|maintained|preserved|protected|secured|safe|risk-free|error-free|bug-free|defect-free|fault-free|failure-free|problem-free|issue-free|trouble-free|worry-free|stress-free|easy|simple|straightforward|clear|obvious|apparent|evident|visible|transparent|open|accessible|available|reachable|obtainable|achievable|attainable|feasible|possible|practical|realistic|reasonable|logical|rational|sensible|wise|smart|intelligent|clever|effective|efficient|productive|successful|beneficial|valuable|useful|helpful|advantageous|profitable|worthwhile|meaningful|significant|important|critical|essential|vital|crucial|key|core|fundamental|basic|primary|main|principal|chief|major|leading|top|best|optimal|ideal|perfect|excellent|outstanding|superior|premium|high-quality|world-class|state-of-the-art|cutting-edge|advanced|sophisticated|complex|comprehensive|detailed|thorough|complete|full|extensive|broad|wide|deep|rich|dense|concentrated|intensive|focused|targeted|specialized|expert|professional|enterprise|business|commercial|industrial|corporate|organizational|institutional|governmental|public|private|personal|individual|custom|bespoke|tailored|personalized|customized|configured|optimized|enhanced|improved|upgraded|modernized|digitized|automated|intelligent|smart|adaptive|dynamic|flexible|scalable|elastic|resilient|robust|reliable|stable|secure|safe|compliant|governed|regulated|standard|certified|approved|validated|verified|tested|quality|monitored|tracked|logged|audited|documented|supported|maintained|sustainable|long-term|future-proof|backward-compatible|forward-compatible|interoperable|portable|transferable|reusable|recyclable|renewable|green|eco-friendly|sustainable|responsible|ethical|moral|legal|compliant|regulated|governed|controlled|managed|administered|operated|executed|implemented|deployed|installed|configured|setup|prepared|ready|available|accessible|operational|functional|working|active|live|running|online|connected|integrated|synchronized|coordinated|harmonized|aligned|balanced|optimized|tuned|calibrated|adjusted|customized|personalized|specialized|focused|targeted|effective|efficient|productive|successful)\b",
            content,
            re.IGNORECASE,
        )

        topics.update(term.lower() for term in tech_terms)

        # Extract from code blocks and configuration
        code_blocks = re.findall(r"```\w*\n(.*?)\n```", content, re.DOTALL)
        for code in code_blocks:
            # Extract API endpoints, service names, etc.
            endpoints = re.findall(r"/api/v\d+/\w+", code)
            topics.update(endpoint.split("/")[-1] for endpoint in endpoints)

        return topics

    def _extract_api_endpoints(self, content: str) -> list[str]:
        """Extract API endpoints from documentation."""
        endpoints = []

        # Pattern for REST endpoints
        endpoint_patterns = [
            r"(?:GET|POST|PUT|DELETE|PATCH)\s+(/api/[^\s\n]+)",
            r"`(/api/[^`\n]+)`",
            r'"(/api/[^"\n]+)"',
            r"'(/api/[^'\n]+)'",
            r"https?://[^/]+(/api/[^\s\n]+)",
        ]

        for pattern in endpoint_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            endpoints.extend(matches)

        return list(set(endpoints))

    def _extract_cross_references(
        self, file_path: Path, content: str, lines: list[str]
    ) -> list[CrossReference]:
        """Extract cross-references from document content."""
        references = []
        relative_path = str(file_path.relative_to(REPO_ROOT))

        for pattern_info in self.compiled_patterns:
            pattern = pattern_info["pattern"]
            reference_type = pattern_info["type"]
            base_confidence = pattern_info["base_confidence"]

            for line_num, line in enumerate(lines, 1):
                try:
                    matches = re.finditer(pattern, line)

                    for match in matches:
                        # Handle different group name patterns
                        groups = pattern_info["groups"]

                        # Extract link text and URL based on available groups
                        link_text = ""
                        link_url = ""

                        if "text" in groups:
                            link_text = match.group(groups["text"])
                        if "url" in groups:
                            link_url = match.group(groups["url"])
                        elif "path" in groups:
                            link_url = match.group(groups["path"])
                        elif "endpoint" in groups:
                            link_url = match.group(groups["endpoint"])
                        elif "module_path" in groups:
                            link_url = match.group(groups["module_path"])
                        elif "anchor" in groups:
                            link_url = "#" + match.group(groups["anchor"])
                        else:
                            # Fallback to the entire match
                            link_url = match.group(0)

                        # Skip if exclusion patterns match
                        if any(
                            re.match(ex, link_url)
                            for ex in pattern_info.get("exclusions", [])
                        ):
                            continue

                        confidence = self._calculate_confidence(
                            link_text, line, content, pattern_info
                        )

                        ref = CrossReference(
                            source_file=relative_path,
                            target_file=link_url,
                            link_text=link_text or link_url,
                            link_url=link_url,
                            line_number=line_num,
                            reference_type=reference_type,
                            confidence=confidence,
                            context=line.strip(),
                        )

                        references.append(ref)
                        self.cross_references.append(ref)

                except Exception as e:
                    # Log pattern matching errors but continue processing
                    self.validation_issues.append(
                        ValidationIssue(
                            severity="LOW",
                            category="pattern_error",
                            file_path=relative_path,
                            message=f"Pattern matching error: {e}",
                            line_number=line_num,
                        )
                    )

        return references

    def _load_pattern_registry(self):
        """Load pattern registry from YAML configuration."""
        import yaml

        pattern_file = (
            Path(str(REPO_ROOT))
            / "tools"
            / "validation"
            / "cross_reference_patterns.yaml"
        )
        try:
            with open(pattern_file, "r") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            # Return minimal fallback registry if file not found
            return {
                "version": "1.0",
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "categories": {"markdown_links": {"base_confidence": 0.8}},
                "patterns": [
                    {
                        "name": "basic_markdown_link",
                        "category": "markdown_links",
                        "regex": r"\[([^\]]+)\]\(([^)]+)\)",
                        "capture_groups": {"text": 1, "url": 2},
                        "reference_type": "direct",
                        "exclusions": [r"^https?://", r"^mailto:"],
                    }
                ],
                "confidence_scoring": {
                    "base_confidence": 1.0,
                    "max_confidence": 1.0,
                    "min_confidence": 0.1,
                    "text_quality": {
                        "generic_terms": ["here", "link"],
                        "descriptive_terms": {"min_length": 5, "modifier": 0.2},
                        "action_terms": {"terms": ["see", "refer"], "modifier": 0.1},
                    },
                },
            }

    def _compile_patterns(self):
        """Compile patterns from the loaded pattern registry."""
        compiled = []
        for pattern in self.pattern_registry["patterns"]:
            try:
                compiled_pattern = re.compile(pattern["regex"])
                compiled.append(
                    {
                        "pattern": compiled_pattern,
                        "type": pattern["reference_type"],
                        "groups": pattern["capture_groups"],
                        "base_confidence": self.pattern_registry["categories"][
                            pattern["category"]
                        ]["base_confidence"],
                        "exclusions": pattern.get("exclusions", []),
                    }
                )
            except re.error as e:
                # Log pattern compilation error but continue with other patterns
                self.validation_issues.append(
                    ValidationIssue(
                        severity="ERROR",
                        category="pattern_compilation",
                        file_path="pattern_registry",
                        message=f"Failed to compile pattern '{pattern['name']}': {e}",
                    )
                )
        return compiled

    def _calculate_confidence(self, link_text, line, content, pattern_info):
        """Calculate confidence score for a reference using pattern modifiers."""
        confidence = pattern_info["base_confidence"]

        if (
            len(link_text) > 5
            and link_text.lower()
            not in self.pattern_registry["confidence_scoring"]["text_quality"][
                "generic_terms"
            ]
        ):
            confidence += self.pattern_registry["confidence_scoring"]["text_quality"][
                "descriptive_terms"
            ]["modifier"]

        if any(
            word in line.lower()
            for word in self.pattern_registry["confidence_scoring"]["text_quality"][
                "action_terms"
            ]["terms"]
        ):
            confidence += self.pattern_registry["confidence_scoring"]["text_quality"][
                "action_terms"
            ]["modifier"]

        return max(
            self.pattern_registry["confidence_scoring"]["min_confidence"],
            min(
                self.pattern_registry["confidence_scoring"]["max_confidence"],
                confidence,
            ),
        )

    def _classify_reference_type(
        self, link_url: str, link_text: str, context: str
    ) -> str:
        """Classify the type of cross-reference."""
        if "/api/" in link_url.lower():
            return "api"
        elif any(
            word in link_text.lower() for word in ["config", "configuration", "setting"]
        ):
            return "config"
        elif any(
            word in context.lower() for word in ["see also", "related", "refer to"]
        ):
            return "semantic"
        else:
            return "direct"

    def _calculate_reference_confidence(
        self, link_text: str, line: str, content: str
    ) -> float:
        """Calculate confidence score for cross-reference validity."""
        confidence = 1.0

        # Higher confidence for specific link text
        if len(link_text) > 5 and link_text.lower() not in [
            "here",
            "link",
            "click here",
        ]:
            confidence += 0.2

        # Higher confidence for structured references
        if any(
            word in line.lower() for word in ["see", "refer", "documentation", "guide"]
        ):
            confidence += 0.1

        # Lower confidence for generic references
        if link_text.lower() in ["here", "link", "click here", "this"]:
            confidence -= 0.3

        return max(0.1, min(1.0, confidence))

    def validate_cross_references(self) -> list[ValidationIssue]:
        """Validate all cross-references for broken links and consistency."""
        issues = []

        for ref in self.cross_references:
            # Check if target file exists
            target_path = self._resolve_reference_path(ref.source_file, ref.target_file)

            if not target_path or not target_path.exists():
                # Try to find suggestions
                suggestions = self._find_reference_suggestions(ref.target_file)

                issue = ValidationIssue(
                    severity="HIGH" if ref.confidence > 0.7 else "MEDIUM",
                    category="broken_reference",
                    file_path=ref.source_file,
                    message=(
                        f"Broken reference to '{ref.target_file}' (text:"
                        f" '{ref.link_text}')"
                    ),
                    line_number=ref.line_number,
                    suggested_fix=(
                        f"Consider: {', '.join(suggestions[:3])}"
                        if suggestions
                        else None
                    ),
                    related_files=suggestions,
                    relationship_type=ref.reference_type,
                )
                issues.append(issue)

        return issues

    def _resolve_reference_path(
        self, source_file: str, target_url: str
    ) -> Optional[Path]:
        """Resolve relative reference path to absolute path."""
        try:
            # Handle different reference formats
            if target_url.startswith("#"):
                # Anchor link - assume valid for now
                if source_file:
                    return REPO_ROOT / source_file
                else:
                    return None

            # Remove anchor from URL
            clean_url = target_url.split("#")[0] if "#" in target_url else target_url
            if not clean_url:
                return None

            if clean_url.startswith("/"):
                # Absolute path from repo root
                return REPO_ROOT / clean_url.lstrip("/")

            # Relative path
            if source_file:
                source_path = REPO_ROOT / source_file
                target_path = source_path.parent / clean_url
            else:
                target_path = REPO_ROOT / clean_url

            resolved = target_path.resolve()

            # Check if resolved path is within REPO_ROOT
            try:
                resolved.relative_to(REPO_ROOT)
                return resolved
            except ValueError:
                # Path is outside repo root, try alternative resolution strategies
                return self._try_alternative_path_resolution(source_file, clean_url)

        except Exception:
            return None

    def _try_alternative_path_resolution(
        self, source_file: str, target_url: str
    ) -> Optional[Path]:
        """Try alternative strategies to resolve paths that fall outside repo root."""
        try:
            # Strategy 1: If target_url contains "docs/" pattern, try treating it as repo-relative
            if "docs/" in target_url:
                # Extract the part starting from "docs/"
                docs_index = target_url.find("docs/")
                repo_relative_path = target_url[docs_index:]
                candidate = REPO_ROOT / repo_relative_path
                if candidate.exists():
                    return candidate

            # Strategy 2: Try treating the target as repo-relative directly
            candidate = REPO_ROOT / target_url.lstrip("./")
            if candidate.exists():
                return candidate

            # Strategy 3: If target starts with "../", try removing leading "../" patterns
            if target_url.startswith("../"):
                # Remove all leading "../" and try as repo-relative
                clean_target = target_url
                while clean_target.startswith("../"):
                    clean_target = clean_target[3:]
                candidate = REPO_ROOT / clean_target
                if candidate.exists():
                    return candidate

            # Strategy 4: Try finding the file by name in common directories
            target_name = Path(target_url).name
            if target_name:
                # Search in docs directory and subdirectories
                for candidate in DOCS_DIR.rglob(target_name):
                    if candidate.is_file():
                        return candidate

            return None

        except Exception:
            return None

    def _find_reference_suggestions(self, broken_ref: str) -> list[str]:
        """Find suggestions for broken references using fuzzy matching."""
        suggestions = []

        # Extract filename from broken reference
        ref_filename = Path(broken_ref).name.lower()
        ref_stem = Path(broken_ref).stem.lower()

        # Search all documentation files
        for doc_path in DOCS_DIR.rglob("*.md"):
            relative_path = str(doc_path.relative_to(REPO_ROOT))
            filename = doc_path.name.lower()
            stem = doc_path.stem.lower()

            # Calculate similarity
            score = 0
            if filename == ref_filename:
                score = 1.0
            elif stem == ref_stem:
                score = 0.9
            elif ref_stem in stem or stem in ref_stem:
                score = 0.7
            elif any(word in stem for word in ref_stem.split("-") if len(word) > 2):
                score = 0.5

            if score > 0.5:
                suggestions.append((relative_path, score))

        # Sort by score and return top suggestions
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return [path for path, score in suggestions[:5]]

    def detect_semantic_relationships(self) -> list[SemanticRelationship]:
        """Detect semantic relationships between documents."""
        relationships = []

        for doc1_path, node1 in self.document_nodes.items():
            for doc2_path, node2 in self.document_nodes.items():
                if doc1_path == doc2_path:
                    continue

                # Calculate topic overlap
                common_topics = node1.topics.intersection(node2.topics)
                topic_strength = len(common_topics) / max(
                    len(node1.topics), len(node2.topics), 1
                )

                if topic_strength > 0.3:  # Significant overlap
                    # Determine relationship type
                    rel_type = self._determine_relationship_type(
                        node1, node2, common_topics
                    )

                    relationship = SemanticRelationship(
                        doc1=doc1_path,
                        doc2=doc2_path,
                        relationship_type=rel_type,
                        strength=topic_strength,
                        evidence=list(common_topics),
                    )
                    relationships.append(relationship)

        return relationships

    def _determine_relationship_type(
        self, node1: DocumentNode, node2: DocumentNode, common_topics: set[str]
    ) -> str:
        """Determine the type of relationship between two documents."""
        # API implementation relationship
        if ("api" in node1.file_path and "implementation" in node2.file_path) or (
            "api" in node2.file_path and "implementation" in node1.file_path
        ):
            return "implements"

        # Configuration dependency
        if "config" in common_topics or "configuration" in common_topics:
            return "configures"

        # Deployment relationship
        if "deployment" in common_topics or "deploy" in common_topics:
            return "deploys"

        # General reference
        return "references"

    def validate_api_sync(self) -> list[ValidationIssue]:
        """Validate synchronization between API documentation and implementation."""
        issues = []

        for service_name, config in SERVICE_CONFIG.items():
            api_doc_path = f"docs/api/{service_name}.md"

            if api_doc_path in self.document_nodes:
                node = self.document_nodes[api_doc_path]

                # Check if documented endpoints match configured endpoints
                documented_endpoints = set(node.api_endpoints)
                expected_endpoints = set(config["endpoints"])

                # Missing endpoints in documentation
                missing_docs = expected_endpoints - documented_endpoints
                if missing_docs:
                    issue = ValidationIssue(
                        severity="MEDIUM",
                        category="api_sync",
                        file_path=api_doc_path,
                        message=(
                            f"Missing endpoint documentation: {', '.join(missing_docs)}"
                        ),
                        suggested_fix=(
                            "Add documentation for endpoints:"
                            f" {', '.join(missing_docs)}"
                        ),
                        relationship_type="implements",
                    )
                    issues.append(issue)

                # Extra endpoints in documentation
                extra_docs = documented_endpoints - expected_endpoints
                if extra_docs:
                    issue = ValidationIssue(
                        severity="LOW",
                        category="api_sync",
                        file_path=api_doc_path,
                        message=(
                            "Documented endpoints not in implementation:"
                            f" {', '.join(extra_docs)}"
                        ),
                        suggested_fix=(
                            "Verify if these endpoints are implemented or remove"
                            " documentation"
                        ),
                        relationship_type="implements",
                    )
                    issues.append(issue)

        return issues

    def generate_dependency_graph(self) -> dict[str, Any]:
        """Generate dependency graph visualization data."""
        # Build NetworkX graph
        graph = nx.DiGraph()

        # Add nodes
        for doc_path, node in self.document_nodes.items():
            graph.add_node(
                doc_path,
                title=node.title,
                topics=list(node.topics),
                constitutional_hash=node.constitutional_hash,
                api_endpoints=node.api_endpoints,
            )

        # Add edges from cross-references
        for ref in self.cross_references:
            target_path = self._resolve_reference_path(ref.source_file, ref.target_file)
            if target_path and target_path.exists():
                target_relative = str(target_path.relative_to(REPO_ROOT))
                if target_relative in self.document_nodes:
                    graph.add_edge(
                        ref.source_file,
                        target_relative,
                        type=ref.reference_type,
                        confidence=ref.confidence,
                        link_text=ref.link_text,
                    )

        # Calculate graph metrics
        metrics = {
            "total_documents": len(graph.nodes),
            "total_references": len(graph.edges),
            "orphaned_documents": len([n for n in graph.nodes if graph.degree(n) == 0]),
            "highly_connected": len([n for n in graph.nodes if graph.degree(n) > 5]),
            "connected_components": nx.number_weakly_connected_components(graph),
            "average_degree": (
                sum(dict(graph.degree()).values()) / len(graph.nodes)
                if graph.nodes
                else 0
            ),
        }

        # Convert to JSON-serializable format
        graph_data = {
            "nodes": [
                {
                    "id": node,
                    "title": data.get("title", "Unknown"),
                    "topics": data.get("topics", []),
                    "constitutional_hash": data.get("constitutional_hash", False),
                    "api_endpoints": data.get("api_endpoints", []),
                    "degree": graph.degree(node),
                }
                for node, data in graph.nodes(data=True)
            ],
            "edges": [
                {
                    "source": source,
                    "target": target,
                    "type": data.get("type", "direct"),
                    "confidence": data.get("confidence", 1.0),
                    "link_text": data.get("link_text", ""),
                }
                for source, target, data in graph.edges(data=True)
            ],
            "metrics": metrics,
        }

        return graph_data

    def suggest_missing_references(self) -> list[ValidationIssue]:
        """Suggest missing cross-references based on semantic analysis."""
        suggestions = []

        for relationship in self.semantic_relationships:
            if relationship.strength > 0.6:  # High confidence relationship
                # Check if there's already a reference between these documents
                existing_ref = any(
                    ref.source_file == relationship.doc1
                    and self._resolve_target_matches(ref.target_file, relationship.doc2)
                    for ref in self.cross_references
                )

                if not existing_ref:
                    suggestion = ValidationIssue(
                        severity="LOW",
                        category="missing_reference",
                        file_path=relationship.doc1,
                        message=(
                            f"Consider adding reference to '{relationship.doc2}' "
                            f"(relationship: {relationship.relationship_type}, "
                            f"strength: {relationship.strength:.2f})"
                        ),
                        suggested_fix=(
                            f"Add link to {relationship.doc2} in relevant section"
                        ),
                        related_files=[relationship.doc2],
                        relationship_type=relationship.relationship_type,
                    )
                    suggestions.append(suggestion)

        return suggestions

    def _resolve_target_matches(self, target_url: str, doc_path: str) -> bool:
        """Check if target URL resolves to the given document path."""
        resolved_path = self._resolve_reference_path("", target_url)
        if resolved_path:
            try:
                return str(resolved_path.relative_to(REPO_ROOT)) == doc_path
            except ValueError:
                # Path is not within REPO_ROOT
                return False
        return False

    def run_comprehensive_analysis(self, max_workers: int = 4) -> dict[str, Any]:
        """Run comprehensive cross-reference analysis."""
        print("🔍 ACGS Advanced Cross-Reference Analysis")
        print("=" * 50)
        print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
        print(f"Repository: {REPO_ROOT}")
        print(f"Max Workers: {max_workers}")
        print()

        start_time = time.time()

        # Find all markdown files
        md_files = list(DOCS_DIR.rglob("*.md"))
        print(f"📄 Found {len(md_files)} documentation files")

        # Analyze document structure in parallel
        print("🔍 Analyzing document structure...")
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {
                executor.submit(self.analyze_document_structure, file_path): file_path
                for file_path in md_files
            }

            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    node = future.result()
                    self.document_nodes[node.file_path] = node
                    print(f"✅ {file_path.relative_to(REPO_ROOT)}")
                except Exception as e:
                    print(f"❌ {file_path.relative_to(REPO_ROOT)}: {e}")

        print(f"\n🔗 Analyzing {len(self.cross_references)} cross-references...")

        # Validate cross-references
        print("🔍 Validating cross-references...")
        ref_issues = self.validate_cross_references()
        self.validation_issues.extend(ref_issues)

        # Detect semantic relationships
        print("🧠 Detecting semantic relationships...")
        self.semantic_relationships = self.detect_semantic_relationships()

        # Validate API synchronization
        print("🔌 Validating API synchronization...")
        api_issues = self.validate_api_sync()
        self.validation_issues.extend(api_issues)

        # Suggest missing references
        print("💡 Suggesting missing references...")
        missing_refs = self.suggest_missing_references()
        self.validation_issues.extend(missing_refs)

        # Generate dependency graph
        print("📊 Generating dependency graph...")
        dependency_graph = self.generate_dependency_graph()

        analysis_time = time.time() - start_time

        # Compile results
        results = {
            "timestamp": datetime.now().isoformat(),
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "analysis_duration": analysis_time,
            "performance": {
                "files_per_second": len(md_files) / analysis_time,
                "references_per_second": len(self.cross_references) / analysis_time,
            },
            "summary": {
                "total_documents": len(self.document_nodes),
                "total_cross_references": len(self.cross_references),
                "total_issues": len(self.validation_issues),
                "semantic_relationships": len(self.semantic_relationships),
                "critical_issues": len(
                    [i for i in self.validation_issues if i.severity == "CRITICAL"]
                ),
                "high_issues": len(
                    [i for i in self.validation_issues if i.severity == "HIGH"]
                ),
                "medium_issues": len(
                    [i for i in self.validation_issues if i.severity == "MEDIUM"]
                ),
                "low_issues": len(
                    [i for i in self.validation_issues if i.severity == "LOW"]
                ),
            },
            "validation_issues": [
                {
                    "severity": issue.severity,
                    "category": issue.category,
                    "file_path": issue.file_path,
                    "message": issue.message,
                    "line_number": issue.line_number,
                    "suggested_fix": issue.suggested_fix,
                    "related_files": issue.related_files,
                    "relationship_type": issue.relationship_type,
                }
                for issue in self.validation_issues
            ],
            "semantic_relationships": [
                {
                    "doc1": rel.doc1,
                    "doc2": rel.doc2,
                    "relationship_type": rel.relationship_type,
                    "strength": rel.strength,
                    "evidence": rel.evidence,
                }
                for rel in self.semantic_relationships
            ],
            "dependency_graph": dependency_graph,
        }

        return results

    def generate_report(self, results: dict[str, Any]) -> str:
        """Generate comprehensive analysis report."""
        summary = results["summary"]
        issues_by_severity = {}

        for issue in results["validation_issues"]:
            severity = issue["severity"]
            if severity not in issues_by_severity:
                issues_by_severity[severity] = []
            issues_by_severity[severity].append(issue)

        report = f"""# ACGS Advanced Cross-Reference Analysis Report

<!-- Constitutional Hash: {CONSTITUTIONAL_HASH} -->

**Date**: {results['timestamp']}
**Constitutional Hash**: `{CONSTITUTIONAL_HASH}`
**Analysis Duration**: {results['analysis_duration']:.2f} seconds
**Performance**: {results['performance']['files_per_second']:.1f} files/second

## Executive Summary

| Metric | Value |
|--------|-------|
| Total Documents | {summary['total_documents']} |
| Total Cross-References | {summary['total_cross_references']} |
| Semantic Relationships | {summary['semantic_relationships']} |
| Total Issues | {summary['total_issues']} |
| Critical Issues | {summary['critical_issues']} |
| High Priority Issues | {summary['high_issues']} |
| Medium Priority Issues | {summary['medium_issues']} |
| Low Priority Issues | {summary['low_issues']} |

## Dependency Graph Metrics

| Metric | Value |
|--------|-------|
| Connected Components | {results['dependency_graph']['metrics']['connected_components']} |
| Orphaned Documents | {results['dependency_graph']['metrics']['orphaned_documents']} |
| Highly Connected (>5 refs) | {results['dependency_graph']['metrics']['highly_connected']} |
| Average Degree | {results['dependency_graph']['metrics']['average_degree']:.2f} |

## Validation Issues

"""

        for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            if severity in issues_by_severity:
                issues = issues_by_severity[severity]
                report += f"### {severity} Priority ({len(issues)} issues)\n\n"

                for issue in issues:
                    line_info = (
                        f" (line {issue['line_number']})"
                        if issue["line_number"]
                        else ""
                    )
                    report += (
                        f"**{issue['file_path']}**{line_info} ({issue['category']})\n"
                    )
                    report += f"- {issue['message']}\n"

                    if issue["suggested_fix"]:
                        report += f"- 💡 **Suggested Fix**: {issue['suggested_fix']}\n"

                    if issue["related_files"]:
                        report += (
                            "- 🔗 **Related Files**:"
                            f" {', '.join(issue['related_files'][:3])}\n"
                        )

                    report += "\n"

        # Semantic Relationships
        report += "## Semantic Relationships\n\n"
        strong_relationships = [
            r for r in results["semantic_relationships"] if r["strength"] > 0.6
        ]

        if strong_relationships:
            report += "### High-Confidence Relationships\n\n"
            for rel in strong_relationships[:10]:  # Top 10
                report += (
                    f"- **{rel['doc1']}** {rel['relationship_type']} **{rel['doc2']}** "
                )
                report += f"(strength: {rel['strength']:.2f})\n"
                report += f"  - Evidence: {', '.join(rel['evidence'][:5])}\n\n"

        # Graph Analysis
        graph = results["dependency_graph"]

        report += "## Graph Analysis\n\n"
        report += "### Most Connected Documents\n\n"

        # Sort nodes by degree
        sorted_nodes = sorted(graph["nodes"], key=lambda x: x["degree"], reverse=True)
        for node in sorted_nodes[:10]:
            report += f"- **{node['id']}** ({node['degree']} connections)\n"
            if node["topics"]:
                report += f"  - Topics: {', '.join(node['topics'][:5])}\n"

        report += "\n### Orphaned Documents\n\n"
        orphaned = [node for node in graph["nodes"] if node["degree"] == 0]
        if orphaned:
            for node in orphaned:
                report += f"- **{node['id']}** (no connections)\n"
        else:
            report += "✅ No orphaned documents found.\n"

        # Constitutional Compliance
        report += "\n## Constitutional Compliance\n\n"
        compliant_docs = len([n for n in graph["nodes"] if n["constitutional_hash"]])
        total_docs = len(graph["nodes"])
        compliance_rate = (compliant_docs / total_docs * 100) if total_docs > 0 else 0

        report += (
            f"- **Compliance Rate**: {compliance_rate:.1f}%"
            f" ({compliant_docs}/{total_docs} documents)\n"
        )
        report += f"- **Constitutional Hash**: `{CONSTITUTIONAL_HASH}`\n"

        if compliance_rate < 100:
            non_compliant = [n for n in graph["nodes"] if not n["constitutional_hash"]]
            report += "\n### Non-Compliant Documents\n\n"
            for node in non_compliant:
                report += f"- **{node['id']}**\n"

        # Recommendations
        report += "\n## Recommendations\n\n"

        if summary["critical_issues"] > 0:
            report += (
                "🚨 **CRITICAL**: Address critical issues immediately before"
                " deployment.\n\n"
            )

        if summary["high_issues"] > 0:
            report += "⚠️ **HIGH**: Resolve high-priority cross-reference issues.\n\n"

        if graph["metrics"]["orphaned_documents"] > 0:
            report += (
                "🔗 **CONNECTIVITY**: Link orphaned documents to main documentation"
                " structure.\n\n"
            )

        if compliance_rate < 100:
            report += (
                "📋 **COMPLIANCE**: Add constitutional hash to"
                f" {total_docs - compliant_docs} documents.\n\n"
            )

        if summary["total_issues"] == 0:
            report += (
                "✅ **EXCELLENT**: All cross-references are valid and"
                " well-structured.\n\n"
            )

        report += f"""---

**Advanced Cross-Reference Analysis**: Generated by ACGS Advanced Cross-Reference Analyzer
**Constitutional Hash**: `{CONSTITUTIONAL_HASH}` ✅
**Analysis Performance**: {results['performance']['files_per_second']:.1f} files/second, {results['performance']['references_per_second']:.1f} references/second
"""

        return report


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="ACGS Advanced Cross-Reference Analyzer"
    )
    parser.add_argument(
        "--workers", type=int, default=4, help="Number of worker threads"
    )
    parser.add_argument("--output", type=Path, help="Output file for analysis results")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--graph", type=Path, help="Output dependency graph JSON")

    args = parser.parse_args()

    # Run analysis
    analyzer = AdvancedCrossReferenceAnalyzer()
    results = analyzer.run_comprehensive_analysis(args.workers)

    # Print summary
    print("\n" + "=" * 50)
    print("📊 ANALYSIS SUMMARY")
    print("=" * 50)

    summary = results["summary"]
    print(f"📄 Documents Analyzed: {summary['total_documents']}")
    print(f"🔗 Cross-References: {summary['total_cross_references']}")
    print(f"🧠 Semantic Relationships: {summary['semantic_relationships']}")
    print(f"⚠️ Total Issues: {summary['total_issues']}")
    print(f"🚨 Critical Issues: {summary['critical_issues']}")
    print(
        f"⚡ Performance: {results['performance']['files_per_second']:.1f} files/second"
    )

    # Save results
    if args.json or args.output:
        if args.output:
            if args.json:
                with open(args.output, "w") as f:
                    json.dump(results, f, indent=2)
                print(f"📊 JSON results saved to: {args.output}")
            else:
                report = analyzer.generate_report(results)
                with open(args.output, "w") as f:
                    f.write(report)
                print(f"📄 Report saved to: {args.output}")
        else:
            print(json.dumps(results, indent=2))
    else:
        # Generate and save markdown report
        report = analyzer.generate_report(results)
        report_file = (
            REPO_ROOT
            / "validation_reports"
            / f"cross_reference_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        )
        report_file.parent.mkdir(exist_ok=True)

        with open(report_file, "w") as f:
            f.write(report)
        print(f"📄 Analysis report saved to: {report_file}")

    # Save dependency graph
    if args.graph:
        with open(args.graph, "w") as f:
            json.dump(results["dependency_graph"], f, indent=2)
        print(f"📊 Dependency graph saved to: {args.graph}")

    # Exit with appropriate code
    if summary["critical_issues"] > 0:
        print(
            f"\n🚨 {summary['critical_issues']} CRITICAL issues require immediate"
            " attention!"
        )
        return 2
    elif summary["high_issues"] > 0:
        print(f"\n⚠️ {summary['high_issues']} HIGH priority issues should be addressed")
        return 1
    else:
        print("\n🎉 Cross-reference analysis completed successfully!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
