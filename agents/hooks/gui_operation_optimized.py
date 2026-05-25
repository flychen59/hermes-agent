#!/usr/bin/env python3
"""优化的 GUI 操作执行器

集成所有优化：
1. 并发检测 - 防止用户操作干扰
2. 错误恢复 - 自动重试 + 反思调整
3. 速度优化 - 截屏缓存 + 窗口位置缓存
"""

import json
import re
import subprocess
import sys
import time
from pathlib import Path

# 获取 hooks 目录
HOOKS_DIR = Path(__file__).parent


def execute_gui_operation_optimized(operation: str) -> dict:
    """执行优化的 GUI 操作
    
    Args:
        operation: 操作描述，如 "激活 WeChat"、"点击微信第一个对话"
    
    Returns:
        结果字典，包含所有阶段的状态
    """
    
    results = {
        "operation": operation,
        "stages": [],
        "optimizations": {
            "concurrency_detection": False,
            "error_recovery": False,
            "speed_optimization": False
        },
        "success": False
    }
    
    # ── Stage 1: 并发检测 ───────────────────────────────────
    concurrency_hook = HOOKS_DIR / "concurrency_check.py"
    
    if concurrency_hook.exists():
        results["optimizations"]["concurrency_detection"] = True
        
        # 检测用户是否有操作
        check_result = subprocess.run(
            [sys.executable, str(concurrency_hook), "detect"],
            capture_output=True, text=True
        )
        
        if "用户正在操作" in check_result.stdout or "鼠标移动" in check_result.stdout:
            # 等待用户停止操作
            wait_result = subprocess.run(
                [sys.executable, str(concurrency_hook), "wait", "5"],
                capture_output=True, text=True
            )
            
            results["stages"].append({
                "stage": "concurrency_detection",
                "status": "waited",
                "output": wait_result.stdout
            })
        else:
            results["stages"].append({
                "stage": "concurrency_detection",
                "status": "passed",
                "output": "用户未操作，可以继续"
            })
    
    # ── Stage 2: 前置权限检查 ───────────────────────────────────
    pre_hook = HOOKS_DIR / "pre_gui_hook.py"
    
    if pre_hook.exists():
        pre_result = subprocess.run(
            [sys.executable, str(pre_hook), operation],
            capture_output=True, text=True
        )
        
        results["stages"].append({
            "stage": "pre_hook",
            "status": "success" if pre_result.returncode == 0 else "failed",
            "output": pre_result.stdout[:500] if pre_result.stdout else ""
        })
        
        if pre_result.returncode != 0:
            # 前置检查失败，停止执行
            results["success"] = False
            results["error"] = "前置检查失败"
            return results
    
    # ── Stage 3: 执行操作（带错误恢复） ─────────────────────────────
    error_recovery_hook = HOOKS_DIR / "error_recovery.py"
    
    # 解析操作类型
    if re.search(r'(激活|打开|切换到?)(.+)', operation):
        match = re.search(r'(激活|打开|切换到?)(.+)', operation)
        app_name = match.group(2).strip()
        
        if error_recovery_hook.exists():
            results["optimizations"]["error_recovery"] = True
            
            # 使用错误恢复机制执行
            exec_result = subprocess.run(
                [sys.executable, str(error_recovery_hook), "activate", app_name],
                capture_output=True, text=True
            )
            
            results["stages"].append({
                "stage": "execution_with_recovery",
                "status": "success" if "操作成功" in exec_result.stdout else "failed",
                "output": exec_result.stdout
            })
        else:
            # 直接执行
            exec_result = subprocess.run(
                ['osascript', '-e', f'tell application "{app_name}" to activate'],
                capture_output=True, text=True
            )
            
            results["stages"].append({
                "stage": "execution",
                "status": "success" if exec_result.returncode == 0 else "failed",
                "output": exec_result.stdout
            })
    
    elif re.search(r'(点击|click)(.+)', operation):
        # 点击操作
        match = re.search(r'点击\s+(\S+)\s+(\d+)\s+(\d+)', operation)
        if match:
            app = match.group(1)
            x = int(match.group(2))
            y = int(match.group(3))
            
            if error_recovery_hook.exists():
                results["optimizations"]["error_recovery"] = True
                
                exec_result = subprocess.run(
                    [sys.executable, str(error_recovery_hook), "click", app, str(x), str(y)],
                    capture_output=True, text=True
                )
                
                results["stages"].append({
                    "stage": "execution_with_recovery",
                    "status": "success" if "操作成功" in exec_result.stdout else "failed",
                    "output": exec_result.stdout
                })
    
    else:
        # 默认操作
        results["stages"].append({
            "stage": "execution",
            "status": "skipped",
            "output": "操作类型未识别"
        })
    
    # ── Stage 4: 速度优化截屏 ───────────────────────────────────
    speed_hook = HOOKS_DIR / "speed_optimization.py"
    
    if speed_hook.exists():
        results["optimizations"]["speed_optimization"] = True
        
        # 使用快速截屏
        screenshot_result = subprocess.run(
            [sys.executable, str(speed_hook), "test"],
            capture_output=True, text=True
        )
        
        results["stages"].append({
            "stage": "screenshot_optimized",
            "status": "success",
            "output": screenshot_result.stdout[:300]
        })
    else:
        # 普通截屏
        screenshot_path = Path.home() / ".openclaw" / "workspace" / f"screen_{int(time.time())}.png"
        subprocess.run(['screencapture', str(screenshot_path)], capture_output=True)
        
        results["stages"].append({
            "stage": "screenshot",
            "status": "success",
            "output": str(screenshot_path)
        })
    
    # ── Stage 5: 后置验证 ───────────────────────────────────
    post_hook = HOOKS_DIR / "post_gui_hook.py"
    
    if post_hook.exists():
        post_result = subprocess.run(
            [sys.executable, str(post_hook), operation],
            capture_output=True, text=True
        )
        
        results["stages"].append({
            "stage": "post_hook",
            "status": "success" if post_result.returncode == 0 else "failed",
            "output": post_result.stdout[:500] if post_result.stdout else ""
        })
    
    # ── 最终结果 ───────────────────────────────────
    # 判断是否所有关键阶段都成功
    key_stages = ["concurrency_detection", "execution", "execution_with_recovery", "post_hook"]
    failed_stages = [s for s in results["stages"] if s["stage"] in key_stages and s["status"] == "failed"]
    
    results["success"] = len(failed_stages) == 0
    
    return results


def main():
    """CLI 入口"""
    if len(sys.argv) < 2:
        print("用法:")
        print("  python gui_operation_optimized.py <operation>")
        print("  python gui_operation_optimized.py '激活 WeChat'")
        print("  python gui_operation_optimized.py '点击 Runner 100 100'")
        return
    
    operation = sys.argv[1]
    
    result = execute_gui_operation_optimized(operation)
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()