"""
Resume Optimizer Agent - 多Agent协作简历优化系统

流程: JD解析 + 简历分析 (并行) → 差距分析 → 简历重写 → 数值审核 → 质量闭环
"""

import json
import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AgentState:
    """共享状态，在Agent间传递"""
    jd_text: str = ""
    resume_text: str = ""
    target_role: str = ""
    # 各阶段输出
    jd_requirements: dict = field(default_factory=dict)
    resume_analysis: dict = field(default_factory=dict)
    gap_report: dict = field(default_factory=dict)
    optimized_resume: str = ""
    review_report: dict = field(default_factory=dict)
    # 质量闭环
    retry_count: int = 0
    max_retries: int = 3
    passed: bool = False


# ─── Agent 角色定义 ───────────────────────────────────────────

AGENTS = {
    "jd-parser": {
        "role": "JD解析师",
        "prompt": """你是JD解析师。从岗位描述中提取结构化需求：

输出JSON格式：
{{
  "keywords": {{"技能名": 出现次数}},
  "required_skills": ["技能1", "技能2"],
  "preferred_skills": ["技能1", "技能2"],
  "experience_requirements": ["要求1", "要求2"],
  "industry_terms": ["术语1", "术语2"],
  "job_level": "初级/中级/高级",
  "key_metrics": ["考核指标1", "考核指标2"]
}}

JD文本：
{jd_text}"""
    },
    "resume-analyst": {
        "role": "简历分析师",
        "prompt": """你是简历分析师。全面诊断简历质量：

输出JSON格式：
{{
  "structure_score": 0-100,
  "content_score": 0-100,
  "numerical_values": [
    {{"value": "72%→88%", "context": "工具调用准确率", "assessment": "合理/偏高/偏低/模糊"}}
  ],
  "strengths": ["优点1", "优点2"],
  "weaknesses": ["弱点1", "弱点2"],
  "missing_sections": ["缺少的部分"],
  "ats_compatibility_score": 0-100
}}

简历文本：
{resume_text}"""
    },
    "gap-analyzer": {
        "role": "差距分析师",
        "prompt": """你是差距分析师。对比JD需求和简历现状，制定优化方向：

JD需求：
{jd_requirements}

简历诊断：
{resume_analysis}

目标岗位：{target_role}

输出JSON格式：
{{
  "critical_gaps": [{{"gap": "差距描述", "priority": "高/中/低", "action": "建议动作"}}],
  "keyword_embedding_plan": [{{"keyword": "关键词", "target_section": "放在简历哪个部分"}}],
  "quantification_suggestions": [{{"item": "需要量化的内容", "suggested_metrics": "建议的量化指标"}}],
  "restructure_plan": ["结构优化建议"],
  "focus_strategy": "核心定位策略描述"
}}"""
    },
    "resume-writer": {
        "role": "简历重写师",
        "prompt": """你是简历重写师。基于优化方向重写简历：

核心原则：
1. 每条经历用"问题→方案→结果"结构
2. 数值要有论文/行业数据支撑
3. 嵌入JD关键词但自然不堆砌
4. 突出Agent算法能力（主线）+ 多模态训练能力（差异化）

优化方向：
{gap_report}

原始简历：
{resume_text}

审核反馈（如有）：
{review_feedback}

请直接输出优化后的完整简历文本。"""
    },
    "data-reviewer": {
        "role": "数值审核员",
        "prompt": """你是数值审核员。校验简历中所有数值的合理性：

校验标准（基于论文和行业实验数据）：
- GRPO训练后工具调用提升：12-18pp合理
- 多步任务完成率提升：10-18pp合理
- 参数完整率提升：12-16pp合理
- 延迟降幅：15-30%合理
- 模型准确率：取决于模型大小和任务类型
- QPS提升倍数：取决于优化手段

简历文本：
{optimized_resume}

输出JSON格式：
{{
  "total_values": 总数值个数,
  "passed": 通过个数,
  "warning": 需关注个数,
  "failed": 不合理个数,
  "details": [
    {{"value": "数值", "context": "上下文", "verdict": "pass/warn/fail", "reason": "判断依据"}}
  ],
  "overall_pass": true/false,
  "revision_suggestions": ["修改建议"]
}}"""
    }
}


# ─── Skill 模块 ──────────────────────────────────────────────

def keyword_extractor(jd_text: str) -> dict:
    """从JD中提取关键词频率（简单实现，实际可接LLM）"""
    # 预定义的技能关键词库
    SKILL_KEYWORDS = [
        "Agent", "LLM", "Multi-Agent", "RAG", "ReAct", "GRPO", "LoRA",
        "DeepSpeed", "vLLM", "量化", "部署", "Prompt", "Memory",
        "Vector DB", "工具调用", "Function Calling", "SFT", "DPO",
        "多模态", "OCR", "视频理解", "CLIP", "ViT", "Transformers",
    ]
    freq = {}
    for kw in SKILL_KEYWORDS:
        count = jd_text.lower().count(kw.lower())
        if count > 0:
            freq[kw] = count
    return dict(sorted(freq.items(), key=lambda x: -x[1]))


def gap_analyzer(jd_req: dict, resume_analysis: dict) -> dict:
    """计算JD-简历匹配差距"""
    jd_skills = set(jd_req.get("required_skills", []) + jd_req.get("preferred_skills", []))
    resume_strengths = set(resume_analysis.get("strengths", []))
    
    # 简单的关键词匹配
    resume_text_lower = str(resume_analysis).lower()
    covered = {s for s in jd_skills if s.lower() in resume_text_lower}
    gaps = jd_skills - covered
    
    return {
        "total_requirements": len(jd_skills),
        "covered": len(covered),
        "gap_count": len(gaps),
        "match_rate": f"{len(covered)}/{len(jd_skills)}" if jd_skills else "N/A",
        "gaps": list(gaps),
    }


def star_method_writer(experience_text: str) -> str:
    """STAR法则改写模板提示"""
    return f"""请用STAR法则改写以下经历：

Situation: 背景和问题是什么
Task: 你的具体任务是什么
Action: 你采取了什么方案和技术手段
Result: 产生了什么可量化的效果

原始经历：
{experience_text}

改写要求：
- 用"问题→方案→结果"结构
- 每个结果都要有具体数值
- 数值要有依据（论文/行业数据）
- 不要口语化，用简洁书面语
"""


def data_validator(value: str, context: str, category: str) -> dict:
    """数值合理性校验"""
    # 论文理论值范围参考表
    RANGES = {
        "tool_call_accuracy_gain": (10, 20),   # pp
        "multi_step_completion_gain": (10, 18), # pp
        "param_completeness_gain": (12, 16),    # pp
        "latency_reduction": (15, 30),          # %
        "accuracy_2b_vlm": (88, 95),            # %
        "accuracy_7b_vlm": (92, 97),            # %
        "qps_improvement": (3, 10),             # ×
    }
    
    if category in RANGES:
        low, high = RANGES[category]
        # 尝试从value中提取数字
        import re
        nums = re.findall(r'[\d.]+', value)
        if nums:
            num = float(nums[-1])
            in_range = low <= num <= high
            return {
                "value": value,
                "context": context,
                "range": f"{low}-{high}",
                "in_range": in_range,
                "verdict": "pass" if in_range else "warn"
            }
    
    return {"value": value, "context": context, "verdict": "skip", "reason": "无参考范围"}


def resume_formatter(resume_text: str) -> str:
    """简历格式化：统一标题、间距、符号"""
    lines = resume_text.split('\n')
    formatted = []
    for line in lines:
        # 确保标题行有分隔
        if line.startswith('#') or line.startswith('━') or line.startswith('═'):
            formatted.append('')
        formatted.append(line)
    return '\n'.join(formatted)


# ─── 编排引擎 ─────────────────────────────────────────────────

class ResumeOptimizer:
    """简历优化编排器"""
    
    def __init__(self):
        self.state = AgentState()
    
    def run(self, jd_text: str, resume_text: str, target_role: str = "") -> dict:
        """
        执行简历优化全流程
        
        Args:
            jd_text: 岗位描述文本
            resume_text: 原始简历文本
            target_role: 目标岗位名称
            
        Returns:
            优化结果字典
        """
        self.state = AgentState(
            jd_text=jd_text,
            resume_text=resume_text,
            target_role=target_role,
        )
        
        # Stage 1: 并行 - JD解析 + 简历分析
        print("📋 Stage 1: JD解析 + 简历分析（并行）")
        # 实际使用时由LLM填充，这里用Skill预处理
        self.state.jd_requirements = {"keywords": keyword_extractor(jd_text)}
        self.state.resume_analysis = {"raw_length": len(resume_text)}
        
        # Stage 2: 差距分析
        print("📊 Stage 2: 差距分析")
        self.state.gap_report = gap_analyzer(
            self.state.jd_requirements, 
            self.state.resume_analysis
        )
        
        # Stage 3: 重写 + 审核循环
        for attempt in range(self.state.max_retries + 1):
            print(f"✍️  Stage 3: 简历重写（第{attempt + 1}次）")
            # resume_writer prompt 模板
            writer_prompt = AGENTS["resume-writer"]["prompt"].format(
                gap_report=json.dumps(self.state.gap_report, ensure_ascii=False, indent=2),
                resume_text=self.state.resume_text,
                review_feedback=json.dumps(
                    self.state.review_report.get("revision_suggestions", []),
                    ensure_ascii=False
                ) if self.state.review_report else "无（首次重写）"
            )
            
            # 实际使用时交给LLM执行，这里存储prompt
            self.state.optimized_resume = writer_prompt
            
            # Stage 4: 数值审核
            print("🔍 Stage 4: 数值审核")
            reviewer_prompt = AGENTS["data-reviewer"]["prompt"].format(
                optimized_resume=self.state.optimized_resume
            )
            
            # 模拟审核（实际由LLM执行）
            self.state.review_report = {
                "total_values": 0,
                "passed": 0,
                "warning": 0,
                "failed": 0,
                "overall_pass": True,
                "details": [],
                "revision_suggestions": []
            }
            
            if self.state.review_report["overall_pass"]:
                self.state.passed = True
                print("✅ 审核通过！")
                break
            else:
                self.state.retry_count += 1
                print(f"⚠️  审核未通过，重试 {self.state.retry_count}/{self.state.max_retries}")
        
        if not self.state.passed:
            print("⚠️  达到最大重试次数，输出当前最优版本（标记需人工审核）")
        
        return {
            "optimized_resume": self.state.optimized_resume,
            "review_report": self.state.review_report,
            "gap_report": self.state.gap_report,
            "jd_requirements": self.state.jd_requirements,
            "resume_analysis": self.state.resume_analysis,
            "retry_count": self.state.retry_count,
            "passed": self.state.passed,
        }
    
    def get_agent_prompt(self, agent_id: str) -> str:
        """获取指定Agent的prompt模板"""
        if agent_id not in AGENTS:
            raise ValueError(f"Unknown agent: {agent_id}. Available: {list(AGENTS.keys())}")
        
        agent = AGENTS[agent_id]
        return agent["prompt"].format(
            jd_text=self.state.jd_text,
            resume_text=self.state.resume_text,
            target_role=self.state.target_role,
            jd_requirements=json.dumps(self.state.jd_requirements, ensure_ascii=False, indent=2),
            resume_analysis=json.dumps(self.state.resume_analysis, ensure_ascii=False, indent=2),
            gap_report=json.dumps(self.state.gap_report, ensure_ascii=False, indent=2),
            optimized_resume=self.state.optimized_resume,
            review_feedback=json.dumps(
                self.state.review_report.get("revision_suggestions", []),
                ensure_ascii=False
            ) if self.state.review_report else "无"
        )


# ─── 入口 ─────────────────────────────────────────────────────

if __name__ == "__main__":
    # 示例用法
    optimizer = ResumeOptimizer()
    
    jd = """AI Agent算法工程师，要求：熟悉ReAct/GRPO/Tool Use，
    有大模型训练经验（LoRA/DeepSpeed），了解多模态（CLIP/ViT），
    会模型部署（vLLM/AWQ量化）。"""
    
    resume = """张三，3年经验，做过LLM相关工作。"""
    
    result = optimizer.run(jd_text=jd, resume_text=resume, target_role="AI Agent算法工程师")
    print(json.dumps(result["gap_report"], ensure_ascii=False, indent=2))
