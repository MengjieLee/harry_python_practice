"""
=============================================================
第7课：Multi-Agent 编排
=============================================================
知识点：
- 多 Agent：多个专业化 Agent 协作完成复杂任务
- 编排模式：Orchestrator / Pipeline / Debate
- 每个 Agent 独立 prompt，甚至可用不同模型

面试高频问题：
Q: 为什么多 Agent？
A: 专业化、解耦、可控、可扩展

Q: 常见模式？
A: Orchestrator-Workers（分派）/ Pipeline（流水线）/ Debate（辩论）
=============================================================
"""

import os
import json
from dataclasses import dataclass
from openai import OpenAI

# ==================== 配置 ====================
BASE_URL = "https://oneapi-comate.baidu-int.com/v1"
API_KEY = os.getenv("LLM_API_KEY", "")
MODEL = "GLM-5"

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)


# ==================== Agent 基类 ====================
@dataclass
class AgentConfig:
    name: str
    role: str
    system_prompt: str
    model: str = MODEL


class BaseAgent:
    def __init__(self, config: AgentConfig):
        self.config = config

    def run(self, task: str, context: str = "") -> str:
        content = f"背景:\n{context}\n\n任务:\n{task}" if context else task
        resp = client.chat.completions.create(
            model=self.config.model, max_tokens=2048,
            messages=[
                {"role": "system", "content": self.config.system_prompt},
                {"role": "user", "content": content},
            ])
        return resp.choices[0].message.content


# ==================== Orchestrator ====================
class Orchestrator:
    def __init__(self):
        self.workers: dict[str, BaseAgent] = {}

    def add(self, agent: BaseAgent):
        self.workers[agent.config.name] = agent

    def run(self, task: str) -> str:
        print(f"\n{'='*50}\n🎯 {task}\n{'='*50}")

        # 规划
        worker_info = "\n".join(f"- {n}: {a.config.role}" for n, a in self.workers.items())
        plan_resp = client.chat.completions.create(
            model=MODEL, max_tokens=512,
            messages=[
                {"role": "system", "content": '输出JSON: {"subtasks":[{"to":"worker名","task":"描述"}]}，只输出JSON。'},
                {"role": "user", "content": f"Workers:\n{worker_info}\n\n任务: {task}"}
            ])
        try:
            text = plan_resp.choices[0].message.content
            if "```" in text: text = text.split("```")[1].replace("json", "").strip()
            plan = json.loads(text)
        except:
            plan = {"subtasks": [{"to": n, "task": task} for n in self.workers]}

        # 执行
        results = {}
        for sub in plan["subtasks"]:
            name, desc = sub["to"], sub["task"]
            if name in self.workers:
                print(f"   → [{name}] {desc[:40]}")
                results[name] = self.workers[name].run(desc, json.dumps(results, ensure_ascii=False) if results else "")

        # 整合
        all_results = "\n".join(f"[{n}]: {r[:200]}" for n, r in results.items())
        final = client.chat.completions.create(
            model=MODEL, max_tokens=2048,
            messages=[
                {"role": "system", "content": "综合各专家输出给出最终回答。"},
                {"role": "user", "content": f"任务: {task}\n\n输出:\n{all_results}"}
            ])
        return final.choices[0].message.content


# ==================== Pipeline ====================
class Pipeline:
    def __init__(self):
        self.stages: list[BaseAgent] = []

    def add(self, agent: BaseAgent):
        self.stages.append(agent)

    def run(self, input_text: str) -> str:
        print(f"\n🔄 Pipeline ({len(self.stages)} stages)")
        current = input_text
        for i, agent in enumerate(self.stages):
            print(f"   Stage {i+1}: [{agent.config.name}]")
            current = agent.run(current)
        return current


# ==================== Debate ====================
class Debate:
    def __init__(self, rounds=2):
        self.agents: list[BaseAgent] = []
        self.rounds = rounds

    def add(self, agent: BaseAgent):
        self.agents.append(agent)

    def run(self, topic: str) -> str:
        print(f"\n🎭 辩论: {topic}")
        history = []
        for r in range(self.rounds):
            for agent in self.agents:
                ctx = "\n".join(history[-4:]) if history else "第一轮"
                resp = agent.run(f"话题: {topic}", f"讨论:\n{ctx}")
                history.append(f"[{agent.config.name}]: {resp}")
                print(f"   🗣️ {agent.config.name}: {resp[:100]}...")

        final = client.chat.completions.create(
            model=MODEL, max_tokens=1024,
            messages=[
                {"role": "system", "content": "总结辩论，给出平衡结论。"},
                {"role": "user", "content": "\n".join(history)}
            ])
        return final.choices[0].message.content


# ==================== 演示 ====================
def main():
    print(f"🤝 Multi-Agent (模型: {MODEL})")
    print("  1 - Orchestrator（分派）")
    print("  2 - Pipeline（流水线）")
    print("  3 - Debate（辩论）")
    choice = input("选择 (1/2/3): ").strip()

    if choice == "1":
        orch = Orchestrator()
        orch.add(BaseAgent(AgentConfig("analyst", "需求分析师", "拆解需求，输出功能点列表。")))
        orch.add(BaseAgent(AgentConfig("developer", "开发工程师", "编写实现代码。")))
        orch.add(BaseAgent(AgentConfig("reviewer", "审查员", "审查代码，给出评价。")))
        task = input("任务 (回车默认): ").strip() or "实现一个带过期的缓存装饰器"
        print(f"\n📌 结果:\n{orch.run(task)}")

    elif choice == "2":
        pipe = Pipeline()
        pipe.add(BaseAgent(AgentConfig("analyst", "分析师", "理解需求，列出要点。")))
        pipe.add(BaseAgent(AgentConfig("coder", "工程师", "根据分析编写代码。")))
        pipe.add(BaseAgent(AgentConfig("reviewer", "审查员", "审查并给出改进建议。")))
        task = input("任务 (回车默认): ").strip() or "实现 LRU Cache"
        print(f"\n📌 结果:\n{pipe.run(task)}")

    elif choice == "3":
        debate = Debate(rounds=2)
        debate.add(BaseAgent(AgentConfig("乐观派", "乐观者", "看到技术机遇，简洁有力。")))
        debate.add(BaseAgent(AgentConfig("谨慎派", "风险专家", "分析风险问题，简洁有力。")))
        topic = input("话题 (回车默认): ").strip() or "AI 会取代初级程序员吗？"
        print(f"\n⚖️ 总结:\n{debate.run(topic)}")


if __name__ == "__main__":
    main()
