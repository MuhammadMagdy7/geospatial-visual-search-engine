from sqlalchemy import Column, BigInteger, String, Integer, Boolean, DateTime, func
from geoalchemy2 import Geometry
from ..database import Base


class SavedRegion(Base):
    __tablename__ = "saved_regions"

    id = Column(BigInteger, primary_key=True)
    name = Column(String(255), nullable=False)
    geom = Column(Geometry("POLYGON", srid=4326), nullable=False)
    zoom_level = Column(Integer)
    is_processed = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
