from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Location(Base):
    __tablename__ = "locations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    
    # We point directly back to Briefing using the exact same bridge
    briefings = relationship("Briefing", secondary="briefing_locations", back_populates="locations")
    created_at = Column(DateTime, default=datetime.utcnow)

class BriefingLocations(Base):
    __tablename__ = "briefing_locations"
    id = Column(Integer, primary_key=True, index=True)
    briefing_id = Column(Integer, ForeignKey("briefings.id"))
    location_id = Column(Integer, ForeignKey("locations.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
