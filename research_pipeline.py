from graph import graph

from database import (
    create_database,
    save_idea,
    save_research_run,
    save_search_query,
    save_search_result,
    save_analysis,
)


def run_research_pipeline(idea_name: str):
    create_database()

    result = graph.invoke({
        "idea": idea_name
    })

    idea_id = save_idea(
        result["idea"]
    )

    research_run_id = save_research_run(
        idea_id,
        result["research_question"]
    )

    for query_data in result["search_results"]:
        query_id = save_search_query(
            research_run_id,
            query_data["query"]
        )

        for item in query_data["results"]:
            save_search_result(
                query_id,
                item.get("title", ""),
                item.get("url", ""),
                item.get("content", ""),
                item.get("score", 0)
            )

    analysis = {
        "demand_score": result["demand_score"],
        "competition_score": result["competition_score"],
        "profitability_score": result["profitability_score"],
        "confidence_score": result["confidence_score"],
        "customer_segments": result["customer_segments"],
        "top_themes": result["top_themes"],
        "evidence_for": result["evidence_for"],
        "evidence_against": result["evidence_against"],
        "risks": result["risks"],
        "next_test": result["next_test"],
    }

    save_analysis(
        research_run_id,
        analysis
    )

    return {
        "idea_id": idea_id,
        "research_run_id": research_run_id,
        "result": result,
    }