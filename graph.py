from langgraph.graph import StateGraph, START, END

from state import ResearchState
from nodes.question import create_research_question
from nodes.queries import create_search_queries
from nodes.search import search_web
from nodes.analyse import analyse_research


builder = StateGraph(ResearchState)

builder.add_node(
    "create_research_question",
    create_research_question
)

builder.add_node(
    "create_search_queries",
    create_search_queries
)

builder.add_node(
    "search_web",
    search_web
)

builder.add_node(
    "analyse_research",
    analyse_research
)

builder.add_edge(
    START,
    "create_research_question"
)

builder.add_edge(
    "create_research_question",
    "create_search_queries"
)

builder.add_edge(
    "create_search_queries",
    "search_web"
)

builder.add_edge(
    "search_web",
    "analyse_research"
)

builder.add_edge(
    "analyse_research",
    END
)

graph = builder.compile()