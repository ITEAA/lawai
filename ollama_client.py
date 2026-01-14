import requests

OLLAMA_URL = "http://localhost:11434"

def chat_with_ollama(prompt: str, model: str = "llama3.2:3b"):
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "너는 법률·컴플라이언스 분석 AI다."},
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "options": {
            "num_predict": 16   # 🔥 핵심: 짧게 생성
        }
    }

    response = requests.post(
        f"{OLLAMA_URL}/api/chat",
        json=payload,
        timeout=300  # 🔥 테스트용으로만 늘림
    )

    response.raise_for_status()
    return response.json()["message"]["content"]