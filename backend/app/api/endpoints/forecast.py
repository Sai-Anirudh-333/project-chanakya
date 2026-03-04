from fastapi import APIRouter
from pydantic import BaseModel
from app.agents.strategist import StrategistAgent

router = APIRouter()
strategist = StrategistAgent()

class ForecastRequest(BaseModel):
    context: str

@router.post('')
async def forecast(request:ForecastRequest):
    return strategist.analyze(request.context)
