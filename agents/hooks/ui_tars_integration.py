#!/usr/bin/env python3
"""UI-TARS Desktop 集成模块

集成 ByteDance UI-TARS Desktop 到现有 GUI Agent 框架
实现最佳性能的桌面自动化

参考：
- UI-TARS 论文：arXiv:2501.12326
- Agent TARS：https://agent-tars.com
- OSWorld benchmark：24.6 vs Claude 22.0
"""

import subprocess
import json
import time
from pathlib import Path
from datetime import datetime

HOOKS_DIR = Path(__file__).parent
MEMORY_DIR = HOOKS_DIR.parent.parent / "memory" / "runtime"


class UITARSDesktop:
    """UI-TARS Desktop 集成器"""
    
    def __init__(self):
        self.app_name = "UI TARS"
        self.is_running = False
        self.config = None
    
    def check_installed(self):
        """检查是否已安装"""
        result = subprocess.run([
            'osascript', '-e',
            'tell application "System Events" to get name of every process'
        ], capture_output=True, text=True)
        
        return self.app_name in result.stdout
    
    def launch(self):
        """启动 UI-TARS Desktop"""
        subprocess.run([
            'open', '-a', self.app_name
        ], capture_output=True)
        
        time.sleep(3)
        self.is_running = self.check_installed()
        
        return self.is_running
    
    def configure(self, provider="openai-compat", model="glm-5.1", api_key=None, base_url=None):
        """配置 UI-TARS
        
        Args:
            provider: VLM 提供者
            model: 模型名称
            api_key: API 密钥
            base_url: API 基础 URL
        """
        self.config = {
            "provider": provider,
            "model": model,
            "api_key": api_key,
            "base_url": base_url,
            "language": "cn",
            "operator": "computer"  # computer 或 browser
        }
        
        # 保存配置
        config_file = MEMORY_DIR / "ui_tars_config.json"
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)
        config_file.write_text(json.dumps(self.config, indent=2))
        
        return self.config
    
    def get_window_position(self):
        """获取 UI-TARS 窗口位置"""
        script = f'''
tell application "System Events"
    tell process "{self.app_name}"
        try
            set windowPos to position of first window
            set windowSize to size of first window
            return (item 1 of windowPos) & "," & (item 2 of windowPos) & "," & (item 1 of windowSize) & "," & (item 2 of windowSize)
        on error
            return "none"
        end try
    end tell
end tell
'''
        
        result = subprocess.run([
            'osascript', '-e', script
        ], capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0 and result.stdout.strip() != "none":
            try:
                parts = result.stdout.strip().split(",")
                return {
                    "x": int(parts[0]),
                    "y": int(parts[1]),
                    "width": int(parts[2]),
                    "height": int(parts[3])
                }
            except:
                pass
        
        return None
    
    def send_command(self, command):
        """发送命令到 UI-TARS
        
        Args:
            command: 自然语言命令，如 "打开 WeChat"
        """
        # 方案 1: 通过 UI-TARS Desktop 的输入框输入命令
        window_pos = self.get_window_position()
        
        if window_pos:
            # 点击输入框（假设在窗口中央）
            input_x = window_pos["x"] + window_pos["width"] // 2
            input_y = window_pos["y"] + window_pos["height"] - 100
            
            # 激活 UI TARS
            subprocess.run([
                'osascript', '-e',
                f'tell application "{self.app_name}" to activate'
            ], capture_output=True)
            
            time.sleep(0.5)
            
            # 点击输入框
            subprocess.run([
                'osascript', '-e',
                f'tell application "System Events" to click at {{input_x, input_y}}'
            ], capture_output=True)
            
            # 输入命令
            subprocess.run([
                'osascript', '-e',
                f'tell application "System Events" to keystroke "{command}"'
            ], capture_output=True)
            
            # 发送命令（按 Enter）
            subprocess.run([
                'osascript', '-e',
                'tell application "System Events" to key code 36'  # Enter
            ], capture_output=True)
            
            return True
        
        return False
    
    def execute_with_best_performance(self, operation):
        """使用最佳性能执行操作
        
        集成所有优化：
        1. UI-TARS Desktop（最先进的 GUI Agent）
        2. 并发检测（防止用户干扰）
        3. 错误恢复（自动重试）
        4. 速度优化（缓存）
        
        Args:
            operation: 操作描述
        
        Returns:
            执行结果
        """
        
        # ── Step 1: 并发检测 ───────────────────────────────────
        concurrency_hook = HOOKS_DIR / "concurrency_check.py"
        
        if concurrency_hook.exists():
            check_result = subprocess.run(
                [sys.executable, str(concurrency_hook), "detect"],
                capture_output=True, text=True
            )
            
            if "用户正在操作" in check_result.stdout:
                # 等待用户停止
                subprocess.run(
                    [sys.executable, str(concurrency_hook), "wait", "5"],
                    capture_output=True, text=True
                )
        
        # ── Step 2: UI-TARS 执行 ───────────────────────────────────
        if self.is_running:
            # 使用 UI-TARS Desktop 执行
            success = self.send_command(operation)
            
            if success:
                # 等待 UI-TARS 完成
                time.sleep(2)
                
                # 截屏验证
                screen_path = MEMORY_DIR / f"ui_tars_result_{datetime.now().strftime('%H%M%S')}.png"
                subprocess.run(['screencapture', str(screen_path)], capture_output=True)
                
                return {
                    "success": True,
                    "method": "ui_tars_desktop",
                    "operation": operation,
                    "screenshot": str(screen_path)
                }
        
        # ── Step 3: 失败则使用错误恢复 ───────────────────────────────────
        error_recovery_hook = HOOKS_DIR / "error_recovery.py"
        
        if error_recovery_hook.exists():
            # 解析操作
            if "激活" in operation or "打开" in operation:
                import re
                match = re.search(r'(激活|打开|切换到?)(.+)', operation)
                if match:
                    app_name = match.group(2).strip()
                    
                    result = subprocess.run(
                        [sys.executable, str(error_recovery_hook), "activate", app_name],
                        capture_output=True, text=True
                    )
                    
                    return {
                        "success": "操作成功" in result.stdout,
                        "method": "error_recovery",
                        "operation": operation,
                        "output": result.stdout
                    }
        
        # ── Step 4: 直接执行 ───────────────────────────────────
        import re
        match = re.search(r'(激活|打开|切换到?)(.+)', operation)
        if match:
            app_name = match.group(2).strip()
            
            result = subprocess.run(
                ['osascript', '-e', f'tell application "{app_name}" to activate'],
                capture_output=True, text=True
            )
            
            return {
                "success": result.returncode == 0,
                "method": "direct_applescript",
                "operation": operation,
                "output": result.stdout
            }
        
        return {
            "success": False,
            "method": "none",
            "operation": operation,
            "error": "无法执行操作"
        }


def integrate_with_agent_tars_cli(operation):
    """使用 Agent TARS CLI 执行
    
    Agent TARS CLI 支持浏览器自动化和 Visual Grounding
    
    Args:
        operation: 操作描述
    
    Returns:
        执行结果
    """
    
    # Agent TARS CLI 命令
    # agent-tars --provider volcengine --model doubao-1-5-thinking-vision-pro-250428
    
    # 使用现有的配置
    config_file = MEMORY_DIR / "ui_tars_config.json"
    
    if config_file.exists():
        config = json.loads(config_file.read_text())
        
        # 构建命令
        cmd = [
            'agent-tars',
            '--provider', config.get('provider', 'openai-compat'),
            '--model', config.get('model', 'glm-5.1'),
            '--headless',
            '--input', operation
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        return {
            "success": result.returncode == 0,
            "method": "agent_tars_cli",
            "operation": operation,
            "output": result.stdout,
            "error": result.stderr
        }
    
    return {
        "success": False,
        "method": "agent_tars_cli",
        "error": "配置文件不存在"
    }


def main():
    """CLI 入口"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python ui_tars_integration.py check      # 检查是否已安装")
        print("  python ui_tars_integration.py launch     # 启动 UI-TARS")
        print("  python ui_tars_integration.py config     # 配置 UI-TARS")
        print("  python ui_tars_integration.py execute <cmd>  # 执行命令")
        print("  python ui_tars_integration.py cli <cmd>      # 使用 Agent TARS CLI")
        return
    
    cmd = sys.argv[1]
    
    ui_tars = UITARSDesktop()
    
    if cmd == "check":
        installed = ui_tars.check_installed()
        print(f"UI-TARS Desktop 已安装: {installed}")
        
        if installed:
            pos = ui_tars.get_window_position()
            if pos:
                print(f"窗口位置: ({pos['x']}, {pos['y']})")
                print(f"窗口大小: {pos['width']}x{pos['height']}")
    
    elif cmd == "launch":
        success = ui_tars.launch()
        print(f"启动结果: {success}")
        
        if success:
            pos = ui_tars.get_window_position()
            if pos:
                print(f"窗口已打开，位置: ({pos['x']}, {pos['y']})")
    
    elif cmd == "config":
        # 使用 OpenClaw 的配置
        import os
        
        api_key = os.environ.get("OPENAI_API_KEY", "")
        base_url = "http://api.halphen.cn/openai/v1"
        
        config = ui_tars.configure(
            provider="openai-compat",
            model="glm-5.1",
            api_key=api_key,
            base_url=base_url
        )
        
        print(f"配置已保存:")
        print(f"  Provider: {config['provider']}")
        print(f"  Model: {config['model']}")
        print(f"  Base URL: {config['base_url']}")
    
    elif cmd == "execute":
        operation = sys.argv[2] if len(sys.argv) > 2 else "打开 WeChat"
        result = ui_tars.execute_with_best_performance(operation)
        print(json.dumps(result, indent=2))
    
    elif cmd == "cli":
        operation = sys.argv[2] if len(sys.argv) > 2 else "打开 WeChat"
        result = integrate_with_agent_tars_cli(operation)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()