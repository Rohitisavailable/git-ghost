from pathlib import Path
from git import Repo, InvalidGitRepositoryError, NoSuchPathError
from config import Config

def _repo(repo_path):
    path = Path(repo_path).expanduser().resolve()
    if not path.exists() or not path.is_dir():
        raise ValueError("That folder does not exist. Check the path and try again.")
    try:
        repo = Repo(path, search_parent_directories=True)
    except (InvalidGitRepositoryError, NoSuchPathError):
        raise ValueError("That folder is not inside a Git repository.")
    if repo.bare:
        raise ValueError("Bare repositories are not supported.")
    return repo

def scan_repository(repo_path, include_details=True):
    repo = _repo(repo_path)
    commits = []
    try:
        for commit in repo.iter_commits(max_count=Config.MAX_COMMITS):
            commits.append({
                "hash": commit.hexsha[:8],
                "full_hash": commit.hexsha,
                "message": commit.message.strip().splitlines()[0][:160],
                "author": str(commit.author),
                "date": commit.committed_datetime.isoformat(),
                "files_changed": len(commit.stats.files),
                "insertions": commit.stats.total.get("insertions", 0),
                "deletions": commit.stats.total.get("deletions", 0),
            })
    except Exception as exc:
        raise RuntimeError(f"Could not read commit history: {exc}")

    branches = sorted([head.name for head in repo.heads])
    current_branch = repo.active_branch.name if not repo.head.is_detached else "detached HEAD"
    tracked_files = sorted(repo.git.ls_files().splitlines())
    deleted = []
    try:
        for commit in repo.iter_commits(max_count=Config.MAX_COMMITS):
            for item in commit.diff(commit.parents[0] if commit.parents else None, create_patch=False):
                if item.deleted_file:
                    deleted.append({
                        "path": item.a_path,
                        "commit": commit.hexsha[:8],
                        "full_hash": commit.hexsha,
                        "message": commit.message.strip().splitlines()[0][:120],
                        "date": commit.committed_datetime.isoformat(),
                    })
    except Exception:
        pass

    # Keep the most recent deletion event for each path while retaining repeat deletions.
    deleted = deleted[:150]
    result = {
        "repo_name": Path(repo.working_tree_dir).name,
        "repo_path": str(Path(repo.working_tree_dir).resolve()),
        "branch": current_branch,
        "branches": branches,
        "commit_count": int(repo.git.rev_list("--count", "HEAD")) if commits else 0,
        "scanned_commits": len(commits),
        "file_count": len(tracked_files),
        "deleted_count": len(deleted),
        "commits": commits,
        "deleted_files": deleted,
        "tracked_files": tracked_files[:250],
        "truncated": len(commits) >= Config.MAX_COMMITS,
    }
    if include_details:
        result["readme"] = _readme(repo)
    return result

def _readme(repo):
    for name in ("README.md", "readme.md", "README", "Readme.md"):
        candidate = Path(repo.working_tree_dir) / name
        if candidate.is_file():
            try:
                return candidate.read_text(encoding="utf-8", errors="replace")[:4000]
            except OSError:
                return ""
    return ""

def get_file_history(repo_path, file_path):
    repo = _repo(repo_path)
    # Only accept a relative path and reject traversal outside the repository.
    rel = Path(file_path)
    if rel.is_absolute() or ".." in rel.parts:
        raise ValueError("Use a repository-relative file path.")
    safe_path = rel.as_posix()
    try:
        commits = []
        for commit in repo.iter_commits(paths=safe_path, max_count=40):
            commits.append({
                "hash": commit.hexsha[:8],
                "full_hash": commit.hexsha,
                "message": commit.message.strip().splitlines()[0][:160],
                "author": str(commit.author),
                "date": commit.committed_datetime.isoformat(),
            })
        return {"file_path": safe_path, "history": commits}
    except Exception as exc:
        raise RuntimeError(f"Could not read file history: {exc}")

def get_commit_details(repo_path, commit_hash):
    repo = _repo(repo_path)
    try:
        commit = repo.commit(commit_hash)
    except Exception:
        raise ValueError("That commit could not be found.")
    changed = []
    parent = commit.parents[0] if commit.parents else None
    for item in commit.diff(parent, create_patch=False):
        changed.append({
            "path": item.b_path or item.a_path,
            "status": "deleted" if item.deleted_file else "added" if item.new_file else "modified",
        })
    return {
        "hash": commit.hexsha,
        "message": commit.message.strip(),
        "author": str(commit.author),
        "date": commit.committed_datetime.isoformat(),
        "files": changed[:100],
    }
