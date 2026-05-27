"""
=============================================================
第0课：最基础的 LLM API 调用
=============================================================
知识点：
- LLM 本质是一个 "文本输入 → 文本输出" 的函数
- OpenAI 兼容接口是业界事实标准（几乎所有网关/模型都兼容）
- 我们使用自研 OneAPI 网关，统一接入多种模型
- role: system / user / assistant 三种角色
- 理解 Token、Temperature、Max Tokens 等核心参数

关于 OneAPI 网关：
- 统一模型接入层，暴露 OpenAI 兼容 API
- 后端路由到任意供应商（Anthropic/OpenAI/智谱/阿里等）
- 只需切换 model 参数即可切换底层模型
- 好处：统一接口、统一鉴权、统一计费、统一限流

面试高频问题：
Q: Temperature 的作用？

采样随机性，数学层面就是过滤 每个 token 互相相关性的 logits 经过降温 和 softmax（按行归一） 后的值
0 (更随机) ~ 1（更稳定）

A: 控制采样随机性。T=0 贪心确定性输出；T 越高越随机/有创造力。
   底层是对 logits 做 softmax(logits/T) 再采样。

Q: System Prompt 和 User Prompt 的区别？

前者是模型的人设和行为边界，也即顶层的全局规划，是指令层级优先级最高设定。
后者是用户的此次提问内容。

A: System 设定模型人设/行为边界，优先级最高；User 是用户具体问题。

Q: 为什么用 OpenAI 兼容接口？
A: 1. 通用性：一套代码切换任意模型
   2. 降低耦合：不绑定单一供应商
   3. 网关统一了鉴权/限流/计费
   4. 业界事实标准，生态最丰富
=============================================================
"""

import os
from openai import OpenAI

# ==================== 配置 ====================
# 自研 OneAPI 兼容网关
BASE_URL = "https://oneapi-comate.baidu-int.com/v1"
API_KEY = os.getenv("LLM_API_KEY", "")  # export LLM_API_KEY=your_token

# 可选模型（网关支持的模型，按需切换）
AVAILABLE_MODELS = {
    "glm5": "GLM-5",                # 智谱 GLM-5
    "glm5_turbo": "GLM-5-Turbo",    # 智谱 GLM-5 Turbo
    "claude_sonnet": "Claude Sonnet 4.6",  # Anthropic Claude
    "claude_opus": "Claude Opus 4.6",      # Anthropic Claude Opus
    "kimi": "Kimi-K2.6",            # Moonshot Kimi
    "minimax": "MiniMax-M2.7",      # MiniMax
}

# 默认使用 GLM-5
MODEL = AVAILABLE_MODELS["glm5"]
# print(f"当前模型: {MODEL}")
# print(f"可用模型: {list(AVAILABLE_MODELS.keys())}")

# ==================== 创建客户端 ====================
client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL,
)

# ==================== 最简调用 ====================
# 单轮对话 —— LLM 最原始的使用方式
response = client.chat.completions.create(
    model=MODEL,
    max_tokens=1024,
    # temperature: 控制输出随机性 (0~2, 通常用 0~1)
    temperature=0.7,
    messages=[
        # system: 设定模型行为边界
        {"role": "system", "content": "你是一位资深 Python 工程师，回答简洁精准。"},
        # user: 用户的具体问题
        {"role": "user", "content": "用一句话解释什么是 LLM？"},
    ],
)

# ==================== 解析响应 ====================
print("=" * 60)
print("【模型完整响应】")
print(response)

print("=" * 60)
print("【模型输出】")
print(response.choices[0].message.content)
print("=" * 60)

# 关键元信息
print(f"\n📊 Token 用量:")
print(f"   输入 tokens: {response.usage.prompt_tokens}")
print(f"   输出 tokens: {response.usage.completion_tokens}")
print(f"   总 tokens: {response.usage.total_tokens}")
print(f"   停止原因: {response.choices[0].finish_reason}")  # stop / length / tool_calls
print(f"   模型: {response.model}")

""" 输出结果
============================================================
【模型完整响应】
ChatCompletion(id='20260515111046111c2fc33f254029', choices=[Choice(finish_reason='stop', index=0, logprobs=None, message=ChatCompletionMessage(content='LLM 是基于 Transformer 架构、
在海量数据上预训练的深度神经网络，本质是通过概率预测下一个 Token 来实现通用的自然语言理解与生成。', refusal=None, role='assistant', annotations=None, audio=None, function_call=None, tool_calls=None, reasoning_content='用户想要用一句话解释什么是 LLM（大语言模型），要求回答简洁精准，并且扮演一位资深 Python 工程师。\n\n1.  **分析需求：**\n    *   **主题：** LLM（大语言模型）。\n    *   **约束：** 一句话。\n    *   **人设：** 资深 Python 工程师。\n    *   **风格：** 简洁精准。\n\n2.  **起草定义（内心独白/尝试）：**\n    *   *草稿 1（通用）：* LLM 是在海量数据上训练的 AI，可以生成文本。（太简单，不够“资深工程师”）。\n    *   *草稿 2（技术）：* LLM 是一种基于 Transformer 架构的深度神经网络，利用海量文本数据进行预训练，从而具备通用的自然语言理解与生成能力。（不错，但可能有点啰嗦）。\n    *   *草稿 3（Python 工程师风格）：* LLM 本质上是一个基于 Transformer 架构的概率模型，通过预测下一个 Token 来生成连贯文本。
（更好，击中了“概率模型”和“下一个 Token 预测”等关键技术点）。\n    *   *草稿 4（平衡技术深度与简洁性）：* LLM 是基于 Transformer 架构、通过海量数据预训练的深度神经网络，旨在通过预测下一个 Token 实现通用的自然语言理解与生成。\n\n3.  **针对“资深 Python 工程师”人设进行润色：**\n    *   资深工程师关心架构和机制。\n    *   核心关键词：Transformer（架构）、海量数据（规
模）、概率预测/下一个 Token（机制）。\n\n4.  **最终润色（中文）：**\n    "LLM 是基于 Transformer 架构、在海量文本数据上预训练的深度神经网络，通过预测下一个 Token 实现通用的自然语言理
解与生成。"\n\n    *评价：* 准确，提及了架构、训练数据、机制和功能。\n\n    让我们试着让它更简洁有力一点。\n    "LLM 是基于 Transformer 架构的海量参数深度神经网络，通过概率预测下一个 Token 来实现通用的语言理解与生成能力。"\n\n    让我们选一个强调技术本质的版本：\n    "LLM 是基于 Transformer 架构、通过海量数据预训练的深度概率模型，旨在通过预测下一个 Token 实现通用
的自然语言理解与生成。"\n\n5.  **最终选择：**\n    LLM 是基于 Transformer 架构、利用海量文本数据预训练的深度神经网络，通过预测下一个 Token 实现通用的自然语言理解与生成。\n\n    *自我
修正：* 也许“下一个 Token 预测”是工程师最关键的见解。\n\n    *修订后的最终版本：*\n    LLM 是基于 Transformer 架构、在海量数据上预训练的深度神经网络，本质是通过概率预测下一个 Token 来实现通用的自然语言理解与生成。\n\n6.  **输出生成。**'))], created=1778814661, model='glm-5', object='chat.completion', service_tier=None, system_fingerprint=None, usage=CompletionUsage(completion_tokens=680, prompt_tokens=26, total_tokens=706, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=None, audio_tokens=None, reasoning_tokens=638, rejected_prediction_tokens=None), prompt_tokens_details=PromptTokensDetails(audio_tokens=None, cached_tokens=0)), request_id='20260515111046111c2fc33f254029')
============================================================
【模型输出】
LLM 是基于 Transformer 架构、在海量数据上预训练的深度神经网络，本质是通过概率预测下一个 Token 来实现通用的自然语言理解与生成。
============================================================

📊 Token 用量:
   输入 tokens: 26
   输出 tokens: 680
   总 tokens: 706
   停止原因: stop
   模型: glm-5

"""

"""
核心概念小结：
┌─────────────────────────────────────────────────┐
│  User Input  →  [Tokenizer]  →  Token IDs      │
│  Token IDs   →  [LLM Model]  →  Logits         │
│  Logits      →  [Sampling]   →  Next Token      │
│  重复直到 finish_reason 触发                     │
└─────────────────────────────────────────────────┘

OneAPI 网关架构：
┌──────────────────────────────────────────────┐
│            应用层 (你的代码)                    │
│         使用 OpenAI SDK 调用                   │
└──────────────────┬───────────────────────────┘
                   │ OpenAI 兼容 API
                   v
┌──────────────────────────────────────────────┐
│         OneAPI 网关 (统一接入层)                │
│  • 统一鉴权 & 限流                            │
│  • 模型路由 (根据 model 参数分发)              │
│  • 格式转换 (统一为 OpenAI 格式)              │
│  • 监控 & 计费                                │
└──┬──────────┬──────────┬──────────┬─────────┘
   │          │          │          │
   v          v          v          v
┌──────┐ ┌──────┐ ┌──────┐ ┌──────────┐
│GLM-5 │ │Claude│ │ Kimi │ │ MiniMax  │
└──────┘ └──────┘ └──────┘ └──────────┘

下一课：01_multi_turn.py → 多轮对话与上下文管理
"""
