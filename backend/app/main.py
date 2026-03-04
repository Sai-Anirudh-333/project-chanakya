from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from app.databases.db_config import engine
from app.models.base import Base

# CRITICAL: Load config from project root before importing agents
load_dotenv("../.env")

from app.scheduler import autopilot
from app.api.routes import api_router


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

Base.metadata.create_all(bind=engine)

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

app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    # Learned: 0.0.0.0 exposes the server to the network (Docker/External),
    # whereas 127.0.0.1 would lock it to this machine only.
    uvicorn.run(app, host="0.0.0.0", port=8000)
