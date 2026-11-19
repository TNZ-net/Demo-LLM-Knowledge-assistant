# attention.py: one attention head language model
import torch, torch.nn as nn, torch.nn.functional as F
from tokenizer import text, chars, encode, decode

torch.manual_seed(0)
V = len(chars)
data = torch.tensor(encode(text))
n = int(0.9 * len(data))
train_data, val_data = data[:n], data[n:]     

B, T, C = 32, 8, 32      

def get_batch(d):
    ix = torch.randint(len(d) - T, (B,))
    x = torch.stack([d[i:i+T] for i in ix])            
    y = torch.stack([d[i+1:i+T+1] for i in ix])         
    return x, y

class Head(nn.Module):
    def __init__(self):
        super().__init__()
        self.key = nn.Linear(C, C, bias=False)
        self.query = nn.Linear(C, C, bias=False)
        self.value = nn.Linear(C, C, bias=False)
        self.register_buffer("mask", torch.tril(torch.ones(T, T)))   
    def forward(self, x):
        Tx = x.shape[1]
        k, q, v = self.key(x), self.query(x), self.value(x)
        scores = q @ k.transpose(-2, -1) / (C ** 0.5)#(B, T, T) relevance
        scores = scores.masked_fill(self.mask[:Tx, :Tx] == 0, float("-inf"))   
        w = F.softmax(scores, dim=-1)                                
        return w @ v                                                

class TinyAttn(nn.Module):
    def __init__(self):
        super().__init__()
        self.tok = nn.Embedding(V, C)
        self.pos = nn.Embedding(T, C)
        self.head = Head()
        self.out = nn.Linear(C, V)
    def forward(self, x):
        h = self.tok(x) + self.pos(torch.arange(x.shape[1]))  #what + where
        return self.out(self.head(h)) #(B, T, V) logits

model = TinyAttn()
opt = torch.optim.AdamW(model.parameters(), lr=3e-3)

def loss_on(d, batches=20):
    with torch.no_grad():
        ls = []
        for _ in range(batches):
            x, y = get_batch(d)
            ls.append(F.cross_entropy(model(x).view(-1, V), y.view(-1)).item())
    return sum(ls) / len(ls)

@torch.no_grad()
def generate(start, length):
    ids = encode(start)
    for _ in range(length):
        ctx = torch.tensor([ids[-T:]]) #last T characters only
        probs = F.softmax(model(ctx)[0, -1], dim=-1)
        ids.append(torch.multinomial(probs, 1).item())
    return decode(ids)

if __name__ == "__main__":
    for step in range(2001):
        x, y = get_batch(train_data)
        loss = F.cross_entropy(model(x).view(-1, V), y.view(-1))
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 500 == 0:
            print(step, "train:", round(loss_on(train_data), 3), "val:", round(loss_on(val_data), 3))
    print(generate("t", 200))

    x = val_data[:T].unsqueeze(0)
    x2 = x.clone(); x2[0, -1] = (x2[0, -1] + 1) % V
    with torch.no_grad():
        a, b = model(x), model(x2)
    print("past unaffected by future:", torch.allclose(a[0, :-1], b[0, :-1]))