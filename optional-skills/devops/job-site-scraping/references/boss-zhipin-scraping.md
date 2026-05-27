# BOSS 直聘爬取踩坑记录（2026-05-27 实测）

## 背景

搜索 AI Agent 岗位 + 抓取 JD，从 BOSS直聘（zhipin.com）获取数据。

## 反爬等级：极高 ⚠️

BOSS直聘的反爬是国内招聘网站中最严格的之一：

| 方案 | 结果 | 原因 |
|------|------|------|
| Hermes 内置浏览器 | ❌ 安全验证 | IP 标记 |
| curl 直接请求 API | ❌ code:35 IP异常 | IP 标记 |
| Google/Bing/DuckDuckGo/360/Brave 搜索 | ❌ 全部触发验证码 | 搜索引擎也被反爬 |
| 系统 Chrome（含隐身模式） | ❌ 安全验证 | IP 级封锁 |
| patchright headless=True | ❌ 安全验证 | 被检测 |
| **patchright headless=False 直接搜** | ❌ 安全验证 | 直接访问搜索 URL 触发 |
| **patchright headless=False 先访问首页** | ✅ 成功！ | 先建立 session 再搜索 |

## 成功方案详解

### 核心技巧：先访问首页建立 session

```python
from patchright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(
        viewport={"width": 1280, "height": 800},
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
        locale="zh-CN",
    )
    page = context.new_page()
    
    # 关键：先访问首页！
    page.goto("https://www.zhipin.com/")
    time.sleep(5)  # 等 cookie 建立
    
    # 然后再搜索
    page.goto("https://www.zhipin.com/web/geek/job?query=AI%20Agent&city=100010000")
    time.sleep(5)
    
    # 此时页面正常加载，无验证码！
```

### 为什么有效？

BOSS直聘在首页设置了一组 cookie（包含 `__zp_stoken__` 等加密 token），后续页面检查这些 cookie。直接访问深层 URL 时没有这些 cookie，立即触发 IP 封锁验证。

## 验证码类型

如果首页绕过失效，会遇到的验证码：

### 第一层：点击按钮验证
- OCR: "点击按钮进行验证"
- 点击后进入图片选择验证

### 第二层：图片点选验证（9宫格）
- OCR: "请选中下图中所有的：XX"（XX = 红绿灯/斑马线/自行车等）
- **无法自动识别**，必须人工操作
- 需要 patchright headless=False 弹出浏览器 + 用户手动点击

## CSS 选择器（2026-05 验证）

```css
/* 搜索结果列表 */
.job-card-wrapper    /* 职位卡片（部分页面） */
.job-card-box        /* 职位卡片（全国招聘页） */

/* 卡片内元素 */
.job-name            /* 职位名称 */
.salary              /* 薪资 */
.company-name        /* 公司名 */
.company-text a      /* 公司名（备选） */
.tag-list            /* 标签（经验/学历） */
a[href*="/job_detail/"]  /* 详情页链接 */

/* 详情页 */
.job-sec-text        /* JD 正文 */
.job-detail-section  /* JD 正文（备选） */
```

## 经验筛选（重要陷阱）

**URL 参数方式会失败**：
```
# ❌ 不要这样用——会触发登录弹窗
https://www.zhipin.com/web/geek/job?query=AI+Agent&city=100010000&experience=104
```

**正确方式——JS 点击页面筛选标签**：
```python
clicked = page.evaluate("""(() => {
    let links = document.querySelectorAll('a, li, span, div');
    for (let el of links) {
        let text = el.innerText.trim();
        if (text === '1-3年' || text === '1-3 年') {
            el.click();
            return 'clicked: ' + text;
        }
    }
    return 'not found';
})()""")
```

经验筛选标签文本对照：
- `经验不限`
- `1年以内`
- `1-3年`
- `3-5年`
- `5-10年`
- `10年以上`

## JD 截断处理

未登录状态下 JD 末尾有"登录查看完整内容"文字：
```python
# 在 JS 提取时清理
text = text.replace(/登录查看完整内容.*/g, '').trim()
```

截断后的内容无法恢复，只能获取可见部分。完整 JD 需要登录状态。

## 注意事项

1. **page.go_back() 会超时**：BOSS直聘是 SPA，go_back 触发 30s timeout。用 `page.goto(search_url)` 代替
2. **搜索页 title 可能是"全国招聘"**：BOSS直聘有时跳转到全国招聘聚合页，但内容仍是搜索结果
3. **JD 有截断**：未登录状态下 JD 末尾显示"登录查看完整内容"
4. **每页约 15-30 个职位**：可滚动加载或翻页
5. **首页绕过不是 100% 可靠**：如果当天请求过多，首页也会触发验证码

## 备选方案（首页绕过失效时）

```python
# 弹出浏览器 + 等待用户手动过验证码
page.goto("https://www.zhipin.com/")
if "安全验证" in page.title():
    print("请手动完成验证码")
    for i in range(100):  # 最多等 5 分钟
        if "安全验证" not in page.title():
            break
        time.sleep(3)
```

## 城市代码参考

```
100010000 = 全国
101010100 = 北京
101020100 = 上海
101280100 = 广州
101280600 = 深圳
101210100 = 杭州
101110100 = 成都
101060100 = 合肥
```

## macOS 特殊问题

| 问题 | 原因 | 解决 |
|------|------|------|
| patchright 窗口不可见 | macOS 上 Chromium 窗口不自动置前 | osascript 激活 process "Chromium" |
| screencapture OCR 空 | Retina 2x 分辨率（2940x1912） | 用 page.screenshot() 代替 |
| System Events 报 0 窗口 | patchright 窗口对 osascript 不可见 | 用 page.mouse.click 代替 cliclick |
