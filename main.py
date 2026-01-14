from fastapi import FastAPI
from pydantic import BaseModel

from ollama_client import chat_with_ollama

app = FastAPI()

# 기존 health check
@app.get("/health")
def health_check():
    return {"status": "ok"}


# -------------------------------
# Ollama Chat API
# -------------------------------
class ChatRequest(BaseModel):
    prompt: str


@app.post("/api/chat")
def chat_api(request: ChatRequest):
    answer = chat_with_ollama(request.prompt)
    return {"answer": answer}