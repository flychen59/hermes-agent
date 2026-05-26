# GUI 自动化方案对比与速度基准

## 实测速度基准（2026-05-26，Apple Silicon M1）

| 操作 | 工具 | 延迟 |
|------|------|------|
| 移动鼠标 | cliclick m:x,y | 19ms |
| 点击 | cliclick c:x,y | 64ms |
| 打字（英文） | cliclick t:text | ~1s（逐字符） |
| 切换应用 | osascript activate | 96ms |
| 截屏 | screencapture -x | 153ms |
| 快捷键 | osascript key code | 66ms |
| 组合操作 | cliclick m+c+w | 505ms |
| Swift OCR | /tmp/ocr | ~200ms |

## 方案对比（调研结果）

| 方案 | 执行延迟 | AI 视觉 | macOS 原生 | Hermes 集成 | 推荐度 |
|------|----------|---------|------------|-------------|--------|
| cliclick + osascript + OCR | <100ms | ❌ | ✅ | ✅ 天然 | ⭐⭐⭐⭐⭐ |
| OpenHuman (Screen Intelligence) | 2-5s | ✅ | ✅ | ✅ RPC | ⭐⭐⭐⭐ |
| UI-TARS v0.2.4 | 3-8s | ✅ VLM | ✅ | ❌ 无CLI | ⭐⭐⭐ |
| Anthropic Computer Use | 3-10s | ✅ | ❌ Docker | ❌ | ⭐⭐ |
| OpenAI Operator | 5-15s | ✅ | ❌ 浏览器 | ❌ | ⭐ |

## 工具分工（最佳实践）

```
点击坐标     → cliclick c:x,y        (64ms)
移动鼠标     → cliclick m:x,y        (19ms)
打字英文     → cliclick t:text        (~1s)
打字中文     → pbcopy + Cmd+V         (66ms)
字母快捷键   → osascript key code     (66ms)
特殊按键     → cliclick kp:name       (100ms)
切换应用     → osascript activate     (96ms)
截屏         → screencapture -x       (153ms)
截屏区域     → screencapture -R x,y,w,h
文字识别     → /tmp/ocr (Swift Vision) (~200ms)
窗口查询     → osascript System Events
```

## 读取屏幕内容的决策树

```
目标：获取屏幕上的文字/UI 信息

1. 先试 AppleScript UI 查询
   osascript -e 'tell app "System Events" to tell process "X" to get description of every UI element of window 1'
   → 拿到文字？✅ 完成（最快，<100ms）
   → 只返回 missing value？→ 自绘控件应用，进入步骤 2

2. 截屏 + OCR
   screencapture -R x,y,w,h /tmp/region.png && /tmp/ocr /tmp/region.png
   → 文字清晰可读？✅ 完成（~300ms）
   → 乱码/不准确？→ 字体渲染问题，进入步骤 3

3. 截屏 + 人工确认（让用户看图）
   发送截图给用户，请用户告知内容
   → 最终兜底方案
```

## 网页操作决策树

```
目标：在 Chrome 网页上执行操作（点击按钮、导航等）

1. 直接 URL 跳转（最可靠）
   osascript -e 'tell application "Google Chrome" to set URL of active tab to "..."'
   → 页面存在？✅ 完成

2. Chrome AppleScript JS（需开启"允许 Apple 事件中的 JavaScript"）
   execute active tab javascript "document.querySelector('.btn').click()"
   → 能定位元素？✅ 完成

3. 地址栏输入 + 回车
   Cmd+L → 输入 URL → Enter
   → 适用于需要键盘导航的场景

4. OCR 定位 + cliclick 坐标点击（最后手段，精度低）
   → 仅当以上方法都不可行时使用
   → 对自定义字体/动态布局效果差
```

## 不可自动化的场景

| 场景 | 原因 | 替代方案 |
|------|------|----------|
| 闲鱼消息列表 | 网页版无消息功能（404），反爬拦截 | scrcpy + Android |
| 微信 Mac 消息 | 自绘控件，需登录状态 | 截屏 + OCR（可读但精度有限） |
| 抖音消息 | 无网页版 | scrcpy + Android |
| 银行 App 操作 | 安全控件 + 设备绑定 | 不可自动化 |

## osascript key code 速查

```
字母: A=0 S=1 D=2 F=3 H=4 G=5 Z=6 X=7 C=8 V=9 B=11 Q=12 W=13 E=14 R=15 Y=16 T=17
      1=18 2=19 3=20 4=21 6=22 7=23 8=24 9=25 0=29
      O=31 U=32 I=34 P=35 L=37 J=38 K=40 N=45 M=46

特殊: Return=36 Space=49 Tab=48 Esc=53 Delete=51 FwdDelete=117
方向: Left=123 Right=124 Down=125 Up=126
功能: F1=122 F2=120 ... F12=96 Home=115 End=119 PageUp=116 PageDown=121
```
