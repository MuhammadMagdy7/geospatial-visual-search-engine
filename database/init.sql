-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS vector;

-- Note: Tables are created via Alembic migrations in Task 1.3
-- This file only ensures extensions are available at DB initialization