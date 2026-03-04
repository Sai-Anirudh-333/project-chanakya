from fastapi import APIRouter
from app.databases.db_config import SessionLocal
from app.crud.briefings import get_recent_briefings

router = APIRouter()

@router.get("")
async def get_reports(limit: int = 10):
    """
    Fetches the most recent intelligence briefings from the PostgreSQL database.
    """
    with SessionLocal() as db:
        briefings = get_recent_briefings(db, limit=limit)
        
        # We must manually format the SQLAlchemy objects into JSON-serializable dictionaries
        results = []
        for b in briefings:
            results.append({
                "id": b.id,
                "topic": b.topic,
                "content": b.content,
                "created_at": b.created_at.isoformat(),
                "scout_data": b.scout_data,
                "scholar_data": b.scholar_data,
                # Extract just the string names from the Location objects
                "locations": [loc.name for loc in b.locations] 
            })
            
        return {"reports": results}
