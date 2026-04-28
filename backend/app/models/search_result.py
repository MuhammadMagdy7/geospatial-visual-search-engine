from sqlalchemy import Column, Integer, String, Float, DateTime, func, BigInteger
from geoalchemy2 import Geometry
from ..database import Base

class SearchHistory(Base):
    __tablename__ = "search_history"

    id = Column(BigInteger, primary_key=True)
    query_image_hash = Column(String, nullable=False)
    bbox = Column(Geometry("POLYGON", srid=4326), nullable=False)
    threshold = Column(Float, nullable=False)
    results_count = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())
