text = open("data.txt", encoding="utf-8").read()

chars = sorted(set(text))                      # every distinct character, in order
stoi = {c: i for i, c in enumerate(chars)}     # character -> id
itos = {i: c for c, i in stoi.items()}         # id -> character

def encode(s: str) -> list[int]:
    return [stoi[c] for c in s]

def decode(ids: list[int]) -> str:
    return "".join(itos[i] for i in ids)

if __name__ == "__main__":
    print("characters in text:", len(text))
    print("vocab size:", len(chars))
    print(chars)
    print(encode("hello"))
    print(decode(encode("hello")))