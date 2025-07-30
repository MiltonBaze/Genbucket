import os
import json
import torch
import torch.nn as nn
import torch.nn.functional as F

from torch.nn import functional as F
from models.base_model import BaseModel

class Head(nn.Module):
    def __init__(self, n_embd, head_size, dropout, block_size):
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
    def __init__(self, n_embd, n_head, dropout, block_size):
        super().__init__()
        head_size = n_embd // n_head
        self.heads = nn.ModuleList([Head(n_embd, head_size, dropout, block_size) for _ in range(n_head)])
        self.proj = nn.Linear(n_head * head_size, n_embd)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        out = torch.cat([h(x) for h in self.heads], dim=-1)
        return self.dropout(self.proj(out))

class FeedForward(nn.Module):
    def __init__(self, n_embd, dropout):
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
    def __init__(self, n_embd, n_head, dropout, block_size):
        super().__init__()
        self.sa = MultiHeadAttention(n_embd, n_head, dropout, block_size)
        self.ffwd = FeedForward(n_embd, dropout)
        self.ln1 = nn.LayerNorm(n_embd)
        self.ln2 = nn.LayerNorm(n_embd)

    def forward(self, x):
        x = x + self.sa(self.ln1(x))
        return x + self.ffwd(self.ln2(x))

class GPTLanguageModel(nn.Module):
    def __init__(self, vocab_size, n_embd, n_head, n_layer, dropout, block_size):
        super().__init__()
        self.token_embedding_table = nn.Embedding(vocab_size, n_embd)
        self.position_embedding_table = nn.Embedding(block_size, n_embd)
        self.blocks = nn.Sequential(*[Block(n_embd, n_head, dropout, block_size) for _ in range(n_layer)])
        self.ln_f = nn.LayerNorm(n_embd)
        self.lm_head = nn.Linear(n_embd, vocab_size)
        self.block_size = block_size
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
        pos_emb = self.position_embedding_table(torch.arange(T, device=idx.device))
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
            idx_cond = idx[:, -self.block_size:]
            logits, _ = self(idx_cond)
            logits = logits[:, -1, :]
            probs = F.softmax(logits, dim=-1)
            idx_next = torch.multinomial(probs, num_samples=1)
            idx = torch.cat((idx, idx_next), dim=1)
        return idx

class TransformerModel:
    def __init__(self, config: dict):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.config = config
        self.model = None
        self.chars = None
        self.stoi = None
        self.itos = None
        self.train_data = None
        self.val_data = None

    def fit(self, dataset_path: str):
        with open(dataset_path, 'r', encoding='utf-8') as f:
            text = f.read()
        self.chars = sorted(list(set(text)))
        self.stoi = {ch: i for i, ch in enumerate(self.chars)}
        self.itos = {i: ch for i, ch in enumerate(self.chars)}

        encode = lambda s: [self.stoi[c] for c in s if c in self.stoi]
        data = torch.tensor(encode(text), dtype=torch.long)
        n = int(0.9 * len(data))
        self.train_data = data[:n]
        self.val_data = data[n:]

        batch_size = self.config.get("batch_size", 128)
        block_size = self.config.get("block_size", 32)
        max_iters = self.config.get("max_iters", 5000)
        eval_interval = self.config.get("eval_interval", 500)
        learning_rate = self.config.get("learning_rate", 1e-4)
        eval_iters = self.config.get("eval_iters", 200)
        n_embd = self.config.get("n_embd", 128)
        n_head = self.config.get("n_head", 6)
        n_layer = self.config.get("n_layer", 4)
        dropout = self.config.get("dropout", 0.3)

        self.model = GPTLanguageModel(len(self.chars), n_embd, n_head, n_layer, dropout, block_size).to(self.device)
        optimizer = torch.optim.AdamW(self.model.parameters(), lr=learning_rate)

        def get_batch(split):
            data_split = self.train_data if split == 'train' else self.val_data
            ix = torch.randint(len(data_split) - block_size, (batch_size,))
            x = torch.stack([data_split[i:i + block_size] for i in ix])
            y = torch.stack([data_split[i + 1:i + block_size + 1] for i in ix])
            return x.to(self.device), y.to(self.device)

        @torch.no_grad()
        def estimate_loss():
            out = {}
            self.model.eval()
            for split in ['train', 'val']:
                losses = torch.zeros(eval_iters)
                for k in range(eval_iters):
                    X, Y = get_batch(split)
                    _, loss = self.model(X, Y)
                    losses[k] = loss.item()
                out[split] = losses.mean()
            self.model.train()
            return out

        for iter in range(max_iters):
            if iter % eval_interval == 0:
                losses = estimate_loss()
                print(f"Step {iter}: Train Loss {losses['train']:.4f}, Val Loss {losses['val']:.4f}")
            xb, yb = get_batch('train')
            logits, loss = self.model(xb, yb)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        output_dir = self.config.get("output_dir", "Resultados/transformer/modelo_Treinado")
        os.makedirs(output_dir, exist_ok=True)
        torch.save(self.model.state_dict(), os.path.join(output_dir, "transformer_model.pth"))
        with open(os.path.join(output_dir, "vocab.json"), "w", encoding="utf-8") as f:
            json.dump({
                "chars": self.chars,
                "stoi": self.stoi,
                "itos": {str(k): v for k, v in self.itos.items()}
            }, f)

    def predict(self, prompt: str, num_tokens=30):
        if self.model is None:
            output_dir = self.config.get("output_dir", "Result/transformer/modelo_Treinado")
            with open(os.path.join(output_dir, "vocab.json"), "r", encoding="utf-8") as f:
                vocab = json.load(f)
                self.chars = vocab["chars"]
                self.stoi = vocab["stoi"]
                self.itos = {int(k): v for k, v in vocab["itos"].items()}  

            n_embd = self.config.get("n_embd", 128)
            n_head = self.config.get("n_head", 6)
            n_layer = self.config.get("n_layer", 4)
            dropout = self.config.get("dropout", 0.3)
            block_size = self.config.get("block_size", 128)
            self.model = GPTLanguageModel(len(self.chars), n_embd, n_head, n_layer, dropout, block_size).to(self.device)
            self.model.load_state_dict(torch.load(os.path.join(output_dir, "transformer_model.pth"), map_location=self.device))
            self.model.eval()

        encoded_prompt = torch.tensor([self.stoi.get(c, 0) for c in prompt], dtype=torch.long, device=self.device).unsqueeze(0)
        with torch.no_grad():
            output_idx = self.model.generate(encoded_prompt, max_new_tokens=num_tokens)[0].tolist()

        generated_text = ''.join([self.itos.get(i, '') for i in output_idx])
        return [generated_text]
