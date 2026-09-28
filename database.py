import sqlite3
import json

DB_NAME = "business_research.db"

def save_analysis(
    research_run_id: int,
    analysis: dict
):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO analyses (
            research_run_id,
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
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        research_run_id,
        analysis["demand_score"],
        analysis["competition_score"],
        analysis["profitability_score"],
        analysis["confidence_score"],
        json.dumps(analysis["customer_segments"]),
        json.dumps(analysis["top_themes"]),
        json.dumps(analysis["evidence_for"]),
        json.dumps(analysis["evidence_against"]),
        json.dumps(analysis["risks"]),
        json.dumps(analysis["next_test"])
    ))

    connection.commit()
    connection.close()

def create_database():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ideas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS research_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idea_id INTEGER NOT NULL,
            research_question TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (idea_id) REFERENCES ideas(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS search_queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            research_run_id INTEGER NOT NULL,
            query TEXT NOT NULL,
            FOREIGN KEY (research_run_id) REFERENCES research_runs(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS search_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            search_query_id INTEGER NOT NULL,
            title TEXT,
            url TEXT,
            snippet TEXT,
            score REAL,
            FOREIGN KEY (search_query_id) REFERENCES search_queries(id)
        )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analyses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        research_run_id INTEGER NOT NULL,

        demand_score INTEGER,
        competition_score INTEGER,
        profitability_score INTEGER,
        confidence_score INTEGER,

        customer_segments TEXT,
        top_themes TEXT,
        evidence_for TEXT,
        evidence_against TEXT,
        risks TEXT,
        next_test TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY (research_run_id)
            REFERENCES research_runs(id)
    )
""")

    connection.commit()
    connection.close()

def save_idea(name: str):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    # Check whether this idea already exists
    cursor.execute(
        "SELECT id FROM ideas WHERE name = ?",
        (name,)
    )

    existing = cursor.fetchone()

    if existing:
        idea_id = existing[0]
    else:
        cursor.execute(
            "INSERT INTO ideas (name) VALUES (?)",
            (name,)
        )

        idea_id = cursor.lastrowid
        connection.commit()

    connection.close()

    return idea_id


def get_ideas():
    connection = sqlite3.connect(DB_NAME)

    cursor = connection.cursor()

    cursor.execute("""
        SELECT id,  name, created_at
        FROM ideas
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    connection.close()

    return rows

def save_research_result(idea: str, research_question: str):
    connection = sqlite3.connect(DB_NAME)

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO ideas (idea)
        VALUES (?)
    """, (idea,))

    connection.commit()
    connection.close()

if __name__ == "__main__":
    create_database()

    ideas = get_ideas()

    for idea in ideas:
        print(idea)

def save_research_run(idea_id: int, research_question: str):
    connection = sqlite3.connect(DB_NAME)

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO research_runs (
            idea_id,
            research_question
        )
        VALUES (?, ?)
    """, (
        idea_id,
        research_question
    ))

    connection.commit()

    research_run_id = cursor.lastrowid

    connection.close()

    return research_run_id


def save_search_query(research_run_id: int, query: str):
    connection = sqlite3.connect(DB_NAME)

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO search_queries (
            research_run_id,
            query
        )
        VALUES (?, ?)
    """, (
        research_run_id,
        query
    ))

    connection.commit()

    search_query_id = cursor.lastrowid

    connection.close()

    return search_query_id


def save_search_result(
    search_query_id: int,
    title: str,
    url: str,
    snippet: str,
    score: float
):
    connection = sqlite3.connect(DB_NAME)

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO search_results (
            search_query_id,
            title,
            url,
            snippet,
            score
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        search_query_id,
        title,
        url,
        snippet,
        score
    ))

    connection.commit()
    connection.close()



def rename_idea(idea_id: int, new_name: str):

    connection = sqlite3.connect(DB_NAME)

    cursor = connection.cursor()

    cursor.execute("""
        UPDATE ideas
        SET name = ?
        WHERE id = ?
    """, (new_name, idea_id))

    connection.commit()

    connection.close()