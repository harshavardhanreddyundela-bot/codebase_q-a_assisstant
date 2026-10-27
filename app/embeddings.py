"""Step 3: embedding model.

Uses Chroma's bundled MiniLM-L6-v2 (ONNX) model: it runs locally, needs no API key,
and is downloaded automatically on first use. Swap this function to plug in OpenAI /
Gemini embeddings later (see PROGRESS.md - pending item).
"""
from chromadb.utils import embedding_functions


def get_embedding_function():
    return embedding_functions.DefaultEmbeddingFunction()
