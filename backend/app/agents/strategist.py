from pydantic import ValidationError
from langchain_core.load.dump import default
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field, ValidationError
from langchain_core.messages import SystemMessage, HumanMessage

class ForecastOutput(BaseModel):
    optimistic:str = Field(default_factory=str, description="Optimistic take on the context")
    base_case:str = Field(default_factory=str,description="Realistic take on the context")
    pessimistic:str = Field(default_factory=str,description="Pessimistic take on the context")

class StrategistAgent:
    def __init__(self):
        self.llm = ChatGroq(model_name="llama-3.1-8b-instant")

    def analyze(self,context:str):

        print(f"🧠 [STRATEGIST] Analyzing context for strategic forecast...")

        system_prompt = """
        You are a Senior Strategic Analyst for the Indian Armed Forces.
        Your job is to read raw intelligence reports and produce a "Strategic Forecast".
        
        You must provide three distinct scenarios based on the input context:
        1. Optimistic: Best case scenario (e.g., diplomatic success, minimal conflict).
        2. Base Case: Most likely scenario (realistic projection).
        3. Pessimistic: Worst case scenario (maximum conflict, worst outcomes).
        
        Return your analysis in the following JSON format:
        {
            "optimistic": "...",
            "base_case": "...",
            "pessimistic": "..."
        }
        
        Be concise, analytical, and avoid emotional language.
        """

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=context)
        ]

        try:
            raw_response = self.llm.with_structured_output(method="json_mode").invoke(messages)

            validated = ForecastOutput(**raw_response)

            return validated.model_dump()
        except ValidationError as e:
            print(f"❌ [STRATEGIST] Pydantic Validation Error: {e}")
            return {"optimistic": "", "base_case": "", "pessimistic": ""}
        except Exception as e:
            print(f"❌ [STRATEGIST] Generation Error: {e}")
            return {"optimistic": "", "base_case": "", "pessimistic": ""}


