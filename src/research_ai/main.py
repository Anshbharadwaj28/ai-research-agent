from research_ai.research.query_planner import Query_planner
from research_ai.research.web_search import WebResearcher
from research_ai.research.academic_search import AcademicResearcher
from research_ai.research.deduplication import SourceDeduplicator


def run_research(topic: str):

    if not topic or not topic.strip():
        raise ValueError("Research topic cannot be empty.")

    print("\n" + "=" * 70)
    print("RESEARCHPILOT - AI RESEARCH AGENT")
    print("=" * 70)

    print(f"\nResearch Topic: {topic}")


    print("\n[1/4] Generating research queries...")

    planner = Query_planner()
    queries = planner.generate_queries(topic)

    print("\nRaw planner output:")
    print(repr(queries))

    if isinstance(queries, str):
        queries = queries.splitlines()

    if not isinstance(queries, list):
        raise TypeError(
            "Query planner must return a list of strings."
        )

    valid_queries = []

    for query in queries:
        if isinstance(query, str) and query.strip():
            cleaned_query = query.strip()
            cleaned_query = cleaned_query.lstrip("0123456789.-) ").strip()

            if cleaned_query:
                valid_queries.append(cleaned_query)

    queries = list(dict.fromkeys(valid_queries))

    if not queries:
        raise ValueError(
            "Query planner returned no valid queries. "
            "Check query_planner.py."
        )

    print(f"\nGenerated {len(queries)} valid queries:")

    for index, query in enumerate(queries, start=1):
        print(f"{index}. {query}")


    print("\n[2/4] Searching web and academic sources...")

    web_researcher = WebResearcher()
    academic_researcher = AcademicResearcher(max_results=5)

    all_web_results = []
    all_academic_results = []

    for index, query in enumerate(queries, start=1):

        print(f"\nQuery {index}/{len(queries)}: {query}")

        try:
            web_results = web_researcher.search(query)

            if isinstance(web_results, dict):
                results = web_results.get("results", [])
            elif isinstance(web_results, list):
                results = web_results
            else:
                results = []

            all_web_results.extend(results)

            print(f"  Web results: {len(results)}")

        except Exception as error:
            print(f"  Web search failed: {error}")
        try:
            academic_results = academic_researcher.search(query)

            all_academic_results.extend(academic_results)

            print(f"  Academic results: {len(academic_results)}")

        except Exception as error:
            print(f"  Academic search failed: {error}")

    print("\nCollection summary:")
    print(f"Total web results: {len(all_web_results)}")
    print(f"Total academic papers: {len(all_academic_results)}")

    if not all_web_results and not all_academic_results:
        raise RuntimeError(
            "No research sources were retrieved. "
            "Check your API keys and search integrations."
        )

    print("\n[3/4] Removing duplicate sources...")

    deduplicator = SourceDeduplicator()

    unique_sources = deduplicator.deduplicate(
        all_web_results,
        all_academic_results
    )

    print(f"Unique sources: {len(unique_sources)}")


    print("\n[4/4] Research collection completed!")

    for index, source in enumerate(unique_sources, start=1):

        print("\n" + "=" * 70)
        print(f"SOURCE {index}")
        print("=" * 70)

        print("Title:", source.get("title", "Unknown"))
        print("Source types:", source.get("source_types", []))
        print("URL:", source.get("url", "Not available"))

        content = source.get("content", "")

        print("\nContent:")
        print(content[:500] if content else "No content available.")

    print("\n" + "=" * 70)
    print("RESEARCH PIPELINE FINISHED")
    print(f"Total unique sources: {len(unique_sources)}")
    print("=" * 70)

    return unique_sources


if __name__ == "__main__":

    topic = input("\nEnter your research topic: ").strip()

    if not topic:
        print("Please enter a valid research topic.")
    else:
        try:
            run_research(topic)

        except Exception as error:
            print(f"\nResearch pipeline failed: {error}")
