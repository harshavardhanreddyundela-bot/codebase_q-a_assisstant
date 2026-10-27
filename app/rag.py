"""Step 5b: the RAG pipeline - index a repo, then retrieve + generate grounded answers."""
from pathlib import Path
from typing import Dict, List

from . import config, llm, vector_store
from .chunker import chunk_file
from .ingest import iter_source_files

SYSTEM_PROMPT = (
    "You are RepoLens, an assistant that answers questions about a code repository. "
    "Answer ONLY using the code context provided. Cite every claim with the file and "
    "line range in the form `path/to/file.py:10-42`. If the context does not contain "
    "enough information, say so clearly instead of guessing. Be concise and explain "
    "code flow step by step when asked."
)


def index_repo(repo_dir: Path, repo_id: str, label: str) -> Dict:
    chunks, files = [], 0
    for path, text in iter_source_files(repo_dir):
        files += 1
        chunks.extend(chunk_file(path, text))
    if not chunks:
        raise ValueError("No supported source files were found in this repository.")
    vector_store.index_chunks(repo_id, chunks)
    info = {"label": label, "files": files, "chunks": len(chunks)}
    vector_store.register_repo(repo_id, info)
    return {"repo_id": repo_id, **info}


def _build_prompt(question: str, hits: List[Dict]) -> str:
    blocks = []
    for h in hits:
        m = h["meta"]
        blocks.append(f"[{m['file_path']}:{m['start_line']}-{m['end_line']}] ({m['kind']} {m['name']})\n{h['text']}")
    context = "\n\n---\n\n".join(blocks)
    return f"CODE CONTEXT:\n{context}\n\nQUESTION: {question}\n\nANSWER:"


def answer(repo_id: str, question: str, top_k: int = None) -> Dict:
    hits = vector_store.search(repo_id, question, top_k or config.TOP_K)
    if not hits:
        return {"answer": "No code has been indexed for this repository yet.", "sources": []}
    text = llm.generate(SYSTEM_PROMPT, _build_prompt(question, hits))
    sources = [{
        "file_path": h["meta"]["file_path"],
        "start_line": h["meta"]["start_line"],
        "end_line": h["meta"]["end_line"],
        "name": h["meta"]["name"],
        "score": round(1 - h["distance"], 3),
        "snippet": h["text"][:600],
    } for h in hits]
    return {"answer": text, "sources": sources}
