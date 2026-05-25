# 2026 年最新多 Agent 框架调研（2026-05-25）

> 搜索条件：GitHub `created:>2025-10-01` + `stars:>50` + `agent framework`
> 重点关注：能拆解复杂任务 + 自我进化 + 适配 OpenClaw/Hermes

## 🔥 最值得关注的新框架

### Tier 1：最适配我们项目

| 框架 | ⭐ | Created | 语言 | 核心能力 | 适配度 |
|------|-----|---------|------|---------|--------|
| **MetaSwarm** (dsifry/metaswarm) | 280 | 2026-02 | - | 自我进化多Agent编排，18 Agent + 13 Skill + 15 Command，支持 Claude Code/Gemini/Codex CLI，TDD 执行 | ⭐⭐⭐ |
| **SwarmClaw** (swarmclawai/swarmclaw) | 523 | 2026-02 | - | Agent 蜂群 + MCP 工具 + Agent 记忆 + 定时任务 + 任务委托，23+ 内置能力 | ⭐⭐⭐ MCP原生 |
| **InfiAgent** (polyuiislab/infiAgent) | 1171 | 2025-12 | - | 配置驱动创建 Agent，无限时间跨度任务，支持 anthropic skills 格式 | ⭐⭐ skill兼容 |
| **MemStack** (cwinvestments/memstack) | 354 | 2026-02 | - | 127 个预制 skill + 3-Agent 编排 + localhost 仪表盘 + MCP 工具管理 | ⭐⭐ skill可迁移 |

### Tier 2：增长快、有特色

| 框架 | ⭐ | 特色 |
|------|-----|------|
| **Claude-Code-Workflow** (catlog22) | 2035 | JSON 驱动多 Agent 开发框架，增长最快 |
| **Loki-Mode** (asklokesh) | 941 | 全自动 SDLC，输入需求→自动拆解→开发→部署，5 Provider + 11 质量关卡 |
| **MASFactory** (BUPT-GAMMA) | 391 | 图编排 + 可视化 DAG（"Vibe Graphing"） |
| **OpenLegion** (openlegion-ai) | 96 | 自然语言描述 Agent 团队，自动编排 |
| **Loong** (eastreams) | 640 | 轻量级、可扩展的 Agent 基础设施 |
| **Gem-Team** (mubaidr) | 128 | 自学习多 Agent 编排，spec 驱动 |
| **OpenGap** (open-gitagent) | 2790 | Git 原生的 Agent 定义标准 |
| **Agno** (agno-agi) | 40344 | Agent 平台管理，最成熟 |
| **KohakuTerrarium** (Kohaku-Lab) | 334 | 通用 Agent 框架 + 内置 App |
| **Forge** (antoinezambelli) | 1802 | Python 自托管 LLM 工具调用 + 多步 Agent |

## 推荐方案

**MetaSwarm + SwarmClaw 组合**：
- MetaSwarm 做自我进化引擎（18 Agent + 自动 skill 进化 + TDD）
- SwarmClaw 做 MCP 工具桥接层（天然兼容 OpenClaw/Hermes 的 MCP 协议）

**AI 一人公司角色设计**：
```
BD Agent → 搜兼职平台，筛选匹配任务
PM Agent → 分析需求，拆解成子任务 DAG
Worker Agent → 执行具体开发/写作/调研
QA Agent → 质量检查
Delivery Agent → 打包交付
```

**进化闭环**：每次任务完成后 → 记录执行过程到 skill 库 → 失败标记 pitfall → 下次自动引用 → 定期回顾优化 SOP
