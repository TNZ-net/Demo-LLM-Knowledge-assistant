from fastapi.testclient import TestClient
from main import app          
from sqlalchemy import text
from db import engine
import uuid
from sqlalchemy import text
from db import engine
from security import create_token
from cleaner import clean_html
from chunker import chunk_text
from run_ingest import load_sources
from rag import answer, NO_ANSWER
from unittest.mock import patch

client = TestClient(app)      

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_ask_valid():
    uid, token = make_user()
    try:
        r = client.post("/ask", json={"question": "What is RAG?"}, headers=auth(token))
        assert r.status_code == 200
    finally:
        delete_user(uid)

def test_ask_empty_question_rejected():
    uid, token = make_user()
    try:
        r = client.post("/ask", json={"question": ""}, headers=auth(token))
        assert r.status_code == 422
    finally:
        delete_user(uid)

def make_user():
    email = f"test-{uuid.uuid4().hex[:8]}@example.com"
    with engine.begin() as conn:
        uid = conn.execute(
            text("INSERT INTO users (email) VALUES (:e) RETURNING id"), {"e": email}
        ).scalar_one()
    return uid, create_token(uid)

def delete_user(uid):
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM questions WHERE user_id = :u"), {"u": uid})
        conn.execute(text("DELETE FROM users WHERE id = :u"), {"u": uid})

def auth(token):
    return {"Authorization": f"Bearer {token}"}

def test_ask_requires_token():
    r = client.post("/ask", json={"question": "hi"})
    assert r.status_code in (401, 403)

def test_ask_saves_question():
    uid, token = make_user()
    try:
        r = client.post("/ask", json={"question": "What is RAG?"}, headers=auth(token))
        assert r.status_code == 200
        with engine.connect() as conn:
            n = conn.execute(
                text("SELECT count(*) FROM questions WHERE user_id = :u"), {"u": uid}
            ).scalar_one()
        assert n == 1
    finally:
        delete_user(uid)

def test_search_requires_token():
    r = client.post("/search", json={"question": "what does a language model do"})
    assert r.status_code in (401, 403)

def test_search_relevant_returns_hits():
    uid, token = make_user()
    try:
        r = client.post(
            "/search",
            json={"question": "what does a language model do"},
            headers=auth(token),
        )
        assert r.status_code == 200
        assert len(r.json()) > 0          # needs chunks ingested (5.4)
    finally:
        delete_user(uid)

def test_search_bad_k_rejected():
    uid, token = make_user()
    try:
        for bad_k in (0, 50):
            r = client.post("/search", json={"question": "x", "k": bad_k}, headers=auth(token))
            assert r.status_code == 422
    finally:
        delete_user(uid)

def test_clean_html_removes_scripts():
    assert clean_html("<p>Hi</p><script>alert(1)</script>") == "Hi"

def test_chunker_edge_cases():
    assert chunk_text("") == []
    assert chunk_text("hello") == ["hello"]

def test_load_sources_skips_comments(tmp_path):
    f = tmp_path / "s.txt"
    f.write_text("# comment\n\nhttps://a.example/\n", encoding="utf-8")
    assert load_sources(str(f)) == ["https://a.example/"]

def test_irrelevant_question_is_refused():
    text, sources = answer("best recipe for pancakes")
    assert text == NO_ANSWER
    assert sources == []

def test_ask_stream_returns_tokens():
    uid, token = make_user()
    try:
        with patch("main.answer_stream", return_value=(iter(["a","b"]), [], 0.9)):
            r = client.post("/ask/stream", json={"question": "hi"}, headers=auth(token))
        assert r.status_code == 200
        assert r.text == "ab"
    finally:
        delete_user(uid)

def test_eval_set_is_well_formed():
    import json
    cases = json.load(open("eval_set.json", encoding="utf-8"))
    assert len(cases) >= 10
    assert any(c["expect_keyword"] is None for c in cases)
    assert all("question" in c for c in cases)