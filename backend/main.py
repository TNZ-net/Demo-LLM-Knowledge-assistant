# main.py
from fastapi import FastAPI,HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from db import engine
from fastapi.middleware.cors import CORSMiddleware
from security import hash_password
from retrieve import search
import time

import jwt
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from security import verify_password, create_token, decode_token
from rag import answer as rag_answer

from fastapi.responses import StreamingResponse
from rag import answer_stream
from ratelimit import allow, r as redis_client

# Declares the JSON shape the client must send: {"question": "..."}
class AskRequest(BaseModel):
    question: str = Field(min_length=1)

# Creates the application object that uvicorn will run
app = FastAPI(title="Knowledge Assistant API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],   # only our UI, not "*"
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Sources", "X-Question-Id"],
)

bearer = HTTPBearer()
def current_user_id(creds: HTTPAuthorizationCredentials = Depends(bearer)) -> int:
    try:
        return decode_token(creds.credentials)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

def rate_limited_user(user_id: int = Depends(current_user_id)) -> int:
    if not allow(user_id):
        try:
            wait = max(redis_client.ttl(f"rate:user:{user_id}"), 1)
        except Exception:
            wait = 60
        raise HTTPException(status_code=429,
                            detail="Too many questions, please wait a moment",
                            headers={"Retry-After": str(wait)})
    return user_id

# When someone sends GET /health, run this function
@app.get("/health")
def health():
    # FastAPI converts this dict to JSON automatically
    return {"status": "ok", "version": "0.1.0"}

@app.post("/ask")
def ask(body: AskRequest, user_id: int = Depends(rate_limited_user)):
    try:
        text_answer, hits = rag_answer(body.question)
    except RuntimeError:                              # Ollama unreachable
        raise HTTPException(status_code=503, detail="The language model is unavailable")
    sources = sorted({h["source"] for h in hits})
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO questions (user_id, question, answer, sources) "
                 "VALUES (:u, :q, :a, :s)"),
            {"u": user_id, "q": body.question, "a": text_answer, "s": sources},
        )
    return {"answer": text_answer, "sources": sources}

MIN_SIMILARITY = 0.3          # tune in Phase 8

class SearchRequest(BaseModel):
    question: str = Field(min_length=1)
    k: int = Field(default=3, ge=1, le=10)

@app.post("/search")
def search_chunks(body: SearchRequest, user_id: int = Depends(current_user_id)):
    hits = search(body.question, body.k)
    return [h for h in hits if h["similarity"] >= MIN_SIMILARITY]


class UserCreate(BaseModel):
    email: str = Field(min_length=3)

class RegisterRequest(BaseModel):
    email: str = Field(min_length= 3)
    password: str = Field(min_length= 3)

@app.post("/register", status_code=201)
def register(body: RegisterRequest):
    try:
        with engine.begin() as conn:
            row = conn.execute(
                text("INSERT INTO users (email, password_hash) "
                    "VALUES (:email, :ph) RETURNING id, email"),
                {"email": body.email, "ph": hash_password(body.password)},
            ).one()
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Email already registered")
    return {"id": row.id, "email": row.email}   # never return the hash

@app.post("/ask/stream")
def ask_stream(body: AskRequest, user_id: int = Depends(rate_limited_user)):
    t0 = time.perf_counter()
    tokens, hits, top = answer_stream(body.question)
    sources = sorted({h["source"] for h in hits})
    with engine.begin() as conn:                     # create the row up front
        qid = conn.execute(
            text("INSERT INTO questions (user_id, question, sources, top_similarity, "
                 "chunks_used, refused) VALUES (:u, :q, :s, :t, :c, :r) RETURNING id"),
            {"u": user_id, "q": body.question, "s": sources, "t": top,
             "c": len(hits), "r": len(hits) == 0},
        ).scalar_one()

    def generate():
        parts, first = [], None
        try:
            for t in tokens:
                if first is None:
                    first = int((time.perf_counter() - t0) * 1000)
                parts.append(t)
                yield t
        except RuntimeError:
            yield "\n[The language model is unavailable]"
            return
        total = int((time.perf_counter() - t0) * 1000)
        with engine.begin() as conn:
            conn.execute(
                text("UPDATE questions SET answer = :a, latency_ms = :l, first_token_ms = :f "
                     "WHERE id = :id"),
                {"a": "".join(parts), "l": total, "f": first, "id": qid},
            )

    return StreamingResponse(generate(), media_type="text/plain",
                             headers={"X-Sources": ",".join(sources),
                                      "X-Question-Id": str(qid)})

class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/login")
def login(body: LoginRequest):
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT id, password_hash FROM users WHERE email = :e"),
            {"e": body.email},
        ).one_or_none()
    if row is None or row.password_hash is None or not verify_password(body.password, row.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"access_token": create_token(row.id), "token_type": "bearer"}

@app.get("/me")
def me(user_id: int = Depends(current_user_id)):
    return {"user_id": user_id}

class FeedbackRequest(BaseModel):
    value: int = Field(ge=-1, le=1)

@app.patch("/questions/{qid}/feedback")
def set_feedback(qid: int, body: FeedbackRequest, user_id: int = Depends(current_user_id)):
    if body.value == 0:
        raise HTTPException(status_code=422, detail="value must be 1 or -1")
    with engine.begin() as conn:
        n = conn.execute(
            text("UPDATE questions SET feedback = :v WHERE id = :id AND user_id = :u"),
            {"v": body.value, "id": qid, "u": user_id},
        ).rowcount
    if n == 0:
        raise HTTPException(status_code=404, detail="Question not found")
    return {"ok": True}
