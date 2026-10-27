"""Step 1 of the pipeline: get a repository onto disk and list its source files."""
import io
import os
import re
import subprocess
import uuid
import zipfile
from pathlib import Path
from typing import Iterator, Tuple

from . import config

GITHUB_RE = re.compile(r"^https://github\.com/[\w.-]+/[\w.-]+?(\.git)?/?$")


def new_repo_id() -> str:
    return uuid.uuid4().hex[:8]


def load_from_zip(data: bytes, repo_id: str) -> Path:
    """Extract an uploaded ZIP safely (blocks path traversal / zip-slip)."""
    if len(data) > config.MAX_ZIP_BYTES:
        raise ValueError("ZIP is too large (limit 50 MB).")
    dest = config.WORKSPACE_DIR / repo_id
    dest.mkdir(parents=True, exist_ok=True)
    root = dest.resolve()
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        for member in zf.infolist():
            target = (dest / member.filename).resolve()
            if target != root and root not in target.parents:
                raise ValueError(f"Unsafe path in ZIP: {member.filename}")
        zf.extractall(dest)
    return dest


def load_from_github(url: str, repo_id: str) -> Path:
    """Shallow-clone a public GitHub repository."""
    url = url.strip()
    if not GITHUB_RE.match(url):
        raise ValueError("Only public https://github.com/<owner>/<repo> URLs are supported.")
    dest = config.WORKSPACE_DIR / repo_id
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", url, str(dest)],
            check=True, capture_output=True, timeout=180,
        )
    except subprocess.CalledProcessError as e:
        raise ValueError(f"git clone failed: {e.stderr.decode(errors='ignore')[:300]}")
    except subprocess.TimeoutExpired:
        raise ValueError("git clone timed out.")
    return dest


def iter_source_files(root: Path) -> Iterator[Tuple[str, str]]:
    """Yield (relative_posix_path, text) for every supported, reasonably sized file."""
    root = Path(root)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in config.IGNORE_DIRS]
        for name in filenames:
            p = Path(dirpath) / name
            if p.suffix.lower() not in config.SUPPORTED_EXT and name not in config.SPECIAL_FILES:
                continue
            try:
                if p.stat().st_size > config.MAX_FILE_BYTES:
                    continue
                text = p.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            if text.strip():
                yield p.relative_to(root).as_posix(), text
