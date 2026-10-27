# RepoLens — Progress (~70%)

Status is based on the code in this repo. "Written" means the code exists; only items marked
**tested** were actually executed.

| Workstream | Status | Notes |
|---|---|---|
| Requirements & architecture | ✅ Done | README pipeline diagram |
| Ingestion (ZIP + GitHub) | ✅ Written | Zip-slip protection, file filters, size limits |
| Chunking | ✅ Written + **unit-tested** | AST for Python, line windows for other languages |
| Embeddings + ChromaDB | ✅ Written | Local MiniLM; cosine similarity; one collection per repo |
| Retrieval + LLM (RAG) | ✅ Written | Grounded prompt, cites `file:start-end`, top-k configurable |
| FastAPI backend | ✅ Written | /repos/zip, /repos/github, /repos, /repos/{id}/ask |
| Streamlit UI | 🟡 Basic | Chat + source expanders; needs polish |
| Testing / evaluation | 🔴 ~20% | Only chunker tests so far |

## Remaining ~30%
- [ ] End-to-end test on 2–3 real repos with a live API key; fix issues found
- [ ] Reranking (cross-encoder or LLM rerank) to improve retrieval precision
- [ ] "Generate project documentation" feature (README / module summary endpoint)
- [ ] Evaluation set: 15–20 questions with expected files → measure retrieval hit-rate
- [ ] Language-aware chunking for JS/Java (tree-sitter) instead of line windows
- [ ] Chat history in prompts (follow-up questions), error handling polish, deployment
- [ ] Final report + PPT + demo video
