import os

class Config:
    SECRET_KEY = os.environ.get("GHOST_SECRET_KEY", "local-dev-only-change-me")
    OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
    OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:7b")
    MAX_COMMITS = int(os.environ.get("GHOST_MAX_COMMITS", "100"))
