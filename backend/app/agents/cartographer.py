from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
import json

class CartographerAgent:
    def __init__(self):
        self.llm = ChatGroq(
            model_name="llama-3.1-8b-instant"
        )
    
    def extract_locations(self,text:str):
        """
        Uses an LLM to extract the locations from the text.
        why llm for such a simple task?
        Because the text is unstructured and can be in any format.
        and also if user ask What is the threat level in Turkey and Paris
        We need a way to pull out the words Turkey and Paris and ignore everything else.
        Turkey is a country and Paris is a city. So we need to extract both.
        Ambiguity: Is "Turkey" a bird or a country? An LLM knows from the context of the sentence.
        Nicknames: If I say "Trouble in the Big Apple," an LLM knows to return New York.
        Typos/Formatting: LLMs are extremely forgiving. If you misspell "Afghanistan," a list-lookup would fail, but Llama will still probably figure it out.
        Simplicity: Instead of downloading a massive database of 100,000 cities, we just ask the LLM (which we are already paying for/using) to do the "hard work" of reading for us.
        """
        print(f"🗺️ [CARTOGRAPHER] Scanning for locations in: '{text[:50]}...'")

        system_prompt = """
            You are a geospatial intelligence extractor. 
            Identify all cities, regions, or countries mentioned in the text. 
            Return the result as a raw JSON list of strings. 
            Example: ["Paris", "London"] 
            If no locations are found, return []. 
            IMPORTANT: Return ONLY the JSON list. No conversation.
        """

        messages = [
            SystemMessage(
                content = system_prompt
            ),
            HumanMessage(
                content = text
            )
        ]

        try:
            response = self.llm.invoke(messages)
            locations = json.loads(response.content.strip())
            return locations
        except Exception as e:
            print(f"❌ [CARTOGRAPHER] Error extracting locations: {e}")
            return []
