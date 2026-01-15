from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

from backend.app.db.neo4j import run_cypher
from backend.app.db.queries import (
    ANALYZE_BY_ARTICLE,
    ANALYZE_BY_LAW,
)

app = FastAPI()


# -----------------
# Health Check
# -----------------
@app.get("/")
def health():
    return {"status": "ok"}


@app.get("/neo4j/ping")
def neo4j_ping():
    rows = run_cypher("RETURN 1 AS ok")
    return {"neo4j": rows[0]["ok"]}


# -----------------
# Analyze API
# -----------------
class AnalyzeRequest(BaseModel):
    law_name: str
    article_no: Optional[str] = None


@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    if req.article_no:
        rows = run_cypher(
            ANALYZE_BY_ARTICLE,
            {
                "law_name": req.law_name,
                "article_no": req.article_no,
            },
        )
    else:
        rows = run_cypher(
            ANALYZE_BY_LAW,
            {
                "law_name": req.law_name,
            },
        )

    return {
        "law_name": req.law_name,
        "articles": rows,
    }
