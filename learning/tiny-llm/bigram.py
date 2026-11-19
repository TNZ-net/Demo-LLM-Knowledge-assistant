import numpy as np
from tokenizer import text, chars, encode, decode

V = len(chars)
ids = encode(text)

N = np.zeros((V, V))                       
for a, b in zip(ids[:-1], ids[1:]):        
    N[a, b] += 1

P = (N + 1) / (N + 1).sum(axis=1, keepdims=True)  

def generate(start: str, length: int, seed: int = 0) -> str:
    rng = np.random.default_rng(seed)
    out = [encode(start)[0]]
    for _ in range(length):
        nxt = rng.choice(V, p=P[out[-1]])  
        out.append(int(nxt))
    return decode(out)

if __name__ == "__main__":
    print("row sums all 1:", np.allclose(P.sum(axis=1), 1))
    print(generate("t", 200))
    loss = -np.mean([np.log(P[a, b]) for a, b in zip(ids[:-1], ids[1:])])
    print("average loss:", round(float(loss), 3))
    print("random-guess loss would be:", round(float(np.log(V)), 3))