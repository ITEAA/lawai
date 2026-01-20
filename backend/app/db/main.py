from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from typing import List
from fastapi.middleware.cors import CORSMiddleware
import re

from backend.app.db.neo4j import run_cypher
from backend.app.db.queries import ANALYZE_BY_ARTICLE, ANALYZE_BY_LAW


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
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
    level: Optional[str] = None
    article_no: Optional[str] = None

@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    if req.article_no:
        rows = run_cypher(
            ANALYZE_BY_ARTICLE,
            {"law_name": req.law_name, "level": req.level, "article_no": req.article_no},
        )
    else:
        rows = run_cypher(
            ANALYZE_BY_LAW,
            {"law_name": req.law_name, "level": req.level},
        )

    articles = []

    for row in rows:
        item = dict(row)  # Neo4j Row → dict 복사
        item["highlights"] = extract_highlights(item.get("content"))
        articles.append(item)

    return {
        "law_name": req.law_name,
        "articles": articles,
    }
    
OBLIGATION_KEYWORDS = [
    "하여야", "해야", "금지", "의무",
    "제출", "보고", "비치", "작성", "준수"
]

MAX_SENTENCES = 2
MAX_LEN = 180

def extract_highlights(content: str) -> List[str]:
    """
    규칙 기반 발췌:
    - 원문 그대로
    - 의무/금지 표지어 포함 문장만
    - 최대 2문장, 문장당 180자
    - 실패 시 []
    """
    if not content or not isinstance(content, str):
        return []

    text = content.strip()
    if not text:
        return []

    # 나열형/범위형 content 방어 (예: "제1조부터 제5조까지")
    if re.search(r"제\s*\d+\s*조\s*부터\s*제\s*\d+\s*조\s*까지", text):
        return []

    # 아주 단순한 문장 분리 (판단 최소화)
    sentences = re.split(r"(?<=[\.다됨함])\s+", text)

    hits = []
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        if any(k in s for k in OBLIGATION_KEYWORDS):
            hits.append(s[:MAX_LEN])
        if len(hits) >= MAX_SENTENCES:
            break

    return hits
