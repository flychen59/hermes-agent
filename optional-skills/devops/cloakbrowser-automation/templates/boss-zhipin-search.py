"""
BOSS直聘岗位搜索 + JD 抓取模板
用法：修改 QUERY 和 CITY 参数即可
依赖：patchright (pip3 install patchright)，/tmp/ocr (Swift Vision)
"""
from patchright.sync_api import sync_playwright
import subprocess, time, json, os

# ========== 配置 ==========
QUERY = "AI Agent"  # 搜索关键词
CITY = "100010000"  # 城市代码（全国=100010000，北京=101010100，上海=101020100）
MAX_JOBS = 15       # 最大抓取数
HEADLESS = False    # True=无窗口，False=有窗口（BOSS直聘必须 False）

SEARCH_URL = f"https://www.zhipin.com/web/geek/job?query={QUERY.replace(' ', '%20')}&city={CITY}"

# ========== 工具函数 ==========
def ocr(img):
    """用 Swift Vision OCR 识别截图文字"""
    if not os.path.exists('/tmp/ocr'):
        subprocess.run(['swiftc', os.path.expanduser('~/.hermes/skills/macos-gui-automation/scripts/ocr.swift'),
             '-o', '/tmp/ocr', '-framework', 'Vision', '-framework', 'AppKit', '-framework', 'CoreImage'],
            capture_output=True)
    r = subprocess.run(['/tmp/ocr', img], capture_output=True, text=True, timeout=10)
    return r.stdout.strip()

EXTRACT_JOBS_JS = """(() => {
    let jobs = [];
    let items = document.querySelectorAll('.job-card-wrapper, .job-card-box');
    if (items.length === 0) items = document.querySelectorAll('[ka="search-job-item"]');
    if (items.length === 0) items = document.querySelectorAll('.job-list-box li');
    
    items.forEach(item => {
        let j = {};
        let n = item.querySelector('.job-name, .job-title, [class*="job-name"]');
        if (n) j.name = n.innerText.trim();
        let s = item.querySelector('.salary, [class*="salary"]');
        if (s) j.salary = s.innerText.trim();
        let c = item.querySelector('.company-name, [class*="company-name"], .company-text a');
        if (c) j.company = c.innerText.trim();
        let info = item.querySelector('.tag-list, [class*="tag-list"], .info-desc, .job-info');
        if (info) j.info = info.innerText.trim();
        let a = item.querySelector('a[href*="/job_detail/"]');
        if (!a) a = item.closest('a[href*="/job_detail/"]');
        if (a) {
            let h = a.getAttribute('href');
            j.link = h.startsWith('http') ? h : 'https://www.zhipin.com' + h;
        }
        if (j.name) jobs.push(j);
    });
    return JSON.stringify({count: items.length, jobs: jobs});
})()"""

EXTRACT_JD_JS = """(() => {
    let text = '';
    let sels = ['.job-sec-text', '.job-detail-section', '[class*="describe"]', '.detail-content'];
    for (let s of sels) {
        let el = document.querySelector(s);
        if (el && el.innerText.trim().length > 30) { text = el.innerText.trim(); break; }
    }
    if (!text || text.length < 50) {
        let allEls = document.querySelectorAll('div, section');
        for (let el of allEls) {
            let t = el.innerText.trim();
            if ((t.includes('岗位职责') || t.includes('任职要求')) && t.length > 100 && t.length < 3000) {
                text = t; break;
            }
        }
    }
    return text;
})()"""

# ========== 主逻辑 ==========
with sync_playwright() as p:
    browser = p.chromium.launch(headless=HEADLESS)
    context = browser.new_context(
        viewport={"width": 1280, "height": 800},
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
        locale="zh-CN",
    )
    page = context.new_page()
    
    # Step 1: 先访问首页（关键！绕过验证码）
    print(f"搜索: {QUERY} (city={CITY})")
    page.goto("https://www.zhipin.com/", wait_until="domcontentloaded")
    time.sleep(5)
    
    # Step 2: 搜索
    page.goto(SEARCH_URL, wait_until="domcontentloaded")
    time.sleep(5)
    
    # 检查是否被验证拦截
    if "安全验证" in page.title() or "verify" in page.url:
        print("⚠️ 触发验证码，需要手动处理或换 IP")
        page.screenshot(path="/tmp/boss_blocked.png")
        browser.close()
        exit(1)
    
    # Step 3: 提取职位列表
    result = page.evaluate(EXTRACT_JOBS_JS)
    data = json.loads(result)
    jobs = data.get('jobs', [])
    print(f"找到 {len(jobs)} 个职位")
    
    for i, j in enumerate(jobs[:MAX_JOBS]):
        print(f"  {i+1}. {j.get('name','?')} | {j.get('salary','?')} | {j.get('company','?')}")
    
    if not jobs:
        print("❌ 未找到职位")
        browser.close()
        exit(1)
    
    # Step 4: 获取 JD
    all_jds = []
    for i, job in enumerate(jobs[:MAX_JOBS]):
        link = job.get('link')
        if not link:
            continue
        print(f"[{i+1}] {job['name']} @ {job.get('company','?')}")
        try:
            page.goto(link, wait_until="domcontentloaded", timeout=15000)
            time.sleep(3)
            
            if "verify" in page.url or "安全验证" in page.title():
                print("  ⚠️ 验证拦截")
                page.goto(SEARCH_URL, wait_until="domcontentloaded", timeout=15000)
                time.sleep(2)
                continue
            
            jd = page.evaluate(EXTRACT_JD_JS)
            if jd and len(jd) > 30:
                job['jd'] = jd
                print(f"  ✅ ({len(jd)} chars)")
                all_jds.append(job)
            else:
                # OCR 备选
                page.screenshot(path=f"/tmp/bv_jd_{i}.png")
                ocr_text = ocr(f"/tmp/bv_jd_{i}.png")
                if len(ocr_text) > 50:
                    job['jd'] = ocr_text
                    all_jds.append(job)
        except Exception as e:
            print(f"  ❌ {e}")
        
        # 用直接导航返回（不要用 go_back）
        page.goto(SEARCH_URL, wait_until="domcontentloaded", timeout=15000)
        time.sleep(2)
    
    # 保存
    output_path = f"/tmp/boss_{QUERY.replace(' ', '_')}_jds.json"
    with open(output_path, "w") as f:
        json.dump(all_jds, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 保存了 {len(all_jds)} 个 JD 到 {output_path}")
    
    browser.close()
