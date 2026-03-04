from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from .base import Base

class ScoutTopic(Base):
    __tablename__ = "scout_topics"
    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
