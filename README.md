# 🔎 RepoLens — Codebase Q&A Assistant
Gen AI Mastery course project. Ask natural-language questions about a code repository and get
answers grounded in the actual code, with `file:line` references (RAG pipeline).

## Pipeline
```
ZIP / GitHub URL → ingest → chunk (AST for .py, line windows otherwise)
  → embeddings → ChromaDB  ──►  question → top-k retrieval → prompt → LLM → answer + sources
```

## Setup
```bash
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                  # add GEMINI_API_KEY or OPENAI_API_KEY
```

## Run (two terminals)
```bash
uvicorn app.main:app --reload          # backend  → http://localhost:8000/docs
streamlit run frontend/streamlit_app.py  # frontend → http://localhost:8501
```

## Tests
```bash
python -m pytest tests
```

## Structure
| File | Role |
|---|---|
| `app/ingest.py` | ZIP (safe extract) / GitHub clone, file filtering |
| `app/chunker.py` | Function/class-aware chunking with line numbers |
| `app/embeddings.py` | Local embedding model (Chroma default MiniLM) |
| `app/vector_store.py` | ChromaDB indexing, search, repo registry |
| `app/llm.py` | Gemini / OpenAI wrapper |
| `app/rag.py` | Index + retrieve + grounded answer |
| `app/main.py` | FastAPI endpoints |
| `frontend/streamlit_app.py` | Chat UI with source viewer |

See `PROGRESS.md` for what is done and what remains.
