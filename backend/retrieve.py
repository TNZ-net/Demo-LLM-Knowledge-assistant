import sys
from sqlalchemy import text
from db import engine
from embed_demo import model
from ingest import to_pgvector

def search(question: str, k: int = 3) -> list[dict]:
    qvec = model.encode([question], normalize_embeddings=True)[0]
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT source_url, content, embedding <=> CAST(:q AS vector) AS distance "
                 "FROM chunks ORDER BY distance LIMIT :k"),
            {"q": to_pgvector(qvec), "k": k},
        ).all()
    return [{"source": r.source_url, "content": r.content,
             "similarity": round(1 - r.distance, 3)} for r in rows]

if __name__ == "__main__":
    for hit in search(" ".join(sys.argv[1:])):
        print(hit["similarity"], hit["content"][:100].replace("\n", " "))