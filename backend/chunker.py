def chunk_text(text: str, size: int = 500, overlap: int = 100) -> list[str]:
    if overlap >= size:
        raise ValueError("overlap must be smaller than size")
    text = " ".join(text.split())          
    chunks = []
    step = size - overlap                  
    for start in range(0, len(text), step):
        piece = text[start:start + size].strip()
        if piece:
            chunks.append(piece)
        if start + size >= len(text):    
            break
    return chunks

if __name__ == "__main__":
    sample = open("../learning/tiny-llm/data.txt", encoding="utf-8").read()
    cs = chunk_text(sample)
    print("chunks:", len(cs))
    print("lengths:", [len(c) for c in cs])
    print("first chunk:", cs[0])
    print("overlap shared:", cs[0][-100:] == cs[1][:100])