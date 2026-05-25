# 自我进化 Agent 框架调研（2026-05）

用户需求：能拆解复杂问题、动态编排任务、根据执行结果自我进化（反思→迭代→持久改进）的框架。

## 第一梯队：专门做自我进化

### EvoMap/evolver ⭐7555
- **GitHub**: github.com/EvoMap/evolver
- **核心**: GEP（Gene Expression Programming）驱动的自我进化引擎
- **机制**: Gene → Capsule → Event，每次执行是一个"胶囊"，进化过程可审计可回溯
- **更新**: 2026-05-23 仍在活跃
- **适用**: 需要可审计进化过程的场景

### CORAL (Human-Agent-Society/CORAL) ⭐671
- **GitHub**: github.com/Human-Agent-Society/CORAL
- **核心**: 轻量级多 Agent 自主自我进化，专为 auto-research 设计
- **机制**: Agent 执行完任务后自动提取经验 → 共享记忆 → 下次复用
- **支持**: Claude Code / Codex / Cursor
- **更新**: 2026-05-24
- **适用**: 研究型多 Agent 协作

### a-evolve (A-EVO-Lab) ⭐552
- **GitHub**: github.com/A-EVO-Lab/a-evolve
- **论文**: "Position: Agentic Evolution is the Path to Evolving LLMs"
- **核心**: LLM 通过 Agent 行为自身进化
- **适用**: 学术研究、LLM 自进化方向

### AutoSkill (ECNU-ICALK) ⭐426
- **GitHub**: github.com/ECNU-ICALK/AutoSkill
- **核心**: 经验驱动的终身学习，skill 自我进化
- **机制**: 每次执行积累经验 → 失败反思 → 自动改进策略 → 持久化
- **最接近用户需求**: skill 从执行中学习并进化，与 Hermes skill 框架思路一致但多了自动进化

### skill-evolution (hao-cyber) ⭐146
- **GitHub**: github.com/hao-cyber/skill-evolution
- **核心**: skill 从执行中学习、失败反思、自动改进
- **适用**: 已有 skill 框架的进化增强

### Cellium-Agent ⭐46
- **核心**: 自我进化 Agent 框架，决策循环微内核 + 三层记忆 + 热插拔组件

## 第二梯队：主流框架带部分能力

| 框架 | ⭐ | 拆解 | 进化 | 备注 |
|---|---|---|---|---|
| AutoGPT | 184k | ✅ | ❌ | 偏执行 |
| LangGraph | 32.9k | ✅ DAG | ⚠️ 手动写反思 | 灵活但需手写 |
| CrewAI | 52k | ✅ 多角色 | ⚠️ 浅 | 角色协作拆解好 |
| OpenAI Agents | 26.6k | ✅ | ❌ | 轻量 |
| MetaGPT | ~40k | ✅ 流水线 | ❌ | 固定角色流程 |
| AutoGen (微软) | 58k | ✅ | ⚠️ 反思无持久 | 多Agent对话 |
| smolagents (HF) | 27.5k | ✅ 代码思维 | ❌ | 简洁 |
| agno | 40k | ✅ | ❌ | 全功能 |

## 推荐方案

1. **AutoSkill** — 最贴合"根据问题自我进化"的需求，skill 持久进化
2. **CORAL** — 多 Agent 协作 + 经验提取 + 共享记忆
3. **EvoMap/evolver** — 最成熟（7.5k star），可审计的基因编程式进化

## 搜索渠道发现

- GitHub API 搜 `self-evolving agent OR self-improving agent OR agent evolution` 效果好
- 搜 `agent+skill+evolution+learn+reflect` 在限流后会返回 0 结果
- GitHub API 未认证 60次/小时限流，连续查询 25+ 次后会开始返回空
- 解决方案：用 `gh api` 走认证，或在查询间加 `sleep`
