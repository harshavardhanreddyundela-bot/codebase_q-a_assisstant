from app.chunker import chunk_file

PY = '''import os

X = 1

def login(user, pw):
    """check creds"""
    return user == "a" and pw == "b"

class Auth:
    def verify(self, token):
        return bool(token)
'''


def test_python_splits_on_functions_and_classes():
    chunks = chunk_file("auth.py", PY)
    kinds = {(c.kind, c.name) for c in chunks}
    assert ("function", "login") in kinds
    assert ("class", "Auth") in kinds
    login = next(c for c in chunks if c.name == "login")
    assert login.start_line == 5 and "return user" in login.text


def test_line_numbers_are_valid():
    for c in chunk_file("auth.py", PY):
        assert 1 <= c.start_line <= c.end_line <= len(PY.splitlines())


def test_non_python_uses_windows():
    text = "\n".join(f"line {i}" for i in range(1, 200))
    chunks = chunk_file("app.js", text)
    assert len(chunks) >= 3
    assert chunks[0].start_line == 1 and chunks[-1].end_line == 199


def test_syntax_error_falls_back():
    assert chunk_file("bad.py", "def (:\n  x = ") != []
