# Git Ghost 👻

**Your code never truly dies.** Git Ghost is a local-first, horror-themed interface for exploring a Git repository's history. It reveals deleted-file events, recent commits, branches and tracked files, then lets you ask a locally hosted open-weight model questions about the evidence.

## Features

- Haunted terminal-style repository awakening.
- Repository overview: branches, commit count and tracked files.
- Code graveyard: deleted-file events found in scanned Git history.
- Haunted timeline: recent commits, author, date and change counts.
- Séance chat: ask questions using a local Ollama model.
- Offline fallback responses when Ollama is unavailable.

## Requirements

- Python 3.10+
- Git installed and available on PATH
- A local Git repository to inspect
- Optional: [Ollama](https://ollama.com/) for local AI chat

## Setup (Windows PowerShell)

```powershell
git clone <your-git-ghost-repository>
cd git-ghost

py -m venv .venv
.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt

python app.py
```

Open `http://127.0.0.1:5000` in your browser. Enter the full path to a local Git repository, for example:

```text
C:\Users\YourName\Documents\my-project
```

## Setup (macOS / Linux)

```bash
git clone <your-git-ghost-repository>
cd git-ghost

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt

python app.py
```

Open `http://127.0.0.1:5000`.

## Enable local AI with Ollama

Install and start Ollama, then pull the default model:

```bash
ollama pull qwen2.5:3b
```

Run Git Ghost in another terminal. The app sends repository metadata and your question to Ollama's local API at `http://127.0.0.1:11434`. No hosted AI API key is needed.

To use another model, set environment variables before starting Flask.

PowerShell:

```powershell
$env:OLLAMA_MODEL = "gemma2:2b"
$env:OLLAMA_URL = "http://127.0.0.1:11434"
python app.py
```

macOS / Linux:

```bash
OLLAMA_MODEL=gemma2:2b OLLAMA_URL=http://127.0.0.1:11434 python app.py
```

If Ollama is unavailable, the UI still works and the chat uses a small deterministic fallback.

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `OLLAMA_URL` | `http://127.0.0.1:11434` | Local Ollama API base URL |
| `OLLAMA_MODEL` | `qwen2.5:3b` | Model name already pulled in Ollama |
| `GHOST_MAX_COMMITS` | `100` | Number of recent commits to inspect |
| `GHOST_SECRET_KEY` | development value | Flask secret key (not currently used for login) |

## How it works

1. The browser sends a local repository path to Flask.
2. GitPython reads commits, branches, tracked paths and deletion events.
3. The frontend renders the results as a haunted dashboard.
4. For chat, Flask passes a compact evidence summary to Ollama.
5. The model is instructed not to invent repository facts. When Ollama is unavailable, a fallback response is used.

## Project structure

```text
git-ghost/
├── app.py
├── config.py
├── requirements.txt
├── services/
│   ├── git_scanner.py
│   └── ghost_ai.py
├── templates/
│   └── index.html
└── static/
    ├── css/style.css
    └── js/app.js
```

## Important limitations and safety

- This is a local development application. It binds to `127.0.0.1`; do not expose Flask's debug server to a public network.
- Only point it at repositories you own or are authorized to inspect.
- Git Ghost reads repository metadata and commit history; it does not execute repository code or modify Git data.
- The first version scans a configurable recent commit window. Older history may be omitted when the repository has more commits than `GHOST_MAX_COMMITS`.
- A deletion event tells you that a path was deleted in a commit. Git metadata does not reliably reveal *why* a developer deleted it.
- Ollama receives repository metadata included in the prompt. Keep sensitive repository names, commit messages and paths in mind even though inference is local.
- The UI accepts a local filesystem path. Keep this app on your own machine and do not deploy it as-is for untrusted users.

## Roadmap

- Inspect deleted file contents at the parent commit.
- Branch comparison and abandoned-branch detection.
- File-level history and commit detail drawer.
- Searchable graveyard and timeline filters.
- Optional sound design and accessibility controls.
- Tests and packaged desktop experience.

## License

MIT. See `LICENSE`.
