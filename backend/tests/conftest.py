import sys, os, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

def make_app(tmp_path=None):
    from app import create_app
    if tmp_path is None:
        tmp_path = tempfile.mktemp(suffix=".db")
    return create_app(config={
        "DB_PATH": tmp_path,
        "JWT_SECRET": "test-secret-key-32-chars-long-ok",
        "TESTING": True,
    })
