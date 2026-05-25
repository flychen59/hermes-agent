---
name: macos-gui-automation
description: "macOS GUI 自动化控制 — 模拟点击、键盘输入、窗口管理、应用控制、截屏视觉理解闭环。使用 AppleScript/osascript 实现全系统 GUI 操作。"
version: 2.2.0
metadata:
  hermes:
    tags: [automation, macos, gui, applescript, desktop-control, accessibility]
    author: flychen
    created: "2026-05-25"
    related_skills: [browser-automation, apple-notes, apple-reminders]
    priority: high
    mobile_trigger: true
    examples:
      - "查看微信第一个对话是谁"
      - "在 Chrome 中搜索 xxx"
      - "打开 Finder 进入下载文件夹"
      - "截图当前桌面"
      - "切换到 VS Code"
  openclaw:
    emoji: "🖥️"
    os: ["darwin"]
    requires:
      permissions: ["辅助功能 (Accessibility)", "屏幕录制"]
  evolution:
    use_count: 10
    last_used: "2026-05-26T00:45:00+08:00"
    success_rate: 0.90
    auto_evolve: true
    patches:
      - date: "2026-05-26"
        change: "添加并发检测 + 错误恢复机制"
      - date: "2026-05-26"
        change: "添加闭环验证流程，修复截屏路径问题"
---

# macOS GUI 自动化

> 🖥️ **桌面 Agent 核心能力** — 通过视觉理解 + 操作执行 + 结果验证实现完整 GUI 控制闭环

## 权限设置

### 必须授权

| 权限 | 路径 | 应用 |
|------|------|------|
| **辅助功能** | 系统设置 → 隐私与安全性 → 辅助功能 | Terminal.app |
| **屏幕录制** | 系统设置 → 隐私与安全性 → 屏幕录制 | Terminal.app |
| **自动化** | 系统设置 → 隐私与安全性 → 自动化 | Terminal → 允许控制其他应用 |

### 快速授权命令

```bash
# 打开三个权限设置页面
open "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"
open "x-apple.systempreferences:com.apple.preference.security?Privacy_ScreenCapture"
open "x-apple.systempreferences:com.apple.preference.security?Privacy_Automation"
```

---

## 核心能力矩阵

| 能力 | 命令 | 状态 | 验证方式 |
|------|------|------|----------|
| **截屏** | `screencapture` | ✅ | 检查文件存在 |
| **视觉理解** | `image` 工具 | ✅ | AI 分析内容 |
| **点击** | `click at {x,y}` | ✅ | 截屏对比 |
| **键盘输入** | `keystroke` | ✅ | 截屏验证 |
| **窗口查询** | `get name of every process` | ✅ | 输出确认 |
| **应用切换** | `activate` | ✅ | 前台应用确认 |

---

## 操作闭环流程

```
┌────────────────────────────────────────────────────────────┐
│                    GUI Agent 闭环                           │
│                                                            │
│  1. OBSERVE  ──→  截屏当前状态                              │
│  2. ANALYZE  ──→  AI 视觉理解，定位目标                     │
│  3. PLAN     ──→  决策操作（点击/输入/切换）                 │
│  4. ACT      ──→  执行 AppleScript 命令                     │
│  5. VERIFY   ──→  截屏 + 视觉验证结果                        │
│  6. REPORT   ──→  向用户报告操作结果                         │
└────────────────────────────────────────────────────────────┘
```

---

## 命令手册

### 1. 截屏 + 视觉理解

```bash
# 截屏到 workspace
screencapture ~/.openclaw/workspace/screen.png

# 视觉理解（调用 image 工具）
# prompt: "描述这个截图，包括前台应用、窗口位置、可点击元素"
```

### 2. 窗口管理

```bash
# 列出所有可见应用
osascript -e 'tell application "System Events" to get name of every process whose background only is false'

# 获取前台应用
osascript -e 'tell application "System Events" to get name of first process whose frontmost is true'

# 切换应用
osascript -e 'tell application "WeChat" to activate'
osascript -e 'tell application "Google Chrome" to activate'
osascript -e 'tell application "Finder" to activate'
osascript -e 'tell application "Code" to activate'  # VS Code
```

### 3. 鼠标操作

```bash
# 点击坐标 (x, y) - 从左上角 (0,0) 开始
osascript -e 'tell application "System Events" to click at {100, 200}'

# 右键点击
osascript -e 'tell application "System Events" to right click at {100, 200}'

# 双击
osascript -e 'tell application "System Events" to double click at {100, 200}'

# 拖拽
osascript -e 'tell application "System Events" to drag from {100, 100} to {300, 300}'
```

### 4. 键盘操作

```bash
# 输入文本
osascript -e 'tell application "System Events" to keystroke "Hello World"'

# 按键组合
osascript -e 'tell application "System Events" to keystroke "c" using command down'  # Cmd+C
osascript -e 'tell application "System Events" to keystroke "v" using command down'  # Cmd+V
osascript -e 'tell application "System Events" to keystroke "f" using command down'  # Cmd+F
osascript -e 'tell application "System Events" to keystroke "t" using command down'  # Cmd+T
osascript -e 'tell application "System Events" to keystroke "0" using command down'  # Cmd+0

# 特殊按键 (key code)
osascript -e 'tell application "System Events" to key code 36'  # Return
osascript -e 'tell application "System Events" to key code 48'  # Tab
osascript -e 'tell application "System Events" to key code 49'  # Space
osascript -e 'tell application "System Events" to key code 51'  # Delete
osascript -e 'tell application "System Events" to key code 53'  # Escape
osascript -e 'tell application "System Events" to key code 123' # Left Arrow
osascript -e 'tell application "System Events" to key code 124' # Right Arrow
osascript -e 'tell application "System Events" to key code 125' # Down Arrow
osascript -e 'tell application "System Events" to key code 126' # Up Arrow
```

### 5. 中文输入（剪贴板中转）

```bash
# 复制到剪贴板
echo "中文内容" | pbcopy

# 粘贴
osascript -e 'tell application "System Events" to keystroke "v" using command down'
```

### 6. Finder 操作

```bash
# 打开路径
osascript -e 'tell application "Finder" to open (POSIX file "/Users/flychen/Downloads")'
osascript -e 'tell application "Finder" to activate'

# 选择文件
osascript -e 'tell application "Finder" to select (POSIX file "/Users/flychen/test.txt")'

# 新建文件夹
osascript -e 'tell application "Finder" to make new folder at (POSIX file "/Users/flychen/Desktop") with properties {name:"NewFolder"}'
```

---

## 飞书手机控制指令

在飞书发消息给 Hermes：

| 指令 | 效果 |
|------|------|
| `查看微信第一个对话` | 切换微信 → 截屏 → 告诉你第一个聊天对象 |
| `截图桌面` | 截屏当前桌面状态 |
| `切换到 Chrome` | 激活 Chrome 浏览器 |
| `打开下载文件夹` | Finder 打开 Downloads |
| `列出所有窗口` | 显示当前打开的所有应用 |

---

## 使用示例

### 示例 1：查看微信第一个对话

```bash
# 闭环操作流程
1. osascript -e 'tell application "WeChat" to activate' && sleep 2
2. screencapture ~/.openclaw/workspace/wechat.png
3. image 工具分析：左侧聊天列表第一个是谁
4. 返回结果："第一个对话是「打碎焦虑」"
```

### 示例 2：在 Chrome 搜索

```bash
1. osascript -e 'tell application "Google Chrome" to activate'
2. osascript -e 'tell application "System Events" to keystroke "l" using command down'  # Cmd+L
3. osascript -e 'tell application "System Events" to keystroke "https://google.com/search?q=hermes"'
4. osascript -e 'tell application "System Events" to key code 36'  # 回车
5. 截屏验证
```

### 示例 3：滚动聊天列表

```bash
# 回到顶部
osascript -e 'tell application "System Events" to key code 126 using command down'  # Cmd+Up

# 滚动到底部
osascript -e 'tell application "System Events" to key code 125 using command down'  # Cmd+Down
```

---

## 常见问题

| 问题 | 解决方案 |
|------|----------|
| 截屏看不到目标窗口 | 先 `activate`，等待 2 秒再截屏 |
| 点击位置不准 | 先截屏定位，确认坐标后再点击 |
| 中文输入乱码 | 用 `pbcopy` + `Cmd+V` 中转 |
| 权限弹窗阻止 | 去系统设置授权，然后重试 |
| 微信窗口最小化 | 用 `Cmd+0` 强制显示主窗口 |

---

## 安全提示

- ⚠️ GUI 操作会真实改变你的桌面，请确认命令后再执行
- ⚠️ 敏感操作（删除、发送消息、转账等）建议先询问用户
- ✅ 操作后用截屏验证结果
- ✅ 重要操作记录到 memory/runtime/

---

## 技术架构

```
┌─────────────────────────────────────────────┐
│         Harness GUI Agent Stack             │
├─────────────────────────────────────────────┤
│                                             │
│  hermes-agent (飞书控制)                     │
│      ↓                                      │
│  macos-gui-automation (SKILL.md)            │
│      ↓                                      │
│  ┌─────────────────────────────────────┐    │
│  │ AppleScript/osascript               │    │
│  │   - click, keystroke, activate      │    │
│  │   - window query, process control   │    │
│  └─────────────────────────────────────┘    │
│      ↓                                      │
│  screencapture + image tool                 │
│      ↓                                      │
│  visual understanding + verification        │
└─────────────────────────────────────────────┘
```

---

## 进化记录

| 版本 | 日期 | 变更 | 验证状态 |
|------|------|------|----------|
| 2.1.0 | 2026-05-26 | 适配 Harness 框架，添加 hermes metadata | ✅ 已验证 |
| 2.0.0 | 2026-05-26 | 添加闭环验证流程 | ✅ 已验证 |
| 1.0.0 | 2026-05-25 | 初始版本 | ✅ 基础功能 |

---

## 相关 Skills

- **browser-automation**: 浏览器专用自动化（Playwright）
- **apple-notes**: Apple Notes 操作
- **apple-reminders**: Apple Reminders 操作
- **web-research**: 网络研究与搜索