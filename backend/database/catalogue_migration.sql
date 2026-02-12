-- Run this SQL in your Supabase SQL Editor to add catalogue features

-- Add search_count column for popularity tracking
ALTER TABLE species 
ADD COLUMN IF NOT EXISTS search_count INTEGER DEFAULT 0;

-- Add native_region column for location filtering
ALTER TABLE species 
ADD COLUMN IF NOT EXISTS native_region TEXT[];

-- Create index on search_count for fast popularity sorting
CREATE INDEX IF NOT EXISTS idx_species_search_count 
ON species(search_count DESC);

-- Create index on native_region for location filtering
CREATE INDEX IF NOT EXISTS idx_species_native_region 
ON species USING GIN(native_region);

-- Update existing records with sample data
-- You can customize this based on actual flower origins

-- Set random search counts for testing (0-1000)
UPDATE species 
SET search_count = FLOOR(RANDOM() * 1000)
WHERE search_count IS NULL OR search_count = 0;

-- Set sample native regions based on common flower origins
-- North American flowers
UPDATE species 
SET native_region = ARRAY['United States', 'Canada', 'Mexico']
WHERE scientific_name IN (
    'Helianthus annuus',  -- Sunflower
    'Echinacea purpurea', -- Purple Coneflower
    'Rudbeckia hirta'     -- Black-eyed Susan
);

-- European flowers
UPDATE species 
SET native_region = ARRAY['United Kingdom', 'France', 'Germany', 'Netherlands']
WHERE scientific_name IN (
    'Rosa rubiginosa',      -- Rose
    'Lavandula angustifolia', -- Lavender
    'Bellis perennis'       -- Daisy
);

-- Asian flowers
UPDATE species 
SET native_region = ARRAY['China', 'Japan', 'India']
WHERE scientific_name IN (
    'Chrysanthemum morifolium', -- Chrysanthemum
    'Paeonia lactiflora',       -- Peony
    'Camellia japonica'         -- Camellia
);

-- African flowers
UPDATE species 
SET native_region = ARRAY['South Africa', 'Kenya', 'Madagascar']
WHERE scientific_name IN (
    'Protea cynaroides',     -- King Protea
    'Strelitzia reginae',    -- Bird of Paradise
    'Zantedeschia aethiopica' -- Calla Lily
);

-- Tropical flowers (multiple regions)
UPDATE species 
SET native_region = ARRAY['Brazil', 'Indonesia', 'Philippines', 'Hawaii']
WHERE scientific_name IN (
    'Hibiscus rosa-sinensis', -- Hibiscus
    'Plumeria rubra',         -- Frangipani
    'Anthurium andraeanum'    -- Anthurium
);

-- Mediterranean flowers
UPDATE species 
SET native_region = ARRAY['Greece', 'Italy', 'Spain', 'Turkey']
WHERE scientific_name IN (
    'Narcissus poeticus',  -- Poet's Narcissus
    'Iris germanica',      -- Bearded Iris
    'Tulipa gesneriana'    -- Tulip
);

-- Set default for any remaining flowers
UPDATE species 
SET native_region = ARRAY['Global', 'Cultivated']
WHERE native_region IS NULL;

-- Add comment for documentation
COMMENT ON COLUMN species.search_count IS 'Number of times this flower has been searched/identified (for popularity tracking)';
COMMENT ON COLUMN species.native_region IS 'Array of countries/regions where this flower is native or commonly grown';
