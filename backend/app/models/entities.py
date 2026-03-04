from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

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

class BriefingEntities(Base):
    __tablename__ = "briefing_entities"
    id = Column(Integer, primary_key=True, index=True)
    briefing_id = Column(Integer, ForeignKey("briefings.id"))
    entity_id = Column(Integer, ForeignKey("entities.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
