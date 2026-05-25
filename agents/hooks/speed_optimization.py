#!/usr/bin/env python3
"""速度优化 - 异步视觉理解 + 截屏缓存 + 窗口位置缓存

优化目标：
- 截屏：500ms → 200ms
- 视觉理解：2000ms → 1000ms（异步预分析）
- AppleScript：1000ms → 200ms（批量执行）
- 总计：3500ms → 1400ms
"""

import subprocess
import time
import json
import threading
import queue
from pathlib import Path
from datetime import datetime
from functools import lru_cache

MEMORY_DIR = Path(__file__).parent.parent / "memory" / "runtime"
CACHE_DIR = MEMORY_DIR / "cache"


class ScreenCache:
    """截屏缓存"""
    
    def __init__(self, max_age_seconds=2):
        self.cache = {}
        self.max_age = max_age_seconds
    
    def get(self, key):
        """获取缓存的截屏"""
        if key in self.cache:
            entry = self.cache[key]
            age = time.time() - entry["timestamp"]
            if age < self.max_age:
                return entry["path"]
            else:
                # 过期，删除
                del self.cache[key]
        return None
    
    def set(self, key, path):
        """设置缓存"""
        self.cache[key] = {
            "path": path,
            "timestamp": time.time()
        }


class WindowPositionCache:
    """窗口位置缓存"""
    
    def __init__(self, max_age_seconds=5):
        self.cache = {}
        self.max_age = max_age_seconds
    
    def get(self, app_name):
        """获取缓存的窗口位置"""
        if app_name in self.cache:
            entry = self.cache[app_name]
            age = time.time() - entry["timestamp"]
            if age < self.max_age:
                return entry["position"]
            else:
                del self.cache[app_name]
        return None
    
    def set(self, app_name, position):
        """设置缓存"""
        self.cache[app_name] = {
            "position": position,
            "timestamp": time.time()
        }
    
    def invalidate(self, app_name):
        """失效缓存"""
        if app_name in self.cache:
            del self.cache[app_name]


class AsyncVisualAnalyzer:
    """异步视觉分析器"""
    
    def __init__(self):
        self.analysis_queue = queue.Queue()
        self.analysis_thread = None
        self.analysis_results = {}
        self.running = False
    
    def start(self):
        """启动异步分析线程"""
        if self.running:
            return
        
        self.running = True
        self.analysis_thread = threading.Thread(target=self._analyze_worker)
        self.analysis_thread.daemon = True
        self.analysis_thread.start()
    
    def stop(self):
        """停止异步分析"""
        self.running = False
        if self.analysis_thread:
            self.analysis_thread.join(timeout=1)
    
    def submit_analysis(self, screen_path, analysis_id, prompt):
        """提交异步分析任务"""
        self.analysis_queue.put({
            "id": analysis_id,
            "path": screen_path,
            "prompt": prompt
        })
    
    def get_analysis_result(self, analysis_id, timeout=5):
        """获取分析结果"""
        if analysis_id in self.analysis_results:
            return self.analysis_results.pop(analysis_id)
        
        # 等待结果
        for _ in range(int(timeout * 10)):
            if analysis_id in self.analysis_results:
                return self.analysis_results.pop(analysis_id)
            time.sleep(0.1)
        
        return None
    
    def _analyze_worker(self):
        """异步分析工作线程"""
        while self.running:
            try:
                task = self.analysis_queue.get(timeout=1)
                
                # 这里应该调用视觉模型分析
                # 目前使用模拟结果
                result = {
                    "id": task["id"],
                    "analysis": f"分析结果（模拟）",
                    "timestamp": time.time()
                }
                
                self.analysis_results[task["id"]] = result
                
            except queue.Empty:
                continue


class BatchAppleScriptExecutor:
    """批量 AppleScript 执行器"""
    
    def __init__(self):
        self.script_queue = []
    
    def add(self, script):
        """添加脚本到队列"""
        self.script_queue.append(script)
    
    def execute_batch(self):
        """批量执行所有脚本"""
        if not self.script_queue:
            return []
        
        # 合合所有脚本为一个
        combined_script = "\n".join(self.script_queue)
        
        result = subprocess.run([
            'osascript', '-e', combined_script
        ], capture_output=True, text=True, timeout=30)
        
        # 清空队列
        self.script_queue.clear()
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout.strip(),
            "error": result.stderr.strip()
        }


# 全局缓存实例
screen_cache = ScreenCache()
window_cache = WindowPositionCache()
async_analyzer = AsyncVisualAnalyzer()
batch_executor = BatchAppleScriptExecutor()


def fast_capture_screen(app_name=None, use_cache=True):
    """快速截屏（带缓存）"""
    cache_key = app_name or "global"
    
    if use_cache:
        cached_path = screen_cache.get(cache_key)
        if cached_path:
            return cached_path
    
    # 截屏
    output_path = MEMORY_DIR / f"fast_screen_{datetime.now().strftime('%H%M%S')}.png"
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    
    result = subprocess.run([
        'screencapture', '-x', str(output_path)
    ], capture_output=True)
    
    if result.returncode == 0:
        screen_cache.set(cache_key, output_path)
        return output_path
    
    return None


def fast_get_window_position(app_name, use_cache=True):
    """快速获取窗口位置（带缓存）"""
    if use_cache:
        cached_pos = window_cache.get(app_name)
        if cached_pos:
            return cached_pos
    
    script = f'''
tell application "System Events"
    tell process "{app_name}"
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
            position = {
                "x": int(parts[0]),
                "y": int(parts[1]),
                "width": int(parts[2]),
                "height": int(parts[3])
            }
            window_cache.set(app_name, position)
            return position
        except:
            pass
    
    return None


def fast_click_relative(app_name, rel_x, rel_y):
    """快速相对点击（使用缓存窗口位置）"""
    window_pos = fast_get_window_position(app_name)
    
    if window_pos:
        abs_x = window_pos["x"] + rel_x
        abs_y = window_pos["y"] + rel_y
        
        script = f'''
tell application "{app_name}" to activate
tell application "System Events"
    click at {{abs_x, abs_y}}
end tell
'''
        
        script = script.replace("{abs_x}", str(abs_x)).replace("{abs_y}", str(abs_y))
        
        # 失效窗口缓存（点击可能改变窗口位置）
        window_cache.invalidate(app_name)
        
        return subprocess.run([
            'osascript', '-e', script
        ], capture_output=True, text=True, timeout=5)
    
    return None


def preload_next_screen_analysis(prompt):
    """预加载下一屏幕分析"""
    screen_path = fast_capture_screen(use_cache=False)
    
    if screen_path:
        analysis_id = datetime.now().strftime("%H%M%S")
        async_analyzer.submit_analysis(screen_path, analysis_id, prompt)
        return analysis_id
    
    return None


def measure_performance(func, *args):
    """测量性能"""
    start = time.time()
    result = func(*args)
    elapsed = time.time() - start
    return result, elapsed


def main():
    """CLI 测试"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python speed_optimization.py test")
        print("  python speed_optimization.py benchmark")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "test":
        print("测试速度优化:")
        
        # 测试截屏缓存
        print("\n1. 截屏缓存测试")
        screen1, t1 = measure_performance(fast_capture_screen)
        print(f"  第一次截屏: {t1:.3f}s, 保存到 {screen1}")
        
        screen2, t2 = measure_performance(fast_capture_screen)
        print(f"  第二次截屏（缓存）: {t2:.3f}s, 返回 {screen2}")
        
        print(f"  ⚡ 缓存提速: {t1/t2:.1f}x")
        
        # 测试窗口位置缓存
        print("\n2. 窗口位置缓存测试")
        pos1, t3 = measure_performance(fast_get_window_position, "WeChat")
        print(f"  第一次获取: {t3:.3f}s, 结果 {pos1}")
        
        pos2, t4 = measure_performance(fast_get_window_position, "WeChat")
        print(f"  第二次获取（缓存）: {t4:.3f}s, 结果 {pos2}")
        
        print(f"  ⚡ 缓存提速: {t3/t4:.1f}x")
        
        # 测试批量执行
        print("\n3. 批量执行测试")
        batch_executor.add('tell application "WeChat" to activate')
        batch_executor.add('delay 0.1')
        
        _, t5 = measure_performance(batch_executor.execute_batch)
        print(f"  批量执行: {t5:.3f}s")
    
    elif cmd == "benchmark":
        print("性能基准测试:")
        
        results = []
        
        # 截屏性能
        for i in range(10):
            _, t = measure_performance(fast_capture_screen, use_cache=False)
            results.append(("截屏", t))
        
        # 窗口位置性能
        for i in range(10):
            _, t = measure_performance(fast_get_window_position, "WeChat", use_cache=False)
            results.append(("窗口位置", t))
        
        # 统计
        import statistics
        
        for op in ["截屏", "窗口位置"]:
            times = [t for o, t in results if o == op]
            avg = statistics.mean(times)
            std = statistics.stdev(times) if len(times) > 1 else 0
            
            print(f"{op}: 平均 {avg:.3f}s ± {std:.3f}s")


if __name__ == "__main__":
    main()