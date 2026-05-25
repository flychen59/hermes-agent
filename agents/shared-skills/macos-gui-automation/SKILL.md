---
name: macos-gui-automation
description: "macOS GUI 自动化控制 — 模拟点击、键盘输入、窗口管理、应用控制、截屏。使用 AppleScript/osascript 实现全系统 GUI 操作。"
version: 1.0.0
metadata:
  openclaw:
    emoji: "🖥️"
    os: ["darwin"]
    requires:
      permissions: ["辅助功能 (Accessibility)"]
  gitagent:
    tags: [automation, macos, gui, applescript, desktop-control]
    author: flychen
    created: 2026-05-25
---

# macOS GUI 自动化

通过 AppleScript + exec 工具实现 macOS 全系统 GUI 自动化控制。

## 前置要求

**必须授权辅助功能**：
1. 系统设置 → 隐私与安全性 → 辅助功能
2. 添加 Terminal.app（或运行 Agent 的应用）
3. 解锁后勾选启用

验证授权：
```bash
osascript -e 'tell application "System Events" to get name of first process'
```

## 核心命令

### 1. 窗口管理

```bash
# 列出所有可见应用
osascript -e 'tell application "System Events" to get name of every process whose background only is false'

# 获取前台应用
osascript -e 'tell application "System Events" to get name of first process whose frontmost is true'

# 获取指定应用的窗口列表
osascript -e 'tell application "System Events" to get name of every window of process "Finder"'

# 获取窗口位置和大小
osascript -e 'tell application "System Events" to get position of first window of process "Finder"'
osascript -e 'tell application "System Events" to get size of first window of process "Finder"'
```

### 2. 应用控制

```bash
# 打开应用
osascript -e 'tell application "Finder" to activate'

# 打开应用并打开路径
osascript -e 'tell application "Finder" to open (POSIX file "/Users/flychen/Downloads")'
osascript -e 'tell application "Finder" to activate'

# 退出应用
osascript -e 'tell application "Calculator" to quit'

# 隐藏应用
osascript -e 'tell application "System Events" to set visible of process "Finder" to false'
```

### 3. 鼠标操作

```bash
# 点击坐标 (x, y)
osascript -e 'tell application "System Events" to click at {100, 200}'

# 右键点击
osascript -e 'tell application "System Events" to right click at {100, 200}'

# 双击
osascript -e 'tell application "System Events" to double click at {100, 200}'

# 拖拽 (从 {x1,y1} 到 {x2,y2})
osascript -e 'tell application "System Events" to drag from {100, 100} to {300, 300}'
```

### 4. 键盘操作

```bash
# 输入文本
osascript -e 'tell application "System Events" to keystroke "Hello World"'

# 按键组合 (Cmd+C)
osascript -e 'tell application "System Events" to keystroke "c" using command down'

# Cmd+V
osascript -e 'tell application "System Events" to keystroke "v" using command down'

# Cmd+Tab 切换应用
osascript -e 'tell application "System Events" to keystroke tab using command down'

# 回车键
osascript -e 'tell application "System Events" to key code 36'

# 常用 key code:
# 36 = Return, 48 = Tab, 49 = Space, 51 = Delete, 53 = Escape
# 123 = Left, 124 = Right, 125 = Down, 126 = Up
```

### 5. 菜单操作

```bash
# 点击菜单项
osascript -e 'tell application "System Events" to tell process "Finder"
    click menu item "New Finder Window" of menu "File" of menu bar 1
end tell'

# 点击子菜单
osascript -e 'tell application "System Events" to tell process "Finder"
    click menu item "Compress" of menu "File" of menu bar 1
end tell'
```

### 6. 截屏

```bash
# 全屏截屏
screencapture -x /tmp/screenshot.png

# 指定区域截屏 (x,y,width,height)
screencapture -R 0,0,800,600 /tmp/screenshot.png

# 窗口截屏 (交互选择)
screencapture -w /tmp/window.png

# 截屏到剪贴板
screencapture -c
```

### 7. 文件操作 (Finder)

```bash
# 打开路径
osascript -e 'tell application "Finder" to open (POSIX file "/Users/flychen/Documents")'
osascript -e 'tell application "Finder" to activate'

# 选择文件
osascript -e 'tell application "Finder" to select (POSIX file "/Users/flychen/test.txt")'

# 获取选中文件
osascript -e 'tell application "Finder" to get POSIX path of (selection as alias)'

# 新建文件夹
osascript -e 'tell application "Finder" to make new folder at (POSIX file "/Users/flychen/Desktop") with properties {name:"NewFolder"}'
```

## 使用模式

### 模式 1：直接 exec 调用

```
用户: "帮我打开 Finder 并进入下载文件夹"
→ exec: osascript -e 'tell application "Finder" to open (POSIX file "/Users/flychen/Downloads")'
→ exec: osascript -e 'tell application "Finder" to activate'
```

### 模式 2：多步骤自动化

```
用户: "在 Chrome 中搜索 OpenClaw"
→ exec: osascript -e 'tell application "Google Chrome" to activate'
→ exec: osascript -e 'tell application "System Events" to keystroke "l" using command down'  # Cmd+L 聚焦地址栏
→ exec: osascript -e 'tell application "System Events" to keystroke "https://google.com/search?q=OpenClaw"'
→ exec: osascript -e 'tell application "System Events" to key code 36'  # 回车
```

### 模式 3：状态查询

```
用户: "当前打开了哪些窗口？"
→ exec: osascript -e 'tell application "System Events" to get name of every process whose background only is false'
→ 返回: Terminal, Finder, Chrome, WeChat...
```

## 常见问题

### Q: 提示 "不允许辅助访问"
A: 去系统设置 → 隐私与安全性 → 辅助功能 → 添加 Terminal

### Q: 点击坐标不准
A: 坐标系从左上角 (0,0) 开始，先获取窗口位置再计算相对坐标

### Q: 找不到窗口
A: 先用 `get name of every window of process "xxx"` 确认窗口名称

### Q: 中文输入乱码
A: AppleScript 对中文支持有限，建议用剪贴板中转：
```bash
echo "中文内容" | pbcopy
osascript -e 'tell application "System Events" to keystroke "v" using command down'
```

## 安全提示

- GUI 自动化会真实操作你的电脑，请确认命令后再执行
- 敏感操作（删除、发送等）建议先询问用户
- 可用 `--dry-run` 模式先预览（需要自行实现）

## 进化记录

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-05-25 | 1.0.0 | 初始版本，支持基础 GUI 操作 |

## 相关 Skills

- browser-automation: 浏览器专用自动化
- apple-notes: Apple Notes 操作
- apple-reminders: Apple Reminders 操作