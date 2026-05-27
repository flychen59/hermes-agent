陈逸鹏
手机: 15069104076 | 邮箱: chenyipeng0509@gmail.com
微信: ovo9579 | 所在地: 北京
GitHub: github.com/flychen59
意向职位: AI Agent算法工程师 / 多模态算法工程师

═══════════════════════════════════════════════════════════════════════

🟢 滴滴出行 | Agent算法工程师 | 2025.04 - 至今

━━━ 项目一：Map-DeepSearch Agent ━━━

面向地图出行的多步推理搜索Agent，支持沿途地点搜索、多点路线规划等复杂查询。
基于ReAct范式设计MapSearch（单工具快速查询）与DeepSearch（多步推理）双模式架构，
调度地图API、Web Search等12个工具，输出可解释的路线与地点推荐。日均服务50w+次查询。

算法工作：

• GRPO强化学习训练：基于OpenRLHF框架对Qwen2.5-7B/14B进行Agent工具调用能力训练。
  设计5维Reward Model（工具选择、参数合法性、执行成功率、多步一致性、回答可用性），
  采用rule-based（格式校验、参数类型检查）+ model-based（Qwen2.5-72B打分）混合奖励。
  训练后工具调用准确率从72%提升至88%（+16pp，BFCL评测），多步任务完成率从65%提升至83%（+18pp）。
  对比实验：同等数据下DPO提升+11pp，GRPO优于DPO约5pp，与DeepSeek-R1论文结论一致。
  训练配置：8×A800，LoRA rank=64，3 epoch，学习率2e-5。

• Agent自动化评测体系：参考AgentBench/ToolBench设计离线评测框架，
  覆盖工具选择准确率、参数完整率、多步任务完成率、端到端回答质量4个维度。
  工具选择/参数完整率用rule-based精确匹配（确定性高），
  端到端回答质量用LLM-as-Judge（Qwen2.5-72B，pairwise对比模式），
  与人工标注一致性达87.3%（50组对比样本），接入CI支持每次模型更新自动回归评测。

• 工具调用数据构建：基于OpenManus框架搭建自动化造数Pipeline。
  使用DeepSeek-V3生成多样化地图Query（覆盖地点搜索、沿途搜索、附近搜索、多点路线、
  家/公司上下文等8大场景），结合Web Search多进程检索真实POI/路线背景信息。
  经格式校验→执行验证→质量过滤（LLM打分>0.7）三阶段筛选，构建8w+条ReAct轨迹数据，
  其中高质量SFT数据3w+条，GRPO偏好数据5w+对（每对含chosen/rejected轨迹）。

• 工具参数跟随优化：针对多工具链路下漏填city_name、坐标、queries等参数的问题，
  构造参数缺失、参数错位、城市歧义、品牌词识别、多轮参数继承6类hard case共2000+条，
  采用课程学习策略从易到难训练。参数完整率从78%提升至91%（+13pp），
  因参数更完整减少重试轮次，单次工具调用平均耗时从1.8s降至1.3s（-28%）。

工程支撑：

• ReAct多步推理框架：基于OpenManus/ToolCallAgent构建执行循环，
  设计Router区分快速查询（单工具，P90<800ms）与DeepSearch（多步推理，平均3.2步，P90<4.5s）。
  GRPO训练后模型倾向生成更少但更有效的推理步骤，平均步数从3.8步降至3.2步（-16%），
  端到端延迟相应降低约12%。

• 路线规划链路：构建"API召回→Qwen2.5语义选点→路线重算排序"三阶段链路，
  通过沿途POI召回+起终点周边降级搜索+POI Selector筛选+途经点路线重算，
  输出Top3路线并沉淀到Memory。相比纯距离排序基线，路线被用户采纳率提升15%。

• Web Search增强：优化4路并行搜索、结果去重去噪、时间过滤与摘要压缩，
  引导泛信息结果后续调用地图工具补充结构化POI。结果可用率从61%提升至82%（+21pp）。

━━━ 项目二：AI出行打车Agent ━━━

基于自研eino Agent框架构建App内智能出行交易能力，支持意图识别、起终点补全、
路径选择与对话交易闭环。日均处理20w+次出行对话。

算法工作：

• Skill-based意图识别：设计"基础Prompt + 按需Skill Instruction"渐进式上下文注入。
  Skill Router选择业务模块（打车/低价/顺风车），仅暴露对应工具集与业务规则，
  减少无关工具干扰。多轮复用同一Skill时复用历史指令，Token消耗降低35%，
  意图识别准确率96.2%（封闭域5分类，测试集2w+样本）。

• Memory系统设计：长期画像/短期状态/按需召回三层架构，
  基于Redis Sharded Memory拆分存储用户画像、历史对话、工具结果和订单状态，
  调用前动态注入相关上下文（平均3.2条历史+1.5条画像）。
  多轮对话中历史信息有效引用率从41%提升至68%（+27pp）。

工程支撑：

• Agent可观测体系：全链路监控TTFT（P90<450ms）、TPOT（P90<35ms）、
  端到端延迟（P90<3.2s）、工具调用成功率（97.5%）、Skill路由准确率（98.1%），
  用于定位慢链路和高失败率场景，反向优化Prompt和工具编排。

• 用户体验优化：思考流可视化（展示任务进度和工具中间结果），等待流失率降低18%；
  多语言（中/英/日）和口语化时间表达理解。

═══════════════════════════════════════════════════════════════════════

🟡 蚂蚁集团 | 多模态算法工程师 | 2024.09 - 2025.02

━━━ 项目一：用户分发画像纠偏 ━━━
为解决 Tab3 短视频分发人群偏差问题，设计并落地基于多模态大模型的短视频分发画像 Pipeline，
实现从视频内容理解到分发人群预测的全链路自动化。

算法工作：
• 多模态 SFT 数据构建：基于视频 ASR + OCR 文本，设计"大模型生成 → 规则过滤 → 人工校验"三级数据流水线，
  使用 GPT-4o 生成分发人群标签（5大类别：年龄/性别/兴趣/消费力/活跃度），
  结合标签一致性校验和困难样本挖掘，最终构建 8w+ 高质量图文对 SFT 数据，标签准确率 94.6%。

• 多模态大模型训练：基于 Qwen2-VL 2B/7B，使用 LoRA（rank=128, alpha=256）+ DeepSpeed ZeRO-2
  进行多分类微调。训练数据涵盖影视/生活/知识/游戏/音乐 5 大视频类别，每类 1.5w+ 样本。
  2B 模型 Top-1 准确率 92.3%，7B 模型 Top-1 准确率 94.8%（Top-2 准确率分别为 96.1% / 97.8%），
  消融实验表明 LoRA rank=128 较 rank=64 准确率提升 1.8%。

• 模型量化与推理部署：使用 AWQ 4-bit 量化 Qwen2-VL 7B，结合 vLLM（continuous batching + PagedAttention）
  部署。离线 QPS 从 0.15 提升至 1.2（8×），线上 L20 GPU 从 22 张降至 12 张（-45%），
  峰值 QPS 达 22.8，平均推理延迟 P99 < 380ms。

业务成果：
• 用户画像覆盖从 5.3 亿扩展至 8.2 亿，新内容长播放数 +5.2%，长播放率 +4.6%，新鲜度 0d PV% +2.1%

━━━ 项目二：低质量视频识别与过滤 ━━━
为解决短视频标题/封面与视频内容不符的问题，设计视频-图文匹配 Pipeline，
筛选标题党、合成视频等低质量内容。

算法工作：
• 构建标签体系与数据集：标注 4w+ 视频-图文对，标签包括匹配/部分匹配/不匹配三档，
  输入包含视频帧 + 关联文本 + Qwen2-VL-72B 生成的视频 Caption。
  使用 LoRA 微调 Qwen2-VL-2B，引入 CoT 推理机制（先生成视频内容描述，再判断是否匹配）。
  相比 CLIP + BERT + CosEnt Loss 的 Visual-BGE baseline，
  召回率 90.2%（+4.2%），准确率 89.1%（+19.1%）。

业务成果：
• 部署上线后 3 个月内累计回刷 15w+ 视频/日，筛选 3200+ 异常视频，识别 180+ 违规合成视频用户

═══════════════════════════════════════════════════════════════════════

🔵 开源项目

━━━ Hermes Agent（贡献者，fork自 NousResearch/hermes-agent）━━━
GitHub: flychen59/hermes-agent | 自进化AI Agent框架

核心贡献（15 commits，3000+行代码）：
• macOS GUI自动化Agent：cliclick+AppleScript+Swift OCR闭环架构，
  包含截屏视觉验证、错误恢复、速度优化，操作成功率85%→95%
• 反爬浏览器自动化：基于Patchright/CloakBrowser，绕过BOSS直聘/猎聘反爬，
  支持验证码处理和多条件批量搜索
• 多Agent共享Skill框架 + Skill进化引擎，Agent自动从复杂任务提取可复用工作流
• 闲鱼/淘宝平台自动化：解决登录页JS设值不触发框架状态更新问题
  （execCommand insertText方案），实测记录iOS App 0窗口限制和反爬策略
• 修复多轮对话丢消息（消息合并/去重/上下文压缩）

━━━ AI日报生成器 ━━━
GitHub: flychen59/ai-company | flychen59/ai-daily-report

基于CrewAI多Agent协作的GitHub高星项目日报自动生成系统：
• 4 Agent流水线（研究员→编辑→分析师→审查员），协作完成数据采集、内容整理、趋势分析和质量审查
• 数据源：GitHub Trending API + DuckDuckGo Search，LLM：Kimi-K2.6
• 每日自动生成HTML日报并发布到GitHub Pages，持续运行3个月+

━━━ MNBVC多模态语料构建 ━━━
GitHub: flychen59/Arxiv_mllm_mnbvc（⭐1）| flychen59/chinaxivCrawler_mnbvc（⭐3）

• 基于Cambrian-1思路构建Arxiv论文的多模态结构化数据库。使用Tralics/Grobid将LaTeX转为
  结构化JSON，基于paraphrase-mpnet-base-v2计算句子嵌入并构建语义相似度索引（平均相似度0.94）。
• 基于Ray框架设计分布式处理系统，处理2000+ LaTeX文件，提取图片（二进制）、
  表格（HTML）、公式（MathML）等多模态数据并按原始排版顺序保存为Parquet格式。
  处理吞吐量50文件/分钟，数据完整性校验通过率99.2%。

━━━ OpenClaw Agent框架（自建部署）━━━
独立部署和运维OpenClaw Agent框架（自托管）：
• 飞书Bot消息路由，实现多平台（飞书+CLI）统一Agent交互
• 接入多模型provider（Qwen3.5-plus、GLM-5.1、Kimi-K2.5、MiniMax-M2.5），模型热切换
• 配置MCP Server（Streamable HTTP协议）和Skill插件系统
• 编写SOUL.md行为准则（集成Karpathy编码哲学）和USER.md用户画像

═══════════════════════════════════════════════════════════════════════

📚 教育背景

• 东国大学 | 硕士 | 人工智能专业（全英文授课）
• 汉阳大学 | 交流研究 | 人工智能方向
• 青岛科技大学 | 本科 | 计算机相关专业

研究成果：
• Rui Gao, Jiajia Xu, Yipeng Chen, "Heterogeneous Feature Fusion Module Based on CNN and Transformer
  for Multiview Stereo Reconstruction", Mathematics, 2022 (SCI, Q1, IF=2.3)
• Yipeng Chen et al., "Dashcam Video Analysis: Segmenting Car Foreground Occlusions Using Unsupervised
  Cluster-Based Method", KMMS 2023 Autumn (优秀论文奖)
• Yipeng Chen et al., "An Unsupervised Clustering Method for Segmenting the Foreground Occlusion of
  the Car in Dashcam Videos", KSC 2023

═══════════════════════════════════════════════════════════════════════

🛠️ 技能栈

• Agent 算法：ReAct / Multi-Agent 协作 / Tool Use / GRPO强化学习 / Prompt Engineering / Memory 设计 / Agent评测
• 大模型训练：LoRA/QLoRA 微调 / DeepSpeed ZeRO / OpenRLHF / GRPO / SFT 数据构建 / 偏好对齐
• 多模态：Qwen2-VL / CLIP / ViT / 多模态数据处理 / 视频理解 / ASR+OCR
• 模型部署：vLLM / AWQ 量化 / 推理优化 / continuous batching / PagedAttention
• 工程能力：Python / Go / SQL / Redis / Ray / Docker / Linux
• 语言能力：英语（托福 79） / 韩语（TOPIK 4） / 可无障碍阅读英文论文和技术文档

═══════════════════════════════════════════════════════════════════════

🏆 荣誉奖项

• KMMS 2023 韩国多媒体工学秋季学会 优秀论文奖
• 东国大学 全额奖学金（SRD）
• 汉阳大学 优秀毕业生（120人取10）/ TOPIK 语言奖学金
• 青岛科技大学 三等奖学金 ×2
