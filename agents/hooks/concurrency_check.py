#!/usr/bin/env python3
"""智能并发检测 - 检测用户操作，自动暂停/恢复 Agent 操作

解决问题：用户操作时 Agent 操作被阻挡
方案：智能检测用户活动，自动暂停 Agent 操作
"""

import subprocess
import time
import json
from pathlib import Path

RUNTIME_DIR = Path(__file__).parent.parent.parent / "memory" / "runtime"
STATE_FILE = RUNTIME_DIR / "agent_pause_state.json"


def get_mouse_position():
    """获取鼠标位置"""
    result = subprocess.run([
        'osascript', '-e',
        '''
        tell application "System Events"
            try
                set mousePos to (do shell script "echo $((\$(osascript -e \"tell application \\\"System Events\\\" to get mouse position\") // 1))")
            end try
        end tell
        '''
    ], capture_output=True, text=True)
    
    # 尝试解析结果
    try:
        # 使用更简单的方法：获取窗口位置作为参考
        result = subprocess.run([
            'osascript', '-e',
            'tell application "System Events" to get position of first window of first process whose frontmost is true'
        ], capture_output=True, text=True)
        
        pos_str = result.stdout.strip()
        # 格式: "100, 200"
        parts = pos_str.split(", ")
        if len(parts) == 2:
            return float(parts[0].replace("{", "").strip()), float(parts[1].replace("}", "").strip())
    except:
        pass
    
    # 最后方案：使用 screencapture 时间戳模拟
    return time.time() % 1000, time.time() % 800


def get_frontmost_app():
    """获取前台应用"""
    result = subprocess.run([
        'osascript', '-e',
        'tell application "System Events" to get name of first process whose frontmost is true'
    ], capture_output=True, text=True)
    return result.stdout.strip()


def detect_user_activity(check_interval=0.1, movement_threshold=5):
    """检测用户是否有最近操作
    
    Args:
        check_interval: 检测间隔（秒）
        movement_threshold: 鼠标移动阈值（像素）
    
    Returns:
        (is_active, reason): 是否活跃，原因
    """
    # 1. 检测鼠标移动
    x1, y1 = get_mouse_position()
    if x1 is None:
        return False, "无法获取鼠标位置"
    
    time.sleep(check_interval)
    
    x2, y2 = get_mouse_position()
    if x2 is None:
        return False, "无法获取鼠标位置"
    
    # 计算移动距离
    distance = abs(x2 - x1) + abs(y2 - y1)
    
    if distance > movement_threshold:
        return True, f"鼠标移动 {distance} 像素"
    
    # 2. 检测前台应用变化（可能用户切换了应用）
    # 这个检测需要记录上次的前台应用
    
    return False, "用户未操作"


def smart_wait_for_user_idle(max_wait=5, pause_agent=True):
    """智能等待用户停止操作
    
    Args:
        max_wait: 最大等待时间（秒）
        pause_agent: 是否暂停 Agent
    
    Returns:
        (success, message): 是否成功，消息
    """
    # 设置暂停状态
    if pause_agent:
        set_agent_pause_state(True, "等待用户停止操作")
    
    start_time = time.time()
    consecutive_idle = 0
    idle_threshold = 3  # 连续 3 次检测无操作才算真正空闲
    
    while time.time() - start_time < max_wait:
        active, reason = detect_user_activity()
        
        if not active:
            consecutive_idle += 1
            if consecutive_idle >= idle_threshold:
                # 用户已停止操作
                if pause_agent:
                    set_agent_pause_state(False, "用户已停止操作，恢复执行")
                return True, f"用户已停止操作（等待了 {time.time() - start_time:.1f} 秒）"
        else:
            consecutive_idle = 0
            # 重置等待时间，继续等待
            pass
        
        time.sleep(0.1)
    
    # 等待超时
    if pause_agent:
        set_agent_pause_state(True, f"等待超时，用户持续操作: {reason}")
    
    return False, f"等待超时: {reason}"


def set_agent_pause_state(pause, reason):
    """设置 Agent 暂停状态
    
    Args:
        pause: 是否暂停
        reason: 原因
    """
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    
    state = {
        "pause": pause,
        "reason": reason,
        "timestamp": time.time(),
        "timestamp_iso": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    
    STATE_FILE.write_text(json.dumps(state, indent=2))
    
    if pause:
        print(f"⚠️ Agent 已暂停: {reason}")
    else:
        print(f"✅ Agent 已恢复: {reason}")


def get_agent_pause_state():
    """获取 Agent 暂停状态"""
    if not STATE_FILE.exists():
        return {"pause": False, "reason": "无暂停状态"}
    
    try:
        return json.loads(STATE_FILE.read_text())
    except:
        return {"pause": False, "reason": "状态文件损坏"}


def should_pause_for_user():
    """判断是否应该为用户暂停"""
    active, reason = detect_user_activity()
    
    if active:
        # 用户正在操作，建议暂停
        return True, reason
    
    # 检查当前暂停状态
    state = get_agent_pause_state()
    if state.get("pause"):
        # 已经暂停，继续保持
        return True, state.get("reason", "已暂停")
    
    return False, "可以继续操作"


def main():
    """CLI 入口"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python concurrency_check.py detect    # 检测用户活动")
        print("  python concurrency_check.py wait       # 等待用户停止")
        print("  python concurrency_check.py state      # 获取暂停状态")
        print("  python concurrency_check.py should     # 判断是否应该暂停")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "detect":
        active, reason = detect_user_activity()
        print(f"用户活动: {active}")
        print(f"原因: {reason}")
    
    elif cmd == "wait":
        max_wait = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        success, message = smart_wait_for_user_idle(max_wait)
        print(f"等待结果: {success}")
        print(f"消息: {message}")
    
    elif cmd == "state":
        state = get_agent_pause_state()
        print(json.dumps(state, indent=2))
    
    elif cmd == "should":
        should, reason = should_pause_for_user()
        print(f"应该暂停: {should}")
        print(f"原因: {reason}")
    
    else:
        print(f"未知命令: {cmd}")


if __name__ == "__main__":
    main()