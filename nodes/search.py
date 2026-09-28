from state import ResearchState
from services import search


def search_web(state: ResearchState):

    all_results = []

    for query in state["search_queries"]:
        result = search.invoke({
            "query": query
        })

        all_results.append(result)

    return {
        "search_results": all_results
    }