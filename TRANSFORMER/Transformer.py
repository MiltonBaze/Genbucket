import os
import sys
import json
import torch
import torch.nn as nn
from torch.nn import functional as F

# === Verifica se o caminho do dataset foi passado ===
if len(sys.argv) < 2:
    print("❌ Caminho do dataset não informado.")
    sys.exit(1)

dataset_path = sys.argv[1]

if not os.path.exists(dataset_path):
    print(f"❌ Arquivo de dataset '{dataset_path}' não encontrado.")
    sys.exit(1)

# === Carrega config.json ===
script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, 'config.json')

if not os.path.exists(config_path):
    print("❌ Arquivo 'config.json' não encontrado.")
    sys.exit(1)

with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

# === Hiperparâmetros ===
batch_size = config.get("batch_size", 128)
block_size = config.get("block_size", 128)
max_iters = config.get("max_iters", 5000)
eval_interval = config.get("eval_interval", 500)
learning_rate = config.get("learning_rate", 1e-4)
eval_iters = config.get("eval_iters", 200)
n_embd = config.get("n_embd", 128)
n_head = config.get("n_head", 6)
n_layer = config.get("n_layer", 4)
dropout = config.get("dropout", 0.3)
num_buckets = config.get("num_buckets", 100000)
buckets_per_file = config.get("buckets_per_file", 10000)

device = 'cuda' if torch.cuda.is_available() else 'cpu'
torch.manual_seed(1337)

# === Carrega dataset ===
with open(dataset_path, 'r', encoding='utf-8') as f:
    text = f.read()

# === Tokenização ===
chars = sorted(list(set(text)))
stoi = {ch: i for i, ch in enumerate(chars)}
itos = {i: ch for ch, i in stoi.items()}
vocab_size = len(chars)

encode = lambda s: [stoi[c] for c in s if c in stoi]
decode = lambda l: ''.join([itos[i] for i in l])

data = torch.tensor(encode(text), dtype=torch.long)
n = int(0.9 * len(data))
train_data = data[:n]
val_data = data[n:]

def get_batch(split):
    data_split = train_data if split == 'train' else val_data
    ix = torch.randint(len(data_split) - block_size, (batch_size,))
    x = torch.stack([data_split[i:i+block_size] for i in ix])
    y = torch.stack([data_split[i+1:i+block_size+1] for i in ix])
    return x.to(device), y.to(device)

@torch.no_grad()
def estimate_loss():
    out = {}
    model.eval()
    for split in ['train', 'val']:
        losses = torch.zeros(eval_iters)
        for k in range(eval_iters):
            X, Y = get_batch(split)
            _, loss = model(X, Y)
            losses[k] = loss.item()
        out[split] = losses.mean()
    model.train()
    return out

# === Modelo Transformer ===
class Head(nn.Module):
    def __init__(self, head_size):
        super().__init__()
        self.key = nn.Linear(n_embd, head_size, bias=False)
        self.query = nn.Linear(n_embd, head_size, bias=False)
        self.value = nn.Linear(n_embd, head_size, bias=False)
        self.register_buffer('tril', torch.tril(torch.ones(block_size, block_size)))
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        B, T, C = x.shape
        k = self.key(x)
        q = self.query(x)
        wei = q @ k.transpose(-2, -1) / (C ** 0.5)
        wei = wei.masked_fill(self.tril[:T, :T] == 0, float('-inf'))
        wei = F.softmax(wei, dim=-1)
        v = self.value(x)
        return self.dropout(wei) @ v

class MultiHeadAttention(nn.Module):
    def __init__(self, num_heads, head_size):
        super().__init__()
        self.heads = nn.ModuleList([Head(head_size) for _ in range(num_heads)])
        self.proj = nn.Linear(num_heads * head_size, n_embd)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        out = torch.cat([h(x) for h in self.heads], dim=-1)
        return self.dropout(self.proj(out))

class FeedForward(nn.Module):
    def __init__(self, n_embd):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_embd, 4 * n_embd),
            nn.ReLU(),
            nn.Linear(4 * n_embd, n_embd),
            nn.Dropout(dropout)
        )

    def forward(self, x):
        return self.net(x)

class Block(nn.Module):
    def __init__(self, n_embd, n_head):
        super().__init__()
        head_size = n_embd // n_head
        self.sa = MultiHeadAttention(n_head, head_size)
        self.ffwd = FeedForward(n_embd)
        self.ln1 = nn.LayerNorm(n_embd)
        self.ln2 = nn.LayerNorm(n_embd)

    def forward(self, x):
        x = x + self.sa(self.ln1(x))
        return x + self.ffwd(self.ln2(x))

class GPTLanguageModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.token_embedding_table = nn.Embedding(vocab_size, n_embd)
        self.position_embedding_table = nn.Embedding(block_size, n_embd)
        self.blocks = nn.Sequential(*[Block(n_embd, n_head) for _ in range(n_layer)])
        self.ln_f = nn.LayerNorm(n_embd)
        self.lm_head = nn.Linear(n_embd, vocab_size)
        self.apply(self._init_weights)

    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def forward(self, idx, targets=None):
        B, T = idx.shape
        tok_emb = self.token_embedding_table(idx)
        pos_emb = self.position_embedding_table(torch.arange(T, device=device))
        x = tok_emb + pos_emb
        x = self.blocks(x)
        x = self.ln_f(x)
        logits = self.lm_head(x)
        loss = None
        if targets is not None:
            loss = F.cross_entropy(logits.view(-1, logits.size(-1)), targets.view(-1))
        return logits, loss

    def generate(self, idx, max_new_tokens):
        for _ in range(max_new_tokens):
            idx_cond = idx[:, -block_size:]
            logits, _ = self(idx_cond)
            logits = logits[:, -1, :]
            probs = F.softmax(logits, dim=-1)
            idx_next = torch.multinomial(probs, num_samples=1)
            idx = torch.cat((idx, idx_next), dim=1)
        return idx

# === Treinamento ===
model = GPTLanguageModel().to(device)
optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)

for iter in range(max_iters):
    if iter % eval_interval == 0:
        losses = estimate_loss()
        print(f"Step {iter}: Train Loss {losses['train']:.4f}, Val Loss {losses['val']:.4f}")
    xb, yb = get_batch('train')
    logits, loss = model(xb, yb)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

# === Geração das fases ===
prompt_base_dir = os.path.join(script_dir, "prompt")
os.makedirs(prompt_base_dir, exist_ok=True)

context = torch.zeros((1, 1), dtype=torch.long, device=device)
nomes_unicos = set(text.split())

print("\n Iniciando geração dos nomes...")

for fase in range(1, 11):
    fase_dir = os.path.join(prompt_base_dir, f'V_{fase}')
    os.makedirs(fase_dir, exist_ok=True)

    saida_arquivo = os.path.join(fase_dir, f'Saida{fase}.txt')
    saida_filtrada_arquivo = os.path.join(fase_dir, f'Saida{fase}_Filtrado.txt')

    nomes_fase = []

    print(f" Fase {fase}: gerando {buckets_per_file} nomes únicos...")

    with open(saida_arquivo, 'w', encoding='utf-8') as arq, open(saida_filtrada_arquivo, 'w', encoding='utf-8') as arq_filtrado:
        while len(nomes_fase) < buckets_per_file:
            output = decode(model.generate(context, max_new_tokens=50)[0].tolist())
            for nome in output.split():
                clean = ''.join(filter(str.isalnum, nome)).lower()
                if clean and clean not in nomes_unicos:
                    nomes_unicos.add(clean)
                    nomes_fase.append(clean)
                    arq.write(clean + '\n')
                    arq_filtrado.write(clean + '\n')
                if len(nomes_fase) >= buckets_per_file:
                    break

print("✅ Geração concluída.")
