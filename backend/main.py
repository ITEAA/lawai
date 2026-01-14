from fastapi import FastAPI
from backend.app.db.neo4j import run_cypher

app = FastAPI()

@app.get("/")
def health():
    return {"status": "ok"}

@app.get("/neo4j/ping")
def neo4j_ping():
    rows = run_cypher("RETURN 1 AS ok")
    return {"neo4j": rows[0]["ok"]}

@app.get("/analyze")
def analyze():
    query = """
    MATCH (a:ARTICLE)
    WHERE a.risk_level_final IN ["HIGH", "MID", "LOW"]

    OPTIONAL MATCH (d:DOC)-[:CONTAINS]->(a)
    OPTIONAL MATCH (p:ARTICLE)-[:PENALTY_LINK]->(a)
    OPTIONAL MATCH (a)-[:REFERENCE_WEAK]->(ref1:ARTICLE)
    OPTIONAL MATCH (a)-[:DELEGATION_PATTERN]->(ref2:ARTICLE)

    RETURN
      a.risk_level_final AS risk_level,
      a.node_id     AS article_id,
      a.law_name    AS law_name,
      a.article_no  AS article_no,
      a.title       AS title,
      a.content     AS content,

      d.node_id     AS doc_id,
      d.title       AS doc_title,

      collect(
        DISTINCT CASE
          WHEN p IS NOT NULL THEN {
            article_id: p.node_id,
            article_no: p.article_no,
            title: p.title,
            content: p.content
          }
        END
      ) AS penalties,

      collect(
        DISTINCT CASE
          WHEN ref1 IS NOT NULL THEN {
            article_id: ref1.node_id,
            article_no: ref1.article_no,
            title: ref1.title
          }
        END
      ) AS reference_weak,

      collect(
        DISTINCT CASE
          WHEN ref2 IS NOT NULL THEN {
            article_id: ref2.node_id,
            article_no: ref2.article_no,
            title: ref2.title
          }
        END
      ) AS delegation_pattern
    """

    rows = run_cypher(query)

    result = {
        "HIGH": [],
        "MID": [],
        "LOW": []
    }

    for r in rows:
        penalties = [p for p in r["penalties"] if p] if r["penalties"] else []
        penalties_out = penalties if penalties else None  # 합의: 없으면 null

        item = {
            "article": {
                "id": r["article_id"],
                "law_name": r["law_name"],
                "article_no": r["article_no"],
                "title": r["title"],
                "content": r["content"],
            },
            "doc": {
                "id": r["doc_id"],
                "title": r["doc_title"]
            } if r["doc_id"] else None,
            "penalties": penalties_out,
            "references": {
                "reference_weak": [x for x in r["reference_weak"] if x],
                "delegation_pattern": [x for x in r["delegation_pattern"] if x],
            }
        }

        result[r["risk_level"]].append(item)

    return result
