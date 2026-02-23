from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List
from contextlib import asynccontextmanager
from langchain_core.messages import HumanMessage, AIMessage
from app.databases.db_config import engine, SessionLocal
from app.databases import models
from app.databases.crud import CRUD
from app.databases.db_config import SessionLocal
from sqlalchemy import func
from app.databases.models import Entity, BriefingEntities

# CRITICAL: Load config from project root before importing agents
load_dotenv("../.env")

from app.graph import app as chanakya_brain
from app.scheduler import autopilot
from app.agents.strategist import StrategistAgent
from app.agents.chat_summarizer import ChatSummarizer


@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs right as the server boots up
    autopilot.start()
    yield # The server runs and handles requests
    # This runs right as the server is shutting down
    autopilot.shutdown()


app = FastAPI(
    title="Project Chanakya",
    description="Operational Backend for OSINT Defense Dashboard",
    version="1.0.0",
    lifespan=lifespan
)

strategist = StrategistAgent()
chat_summarizer = ChatSummarizer()
chat_session = {}
models.Base.metadata.create_all(bind=engine)

# Enable CORS (Cross-Origin Resource Sharing)
# This allows our Frontend to talk to this Backend.
# By disabling credentials, we are allowed to use the wildcard "*" 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """
    Root endpoint.
    Using 'async' allows the server to handle thousands of concurrent connections
    (like a waiter taking multiple orders) without blocking the thread.
    """
    return {"system_status": "ONLINE", "clearance_level": "UNCLASSIFIED"}

class MessageItem(BaseModel):
    """Strongly-typed Pydantic schema for a single chat message.
    This ensures the API returns a clean 422 error if 'role' or 'text' is missing.
    """
    role: str
    text: str

class ChatRequest(BaseModel):
    query:str
    session_id:str="default"

class ForecastRequest(BaseModel):
    context: str

@app.post("/api/chat")
async def chat(request: ChatRequest):
    # Convert frontend generic messages {"role": "...", "text": "..."} 
    # into LangChain specific message objects
    history = chat_session.get(request.session_id,[])
    history.append(
        {"role": "user", "text": request.query}
    )
    if(len(history)>6):
        summary = chat_summarizer.summarize(history)
        history = history[-6:]
        history.insert(0, {"role": "chanakya", "text": summary["summary"]})
    langchain_messages = []
    for msg in history:
        if msg["role"] == "user":
            langchain_messages.append(HumanMessage(content=msg["text"]))
        elif msg["role"] == "chanakya":
            langchain_messages.append(AIMessage(content=msg["text"]))
            
    msgDic = {
        "messages": langchain_messages
    }
    response = chanakya_brain.invoke(msgDic)
    history.append(
        {"role": "chanakya", "text": response["messages"][-1].content}
    )
    chat_session[request.session_id] = history
    response["messages"] = history

    return response

@app.get("/api/reports")
async def get_reports(limit: int = 10):
    """
    Fetches the most recent intelligence briefings from the PostgreSQL database.
    """
    with SessionLocal() as db:
        crud = CRUD(db)
        briefings = crud.get_recent_briefings(limit=limit)
        
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

@app.get("/api/entities")
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

@app.post('/api/forecast')
async def forecast(request:ForecastRequest):
    return strategist.analyze(request.context)

if __name__ == "__main__":
    import uvicorn
    # Learned: 0.0.0.0 exposes the server to the network (Docker/External),
    # whereas 127.0.0.1 would lock it to this machine only.
    uvicorn.run(app, host="0.0.0.0", port=7000)
