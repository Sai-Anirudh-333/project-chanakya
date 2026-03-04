from sqlalchemy.orm import Session
from app.models.topics import ScoutTopic
from app.schemas.topics import TopicCreate

def create_topic(db: Session, topic: TopicCreate):
    db_topic = ScoutTopic(topic=topic.topic)
    db.add(db_topic)
    db.commit()
    db.refresh(db_topic)
    return db_topic

def get_topics(db: Session, skip: int = 0, limit: int = 100):
    return db.query(ScoutTopic).offset(skip).limit(limit).all()

def delete_topic(db: Session, topic_id: int):
    topic = db.query(ScoutTopic).filter(ScoutTopic.id == topic_id).first()
    if topic:
        db.delete(topic)
        db.commit()
        return True
    return False
