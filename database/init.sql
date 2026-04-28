-- CREATE EXTENSION IF NOT EXISTS postgis;
-- CREATE EXTENSION IF NOT EXISTS vector;

-- CREATE TABLE satellite_tiles (
--     id              BIGSERIAL PRIMARY KEY,
--     tile_hash       TEXT UNIQUE NOT NULL,
--     geom            GEOMETRY(Polygon, 4326) NOT NULL,
--     center_point    GEOMETRY(Point, 4326) NOT NULL,
--     embedding       VECTOR(768),              -- DINOv2 base output dimension
--     tile_size_px    INTEGER NOT NULL,
--     zoom_level      INTEGER NOT NULL,
--     source          TEXT DEFAULT 'google_maps',
--     image_path      TEXT,
--     similarity      FLOAT,
--     captured_at     TIMESTAMP,
--     created_at      TIMESTAMP DEFAULT NOW()
-- );

-- CREATE TABLE search_history (
--     id              BIGSERIAL PRIMARY KEY,
--     query_image_hash TEXT NOT NULL,
--     bbox            GEOMETRY(Polygon, 4326) NOT NULL,
--     threshold       FLOAT NOT NULL,
--     results_count   INTEGER,
--     created_at      TIMESTAMP DEFAULT NOW()
-- );

-- CREATE TABLE saved_regions (
--     id              BIGSERIAL PRIMARY KEY,
--     name            TEXT NOT NULL,
--     geom            GEOMETRY(Polygon, 4326) NOT NULL,
--     zoom_level      INTEGER,
--     is_processed    BOOLEAN DEFAULT FALSE,
--     created_at      TIMESTAMP DEFAULT NOW()
-- );

-- -- Indexes
-- CREATE INDEX idx_tiles_geom ON satellite_tiles USING GIST (geom);
-- CREATE INDEX idx_tiles_embedding ON satellite_tiles USING hnsw (embedding vector_cosine_ops);
-- CREATE INDEX idx_tiles_source ON satellite_tiles (source);
-- CREATE INDEX idx_regions_geom ON saved_regions USING GIST (geom);
CREATE EXTENSION IF NOT EXISTS postgis;
-- CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE satellite_tiles (
    id              BIGSERIAL PRIMARY KEY,
    tile_hash       TEXT UNIQUE NOT NULL,
    geom            GEOMETRY(Polygon, 4326) NOT NULL,
    center_point    GEOMETRY(Point, 4326) NOT NULL,
    tile_size_px    INTEGER NOT NULL,
    zoom_level      INTEGER NOT NULL,
    source          TEXT DEFAULT 'google_maps',
    image_path      TEXT,
    similarity      FLOAT,
    captured_at     TIMESTAMP,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE search_history (
    id              BIGSERIAL PRIMARY KEY,
    query_image_hash TEXT NOT NULL,
    bbox            GEOMETRY(Polygon, 4326) NOT NULL,
    threshold       FLOAT NOT NULL,
    results_count   INTEGER,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE saved_regions (
    id              BIGSERIAL PRIMARY KEY,
    name            TEXT NOT NULL,
    geom            GEOMETRY(Polygon, 4326) NOT NULL,
    zoom_level      INTEGER,
    is_processed    BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_tiles_geom ON satellite_tiles USING GIST (geom);
CREATE INDEX idx_tiles_source ON satellite_tiles (source);
CREATE INDEX idx_regions_geom ON saved_regions USING GIST (geom);