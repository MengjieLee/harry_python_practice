'''
/bigram_v2.py
step(0): train loss 6.3928, val loss 6.3631
step(300): train loss 1.4620, val loss 7.3354
step(600): train loss 1.4322, val loss 7.6983
step(900): train loss 1.4204, val loss 7.8798
step(1200): train loss 1.4189, val loss 7.8799
step(1500): train loss 1.3994, val loss 7.8500
step(1800): train loss 1.3902, val loss 7.8606
step(2100): train loss 1.4002, val loss 7.8513
step(2400): train loss 1.3809, val loss 7.8428
step(2700): train loss 1.4017, val loss 7.8898
'''

from pyexpat import model
from turtle import forward
import torch
import torch.nn as nn
from torch.nn import functional as F


batch_size = 32
block_size = 8
max_iters = 3000
eval_interval = 300
learning_rate = 1e-2
device = 'cuda' if torch.cuda.is_available() else 'cpu'
eval_iters = 200
n_embd = 32

# ======== 固定随机种子，保证复现性 ========
torch.manual_seed(9527)


# ======== 数据源 ========
with open('input_cn.txt', 'r', encoding='utf-8') as f:
    text = f.read()
chars = sorted(list(set(text)))
vocab_size = len(chars)

# ======== 编码器，解码器 ========
stoi = { ch:i for i, ch in enumerate(chars)}
itos = { i:ch for i, ch in enumerate(chars)}
encode = lambda s: [stoi[ch] for ch in s] # encode: input a string, output a list of integers
decode = lambda l: ''.join([itos[i] for i in l]) # decode: input a list of integers, output a string

# ======== 训测集 ========
data = torch.tensor(encode(text), dtype=torch.long)
n = int(0.9 * len(data)) # first 90% will be train, rest val
train_data = data[:n]
val_data = data[n:]


# ======== 加载数据 ========
def get_batch(split):
    data = train_data if split == 'train' else val_data
    ix = torch.randint(len(data) - block_size, (batch_size,))
    x = torch.stack([data[i:i + block_size] for i in ix])
    y = torch.stack([data[i+1:i + block_size+1] for i in ix])
    x, y = x.to(device), y.to(device)
    return x, y


# ======== 计算损失 ========
@torch.no_grad() # 关闭梯度计算（节省显存 + 加速评估），类比边开车边记路线（算梯度）
def estimate_loss():
    out = {}
    model.eval() # 模型切到评估模式，避免训练特性干扰
    for split in ['train', 'val']: # 分别评估训练集（是否学会）和验证集（是否学废，过拟合）
        losses = torch.zeros(eval_iters) # 存储多批次的 loss
        for k in range(eval_iters): # 采样 eval_iters 个批次，类比判断学生的成绩：只看一次小测不可靠，看 10 次小测的平均分才更真实。
            X, Y = get_batch(split) # 获取该数据集的一个批次
            logits, loss = model(X, Y) # 前向传播计算 loss
            losses[k] = loss.item() # 记录单个批次 loss
        out[split] = losses.mean() # 计算多批次 loss 的平均值
    model.train() # 模型切到训练模式
    return out


# ======== 简易版 bigram 模型 ========
class BigramLanguageModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.token_embedding_table = nn.Embedding(vocab_size, n_embd)
        self.position_embedding_table = nn.Embedding(block_size, n_embd)
        self.lm_head = nn.Linear(n_embd, vocab_size)

    def forward(self, idx, targets=None):
        B, T = idx.shape
        tok_embd = self.token_embedding_table(idx) # (B, T, embedding_c)
        pos_embd = self.position_embedding_table(torch.arange(T, device=device)) # (T, embedding_c)
        x = tok_embd + pos_embd # (B, T, embedding_c)
        logits = self.lm_head(x) # # (B, T, vocab_size)
        if targets is None:
            loss = None
        else:
            B, T, C = logits.shape
            logits = logits.view(B*T, C)
            targets = targets.view(B*T)
            loss = F.cross_entropy(logits, targets)
        return logits, loss

    def generate(self, idx, max_new_tokens):
        for _ in range(max_new_tokens):
            logits, loss = self(idx)
            logits = logits[:, -1, :] # becomes (B, C) 提取最后一个时间步的预测结果，核心是适配 Bigram 模型 “只依赖最后一个 Token 预测下一个 Token” 的核心逻辑
            probs = F.softmax(logits, dim=-1)
            idx_next = torch.multinomial(probs, num_samples=1)
            idx = torch.cat((idx, idx_next), dim=1)
        return idx


model = BigramLanguageModel()
m = model.to(device)


# ======== 优化器 ========
'''
计算损失（loss）→ 清空旧梯度 → 计算新梯度（反向传播）→ 用梯度更新参数
让模型参数朝着 “损失减小” 的方向调整
'''
optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)
for iter in range(max_iters):
    if iter % eval_interval == 0:
        losses = estimate_loss()
        print(f'step({iter}): train loss {losses["train"]:.4f}, val loss {losses["val"]:.4f}')

    xb, yb = get_batch('train')

    logits, loss = model(xb, yb)
    optimizer.zero_grad(set_to_none=True) # 清空旧梯度（必须先清，否则梯度会累加）
    loss.backward() # 计算梯度（反向传播）
    optimizer.step() # 用梯度更新参数


# ======== 预测生成 ========
context = torch.zeros((1, 1), dtype=torch.long, device=device)
print(decode(m.generate(context, max_new_tokens=500)[0].tolist()))
