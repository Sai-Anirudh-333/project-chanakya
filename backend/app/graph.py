from typing import TypedDict, Annotated, Sequence, List
import operator
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
import json
from app.databases.crud import CRUD
from app.databases.db_config import SessionLocal

# Import our Agents
from app.agents.scholar import ScholarAgent
from app.agents.scout import ScoutAgent
from app.agents.cartographer import CartographerAgent
from app.agents.entity_extractor import EntityExtractorAgent


# =========================================================
# Pydantic Output Schema for the Synthesizer
# This is the contract between us and the LLM.
# If the LLM returns anything else, we get a clean error
# instead of silent data corruption.
# =========================================================
class BriefingOutput(BaseModel):
    topic: str = Field(description="A short, 3-5 word title for this intelligence report.")
    content: str = Field(description="The full, detailed intelligence briefing.")

# 1. Define the "State" of the brain
# QUESTION: Why do we need a TypedDict here? 
# Think about how data flows between different agents.
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    scholar_data: str
    scout_data: str
    locations: Annotated[List[str], operator.add]
    is_allowed: str
    final_topic: str       # To pass from synthesizer to DB node
    final_content: str     # To pass from synthesizer to DB and Entity node
    entities: dict         # Contains people, organizations, countries

# 2. Initialize Tools & LLM
llm = ChatGroq(model_name="llama-3.1-8b-instant")
scholar = ScholarAgent()
scout = ScoutAgent()
cartographer = CartographerAgent()
entity_extractor = EntityExtractorAgent()

# 3. Define the Nodes (The Workers)
def guard_node(state: AgentState):
    """
    Acts as a firewall. Rejects non-defense/geopolitical queries.
    """
    system_prompt = (
        "You are a strict military AI guardrail. "
        "Your job is to determine if the user's conversation is related to defense, geopolitics, strategy, intelligence, or global events. "
        "If the conversation history is related to these themes, reply with 'ALLOWED'. "
        "If it is a general question (e.g. recipes, coding, casual chat, poems, standard facts not related to defense), reply with 'REJECTED'. "
        "Respond ONLY with 'ALLOWED' or 'REJECTED'."
    )
    
    # FIX: Pass the entire conversation history to the Guard so it understands context like "is it complete?"
    messages = [SystemMessage(content=system_prompt)] + list(state['messages'])
    
    response = llm.invoke(messages)
    decision = response.content.strip().upper()
    
    if "REJECTED" in decision:
        return {
            "is_allowed": "no",
            "messages": [AIMessage(content="CLASSIFIED: Query outside operational parameters. Request denied.")]
        }
        
    return {"is_allowed": "yes"}

def router_node(state: AgentState):
    """
    The 'Commander'. Uses an LLM to decide the next step.
    """
    # Prompt the Router to classify the intent based on the whole conversation
    system_prompt = (
        "You are a sophisticated routing system for a Defense AI. "
        "Classify the user's latest query into one of three categories based on the conversation history:\n"
        "1. 'scout' -> Real-time info, news, current events.\n"
        "2. 'scholar' -> Historical treaties, defense doctrines, official reports.\n"
        "3. 'both' -> Requires connecting past documents with live news.\n"
        "Return ONLY the category name (scout, scholar, or both)."
    )
    
    # FIX: Pass the entire conversation history to the Router
    messages = [SystemMessage(content=system_prompt)] + list(state['messages'])
    
    response = llm.invoke(messages)
    decision = response.content.strip().lower()
    
    # Fallback in case LLM chats instead of outputting a label
    if "scout" in decision: return {"next": "scout"}
    if "scholar" in decision: return {"next": "scholar"}
    return {"next": "both"}

def scout_node(state: AgentState):
    """
    Executes a web search.
    """
    query = state['messages'][-1].content
    results = scout.search(query)
    
    # Return valid JSON string instead of Python string representation
    return {"scout_data": json.dumps(results)}

def scholar_node(state: AgentState):
    """
    Queries the vector database.
    """
    query = state['messages'][-1].content
    results = scholar.query(query)
    return {"scholar_data": str(results)}

def cartographer_node(state: AgentState):
    """
    Extracts geographic locations from the query.
    """
    
    query = state['messages'][-1].content
    locations = cartographer.extract_locations(query)
    return {"locations": locations}

def synthesizer_node(state: AgentState):
    """
    Combines intel from Scout and Scholar into a final briefing.
    """
    places_found = state.get("locations", [])
    
    # Combine the system prompt, the conversational history, AND the injected intel data
    messages = [
        SystemMessage(
            content="""You are Chanakya, a Defense Intelligence AI. 
            Summarize the following intel into a concise briefing. Mentions specific locations identified by the Cartographer if relevant.
            CRITICAL: You must respond in valid JSON format with exactly two keys:
            1. "topic": A short, 3-5 word title for this specific intelligence report.
            2. "content": Your full, detailed briefing.
            """
        )
    ] + state['messages'] + [
        HumanMessage(content=f"Locations Identified: {places_found}\nScout Intel: {state.get('scout_data', 'None')}\nScholar Intel: {state.get('scholar_data', 'None')}")
    ]
    
    # WHY json_mode + manual Pydantic instead of .with_structured_output(BriefingOutput)?
    # When you pass a Pydantic class to with_structured_output(), LangChain switches to 
    # "function calling" mode on Groq. The small llama-3.1-8b-instant model cannot handle 
    # function calling reliably — it formats the response as <function=BriefingOutput> which 
    # is invalid JSON and causes a 400 error from Groq.
    # Solution: Use json_mode for the raw LLM call, then manually validate through Pydantic.
    raw_response = llm.with_structured_output(method="json_mode").invoke(messages)
    
    # This validates the dict against our schema. If fields are missing or wrong type, 
    # Pydantic raises a clear ValidationError immediately — no silent garbage in the DB!
    response = BriefingOutput(**raw_response)
    
    final_topic = response.topic
    final_content = response.content

    # We return the content to the chat, but we also save topic and content into the State
    # so the downstream Entity Extractor and DB nodes can use them.
    return {
        "final_topic": final_topic, 
        "final_content": final_content, 
        "messages": [AIMessage(content=final_content)]
    }

def entity_extractor_node(state: AgentState):
    """
    Extracts structured entities from the final synthesized briefing.
    """
    content = state.get("final_content", "")
    entities = entity_extractor.extract(content)
    return {"entities": entities}

def database_writer_node(state: AgentState):
    """
    Saves the completely constructed state to PostgreSQL.
    """
    places_found = state.get("locations", [])
    topic = state.get("final_topic", "General Briefing")
    content = state.get("final_content", "")
    scout_data = state.get('scout_data')
    scholar_data = state.get('scholar_data')
    entities = state.get('entities', {})

    with SessionLocal() as db:
        crud = CRUD(db)
        crud.save_briefing(
            topic=topic, 
            content=content, 
            locations=places_found,
            scout_data=scout_data,
            scholar_data=scholar_data,
            entities=entities
        )
    return {}

# 4. Build the Graph
workflow = StateGraph(AgentState)

workflow.add_node("guard", guard_node)
workflow.add_node("router", router_node)
workflow.add_node("scout", scout_node)
workflow.add_node("scholar", scholar_node)
workflow.add_node('cartographer', cartographer_node)
workflow.add_node("synthesizer", synthesizer_node)
workflow.add_node("entity_extractor", entity_extractor_node)
workflow.add_node("database_writer", database_writer_node)

workflow.set_entry_point("guard")

def check_guard(state: AgentState):
    if state.get("is_allowed") == "no":
        return "end"
    return "router"

workflow.add_conditional_edges(
    "guard",
    check_guard,
    {
        "end": END,
        "router": "router"
    }
)

workflow.add_edge("router", "scout")
workflow.add_edge("router", "scholar")
workflow.add_edge("router", "cartographer")
workflow.add_edge("scout", "synthesizer")
workflow.add_edge("scholar", "synthesizer")
workflow.add_edge("cartographer", "synthesizer")

# The final pipeline flow: Synthesize -> Extract Entities -> Save to DB -> End
workflow.add_edge("synthesizer", "entity_extractor")
workflow.add_edge("entity_extractor", "database_writer")
workflow.add_edge("database_writer", END)

app = workflow.compile()
