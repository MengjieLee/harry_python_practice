"""
=============================================================
第6课：Skill / Plugin 模式
=============================================================
知识点：
- Skill = Prompt + Tools + 执行策略（复合能力单元）
- Tool 是原子操作，Skill 是编排好的复合能力
- Plugin 是 Skill 的可发现/可分发形式

面试高频问题：
Q: Skill vs Tool？
A: Tool 单一操作(read_file)；Skill = 专用prompt + 工具集 + 执行策略
Q: Plugin 设计原则？
A: 可发现性、隔离性、热插拔、标准接口
=============================================================
"""

import os
import json
from dataclasses import dataclass
from typing import Callable
from openai import OpenAI

# ==================== 配置 ====================
BASE_URL = "https://oneapi-comate.baidu-int.com/v1"
API_KEY = os.getenv("LLM_API_KEY", "")
MODEL = "GLM-5"

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)


# ==================== Skill 框架 ====================
@dataclass
class Skill:
    name: str
    description: str
    trigger_keywords: list[str]
    system_prompt: str
    tools: list[dict]
    tool_handlers: dict[str, Callable]
    max_steps: int = 5


class SkillRegistry:
    def __init__(self):
        self.skills: dict[str, Skill] = {}

    def register(self, skill: Skill):
        self.skills[skill.name] = skill
        print(f"   ✅ {skill.name}: {skill.description}")

    def route(self, text: str) -> Skill | None:
        for skill in self.skills.values():
            if any(kw in text.lower() for kw in skill.trigger_keywords):
                return skill
        return None


class SkillExecutor:
    def execute(self, skill: Skill, user_input: str) -> str:
        print(f"   ⚡ 激活: [{skill.name}]")
        messages = [
            {"role": "system", "content": skill.system_prompt},
            {"role": "user", "content": user_input},
        ]
        for _ in range(skill.max_steps):
            resp = client.chat.completions.create(
                model=MODEL, max_tokens=2048, tools=skill.tools, messages=messages)
            choice = resp.choices[0]
            msg = choice.message

            if choice.finish_reason == "stop":
                return msg.content or ""

            if msg.tool_calls:
                messages.append(msg)
                for tc in msg.tool_calls:
                    handler = skill.tool_handlers.get(tc.function.name)
                    if handler:
                        result = handler(**json.loads(tc.function.arguments))
                        messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})
        return "超时"


# ==================== 具体 Skills ====================
def code_review_skill() -> Skill:
    def analyze(code: str, **_) -> str:
        issues = []
        if "eval(" in code: issues.append("HIGH: eval() 安全风险")
        if "import *" in code: issues.append("MEDIUM: 避免 wildcard import")
        return json.dumps(issues or ["无明显问题"], ensure_ascii=False)

    def suggest(code: str, focus: str = "quality", **_) -> str:
        return json.dumps([f"针对{focus}：建议优化数据结构", "添加类型注解"], ensure_ascii=False)

    return Skill(
        name="code_review", description="代码审查与改进建议",
        trigger_keywords=["review", "代码审查", "看看代码"],
        system_prompt="你是代码审查专家。先 analyze 分析，再 suggest 建议，最后综合评价。",
        tools=[
            {"type": "function", "function": {"name": "analyze", "description": "分析代码问题",
                "parameters": {"type": "object", "properties": {"code": {"type": "string"}}, "required": ["code"]}}},
            {"type": "function", "function": {"name": "suggest", "description": "改进建议",
                "parameters": {"type": "object", "properties": {"code": {"type": "string"}, "focus": {"type": "string"}}, "required": ["code"]}}},
        ],
        tool_handlers={"analyze": analyze, "suggest": suggest},
    )


def sql_skill() -> Skill:
    def get_schema(table_name: str, **_) -> str:
        schemas = {"users": "id INT, name VARCHAR, email VARCHAR",
                   "orders": "id INT, user_id INT, amount DECIMAL"}
        return schemas.get(table_name, f"表 {table_name} 不存在")

    def run_sql(sql: str, **_) -> str:
        return json.dumps({"rows": [["Alice", 1500], ["Bob", 2300]], "count": 2})

    return Skill(
        name="sql_assistant", description="自然语言转 SQL 并执行",
        trigger_keywords=["sql", "查询", "数据库", "表"],
        system_prompt="你是 SQL 专家。先 get_schema 看表结构，再写 SQL，用 run_sql 执行。",
        tools=[
            {"type": "function", "function": {"name": "get_schema", "description": "获取表结构",
                "parameters": {"type": "object", "properties": {"table_name": {"type": "string"}}, "required": ["table_name"]}}},
            {"type": "function", "function": {"name": "run_sql", "description": "执行SQL",
                "parameters": {"type": "object", "properties": {"sql": {"type": "string"}}, "required": ["sql"]}}},
        ],
        tool_handlers={"get_schema": get_schema, "run_sql": run_sql},
    )


# ==================== Skill Agent ====================
class SkillAgent:
    def __init__(self):
        self.registry = SkillRegistry()
        self.executor = SkillExecutor()

    def register(self, skill: Skill):
        self.registry.register(skill)

    def chat(self, text: str) -> str:
        skill = self.registry.route(text)
        if skill:
            return self.executor.execute(skill, text)
        resp = client.chat.completions.create(model=MODEL, max_tokens=1024, messages=[{"role": "user", "content": text}])
        return resp.choices[0].message.content


if __name__ == "__main__":
    print("=" * 60)
    print(f"🧩 Skill/Plugin 演示 (模型: {MODEL})")
    print("=" * 60)

    agent = SkillAgent()
    print("\n📦 注册 Skills:")
    agent.register(code_review_skill())
    agent.register(sql_skill())

    print("\n试试: 'review: def f(): eval(input())' / '查询 users 表'\n输入 'quit' 退出")

    while True:
        q = input("\n👤 You: ").strip()
        if not q: continue
        if q.lower() == "quit": break
        print(f"\n🤖 {agent.chat(q)}")
