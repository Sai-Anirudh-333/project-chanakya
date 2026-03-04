from fastapi import APIRouter
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage
from app.graph import app as chanakya_brain
from app.agents.chat_summarizer import ChatSummarizer
from app.schemas.chat import ChatRequest
router = APIRouter()
chat_summarizer = ChatSummarizer()
chat_session = {} # In production this would be moved to Redis or Postgres

@router.post("")
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
