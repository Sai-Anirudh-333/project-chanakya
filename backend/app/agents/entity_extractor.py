from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field, ValidationError
from typing import List
import json

class ExtractedEntities(BaseModel):
    people: List[str] = Field(default_factory=list, description="List of individual people mentioned.")
    organizations: List[str] = Field(default_factory=list, description="List of organizations, companies, militaries, or groups.")
    countries: List[str] = Field(default_factory=list, description="List of sovereign countries or nations mentioned.")

class EntityExtractorAgent:
    def __init__(self):
        self.llm = ChatGroq(model_name="llama-3.1-8b-instant")
        
    def extract(self, text: str) -> dict:
        print(f"🧠 [ANALYST] Extracting structured entities (People, Orgs, Countries)...")
        
        system_prompt = """
        You are an elite intelligence analyst. Extract all critical entities from the provided briefing text.
        
        You must structure your response as EXACTLY this JSON format:
        {
            "people": ["Name 1", "Name 2"],
            "organizations": ["Org 1", "Org 2"],
            "countries": ["Country 1", "Country 2"]
        }
        
        Return ONLY valid JSON. Do not include any conversation, markdown tags, or explanations.
        If no entities exist for a category, use an empty list [].
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=text)
        ]
        
        try:
            # We use json_mode + manual Pydantic validation (Phase 7 Learning)
            # This protects us from the Groq 400 function calling error on small models.
            raw_response = self.llm.with_structured_output(method="json_mode").invoke(messages)
            
            # Validate output structure strictly
            validated = ExtractedEntities(**raw_response)
            
            # Return as a simple dictionary payload
            return validated.model_dump()
            
        except ValidationError as e:
            print(f"❌ [ANALYST] Pydantic Validation Error: LLM returned malformed schema. {e}")
            return {"people": [], "organizations": [], "countries": []}
        except Exception as e:
            print(f"❌ [ANALYST] Generation Error: {e}")
            return {"people": [], "organizations": [], "countries": []}
