# 多 Agent "AI 公司"框架调研（2026-05）

## 用户需求
用多 Agent 框架模拟公司团队分工，拆解复杂任务，自我进化。目标是接兼职任务（freelance/gig），自动拆解→执行→交付，每次任务后进化。

## 主流框架对比

| 框架 | ⭐ | 角色/公司模拟 | 自我进化 | 适合接活 | 灵活度 |
|------|-----|-------------|---------|---------|-------|
| **MetaGPT** | ~40k | ✅ CEO→PM→架构师→工程师→QA 完整公司流水线 | ❌ 固定SOP | 软件开发类 | 中 |
| **ChatDev** | 33k | ✅ 对话驱动的AI软件公司 | ❌ 无 | 软件开发类 | 中 |
| **CrewAI** | 52k | ✅ 自定义角色+Hierarchical Manager | ⚠️ 浅 | ✅ 任意业务 | ⭐⭐⭐ |
| **AutoGen** (微软) | 58k | ✅ 多Agent对话协作 | ⚠️ 有反思无持久 | ✅ 通用 | ⭐⭐ |
| **LangGraph** | 33k | ⚠️ 需手动定义DAG | ⚠️ 需手动写 | ✅ 精确流程控制 | ⭐⭐⭐ |
| **agno** | 40k | ✅ Agent平台管理 | ❌ | ✅ | ⭐⭐ |
| **smolagents** (HF) | 27.5k | ❌ 单Agent为主 | ❌ | ❌ | ⭐ |
| **openai-agents** | 26.6k | ✅ 轻量多Agent | ❌ | ✅ | ⭐⭐ |

## 自我进化专项框架

| 框架 | ⭐ | 核心能力 |
|------|-----|---------|
| **EvoMap/evolver** | 7555 | GEP 驱动进化引擎，Gene/Capsule/Event 可审计进化 |
| **CORAL** | 671 | 轻量多Agent自主进化，支持 Claude Code/Codex |
| **AutoSkill** | 426 | 经验驱动终身学习，skill 自动进化 |
| **skill-evolution** | 146 | skill 从执行学习+失败反思+自动改进 |
| **Cellium-Agent** | 46 | 决策循环微内核+三层记忆+热插拔 |

## 推荐：CrewAI + 现有 OpenClaw/Hermes

理由：
1. CrewAI 最灵活——不限于写代码，可定义任何角色（BD/PM/Worker/QA/Delivery）
2. 支持自定义工具——OpenClaw/Hermes 作为底层工具接入
3. Hierarchical 流程有 Manager Agent 负责拆解调度
4. 社区最大，插件最多

### "AI 一人公司"角色设计

```
BD Agent → 搜兼职平台，筛选匹配任务
PM Agent → 分析需求，拆解成子任务 DAG
Worker Agent → 执行具体开发/写作/调研
QA Agent → 质量检查
Delivery Agent → 打包交付
```

### 进化闭环

每次任务完成后：
1. 记录执行过程和结果到 skill 库
2. 失败的步骤标记为 pitfall
3. 下次同类任务自动引用历史经验
4. 定期回顾和优化 SOP
