---
name: cloakbrowser-automation
description: "隐身浏览器自动化 — 用 CloakBrowser 绕过反爬检测，自动登录、注册、浏览网页。替代 Playwright 直接使用，过 Cloudflare/reCAPTCHA/FingerprintJS。"
version: 1.1.0
author: Hermes Agent
metadata:
  hermes:
    tags: [browser, automation, stealth, cloaking, web, scraping, login, registration]
    related_skills: [web-research, dynamic-task-decomposition]
---

# CloakBrowser 隐身浏览器自动化

## 触发条件

当用户要求以下操作时，自动使用 CloakBrowser 而非普通 Playwright：
- 登录某个网站
- 注册账号
- 在有反爬检测的网站上操作（Cloudflare、reCAPTCHA、FingerprintJS）
- 网页搜索调研被拦截时

## 安装状态

- Python: `pip3 install cloakbrowser` ✅ 已安装 (v0.3.30)
- Python: `pip3 install patchright` ✅ 已安装 (v1.60.0)
- Chromium: `npx cloakbrowser install` 下载中（~200MB），`npx cloakbrowser info` 查看状态。下载可能超时需 `terminal(background=true)` 后台跑
- 用法: `from patchright.sync_api import sync_playwright`（推荐，cloakbrowser import 有兼容问题）
- **实测验证（2026-05-25）**：百度/GitHub headless 正常 ✅，反检测 `navigator.webdriver: False` ✅，Google 登录密码通过 ✅（headed 模式），2FA 需手机配合

## 关键发现：headless vs headed

**Google 登录**（accounts.google.com）：
- headless=True → 被检测，URL 变 `/v3/signin/rejected`，密码框不出现
- headless=False → 正常通过邮箱+密码验证，但 2FA 仍需手动（手机推送/验证码）

**普通网站**（baidu.com, github.com）：
- headless=True 完全正常，反检测通过（`navigator.webdriver: False`）

**结论**：高安全网站用 `headless=False`，普通网站 headless 即可。

## 推荐用法（patchright）

```python
from patchright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # 高安全网站
    context = browser.new_context(
        viewport={'width': 1280, 'height': 800},
        user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
        locale='zh-CN',
    )
    page = context.new_page()
```

## 核心代码模板

### 自动登录

```python
from cloakbrowser import launch

def auto_login(url, username, password):
    browser = launch(humanize=True)  # humanize=True 模拟人类行为
    page = browser.new_page()

    # 1. 打开登录页
    page.goto(url)
    page.wait_for_load_state("networkidle")

    # 2. 填写账号密码
    page.fill('input[type="email"], input[name="username"], input[name="email"]', username)
    page.fill('input[type="password"]', password)

    # 3. 点击登录
    page.click('button[type="submit"], input[type="submit"], button:has-text("登录"), button:has-text("Log in"), button:has-text("Sign in")')

    # 4. 等待跳转
    page.wait_for_load_state("networkidle")

    return browser, page
```

### 自动注册

```python
def auto_register(url, form_data):
    """
    form_data = {
        "email": "xxx@xxx.com",
        "password": "xxx",
        "username": "xxx",
        # ... 其他字段
    }
    """
    browser = launch(humanize=True, headless=False)  # 注册建议用有窗口模式，方便处理验证
    page = browser.new_page()
    page.goto(url)
    page.wait_for_load_state("networkidle")

    # 逐个填写表单字段
    for field, value in form_data.items():
        selectors = [
            f'input[name="{field}"]',
            f'input[id="{field}"]',
            f'input[placeholder*="{field}"]',
            f'input[type="{field}"]',
        ]
        for selector in selectors:
            try:
                page.fill(selector, str(value))
                break
            except:
                continue

    # 点击注册按钮
    page.click('button[type="submit"], button:has-text("注册"), button:has-text("Sign up"), button:has-text("Register")')
    page.wait_for_load_state("networkidle")

    return browser, page
```

### 带代理的搜索调研

```python
def stealth_research(url, proxy=None):
    kwargs = {"humanize": True}
    if proxy:
        kwargs["proxy"] = proxy

    browser = launch(**kwargs)
    page = browser.new_page()
    page.goto(url, wait_until="domcontentloaded")
    content = page.content()
    return browser, page, content
```

## 重要参数

| 参数 | 说明 | 推荐值 |
|------|------|--------|
| `humanize=True` | 模拟人类鼠标/键盘行为 | **注册和登录时必须开** |
| `headless=False` | 显示浏览器窗口 | 注册时建议开，方便手动处理验证码 |
| `headless=True` | 无窗口模式 | 批量操作、定时任务用 |
| `proxy="http://user:pass@host:port"` | 代理 | 被封IP时使用 |
| `timezone="Asia/Shanghai"` | 时区伪装 | 国外网站建议配合geoip |
| `locale="zh-CN"` | 语言伪装 | 按目标网站设置 |

## 反检测能力

- reCAPTCHA v3: 0.9分（人类级别）
- Cloudflare Turnstile: ✅ 通过
- FingerprintJS: ✅ 通过
- BrowserScan: ✅ 正常
- navigator.webdriver: false
- TLS 指纹: 与 Chrome 一致

## References

- **`references/taobao-xianyu-login.md`** — 淘宝/闲鱼登录完整踩坑记录：JS 赋值不生效、完整流程、选择器表、闲鱼封闭生态、macOS 0 窗口、multi-agent 限制、Hermes browser vs CloakBrowser 分工
- **`references/boss-zhipin-scraping.md`** — BOSS直聘爬取完整方案：首页绕过反爬技巧、验证码类型、CSS 选择器表、截图方案对比、URL 格式
- **skill `job-site-scraping`** — 招聘网站岗位搜索独立 skill，含通用模板脚本 `templates/job-search-scraper.py`

## 陷阱

- **CloakBrowser Chromium 未下载**：`npx cloakbrowser install` 下载慢，用 `terminal(background=true)` 后台跑
- **`from cloakbrowser import launch` 可能报错**：用 `from patchright.sync_api import sync_playwright` 替代
- **Google 等 2FA 网站**：headless 模式被检测为 bot，必须 `headless=False`；即使密码正确仍需手机确认二次验证
- **每步加 `time.sleep()`**：Google 登录每步操作间需要等 2-3 秒，太快会被拦截
- **viewport 要设桌面尺寸**：不设会默认移动版，选择器不同
- 每次操作完成后记得 `browser.close()` 释放资源
- 不要短时间内对同一网站高频操作，仍有被封风险
- **macOS 上 headless=False 可能 0 窗口**：patchright 启动的 "Google Chrome for Testing" 在 macOS 上 osascript 报 0 窗口，page.screenshot() 返回空白。替代：用 Hermes browser 操作页面
- **execute_code sandbox 没有 patchright**：必须用 `terminal()` 运行脚本文件
- **淘宝表单 JS 设值不生效**：框架绑定 input，`input.value = 'xxx'` + dispatchEvent 不更新框架状态。**验证码必须 browser_type**，手机号可以 JS 填
- **验证码只能点一次"获取"**：每次点击发新码，旧码立即失效
- **browser_type 必须瞄准正确 ref**：短信模式下 accessibility tree 被国家代码 combobox（191个 option）淹没，看不到验证码输入框的 ref。解决方案：先用 `browser_console` 执行 `document.getElementById('fm-smscode').focus()`，然后直接 `browser_console` 键入 `document.execCommand('insertText', false, '验证码')` — 这比 browser_type 更可靠，因为 browser_type 需要可见的 ref 元素
- **execCommand insertText 绕过框架问题**：`document.execCommand('insertText', false, '9939')` 在已 focus 的 input 上可以正确触发框架状态更新，比 `input.value = ...` 更可靠
- **glm-5.1 子 agent delegate_task 效果差**：40-48 次 API 调用后超时或空结果，简单任务直接主 agent 做
- **vision 工具被纯文本模型拦截**：glm-5.1 下 vision_analyze/browser_vision 都报 "Your request was blocked"，需要 VLM 模型
- **BOSS直聘 IP 封锁极严**：普通 Playwright、patchright headless、系统 Chrome（含隐身模式）全部被 IP 级别拦截到安全验证页。必须 patchright headless=False + 手动过图片点选验证码。验证码是「请选中下图中所有的：XX」类型，无法自动识别，必须人工操作
- **patchright headed 窗口在 macOS 上不可见**：patchright 启动的 Chromium 窗口可能不会自动置前。需要 `osascript -e 'tell application "System Events" to set frontmost of process "Chromium" to true'` 强制激活。进程名是 "Chromium" 不是 "Google Chrome"
- **screencapture 截 Retina 全屏 → OCR 空**：screencapture 输出 2x 分辨率（2940x1912），sips -Z 1440 缩小后 Swift Vision OCR 仍返回空。但 patchright page.screenshot() 输出标准分辨率（1280x800），OCR 正常。**必须用 patchright 的 screenshot 而非 screencapture 来获取可 OCR 的页面截图**
- **Chrome Apple Events JS 开启步骤**：菜单「显示 → 开发者 → 允许 Apple 事件中的 JavaScript」（注意 macOS Chrome 中文菜单是「显示」不是「查看」）。开启后可能需要重启 Chrome 才生效。用 AppleScript 点击菜单开启时，菜单路径：`menu bar item "显示" → menu "显示" → menu item "开发者" → menu "开发者" → menu item "允许 Apple 事件中的 JavaScript"`
- **screencapture -l windowID 和 -R x,y,w,h 均失败**：在当前环境下 `screencapture -R` 报 "could not create image from rect"，`screencapture -l` 报 "could not create image from window"。只能用 `screencapture -x` 全屏截取（但 OCR 有问题），或用 patchright page.screenshot()
- **反爬绕过技巧：先访问首页**：很多反爬网站（如 BOSS直聘）直接访问深层 URL 触发验证码，但先 `page.goto("https://example.com/")` 建立合法 session/cookie 后再跳转目标页面可绕过。优先尝试此方法。适用场景：招聘网站、电商平台、社交媒体等需要合法 session 的网站
- **page.go_back() 在 SPA 网站可能超时**：如 BOSS直聘等 SPA 网站的 go_back 会触发 30s timeout。替代方案：`page.goto(original_url)` 直接导航回去。所有涉及列表→详情→返回列表的爬取场景都应用 goto 代替 go_back
- **反爬网站筛选不要用 URL 参数**：BOSS直聘等网站在搜索 URL 加 `experience=104` 等筛选参数会触发登录弹窗。应加载无筛选的搜索页后，用 `page.evaluate("...el.click()...")` 点击页面上的筛选标签
- **JD 截断处理**：未登录状态招聘网站详情页 JD 末尾显示"登录查看完整内容"，用 JS `.replace(/登录查看完整内容.*/g, '')` 清理。截断后的内容无法恢复
