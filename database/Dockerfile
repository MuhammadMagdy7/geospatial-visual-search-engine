# Pre-built image with PostgreSQL + PostGIS + pgvector
# Avoids apt-get dependency issues in restricted networks
FROM ghcr.io/payloadcms/postgis-vector:latest

# Copy init script (will run on first container start)
COPY init.sql /docker-entrypoint-initdb.d/init.sql