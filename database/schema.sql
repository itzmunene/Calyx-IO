-- Calyx.io Database Schema
-- Run this in your Supabase SQL Editor

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- ============================================
-- 1. SPECIES TABLE (Core flower data)
-- ============================================
CREATE TABLE IF NOT EXISTS species (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scientific_name TEXT NOT NULL UNIQUE,
    common_names TEXT[] NOT NULL,
    family TEXT,
    
    -- Traits for elimination (stored as JSONB for flexibility)
    traits JSONB NOT NULL,
    /*
    Example traits structure:
    {
        "color_primary": ["yellow", "white"],
        "color_secondary": ["pink"],
        "petal_count": 5,
        "petal_arrangement": "single",
        "flower_size": "medium",
        "season": ["spring", "summer"]
    }
    */
    
    -- Vector embedding (CLIP-ViT-B/32 reduced to 384-dim)
    embedding vector(384),
    
    -- Metadata
    description TEXT,
    care_tips TEXT,
    bloom_season TEXT[],
    
    -- Images
    primary_image_url TEXT,
    thumbnail_url TEXT,
    image_license TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- 2. SPECIES MEDIA TABLE (Multiple images)
-- ============================================
CREATE TABLE IF NOT EXISTS species_media (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    species_id UUID REFERENCES species(id) ON DELETE CASCADE,
    image_url TEXT NOT NULL,
    thumbnail_url TEXT,
    quality_score FLOAT DEFAULT 0.5,
    source TEXT, -- 'iNaturalist', 'manual_upload', etc.
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- 3. IDENTIFICATION CACHE (Performance optimization)
-- ============================================
CREATE TABLE IF NOT EXISTS identification_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    image_hash TEXT UNIQUE NOT NULL,
    species_id UUID REFERENCES species(id),
    confidence FLOAT,
    traits_extracted JSONB,
    method TEXT, -- 'trait_elimination', 'vector_match', 'cache_hit'
    created_at TIMESTAMP DEFAULT NOW(),
    hit_count INTEGER DEFAULT 1,
    
    -- Auto-expire after 7 days
    expires_at TIMESTAMP DEFAULT (NOW() + INTERVAL '7 days')
);

-- ============================================
-- 4. USER FEEDBACK TABLE (Model improvement)
-- ============================================
CREATE TABLE IF NOT EXISTS identification_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cache_id UUID REFERENCES identification_cache(id),
    user_confirmed BOOLEAN,
    correct_species_id UUID REFERENCES species(id),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- INDEXES (Performance optimization)
-- ============================================

-- Traits search (JSONB GIN index)
CREATE INDEX IF NOT EXISTS idx_species_traits ON species USING GIN(traits);

-- Vector similarity search (IVFFlat index)
CREATE INDEX IF NOT EXISTS idx_species_embedding 
    ON species 
    USING ivfflat(embedding vector_cosine_ops) 
    WITH (lists = 10);

-- Text search on common names (GIN index for trigrams)
CREATE INDEX IF NOT EXISTS idx_species_common_names 
    ON species 
    USING GIN(common_names);

-- Text search on scientific names
CREATE INDEX IF NOT EXISTS idx_species_scientific_name 
    ON species 
    USING GIN(scientific_name gin_trgm_ops);

-- Cache lookup
CREATE INDEX IF NOT EXISTS idx_cache_hash 
    ON identification_cache(image_hash);

-- Cache expiration cleanup
CREATE INDEX IF NOT EXISTS idx_cache_expires 
    ON identification_cache(expires_at);

-- Species ID lookup
CREATE INDEX IF NOT EXISTS idx_species_id 
    ON species(id);

-- Media by species
CREATE INDEX IF NOT EXISTS idx_media_species 
    ON species_media(species_id);

-- ============================================
-- FUNCTIONS
-- ============================================

-- Vector similarity search function
CREATE OR REPLACE FUNCTION match_species(
    query_embedding vector(384),
    match_threshold float DEFAULT 0.5,
    match_count int DEFAULT 5
)
RETURNS TABLE (
    species_id uuid,
    scientific_name text,
    common_names text[],
    similarity float
)
LANGUAGE sql STABLE
AS $$
    SELECT
        s.id,
        s.scientific_name,
        s.common_names,
        1 - (s.embedding <=> query_embedding) as similarity
    FROM species s
    WHERE s.embedding IS NOT NULL
      AND 1 - (s.embedding <=> query_embedding) > match_threshold
    ORDER BY s.embedding <=> query_embedding
    LIMIT match_count;
$$;

-- Cleanup expired cache (run daily via cron)
CREATE OR REPLACE FUNCTION cleanup_expired_cache()
RETURNS void
LANGUAGE sql
AS $$
    DELETE FROM identification_cache
    WHERE expires_at < NOW();
$$;

-- Update timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_species_updated_at
    BEFORE UPDATE ON species
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- ROW LEVEL SECURITY (Optional - for future user accounts)
-- ============================================

-- Enable RLS on tables (disabled for now for simplicity)
-- ALTER TABLE species ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE species_media ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE identification_cache ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE identification_feedback ENABLE ROW LEVEL SECURITY;

-- ============================================
-- COMMENTS (Documentation)
-- ============================================

COMMENT ON TABLE species IS 'Core flower species data with traits and embeddings';
COMMENT ON COLUMN species.traits IS 'JSONB field containing searchable traits for elimination algorithm';
COMMENT ON COLUMN species.embedding IS '384-dimensional vector from CLIP model for similarity search';
COMMENT ON TABLE identification_cache IS 'Cache layer for repeated image identifications (7-day expiry)';
COMMENT ON FUNCTION match_species IS 'Vector similarity search using cosine distance';

-- ============================================
-- SUCCESS MESSAGE
-- ============================================

DO $$ 
BEGIN
    RAISE NOTICE '✅ Calyx.io database schema created successfully!';
    RAISE NOTICE 'Next steps:';
    RAISE NOTICE '1. Run seed_data.sql to insert 100 flower species';
    RAISE NOTICE '2. Set up Row Level Security policies if needed';
    RAISE NOTICE '3. Configure Supabase Storage for images';
END $$;
