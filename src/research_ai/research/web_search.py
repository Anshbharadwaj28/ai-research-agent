import os
from langchain_tavily import TavilySearch
from dotenv import load_dotenv

load_dotenv()

class WebResearcher:

    def __init__(self):
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise ValueError("TAVILY_API_KEY not found")

        self.search_tool = TavilySearch(
            max_results = 5,
            topic = "general",
            search_depth = "advanced"
        )
    
    def search (self,query:str):
        results = self.search_tool.invoke({
            "query" : query
        })
        return results
