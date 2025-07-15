#!/usr/bin/env python3
# Constitutional Hash: cdd01ef066bc6cf2
"""
Research Papers Import Tool for ACGS Knowledge Base

This script extracts metadata from research papers and imports them into the PostgreSQL database.
It supports PDF extraction, arXiv ID parsing, and automatic keyword extraction.
"""

import argparse
import json
import logging
import os
import re
import subprocess
import sys
import tarfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import psycopg2
import requests
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class PaperMetadata:
    """Data class for paper metadata"""

    title: str
    authors: List[str] = None
    abstract: str = None
    arxiv_id: str = None
    doi: str = None
    publication_date: str = None
    venue: str = None
    venue_type: str = None
    paper_type: str = None
    file_path: str = None
    file_size: int = None
    page_count: int = None
    keywords: List[str] = None
    full_text: str = None


class PaperImporter:
    """Main class for importing research papers into the knowledge base"""

    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.connection = None
        self.research_dir = project_root / "docs" / "research"

    def connect_db(self):
        """Establish database connection"""
        try:
            self.connection = psycopg2.connect(
                host=self.db_config["DB_HOST"],
                port=self.db_config["DB_PORT"],
                database=self.db_config["DB_NAME"],
                user=self.db_config["DB_USER"],
                password=os.environ.get("PASSWORD")DB_PASSWORD"],
            )
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    def disconnect_db(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")

    def extract_archives(self):
        """Extract research paper archives if they exist"""
        logger.info("Checking for compressed research archives...")

        # Extract papers archive
        papers_archive = self.research_dir / "papers_archive.tar.gz"
        if papers_archive.exists():
            logger.info("Extracting papers archive...")
            with tarfile.open(papers_archive, "r:gz") as tar:
                tar.extractall(path=self.research_dir)
            logger.info("Papers archive extracted")

        # Extract arXiv images archive
        arxiv_images_archive = (
            self.research_dir / "arXiv-2506.16507v1" / "images_archive.tar.gz"
        )
        if arxiv_images_archive.exists():
            logger.info("Extracting arXiv images archive...")
            with tarfile.open(arxiv_images_archive, "r:gz") as tar:
                tar.extractall(path=arxiv_images_archive.parent)
            logger.info("arXiv images archive extracted")

    def parse_arxiv_id(self, filename: str) -> Optional[str]:
        """Extract arXiv ID from filename"""
        # Pattern for arXiv IDs like 2501.09620, 1502.05477, etc.
        patterns = [
            r"(\d{4}\.\d{4,5})",  # Standard arXiv format
            r"arxiv[:-](\d{4}\.\d{4,5})",  # With arxiv prefix
        ]

        for pattern in patterns:
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    def extract_title_from_filename(self, filename: str) -> str:
        """Extract title from filename"""
        # Remove file extension
        title = filename.replace(".pdf", "").replace(".txt", "")

        # Remove arXiv ID if present
        arxiv_pattern = r"\d{4}\.\d{4,5}_?"
        title = re.sub(arxiv_pattern, "", title)

        # Replace underscores and hyphens with spaces
        title = title.replace("_", " ").replace("-", " ")

        # Clean up multiple spaces
        title = re.sub(r"\s+", " ", title).strip()

        # Capitalize words properly
        title = " ".join(word.capitalize() for word in title.split())

        return title

    def fetch_arxiv_metadata(self, arxiv_id: str) -> Optional[Dict]:
        """Fetch metadata from arXiv API"""
        try:
            url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                # Parse XML response (simplified)
                content = response.text

                # Extract title
                title_match = re.search(r"<title>(.*?)</title>", content, re.DOTALL)
                title = title_match.group(1).strip() if title_match else None

                # Extract abstract
                abstract_match = re.search(
                    r"<summary>(.*?)</summary>", content, re.DOTALL
                )
                abstract = abstract_match.group(1).strip() if abstract_match else None

                # Extract authors
                authors = []
                author_matches = re.findall(r"<name>(.*?)</name>", content)
                authors = [author.strip() for author in author_matches]

                # Extract publication date
                date_match = re.search(r"<published>(.*?)</published>", content)
                pub_date = (
                    date_match.group(1)[:10] if date_match else None
                )  # YYYY-MM-DD

                return {
                    "title": title,
                    "abstract": abstract,
                    "authors": authors,
                    "publication_date": pub_date,
                    "venue": "arXiv",
                    "venue_type": "preprint",
                }
        except Exception as e:
            logger.warning(f"Failed to fetch arXiv metadata for {arxiv_id}: {e}")

        return None

    def extract_keywords_from_title_abstract(
        self, title: str, abstract: str = None
    ) -> List[str]:
        """Extract relevant keywords from title and abstract"""
        text = title.lower()
        if abstract:
            text += " " + abstract.lower()

        # Predefined keywords relevant to ACGS research
        relevant_keywords = [
            "constitutional ai",
            "constitutional training",
            "harmlessness",
            "helpfulness",
            "reward modeling",
            "reward function",
            "reward hacking",
            "reward optimization",
            "rlhf",
            "reinforcement learning from human feedback",
            "human feedback",
            "preference learning",
            "preference optimization",
            "dpo",
            "direct preference optimization",
            "ai safety",
            "alignment",
            "safety evaluation",
            "risk assessment",
            "robustness",
            "adversarial",
            "distribution shift",
            "generalization",
            "evaluation",
            "benchmarks",
            "metrics",
            "human evaluation",
            "interpretability",
            "explainability",
            "mechanistic interpretability",
            "language models",
            "large language models",
            "llm",
            "transformer",
            "fine-tuning",
            "instruction following",
            "training methods",
            "optimization",
            "ppo",
            "proximal policy optimization",
            "causal reasoning",
            "causal inference",
            "counterfactuals",
            "multi-agent",
            "agent coordination",
            "emergent behavior",
            "human-ai interaction",
            "collaborative ai",
            "user studies",
            "ai ethics",
            "fairness",
            "bias",
            "transparency",
            "accountability",
            "ai governance",
            "policy",
            "regulation",
            "standards",
        ]

        found_keywords = []
        for keyword in relevant_keywords:
            if keyword in text:
                found_keywords.append(keyword)

        return found_keywords

    def categorize_paper_type(self, title: str, abstract: str = None) -> str:
        """Determine paper type based on content"""
        text = (title + " " + (abstract or "")).lower()

        if any(word in text for word in ["survey", "review", "overview"]):
            return "survey"
        elif any(word in text for word in ["position", "opinion", "perspective"]):
            return "position"
        elif any(word in text for word in ["technical", "system", "implementation"]):
            return "technical"
        else:
            return "research"

    def get_file_info(self, file_path: Path) -> Tuple[int, int]:
        """Get file size and page count"""
        file_size = file_path.stat().st_size if file_path.exists() else 0
        page_count = None

        # Try to get page count from PDF
        if file_path.suffix.lower() == ".pdf" and file_path.exists():
            try:
                result = subprocess.run(
                    ["pdfinfo", str(file_path)],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode == 0:
                    for line in result.stdout.split("\n"):
                        if line.startswith("Pages:"):
                            page_count = int(line.split(":")[1].strip())
                            break
            except Exception as e:
                logger.debug(f"Could not extract page count from {file_path}: {e}")

        return file_size, page_count

    def process_paper(self, file_path: Path) -> PaperMetadata:
        """Process a single paper file and extract metadata"""
        filename = file_path.stem

        # Extract arXiv ID
        arxiv_id = self.parse_arxiv_id(filename)

        # Start with filename-based title
        title = self.extract_title_from_filename(filename)
        authors = []
        abstract = None
        publication_date = None
        venue = None
        venue_type = "preprint"

        # Try to fetch from arXiv API if we have an ID
        if arxiv_id:
            arxiv_data = self.fetch_arxiv_metadata(arxiv_id)
            if arxiv_data:
                title = arxiv_data.get("title", title)
                authors = arxiv_data.get("authors", [])
                abstract = arxiv_data.get("abstract")
                publication_date = arxiv_data.get("publication_date")
                venue = arxiv_data.get("venue", "arXiv")
                venue_type = arxiv_data.get("venue_type", "preprint")

        # Extract keywords
        keywords = self.extract_keywords_from_title_abstract(title, abstract)

        # Determine paper type
        paper_type = self.categorize_paper_type(title, abstract)

        # Get file information
        file_size, page_count = self.get_file_info(file_path)

        # Calculate relevance score based on keywords
        relevance_score = min(5.0, len(keywords) * 0.3)  # Simple scoring

        return PaperMetadata(
            title=title,
            authors=authors,
            abstract=abstract,
            arxiv_id=arxiv_id,
            publication_date=publication_date,
            venue=venue,
            venue_type=venue_type,
            paper_type=paper_type,
            file_path=(
                str(file_path.relative_to(project_root))
                if file_path.is_relative_to(project_root)
                else str(file_path)
            ),
            file_size=file_size,
            page_count=page_count,
            keywords=keywords,
        )

    def insert_author(self, cursor, author_name: str) -> str:
        """Insert author and return ID"""
        cursor.execute(
            "INSERT INTO authors (name) VALUES (%s) ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name RETURNING id",
            (author_name,),
        )
        return cursor.fetchone()["id"]

    def insert_keyword(self, cursor, keyword: str) -> str:
        """Insert keyword and return ID"""
        cursor.execute(
            "INSERT INTO keywords (keyword) VALUES (%s) ON CONFLICT (keyword) DO UPDATE SET keyword = EXCLUDED.keyword RETURNING id",
            (keyword,),
        )
        return cursor.fetchone()["id"]

    def insert_paper(self, paper: PaperMetadata) -> str:
        """Insert paper into database and return ID"""
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            try:
                # Insert paper
                cursor.execute(
                    """
                    INSERT INTO papers (
                        title, abstract, arxiv_id, publication_date, venue, venue_type,
                        paper_type, file_path, file_size, page_count, relevance_score,
                        added_by, processed_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    ) RETURNING id
                """,
                    (
                        paper.title,
                        paper.abstract,
                        paper.arxiv_id,
                        paper.publication_date,
                        paper.venue,
                        paper.venue_type,
                        paper.paper_type,
                        paper.file_path,
                        paper.file_size,
                        paper.page_count,
                        min(
                            5.0, len(paper.keywords or []) * 0.3
                        ),  # Simple relevance score
                        "import_script",
                        datetime.now(),
                    ),
                )

                paper_id = cursor.fetchone()["id"]

                # Insert authors
                if paper.authors:
                    for i, author_name in enumerate(paper.authors):
                        author_id = self.insert_author(cursor, author_name)
                        # Use ON CONFLICT to handle duplicates
                        cursor.execute(
                            """
                            INSERT INTO paper_authors (paper_id, author_id, author_order) 
                            VALUES (%s, %s, %s) 
                            ON CONFLICT (paper_id, author_id) DO UPDATE SET author_order = EXCLUDED.author_order
                        """,
                            (paper_id, author_id, i + 1),
                        )

                # Insert keywords
                if paper.keywords:
                    for keyword in paper.keywords:
                        keyword_id = self.insert_keyword(cursor, keyword)
                        # Use ON CONFLICT to handle duplicates
                        cursor.execute(
                            """
                            INSERT INTO paper_keywords (paper_id, keyword_id, relevance_score) 
                            VALUES (%s, %s, %s) 
                            ON CONFLICT (paper_id, keyword_id) DO UPDATE SET relevance_score = EXCLUDED.relevance_score
                        """,
                            (paper_id, keyword_id, 1.0),
                        )

                self.connection.commit()
                return paper_id

            except Exception as e:
                self.connection.rollback()
                logger.error(f"Failed to insert paper {paper.title}: {e}")
                raise

    def import_papers(self, papers_dir: Path = None):
        """Import all papers from the specified directory"""
        if papers_dir is None:
            papers_dir = self.research_dir / "papers"

        if not papers_dir.exists():
            logger.error(f"Papers directory not found: {papers_dir}")
            return

        logger.info(f"Importing papers from: {papers_dir}")

        # Find all PDF files
        pdf_files = list(papers_dir.glob("*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF files")

        imported_count = 0
        skipped_count = 0

        for pdf_file in pdf_files:
            try:
                # Check if paper already exists (by file path)
                with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                    relative_path = str(pdf_file.relative_to(project_root))
                    cursor.execute(
                        "SELECT id FROM papers WHERE file_path = %s", (relative_path,)
                    )

                    if cursor.fetchone():
                        logger.info(f"Skipping already imported paper: {pdf_file.name}")
                        skipped_count += 1
                        continue

                # Process and import paper
                logger.info(f"Processing: {pdf_file.name}")
                paper_metadata = self.process_paper(pdf_file.resolve())
                paper_id = self.insert_paper(paper_metadata)

                logger.info(f"Imported paper: {paper_metadata.title} (ID: {paper_id})")
                imported_count += 1

            except Exception as e:
                logger.error(f"Failed to import {pdf_file.name}: {e}")
                continue

        # Refresh search view
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT refresh_paper_search_view()")
            self.connection.commit()

        logger.info(
            f"Import completed: {imported_count} papers imported, {skipped_count} skipped"
        )


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Import research papers into ACGS Knowledge Base"
    )
    parser.add_argument(
        "--extract", action="store_true", help="Extract archives before importing"
    )
    parser.add_argument(
        "--papers-dir", type=Path, help="Directory containing PDF files"
    )
    parser.add_argument("--config", type=Path, help="Database config file path")

    args = parser.parse_args()

    # Load database configuration
    config_path = args.config or (project_root / "database" / "config/environments/development.env")
    if config_path.exists():
        load_dotenv(config_path)

    db_config = {
        "DB_HOST": os.getenv("DB_HOST", "localhost"),
        "DB_PORT": os.getenv("DB_PORT", "5432"),
        "DB_NAME": os.getenv("DB_NAME", "acgs_research_kb"),
        "DB_USER": os.getenv("DB_USER", "acgs_user"),
        "DB_PASSWORD": os.getenv("DB_PASSWORD", "acgs_secure_password_2025"),
    }

    # Create importer
    importer = PaperImporter(db_config)

    try:
        # Connect to database
        importer.connect_db()

        # Extract archives if requested
        if args.extract:
            importer.extract_archives()

        # Import papers
        importer.import_papers(args.papers_dir)

    except Exception as e:
        logger.error(f"Import failed: {e}")
        sys.exit(1)
    finally:
        importer.disconnect_db()


if __name__ == "__main__":
    main()
