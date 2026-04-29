"""Categories for tracked objects (cars, aircraft, buildings, etc.)."""

from sqlalchemy import Column, BigInteger, String, Text, DateTime, func
from sqlalchemy.orm import relationship
from ..database import Base


class ObjectCategory(Base):
    __tablename__ = "object_categories"

    id = Column(BigInteger, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)        # internal name (English)
    name_ar = Column(String(100))                                   # Arabic display name
    icon = Column(String(50))                                       # Lucide icon name
    color = Column(String(7))                                       # hex color #RRGGBB
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationship
    tracked_objects = relationship("TrackedObject", back_populates="category")
