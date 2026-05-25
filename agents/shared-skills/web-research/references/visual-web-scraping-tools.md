# 视觉爬虫工具调研（2026-05-25）

## 需求场景
搜索网页 → 看图片 → 理解内容 → 提取有用信息

## 第一梯队：成熟度高、社区活跃

| 工具 | ⭐ | 最近更新 | 核心能力 | 免费/付费 | 视觉能力 |
|------|-----|---------|---------|----------|---------|
| **Firecrawl** | 124k | 2026-05-25 | 搜索+爬取+清洗+截图，专为 AI Agent 设计 | 免费500次/月 | ✅ 截图、结构化提取、批量爬取 |
| **browser-use** | 95k | 2026-05-23 | AI Agent 直接操控浏览器，能"看"页面 | 开源免费，需自备 LLM API | ✅✅ 最强，多模态理解页面、点击、输入 |
| **Crawl4AI** | 66k | 2026-05-25 | 本地爬虫，输出 Markdown/JSON，截图+图片提取 | 完全免费开源 | ✅ 截图、图片提取、懒加载处理 |
| **Crawlee** | 23k | 2026-05-25 | Node.js 爬虫框架，专业级 | 开源免费 | ⚠️ 不直接支持视觉 |
| **Browserless** | 13k | 2026-05-22 | 云端无头浏览器服务 | 免费6小时/月 | ✅ 截图+PDF+内容提取 |

## 第二梯队：AI原生提取

| 工具 | ⭐ | 最近更新 | 核心能力 | 免费/付费 |
|------|-----|---------|---------|----------|
| **ScrapeGraphAI** | 26k | 2026-05-21 | 用 LLM 自动理解页面结构并提取数据 | 开源免费，需 LLM API |
| **Stagehand** (Browserbase) | 23k | 2026-05-25 | 浏览器 Agent SDK，云端浏览器 | 免费10小时/月 |
| **AgentQL** | 1.4k | 2026-05-19 | 用类 SQL 查询语言精准提取网页元素 | 有免费额度 |
| **Jina Reader** | 11k | 2026-05-22 | URL 转 LLM 友好的 Markdown，一行命令 | 免费 |

## MCP Server（直接接入 Agent）

| 工具 | ⭐ | 说明 |
|------|-----|------|
| **Playwright MCP** (微软) | 33k | 截图+浏览器操控 |
| **Browserbase MCP** | 3.4k | Stagehand 的 MCP 封装 |
| **Scrapfly MCP** | 8 | 企业级爬虫 MCP |

## browser-use 实战经验

### 安装（需要 Python 3.10+）
```bash
python3.12 -m venv ~/ai-company/.venv
source ~/ai-company/.venv/bin/activate
pip install browser-use playwright langchain-openai
python -m playwright install chromium
```

### 新版 API（v0.12.8+）
browser-use 0.12.8 大改了 API：
- `BrowserConfig` → `BrowserProfile`（`from browser_use.browser.profile import BrowserProfile`）
- 不再接受 `langchain_openai.ChatOpenAI`，需要用自己的 wrapper：`from browser_use.llm.openai.chat import ChatOpenAI`
- `Agent` 参数：`browser_profile=` 替代 `browser=`

### 多模态 LLM 要求
browser-use 需要**真正支持 vision 的 LLM**：
- ✅ GPT-4o / GPT-4o-mini、Claude Sonnet/Opus、Gemini 2.5 Pro
- ❌ thinking 模型（kimi-k2.6 经中转站后 content 返回 None，reasoning 放在 reasoning_content）
- ❌ 纯文本模型（无法处理截图）

### 常见错误
- `"Your request was blocked"` — LLM API 中转站 content moderation 拦截，或 thinking 模型格式不兼容
- `'ChatOpenAI' object has no attribute 'provider'` — 用了 langchain 的 ChatOpenAI，需要用 browser-use 自带的
- `TypeError: unsupported operand type(s) for |: 'type' and 'NoneType'` — Python 3.9 不支持 X | None 语法，需 3.10+

### YuTou API 中转站
- 域名：`https://yutou.virtualgoods.top`
- 只有 2 个模型：`moonshotai/kimi-k2.5`、`moonshotai/kimi-k2.6`
- kimi-k2.6 是 thinking 模型，**不支持图片理解**（多模态请求返回 error）
- 不适合 browser-use 的视觉能力
