import sys
from sqlalchemy import text
from db import engine
from chunker import chunk_text
from embed_demo import model        

def to_pgvector(vec) -> str:
    return "[" + ",".join(str(float(x)) for x in vec) + "]"

def ingest(source_url: str, content: str) -> int:
    chunks = chunk_text(content)
    if not chunks:
        return 0
    vecs = model.encode(chunks, normalize_embeddings=True)  
    with engine.begin() as conn:                            
        conn.execute(text("DELETE FROM chunks WHERE source_url = :s"), {"s": source_url})
        for chunk, vec in zip(chunks, vecs):
            conn.execute(
                text("INSERT INTO chunks (source_url, content, embedding) "
                     "VALUES (:s, :c, CAST(:e AS vector))"),
                {"s": source_url, "c": chunk, "e": to_pgvector(vec)},
            )
    return len(chunks)

if __name__ == "__main__":
    path = sys.argv[1]
    n = ingest(source_url=path, content=open(path, encoding="utf-8").read())
    print("stored chunks:", n)