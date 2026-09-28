import json

from state import ResearchState
from services import llm
from models import ResearchAnalysis


def analyse_research(state: ResearchState):

    evidence = json.dumps(
        state["search_results"],
        indent=2
    )

    response = llm.invoke(
        f"""
        Analyse this business idea:

        {state['idea']}

        Research question:
        {state['research_question']}

        Evidence:
        {evidence}

        Return ONLY valid JSON with exactly these fields:

        demand_score
        competition_score
        profitability_score
        confidence_score
        customer_segments
        top_themes
        evidence_for
        evidence_against
        risks
        next_test

        All scores must be integers from 0 to 100.

        Do not invent sales figures, market sizes,
        search volumes, or conversion rates.
        Base everything only on the supplied evidence.
        """
    )

    raw = response.content.strip()

    raw = raw.removeprefix("```json")
    raw = raw.removesuffix("```")
    raw = raw.strip()

    parsed = json.loads(raw)

    validated = ResearchAnalysis(**parsed)

    return validated.model_dump()