"""initial schema

Revision ID: 0001_initial
Revises: 
Create Date: 2026-04-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = '0001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # NOTE: Extensions (postgis, vector) are created by init.sql at DB initialization.
    # We do NOT create them here to avoid issues if migration runs in environments
    # where the user lacks SUPERUSER privileges.

    # ---------- satellite_tiles ----------
    op.create_table(
        'satellite_tiles',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('tile_hash', sa.String(length=64), nullable=False),
        sa.Column('geom', Geometry('POLYGON', srid=4326), nullable=False),
        sa.Column('center_point', Geometry('POINT', srid=4326), nullable=False),
        sa.Column('embedding', Vector(512), nullable=True),
        sa.Column('tile_size_px', sa.Integer(), nullable=False),
        sa.Column('zoom_level', sa.Integer(), nullable=False),
        sa.Column('source', sa.String(length=50), server_default='google_maps'),
        sa.Column('image_path', sa.String(length=512), nullable=True),
        sa.Column('captured_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tile_hash'),
    )
    op.create_index('idx_tiles_geom', 'satellite_tiles', ['geom'], postgresql_using='gist')
    op.create_index('idx_tiles_source', 'satellite_tiles', ['source'])
    # HNSW index for vector cosine similarity search
    op.execute("""
        CREATE INDEX idx_tiles_embedding 
        ON satellite_tiles 
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
    """)

    # ---------- saved_regions ----------
    op.create_table(
        'saved_regions',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('geom', Geometry('POLYGON', srid=4326), nullable=False),
        sa.Column('zoom_level', sa.Integer(), nullable=True),
        sa.Column('is_processed', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_regions_geom', 'saved_regions', ['geom'], postgresql_using='gist')

    # ---------- search_history ----------
    op.create_table(
        'search_history',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('query_image_hash', sa.String(length=64), nullable=True),
        sa.Column('query_text', sa.Text(), nullable=True),
        sa.Column('bbox', Geometry('POLYGON', srid=4326), nullable=False),
        sa.Column('threshold', sa.Float(), nullable=False),
        sa.Column('results_count', sa.Integer(), nullable=True),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_history_bbox', 'search_history', ['bbox'], postgresql_using='gist')
    op.create_index('idx_history_created', 'search_history', ['created_at'])

    # ---------- object_categories ----------
    op.create_table(
        'object_categories',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('name_ar', sa.String(length=100), nullable=True),
        sa.Column('icon', sa.String(length=50), nullable=True),
        sa.Column('color', sa.String(length=7), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )

    # ---------- tracked_objects ----------
    op.create_table(
        'tracked_objects',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('category_id', sa.BigInteger(), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('geom', Geometry('POINT', srid=4326), nullable=False),
        sa.Column('bbox_geom', Geometry('POLYGON', srid=4326), nullable=True),
        sa.Column('embedding', Vector(512), nullable=True),
        sa.Column('thumbnail_path', sa.String(length=512), nullable=True),
        sa.Column('similarity_at_save', sa.Float(), nullable=True),
        sa.Column('is_monitored', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['category_id'], ['object_categories.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_tracked_geom', 'tracked_objects', ['geom'], postgresql_using='gist')
    op.create_index('idx_tracked_category', 'tracked_objects', ['category_id'])
    op.create_index(
        'idx_tracked_monitored',
        'tracked_objects',
        ['is_monitored'],
        postgresql_where=sa.text('is_monitored = true'),
    )


def downgrade() -> None:
    op.drop_table('tracked_objects')
    op.drop_table('object_categories')
    op.drop_table('search_history')
    op.drop_table('saved_regions')
    op.drop_index('idx_tiles_embedding', table_name='satellite_tiles')
    op.drop_table('satellite_tiles')
