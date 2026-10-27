"""Step 2: split source files into chunks that keep file path + line numbers.

Python files are split along function / class boundaries using `ast`
(so one chunk = one logical unit). Everything else uses overlapping line windows.
"""
import ast
from dataclasses import dataclass
from typing import List, Tuple

from . import config

Numbered = List[Tuple[int, str]]  # (1-based line number, line text)


@dataclass
class Chunk:
    file_path: str
    start_line: int
    end_line: int
    kind: str      # function | class | module | block
    name: str
    text: str


def _windows(path: str, lines: Numbered, kind: str = "block", name: str = "") -> List[Chunk]:
    step = max(1, config.CHUNK_LINES - config.CHUNK_OVERLAP)
    out: List[Chunk] = []
    for i in range(0, len(lines), step):
        part = lines[i:i + config.CHUNK_LINES]
        if part and "".join(t for _, t in part).strip():
            out.append(Chunk(path, part[0][0], part[-1][0], kind, name,
                             "\n".join(t for _, t in part)))
        if i + config.CHUNK_LINES >= len(lines):
            break
    return out


def _chunk_python(path: str, source: str) -> List[Chunk]:
    raw = source.splitlines()
    numbered: Numbered = list(enumerate(raw, start=1))
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return _windows(path, numbered)

    chunks: List[Chunk] = []
    covered = set()
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        start = min([node.lineno] + [d.lineno for d in node.decorator_list])
        end = node.end_lineno or node.lineno
        kind = "class" if isinstance(node, ast.ClassDef) else "function"
        seg = numbered[start - 1:end]
        if len(seg) <= config.MAX_CHUNK_LINES:
            chunks.append(Chunk(path, start, end, kind, node.name, "\n".join(t for _, t in seg)))
        else:
            chunks.extend(_windows(path, seg, kind, node.name))
        covered.update(range(start, end + 1))

    leftovers = [(n, t) for n, t in numbered if n not in covered]
    chunks.extend(_windows(path, leftovers, "module", "<module level>"))
    return sorted(chunks, key=lambda c: c.start_line)


def chunk_file(path: str, text: str) -> List[Chunk]:
    if path.endswith(".py"):
        return _chunk_python(path, text)
    return _windows(path, list(enumerate(text.splitlines(), start=1)))
