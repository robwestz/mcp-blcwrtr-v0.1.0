-- MCP BacklinkContent Database Schema
-- Version: 1.0.0
-- Idempotent initialization script

-- Create UUID extension if not exists
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Customers table
CREATE TABLE IF NOT EXISTS customers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    target_market TEXT,
    seo_goals JSONB DEFAULT '{}'::jsonb,
    latest_ai_insight TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Pages table
CREATE TABLE IF NOT EXISTS pages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    url TEXT NOT NULL UNIQUE,
    type TEXT CHECK (type IN ('landing', 'article', 'category', 'product')),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Links table
CREATE TABLE IF NOT EXISTS links (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    source_url TEXT NOT NULL,
    target_url TEXT NOT NULL,
    anchor_text TEXT NOT NULL,
    dr_score NUMERIC(3,1),
    status TEXT CHECK (status IN ('planned', 'placed', 'live', 'removed', 'rejected')),
    cost_sek NUMERIC(10,2),
    placed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Anchor portfolio table
CREATE TABLE IF NOT EXISTS anchor_portfolio (
    target_domain TEXT PRIMARY KEY,
    exact INTEGER DEFAULT 0,
    partial INTEGER DEFAULT 0,
    brand INTEGER DEFAULT 0,
    generic INTEGER DEFAULT 0,
    risk NUMERIC(3,2) CHECK (risk >= 0 AND risk <= 1),
    last_calculated TIMESTAMPTZ DEFAULT NOW()
);

-- Entity graph table
CREATE TABLE IF NOT EXISTS entity_graph (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    graph_name TEXT NOT NULL,
    nodes JSONB NOT NULL,
    edges JSONB NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- SERP snapshots table  
CREATE TABLE IF NOT EXISTS serp_snapshots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    query TEXT NOT NULL,
    locale TEXT NOT NULL DEFAULT 'sv-SE',
    intents JSONB NOT NULL,
    lsi_terms JSONB NOT NULL,
    top_urls JSONB NOT NULL,
    ttl TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Publisher profiles table
CREATE TABLE IF NOT EXISTS publisher_profiles (
    domain TEXT PRIMARY KEY,
    voice JSONB NOT NULL,
    lix_range TEXT CHECK (lix_range IN ('very_easy', 'easy', 'medium', 'hard', 'very_hard')),
    policy JSONB DEFAULT '{}'::jsonb,
    examples JSONB DEFAULT '[]'::jsonb,
    verified_at TIMESTAMPTZ DEFAULT NOW()
);

-- Trust registry table
CREATE TABLE IF NOT EXISTS trust_registry (
    domain TEXT PRIMARY KEY,
    trust_level TEXT CHECK (trust_level IN ('T1', 'T2', 'T3', 'T4')),
    region TEXT DEFAULT 'SE',
    competitor BOOLEAN DEFAULT false,
    pattern TEXT,
    notes TEXT,
    last_verified TIMESTAMPTZ DEFAULT NOW()
);

-- Audit log table
CREATE TABLE IF NOT EXISTS audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_ref UUID,
    step TEXT NOT NULL,
    status TEXT NOT NULL,
    error_code TEXT,
    payload JSONB DEFAULT '{}'::jsonb,
    ts TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_links_customer_id ON links(customer_id);
CREATE INDEX IF NOT EXISTS idx_links_target_url ON links(target_url);
CREATE INDEX IF NOT EXISTS idx_links_status ON links(status);
CREATE INDEX IF NOT EXISTS idx_pages_customer_id ON pages(customer_id);
CREATE INDEX IF NOT EXISTS idx_audit_order_ref ON audit_log(order_ref);
CREATE INDEX IF NOT EXISTS idx_audit_ts ON audit_log(ts);
CREATE INDEX IF NOT EXISTS idx_serp_query_locale ON serp_snapshots(query, locale);

-- Insert some initial trust sources
INSERT INTO trust_registry (domain, trust_level, region, competitor, pattern) 
VALUES 
    ('riksarkivet.se', 'T1', 'SE', false, 'government'),
    ('kb.se', 'T1', 'SE', false, 'government'), 
    ('scb.se', 'T1', 'SE', false, 'government'),
    ('wikipedia.org', 'T2', 'GLOBAL', false, 'encyclopedia'),
    ('dn.se', 'T2', 'SE', false, 'news'),
    ('svt.se', 'T2', 'SE', false, 'news'),
    ('aftonbladet.se', 'T3', 'SE', false, 'tabloid'),
    ('expressen.se', 'T3', 'SE', false, 'tabloid')
ON CONFLICT (domain) DO NOTHING;

-- Create update timestamp function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add update triggers
DO $$ 
BEGIN
    -- Customers
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_customers_updated_at') THEN
        CREATE TRIGGER update_customers_updated_at BEFORE UPDATE ON customers
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;
    
    -- Pages
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_pages_updated_at') THEN
        CREATE TRIGGER update_pages_updated_at BEFORE UPDATE ON pages
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;
    
    -- Links
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_links_updated_at') THEN
        CREATE TRIGGER update_links_updated_at BEFORE UPDATE ON links
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;
END $$;

-- Verify installation
DO $$ 
BEGIN
    RAISE NOTICE 'Database schema initialized successfully';
    RAISE NOTICE 'Tables created: customers, pages, links, anchor_portfolio, entity_graph, serp_snapshots, publisher_profiles, trust_registry, audit_log';
END $$;
