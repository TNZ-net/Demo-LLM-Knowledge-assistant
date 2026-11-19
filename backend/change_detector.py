import hashlib
from sqlalchemy import text
from db import engine

def content_hash(cleaned: str) -> str:
    return hashlib.sha256(cleaned.encode("utf-8")).hexdigest()

def has_changed(url: str, cleaned: str) -> bool:
    with engine.connect() as conn:
        old = conn.execute(
            text("SELECT content_hash FROM sources WHERE url = :u"), {"u": url}
        ).scalar_one_or_none()
    return old != content_hash(cleaned)    

def record(url: str, cleaned: str) -> None:
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO sources (url, content_hash) VALUES (:u, :h) "
                 "ON CONFLICT (url) DO UPDATE "
                 "SET content_hash = :h, last_checked = now()"),
            {"u": url, "h": content_hash(cleaned)},
        )

if __name__ == "__main__":
    url = "test://demo"
    print("first time  :", has_changed(url, "hello world"))     # expect True
    record(url, "hello world")
    print("same text   :", has_changed(url, "hello world"))     # expect False
    print("one char off:", has_changed(url, "hello World"))     # expect True
    with engine.begin() as conn:                                # clean up the demo row
        conn.execute(text("DELETE FROM sources WHERE url = :u"), {"u": url})