陈逸鹏
手机: 15069104076 | 邮箱: chenyipeng0509@gmail.com | 所在地: 北京
GitHub: github.com/flychen59
意向：大模型算法工程师（Agent方向）

---

## 滴滴出行 · Agent算法工程师（2025.04至今）

### 项目一：Map-DeepSearch Agent

面向出行垂类的多步推理搜索Agent，支持沿途搜索、多点路线规划、周边搜索等复杂决策场景，核心能力（Tool Use/多步规划/RL训练）可直接迁移至汽车、本地生活等垂类场景。日均服务50万+次查询。

**GRPO强化学习训练工具调用能力**
- 问题：Qwen2.5基座模型在多工具场景下工具选择和参数填充准确率不足（72%），影响复杂查询完成率
- 方案：基于OpenRLHF框架，设计规则Reward + LLM-as-Judge混合奖励函数（覆盖工具选择正确性、参数合法性、执行成功率、多步规划一致性、回答可用性5个维度），对Qwen2.5-7B/14B进行GRPO训练，同步对比DPO验证GRPO优越性。训练中引入CoT引导模型自主分解复杂查询为多步工具调用计划，通过多轮rollout实现Self-Refine策略迭代
- 结果：工具调用准确率72%→88%（+16pp），多步任务完成率65%→83%（+18pp）；GRPO优于DPO约5pp，与DeepSeek-R1论文结论一致
- 训练配置：8×A800，LoRA rank=64，3 epoch，lr=2e-5

**工具参数跟随优化**
- 问题：模型频繁漏填city_name、起终点坐标、query_slm等关键参数，导致工具调用失败需重试
- 方案：构造参数缺失、参数错位、城市歧义、品牌词识别等hard case专项训练集，提升模型对工具schema的跟随能力
- 结果：参数完整率78%→91%（+13pp），因重试减少单次调用耗时从1.8s降至1.3s（-28%）

**自动化训练数据构建**
- 问题：出行垂类缺乏高质量Agent训练数据，通用数据集（ToolBench、API-Bank）与地图场景偏差大
- 方案：基于OpenManus/ReAct轨迹格式搭建造数Pipeline：(1) DeepSeek-V3/GLM生成多样化地图Query，结合WebSearch检索真实POI/路线背景；(2) ReAct Agent采集轨迹（12工具+WebSearch，平均3.2步/条）；(3) 格式校验→执行验证→LLM质量打分三阶段过滤，最终8w+条高质量轨迹，按质量分级构造SFT数据（3w+）和GRPO偏好对（5w+）
- 结果：造数效率提升约50倍（单条成本50元→<1元），覆盖地点搜索/附近搜索/沿途搜索/多点路线/家司上下文等场景

**Agent评测体系**
- 问题：模型迭代缺乏可量化的评测标准，依赖人工主观判断
- 方案：搭建3k+离线评测集，覆盖工具选择、参数完整性、执行成功率、多步规划一致性、回答质量5个维度。工具选择/参数完整性采用规则匹配，回答质量引入LLM-as-Judge pairwise对比
- 结果：接入CI实现模型更新自动回归评测，迭代周期从"凭感觉"转为数据驱动

---

### 项目二：工具策略算法优化

**沿途搜索：多路召回 + 语义筛选 + 真实路线复排**
- 问题：沿途找点单一依赖路线缓冲区检索，漏召回率高，推荐结果未经真实路线验证
- 方案：构建"地图API召回 + POI Selector语义筛选（基于NLP的细粒度意图理解与POI匹配） + 真实路线重算排序"方案：并发召回品牌词/细分类/大类候选，按poi_id去重后结合baseline路线计算实际绕路距离和时间，输出Top推荐路线
- 结果：沿途推荐采纳率较原始检索方案提升约15%

**周边搜索：分层召回 + LCS去重保多样性**
- 问题：单query检索召回率低，同址重复和母子POI干扰严重
- 方案：升级为"多query × 多类目 × 多半径"分层召回，引入POI Selector轻量重排、poi_id去重和LCS地址相似度去重，减少同址重复点和母子POI干扰
- 结果：离线有效召回率68%→84%（+16pp），重复POI比例下降约30%

**多点最短路径：Held-Karp动态规划**
- 问题：多点规划需对N个途经点排列求最短总距离，暴力枚举复杂度O(n!)
- 方案：基于两两路线距离矩阵建模多点访问顺序问题，使用Held-Karp动态规划替代全排列枚举（O(n²·2ⁿ)），支持固定起终点、无序途经点和起终点相同等case
- 结果：5点规划耗时3.2s→0.8s（-75%），4点以内<500ms

**WebSearch外部知识增强**
- 问题：网页结果噪声大、过期信息多、与地图POI粒度不一致
- 方案：支持多query并发搜索 + 网页结果清洗 + 时效过滤 + 摘要压缩 + 地图POI回查约束
- 结果：Web结果可用率61%→82%（+21pp）

**上下文减耗优化**
- 问题：旧版重型history replay导致上下文token浪费，复杂查询推理步数多
- 方案：将旧版history replay收缩为当前Agent执行态transcript，POI/route等结构化结果按poi_id/route_id存入mem缓存，避免工具结果反复拼接进上下文
- 结果：平均上下文token降低约20%，复杂查询推理步数减少0.6步，端到端耗时降低约10%

**工程框架：MapSearch/DeepSearch双模式Agent**
- 基于Manus/ToolCallAgent搭建双模式框架，Router区分快速查询（P90<800ms）与DeepSearch（平均3.2步，P90<4.5s），按场景装配定位/POI检索/周边搜/沿途搜/路线规划/WebSearch工具链

---

### 项目三：对话交易Agent

基于自研eino Agent框架构建App内智能出行交易能力。日均处理20万+次对话。

**Skill-based意图识别与Memory系统**
- 设计Skill Router渐进式上下文注入，Token消耗降低35%，意图识别准确率96.2%
- 设计长期画像/短期状态/按需召回三层Memory，历史信息有效引用率41%→68%（+27pp）
- 全链路可观测：TTFT P90<450ms，TPOT P90<35ms，端到端P90<3.2s，工具成功率97.5%

---

## 蚂蚁集团 · 多模态算法工程师（2024.09 - 2025.02）

### 短视频分发画像纠偏

面向短视频分发的人群偏差问题，设计基于多模态大模型的视频内容理解→分发人群预测全链路Pipeline。

**多模态SFT数据构建** — "大模型生成→规则过滤→人工校验"三级流水线，GPT-4o生成5维度人群标签，8w+图文对，准确率94.6%

**多模态大模型训练** — Qwen2-VL 2B/7B + LoRA(rank=128) + DeepSpeed ZeRO-2，7B Top-1准确率94.8%；消融实验rank=128较rank=64提升1.8%

**模型量化与推理部署** — AWQ 4-bit + vLLM（continuous batching + PagedAttention），QPS 0.15→1.2（8×），GPU 22张→12张（-45%），P99<380ms

**业务成果：** 画像覆盖5.3亿→8.2亿，新内容长播放数+5.2%，长播放率+4.6%

### 低质量视频识别

标注4w+视频-图文对，LoRA微调Qwen2-VL-2B + CoT推理机制，召回率90.2%（+4.2%），准确率89.1%（+19.1%）

---

## 开源项目

**Hermes Agent**（fork自NousResearch/hermes-agent）
- macOS GUI自动化Agent：截屏→OCR→点击→校验闭环，操作成功率85%→95%
- 多Agent共享Skill框架+Skill进化引擎
- 修复多轮对话丢消息（消息合并/去重/上下文压缩）

**AI日报生成器**（flychen59/ai-daily-report）
- CrewAI多Agent协作系统，持续运行3个月+，每日发布GitHub Pages

**MNBVC多模态语料**（flychen59/Arxiv_mllm_mnbvc）
- Ray分布式处理2000+篇论文，LaTeX→JSON多模态结构化数据库

---

## 教育背景

- 东国大学 | 硕士 | 人工智能（全英文授课）
- 汉阳大学 | 交流研究 | 人工智能
- 青岛科技大学 | 本科 | 计算机

论文3篇：SCI Q1 1篇（多视图立体重建，CNN+Transformer异构融合），韩国会议2篇（前景分割，无监督聚类，KMMS 2023优秀论文奖）

---

## 技能

- Agent算法：ReAct / Tool Use / Function Calling / GRPO强化学习 / CoT / Memory设计 / Agent评测
- RL训练：DPO / GRPO / RLHF / 偏好数据构建 / Reward Model / OpenRLHF
- 多模态：Qwen2-VL / 视频理解 / CLIP / ViT / 多模态数据处理
- 大模型训练：LoRA/QLoRA / DeepSpeed ZeRO / SFT数据构建 / 偏好对齐
- 检索与排序：RAG / 多路召回 / 语义筛选 / 距离矩阵DP优化
- 模型部署：vLLM / AWQ量化 / continuous batching / PagedAttention
- 工程：Python / Go / Redis / Ray / Docker / Linux
- 语言：英语（托福79）/ 韩语（TOPIK 4）/ 可无障碍阅读英文论文和技术文档

---

## 荣誉

- KMMS 2023 韩国多媒体工学秋季学会 优秀论文奖
- 东国大学 全额奖学金（SRD）
- 汉阳大学 优秀毕业生（120人取10）/ TOPIK语言奖学金
