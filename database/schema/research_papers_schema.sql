-- Research Papers Knowledge Base Schema
-- PostgreSQL Database for ACGS Research Materials

-- Create database (run as superuser)
-- CREATE DATABASE acgs_research_kb;

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Authors table
CREATE TABLE authors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    affiliation VARCHAR(500),
    orcid VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create unique index on author name for deduplication
CREATE UNIQUE INDEX idx_authors_name ON authors(name);

-- Research categories and topics
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    parent_id UUID REFERENCES categories(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Keywords/tags
CREATE TABLE keywords (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    keyword VARCHAR(100) NOT NULL UNIQUE,
    category_id UUID REFERENCES categories(id),
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Research papers main table
CREATE TABLE papers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    abstract TEXT,
    arxiv_id VARCHAR(50),
    doi VARCHAR(255),
    publication_date DATE,
    venue VARCHAR(255),
    venue_type VARCHAR(50), -- 'conference', 'journal', 'preprint', 'workshop'
    paper_type VARCHAR(50), -- 'research', 'survey', 'position', 'technical'
    file_path VARCHAR(500),
    file_size BIGINT,
    page_count INTEGER,
    language VARCHAR(10) DEFAULT 'en',
    is_open_access BOOLEAN DEFAULT false,
    quality_score DECIMAL(3,2), -- 0.0 to 5.0
    relevance_score DECIMAL(3,2), -- 0.0 to 5.0 for ACGS relevance
    full_text TEXT, -- Extracted text content
    citations_count INTEGER DEFAULT 0,
    
    -- Administrative fields
    added_by VARCHAR(100),
    processed_at TIMESTAMP WITH TIME ZONE,
    last_accessed TIMESTAMP WITH TIME ZONE,
    access_count INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Paper authors relationship
CREATE TABLE paper_authors (
    paper_id UUID REFERENCES papers(id) ON DELETE CASCADE,
    author_id UUID REFERENCES authors(id) ON DELETE CASCADE,
    author_order INTEGER NOT NULL,
    is_corresponding BOOLEAN DEFAULT false,
    PRIMARY KEY (paper_id, author_id)
);

-- Paper keywords relationship
CREATE TABLE paper_keywords (
    paper_id UUID REFERENCES papers(id) ON DELETE CASCADE,
    keyword_id UUID REFERENCES keywords(id) ON DELETE CASCADE,
    relevance_score DECIMAL(3,2) DEFAULT 1.0,
    PRIMARY KEY (paper_id, keyword_id)
);

-- Paper citations (references between papers)
CREATE TABLE paper_citations (
    citing_paper_id UUID REFERENCES papers(id) ON DELETE CASCADE,
    cited_paper_id UUID REFERENCES papers(id) ON DELETE CASCADE,
    citation_context TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (citing_paper_id, cited_paper_id)
);

-- Research notes and annotations
CREATE TABLE paper_annotations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    paper_id UUID REFERENCES papers(id) ON DELETE CASCADE,
    annotation_type VARCHAR(50), -- 'note', 'highlight', 'bookmark', 'summary'
    content TEXT NOT NULL,
    page_number INTEGER,
    position_data JSONB, -- For precise positioning
    tags TEXT[],
    author VARCHAR(100),
    is_public BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Reading lists and collections
CREATE TABLE collections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT false,
    created_by VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Papers in collections
CREATE TABLE collection_papers (
    collection_id UUID REFERENCES collections(id) ON DELETE CASCADE,
    paper_id UUID REFERENCES papers(id) ON DELETE CASCADE,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    notes TEXT,
    PRIMARY KEY (collection_id, paper_id)
);

-- Search and access logs
CREATE TABLE search_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    query TEXT NOT NULL,
    search_type VARCHAR(50), -- 'fulltext', 'metadata', 'semantic'
    results_count INTEGER,
    user_id VARCHAR(100),
    ip_address INET,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_papers_title_gin ON papers USING gin(title gin_trgm_ops);
CREATE INDEX idx_papers_abstract_gin ON papers USING gin(abstract gin_trgm_ops);
CREATE INDEX idx_papers_fulltext_gin ON papers USING gin(full_text gin_trgm_ops);
CREATE INDEX idx_papers_arxiv_id ON papers(arxiv_id);
CREATE INDEX idx_papers_doi ON papers(doi);
CREATE INDEX idx_papers_publication_date ON papers(publication_date);
CREATE INDEX idx_papers_venue ON papers(venue);
CREATE INDEX idx_papers_relevance_score ON papers(relevance_score DESC);
CREATE INDEX idx_papers_quality_score ON papers(quality_score DESC);

CREATE INDEX idx_authors_name_gin ON authors USING gin(name gin_trgm_ops);
CREATE INDEX idx_keywords_keyword_gin ON keywords USING gin(keyword gin_trgm_ops);

CREATE INDEX idx_paper_authors_paper ON paper_authors(paper_id);
CREATE INDEX idx_paper_authors_author ON paper_authors(author_id);
CREATE INDEX idx_paper_keywords_paper ON paper_keywords(paper_id);
CREATE INDEX idx_paper_keywords_keyword ON paper_keywords(keyword_id);

-- Create full-text search configuration
CREATE TEXT SEARCH CONFIGURATION acgs_papers (COPY = english);

-- Create materialized view for fast paper search
CREATE MATERIALIZED VIEW paper_search_view AS
SELECT 
    p.id,
    p.title,
    p.abstract,
    p.arxiv_id,
    p.doi,
    p.publication_date,
    p.venue,
    p.quality_score,
    p.relevance_score,
    array_agg(DISTINCT a.name) as authors,
    array_agg(DISTINCT k.keyword) as keywords,
    setweight(to_tsvector('acgs_papers', coalesce(p.title, '')), 'A') ||
    setweight(to_tsvector('acgs_papers', coalesce(p.abstract, '')), 'B') ||
    setweight(to_tsvector('acgs_papers', coalesce(string_agg(a.name, ' '), '')), 'C') ||
    setweight(to_tsvector('acgs_papers', coalesce(string_agg(k.keyword, ' '), '')), 'D') as search_vector
FROM papers p
LEFT JOIN paper_authors pa ON p.id = pa.paper_id
LEFT JOIN authors a ON pa.author_id = a.id
LEFT JOIN paper_keywords pk ON p.id = pk.paper_id
LEFT JOIN keywords k ON pk.keyword_id = k.id
GROUP BY p.id, p.title, p.abstract, p.arxiv_id, p.doi, p.publication_date, p.venue, p.quality_score, p.relevance_score;

-- Create index on search vector
CREATE INDEX idx_paper_search_vector ON paper_search_view USING gin(search_vector);

-- Create functions for automatic updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers
CREATE TRIGGER update_papers_updated_at BEFORE UPDATE ON papers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_authors_updated_at BEFORE UPDATE ON authors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_annotations_updated_at BEFORE UPDATE ON paper_annotations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_collections_updated_at BEFORE UPDATE ON collections
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to refresh search view
CREATE OR REPLACE FUNCTION refresh_paper_search_view()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW paper_search_view;
END;
$$ language 'plpgsql';

-- Function to update keyword usage count
CREATE OR REPLACE FUNCTION update_keyword_usage()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE keywords SET usage_count = usage_count + 1 WHERE id = NEW.keyword_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE keywords SET usage_count = usage_count - 1 WHERE id = OLD.keyword_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_keyword_usage_trigger
    AFTER INSERT OR DELETE ON paper_keywords
    FOR EACH ROW EXECUTE FUNCTION update_keyword_usage();
