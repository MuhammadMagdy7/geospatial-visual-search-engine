from sqlalchemy import Column, Integer, String, Float, DateTime, func, BigInteger
from geoalchemy2 import Geometry
from pgvector.sqlalchemy import Vector
from ..database import Base


class SatelliteTile(Base):
    __tablename__ = "satellite_tiles"

    id = Column(BigInteger, primary_key=True)
    tile_hash = Column(String, unique=True, nullable=False)
    geom = Column(Geometry("POLYGON", srid=4326), nullable=False)
    center_point = Column(Geometry("POINT", srid=4326), nullable=False)
    embedding = Column(Vector(512))  # RemoteCLIP ViT-B/32 outputs 512-dim
    tile_size_px = Column(Integer, nullable=False)
    zoom_level = Column(Integer, nullable=False)
    source = Column(String, default="google_maps")
    image_path = Column(String)
    captured_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
