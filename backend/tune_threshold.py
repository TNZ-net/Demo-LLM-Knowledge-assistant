import json
from retrieve import search

cases = json.load(open("eval_set.json", encoding="utf-8"))
scored = []
for c in cases:
    found = search(c["question"], 3)
    scored.append((c, found))

print("threshold  wrongly_refused  wrongly_answered")
for th in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]:
    wrongly_refused = wrongly_answered = 0
    for c, found in scored:
        kept = [h for h in found if h["similarity"] >= th]
        kw = c["expect_keyword"]
        if kw is None and kept:
            wrongly_answered += 1
        if kw is not None and not any(kw.lower() in h["content"].lower() for h in kept):
            wrongly_refused += 1
    print(f"{th:<10} {wrongly_refused:<16} {wrongly_answered}")