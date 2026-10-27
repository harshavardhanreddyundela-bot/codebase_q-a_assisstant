"""FastAPI backend.  Run:  uvicorn app.main:app --reload"""
import shutil
import zipfile

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from . import config, ingest, rag, vector_store
from .llm import LLMNotConfigured

app = FastAPI(title="RepoLens - Codebase Q&A Assistant")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class GithubRequest(BaseModel):
    url: str


class AskRequest(BaseModel):
    question: str
    top_k: int = config.TOP_K


@app.get("/health")
def health():
    return {"status": "ok", "llm_provider": config.LLM_PROVIDER}


@app.post("/repos/zip")
async def upload_zip(file: UploadFile = File(...)):
    if not (file.filename or "").lower().endswith(".zip"):
        raise HTTPException(400, "Please upload a .zip file.")
    repo_id = ingest.new_repo_id()
    try:
        repo_dir = ingest.load_from_zip(await file.read(), repo_id)
        return rag.index_repo(repo_dir, repo_id, label=file.filename)
    except (ValueError, zipfile.BadZipFile) as e:
        shutil.rmtree(config.WORKSPACE_DIR / repo_id, ignore_errors=True)
        raise HTTPException(400, str(e))


@app.post("/repos/github")
def add_github(req: GithubRequest):
    repo_id = ingest.new_repo_id()
    try:
        repo_dir = ingest.load_from_github(req.url, repo_id)
        return rag.index_repo(repo_dir, repo_id, label=req.url.rstrip("/").split("github.com/")[-1])
    except ValueError as e:
        shutil.rmtree(config.WORKSPACE_DIR / repo_id, ignore_errors=True)
        raise HTTPException(400, str(e))


@app.get("/repos")
def repos():
    return vector_store.list_repos()


@app.post("/repos/{repo_id}/ask")
def ask(repo_id: str, req: AskRequest):
    if repo_id not in vector_store.list_repos():
        raise HTTPException(404, "Unknown repository id.")
    if not req.question.strip():
        raise HTTPException(400, "Question is empty.")
    try:
        return rag.answer(repo_id, req.question, req.top_k)
    except LLMNotConfigured as e:
        raise HTTPException(503, str(e))
