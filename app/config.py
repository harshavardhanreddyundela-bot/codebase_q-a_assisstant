"""Central configuration (read from environment / .env)."""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:  # dotenv is optional for unit tests
    pass

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

CHROMA_DIR = Path(os.getenv("CHROMA_DIR", "./data/chroma"))
WORKSPACE_DIR = Path(os.getenv("WORKSPACE_DIR", "./data/repos"))
REGISTRY_FILE = Path(os.getenv("REGISTRY_FILE", "./data/repos.json"))

TOP_K = int(os.getenv("TOP_K", "6"))

# Ingestion limits
MAX_FILE_BYTES = 300_000
MAX_ZIP_BYTES = 50 * 1024 * 1024

# Chunking
CHUNK_LINES = 60
CHUNK_OVERLAP = 10
MAX_CHUNK_LINES = 120   # a function/class longer than this is split into windows

SUPPORTED_EXT = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".go", ".rs", ".c", ".cpp",
    ".h", ".cs", ".rb", ".php", ".kt", ".swift", ".sql", ".sh",
    ".html", ".css", ".json", ".yml", ".yaml", ".toml", ".md", ".txt",
}
SPECIAL_FILES = {"Dockerfile", "Makefile", "requirements.txt"}
IGNORE_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "env", "dist",
    "build", ".idea", ".vscode", "target", ".next", ".mypy_cache", ".pytest_cache",
}
