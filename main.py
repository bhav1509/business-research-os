import json
import os

from graph import graph
from database import (
    create_database,
    save_idea,
    save_research_run,
    save_search_query,
    save_search_result,
)


USE_CACHED_RESULT = True


if __name__ == "__main__":

    # --------------------------------
    # 1. Load or generate research
    # --------------------------------

    if USE_CACHED_RESULT and os.path.exists("result.json"):

        with open("result.json", "r") as f:
            result = json.load(f)

        print("📦 Using cached research")

    else:

        result = graph.invoke({
            "idea": "Printable Coloring Bookmarks"
        })

        with open("result.json", "w") as f:
            json.dump(result, f, indent=2)

        print("🌐 Fresh research completed and cached")


    # --------------------------------
    # 2. Save research to SQLite
    # --------------------------------

    create_database()

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

    print("✅ Research saved to SQLite")


    # --------------------------------
    # 3. Display result
    # --------------------------------

    print("\nBusiness idea:")
    print(result["idea"])

    print("\nFirst research question:")
    print(result["research_question"])

    print("\nSearch queries:")
    print(result["search_queries"])