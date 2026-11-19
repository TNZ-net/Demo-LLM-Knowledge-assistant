# train.py: train the neural bigram (learning example)
import torch
import torch.nn.functional as F
from neural_bigram import model, x, y
from tokenizer import encode, decode

optimizer = torch.optim.AdamW(model.parameters(), lr=0.1)

for step in range(301):
    logits = model(x)                       # 1. forward: make predictions
    loss = F.cross_entropy(logits, y)       # 2. measure how wrong
    optimizer.zero_grad()                   # 3. clear old gradients
    loss.backward()                         # 4. backprop: compute gradients
    optimizer.step()                        # 5. nudge parameters downhill
    if step % 50 == 0:
        print(step, round(loss.item(), 3))

@torch.no_grad()                            # no gradients needed when generating
def generate(start: str, length: int) -> str:
    ids = [encode(start)[0]]
    for _ in range(length):
        probs = F.softmax(model(torch.tensor([ids[-1]])), dim=1)
        ids.append(torch.multinomial(probs, 1).item())   # sample next token
    return decode(ids)

print(generate("t", 200))