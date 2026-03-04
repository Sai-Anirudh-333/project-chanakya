from fastapi import APIRouter

from app.api.endpoints import chat, reports, entities, forecast, topics, documents

api_router = APIRouter()

# Include all the individual routers.
# We map them to their specific prefixes here, so inside the individual files we just use "/" or "/{id}".
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(entities.router, prefix="/entities", tags=["entities"])
api_router.include_router(forecast.router, prefix="/forecast", tags=["forecast"])
api_router.include_router(topics.router, prefix="/topics", tags=["topics"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
