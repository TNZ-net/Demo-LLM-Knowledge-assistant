import json, uuid
from sqlalchemy import text
from db import engine
from retrieve import search
from rag import MIN_SIMILARITY

def evaluate(path: str = "eval_set.json", k: int = 3) -> list[dict]:
    cases = json.load(open(path, encoding="utf-8"))
    rows = []
    for c in cases:
        found = search(c["question"], k)
        top = found[0]["similarity"] if found else 0.0
        kept = [h for h in found if h["similarity"] >= MIN_SIMILARITY]
        kw = c["expect_keyword"]
        if kw is None:                                  
            passed = len(kept) == 0
        else:                                            
            passed = any(kw.lower() in h["content"].lower() for h in kept)
        rows.append({"question": c["question"], "answerable": kw is not None,
                     "top": top, "passed": passed})
    return rows

def save(rows: list[dict]) -> str:
    run_id = uuid.uuid4().hex[:8]
    with engine.begin() as conn:
        for r in rows:
            conn.execute(
                text("INSERT INTO eval_results (run_id, question, answerable, top_similarity, passed) "
                     "VALUES (:r, :q, :a, :t, :p)"),
                {"r": run_id, "q": r["question"], "a": r["answerable"],
                 "t": r["top"], "p": r["passed"]},
            )
    return run_id

if __name__ == "__main__":
    rows = evaluate()
    for r in rows:
        print("PASS" if r["passed"] else "FAIL", f"{r['top']:.3f}", r["question"][:60])
    ans = [r for r in rows if r["answerable"]]
    una = [r for r in rows if not r["answerable"]]
    print(f"hit rate (answerable): {sum(r['passed'] for r in ans)}/{len(ans)}")
    print(f"correct refusals     : {sum(r['passed'] for r in una)}/{len(una)}")
    print("saved run:", save(rows))