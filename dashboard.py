import json
import sqlite3

import plotly.graph_objects as go
import streamlit as st
from research_pipeline import run_research_pipeline
from database import rename_idea

DB_NAME = "business_research.db"


# --------------------------------------------------
# Page config
# --------------------------------------------------

st.set_page_config(
    page_title="Business Research Dashboard",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Business Research Dashboard")


# --------------------------------------------------
# Helpers
# --------------------------------------------------

def get_connection():
    return sqlite3.connect(DB_NAME)


def safe_json_loads(value):
    """Safely convert JSON text stored in SQLite back to Python."""
    if not value:
        return []

    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return []


def clamp_score(value):
    """Keep scores safely within 0-100."""
    try:
        return max(0, min(100, int(value)))
    except (TypeError, ValueError):
        return 0


# --------------------------------------------------
# Load ideas
# --------------------------------------------------

connection = get_connection()

ideas = connection.execute(
    """
    SELECT id, name, created_at
    FROM ideas
    ORDER BY created_at DESC
    """
).fetchall()

connection.close()


# --------------------------------------------------
# Sidebar
# --------------------------------------------------

st.sidebar.subheader("➕ New Project")

with st.sidebar.form("new_project_form"):

    new_idea = st.text_area(
        "Describe your business idea",
        placeholder="Example: Adult coloring books for Amazon KDP"
    )

    start_research = st.form_submit_button(
        "Start Research"
    )


if start_research:

    if not new_idea.strip():
        st.sidebar.warning(
            "Please enter a business idea."
        )

    else:

        try:
            with st.spinner(
                "Researching your idea..."
            ):
                run_research_pipeline(
                    new_idea.strip()
                )

            st.success(
                "Research complete."
            )

            st.rerun()

        except Exception as error:
            st.error(
                f"Research failed: {error}"
            )

st.sidebar.title("Business Research")

if not ideas:
    st.sidebar.info("No ideas found.")
    st.stop()

idea_lookup = {
    name: idea_id
    for idea_id, name, created_at in ideas
}

selected_idea = st.sidebar.selectbox(
    "Choose an idea",
    list(idea_lookup.keys()),
)

selected_idea_id = idea_lookup[selected_idea]

st.sidebar.divider()
st.sidebar.caption(f"{len(ideas)} idea(s) stored")


# --------------------------------------------------
# Selected idea
# --------------------------------------------------

st.header(selected_idea)

with st.expander("✏️ Rename Project"):

    new_name = st.text_input(
        "Project name",
        value=selected_idea
    )

    if st.button("Save Name"):

        if new_name.strip():

            rename_idea(
                selected_idea_id,
                new_name.strip()
            )

            st.success("Project renamed.")

            st.rerun()
            
connection = get_connection()

idea_details = connection.execute(
    """
    SELECT created_at
    FROM ideas
    WHERE id = ?
    """,
    (selected_idea_id,),
).fetchone()

connection.close()

if idea_details:
    st.caption(f"Idea created: {idea_details[0]}")


# --------------------------------------------------
# Load research runs
# --------------------------------------------------

connection = get_connection()

runs = connection.execute(
    """
    SELECT
        id,
        research_question,
        created_at
    FROM research_runs
    WHERE idea_id = ?
    ORDER BY created_at DESC
    """,
    (selected_idea_id,),
).fetchall()

connection.close()

if not runs:
    st.info("No research runs available for this idea.")
    st.stop()


# --------------------------------------------------
# Choose research run
# --------------------------------------------------

run_lookup = {
    f"{created_at} — {question[:70]}": run_id
    for run_id, question, created_at in runs
}

selected_run_label = st.selectbox(
    "Research run",
    list(run_lookup.keys()),
)

selected_run_id = run_lookup[selected_run_label]

selected_run = next(
    run
    for run in runs
    if run[0] == selected_run_id
)

run_id, question, run_created_at = selected_run

st.write(f"**Research question:** {question}")
st.caption(f"Run created: {run_created_at}")

st.divider()


# ==================================================
# ANALYSIS
# ==================================================

connection = get_connection()

analysis_row = connection.execute(
    """
    SELECT
        demand_score,
        competition_score,
        profitability_score,
        confidence_score,
        customer_segments,
        top_themes,
        evidence_for,
        evidence_against,
        risks,
        next_test
    FROM analyses
    WHERE research_run_id = ?
    ORDER BY created_at DESC
    LIMIT 1
    """,
    (run_id,),
).fetchone()

connection.close()

if analysis_row:

    (
        demand_score,
        competition_score,
        profitability_score,
        confidence_score,
        customer_segments,
        top_themes,
        evidence_for,
        evidence_against,
        risks,
        next_test,
    ) = analysis_row

    demand_score = clamp_score(demand_score)
    competition_score = clamp_score(competition_score)
    profitability_score = clamp_score(profitability_score)
    confidence_score = clamp_score(confidence_score)

    # Higher competition is bad, so convert it for the opportunity visuals.
    market_openness_score = 100 - competition_score

    overall_score = round(
        demand_score * 0.35
        + profitability_score * 0.30
        + market_openness_score * 0.20
        + confidence_score * 0.15
    )

    # ----------------------------------------------
    # KPI cards
    # ----------------------------------------------

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Overall", f"{overall_score}/100")
    col2.metric("Demand", f"{demand_score}/100")
    col3.metric("Competition", f"{competition_score}/100")
    col4.metric("Profitability", f"{profitability_score}/100")
    col5.metric("Confidence", f"{confidence_score}/100")

    st.caption(
        "Competition is shown as the raw competition score above. "
        "In the opportunity chart, it is converted to Market Openness = 100 − Competition."
    )

    # ----------------------------------------------
    # Verdict
    # ----------------------------------------------

    if overall_score >= 75:
        st.success("🟢 Strong opportunity — worth moving to a real market test.")
    elif overall_score >= 55:
        st.warning("🟡 Worth validating — promising signals, but key assumptions are still unproven.")
    else:
        st.error("🔴 Weak opportunity — gather stronger evidence before investing further.")

    # ----------------------------------------------
    # Radar chart + score bars
    # ----------------------------------------------

    chart_col, health_col = st.columns([1.15, 1])

    with chart_col:
        st.subheader("Opportunity Profile")

        radar_labels = [
            "Demand",
            "Market Openness",
            "Profitability",
            "Confidence",
        ]

        radar_values = [
            demand_score,
            market_openness_score,
            profitability_score,
            confidence_score,
        ]

        # Close the radar polygon by repeating the first value.
        radar_labels_closed = radar_labels + [radar_labels[0]]
        radar_values_closed = radar_values + [radar_values[0]]

        radar = go.Figure()

        radar.add_trace(
            go.Scatterpolar(
                r=radar_values_closed,
                theta=radar_labels_closed,
                fill="toself",
                name="Opportunity profile",
                hovertemplate="%{theta}: %{r}/100<extra></extra>",
            )
        )

        radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                )
            ),
            showlegend=False,
            margin=dict(l=35, r=35, t=25, b=25),
            height=390,
        )

        st.plotly_chart(
            radar,
            use_container_width=True,
            config={"displayModeBar": False},
        )

    with health_col:
        st.subheader("Business Health")

        st.write("Demand")
        st.progress(demand_score / 100)
        st.caption(f"{demand_score}/100")

        st.write("Market openness")
        st.progress(market_openness_score / 100)
        st.caption(
            f"{market_openness_score}/100 "
            f"(competition is {competition_score}/100)"
        )

        st.write("Profitability")
        st.progress(profitability_score / 100)
        st.caption(f"{profitability_score}/100")

        st.write("Confidence")
        st.progress(confidence_score / 100)
        st.caption(f"{confidence_score}/100")

    st.divider()

    # ----------------------------------------------
    # Customer segments
    # ----------------------------------------------

    segments = safe_json_loads(customer_segments)

    st.subheader("Customer Segments")

    if segments:
        segment_columns = st.columns(min(len(segments), 4))

        for index, segment in enumerate(segments):
            segment_columns[index % len(segment_columns)].info(segment)
    else:
        st.caption("No customer segments available.")

    # ----------------------------------------------
    # Top themes
    # ----------------------------------------------

    themes = safe_json_loads(top_themes)

    st.subheader("Top Themes")

    if themes:
        theme_columns = st.columns(2)

        for index, theme in enumerate(themes):
            theme_columns[index % 2].write(f"• {theme}")
    else:
        st.caption("No themes available.")

    # ----------------------------------------------
    # Recommended experiments
    # ----------------------------------------------

    next_tests = safe_json_loads(next_test)

    st.subheader("Recommended Next Tests")

    if next_tests:
        for index, test in enumerate(next_tests, start=1):
            st.info(f"{index}. {test}")
    else:
        st.caption("No experiments available.")

    # ----------------------------------------------
    # Risks
    # ----------------------------------------------

    risk_items = safe_json_loads(risks)

    with st.expander("⚠️ Risks"):
        if risk_items:
            for risk in risk_items:
                st.write(f"• {risk}")
        else:
            st.write("No risks available.")

    # ----------------------------------------------
    # Evidence
    # ----------------------------------------------

    supporting_evidence = safe_json_loads(evidence_for)
    opposing_evidence = safe_json_loads(evidence_against)

    evidence_col1, evidence_col2 = st.columns(2)

    with evidence_col1:
        with st.expander("✅ Evidence For"):
            if supporting_evidence:
                for evidence in supporting_evidence:
                    st.write(f"• {evidence}")
            else:
                st.write("No supporting evidence available.")

    with evidence_col2:
        with st.expander("❌ Evidence Against"):
            if opposing_evidence:
                for evidence in opposing_evidence:
                    st.write(f"• {evidence}")
            else:
                st.write("No opposing evidence available.")

else:
    st.warning("No structured analysis available for this research run.")


# ==================================================
# RAW RESEARCH
# ==================================================

st.divider()

with st.expander("🔎 Raw Research"):

    connection = get_connection()

    queries = connection.execute(
        """
        SELECT id, query
        FROM search_queries
        WHERE research_run_id = ?
        ORDER BY id
        """,
        (run_id,),
    ).fetchall()

    connection.close()

    if not queries:
        st.write("No search queries found.")

    for query_id, query in queries:

        st.markdown(f"### {query}")

        connection = get_connection()

        results = connection.execute(
            """
            SELECT
                title,
                url,
                snippet,
                score
            FROM search_results
            WHERE search_query_id = ?
            ORDER BY score DESC
            """,
            (query_id,),
        ).fetchall()

        connection.close()

        if not results:
            st.caption("No results stored for this query.")

        for title, url, snippet, score in results:

            if title:
                st.markdown(f"**{title}**")

            if snippet:
                st.write(snippet)

            if url:
                st.markdown(f"[Open source]({url})")

            if score is not None:
                st.caption(f"Relevance: {score:.2f}")

            st.divider()
