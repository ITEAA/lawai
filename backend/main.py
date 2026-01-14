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
