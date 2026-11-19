import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")  

sentences = [
    "How do I reset my password?",
    "I forgot my login credentials.",
    "What is the capital of France?",
]
vecs = model.encode(sentences, normalize_embeddings=True) 

def cosine(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

if __name__ == "__main__":
    print("shape:", vecs.shape)
    print("first 5 numbers:", vecs[0][:5])
    print("password vs login :", round(cosine(vecs[0], vecs[1]), 3))
    print("password vs France:", round(cosine(vecs[0], vecs[2]), 3))