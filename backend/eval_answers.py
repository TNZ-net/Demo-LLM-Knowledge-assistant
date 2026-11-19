import uuid
from sqlalchemy import text
from db import engine
from rag import answer

CASES = [
    ("Who said the world is a process of our thinking?", "answerable"),
    ("What did Edison say about failure?", "answerable"),
    ("Which quote says being ridiculous is better than being boring?", "answerable"),
    ("What helps people organize information and complete tasks?", "answerable"),
    ("What is Einstein's birthday?", "not_in_text"),
    ("How old was Edison when he died?", "not_in_text"),
    ("best recipe for pancakes", "off_topic"),
    ("what is the capital of Japan", "off_topic"),
]

run_id = uuid.uuid4().hex[:8]
for question, ctype in CASES:
    ans, hits = answer(question)
    print("\n" + "=" * 70)
    print(f"[{ctype}] {question}")
    for i, h in enumerate(hits):
        print(f"  context [{i+1}]: {h['content'][:200]}...")
    print(f"ANSWER: {ans}")
    ok = input("Faithful? (y = only uses the context or correctly refuses, n = invents) ").strip().lower() == "y"
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO eval_answers (run_id, question, case_type, answer, faithful) "
                 "VALUES (:r, :q, :c, :a, :f)"),
            {"r": run_id, "q": question, "c": ctype, "a": ans, "f": ok},
        )

with engine.connect() as conn:
    rows = conn.execute(
        text("SELECT case_type, count(*), sum(faithful::int) FROM eval_answers "
             "WHERE run_id = :r GROUP BY case_type"), {"r": run_id}).all()
print("\nrun", run_id)
for r in rows:
    print(f"{r.case_type:12} faithful {r[2]}/{r[1]}")