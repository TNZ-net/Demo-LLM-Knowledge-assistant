import torch
import torch.nn as nn
import torch.nn.functional as F
from tokenizer import text, chars, encode

torch.manual_seed(0)                      
V = len(chars)
data = torch.tensor(encode(text))         

x = data[:-1]                             
y = data[1:]                              

class BigramNN(nn.Module):
    def __init__(self, V):
        super().__init__()
        self.table = nn.Embedding(V, V)   
    def forward(self, x):
        return self.table(x)              

model = BigramNN(V)
logits = model(x)
loss = F.cross_entropy(logits, y)         

if __name__ == "__main__":
    print("x shape:", x.shape, " logits shape:", logits.shape)
    print("initial loss:", round(loss.item(), 3), " log(V):", round(float(torch.log(torch.tensor(float(V)))), 3))
    probs = F.softmax(logits, dim=1)
    print("row sums to 1:", torch.allclose(probs.sum(dim=1), torch.ones(len(x))))
    manual = -torch.log(probs[torch.arange(len(y)), y]).mean()
    print("manual loss:", round(manual.item(), 3))