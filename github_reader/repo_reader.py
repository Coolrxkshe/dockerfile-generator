import os
import tempfile
import shutil
from pathlib import Path


def clone_github_repo(url: str) -> tuple:
    """
    Clone a public GitHub repo to a temp folder.
    Returns (temp_dir_path, error_message)
    """
    try:
        import git
    except ImportError:
        return None, "gitpython not installed. Run: pip install gitpython"

    # clean the URL
    url = url.strip().rstrip("/")
    if not url.startswith("http"):
        url = "https://github.com/" + url

    tmp_dir = tempfile.mkdtemp(prefix="dockergen_")

    try:
        git.Repo.clone_from(url, tmp_dir, depth=1)
        return tmp_dir, None
    except Exception as e:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        return None, str(e)


def get_repo_info(url: str) -> dict:
    """Extract owner and repo name from GitHub URL."""
    url = url.strip().rstrip("/")
    parts = url.replace("https://github.com/", "").replace("http://github.com/", "").split("/")
    if len(parts) >= 2:
        return {"owner": parts[0], "repo": parts[1]}
    return {"owner": "unknown", "repo": "unknown"}


def cleanup_repo(tmp_dir: str):
    """Delete the cloned repo temp folder."""
    try:
        shutil.rmtree(tmp_dir, ignore_errors=True)
    except Exception:
        pass