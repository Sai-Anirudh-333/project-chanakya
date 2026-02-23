from ddgs import DDGS
from typing import List, Dict

class ScoutAgent:
    """
    The 'Scout' is responsible for gathering live intelligence from the open web.
    It uses privacy-focused search engines to avoid tracking.
    """
    
    def __init__(self):
        # Initialize search session once to reuse connections
        self.ddgs = DDGS()

    def search(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """
        Scans the web for the given query using DuckDuckGo.
        Returns cleaned, text-only results to save LLM context window.
        """
        print(f"🕵️ [SCOUT] Searching for: '{query}'...")
        
        try:
            # DuckDuckGo returns an iterator, convert to list
            results = list(self.ddgs.text(query, max_results=max_results))
        except Exception as e:
            print(f"❌ [SCOUT] Error during search: {e}")
            return []
        
        # Format the output for the "Commander" (LLM) to read easily
        clean_results = []
        for r in results:
            clean_results.append({
                "title": r.get("title", ""),
                "link": r.get("href", ""),
                "snippet": r.get("body", "")  # DDGS already strips most HTML
            })
            
        print(f"✅ [SCOUT] Found {len(clean_results)} intel reports.")
        return clean_results
