import requests
import json
import os

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/chat")
MODEL = "qwen2.5:1.5b"            

def chat(prompt: str, system: str | None = None, timeout: int = 120) -> str:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    try:
        r = requests.post(
            OLLAMA_URL,
            json={"model": MODEL, "messages": messages, "stream": False,
                  "options": {"temperature": 0}},
            timeout=timeout,
        )
        r.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"LLM unavailable: {e}") from e
    return r.json()["message"]["content"]

def chat_stream(prompt: str, system: str | None = None, timeout: int = 120):
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    try:
        r = requests.post(
            OLLAMA_URL,
            json={"model": MODEL, "messages": messages, "stream": True,
                  "options": {"temperature": 0}},
            timeout=timeout, stream=True,
        )
        r.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"LLM unavailable: {e}") from e
    for line in r.iter_lines():
        if line:
            piece = json.loads(line).get("message", {}).get("content", "")
            if piece:
                yield piece

if __name__ == "__main__":
    print(chat("In one sentence, what is RAG in AI?"))