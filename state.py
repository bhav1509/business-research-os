from typing import TypedDict


class ResearchState(TypedDict):
    idea: str
    research_question: str
    search_queries: list[str]
    search_results: list

    demand_score: int
    competition_score: int
    profitability_score: int
    confidence_score: int

    customer_segments: list[str]
    top_themes: list[str]
    evidence_for: list[str]
    evidence_against: list[str]
    risks: list[str]
    next_test: str