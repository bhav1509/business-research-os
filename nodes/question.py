from state import ResearchState
from services import llm

def create_research_question(state: ResearchState):

    response = llm.invoke(
        f"""
        I want to validate this business idea:

        {state['idea']}

        Give me ONE important market research question
        I should answer first.

        Return only the question.
        """
    )

    return {
        "research_question": response.content
    }