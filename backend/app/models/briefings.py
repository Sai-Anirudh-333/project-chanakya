from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

# We must import the relationship models to avoid unmapped errors if they are queried through the briefing
from .locations import Location, BriefingLocations
from .entities import Entity, BriefingEntities

class Briefing(Base):
    __tablename__ = "briefings"
    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    scout_data = Column(Text, nullable=True)     # Added for Phase 7 Polish
    scholar_data = Column(Text, nullable=True)   # Added for Phase 7 Polish
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # We point directly to "Location" but tell SQLAlchemy to use the Association Table string as the bridge
    locations = relationship("Location", secondary="briefing_locations", back_populates="briefings")
    
    # Phase 8: Add many-to-many relationship to Entities
    entities = relationship("Entity", secondary="briefing_entities", back_populates="briefings")
