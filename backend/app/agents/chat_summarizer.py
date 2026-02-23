from langchain_groq import ChatGroq
from pydantic import BaseModel, Field, ValidationError
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

class MessageItem(BaseModel):
    """Strongly-typed Pydantic schema for a single chat message.
    This ensures the API returns a clean 422 error if 'role' or 'text' is missing.
    """
    role: str
    text: str

class SummarizerOutput(BaseModel):
    summary:str = Field(default_factory=str, description="Summary of the context")

class ChatSummarizer:
    def __init__(self):
        self.llm = ChatGroq(model_name="llama-3.1-8b-instant")

    def summarize(self,history:MessageItem):
        print(f"🧠 [CHAT SUMMARIZER] Summarizing context for chat...")
        system_prompt = """
        You are a Senior Strategic Analyst for the Indian Armed Forces.
        You will be given the converstation history of a user with Chanakya.
        Your job is to summarize the conversation history and produce a "Strategic Summary".
        
        Return your analysis in the following JSON format:
        {
            "summary": "..."
        }
        
        Be concise, analytical, and avoid emotional language.
        """
        messages = [SystemMessage(content=system_prompt)]
        for msg in history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["text"]))
            elif msg["role"] == "chanakya":
                messages.append(AIMessage(content=msg["text"]))
        
        try:
            raw_response = self.llm.with_structured_output(method="json_mode").invoke(messages)
            validated = SummarizerOutput(**raw_response)
            return validated.model_dump()
        except ValidationError as e:
            print(f"❌ [CHAT SUMMARIZER] Pydantic Validation Error: {e}")
            return {"summary": ""}
        except Exception as e:
            print(f"❌ [CHAT SUMMARIZER] Generation Error: {e}")
            return {"summary": ""}