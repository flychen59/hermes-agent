#!/usr/bin/env python3
"""GUI 操作前置 Hook — 安全检查

在执行 GUI 操作前进行安全检查：
- 检查权限状态
- 验证操作类型安全性
- 记录操作意图
"""

import json
import sys
from pathlib import Path
from datetime import datetime

HOOKS_DIR = Path(__file__).parent.parent.parent / "hooks"
RUNTIME_DIR = Path(__file__).parent.parent.parent / "memory" / "runtime"

# 安全操作分类
SAFE_OPERATIONS = [
    "截图",
    "查看",
    "列出",
    "切换应用",
    "打开",
]

CONFIRM_OPERATIONS = [
    "点击",
    "输入",
    "发送",
    "粘贴",
]

DANGER_OPERATIONS = [
    "删除",
    "转账",
    "支付",
    "发送消息",
]


def check_permissions():
    """检查必要权限"""
    import subprocess
    
    results = {
        "accessibility": False,
        "screen_capture": False,
    }
    
    # 检查辅助功能
    try:
        subprocess.run(
            ['osascript', '-e', 'tell application "System Events" to get name of first process'],
            capture_output=True, timeout=5
        )
        results["accessibility"] = True
    except:
        pass
    
    # 检查截屏
    try:
        subprocess.run(
            ['screencapture', '-x', '/tmp/hook-test.png'],
            capture_output=True, timeout=5
        )
        results["screen_capture"] = True
    except:
        pass
    
    return results


def classify_operation(operation: str) -> str:
    """分类操作类型"""
    for op in DANGER_OPERATIONS:
        if op in operation:
            return "danger"
    
    for op in CONFIRM_OPERATIONS:
        if op in operation:
            return "confirm"
    
    for op in SAFE_OPERATIONS:
        if op in operation:
            return "safe"
    
    return "unknown"


def log_operation_intent(operation: str, classification: str):
    """记录操作意图"""
    log_file = RUNTIME_DIR / "gui_operations.jsonl"
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "operation": operation,
        "classification": classification,
        "hook": "pre_gui_hook",
    }
    
    with open(log_file, "a") as f:
        f.write(json.dumps(entry) + "\n")


def main():
    """主入口"""
    if len(sys.argv) < 2:
        print("Usage: pre_gui_hook.py <operation>")
        sys.exit(1)
    
    operation = sys.argv[1]
    
    # 1. 检查权限
    permissions = check_permissions()
    if not permissions["accessibility"]:
        print("⚠️ 警告：辅助功能权限未授权")
        print("请执行：open 'x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility'")
        sys.exit(2)
    
    if not permissions["screen_capture"]:
        print("⚠️ 警告：屏幕录制权限未授权")
        print("请执行：open 'x-apple.systempreferences:com.apple.preference.security?Privacy_ScreenCapture'")
        sys.exit(2)
    
    # 2. 分类操作
    classification = classify_operation(operation)
    
    # 3. 根据分类处理
    if classification == "danger":
        print(f"❌ 拒绝危险操作：{operation}")
        print("此操作需要用户手动执行")
        sys.exit(3)
    
    if classification == "confirm":
        print(f"⚠️ 需确认操作：{operation}")
        print("建议先截屏验证目标位置")
    
    # 4. 记录操作意图
    log_operation_intent(operation, classification)
    
    print(f"✅ 操作已通过前置检查：{operation} (分类: {classification})")
    sys.exit(0)


if __name__ == "__main__":
    main()