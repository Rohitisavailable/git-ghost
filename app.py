from flask import Flask, render_template, request, jsonify
from pathlib import Path
from services.git_scanner import scan_repository, get_file_history, get_commit_details
from services.ghost_ai import ask_ghost
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

@app.get("/")
def index():
    return render_template("index.html")

@app.post("/api/scan")
def api_scan():
    data = request.get_json(silent=True) or {}
    repo_path = (data.get("repo_path") or "").strip()
    if not repo_path:
        return jsonify({"error": "Enter a repository path."}), 400
    try:
        result = scan_repository(repo_path)
        return jsonify(result)
    except (ValueError, RuntimeError) as exc:
        return jsonify({"error": str(exc)}), 400

@app.post("/api/ask")
def api_ask():
    data = request.get_json(silent=True) or {}
    repo_path = (data.get("repo_path") or "").strip()
    question = (data.get("question") or "").strip()
    if not repo_path or not question:
        return jsonify({"error": "Repository path and question are required."}), 400
    try:
        context = scan_repository(repo_path, include_details=False)
        answer = ask_ghost(question, context)
        return jsonify({"answer": answer, "source": "ollama" if answer.get("used_ai") else "fallback"})
    except (ValueError, RuntimeError) as exc:
        return jsonify({"error": str(exc)}), 400

@app.post("/api/file-history")
def api_file_history():
    data = request.get_json(silent=True) or {}
    repo_path = (data.get("repo_path") or "").strip()
    file_path = (data.get("file_path") or "").strip()
    try:
        return jsonify(get_file_history(repo_path, file_path))
    except (ValueError, RuntimeError) as exc:
        return jsonify({"error": str(exc)}), 400

@app.post("/api/commit")
def api_commit():
    data = request.get_json(silent=True) or {}
    repo_path = (data.get("repo_path") or "").strip()
    commit_hash = (data.get("commit_hash") or "").strip()
    try:
        return jsonify(get_commit_details(repo_path, commit_hash))
    except (ValueError, RuntimeError) as exc:
        return jsonify({"error": str(exc)}), 400

if __name__ == "__main__":
    # Local-only development server. Do not expose this debug server to the internet.
    app.run(host="127.0.0.1", port=5000, debug=True)
