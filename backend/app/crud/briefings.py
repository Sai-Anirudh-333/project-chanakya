from sqlalchemy.orm import Session
from typing import List, Any
from app.models.briefings import Briefing
from app.crud.locations import save_locations
from app.crud.entities import save_entities

def save_briefing(db: Session, topic: str, content: str, locations: List[Any], scout_data: str = None, scholar_data: str = None, entities: dict = None):
    briefing = Briefing(
        topic=topic, 
        content=content,
        scout_data=scout_data,
        scholar_data=scholar_data
    )
    briefing.locations = save_locations(db, locations)
    if entities:
        briefing.entities = save_entities(db, entities)
    
    # This updates the object with its new ID from PostgreSQL
    db.add(briefing)
    db.commit()
    db.refresh(briefing)
    return briefing

def get_recent_briefings(db: Session, limit: int = 10):
    # We use .order_by(Briefing.created_at.desc()) to get the newest ones first
    return db.query(Briefing).order_by(Briefing.created_at.desc()).limit(limit).all()
