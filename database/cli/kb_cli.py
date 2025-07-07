#!/usr/bin/env python3
"""
ACGS Research Papers Knowledge Base CLI

Command-line interface for searching and managing the research papers database.
"""

import os
import sys
import argparse
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import tabulate

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

class KnowledgeBaseCLI:
    """CLI for ACGS Research Papers Knowledge Base"""
    
    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.connection = None
    
    def connect(self):
        """Connect to database"""
        try:
            self.connection = psycopg2.connect(
                host=self.db_config['DB_HOST'],
                port=self.db_config['DB_PORT'],
                database=self.db_config['DB_NAME'],
                user=self.db_config['DB_USER'],
                password=self.db_config['DB_PASSWORD']
            )
            return True
        except Exception as e:
            print(f"Failed to connect to database: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from database"""
        if self.connection:
            self.connection.close()
    
    def search_papers(self, query: str, limit: int = 10, search_type: str = 'fulltext') -> List[Dict]:
        """Search papers using various methods"""
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            if search_type == 'fulltext':
                # Full-text search using PostgreSQL's search capabilities
                cursor.execute("""
                    SELECT p.id, p.title, p.abstract, p.arxiv_id, p.venue, p.publication_date,
                           p.relevance_score, papers.file_path,
                           p.authors, p.keywords,
                           ts_rank(search_vector, plainto_tsquery('acgs_papers', %s)) as rank
                    FROM paper_search_view p
                    JOIN papers ON p.id = papers.id
                    WHERE search_vector @@ plainto_tsquery('acgs_papers', %s)
                    ORDER BY rank DESC, p.relevance_score DESC
                    LIMIT %s
                """, (query, query, limit))
            
            elif search_type == 'title':
                # Search by title similarity
                cursor.execute("""
                    SELECT p.id, p.title, p.abstract, p.arxiv_id, p.venue, p.publication_date,
                           p.relevance_score, p.file_path,
                           array_agg(DISTINCT a.name) as authors,
                           array_agg(DISTINCT k.keyword) as keywords
                    FROM papers p
                    LEFT JOIN paper_authors pa ON p.id = pa.paper_id
                    LEFT JOIN authors a ON pa.author_id = a.id
                    LEFT JOIN paper_keywords pk ON p.id = pk.paper_id
                    LEFT JOIN keywords k ON pk.keyword_id = k.id
                    WHERE p.title ILIKE %s
                    GROUP BY p.id, p.title, p.abstract, p.arxiv_id, p.venue, p.publication_date,
                             p.relevance_score, p.file_path
                    ORDER BY p.relevance_score DESC
                    LIMIT %s
                """, (f'%{query}%', limit))
            
            elif search_type == 'keyword':
                # Search by keywords
                cursor.execute("""
                    SELECT p.id, p.title, p.abstract, p.arxiv_id, p.venue, p.publication_date,
                           p.relevance_score, p.file_path,
                           array_agg(DISTINCT a.name) as authors,
                           array_agg(DISTINCT k.keyword) as keywords
                    FROM papers p
                    LEFT JOIN paper_authors pa ON p.id = pa.paper_id
                    LEFT JOIN authors a ON pa.author_id = a.id
                    LEFT JOIN paper_keywords pk ON p.id = pk.paper_id
                    LEFT JOIN keywords k ON pk.keyword_id = k.id
                    WHERE p.id IN (
                        SELECT DISTINCT pk2.paper_id 
                        FROM paper_keywords pk2
                        JOIN keywords k2 ON pk2.keyword_id = k2.id
                        WHERE k2.keyword ILIKE %s
                    )
                    GROUP BY p.id, p.title, p.abstract, p.arxiv_id, p.venue, p.publication_date,
                             p.relevance_score, p.file_path
                    ORDER BY p.relevance_score DESC
                    LIMIT %s
                """, (f'%{query}%', limit))
            
            elif search_type == 'author':
                # Search by author
                cursor.execute("""
                    SELECT p.id, p.title, p.abstract, p.arxiv_id, p.venue, p.publication_date,
                           p.relevance_score, p.file_path,
                           array_agg(DISTINCT a.name) as authors,
                           array_agg(DISTINCT k.keyword) as keywords
                    FROM papers p
                    LEFT JOIN paper_authors pa ON p.id = pa.paper_id
                    LEFT JOIN authors a ON pa.author_id = a.id
                    LEFT JOIN paper_keywords pk ON p.id = pk.paper_id
                    LEFT JOIN keywords k ON pk.keyword_id = k.id
                    WHERE p.id IN (
                        SELECT DISTINCT pa2.paper_id 
                        FROM paper_authors pa2
                        JOIN authors a2 ON pa2.author_id = a2.id
                        WHERE a2.name ILIKE %s
                    )
                    GROUP BY p.id, p.title, p.abstract, p.arxiv_id, p.venue, p.publication_date,
                             p.relevance_score, p.file_path
                    ORDER BY p.relevance_score DESC
                    LIMIT %s
                """, (f'%{query}%', limit))
            
            return cursor.fetchall()
    
    def get_paper_details(self, paper_id: str) -> Dict:
        """Get detailed information about a specific paper"""
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT p.*,
                       (
                           SELECT array_agg(a2.name ORDER BY pa2.author_order)
                           FROM paper_authors pa2
                           JOIN authors a2 ON pa2.author_id = a2.id
                           WHERE pa2.paper_id = p.id
                       ) as authors,
                       array_agg(DISTINCT k.keyword) as keywords
                FROM papers p
                LEFT JOIN paper_keywords pk ON p.id = pk.paper_id
                LEFT JOIN keywords k ON pk.keyword_id = k.id
                WHERE p.id = %s
                GROUP BY p.id
            """, (paper_id,))
            
            return cursor.fetchone()
    
    def list_categories(self) -> List[Dict]:
        """List all research categories"""
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT c.name, c.description, 
                       COUNT(DISTINCT pk.paper_id) as paper_count
                FROM categories c
                LEFT JOIN keywords k ON c.id = k.category_id
                LEFT JOIN paper_keywords pk ON k.id = pk.keyword_id
                WHERE c.parent_id IS NULL
                GROUP BY c.id, c.name, c.description
                ORDER BY paper_count DESC, c.name
            """)
            
            return cursor.fetchall()
    
    def list_collections(self) -> List[Dict]:
        """List all paper collections"""
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT c.id, c.name, c.description, c.is_public, c.created_by,
                       COUNT(cp.paper_id) as paper_count
                FROM collections c
                LEFT JOIN collection_papers cp ON c.id = cp.collection_id
                GROUP BY c.id, c.name, c.description, c.is_public, c.created_by
                ORDER BY paper_count DESC, c.name
            """)
            
            return cursor.fetchall()
    
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            # Paper statistics
            cursor.execute("SELECT COUNT(*) as total_papers FROM papers")
            total_papers = cursor.fetchone()['total_papers']
            
            cursor.execute("SELECT COUNT(DISTINCT venue) as unique_venues FROM papers WHERE venue IS NOT NULL")
            unique_venues = cursor.fetchone()['unique_venues']
            
            cursor.execute("SELECT COUNT(*) as total_authors FROM authors")
            total_authors = cursor.fetchone()['total_authors']
            
            cursor.execute("SELECT COUNT(*) as total_keywords FROM keywords")
            total_keywords = cursor.fetchone()['total_keywords']
            
            cursor.execute("SELECT AVG(relevance_score) as avg_relevance FROM papers WHERE relevance_score IS NOT NULL")
            avg_relevance = cursor.fetchone()['avg_relevance']
            
            # Top venues
            cursor.execute("""
                SELECT venue, COUNT(*) as paper_count 
                FROM papers 
                WHERE venue IS NOT NULL 
                GROUP BY venue 
                ORDER BY paper_count DESC 
                LIMIT 5
            """)
            top_venues = cursor.fetchall()
            
            # Top keywords
            cursor.execute("""
                SELECT k.keyword, k.usage_count
                FROM keywords k
                ORDER BY k.usage_count DESC
                LIMIT 10
            """)
            top_keywords = cursor.fetchall()
            
            return {
                'total_papers': total_papers,
                'total_authors': total_authors,
                'total_keywords': total_keywords,
                'unique_venues': unique_venues,
                'avg_relevance': float(avg_relevance) if avg_relevance else 0.0,
                'top_venues': top_venues,
                'top_keywords': top_keywords
            }
    
    def format_search_results(self, results: List[Dict], detailed: bool = False) -> str:
        """Format search results for display"""
        if not results:
            return "No papers found."
        
        if detailed:
            output = []
            for i, paper in enumerate(results, 1):
                authors_str = ', '.join(paper.get('authors', []) or [])
                keywords_str = ', '.join(paper.get('keywords', []) or [])
                
                output.append(f"\n{i}. {paper['title']}")
                output.append(f"   ID: {paper['id']}")
                output.append(f"   Authors: {authors_str}")
                output.append(f"   Venue: {paper.get('venue', 'N/A')} ({paper.get('publication_date', 'N/A')})")
                output.append(f"   ArXiv ID: {paper.get('arxiv_id', 'N/A')}")
                output.append(f"   Relevance: {paper.get('relevance_score', 0.0):.2f}")
                output.append(f"   Keywords: {keywords_str}")
                if paper.get('abstract'):
                    abstract = paper['abstract'][:200] + "..." if len(paper['abstract']) > 200 else paper['abstract']
                    output.append(f"   Abstract: {abstract}")
                output.append(f"   File: {paper.get('file_path', 'N/A')}")
            
            return '\n'.join(output)
        else:
            # Table format
            table_data = []
            for paper in results:
                authors_str = ', '.join((paper.get('authors', []) or [])[:2])  # First 2 authors
                if len(paper.get('authors', []) or []) > 2:
                    authors_str += " et al."
                
                pub_date = paper.get('publication_date', 'N/A')
                if hasattr(pub_date, 'strftime'):
                    pub_date_str = pub_date.strftime('%Y-%m-%d')
                else:
                    pub_date_str = str(pub_date)[:10] if pub_date != 'N/A' else 'N/A'
                
                table_data.append([
                    paper['id'][:8],  # Short ID
                    paper['title'][:50] + "..." if len(paper['title']) > 50 else paper['title'],
                    authors_str[:30] + "..." if len(authors_str) > 30 else authors_str,
                    paper.get('venue', 'N/A')[:15],
                    pub_date_str,
                    f"{paper.get('relevance_score', 0.0):.1f}"
                ])
            
            headers = ['ID', 'Title', 'Authors', 'Venue', 'Date', 'Rel.']
            return tabulate.tabulate(table_data, headers=headers, tablefmt='grid')

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description="ACGS Research Papers Knowledge Base CLI")
    
    # Database config
    parser.add_argument("--config", type=Path, help="Database config file path")
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search papers')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--type', choices=['fulltext', 'title', 'keyword', 'author'], 
                              default='fulltext', help='Search type')
    search_parser.add_argument('--limit', type=int, default=10, help='Number of results')
    search_parser.add_argument('--detailed', action='store_true', help='Show detailed results')
    
    # Show command
    show_parser = subparsers.add_parser('show', help='Show paper details')
    show_parser.add_argument('paper_id', help='Paper ID')
    
    # List commands
    list_parser = subparsers.add_parser('list', help='List items')
    list_parser.add_argument('item', choices=['categories', 'collections'], help='What to list')
    
    # Stats command
    subparsers.add_parser('stats', help='Show database statistics')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Load database configuration
    config_path = args.config or (Path(__file__).parent.parent / ".env")
    if config_path.exists():
        load_dotenv(config_path)
    
    db_config = {
        'DB_HOST': os.getenv('DB_HOST', 'localhost'),
        'DB_PORT': os.getenv('DB_PORT', '5432'),
        'DB_NAME': os.getenv('DB_NAME', 'acgs_research_kb'),
        'DB_USER': os.getenv('DB_USER', 'acgs_user'),
        'DB_PASSWORD': os.getenv('DB_PASSWORD', 'acgs_secure_password_2025')
    }
    
    # Create CLI instance
    cli = KnowledgeBaseCLI(db_config)
    
    if not cli.connect():
        sys.exit(1)
    
    try:
        if args.command == 'search':
            results = cli.search_papers(args.query, args.limit, args.type)
            print(cli.format_search_results(results, args.detailed))
            
        elif args.command == 'show':
            paper = cli.get_paper_details(args.paper_id)
            if paper:
                print(f"\nTitle: {paper['title']}")
                print(f"ID: {paper['id']}")
                
                if paper.get('authors'):
                    print(f"Authors: {', '.join(paper['authors'])}")
                
                if paper.get('abstract'):
                    print(f"\nAbstract:\n{paper['abstract']}")
                
                print(f"\nDetails:")
                print(f"  ArXiv ID: {paper.get('arxiv_id', 'N/A')}")
                print(f"  DOI: {paper.get('doi', 'N/A')}")
                print(f"  Venue: {paper.get('venue', 'N/A')} ({paper.get('venue_type', 'N/A')})")
                print(f"  Publication Date: {paper.get('publication_date', 'N/A')}")
                print(f"  Paper Type: {paper.get('paper_type', 'N/A')}")
                print(f"  Relevance Score: {paper.get('relevance_score', 0.0):.2f}")
                print(f"  File Path: {paper.get('file_path', 'N/A')}")
                print(f"  File Size: {paper.get('file_size', 0)} bytes")
                print(f"  Page Count: {paper.get('page_count', 'N/A')}")
                
                if paper.get('keywords'):
                    print(f"  Keywords: {', '.join(paper['keywords'])}")
                
            else:
                print(f"Paper with ID {args.paper_id} not found.")
                
        elif args.command == 'list':
            if args.item == 'categories':
                categories = cli.list_categories()
                table_data = [[c['name'], c['description'][:50], c['paper_count']] for c in categories]
                print(tabulate.tabulate(table_data, headers=['Category', 'Description', 'Papers'], tablefmt='grid'))
                
            elif args.item == 'collections':
                collections = cli.list_collections()
                table_data = [[c['name'], c['description'][:50], c['paper_count'], 
                             'Yes' if c['is_public'] else 'No'] for c in collections]
                print(tabulate.tabulate(table_data, headers=['Collection', 'Description', 'Papers', 'Public'], tablefmt='grid'))
                
        elif args.command == 'stats':
            stats = cli.get_statistics()
            print("\nACGS Research Papers Knowledge Base Statistics")
            print("=" * 50)
            print(f"Total Papers: {stats['total_papers']}")
            print(f"Total Authors: {stats['total_authors']}")
            print(f"Total Keywords: {stats['total_keywords']}")
            print(f"Unique Venues: {stats['unique_venues']}")
            print(f"Average Relevance Score: {stats['avg_relevance']:.2f}")
            
            if stats['top_venues']:
                print("\nTop Venues:")
                for venue in stats['top_venues']:
                    print(f"  {venue['venue']}: {venue['paper_count']} papers")
            
            if stats['top_keywords']:
                print("\nTop Keywords:")
                for keyword in stats['top_keywords']:
                    print(f"  {keyword['keyword']}: {keyword['usage_count']} papers")
                    
    finally:
        cli.disconnect()

if __name__ == "__main__":
    main()
