import requests
from flask import current_app

SYSTEM_PROMPT = """You are Git Ghost, an atmospheric but helpful spirit haunting a software repository.
Speak with a restrained spooky personality: eerie, witty, cinematic, never abusive. You are also a precise
software-history assistant. Only state facts supported by the supplied repository evidence. If the evidence
does not answer something, say so clearly and suggest which Git command or file history could reveal it.
Never invent commit hashes, authors, dates, or reasons for a change. Keep answers concise and useful."""

def ask_ghost(question, context):
    # Keep prompt context compact and grounded in scanned repository metadata.
    compact = {
        "repository": context.get("repo_name"),
        "branch": context.get("branch"),
        "commit_count": context.get("commit_count"),
        "branches": context.get("branches", [])[:20],
        "recent_commits": context.get("commits", [])[:20],
        "deleted_files": context.get("deleted_files", [])[:30],
        "tracked_files": context.get("tracked_files", [])[:80],
    }
    prompt = f"Repository evidence (JSON):\n{compact}\n\nUser question: {question}"
    url = current_app.config["OLLAMA_URL"].rstrip("/") + "/api/chat"
    model = current_app.config["OLLAMA_MODEL"]
    try:
        response = requests.post(
            url,
            json={"model": model, "stream": False, "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ]},
            timeout=90,
        )
        response.raise_for_status()
        answer = response.json().get("message", {}).get("content", "").strip()
        if answer:
            return {"text": answer, "used_ai": True, "model": model}
    except requests.RequestException:
        pass

    # Useful offline fallback so the project remains demonstrable without Ollama.
    return {
        "text": _fallback_answer(question, compact),
        "used_ai": False,
        "model": None,
    }

def _fallback_answer(question, context):
    q = question.lower()
    if any(word in q for word in ("deleted", "graveyard", "removed")):
        entries = context.get("deleted_files", [])[:5]
        if entries:
            lines = [f" I found {len(context.get('deleted_files', []))} deletion event(s) in the scanned history."]
            for item in entries:
                lines.append(f"• {item['path']} — commit {item['commit']} ({item['message']})")
            return "The graveyard has yielded evidence:\n" + "\n".join(lines) + "\n\nI cannot infer the developer's motive from Git metadata alone."
        return "The graveyard is quiet. No deleted-file events were found in the scanned commit window."
    return (
        f"I have awakened inside {context.get('repository') or 'this repository'} on branch "
        f"{context.get('branch') or 'unknown'}. I can see "
        f"{context.get('commit_count', 0)} commits and {len(context.get('tracked_files', []))} tracked file(s) "
        f"in the available scan. The local Ollama model is not responding, so I cannot interpret your question yet. "
        "Start Ollama and pull the configured model to give me a voice."
    )
