---
name: web-research
description: 通用网络调研，搜索技术方案、API 文档、最佳实践
version: 1.0.0
metadata:
  hermes:
    tags: [research, web, search, documentation]
    related_skills: [arxiv-search, paper-summary]
  evolution:
    use_count: 0
    last_used: ""
    success_rate: 0.0
    auto_evolve: true
---

# 网络调研

## 使用场景
- 调研技术方案和 API
- 搜索开源项目
- 查找文档和最佳实践

## 步骤

1. **明确调研目标** — 从用户消息提取：
   - 调研主题
   - 期望输出（列表/对比/教程）
   - 时效性要求

2. **多源搜索**
   - GitHub（项目、star 数、活跃度）
   - 官方文档（API reference）
   - 技术博客（实现细节）
   - Stack Overflow（常见问题）

3. **信息提取**
   - 每个来源提取关键信息
   - 对比不同方案的优劣
   - 注意时效性（标注日期）

4. **结构化输出**
   ```
   ## 调研结果：{topic}
   
   ### 方案对比
   | 方案 | 优势 | 劣势 | 适用场景 |
   
   ### 推荐
   基于分析推荐...
   
   ### 参考
   - [来源1](url)
   ```

5. **知识入库** — 重要发现写入 `knowledge/` 目录

## 陷阱
- 不要只看第一页结果
- 注意文章发布日期，避免过时信息
- GitHub 项目看 last commit 时间和 issue 活跃度
