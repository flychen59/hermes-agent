陈逸鹏
手机: 15069104076 | 邮箱: chenyipeng0509@gmail.com | 所在地: 北京
GitHub: github.com/flychen59
意向：AI Agent算法工程师 / 多模态算法工程师

---

## 滴滴出行 · Agent算法工程师（2025.04至今）

### 项目一：Map-DeepSearch Agent

面向地图出行的多步推理搜索Agent，支持沿途搜索、多点路线规划等复杂场景。日均服务50万+次查询。

**GRPO强化学习训练工具调用能力**
- 问题：Qwen2.5基座模型在多工具场景下工具选择和参数填充准确率不足，影响复杂查询完成率
- 方案：基于OpenRLHF框架，设计5维混合奖励函数（工具选择、参数合法性、执行成功率、多步一致性、回答可用性），采用rule-based校验与Qwen2.5-72B打分相结合的策略，对Qwen2.5-7B/14B进行GRPO训练
- 结果：工具调用准确率从72%提升至88%（BFCL评测，+16pp），多步任务完成率从65%提升至83%（+18pp）；同等条件下对比DPO方法，GRPO优于DPO约5pp，与DeepSeek-R1论文结论一致
- 训练配置：8×A800，LoRA rank=64，3 epoch，lr=2e-5

**Agent自动化评测体系**
- 问题：模型迭代缺乏可量化的评测标准，依赖人工主观判断，迭代效率低
- 方案：参考AgentBench/ToolBench设计离线评测框架，覆盖工具选择、参数完整、任务完成、回答质量4个维度。工具选择/参数完整性采用rule-based精确匹配，回答质量采用LLM-as-Judge（Qwen2.5-72B pairwise对比模式）
- 结果：评测与人工标注一致性达87.3%（50组样本），接入CI实现模型更新自动回归评测，迭代周期从"凭感觉"转为数据驱动

**自动化训练数据构建**
- 问题：地图DeepSearch场景缺乏高质量Agent训练数据，人工标注成本高
- 方案：基于OpenManus框架搭建造数Pipeline，使用DeepSeek-V3生成8大场景地图Query，结合Web Search检索真实POI/路线信息，经格式校验→执行验证→质量过滤（LLM打分>0.7）三阶段筛选
- 结果：构建8w+条ReAct轨迹数据，其中SFT数据3w+条，GRPO偏好数据5w+对

**工具参数跟随优化**
- 问题：多工具链路下模型频繁漏填city_name、坐标等关键参数，导致工具调用失败需重试
- 方案：构造参数缺失、参数错位、城市歧义、品牌词识别、多轮参数继承6类hard case共2000+条，采用课程学习策略从易到难训练
- 结果：参数完整率从78%提升至91%（+13pp），因重试减少单次调用耗时从1.8s降至1.3s（-28%）

**工程支撑：**
- ReAct多步推理框架：Router区分快速查询（P90<800ms）与DeepSearch（平均3.2步，P90<4.5s），GRPO训练后推理步数从3.8步降至3.2步（-16%），端到端延迟降低约12%
- 路线规划链路：构建"API召回→语义选点→路线重算排序"三阶段，路线采纳率较基线提升15%
- Web Search增强：4路并行搜索+去重去噪+时间过滤+摘要压缩，结果可用率从61%提升至82%（+21pp）

---

### 项目二：AI出行打车Agent

基于自研eino Agent框架构建App内智能出行交易能力，支持意图识别、起终点补全与对话交易闭环。日均处理20万+次对话。

**Skill-based意图识别与上下文管理**
- 问题：多业务线（打车/低价/顺风车）工具集混合暴露导致Token浪费和意图混淆
- 方案：设计Skill Router渐进式上下文注入机制，先路由业务模块，再按需加载对应工具集与规则，同Skill多轮复用历史指令
- 结果：Token消耗降低35%，意图识别准确率96.2%（封闭域5分类，2w+测试样本）

**Memory系统设计**
- 问题：多轮对话中模型无法有效引用历史信息（地址偏好、历史订单、上轮工具结果），导致重复提问和上下文断裂
- 方案：设计长期画像/短期状态/按需召回三层Memory架构，基于Redis Sharded Memory拆分存储，调用前动态注入相关上下文（平均3.2条历史+1.5条画像）
- 结果：多轮对话历史信息有效引用率从41%提升至68%（+27pp）

**工程支撑：**
- 全链路可观测：TTFT P90<450ms，TPOT P90<35ms，端到端P90<3.2s，工具成功率97.5%，Skill路由准确率98.1%
- 思考流可视化：等待期间展示任务进度和中间结果，用户流失率降低18%

---

## 蚂蚁集团 · 多模态算法工程师（2024.09 - 2025.02）

### 项目一：短视频分发画像纠偏

面向Tab3短视频分发的人群偏差问题，设计基于多模态大模型的视频内容理解→分发人群预测全链路Pipeline。

**多模态SFT数据构建**
- 问题：短视频分发缺乏细粒度人群标签，人工标注效率低且一致性差
- 方案：基于视频ASR+OCR文本，设计"大模型生成→规则过滤→人工校验"三级数据流水线，使用GPT-4o生成5维度人群标签（年龄/性别/兴趣/消费力/活跃度），结合标签一致性校验和困难样本挖掘
- 结果：构建8w+高质量图文对SFT数据，标签准确率94.6%

**多模态大模型训练**
- 问题：通用VLM在视频分发人群预测任务上表现不足，需领域适配
- 方案：基于Qwen2-VL 2B/7B，使用LoRA（rank=128, alpha=256）+ DeepSpeed ZeRO-2进行多分类微调，训练数据涵盖影视/生活/知识/游戏/音乐5大视频类别
- 结果：2B模型Top-1准确率92.3%，7B模型Top-1准确率94.8%（Top-2分别为96.1%/97.8%）；消融实验LoRA rank=128较rank=64准确率提升1.8%

**模型量化与推理部署**
- 问题：7B模型线上推理成本高，GPU资源占用大
- 方案：AWQ 4-bit量化Qwen2-VL 7B，结合vLLM（continuous batching + PagedAttention）部署
- 结果：离线QPS从0.15提升至1.2（8×），线上GPU从22张降至12张（-45%），峰值QPS达22.8，P99<380ms

**业务成果：** 用户画像覆盖从5.3亿扩展至8.2亿，新内容长播放数+5.2%，长播放率+4.6%，新鲜度0d PV%+2.1%

---

### 项目二：低质量视频识别与过滤

面向短视频标题/封面与内容不符的问题，设计视频-图文匹配Pipeline，筛选标题党与合成视频。

**模型设计与训练**
- 问题：传统CLIP+BERT方案在中文视频场景下准确率低，对语义级不匹配检测能力弱
- 方案：标注4w+视频-图文对（匹配/部分匹配/不匹配三档），使用LoRA微调Qwen2-VL-2B，引入CoT推理机制（先生成视频内容描述，再判断匹配性），输入包含视频帧+关联文本+Qwen2-VL-72B生成的视频Caption
- 结果：相比CLIP+BERT+CosEnt Loss的Visual-BGE baseline，召回率90.2%（+4.2%），准确率89.1%（+19.1%）

**业务成果：** 上线3个月累计回刷15w+/日，筛选3200+异常视频，识别180+违规合成视频用户

---

## 开源项目

**Hermes Agent（贡献者，fork自NousResearch/hermes-agent）**
GitHub: flychen59/hermes-agent

自进化AI Agent框架贡献，15 commits，3000+行代码：

- macOS GUI自动化Agent：cliclick+AppleScript+Swift OCR闭环架构（截屏验证→OCR识别→坐标点击→结果校验），操作成功率85%→95%
- 反爬浏览器自动化：基于Patchright/CloakBrowser绕过BOSS直聘/猎聘反爬，支持验证码处理和多条件批量搜索
- 闲鱼/淘宝平台自动化：解决登录页JS设值不触发前端框架状态更新的问题（execCommand insertText方案），实测记录iOS App在macOS上0窗口限制及闲鱼反爬策略
- 多Agent共享Skill框架+Skill进化引擎，Agent自动从复杂任务提取可复用工作流
- 修复多轮对话丢消息（消息合并/去重/上下文压缩）

**AI日报生成器**
GitHub: flychen59/ai-company | flychen59/ai-daily-report

- 基于CrewAI的多Agent协作系统（研究员→编辑→分析师→审查员），自动生成GitHub高星项目日报
- LLM: Kimi-K2.6，数据源: GitHub Trending + DuckDuckGo，持续运行3个月+，每日发布到GitHub Pages

**简历优化Agent（resume-optimizer）**
GitHub: flychen59/hermes-agent（agents/agent-registry/resume-optimizer）

- 5 Agent协作的简历优化系统：JD解析→差距分析→STAR重写→数值审核→质量闭环
- 内置岗位动态监控：招聘网站采集器（CloakBrowser反爬）+ GitHub高星日报生成器
- 数值校验模块：基于论文理论值自动验证简历数据合理性
- 6个可复用Skill模块，支持新任务快速接入

**MNBVC多模态语料**
GitHub: flychen59/Arxiv_mllm_mnbvc（⭐1）| flychen59/chinaxivCrawler_mnbvc（⭐3）

- 构建Arxiv论文多模态结构化数据库（LaTeX→JSON），Ray分布式处理2000+篇论文
- 提取图片/表格/公式等多模态数据，按排版顺序存为Parquet，吞吐量50文件/分钟

**OpenClaw Agent框架（自建部署）**

- 独立部署运维，飞书Bot消息路由+多模型provider热切换（Qwen3.5-plus/GLM-5.1/Kimi-K2.5/MiniMax-M2.5）
- MCP Server（Streamable HTTP）+ Skill插件系统 + SOUL.md行为准则

---

## 教育背景

- 东国大学 | 硕士 | 人工智能专业（全英文授课）
- 汉阳大学 | 交流研究 | 人工智能方向
- 青岛科技大学 | 本科 | 计算机相关专业

发表论文3篇：SCI Q1 1篇（多视图立体重建，CNN+Transformer异构融合），韩国会议2篇（行车记录仪前景分割，无监督聚类方法，其中KMMS 2023获优秀论文奖）

---

## 技能

- Agent算法：ReAct / Multi-Agent / Tool Use / GRPO强化学习 / Memory设计 / Agent评测（LLM-as-Judge）
- 大模型训练：LoRA/QLoRA / DeepSpeed ZeRO / OpenRLHF / SFT数据构建 / 偏好对齐
- 多模态：Qwen2-VL / CLIP / ViT / 视频理解 / ASR+OCR / 多模态数据处理与对齐
- 模型部署：vLLM / AWQ量化 / continuous batching / PagedAttention
- 工程：Python / Go / Redis / Ray / Docker / Linux
- 语言：英语（托福79）/ 韩语（TOPIK 4）/ 可无障碍阅读英文论文和技术文档

---

## 荣誉

- KMMS 2023 韩国多媒体工学秋季学会 优秀论文奖
- 东国大学 全额奖学金（SRD）
- 汉阳大学 优秀毕业生（120人取10）/ TOPIK语言奖学金
- 青岛科技大学 三等奖学金 ×2
