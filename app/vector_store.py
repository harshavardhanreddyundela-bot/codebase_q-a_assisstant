"""Step 4: ChromaDB storage + semantic search. One collection per repository."""
import json
from typing import Dict, List

import chromadb

from . import config
from .chunker import Chunk
from .embeddings import get_embedding_function

_client = None
BATCH = 100


def _get_client():
    global _client
    if _client is None:
        config.CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(path=str(config.CHROMA_DIR))
    return _client


def _collection(repo_id: str):
    return _get_client().get_or_create_collection(
        name=f"repo_{repo_id}",
        embedding_function=get_embedding_function(),
        metadata={"hnsw:space": "cosine"},
    )


def _document(c: Chunk) -> str:
    # Header gives the embedding model file/symbol context, not just raw code.
    return f"File: {c.file_path}\nLines: {c.start_line}-{c.end_line}\n{c.kind}: {c.name}\n\n{c.text}"


def index_chunks(repo_id: str, chunks: List[Chunk]) -> int:
    col = _collection(repo_id)
    for i in range(0, len(chunks), BATCH):
        part = chunks[i:i + BATCH]
        col.add(
            ids=[f"{repo_id}-{i + j}" for j in range(len(part))],
            documents=[_document(c) for c in part],
            metadatas=[{
                "file_path": c.file_path, "start_line": c.start_line,
                "end_line": c.end_line, "kind": c.kind, "name": c.name,
            } for c in part],
        )
    return len(chunks)


def search(repo_id: str, question: str, k: int = None) -> List[Dict]:
    col = _collection(repo_id)
    n = min(k or config.TOP_K, max(col.count(), 1))
    res = col.query(query_texts=[question], n_results=n)
    hits = []
    for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
        hits.append({"text": doc, "meta": meta, "distance": float(dist)})
    return hits


def delete_repo(repo_id: str) -> None:
    try:
        _get_client().delete_collection(f"repo_{repo_id}")
    except Exception:
        pass


# ---- tiny JSON registry so the UI can list indexed repos with friendly names ----
def _load_registry() -> Dict[str, dict]:
    if config.REGISTRY_FILE.exists():
        return json.loads(config.REGISTRY_FILE.read_text())
    return {}


def register_repo(repo_id: str, info: dict) -> None:
    reg = _load_registry()
    reg[repo_id] = info
    config.REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
    config.REGISTRY_FILE.write_text(json.dumps(reg, indent=2))


def list_repos() -> Dict[str, dict]:
    return _load_registry()
