from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .db_config import Base

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

class BriefingLocations(Base):
    __tablename__ = "briefing_locations"
    id = Column(Integer, primary_key=True, index=True)
    briefing_id = Column(Integer, ForeignKey("briefings.id"))
    location_id = Column(Integer, ForeignKey("locations.id"))
    # We keep the class so it creates the table with `created_at`, but we don't need to manually map to it.
    created_at = Column(DateTime, default=datetime.utcnow)

class Location(Base):
    __tablename__ = "locations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False,unique=True)
    
    # We point directly back to Briefing using the exact same bridge
    briefings = relationship("Briefing", secondary="briefing_locations", back_populates="locations")
    created_at = Column(DateTime, default=datetime.utcnow)

# ==========================================
# Phase 8: Entity Tracking Models
# ==========================================

class BriefingEntities(Base):
    __tablename__ = "briefing_entities"
    id = Column(Integer, primary_key=True, index=True)
    briefing_id = Column(Integer, ForeignKey("briefings.id"))
    entity_id = Column(Integer, ForeignKey("entities.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

class Entity(Base):
    """
    Stores structured extracted entities (People, Organizations, Countries, Events).
    The 'type' column allows us to filter the frontend timeline easily.
    """
    __tablename__ = "entities"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    type = Column(String(50), nullable=False) # e.g., 'Person', 'Organization', 'Country'
    
    briefings = relationship("Briefing", secondary="briefing_entities", back_populates="entities")
    created_at = Column(DateTime, default=datetime.utcnow)

    