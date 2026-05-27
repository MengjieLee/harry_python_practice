"""
=============================================================
第5课：MCP (Model Context Protocol)
=============================================================
知识点：
- MCP 标准化了 LLM 与外部工具/数据的连接
- 三大原语：Tools / Resources / Prompts
- 架构：Host → Client → Server（JSON-RPC 2.0）
- 模型无关，搭配任意 LLM 使用

面试高频问题：
Q: MCP 解决什么问题？
A: M个LLM × N个工具 = M×N适配 → 有MCP后变成 M+N

Q: MCP 和 Function Calling 关系？
A: Function Calling 是模型能力；MCP 是应用协议（标准化工具发现/调用）
=============================================================
"""

import os
import json
from dataclasses import dataclass, field
from typing import Any
from openai import OpenAI

# ==================== 配置 ====================
BASE_URL = "https://oneapi-comate.baidu-int.com/v1"
API_KEY = os.getenv("LLM_API_KEY", "")
MODEL = "GLM-5"

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)


# ==================== MCP Server 模拟 ====================
@dataclass
class MCPTool:
    name: str
    description: str
    input_schema: dict
    handler: Any


class MCPServer:
    """模拟 MCP Server（真实场景是独立进程，stdio/SSE 通信）"""

    def __init__(self, name: str):
        self.name = name
        self.tools: dict[str, MCPTool] = {}

    def add_tool(self, name, description, schema, handler):
        self.tools[name] = MCPTool(name, description, schema, handler)

    def handle_request(self, method: str, params: dict = None) -> dict:
        if method == "initialize":
            return {"serverInfo": {"name": self.name}, "capabilities": {"tools": True}}
        elif method == "tools/list":
            return {"tools": [
                {"name": t.name, "description": t.description, "inputSchema": t.input_schema}
                for t in self.tools.values()
            ]}
        elif method == "tools/call":
            tool = self.tools.get(params["name"])
            if tool:
                result = tool.handler(**params.get("arguments", {}))
                return {"content": [{"type": "text", "text": str(result)}]}
        return {"error": "unknown method"}


class MCPClient:
    """MCP Client —— 聚合多个 Server 的工具"""

    def __init__(self):
        self.servers: dict[str, MCPServer] = {}
        self.tools: list[dict] = []

    def connect(self, server: MCPServer):
        server.handle_request("initialize")
        self.servers[server.name] = server
        result = server.handle_request("tools/list")
        for t in result["tools"]:
            self.tools.append(t)
        print(f"   ✅ 连接 [{server.name}]: {[t['name'] for t in result['tools']]}")

    def get_openai_tools(self) -> list[dict]:
        """转为 OpenAI function calling 格式"""
        return [{"type": "function", "function": {
            "name": t["name"], "description": t["description"], "parameters": t["inputSchema"]
        }} for t in self.tools]

    def call_tool(self, name: str, args: dict) -> str:
        for server in self.servers.values():
            if name in server.tools:
                r = server.handle_request("tools/call", {"name": name, "arguments": args})
                return r["content"][0]["text"] if "content" in r else str(r)
        return f"工具未找到: {name}"


# ==================== 创建 MCP Servers ====================
def create_servers():
    # 文件系统 Server
    fs = MCPServer("filesystem")
    fake_fs = {"/project/main.py": "def main(): print('hello')", "/project/README.md": "# Demo"}

    fs.add_tool("list_files", "列出文件",
                {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
                lambda path: "\n".join(f for f in fake_fs if f.startswith(path)))
    fs.add_tool("read_file", "读取文件",
                {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
                lambda path: fake_fs.get(path, "文件不存在"))

    # 数据库 Server
    db = MCPServer("database")
    users = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]

    db.add_tool("query_users", "查询用户列表",
                {"type": "object", "properties": {}},
                lambda: json.dumps(users, ensure_ascii=False))
    db.add_tool("get_user", "按ID查用户",
                {"type": "object", "properties": {"id": {"type": "integer"}}, "required": ["id"]},
                lambda id: json.dumps(next((u for u in users if u["id"] == id), None), ensure_ascii=False))

    return fs, db


# ==================== MCP Agent ====================
class MCPAgent:
    def __init__(self):
        self.mcp = MCPClient()
        self.messages: list = []

    def connect(self, server: MCPServer):
        self.mcp.connect(server)

    def chat(self, user_input: str) -> str:
        self.messages.append({"role": "user", "content": user_input})
        tools = self.mcp.get_openai_tools()

        for _ in range(5):
            full_msgs = [{"role": "system", "content": "使用工具帮助用户。"}] + self.messages
            response = client.chat.completions.create(model=MODEL, max_tokens=2048, tools=tools, messages=full_msgs)
            choice = response.choices[0]
            msg = choice.message

            if choice.finish_reason == "stop":
                self.messages.append(msg)
                return msg.content or ""

            if msg.tool_calls:
                self.messages.append(msg)
                for tc in msg.tool_calls:
                    name = tc.function.name
                    args = json.loads(tc.function.arguments)
                    print(f"   🔧 MCP: {name}({args})")
                    result = self.mcp.call_tool(name, args)
                    print(f"   📦 → {result[:80]}")
                    self.messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})

        return "超时"


# ==================== 演示 ====================
if __name__ == "__main__":
    print("=" * 60)
    print(f"🔌 MCP 演示 (模型: {MODEL})")
    print("=" * 60)

    fs_server, db_server = create_servers()
    agent = MCPAgent()
    print("\n🔗 连接 MCP Servers:")
    agent.connect(fs_server)
    agent.connect(db_server)

    print(f"\n✅ 共 {len(agent.mcp.tools)} 个 MCP 工具可用")
    print("试试: '查看项目文件' / '查询所有用户'\n输入 'quit' 退出")

    while True:
        q = input("\n👤 You: ").strip()
        if not q:
            continue
        if q.lower() == "quit":
            break
        print(f"\n🤖 {agent.chat(q)}")
