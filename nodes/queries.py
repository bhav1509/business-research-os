from state import ResearchState
from services import llm


def create_search_queries(state: ResearchState):

    response = llm.invoke(
        f"""
        We are researching this business idea:

        {state['idea']}

        Research question:

        {state['research_question']}

        Create 5 specific web search queries
        that would help answer this question.

        Return each query on a new line.
        """
    )

    queries_text = response.content

    queries = [
        query.strip()
        for query in queries_text.split("\n")
        if query.strip()
    ]

    return {
        "search_queries": queries
    }