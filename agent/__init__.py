"""
=============================================================
LLM 应用开发演进路线 —— 从基础到高级
=============================================================

基座服务：厂内自研大模型请求网关
  - 网关地址: https://oneapi-comate.baidu-int.com/v1
  - 调用方式: requests (HTTP POST)，不依赖任何第三方 LLM SDK
  - 鉴权: Bearer Token
  - 支持模型: Claude / GPT / Qwen / 文心 / DeepSeek / ...
  - 接口协议: 兼容 Chat Completions 格式

依赖：pip install requests（标准库级别，零额外依赖）

=============================================================

教程目录 & 技术演进路径：

 Level 0 │ 00_base.py          │ 最基础的 API 调用
         │                      │ → HTTP 请求结构、Token、Temperature
         │
 Level 1 │ 01_multi_turn.py    │ 多轮对话与上下文管理
         │                      │ → 滑动窗口、消息历史、记忆策略
         │
 Level 2 │ 02_streaming.py     │ 流式输出
         │                      │ → SSE 协议、iter_lines、TTFT
         │
 Level 3 │ 03_tool_use.py      │ Tool Use / Function Calling
         │                      │ → tools 定义、tool_calls、tool message
         │
 Level 4 │ 04_react_agent.py   │ ReAct Agent
         │                      │ → Thought-Action-Observation 循环
         │
 Level 5 │ 05_mcp_client.py    │ MCP (Model Context Protocol)
         │                      │ → 工具标准化、Server/Client、JSON-RPC
         │
 Level 6 │ 06_skill.py         │ Skill / Plugin 模式
         │                      │ → 复合能力封装、路由、注册中心
         │
 Level 7 │ 07_multi_agent.py   │ Multi-Agent 编排
         │                      │ → Orchestrator、Pipeline、Debate

=============================================================

使用方式:
    pip install requests
    cd harry_python_practice/agent/
    python 00_base.py

每个文件都可独立运行，运行时输入你的 TOKEN 即可。

=============================================================

核心架构：

   你的代码（requests.post）
         │
         │ HTTP POST + Bearer Token
         v
   ┌─────────────────────────────┐
   │  自研大模型请求网关 (OneAPI)  │
   │  鉴权 / 路由 / 限流 / 监控   │
   └──┬──────┬──────┬──────┬────┘
      │      │      │      │
      v      v      v      v
   Claude  GPT-4o  Qwen  DeepSeek ...

=============================================================

面试知识图谱:

    LLM 基础
    ├── Token / Tokenizer / 上下文窗口
    ├── Temperature / Top-P / Sampling
    └── Prompt Engineering

    应用架构
    ├── Chat Completions API (HTTP)
    ├── Streaming (SSE)
    ├── Function Calling (tool_calls)
    └── RAG (检索增强生成)

    Agent 体系
    ├── ReAct (推理+行动循环)         ← 最高频
    ├── Plan-and-Execute
    ├── Reflexion (自我反思)
    └── Multi-Agent (多智能体协作)    ← 最高频

    工程化
    ├── MCP (工具标准协议)            ← 最高频
    ├── Skill/Plugin (能力封装)
    ├── 统一网关 (鉴权/路由/监控)
    └── Evaluation (评估体系)

=============================================================
"""
