from fastapi import FastAPI

app = FastAPI(
    title="LawAI Backend",
    description="Backend API for GraphRAG-based legal compliance system",
    version="0.1.0"
)

@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "LawAI backend is running on Render"
    }

@app.get("/health")
def health_check():
    return {
        "health": "ok"
    }
