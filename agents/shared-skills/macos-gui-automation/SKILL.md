---
name: macos-gui-automation
description: "macOS GUI 自动化控制 — 模拟点击、键盘输入、窗口管理、应用控制、截屏视觉理解闭环。使用 AppleScript/osascript 实现全系统 GUI 操作。"
version: 3.2.0
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
    success_rate: 0.55
    auto_evolve: true
    patches:
      - date: "2026-05-26"
        change: "v3.1.0: 闲鱼实测暴露的问题——坐标点击对网页不可靠、移动App无网页消息API、OCR对自定义字体乱码、/tmp/ocr不持久。新增scripts/ocr.swift持久化源码、references中增加决策树和不可自动化场景表"
    patches:
      - date: "2026-05-26"
        change: "实测补全已知限制：System Events 超时、cliclick 无 scroll、辅助功能权限、browser_vision vs screencapture 区别。成功率从 0.90 下调至 0.55（实测网页滚动/操作失败居多）"
      - date: "2026-05-26"
        change: "添加并发检测 + 错误恢复机制"
      - date: "2026-05-26"
        change: "v3.0.0: 大幅重构。新增 Swift OCR 脚本(scripts/ocr.swift)解决 vision_analyze 被拦截问题；发现微信等自绘控件应用无法用 AppleScript 读取 UI；合并去重已知限制章节；新增 references/speed-benchmarks.md（方案对比+key code 速查）"
---

# macOS GUI 自动化

> 🖥️ **桌面 Agent 核心能力** — 通过视觉理解 + 操作执行 + 结果验证实现完整 GUI 控制闭环

## 权限设置

### 必须授权

| 权限 | 路径 | 应用 |
|------|------|------|
| **辅助功能** | 系统设置 → 隐私与安全性 → 辅助功能 | Terminal.app + `/usr/bin/osascript` + `/opt/homebrew/bin/cliclick`（三项缺一不可） |
| **屏幕录制** | 系统设置 → 隐私与安全性 → 屏幕录制 | Terminal.app |
| **自动化** | 系统设置 → 隐私与安全性 → 自动化 | Terminal → 允许控制其他应用 |

### 快速授权命令

```bash
# 打开三个权限设置页面
open "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"
open "x-apple.systempreferences:com.apple.preference.security?Privacy_ScreenCapture"
open "x-apple.systempreferences:com.apple.preference.security?Privacy_Automation"

# 在辅助功能页面点 + 号，逐一添加：
#   /usr/bin/osascript
#   /opt/homebrew/bin/cliclick
#   /Applications/Utilities/Terminal.app（如果已有则跳过）
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

## ⚠️ 已知限制（2026-05 实测）

### 1. 辅助功能权限必须预授权三项（缺一不可）
- **Terminal.app** — 终端本身
- **osascript** — `/usr/bin/osascript`（未授权报 `-25211`）
- **cliclick** — `/opt/homebrew/bin/cliclick`（未授权持续 WARNING）
- 快速授权：`open "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"` 点 `+` 逐一添加
- 自动化权限也要开：`open "x-apple.systempreferences:com.apple.preference.security?Privacy_Automation"`
- 屏幕录制也要开：`open "x-apple.systempreferences:com.apple.preference.security?Privacy_ScreenCapture"`

### 2. cliclick kp 不支持字母键
- `kp` 只接受特殊键名（return/esc/space/arrow-* 等），`kp:v` `kp:f` 都会报错
- **字母快捷键用 osascript key code**：`osascript -e 'tell application "System Events" to key code 9 using command down'`（Cmd+V）
- 字母 key code 表：V=9, C=8, X=7, A=0, S=1, Z=6, F=3, L=37, T=17, W=13, Q=12, N=45

### 3. cliclick 不支持滚动
- cliclick 5.1 没有 scroll 命令
- 替代：`browser_scroll`（网页）或 osascript key code 125/126（方向键，需权限）

### 4. System Events 超时（-1712）
- 目标应用有弹窗/权限对话框时会阻塞
- 解决：优先用 browser_navigate 操作网页，System Events 作最后手段

### 6. Chrome AppleScript JS 默认关闭
- 需手动开启「查看 → 开发者 → 允许 Apple 事件中的 JavaScript」
- **注意 macOS 中文 Chrome 菜单是「显示」不是「查看」**
- 菜单路径：`menu bar item "显示" → menu "显示" → menu item "开发者" → menu "开发者" → menu item "允许 Apple 事件中的 JavaScript"`
- 未开启返回错误码 12
- 可用 AppleScript 自动点击菜单开启：
```applescript
tell application "Google Chrome" to activate
delay 0.3
tell application "System Events"
    tell process "Google Chrome"
        click menu bar item "显示" of menu bar 1
        delay 0.3
        click menu item "开发者" of menu "显示" of menu bar item "显示" of menu bar 1
        delay 0.3
        click menu item "允许 Apple 事件中的 JavaScript" of menu "开发者" of menu item "开发者" of menu "显示" of menu bar item "显示" of menu bar 1
    end tell
end tell
```
- 开启后可能需要重启 Chrome 才生效（实测有时不用）

- **screencapture -R x,y,w,h 和 -l windowID 均可能失败**：实测 `screencapture -R` 报 "could not create image from rect"，`screencapture -l` 报 "could not create image from window"。只能用 `screencapture -x` 全屏截取（但 Retina OCR 有问题），或用 patchright `page.screenshot()`
- **screencapture vs browser_vision 不可混用**
- `screencapture` → 本地桌面（受窗口遮挡影响）
- `browser_vision` → 云端无头浏览器（和本地 Chrome 完全独立）
- 操作本地应用必须用 `screencapture`

### 7. vision_analyze 拦截本地截图
- Hermes `vision_analyze` 对本地截图返回 "Your request was blocked"
- **替代**：用 `/tmp/ocr`（Swift Vision OCR）识别文字，见 OCR 章节

### 推荐的可靠操作流程

```
1. open -a "App Name"           # 打开/激活应用
2. sleep 3                      # 等待窗口加载
3. screencapture /tmp/scr.png   # 截屏
4. vision_analyze               # 分析内容
5. 根据分析结果决定下一步
```

## ✅ 实测速度基准（2026-05-26 通过）

| 操作 | 工具 | 延迟 |
|------|------|------|
| 移动鼠标 | cliclick m:x,y | **19ms** |
| 点击 | cliclick c:x,y | **64ms** |
| 打字 | cliclick t:text | **~1s**（逐字符） |
| 切换应用 | osascript activate | **96ms** |
| 截屏 | screencapture -x | **153ms** |
| 快捷键 | osascript key code | **66ms** |
| 组合操作 | cliclick m+c+w | **505ms** |

### 快捷键：osascript key code 方案（已验证可用）

cliclick 的 `kp` 只支持特殊键名（return/esc/space 等），**字母快捷键必须用 osascript key code**：

```bash
# 常用 key code 对照表
# V=9, C=8, X=7, A=0, S=1, Z=6, F=3, L=37, T=17, W=13, Q=12, N=45
# Return=36, Space=49, Tab=48, Esc=53, Delete=51
# Left=123, Right=124, Down=125, Up=126

# Cmd+V (粘贴)
osascript -e 'tell application "System Events" to key code 9 using command down'

# Cmd+C (复制)
osascript -e 'tell application "System Events" to key code 8 using command down'

# Cmd+Space (Spotlight)
osascript -e 'tell application "System Events" to key code 49 using command down'

# Cmd+Tab (切换应用)
osascript -e 'tell application "System Events" to key code 48 using command down'
```

### 推荐的完整工具链

```
┌─────────────────────────────────────────┐
│ 操作类型          → 最佳工具             │
├─────────────────────────────────────────┤
│ 点击坐标          → cliclick c:x,y      │
│ 移动鼠标          → cliclick m:x,y      │
│ 打字（英文）      → cliclick t:text      │
│ 打字（中文）      → pbcopy + Cmd+V       │
│ 快捷键（字母）    → osascript key code   │
│ 快捷键（特殊键）  → cliclick kp:name     │
│ 切换应用          → osascript activate   │
│ 截屏              → screencapture -x     │
│ 窗口查询          → osascript System Events│
└─────────────────────────────────────────┘
```

## 常见问题

| 问题 | 解决方案 |
|------|----------|
| 截屏看不到目标窗口 | 先 `activate`，等待 2-3 秒再截屏 |
| 点击位置不准 | 先截屏定位，确认坐标后再点击 |
| 中文输入乱码 | 用 `pbcopy` + `Cmd+V` 中转 |
| 权限弹窗阻止 | 去系统设置授权，然后重试 |
| 微信窗口最小化 | 用 `Cmd+0` 强制显示主窗口 |
| System Events 超时 -1712 | 辅助功能权限未授予，需手动开启 |
| osascript 报错 -25211 | **osascript 本身未被授权辅助功能**，需在系统设置中添加 `/usr/bin/osascript` |
| cliclick 持续 WARNING | **cliclick 未被授权辅助功能**，需在系统设置中添加 `/opt/homebrew/bin/cliclick` |
| screencapture 抓到错误窗口 | 先 activate 目标应用，等 3 秒 |
| browser_vision 截图不对 | 内置浏览器是云端的，用 screencapture 代替 |
| 滚动页面失败 | 目前无可靠方案，需辅助功能权限 |
| System Events 超时 (-1712) | 改用内置浏览器操作网页，或检查权限弹窗 |
| cliclick scroll 无效 | cliclick 5.1 不支持滚动，改用 browser_scroll 或 JS |
| 截屏内容和预期不符 | 确认是用 screencapture（本地桌面）还是 browser_vision（云端浏览器）|

---

## 安全提示

- ⚠️ GUI 操作会真实改变你的桌面，请确认命令后再执行
- ⚠️ 敏感操作（删除、发送消息、转账等）建议先询问用户
- ✅ 操作后用截屏验证结果
- ✅ 重要操作记录到 memory/runtime/

---

## OCR 识别（macOS 原生 Vision 框架）

当 `vision_analyze` 被拦截（隐私策略阻止）时，用本地 Swift OCR 脚本替代：

```bash
# 使用已编译的 OCR 工具（scripts/ocr.swift）
/tmp/ocr /tmp/screenshot.png
```

脚本源码在 `scripts/ocr.swift`，支持中英文，编译命令：
```bash
swiftc scripts/ocr.swift -o /tmp/ocr -framework Vision -framework AppKit -framework CoreImage
```
首次使用前检查：`[ -f /tmp/ocr ] || swiftc <skill_dir>/scripts/ocr.swift -o /tmp/ocr -framework Vision -framework AppKit -framework CoreImage`

**适用场景**：微信/QQ 等自绘控件应用，AppleScript 无法读取 UI 文字，只能截屏 + OCR。

## ⚠️ 关键陷阱：vision_analyze 不可用于本地截图

- Hermes 的 `vision_analyze` 工具会拦截本地截屏（返回 `"Your request was blocked"`）
- **替代方案**：用 `scripts/ocr.swift` 编译的 `/tmp/ocr` 做本地 OCR 文字识别
- `browser_vision` 只能用于云端无头浏览器的截图，不适用于桌面截屏

## ⚠️ 关键陷阱：自绘控件应用（微信、QQ、Discord 等）

- 微信/QQ 使用**自绘控件**（非标准 NSView），AppleScript 的 `UI element` 查询几乎拿不到文字内容
- `description of every UI element of window 1` 只返回空值或"missing value"
- **唯一可行路径**：截屏 → OCR 识别文字 → 基于坐标点击
- `screencapture -R x,y,w,h` 可以截取指定区域，用于精准截取聊天列表

## ⚠️ 关键陷阱：坐标点击在网页上不可靠

- 闲鱼等现代 Web 应用的底部导航是**动态渲染的 DOM 元素**，位置随屏幕大小/缩放/内容变化
- OCR 对网页自定义字体的识别准确率很低（大量乱码），无法精确定位
- **策略优先级**：Chrome AppleScript JS → 地址栏 URL 跳转 → OCR 定位坐标 → cliclick 点击（从高到低）
- 如果 Chrome 允许了 Apple Events JS（查看→开发者→允许），优先用 `execute javascript` 定位元素坐标
- **直接 URL 导航最可靠**：`osascript -e 'tell application "Google Chrome" to set URL of active tab of window 1 to "https://..."'`

## ⚠️ 关键陷阱：移动优先 App 无法通过网页自动化消息

- 闲鱼（goofish.com）、抖音等移动优先 App 的**消息/聊天功能在网页版不存在**
- `/msg` `/chat` 等消息 URL 返回 404
- 浏览器自动化（browser_navigate）也会被闲鱼反爬检测拦截（"非法访问"）
- **解决**：需要用 scrcpy（Android 投屏）或 Xcode iOS 模拟器才能自动化这类 App
- 安装 scrcpy：`brew install scrcpy adb`

## ⚠️ 关键陷阱：iOS App on Apple Silicon（WrappedBundle）

- 用户安装的闲鱼是通过 Mac App Store 安装的 **iOS App**（通过 Apple Silicon 兼容层运行）
- 目录结构：`/Applications/闲鱼.app/Wrapper/Runner.app/` — 注意没有 `Contents/` 子目录
- 进程名是 `Runner`（不是中文名），`ps aux | grep Runner` 可找到
- **0 个窗口**：iOS App 在 macOS 上运行时 System Events 报 `count of windows = 0`
- `activate` 无效：`open -a "闲鱼"` 能启动进程，但无法通过 osascript 激活到前台
- 截屏也无法捕获其内容（可能需要 screen recording 权限授权给 Runner）
- **结论**：iOS 兼容层 App 目前**无法通过 Hermes 进行 GUI 自动化**
- 如需操作这类 App，必须用 scrcpy + Android 手机或 iOS 模拟器

## ⚠️ 关键陷阱：/tmp/ocr 不持久 + Retina 截图问题

- `/tmp/ocr` 是本次编译的 Swift 二进制，**重启后会被清理**
- 首次使用前需检查并重新编译：
  ```bash
  [ -f /tmp/ocr ] || swiftc ~/.hermes/skills/macos-gui-automation/scripts/ocr.swift -o /tmp/ocr -framework Vision -framework AppKit -framework CoreImage
  ```
- **Retina 截图 OCR 空输出**：`screencapture` 在 Retina 屏上生成超大 PNG（8MB+，2940×1912），即使 `sips -Z 1440` 缩小后 Swift Vision OCR **仍返回空字符串**
  - `screencapture -x` 全屏 + sips 缩小 → OCR 空
  - `screencapture -R x,y,w,h` → "could not create image from rect" 失败
  - `screencapture -l windowID` → "could not create image from window" 失败
  - **解决方案**：用 patchright/Playwright 的 `page.screenshot()` 截图（输出标准分辨率如 1280x800），OCR 正常
- **OCR 对闲鱼等自定义字体/图标几乎无效**：大量乱码，无法精确定位按钮
- **OCR 空输出时**：先确认截图来源。screencapture 的 Retina 截图即使用 sips 缩小 OCR 也可能空，改用 patchright screenshot

## 技术架构

```
┌──────────────────────────────────────────────────┐
│            Harness GUI Agent Stack                │
├──────────────────────────────────────────────────┤
│                                                  │
│  hermes-agent (飞书控制)                          │
│      ↓                                           │
│  macos-gui-automation (SKILL.md)                 │
│      ↓                                           │
│  ┌────────────────────────────────────────┐      │
│  │ 操作层（按场景选择最佳工具）            │      │
│  │  cliclick    → 点击/移动/打字           │      │
│  │  osascript   → 快捷键/切换应用/窗口查询  │      │
│  │  screencapture → 截屏                   │      │
│  └────────────────────────────────────────┘      │
│      ↓                                           │
│  ┌────────────────────────────────────────┐      │
│  │ 理解层（二选一）                        │      │
│  │  vision_analyze → 云端截屏分析          │      │
│  │  /tmp/ocr (Swift Vision) → 本地OCR    │      │
│  └────────────────────────────────────────┘      │
│      ↓                                           │
│  visual understanding + verification             │
└──────────────────────────────────────────────────┘
```

---

## 进化记录

| 版本 | 日期 | 变更 | 验证状态 |
|------|------|------|----------|
| 3.2.0 | 2026-05-26 | 新增：iOS App (WrappedBundle) 无法自动化陷阱、Retina 截图 OCR 空输出修复、Chrome 地址栏 URL 跳转作为首选导航方式 | ✅ 闲鱼+微信实测 |
| 3.1.0 | 2026-05-26 | 新增：坐标点击不可靠陷阱、移动App无法网页自动化、OCR决策树、scripts/ocr.swift 持久化、/tmp/ocr 重启清理提醒 | ✅ 闲鱼实测验证 |
| 3.0.0 | 2026-05-26 | 重构：新增 Swift OCR、微信自绘控件陷阱、合并去重限制章节、速度基准参考文件 | ✅ 已验证 |
| 2.1.0 | 2026-05-26 | 适配 Harness 框架，添加 hermes metadata | ✅ 已验证 |
| 2.0.0 | 2026-05-26 | 添加闭环验证流程 | ✅ 已验证 |
| 1.0.0 | 2026-05-25 | 初始版本 | ✅ 基础功能 |

---

## 相关 Skills

- **browser-automation**: 浏览器专用自动化（Playwright）
- **apple-notes**: Apple Notes 操作
- **apple-reminders**: Apple Reminders 操作
- **web-research**: 网络研究与搜索