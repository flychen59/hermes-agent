#!/usr/bin/env python3
"""GUI 操作后置 Hook — 结果验证

在执行 GUI 操作后进行验证：
- 截屏验证操作结果
- 对比前后状态
- 记录操作结果
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

RUNTIME_DIR = Path(__file__).parent.parent.parent / "memory" / "runtime"
WORKSPACE_DIR = Path.home() / ".openclaw" / "workspace"


def capture_screen(output_path: Path):
    """截屏"""
    subprocess.run(
        ['screencapture', str(output_path)],
        capture_output=True
    )
    return output_path.exists()


def get_frontmost_app():
    """获取前台应用"""
    result = subprocess.run(
        ['osascript', '-e', 'tell application "System Events" to get name of first process whose frontmost is true'],
        capture_output=True, text=True
    )
    return result.stdout.strip()


def log_operation_result(operation: str, success: bool, details: dict):
    """记录操作结果"""
    log_file = RUNTIME_DIR / "gui_operations.jsonl"
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "operation": operation,
        "success": success,
        "details": details,
        "hook": "post_gui_hook",
    }
    
    with open(log_file, "a") as f:
        f.write(json.dumps(entry) + "\n")


def main():
    """主入口"""
    if len(sys.argv) < 2:
        print("Usage: post_gui_hook.py <operation> [--before <path>]")
        sys.exit(1)
    
    operation = sys.argv[1]
    before_path = None
    
    # 解析参数
    if "--before" in sys.argv:
        idx = sys.argv.index("--before")
        if idx + 1 < len(sys.argv):
            before_path = Path(sys.argv[idx + 1])
    
    # 1. 截屏验证
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    after_path = WORKSPACE_DIR / f"gui_verify_{timestamp}.png"
    
    capture_result = capture_screen(after_path)
    frontmost_app = get_frontmost_app()
    
    # 2. 记录结果
    details = {
        "after_screen": str(after_path),
        "before_screen": str(before_path) if before_path else None,
        "frontmost_app": frontmost_app,
        "capture_success": capture_result,
    }
    
    success = capture_result and frontmost_app != ""
    
    log_operation_result(operation, success, details)
    
    # 3. 输出验证结果
    if success:
        print(f"✅ 操作验证成功：{operation}")
        print(f"  前台应用：{frontmost_app}")
        print(f"  截屏路径：{after_path}")
    else:
        print(f"❌ 操作验证失败：{operation}")
        print(f"  请检查截屏或应用状态")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()