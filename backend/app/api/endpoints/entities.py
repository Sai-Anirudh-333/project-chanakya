from fastapi import APIRouter
from sqlalchemy import func
from app.databases.db_config import SessionLocal
from app.models.entities import Entity, BriefingEntities

router = APIRouter()

@router.get("")
async def get_entities():
    """
    Fetches extracted entities across all reports, grouped by type.
    """

    with SessionLocal() as db:
        # Get count of briefings per entity using a SQL JOIN
        entities = (
            db.query(
                Entity.id, 
                Entity.name, 
                Entity.type,
                func.count(BriefingEntities.briefing_id).label('mention_count')
            )
            .join(BriefingEntities, Entity.id == BriefingEntities.entity_id)
            .group_by(Entity.id)
            .order_by(func.count(BriefingEntities.briefing_id).desc())
            .all()
        )
        
        results = {
            "people": [],
            "organizations": [],
            "countries": []
        }
        
        for e in entities:
            item = {"id": e.id, "name": e.name, "mentions": e.mention_count}
            if e.type == "Person": results["people"].append(item)
            elif e.type == "Organization": results["organizations"].append(item)
            elif e.type == "Country": results["countries"].append(item)
            
        return results
