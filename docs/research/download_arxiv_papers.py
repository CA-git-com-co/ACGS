#!/usr/bin/env python3
"""
ACGS Research Paper Downloader from arXiv
Constitutional Hash: cdd01ef066bc6cf2

This script downloads all project-related research papers from arXiv based on
the bibliography files in the ACGS research directory.

Features:
- Extracts arXiv IDs from bibliography files
- Downloads papers in PDF format
- Organizes papers by category
- Generates metadata and index files
- Supports batch downloading with rate limiting
"""

import asyncio
import json
import logging
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple
from urllib.parse import urljoin

import aiohttp
import feedparser
import requests
from tqdm import tqdm

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ArxivPaperDownloader:
    """Downloads research papers from arXiv based on bibliography references."""
    
    def __init__(self, research_dir: Path):
        self.research_dir = Path(research_dir)
        self.papers_dir = self.research_dir / "papers"
        self.papers_dir.mkdir(exist_ok=True)
        
        # arXiv API configuration
        self.arxiv_api_base = "http://export.arxiv.org/api/query"
        self.arxiv_pdf_base = "https://arxiv.org/pdf"
        
        # Rate limiting
        self.request_delay = 3  # seconds between requests (arXiv recommends 3s)
        
        # Paper metadata
        self.paper_metadata = {}
        self.download_stats = {
            "total_found": 0,
            "downloaded": 0,
            "skipped": 0,
            "errors": 0
        }
    
    def extract_arxiv_ids_from_bib(self, bib_file: Path) -> Set[str]:
        """Extract arXiv IDs from a bibliography file."""
        arxiv_ids = set()
        
        try:
            with open(bib_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Pattern to match arXiv IDs in various formats
            patterns = [
                r'arXiv:(\d{4}\.\d{4,5})',  # Standard format: arXiv:2403.15583
                r'ArXiv:(\d{4}\.\d{4,5})',  # Capitalized
                r'arxiv\.org/abs/(\d{4}\.\d{4,5})',  # URL format
                r'arXiv preprint arXiv:(\d{4}\.\d{4,5})',  # Journal format
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                arxiv_ids.update(matches)
            
            logger.info(f"Found {len(arxiv_ids)} arXiv IDs in {bib_file.name}")
            return arxiv_ids
            
        except Exception as e:
            logger.error(f"Error reading {bib_file}: {e}")
            return set()
    
    def get_all_arxiv_ids(self) -> Set[str]:
        """Extract all arXiv IDs from all bibliography files."""
        all_ids = set()
        
        # Search for bibliography files
        bib_files = list(self.research_dir.rglob("*.bib"))
        
        logger.info(f"Found {len(bib_files)} bibliography files")
        
        for bib_file in bib_files:
            ids = self.extract_arxiv_ids_from_bib(bib_file)
            all_ids.update(ids)
        
        logger.info(f"Total unique arXiv IDs found: {len(all_ids)}")
        return all_ids
    
    async def get_paper_metadata(self, arxiv_id: str) -> Dict:
        """Get paper metadata from arXiv API."""
        try:
            url = f"{self.arxiv_api_base}?id_list={arxiv_id}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # Parse the Atom feed
                        feed = feedparser.parse(content)
                        
                        if feed.entries:
                            entry = feed.entries[0]
                            
                            # Extract authors
                            authors = []
                            if hasattr(entry, 'authors'):
                                authors = [author.name for author in entry.authors]
                            elif hasattr(entry, 'author'):
                                authors = [entry.author]
                            
                            # Extract categories
                            categories = []
                            if hasattr(entry, 'tags'):
                                categories = [tag.term for tag in entry.tags]
                            
                            metadata = {
                                "arxiv_id": arxiv_id,
                                "title": entry.title,
                                "authors": authors,
                                "summary": entry.summary,
                                "published": entry.published,
                                "updated": entry.updated if hasattr(entry, 'updated') else entry.published,
                                "categories": categories,
                                "pdf_url": f"{self.arxiv_pdf_base}/{arxiv_id}.pdf",
                                "abs_url": entry.link,
                                "constitutional_hash": CONSTITUTIONAL_HASH
                            }
                            
                            return metadata
                        
        except Exception as e:
            logger.error(f"Error getting metadata for {arxiv_id}: {e}")
        
        return None
    
    async def download_paper_pdf(self, arxiv_id: str, metadata: Dict) -> bool:
        """Download a paper PDF from arXiv."""
        try:
            pdf_url = f"{self.arxiv_pdf_base}/{arxiv_id}.pdf"
            
            # Create filename
            safe_title = re.sub(r'[^\w\s-]', '', metadata['title'])[:50]
            safe_title = re.sub(r'[-\s]+', '-', safe_title)
            filename = f"{arxiv_id}_{safe_title}.pdf"
            filepath = self.papers_dir / filename
            
            # Skip if already exists
            if filepath.exists():
                logger.info(f"Paper {arxiv_id} already exists, skipping")
                self.download_stats["skipped"] += 1
                return True
            
            # Download PDF
            async with aiohttp.ClientSession() as session:
                async with session.get(pdf_url) as response:
                    if response.status == 200:
                        content = await response.read()
                        
                        with open(filepath, 'wb') as f:
                            f.write(content)
                        
                        logger.info(f"Downloaded: {filename}")
                        self.download_stats["downloaded"] += 1
                        return True
                    else:
                        logger.error(f"Failed to download {arxiv_id}: HTTP {response.status}")
                        
        except Exception as e:
            logger.error(f"Error downloading {arxiv_id}: {e}")
            self.download_stats["errors"] += 1
        
        return False
    
    def categorize_papers(self) -> Dict[str, List[str]]:
        """Categorize papers based on their arXiv categories and content."""
        categories = {
            "constitutional_ai": [],
            "reward_modeling": [],
            "preference_optimization": [],
            "causal_reasoning": [],
            "alignment_safety": [],
            "quantum_computing": [],
            "machine_learning": [],
            "nlp_language_models": [],
            "other": []
        }
        
        for arxiv_id, metadata in self.paper_metadata.items():
            title_lower = metadata['title'].lower()
            summary_lower = metadata['summary'].lower()
            arxiv_categories = metadata.get('categories', [])
            
            # Categorization logic
            if any(term in title_lower or term in summary_lower for term in 
                   ['constitutional', 'governance', 'democratic']):
                categories["constitutional_ai"].append(arxiv_id)
            elif any(term in title_lower or term in summary_lower for term in 
                     ['reward model', 'reward modeling', 'rlhf', 'human feedback']):
                categories["reward_modeling"].append(arxiv_id)
            elif any(term in title_lower or term in summary_lower for term in 
                     ['preference optimization', 'dpo', 'direct preference']):
                categories["preference_optimization"].append(arxiv_id)
            elif any(term in title_lower or term in summary_lower for term in 
                     ['causal', 'causality', 'counterfactual']):
                categories["causal_reasoning"].append(arxiv_id)
            elif any(term in title_lower or term in summary_lower for term in 
                     ['alignment', 'safety', 'harmless', 'jailbreak']):
                categories["alignment_safety"].append(arxiv_id)
            elif any(term in title_lower or term in summary_lower for term in 
                     ['quantum', 'qec', 'error correction']):
                categories["quantum_computing"].append(arxiv_id)
            elif any(cat.startswith('cs.LG') or cat.startswith('stat.ML') for cat in arxiv_categories):
                categories["machine_learning"].append(arxiv_id)
            elif any(cat.startswith('cs.CL') for cat in arxiv_categories):
                categories["nlp_language_models"].append(arxiv_id)
            else:
                categories["other"].append(arxiv_id)
        
        return categories
    
    def generate_index_files(self):
        """Generate index files for downloaded papers."""
        # Generate main index
        index_data = {
            "generated_at": datetime.now().isoformat(),
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "total_papers": len(self.paper_metadata),
            "download_stats": self.download_stats,
            "papers": self.paper_metadata
        }
        
        with open(self.papers_dir / "index.json", 'w') as f:
            json.dump(index_data, f, indent=2)
        
        # Generate categorized index
        categories = self.categorize_papers()
        with open(self.papers_dir / "categories.json", 'w') as f:
            json.dump(categories, f, indent=2)
        
        # Generate markdown index
        self.generate_markdown_index(categories)
    
    def generate_markdown_index(self, categories: Dict[str, List[str]]):
        """Generate a markdown index of all papers."""
        md_content = f"""# ACGS Research Papers Index
# Constitutional Hash: {CONSTITUTIONAL_HASH}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Download Statistics
- Total papers found: {self.download_stats['total_found']}
- Successfully downloaded: {self.download_stats['downloaded']}
- Already existed (skipped): {self.download_stats['skipped']}
- Download errors: {self.download_stats['errors']}

## Papers by Category

"""
        
        for category, paper_ids in categories.items():
            if paper_ids:
                md_content += f"### {category.replace('_', ' ').title()} ({len(paper_ids)} papers)\n\n"
                
                for arxiv_id in paper_ids:
                    if arxiv_id in self.paper_metadata:
                        metadata = self.paper_metadata[arxiv_id]
                        authors_str = ", ".join(metadata['authors'][:3])
                        if len(metadata['authors']) > 3:
                            authors_str += " et al."
                        
                        md_content += f"- **[{metadata['title']}]({metadata['abs_url']})** "
                        md_content += f"([PDF]({metadata['pdf_url']}))\n"
                        md_content += f"  - Authors: {authors_str}\n"
                        md_content += f"  - arXiv ID: {arxiv_id}\n"
                        md_content += f"  - Published: {metadata['published'][:10]}\n\n"
        
        with open(self.papers_dir / "README.md", 'w') as f:
            f.write(md_content)
    
    async def download_all_papers(self):
        """Download all papers found in bibliography files."""
        logger.info("Starting ACGS research paper download")
        logger.info(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
        
        # Get all arXiv IDs
        arxiv_ids = self.get_all_arxiv_ids()
        self.download_stats["total_found"] = len(arxiv_ids)
        
        if not arxiv_ids:
            logger.warning("No arXiv IDs found in bibliography files")
            return
        
        # Download papers with progress bar
        with tqdm(total=len(arxiv_ids), desc="Downloading papers") as pbar:
            for arxiv_id in arxiv_ids:
                try:
                    # Get metadata
                    metadata = await self.get_paper_metadata(arxiv_id)
                    if metadata:
                        self.paper_metadata[arxiv_id] = metadata
                        
                        # Download PDF
                        await self.download_paper_pdf(arxiv_id, metadata)
                    
                    # Rate limiting
                    await asyncio.sleep(self.request_delay)
                    pbar.update(1)
                    
                except Exception as e:
                    logger.error(f"Error processing {arxiv_id}: {e}")
                    self.download_stats["errors"] += 1
                    pbar.update(1)
        
        # Generate index files
        self.generate_index_files()
        
        logger.info("Download completed!")
        logger.info(f"Downloaded: {self.download_stats['downloaded']} papers")
        logger.info(f"Skipped: {self.download_stats['skipped']} papers")
        logger.info(f"Errors: {self.download_stats['errors']} papers")

async def main():
    """Main function."""
    research_dir = Path(__file__).parent
    downloader = ArxivPaperDownloader(research_dir)
    
    await downloader.download_all_papers()

if __name__ == "__main__":
    asyncio.run(main())
