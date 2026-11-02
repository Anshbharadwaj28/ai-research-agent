from src.research_ai.research.web_search import WebResearcher
researcher = WebResearcher()

query = "Graph databases for AI agent memory"

results = researcher.search(query)

print("\nWEB SEARCH RESULTS\n")

print(results)