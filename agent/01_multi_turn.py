"""
=============================================================
第1课：多轮对话与上下文管理
=============================================================
知识点：
- LLM 本身是无状态的，每次请求必须带完整对话历史
- Messages 数组就是"记忆"，客户端负责维护
- 上下文窗口有限，需要策略管理

面试高频问题：
Q: LLM 如何实现多轮对话？

LLM 是无状态，客户端负责策略管理 messages 数据维护。

A: LLM 本身无状态。客户端把历史 messages 全部发给模型，
   模型基于完整上下文生成回复。"记忆"在客户端，不在模型里。

Q: 上下文窗口满了怎么办？

1. 滑动窗口。 启发性截断记忆。技术支持，任务型 agent。
2. 摘要。LLM 压缩，分滚动（每轮）和分层（短期详细+长期概括）。长对话，保持全局一致性场景。
3. 增强能力。
    - RAG。历史信息存入向量数据库，需要时按需加载插入上下文。跨会话知识复用。
    - 分层记忆。工作记忆（当前对话，直接放上下文），短期记忆（最近几轮，按需检索），长期记忆（历史，向量检索+摘要）。
    - ctx length。调大，更贵。

A: 1. 滑动窗口：丢弃最早的消息
   2. 摘要压缩：用 LLM 对历史做摘要
   3. RAG 检索：只放相关片段

Q: python 内存管理介绍。
A: 引用计数 + 垃圾回收（解决循环引用），还有内存池 pymalloc 解决频繁小对象的创建。避免过渡向 OS 申领内存的开销(C 标准库的 malloc)。

Q: C malloc 的处理逻辑，即堆与系统调用（如 linux 的 brk 和 mmap）
A: 先说结论，brk 和 mmap 是在无碎片和利用率的策略上找平衡，两者的基线是 128k。
    - 堆。app runtime 的使用内存区域（虚拟地址空间）。
    - brk。针对堆的操作，连续，快速，适合小对象。
    - mmap。针对堆中空闲的"空洞"去操作映射真实内存，非连续，适合大对象。

=============================================================
"""

import os
from openai import OpenAI

# ==================== 配置 ====================
BASE_URL = "https://oneapi-comate.baidu-int.com/v1"
API_KEY = os.getenv("LLM_API_KEY", "")
MODEL = "GLM-5"

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)


# ==================== 多轮对话实现 ====================
class ChatSession:
    """
    多轮对话管理器
    核心：维护 messages 列表，每次请求带完整历史
    """

    def __init__(self, system_prompt: str = "", max_history: int = 20):
        self.system_prompt = system_prompt
        self.messages: list[dict] = []
        self.max_history = max_history
        # Token 统计
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.turn_count = 0

    def chat(self, user_input: str) -> str:
        # 1. 追加用户消息
        self.messages.append({"role": "user", "content": user_input})

        # 2. 滑动窗口截断
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history:]

        # 3. 构建完整消息（system + history）
        full_messages = []
        if self.system_prompt:
            full_messages.append({"role": "system", "content": self.system_prompt})
        full_messages.extend(self.messages)

        # 4. 调用 API
        response = client.chat.completions.create(
            model=MODEL,
            max_tokens=2048,
            messages=full_messages,
        )

        assistant_msg = response.choices[0].message.content

        # 5. 统计本轮 token 消耗
        self.turn_count += 1
        prompt_tokens = response.usage.prompt_tokens
        completion_tokens = response.usage.completion_tokens
        total_tokens = response.usage.total_tokens
        self.total_prompt_tokens += prompt_tokens
        self.total_completion_tokens += completion_tokens

        print(f"\n   📊 第{self.turn_count}轮 Token: 输入={prompt_tokens}, 输出={completion_tokens}, 小计={total_tokens}")

        # 6. 追加 assistant 回复到历史
        self.messages.append({"role": "assistant", "content": assistant_msg})
        return assistant_msg

    def get_total_tokens(self) -> dict:
        """获取累计 token 统计"""
        return {
            "turns": self.turn_count,
            "total_prompt_tokens": self.total_prompt_tokens,
            "total_completion_tokens": self.total_completion_tokens,
            "total_tokens": self.total_prompt_tokens + self.total_completion_tokens,
        }

    def get_history_tokens_estimate(self) -> int:
        """粗略估算 token 数"""
        total_chars = sum(len(m["content"]) for m in self.messages)
        return total_chars * 2


# ==================== 交互演示 ====================
def main():
    session = ChatSession(
        system_prompt="你是一位耐心的编程导师，用简洁的中文回答。记住上下文。",
        max_history=2,
    )

    print("=" * 60)
    print(f"多轮对话演示 (模型: {MODEL})")
    print("输入 'quit' 退出，'history' 查看历史")
    print("=" * 60)

    while True:
        user_input = input("\n👤 You: ").strip()
        if not user_input:
            continue
        if user_input.lower() == "quit":
            # 退出时打印总 token 消耗
            stats = session.get_total_tokens()
            print(f"\n{'='*60}")
            print(f"📊 Token 消耗汇总:")
            print(f"   总轮数: {stats['turns']}")
            print(f"   总输入 tokens: {stats['total_prompt_tokens']}")
            print(f"   总输出 tokens: {stats['total_completion_tokens']}")
            print(f"   总 tokens: {stats['total_tokens']}")
            print(f"{'='*60}")
            break
        if user_input.lower() == "history":
            print(f"\n📜 历史 ({len(session.messages)} 条):")
            for i, msg in enumerate(session.messages):
                icon = "👤" if msg["role"] == "user" else "🤖"
                preview = msg["content"][:50] + "..." if len(msg["content"]) > 50 else msg["content"]
                print(f"   {i+1}. {icon} {preview}")
            print(f"   预估 tokens: ~{session.get_history_tokens_estimate()}")
            continue

        response = session.chat(user_input)
        print(f"\n🤖 Assistant: {response}")


if __name__ == "__main__":
    main()

"""

"""
