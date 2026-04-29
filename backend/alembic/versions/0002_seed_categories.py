"""seed default categories

Revision ID: 0002_seed_categories
Revises: 0001_initial
Create Date: 2026-04-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0002_seed_categories'
down_revision: Union[str, None] = '0001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


DEFAULT_CATEGORIES = [
    ("Cars", "سيارات", "Car", "#EF4444", "Vehicles, including parked cars in lots and on streets"),
    ("Aircraft", "طائرات", "Plane", "#3B82F6", "Airplanes, helicopters, and other aircraft"),
    ("Buildings", "مباني", "Building", "#10B981", "Residential, commercial, and industrial buildings"),
    ("Ships", "سفن", "Ship", "#06B6D4", "Boats, ships, and other watercraft"),
    ("Roads", "طرق", "Route", "#F59E0B", "Highways, streets, intersections"),
    ("Vegetation", "نباتات", "Trees", "#22C55E", "Forests, parks, agricultural land"),
    ("Water", "مياه", "Waves", "#0EA5E9", "Lakes, rivers, ponds, swimming pools"),
    ("Other", "أخرى", "Box", "#6B7280", "Anything not fitting the above categories"),
]


def upgrade() -> None:
    categories_table = sa.table(
        'object_categories',
        sa.column('name', sa.String),
        sa.column('name_ar', sa.String),
        sa.column('icon', sa.String),
        sa.column('color', sa.String),
        sa.column('description', sa.Text),
    )

    op.bulk_insert(
        categories_table,
        [
            {
                "name": name,
                "name_ar": name_ar,
                "icon": icon,
                "color": color,
                "description": description,
            }
            for (name, name_ar, icon, color, description) in DEFAULT_CATEGORIES
        ],
    )


def downgrade() -> None:
    op.execute("DELETE FROM object_categories WHERE name = ANY(ARRAY[%s])" % 
               ", ".join(f"'{name}'" for name, *_ in DEFAULT_CATEGORIES))
