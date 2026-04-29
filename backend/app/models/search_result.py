"""Search history for analytics and potential caching."""

from sqlalchemy import Column, BigInteger, String, Text, Float, Integer, DateTime, func
from geoalchemy2 import Geometry
from ..database import Base


class SearchHistory(Base):
    __tablename__ = "search_history"

    id = Column(BigInteger, primary_key=True)
    query_image_hash = Column(String(64))           # SHA256 of query image, nullable for text search
    query_text = Column(Text)                        # text query, nullable for image search
    bbox = Column(Geometry("POLYGON", srid=4326), nullable=False)
    threshold = Column(Float, nullable=False)
    results_count = Column(Integer)
    duration_ms = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())
