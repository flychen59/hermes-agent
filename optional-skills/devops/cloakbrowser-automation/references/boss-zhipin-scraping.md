# BOSS直聘爬取方案

## 核心问题

BOSS直聘对自动化访问的封锁极其严格：
- 普通 Playwright：直接拦截
- patchright headless：直接拦截
- patchright headless=False + 直接访问搜索页：触发验证码
- 系统 Chrome（含隐身模式）：同样 IP 级别拦截
- curl API 调用：返回 code 35 "IP地址存在异常行为"
- 所有搜索引擎（Google/Bing/Brave/360）：都有各自的验证码拦截

## 最佳方案（2026-05-27 验证通过 ✅）

**patchright headless=False + 先访问首页 + 再搜索（无需手动过验证码）**

关键发现：直接访问搜索 URL 会触发验证码，但**先访问 `zhipin.com/` 首页建立 session 后再跳转搜索页可以绕过验证**。实际测试中首页直接打开无验证，搜索页也正常加载了 15 个职位。

**注意**：搜索页会跳转到 `/web/geek/jobs` (注意是 jobs 不是 job)，title 变成"全国招聘"页面。

```python
from patchright.sync_api import sync_playwright
import subprocess, time, json

SEARCH_URL = "https://www.zhipin.com/web/geek/job?query=AI%20Agent&city=100010000"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(
        viewport={"width": 1280, "height": 800},
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
        locale="zh-CN",
    )
    page = context.new_page()
    
    # 关键：先访问首页建立 session
    page.goto("https://www.zhipin.com/", wait_until="domcontentloaded")
    time.sleep(5)
    
    # 再搜索（可能自动跳转到 jobs 页面）
    page.goto(SEARCH_URL, wait_until="domcontentloaded")
    time.sleep(5)
    
    # 用 JS 提取（选择器见下方表格）
    # ...
    
    # 获取 JD 详情时，不要用 page.go_back()！会超时
    # 改用 page.goto(SEARCH_URL) 直接导航回去
    for job in jobs[:10]:
        page.goto(job['link'], wait_until="domcontentloaded", timeout=15000)
        time.sleep(3)
        jd = page.evaluate("""...""")
        page.goto(SEARCH_URL, wait_until="domcontentloaded", timeout=15000)  # 不要用 go_back
        time.sleep(2)
```

## 备选方案（需要手动过验证码）

如果首页方案失效，回退到手动过验证码：

```python
from patchright.sync_api import sync_playwright
import subprocess, time, json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, args=['--start-maximized'])
    context = browser.new_context(
        viewport={"width": 1280, "height": 800},
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
        locale="zh-CN",
    )
    page = context.new_page()
    page.goto("https://www.zhipin.com/web/geek/job?query=AI+Agent&city=100010000",
              wait_until="domcontentloaded")
    
    # 激活 Chromium 窗口到前台（关键！）
    subprocess.run(['osascript', '-e', 
        'tell application "System Events" to set frontmost of process "Chromium" to true'],
        capture_output=True)
    
    # 轮询等待用户手动过验证码
    for i in range(200):
        if "安全验证" not in page.title() and "verify" not in page.url:
            break
        time.sleep(3)
    
    # 用 JS 提取职位列表
    jobs = page.evaluate("""(() => {
        let jobs = [];
        document.querySelectorAll('.job-card-wrapper').forEach(item => {
            let j = {};
            let n = item.querySelector('.job-name');
            if (n) j.name = n.innerText.trim();
            let s = item.querySelector('.salary');
            if (s) j.salary = s.innerText.trim();
            let c = item.querySelector('.company-name');
            if (c) j.company = c.innerText.trim();
            let info = item.querySelector('.tag-list');
            if (info) j.info = info.innerText.trim();
            let a = item.querySelector('a[href*="/job_detail/"]');
            if (a) {
                let h = a.getAttribute('href');
                j.link = h.startsWith('http') ? h : 'https://www.zhipin.com' + h;
            }
            if (j.name) jobs.push(j);
        });
        return JSON.stringify(jobs);
    })()""")
    
    # 逐个获取 JD 详情
    for job in json.loads(jobs)[:10]:
        page.goto(job['link'], wait_until="domcontentloaded")
        time.sleep(3)
        jd = page.evaluate("""(() => {
            let el = document.querySelector('.job-sec-text, .job-detail-section');
            return el ? el.innerText.trim() : '';
        })()""")
        job['jd'] = jd
        page.go_back()
        time.sleep(2)
```

## 验证码类型

BOSS直聘的安全验证是**图片点选验证码**：
- 提示：「请选中下图中所有的：XX」
- 9张小图，需要点选指定类型
- 无法自动识别（需要 VLM + 图片理解能力）
- OCR 只能看到提示文字，看不到图片内容

## 陷阱：page.go_back() 在 BOSS 直聘会超时

用 `page.go_back()` 返回搜索页会触发 30s 超时。改用 `page.goto(SEARCH_URL)` 直接导航回去。

## 职位列表 CSS 选择器（2026-05-27 实测）

| 字段 | 选择器 | 备注 |
|------|--------|------|
| 职位卡片 | `.job-card-wrapper` 或 `.job-card-box` | `.job-card-box` 是实际生效的 class |
| 职位名称 | `.job-name` | ✅ 正常提取 |
| 薪资 | `.salary` 或 `[class*="salary"]` | ⚠️ 可能提取为空，需 OCR 补充 |
| 公司名称 | `.company-name` 或 `[class*="company-name"]` | ⚠️ 可能提取为空，需 OCR 补充 |
| 标签（地点/经验/学历）| `.tag-list` | ✅ |
| 详情链接 | `a[href*="/job_detail/"]` | ✅ 注意 href 可能是相对路径 |
| JD 正文 | `.job-sec-text` 或 `.job-detail-section` | ⚠️ 内容可能被截断（"登录查看完整内容"）|

**公司名和薪资可能为空**：DOM 结构里可能没有对应元素，或元素被懒加载。备选方案：用 `page.screenshot()` + `/tmp/ocr` 做 OCR 补充。

## city 参数

| 城市代码 | 城市 |
|----------|------|
| 100010000 | 全国 |
| 101010100 | 北京 |
| 101020100 | 上海 |
| 101280100 | 广州 |
| 101280600 | 深圳 |
| 101210100 | 杭州 |

## 截图方案对比

| 方案 | 可用性 | OCR 兼容 |
|------|--------|----------|
| `page.screenshot()` | ✅ | ✅ 1280x800 标准 |
| `screencapture -x` 全屏 | ✅ | ❌ Retina 2940x1912，sips 缩小后 OCR 仍空 |
| `screencapture -R x,y,w,h` | ❌ "could not create image from rect" | - |
| `screencapture -l windowID` | ❌ "could not create image from window" | - |

## URL 格式

搜索页：`https://www.zhipin.com/web/geek/job?query={keyword}&city={cityCode}`
职位详情：`https://www.zhipin.com/job_detail/{jobId}.html`
