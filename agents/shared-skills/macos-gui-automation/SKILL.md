---
name: macos-gui-automation
description: "macOS GUI 自动化控制 — 模拟点击、键盘输入、窗口管理、应用控制、截屏视觉理解闭环。使用 AppleScript/osascript 实现全系统 GUI 操作，支持操作验证。"
version: 2.0.0
metadata:
  openclaw:
    emoji: "🖥️"
    os: ["darwin"]
    requires:
      permissions: ["辅助功能 (Accessibility)", "屏幕录制"]
---

# macOS GUI 自动化（闭环验证版）

通过 AppleScript + exec + image 工具实现 macOS 全系统 GUI 自动化控制，**支持操作后视觉验证**。

## 前置要求

**必须授权两项权限**：
1. **辅助功能**：系统设置 → 隐私与安全性 → 辅助功能 → 添加 Terminal
2. **屏幕录制**：系统设置 → 隐私与安全性 → 屏幕录制 → 允许 Terminal

验证授权：
```bash
# 辅助功能测试
osascript -e 'tell application "System Events" to get name of first process'

# 截屏测试
screencapture -x ~/.openclaw/workspace/test.png
```

---

## 核心能力（已验证 ✅）

| 能力 | 工具 | 状态 |
|------|------|------|
| 截屏 | `screencapture` | ✅ 已验证 |
| 视觉理解 | `image` 工具 | ✅ 已验证 |
| 点击操作 | AppleScript `click at {x,y}` | ✅ 已验证 |
| 键盘输入 | AppleScript `keystroke` | ✅ 已验证 |
| 窗口查询 | AppleScript `get name of every process` | ✅ 已验证 |
| 应用切换 | AppleScript `activate` | ✅ 已验证 |

---

## 核心命令

### 1. 截屏 + 视觉理解（闭环验证）

```bash
# 截屏
screencapture -x ~/.openclaw/workspace/screen.png

# 视觉理解（AI 分析）
# 使用 image 工具分析截图
```

### 2. 窗口管理

```bash
# 列出所有可见应用
osascript -e 'tell application "System Events" to get name of every process whose background only is false'

# 获取前台应用
osascript -e 'tell application "System Events" to get name of first process whose frontmost is true'

# 切换应用
osascript -e 'tell application "Finder" to activate'
osascript -e 'tell application "WeChat" to activate'
osascript -e 'tell application "Google Chrome" to activate'
```

### 3. 鼠标操作

```bash
# 点击坐标 (x, y) - 从左上角开始
osascript -e 'tell application "System Events" to click at {100, 200}'

# 右键点击
osascript -e 'tell application "System Events" to right click at {100, 200}'

# 双击
osascript -e 'tell application "System Events" to double click at {100, 200}'
```

### 4. 键盘操作

```bash
# 输入文本
osascript -e 'tell application "System Events" to keystroke "Hello World"'

# 按键组合 (Cmd+C)
osascript -e 'tell application "System Events" to keystroke "c" using command down'

# Cmd+F 搜索
osascript -e 'tell application "System Events" to keystroke "f" using command down'

# 回车键 (key code 36)
osascript -e 'tell application "System Events" to key code 36'

# 常用 key code:
# 36 = Return, 48 = Tab, 49 = Space, 51 = Delete, 53 = Escape
# 123 = Left, 124 = Right, 125 = Down, 126 = Up
```

### 5. 中文输入（剪贴板中转）

```bash
# 先复制到剪贴板
echo "中文内容" | pbcopy

# 再粘贴
osascript -e 'tell application "System Events" to keystroke "v" using command down'
```

---

## 操作闭环流程

### 标准操作流程：观察 → 操作 → 验证

```
1. 截屏观察当前状态
   screencapture -x ~/.openclaw/workspace/state-before.png

2. 分析截图，确定目标位置
   image 工具分析

3. 执行操作
   click / keystroke / activate

4. 截屏验证操作结果
   screencapture -x ~/.openclaw/workspace/state-after.png

5. 分析验证结果
   image 工具分析
```

---

## 使用示例

### 示例 1：切换到 Finder 并搜索文件

```bash
# 1. 切换应用
osascript -e 'tell application "Finder" to activate'
sleep 1

# 2. 打开搜索框 (Cmd+F)
osascript -e 'tell application "System Events" to keystroke "f" using command down'
sleep 1

# 3. 输入搜索词
osascript -e 'tell application "System Events" to keystroke "hermes"'

# 4. 截屏验证
screencapture -x ~/.openclaw/workspace/result.png
# 使用 image 工具分析验证
```

### 示例 2：查看微信第一个对话

```bash
# 1. 切换到微信
osascript -e 'tell application "WeChat" to activate'
sleep 1

# 2. 截屏
screencapture -x ~/.openclaw/workspace/wechat.png

# 3. 视觉理解第一个对话对象
# image 工具分析左侧对话列表
```

### 示例 3：在浏览器中点击某个链接

```bash
# 1. 切换到 Chrome
osascript -e 'tell application "Google Chrome" to activate'
sleep 1

# 2. 截屏确定链接位置
screencapture -x ~/.openclaw/workspace/chrome-before.png

# 3. 分析截图，找到链接坐标

# 4. 点击
osascript -e 'tell application "System Events" to click at {500, 300}'

# 5. 截屏验证
screencapture -x ~/.openclaw/workspace/chrome-after.png
```

---

## 常见问题

### Q: 截屏看不到微信窗口内容
A: 确保微信窗口在前台且未被遮挡，先 `activate` 再截屏

### Q: 点击位置不准
A: 坐标系从左上角 (0,0) 开始，先用截屏确定准确位置

### Q: 中文输入乱码
A: 用剪贴板中转：`echo "中文" | pbcopy` → `Cmd+V`

### Q: 权限弹窗阻止操作
A: 去系统设置授权，然后重试

---

## 安全提示

- GUI 操作会真实改变你的桌面，请确认命令后再执行
- 敏感操作（删除、发送消息等）建议先询问
- 操作后用截屏验证结果

---

## 技术实现

- **截屏**：`screencapture` 命令
- **视觉理解**：OpenClaw `image` 工具 + 视觉模型
- **点击/键盘**：AppleScript `System Events`
- **窗口管理**：AppleScript `tell application`

---

## 更新记录

| 版本 | 日期 | 变更 |
|------|------|------|
| 2.0.0 | 2026-05-26 | 添加闭环验证流程，所有能力已实测验证 |
| 1.0.0 | 2026-05-25 | 初始版本 |

## 相关 Skills

- browser-automation: 浏览器专用自动化
- apple-notes: Apple Notes 操作
- apple-reminders: Apple Reminders 操作