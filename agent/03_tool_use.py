"""
=============================================================
第3课：Tool Use / Function Calling
=============================================================
知识点：
- LLM 不直接执行工具，而是输出结构化的"调用意图"
- 客户端负责实际执行工具，并将结果返回给 LLM
- 这是 Agent 的核心基础能力

面试高频问题：
Q: Function Calling 流程？
A: 用户提问 → LLM 输出 tool_calls → 客户端执行 → tool message 返回 → LLM 最终回答

Q: LLM 怎么"学会"调工具的？
A: 通过 tools 参数传入 JSON Schema 描述，模型训练时已学会匹配意图并生成调用参数。

Q: 如何高度自定义工具？如在指定开发机环境操作。
A: 工具本质就是"名字+描述+参数schema+执行函数"。
   执行函数可以做任何事：SSH远程执行、调API、操作DB等。
   LLM 只负责决定调什么工具、传什么参数；
   真正的执行逻辑完全由客户端控制，灵活性极高。

TODO 如果想要测试开发环境，需要：
1. export DEV_ENV_PWD="你的密码"
2. 确保 sshpass 已安装: apt install sshpass
=============================================================
"""

import os
import json
import subprocess
from openai import OpenAI

# ==================== 配置 ====================
BASE_URL = "https://oneapi-comate.baidu-int.com/v1"
API_KEY = os.getenv("LLM_API_KEY", "")
MODEL = "GLM-5"

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)


# ==================== 工具定义 ====================
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_lmj_weather",
            "description": "获取指定城市的当前天气信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名称"},
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "lmj_calculate",
            "description": "执行数学计算表达式",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "数学表达式，如 '2+3*4'"}
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_on_dev_machine",
            "description": "在开发机(10.178.221.140)的 tmux lmj 会话第4个面板中执行 shell 命令，用于查看日志、运行脚本、检查进程等",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "要执行的 shell 命令，如 'ls -la' / 'cat /tmp/test.log' / 'ps aux | grep python'"}
                },
                "required": ["command"]
            }
        }
    },
]


# ==================== 工具实现 ====================
DEV_HOST = "10.178.221.140"
DEV_PWD = os.getenv("DEV_ENV_PWD", "")


def run_on_dev_machine(command: str) -> str:
    """
    通过 SSH 在开发机的 tmux lmj 第4个面板执行命令。
    使用 sshpass + ssh 执行，tmux send-keys 发送命令到指定 panel。
    """
    # tmux 面板索引从 0 开始，第4个 panel = index 3
    tmux_cmd = f"tmux send-keys -t lmj.3 '{command}' Enter"
    # 先发送命令，再读取输出（通过 capture-pane）
    full_cmd = (
        f"sshpass -p '{DEV_PWD}' ssh -o StrictHostKeyChecking=no root@{DEV_HOST} "
        f"\"{tmux_cmd} && sleep 1 && tmux capture-pane -t lmj.3 -p\""
    )
    try:
        result = subprocess.run(
            full_cmd, shell=True, capture_output=True, text=True, timeout=15
        )
        output = result.stdout.strip() or result.stderr.strip()
        return json.dumps({"output": output[-2000:]}, ensure_ascii=False)  # 截断过长输出
    except subprocess.TimeoutExpired:
        return json.dumps({"error": "命令执行超时(15s)"})
    except Exception as e:
        return json.dumps({"error": str(e)})


def execute_tool(name: str, args: dict) -> str:
    if name == "get_lmj_weather":
        data = {"北京": {"temp": 22, "condition": "晴"},
                "上海": {"temp": 26, "condition": "多云"},
                "深圳": {"temp": 30, "condition": "雷阵雨"}}
        city = args["city"]
        return json.dumps(data.get(city, {"temp": 20, "condition": "未知"}), ensure_ascii=False)
    elif name == "lmj_calculate":
        try:
            return json.dumps({"result": eval(args["expression"])})
        except Exception as e:
            return json.dumps({"error": str(e)})
    elif name == "run_on_dev_machine":
        return run_on_dev_machine(args["command"])
    return json.dumps({"error": f"未知工具: {name}"})


# ==================== Tool Use 循环 ====================
def tool_use_loop():
    """通用 Tool Use 循环 —— Agent 核心雏形"""
    print(f"\n🔧 Tool Use 演示 (模型: {MODEL})")
    print("输入 'quit' 退出")
    print("试试: '北京天气怎么样？帮我算 15*23+47'")
    print("      '帮我看下开发机上有哪些 python 进程'")
    print("=" * 60)

    messages = []

    while True:
        user_input = input("\n👤 You: ").strip()
        if user_input.lower() == "quit":
            break

        messages.append({"role": "user", "content": user_input})

        # 循环直到不再需要工具
        while True:
            response = client.chat.completions.create(
                model=MODEL, max_tokens=2048, tools=tools, messages=messages
            )

            choice = response.choices[0]
            msg = choice.message

            # 最终回答
            if choice.finish_reason == "stop":
                print(f"\n🤖 Assistant: {msg.content}")
                messages.append({"role": "assistant", "content": msg.content})
                break

            # 工具调用
            if msg.tool_calls:
                print(f"🪄 Tool call: {msg}")
                messages.append(msg)
                for tc in msg.tool_calls:
                    fname = tc.function.name
                    fargs = json.loads(tc.function.arguments)
                    print(f"   🔧 调用: {fname}({json.dumps(fargs, ensure_ascii=False)})")

                    result = execute_tool(fname, fargs)
                    print(f"   📦 结果: {result}")

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": result,
                    })
            else:
                # 其他情况
                if msg.content:
                    print(f"\n🤖 Assistant: {msg.content}")
                messages.append({"role": "assistant", "content": msg.content or ""})
                break


if __name__ == "__main__":
    tool_use_loop()

"""
Tool Use 时序：
  User → Client → LLM: messages + tools 定义
  LLM → Client: tool_calls [{name, arguments}]
  Client: 执行工具，得到结果
  Client → LLM: tool message (tool_call_id + content)
  LLM → Client: 最终文本回答 (finish_reason=stop)

下一课：04_react_agent.py → ReAct Agent
"""
