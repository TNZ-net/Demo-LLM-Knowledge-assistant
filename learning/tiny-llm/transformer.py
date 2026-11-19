import torch, torch.nn as nn, torch.nn.functional as F
from attention import Head, get_batch, train_data, val_data, V, C, T
from tokenizer import encode, decode

torch.manual_seed(0)

class Block(nn.Module):
    def __init__(self):
        super().__init__()
        self.ln1 = nn.LayerNorm(C)
        self.head = Head()                       
        self.ln2 = nn.LayerNorm(C)
        self.ff = nn.Sequential(
            nn.Linear(C, 4 * C), nn.ReLU(), nn.Linear(4 * C, C), nn.Dropout(0.2)
        )
    def forward(self, x):
        x = x + self.head(self.ln1(x))          
        x = x + self.ff(self.ln2(x)) #MLP + residual
        return x

class TinyTransformer(nn.Module):
    def __init__(self):
        super().__init__()
        self.tok = nn.Embedding(V, C)
        self.pos = nn.Embedding(T, C)
        self.blocks = nn.Sequential(Block(), Block())  
        self.ln = nn.LayerNorm(C)
        self.out = nn.Linear(C, V)
    def forward(self, x):
        h = self.tok(x) + self.pos(torch.arange(x.shape[1]))
        return self.out(self.ln(self.blocks(h)))

model = TinyTransformer()
opt = torch.optim.AdamW(model.parameters(), lr=3e-3)

def loss_on(d, batches=20):
    model.eval()           
    with torch.no_grad():
        ls = [F.cross_entropy(model(x).view(-1, V), y.view(-1)).item()
              for x, y in (get_batch(d) for _ in range(batches))]
    model.train()
    return sum(ls) / len(ls)

@torch.no_grad()
def generate(start, length):
    model.eval()
    ids = encode(start)
    for _ in range(length):
        probs = F.softmax(model(torch.tensor([ids[-T:]]))[0, -1], dim=-1)
        ids.append(torch.multinomial(probs, 1).item())
    model.train()
    return decode(ids)

if __name__ == "__main__":
    print("parameters:", sum(p.numel() for p in model.parameters()))
    for step in range(2001):
        x, y = get_batch(train_data)
        loss = F.cross_entropy(model(x).view(-1, V), y.view(-1))
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 500 == 0:
            print(step, "train:", round(loss_on(train_data), 3), "val:", round(loss_on(val_data), 3))
    print(generate("t", 200))