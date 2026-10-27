"""Streamlit UI.  Run:  streamlit run frontend/streamlit_app.py"""
import os

import requests
import streamlit as st

API = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="RepoLens", page_icon="🔎", layout="wide")
st.title("🔎 RepoLens — Codebase Q&A Assistant")


def api_error(r: requests.Response) -> str:
    try:
        return r.json().get("detail", r.text)
    except Exception:
        return r.text


with st.sidebar:
    st.header("1. Add a repository")
    zf = st.file_uploader("Upload project ZIP", type=["zip"])
    if zf and st.button("Index ZIP"):
        with st.spinner("Parsing, chunking and embedding..."):
            r = requests.post(f"{API}/repos/zip", files={"file": (zf.name, zf.getvalue())}, timeout=600)
        if r.ok:
            st.session_state["active_repo"] = r.json()["repo_id"]
            st.success(f"Indexed {r.json()['files']} files / {r.json()['chunks']} chunks")
        else:
            st.error(api_error(r))

    gh = st.text_input("...or public GitHub URL", placeholder="https://github.com/owner/repo")
    if gh and st.button("Index GitHub repo"):
        with st.spinner("Cloning and indexing..."):
            r = requests.post(f"{API}/repos/github", json={"url": gh}, timeout=600)
        if r.ok:
            st.session_state["active_repo"] = r.json()["repo_id"]
            st.success(f"Indexed {r.json()['files']} files / {r.json()['chunks']} chunks")
        else:
            st.error(api_error(r))

    st.header("2. Pick a repository")
    try:
        repos = requests.get(f"{API}/repos", timeout=10).json()
    except requests.RequestException:
        repos = {}
        st.warning("Backend not reachable. Start it with: uvicorn app.main:app --reload")
    ids = list(repos.keys())
    if ids:
        default = ids.index(st.session_state["active_repo"]) if st.session_state.get("active_repo") in ids else 0
        repo_id = st.selectbox("Indexed repos", ids, index=default,
                               format_func=lambda i: f"{repos[i]['label']} ({repos[i]['chunks']} chunks)")
    else:
        repo_id = None
    top_k = st.slider("Chunks retrieved (top-k)", 2, 12, 6)

if not repo_id:
    st.info("Upload a ZIP or add a GitHub repo from the sidebar to begin.")
    st.stop()

history = st.session_state.setdefault("history", {}).setdefault(repo_id, [])
for msg in history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        for s in msg.get("sources", []):
            with st.expander(f"{s['file_path']}:{s['start_line']}-{s['end_line']}  (score {s['score']})"):
                st.code(s["snippet"])

if q := st.chat_input("Ask about this codebase, e.g. 'How does authentication work?'"):
    history.append({"role": "user", "content": q})
    with st.chat_message("user"):
        st.markdown(q)
    with st.chat_message("assistant"):
        with st.spinner("Retrieving code and generating answer..."):
            r = requests.post(f"{API}/repos/{repo_id}/ask", json={"question": q, "top_k": top_k}, timeout=120)
        if r.ok:
            data = r.json()
            st.markdown(data["answer"])
            for s in data["sources"]:
                with st.expander(f"{s['file_path']}:{s['start_line']}-{s['end_line']}  (score {s['score']})"):
                    st.code(s["snippet"])
            history.append({"role": "assistant", "content": data["answer"], "sources": data["sources"]})
        else:
            st.error(api_error(r))
