"""
=============================================================
第2课：流式输出 (Streaming)
=============================================================
知识点：
- 非流式：等全部生成完才返回（延迟高）
- 流式：边生成边返回，逐 token 推送（首字延迟低）
- SSE (Server-Sent Events) 是流式传输的底层协议

面试高频问题：
Q: 流式输出的底层原理？
A: HTTP SSE 协议，chunked transfer。每个 chunk 含一个 delta。
   格式: "data: {json}\n\n"，最后 "data: [DONE]"。

Q: 流式 vs 非流式？
A: 流式：用户体验好，首 token 延迟低
   非流式：实现简单，适合批处理
=============================================================
"""

import os
import sys
import time
from openai import OpenAI

# ==================== 配置 ====================
BASE_URL = "https://oneapi-comate.baidu-int.com/v1"
API_KEY = os.getenv("LLM_API_KEY", "")
MODEL = "GLM-5"

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)


# ==================== 基础流式 ====================
def streaming_basic():
    """基础流式 - 带性能指标"""
    print("\n🔥 基础流式输出:")
    print("-" * 40)

    full_response = ""
    start_time = time.time()
    first_token_time = None

    stream = client.chat.completions.create(
        model=MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": "什么是 Token？一句话回答。"}],
        stream=True,
    )

    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            text = chunk.choices[0].delta.content
            if first_token_time is None:
                first_token_time = time.time()
            sys.stdout.write(text)
            sys.stdout.flush()
            full_response += text

    end_time = time.time()
    print(f"\n\n📊 性能指标:")
    print(f"   首 token 延迟 (TTFT): {(first_token_time - start_time)*1000:.0f}ms")
    print(f"   总耗时: {(end_time - start_time)*1000:.0f}ms")
    print(f"   输出长度: {len(full_response)} 字符")


# ==================== 查看 chunk 结构 ====================
def streaming_events():
    """查看流式 chunk 详细结构"""
    print("\n🔥 Chunk 结构详情 (前1000个):")
    print("-" * 40)

    stream = client.chat.completions.create(
        model=MODEL,
        max_tokens=256,
        messages=[{"role": "user", "content": "1+1等于几"}],
        stream=True,
    )

    for i, chunk in enumerate(stream):
        if chunk.choices:
            choice = chunk.choices[0]
            delta = choice.delta
            reasoning = getattr(delta, "reasoning_content", None)

            if i < 1000:
                print(f"  chunk {i}: role={delta.role} reasoning={repr(reasoning) if reasoning else None} content={repr(delta.content)} finish={choice.finish_reason}")

            # 输出可见内容
            if delta.content:
                sys.stdout.write(delta.content)
                sys.stdout.flush()

    print(f"\n\n💡 说明: GLM-5 前面的 chunk 是 reasoning（思维链），content 为 None；")
    print(f"   思维链结束后才开始输出可见 content。")

"""
  chunk 117: role=assistant reasoning='出' content=None finish=None
  chunk 118: role=assistant reasoning='计算' content=None finish=None
  chunk 119: role=assistant reasoning='结果' content=None finish=None
  chunk 120: role=assistant reasoning='。' content=None finish=None
  chunk 121: role=assistant reasoning=None content='1' finish=None
1  chunk 122: role=assistant reasoning=None content='+' finish=None
+  chunk 123: role=assistant reasoning=None content='1' finish=None
1  chunk 124: role=assistant reasoning=None content='等于' finish=None
等于  chunk 125: role=assistant reasoning=None content='2' finish=None
2  chunk 126: role=assistant reasoning=None content='。' finish=None
。  chunk 127: role=assistant reasoning=None content='' finish=stop

"""

# ==================== 流式多轮对话 ====================
def streaming_chat():
    """流式 + 多轮"""
    messages = []
    print("\n🔥 流式多轮对话（输入 'quit' 退出）:")
    print("-" * 40)

    while True:
        user_input = input("\n👤 You: ").strip()
        if user_input.lower() == "quit":
            break

        messages.append({"role": "user", "content": user_input})
        print("🤖 Assistant: ", end="")

        full_response = ""
        full_reasoning = ""
        reasoning_started = False
        content_started = False
        stream = client.chat.completions.create(
            model=MODEL, max_tokens=2056, messages=messages, stream=True,
        )
        for chunk in stream:
            if chunk.choices:
                delta = chunk.choices[0].delta
                reasoning = getattr(delta, "reasoning_content", None)

                # reasoning 阶段：收集并提示
                if reasoning:
                    full_reasoning += reasoning
                    if not reasoning_started:
                        reasoning_started = True
                        sys.stdout.write("💭 思考中...")
                        sys.stdout.flush()

                # content 阶段：输出可见回复
                if delta.content:
                    if not content_started:
                        content_started = True
                        if reasoning_started:
                            sys.stdout.write("\n🤖 回复: ")
                            sys.stdout.flush()
                    sys.stdout.write(delta.content)
                    sys.stdout.flush()
                    full_response += delta.content

        # 如果模型只产出了 reasoning 没有 content，把 reasoning 作为回复
        if not full_response and full_reasoning:
            print(f"\n🤖 回复（来自思维链）: {full_reasoning}")
            full_response = full_reasoning
        else:
            print()
        messages.append({"role": "assistant", "content": full_response})


# ==================== 主程序 ====================
if __name__ == "__main__":
    print("=" * 60)
    print(f"流式输出演示 (模型: {MODEL})")
    print("  1 - 基础流式（带性能指标）")
    print("  2 - Chunk 结构详情")
    print("  3 - 流式多轮对话")
    print("=" * 60)

    choice = input("请选择 (1/2/3): ").strip()
    if choice == "1":
        streaming_basic()
    elif choice == "2":
        streaming_events()
    elif choice == "3":
        streaming_chat()
