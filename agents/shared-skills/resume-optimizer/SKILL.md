---
name: resume-optimizer
version: 1.0.0
description: 多Agent协作简历优化 — JD解析→差距分析→STAR重写→数值审核→质量闭环
author: flychen59
tags: [resume, multi-agent, career, optimization]
triggers:
  - "改简历"
  - "优化简历"
  - "简历优化"
  - "resume"
---

# Resume Optimizer Skill

多Agent协作简历优化系统。输入JD + 原始简历，输出针对目标岗位的优化简历。

## 架构

5个专职Agent + 6个可复用Skill模块 + DAG编排 + 质量闭环。

参考框架：CrewAI（角色定义）+ LangGraph（DAG流程控制）。

## 调用方式

### 方式一：直接调用

```
请帮我优化简历，目标岗位是 AI Agent算法工程师。
简历原文：[粘贴简历]
JD：[粘贴岗位描述]
```

### 方式二：提供文件

```
请优化我的简历，简历在 /tmp/resume_raw.txt，JD在 /tmp/jd.txt，目标岗位：AI Agent算法工程师
```

## 执行流程

### Stage 1：并行分析（JD解析 + 简历分析同时进行）

**Agent: JD解析师**
- 提取岗位关键词（技能、工具、经验要求）
- 统计关键词频率
- 识别显性和隐性要求
- 输出：结构化需求清单

**Agent: 简历分析师**
- 诊断简历结构和内容质量
- 提取所有数值并初步评估
- 识别强项和弱项
- 输出：简历诊断报告

### Stage 2：差距分析

**Agent: 差距分析师**
- 对比JD需求和简历现状
- 识别关键差距，按优先级排序
- 制定关键词嵌入计划
- 输出：优化方向文档

### Stage 3：简历重写

**Agent: 简历重写师**
- 按STAR法则改写每条经历
- 统一"问题→方案→结果"结构
- 嵌入JD关键词（自然不堆砌）
- 数值量化，要有论文/行业数据支撑
- 输出：优化后简历

### Stage 4：数值审核 + 质量闭环

**Agent: 数值审核员**
- 校验所有数值合理性
- 对比论文理论值范围：
  - GRPO训练提升：12-18pp
  - 多步完成率提升：10-18pp
  - 参数完整率提升：12-16pp
  - 延迟降幅：15-30%
  - VLM准确率：2B 88-95%, 7B 92-97%
- 审核通过 → 输出最终简历
- 审核不通过 → 回到Stage 3重写（最多3次）

## 可复用Skill模块

| Skill | 文件 | 功能 |
|-------|------|------|
| keyword_extractor | skills/ | JD关键词提取+频率统计 |
| gap_analyzer | skills/ | JD-简历匹配度计算 |
| star_method_writer | skills/ | STAR法则改写模板 |
| data_validator | skills/ | 数值合理性校验 |
| resume_formatter | skills/ | 简历格式化输出 |
| job-site-scraping | external/ | 招聘网站岗位搜索与JD批量抓取（BOSS直聘等） |
| github-trending | external/ | GitHub高星项目日报自动生成（技术趋势追踪） |

## 岗位动态监控（亮点功能）

系统内置两个信息采集模块，支持实时关注业界动态：

1. **job-site-scraping**：基于CloakBrowser反爬的招聘网站采集器
   - 绕过BOSS直聘/猎聘反爬，批量搜索岗位+抓取JD
   - 支持多条件组合搜索（城市+关键词+薪资范围）
   - 输出结构化JSON（岗位名/公司/JD/薪资/要求）
   - 可定时运行，监控新增岗位

2. **github-trending**：GitHub高星项目日报生成器
   - 4 Agent协作（研究员→编辑→分析师→审查员）
   - 自动发现热门技术方向和新兴工具
   - 每日生成HTML日报，发布到GitHub Pages
   - 帮助简历优化师了解最新技术栈和行业趋势

这两个模块让简历优化不再是静态改写，而是**基于实时市场数据**的动态优化。

## 数值校验参考表

| 指标类别 | 合理范围 | 论文来源 |
|---------|---------|---------|
| GRPO工具调用提升 | 10-20pp | Qwen2.5 TR, DeepSeek-R1 |
| GRPO vs DPO增益 | +3~5pp | DeepSeek-R1 |
| 多步完成率提升 | 10-18pp | ReAct, OpenRLHF |
| 参数完整率提升 | 12-16pp | BFCL, ToolBench |
| 延迟降幅 | 15-30% | ReAct步数缩减 |
| ReAct平均步数 | 3-5步 | 出行场景典型值 |
| 7B VLM Top-1准确率 | 92-97% | Qwen2-VL TR |
| AWQ量化QPS提升 | 3-10× | AWQ论文 |
| LLM-as-Judge一致性 | 75-90% | MT-Bench论文 |

## 输出格式

1. `resume_final.md` — 优化后的完整简历
2. `resume_review.md` — 数值审核报告
3. `gap_report.md` — 差距分析和优化方向

## 注意事项

- 蚂蚁等不需要改的部分不要动，只改用户指定的部分
- 数值要有论文依据，不要编造离谱的数据
- 保持"问题→方案→结果"的书面语结构
- 最终版本需要出文字版（给业务老板看的，不是数字堆砌）

## 改动记录

- 2026-05-28: v1.0.0 初始版本，5 Agent + 6 Skill + 质量闭环
