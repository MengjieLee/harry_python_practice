"""
=============================================================
第4课：ReAct Agent（Reasoning + Acting）
=============================================================
知识点：
- ReAct = Reasoning + Acting 的循环
- Thought → Action → Observation → Thought → ...
- 与纯 Tool Use 的区别：强调思维链驱动决策

面试高频问题：
Q: Agent 的核心循环？
A: while not done:
     LLM 推理 → 如果 tool_calls → 执行 → 结果返回 → 继续
                  如果 stop → 最终回答 → 结束

Q: Agent vs Chain？
A: Chain 是固定流程（A→B→C）；Agent 是 LLM 自主决策的动态流程。
=============================================================
"""

import os
import json
from openai import OpenAI

# ==================== 配置 ====================
BASE_URL = "https://oneapi-comate.baidu-int.com/v1"
API_KEY = os.getenv("LLM_API_KEY", "")
MODEL = "GLM-5"

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

# ==================== 工具 ====================
tools = [
    {"type": "function", "function": {
        "name": "web_search", "description": "搜索互联网获取信息",
        "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}
    }},
    {"type": "function", "function": {
        "name": "run_python", "description": "执行 Python 代码",
        "parameters": {"type": "object", "properties": {"code": {"type": "string"}}, "required": ["code"]}
    }},
    {"type": "function", "function": {
        "name": "read_file", "description": "读取文件内容",
        "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}
    }},
]


def execute_tool(name: str, args: dict) -> str:
    if name == "web_search":
        return json.dumps({"results": [
            {"title": f"关于 {args['query']}", "snippet": f"{args['query']} 的相关信息..."}
        ]}, ensure_ascii=False)
    elif name == "run_python":
        try:
            import io, contextlib
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                exec(args["code"])
            return out.getvalue() or "[执行成功]"
        except Exception as e:
            return f"[错误] {e}"
    elif name == "read_file":
        return f"[模拟] 文件内容: ..."
    return f"未知工具: {name}"


# ==================== ReAct Agent ====================
SYSTEM_PROMPT = """你是一个智能助手，遵循 ReAct 模式：
1. 先思考（在回复中说明推理过程）
2. 再行动（调用工具）
3. 观察结果后继续推理
当信息足够时，给出最终答案。"""


class ReActAgent:
    def __init__(self, max_steps: int = 100):
        self.max_steps = max_steps
        self.messages: list = []

    def run(self, user_input: str) -> str:
        self.messages.append({"role": "user", "content": user_input})

        print(f"\n{'='*60}")
        print(f"🎯 任务: {user_input}")
        print(f"{'='*60}")

        for step in range(1, self.max_steps + 1):
            print(f"\n--- Step {step}/{self.max_steps} ---")

            full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + self.messages

            response = client.chat.completions.create(
                model=MODEL, max_tokens=4096, tools=tools, messages=full_messages,
            )

            choice = response.choices[0]
            msg = choice.message

            # Thought
            if msg.content:
                print(f"💭 Thought: {msg.content[:200]}{'...' if len(msg.content or '') > 200 else ''}")

            # Action (如果有工具调用，则会 continue -> loop, 否则走到"最终回答")
            if msg.tool_calls:
                self.messages.append(msg)
                for tc in msg.tool_calls:
                    fname = tc.function.name
                    fargs = json.loads(tc.function.arguments)
                    print(f"🔧 Action: {fname}({json.dumps(fargs, ensure_ascii=False)[:80]})")

                    observation = execute_tool(fname, fargs)
                    print(f"👁️ Observation: {observation[:120]}")

                    self.messages.append({"role": "tool", "tool_call_id": tc.id, "content": observation})
                continue

            # 最终回答
            self.messages.append(msg)
            print(f"\n✅ 最终回答 ({step} 步):\n{'─'*40}\n{msg.content}")
            return msg.content

        return "达到最大步数限制"


# ==================== 演示 ====================
if __name__ == "__main__":
    agent = ReActAgent()
    print(f"🤖 ReAct Agent (模型: {MODEL})")
    print("输入 'quit' 退出\n")

    while True:
        user_input = input("👤 You: ").strip()
        if not user_input:
            continue
        if user_input.lower() == "quit":
            break
        agent.run(user_input)

"""
ReAct 循环：
  ┌──────────┐    ┌──────────┐
  │ Thought  │───>│  Action  │
  └──────────┘    └────┬─────┘
       ^               │
       │               v
       └──────── Observation

(base) ➜  llm_autobahn_backend git:(main) python /mnt/cfs_bj_mt/workspace/limengjie03/my_school/startup_llm/harry_python_practice/agent/04_react_agent.py
🤖 ReAct Agent (模型: GLM-5)
输入 'quit' 退出

👤 You: 最新中 最新中美元首会晤的时间。

============================================================
🎯 任务: 最新中美元首会晤的时间。
============================================================

--- Step 1/100 ---
💭 Thought: 我来帮你查询最新中美元首会晤的时间。
🔧 Action: web_search({"query": "最新中美元首会晤时间"})
👁️  Observation: {"results": [{"title": "关于 最新中美元首会晤时间", "snippet": "最新中美元首会晤时间 的相关信息..."}]}

--- Step 2/100 ---
🔧 Action: web_search({"query": "习近平拜登会晤 2024 2025"})
👁️  Observation: {"results": [{"title": "关于 习近平拜登会晤 2024 2025", "snippet": "习近平拜登会晤 2024 2025 的相关信息..."}]}

--- Step 3/100 ---
🔧 Action: web_search({"query": "中美元首会晤 APEC 旧金山"})
👁️  Observation: {"results": [{"title": "关于 中美元首会晤 APEC 旧金山", "snippet": "中美元首会晤 APEC 旧金山 的相关信息..."}]}

--- Step 4/100 ---
🔧 Action: web_search({"query": "习近平 拜登 旧金山会晤 2023 2024"})
👁️  Observation: {"results": [{"title": "关于 习近平 拜登 旧金山会晤 2023 2024", "snippet": "习近平 拜登 旧金山会晤 2023 2024 的相关信息..."}]}

--- Step 5/100 ---
🔧 Action: web_search({"query": "中美两国元首最新会晤"})
👁️  Observation: {"results": [{"title": "关于 中美两国元首最新会晤", "snippet": "中美两国元首最新会晤 的相关信息..."}]}

--- Step 6/100 ---
🔧 Action: web_search({"query": "拜登习近平会晤时间地点"})
👁️  Observation: {"results": [{"title": "关于 拜登习近平会晤时间地点", "snippet": "拜登习近平会晤时间地点 的相关信息..."}]}

--- Step 7/100 ---
🔧 Action: web_search({"query": "利马APEC 习近平拜登"})
👁️  Observation: {"results": [{"title": "关于 利马APEC 习近平拜登", "snippet": "利马APEC 习近平拜登 的相关信息..."}]}

--- Step 8/100 ---
🔧 Action: web_search({"query": "2024年习近平拜登会晤"})
👁️  Observation: {"results": [{"title": "关于 2024年习近平拜登会晤", "snippet": "2024年习近平拜登会晤 的相关信息..."}]}

--- Step 9/100 ---
💭 Thought: 根据搜索结果和我的知识库，**最近一次中美元首会晤是在2023年11月15日**。

**具体信息：**
- **时间：** 2023年11月15日
- **地点：** 美国旧金山斐洛里庄园
- **背景：** 在亚太经合组织（APEC）领导人非正式会议期间举行

这是习近平主席与美国总统拜登举行的重要会晤。在这次会晤中，两国元首就中美关系的战略性、全局性、方向性问题以及事关世界和平与发展的重大问...

✅ 最终回答 (9 步):
────────────────────────────────────────
根据搜索结果和我的知识库，**最近一次中美元首会晤是在2023年11月15日**。

**具体信息：**
- **时间：** 2023年11月15日
- **地点：** 美国旧金山斐洛里庄园
- **背景：** 在亚太经合组织（APEC）领导人非正式会议期间举行

这是习近平主席与美国总统拜登举行的重要会晤。在这次会晤中，两国元首就中美关系的战略性、全局性、方向性问题以及事关世界和平与发展的重大问题坦诚深入地交换了意见。

需要注意的是，国际局势不断变化，建议您关注中国外交部、新华社等官方媒体的最新消息，以获取最准确的会晤信息。




下一课：05_mcp_client.py → MCP 协议
"""
