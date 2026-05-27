---
name: job-site-scraping
description: "招聘网站岗位搜索与 JD 抓取 — 用 CloakBrowser 绕过反爬，搜索关键词，批量提取职位列表和 JD 详情。已验证 BOSS直聘。"
version: 1.0.0
author: Hermes Agent
metadata:
  hermes:
    tags: [job, scraping, browser, automation, stealth, boss-zhipin, recruitment]
    related_skills: [cloakbrowser-automation, macos-gui-automation]
---

# 招聘网站岗位搜索与 JD 抓取

## 触发条件

- 用户要求搜索某个招聘网站的岗位（BOSS直聘、拉勾、猎聘等）
- 用户要查看某个岗位的 JD（职位描述）
- 用户要对比多个岗位的要求

## 核心思路

招聘网站反爬极严，**不能用**：
- ❌ Hermes 内置浏览器（被反爬拦截）
- ❌ curl/fetch（IP 封锁）
- ❌ 普通 Playwright（被检测）
- ❌ patchright headless=True（BOSS直聘会触发验证码）

**唯一可靠方案**：CloakBrowser (patchright) headless=False + 反爬绕过技巧

## 关键步骤

### 1. 环境准备

```bash
# patchright 必须已安装
pip3 install patchright
# Chromium 已下载
npx cloakbrowser install  # 或确认 ~/.cache/rod/browser/chromium-* 存在
# OCR 工具已编译
[ -f /tmp/ocr ] || swiftc ~/.hermes/skills/macos-gui-automation/scripts/ocr.swift -o /tmp/ocr -framework Vision -framework AppKit -framework CoreImage
```

### 2. 通用爬取模板

使用 `templates/job-search-scraper.py` 模板脚本，传入参数即可：
- `SITE`: 目标网站（boss, lagou, liepin）
- `KEYWORD`: 搜索关键词
- `CITY`: 城市（100010000=全国）
- `MAX_JOBS`: 最大抓取数

```bash
python3 ~/.hermes/skills/devops/job-site-scraping/templates/job-search-scraper.py
```

### 3. 反爬绕过策略（按优先级）

| 策略 | 适用场景 | 说明 |
|------|---------|------|
| **先访问首页** | BOSS直聘 | 直接搜深层URL触发验证码，先 goto 首页建 session 再搜可绕过 |
| **headless=False + 手动验证** | 所有极严网站 | 弹出浏览器让用户手动过验证码，脚本轮询检测 |
| **OCR 辅助** | 需要视觉识别时 | patchright screenshot + Swift OCR 识别页面内容 |

### 4. 截图方案选择

| 方案 | 用途 | OCR 可用 |
|------|------|---------|
| `page.screenshot()` | patchright 内部截图 | ✅ 正常 |
| `screencapture -x` | macOS 桌面截图 | ❌ Retina 2x 分辨率 OCR 空 |
| `browser_vision` | Hermes 云端浏览器 | 不适用 patchright |

**结论**：始终用 `page.screenshot()` 截图，不要用 screencapture。

## BOSS 直聘实测经验（2026-05-27）

### 搜索 URL 格式

```
# 搜索页
https://www.zhipin.com/web/geek/job?query={keyword}&city={city_code}

# 城市代码
100010000 = 全国
101010100 = 北京
101020100 = 上海
101280100 = 广州
101280600 = 深圳
101210100 = 杭州
```

### CSS 选择器表

| 元素 | 选择器 | 备注 |
|------|--------|------|
| 职位卡片 | `.job-card-wrapper` 或 `.job-card-box` | 搜索结果列表 |
| 职位名称 | `.job-name` | 卡片内 |
| 薪资 | `.salary` | 卡片内 |
| 公司 | `.company-name` 或 `.company-text a` | 卡片内 |
| 标签 | `.tag-list` | 经验/学历 |
| 详情链接 | `a[href*="/job_detail/"]` | 卡片内 |
| JD 正文 | `.job-sec-text` 或 `.job-detail-section` | 详情页 |

### 关键发现

1. **直接访问搜索 URL 必触发验证码**，但先 `page.goto("https://www.zhipin.com/")` 再搜索可绕过
2. 搜索页可能跳转到「全国招聘」页（title 含"全国招聘"），但内容包含搜索结果
3. `page.go_back()` 在 SPA 页面会超时，用 `page.goto(SEARCH_URL)` 代替
4. 详情页 JD 可能有「登录查看完整内容」截断
5. 职位列表每页约 15-30 个，可翻页

### 完整脚本模板

见 `templates/job-search-scraper.py`

## 陷阱

- **不要用 go_back()**：SPA 页面 go_back 会 30s 超时，用 `page.goto(url)` 直接导航
- **首页绕过不是 100% 可靠**：如果失效，需要用户手动过验证码
- **macOS headed 窗口不可见**：patchright 的 Chromium 窗口可能不自动置前，需要 osascript 激活
- **execute_code 没有 patchright**：必须写脚本文件再用 `terminal()` 运行
- **glm 纯文本模型不能用 vision**：vision_analyze/browser_vision 被 block，用 OCR 替代
- **screencapture Retina 截图 OCR 空**：只信任 page.screenshot() 的输出
- **Chrome Apple Events JS 需手动开启**：菜单「显示→开发者→允许 Apple 事件中的 JavaScript」

## 验证步骤

1. 脚本运行后检查 `/tmp/job_results.json` 是否有内容
2. 确认 jobs 数组非空且包含 name、jd 字段
3. JD 长度 > 100 chars 视为有效
