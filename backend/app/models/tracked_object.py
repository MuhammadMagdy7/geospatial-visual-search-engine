"""User-saved/monitored objects discovered via visual search."""

from sqlalchemy import (
    Column, BigInteger, String, Text, Float, DateTime, Boolean, ForeignKey, func
)
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from pgvector.sqlalchemy import Vector
from ..database import Base


class TrackedObject(Base):
    __tablename__ = "tracked_objects"

    id = Column(BigInteger, primary_key=True)
    category_id = Column(
        BigInteger,
        ForeignKey("object_categories.id", ondelete="SET NULL"),
        nullable=True,
    )
    name = Column(String(255))                          # optional user-given name
    description = Column(Text)
    
    # Geospatial
    geom = Column(Geometry("POINT", srid=4326), nullable=False)
    bbox_geom = Column(Geometry("POLYGON", srid=4326))   # the surrounding tile
    
    # ML
    embedding = Column(Vector(512))                      # for future re-search
    
    # Metadata
    thumbnail_path = Column(String(512))
    similarity_at_save = Column(Float)
    is_monitored = Column(Boolean, default=False, nullable=False)
    notes = Column(Text)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationship
    category = relationship("ObjectCategory", back_populates="tracked_objects")
