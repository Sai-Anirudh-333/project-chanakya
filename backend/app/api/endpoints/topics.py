from fastapi import APIRouter,Depends,HTTPException
from app.schemas.topics import TopicCreate,TopicResponse
from app.crud import topics
from sqlalchemy.orm import Session
from app.databases.db_config import get_db
from typing import List

router = APIRouter()

@router.post("",response_model=TopicResponse)
async def create_topic(topic:TopicCreate,db:Session = Depends(get_db)):
    return topics.create_topic(db,topic)

@router.get("",response_model=List[TopicResponse])
async def get_topics(db:Session = Depends(get_db)):
    return topics.get_topics(db)

@router.delete("/{id}")
async def delete_topic(id:int,db:Session = Depends(get_db)):
    success = topics.delete_topic(db,id)
    if not success:
        raise HTTPException(status_code=404, detail="Topic not found")
    return {"message": "Topic deleted successfully"}