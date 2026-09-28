import json

from database import (
    get_ideas,
    save_research_run,
    save_analysis
)

from nodes.analyse import analyse_research


with open("result.json", "r") as f:
    cached_result = json.load(f)


import os

ANALYSIS_CACHE = "analysis.json"

if os.path.exists(ANALYSIS_CACHE):

    with open(ANALYSIS_CACHE, "r") as f:
        analysis = json.load(f)

    print("📦 Using cached analysis")

else:

    analysis = analyse_research(cached_result)

    with open(ANALYSIS_CACHE, "w") as f:
        json.dump(analysis, f, indent=2)

    print("🤖 Fresh analysis completed and cached")

print(json.dumps(analysis, indent=2))

ideas = get_ideas()

idea_id = ideas[0][0]

research_run_id = save_research_run(
    idea_id,
    cached_result["research_question"]
)

save_analysis(
    research_run_id,
    analysis
)

print("✅ Analysis saved to SQLite")