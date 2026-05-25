#!/usr/bin/env python3
"""错误恢复机制 - 自动重试 + 反思调整 + 错误分析

解决问题：点击位置不准，应用意外关闭
方案：自动重试 + 失败分析 + 策略调整
"""

import subprocess
import time
import json
from pathlib import Path
from datetime import datetime

# 导入并发检测
try:
    from concurrency_check import smart_wait_for_user_idle
except ImportError:
    smart_wait_for_user_idle = lambda x: (True, "跳过并发检测")

HOOKS_DIR = Path(__file__).parent
MEMORY_DIR = HOOKS_DIR.parent / "memory" / "runtime"
LOG_FILE = MEMORY_DIR / "gui_operations.log"


def capture_screen(output_path=None):
    """截屏"""
    if output_path is None:
        output_path = MEMORY_DIR / f"screen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    
    result = subprocess.run([
        'screencapture', '-x', str(output_path)
    ], capture_output=True, text=True)
    
    return output_path if result.returncode == 0 else None


def execute_applescript(script):
    """执行 AppleScript"""
    result = subprocess.run([
        'osascript', '-e', script
    ], capture_output=True, text=True, timeout=30)
    
    return {
        "success": result.returncode == 0,
        "output": result.stdout.strip(),
        "error": result.stderr.strip(),
        "returncode": result.returncode
    }


def activate_app(app_name):
    """激活应用"""
    script = f'tell application "{app_name}" to activate'
    return execute_applescript(script)


def click_at_position(x, y, process_name=None):
    """点击指定位置"""
    if process_name:
        script = f'''
tell application "System Events"
    tell process "{process_name}"
        click at {{x, y}}
    end tell
end tell
'''
    else:
        script = f'''
tell application "System Events"
    click at {{x, y}}
end tell
'''
    
    script = script.replace("{x}", str(x)).replace("{y}", str(y))
    return execute_applescript(script)


def get_window_info(app_name):
    """获取窗口信息"""
    script = f'''
tell application "System Events"
    tell process "{app_name}"
        try
            set windowPos to position of first window
            set windowSize to size of first window
            return "Position: " & (item 1 of windowPos) & ", " & (item 2 of windowPos) & " Size: " & (item 1 of windowSize) & "x" & (item 2 of windowSize)
        on error
            return "No window found"
        end try
    end tell
end tell
'''
    
    result = execute_applescript(script)
    
    if result["success"]:
        try:
            # 解析 "Position: 100, 200 Size: 500x600"
            parts = result["output"].split(" ")
            pos_str = parts[1] + ", " + parts[2]
            size_str = parts[4]
            
            x, y = pos_str.split(", ")
            w, h = size_str.split("x")
            
            return {
                "x": int(x),
                "y": int(y),
                "width": int(w),
                "height": int(h)
            }
        except:
            pass
    
    return None


def analyze_failure(before_screen, after_screen, operation):
    """分析失败原因"""
    # 简单分析：对比前后屏幕
    
    # 1. 检查是否应用被关闭
    result = subprocess.run([
        'osascript', '-e',
        'tell application "System Events" to get name of every process whose frontmost is true'
    ], capture_output=True, text=True)
    
    frontmost_apps = result.stdout.strip()
    
    # 2. 检查是否有弹窗
    # 使用视觉模型分析（这里用简单逻辑判断）
    
    failure_reasons = [
        "应用可能被意外关闭",
        "点击位置不准确",
        "操作触发其他窗口",
        "用户操作干扰",
    ]
    
    # 随机选择一个原因（实际应该用视觉模型分析）
    import random
    return random.choice(failure_reasons)


def adjust_strategy(operation, failure_reason):
    """调整操作策略"""
    
    # 根据失败原因调整策略
    if "应用可能被意外关闭" in failure_reason:
        # 重新激活应用
        return {
            "action": "reactivate",
            "app": operation.get("app", "Runner"),
            "original_operation": operation
        }
    
    elif "点击位置不准确" in failure_reason:
        # 调整点击位置
        original_x = operation.get("x", 0)
        original_y = operation.get("y", 0)
        
        # 添加偏移
        return {
            "action": "click_adjusted",
            "x": original_x + 10,
            "y": original_y + 10,
            "app": operation.get("app")
        }
    
    elif "操作触发其他窗口" in failure_reason:
        # 关闭弹窗，重新尝试
        return {
            "action": "close_popup_retry",
            "original_operation": operation
        }
    
    elif "用户操作干扰" in failure_reason:
        # 等待用户停止操作
        return {
            "action": "wait_user_idle",
            "original_operation": operation
        }
    
    return operation


def execute_with_retry(operation, max_retries=3):
    """带重试的操作执行
    
    Args:
        operation: 操作定义
            {
                "type": "click" | "activate" | "type" | "key",
                "app": "应用名称",
                "x": 点击位置 x,
                "y": 点击位置 y,
                "keys": 按键序列,
                "text": 输入文本
            }
        max_retries: 最大重试次数
    
    Returns:
        (success, message, attempts)
    """
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    
    attempts = []
    
    for attempt_num in range(1, max_retries + 1):
        attempt = {
            "num": attempt_num,
            "operation": operation,
            "timestamp": datetime.now().isoformat(),
            "result": None,
            "failure_reason": None
        }
        
        try:
            # 1. 等待用户停止操作
            idle_success, idle_msg = smart_wait_for_user_idle(2)
            if not idle_success:
                attempt["result"] = {"success": False, "error": idle_msg}
                attempts.append(attempt)
                continue
            
            # 2. 执行前截屏
            before_screen = capture_screen()
            
            # 3. 执行操作
            if operation["type"] == "activate":
                result = activate_app(operation["app"])
            
            elif operation["type"] == "click":
                result = click_at_position(
                    operation["x"],
                    operation["y"],
                    operation.get("app")
                )
            
            elif operation["type"] == "key":
                keys = operation.get("keys", [])
                script = 'tell application "System Events" to '
                for key in keys:
                    if key.startswith("cmd+"):
                        script += f'keystroke "{key[4:]}" using command down'
                    elif key == "escape":
                        script += 'key code 53'
                    else:
                        script += f'keystroke "{key}"'
                result = execute_applescript(script)
            
            else:
                result = {"success": False, "error": f"未知操作类型: {operation['type']}"}
            
            # 4. 执行后截屏
            time.sleep(0.5)
            after_screen = capture_screen()
            
            # 5. 验证操作是否成功
            # 简单验证：检查是否有错误
            if result["success"]:
                # 操作执行成功，记录
                attempt["result"] = result
                attempts.append(attempt)
                
                # 记录日志
                log_operation(operation, attempt_num, "success")
                
                return True, f"操作成功 (尝试 {attempt_num})", attempts
            else:
                # 操作失败，分析原因
                failure_reason = analyze_failure(before_screen, after_screen, operation)
                attempt["result"] = result
                attempt["failure_reason"] = failure_reason
                attempts.append(attempt)
                
                # 调整策略，准备下次尝试
                operation = adjust_strategy(operation, failure_reason)
                
        except Exception as e:
            attempt["result"] = {"success": False, "error": str(e)}
            attempts.append(attempt)
            
            if attempt_num == max_retries:
                return False, f"操作失败: {e}", attempts
        
        # 等待一下再重试
        time.sleep(0.5)
    
    # 重试耗尽
    log_operation(operation, max_retries, "failed")
    return False, "重试耗尽，操作失败", attempts


def log_operation(operation, attempt_num, status):
    """记录操作日志"""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "operation": operation,
        "attempt": attempt_num,
        "status": status
    }
    
    # 写入日志文件
    if LOG_FILE.exists():
        logs = json.loads(LOG_FILE.read_text())
    else:
        logs = []
    
    logs.append(log_entry)
    LOG_FILE.write_text(json.dumps(logs, indent=2))


def main():
    """CLI 入口"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python error_recovery.py activate <app>")
        print("  python error_recovery.py click <app> <x> <y>")
        print("  python error_recovery.py test")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "activate":
        app = sys.argv[2] if len(sys.argv) > 2 else "Runner"
        operation = {"type": "activate", "app": app}
        success, msg, attempts = execute_with_retry(operation)
        print(f"结果: {success}")
        print(f"消息: {msg}")
        print(f"尝试次数: {len(attempts)}")
    
    elif cmd == "click":
        app = sys.argv[2] if len(sys.argv) > 2 else "Runner"
        x = int(sys.argv[3]) if len(sys.argv) > 3 else 100
        y = int(sys.argv[4]) if len(sys.argv) > 4 else 100
        operation = {"type": "click", "app": app, "x": x, "y": y}
        success, msg, attempts = execute_with_retry(operation)
        print(f"结果: {success}")
        print(f"消息: {msg}")
        print(f"尝试次数: {len(attempts)}")
    
    elif cmd == "test":
        # 测试：激活 WeChat
        print("测试 1: 激活 WeChat")
        operation = {"type": "activate", "app": "WeChat"}
        success, msg, attempts = execute_with_retry(operation, max_retries=2)
        print(f"  结果: {success}, {msg}")
        
        time.sleep(1)
        
        # 测试：获取窗口信息
        print("测试 2: 获取 WeChat 窗口信息")
        window_info = get_window_info("WeChat")
        if window_info:
            print(f"  窗口位置: ({window_info['x']}, {window_info['y']})")
            print(f"  窗口大小: {window_info['width']}x{window_info['height']}")
        
        # 截屏验证
        print("测试 3: 截屏验证")
        screen = capture_screen()
        if screen:
            print(f"  截屏保存: {screen}")
    
    else:
        print(f"未知命令: {cmd}")


if __name__ == "__main__":
    main()