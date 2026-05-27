"""
招聘网站岗位搜索与 JD 抓取 — 通用模板
用法: python3 job-search-scraper.py
修改下方 CONFIG 部分的参数即可
"""
from patchright.sync_api import sync_playwright
import subprocess, time, json, os, sys

# ==================== CONFIG ====================
SITE = "boss"           # boss | lagou | liepin
KEYWORD = "AI Agent"    # 搜索关键词
CITY = "100010000"      # 100010000=全国, 101010100=北京, 101020100=上海
MAX_JOBS = 15           # 最大抓取职位数
MAX_JD = 10             # 最大获取 JD 数
OUTPUT = "/tmp/job_results.json"
# =================================================

# 网站 URL 配置
SITE_CONFIG = {
    "boss": {
        "home": "https://www.zhipin.com/",
        "search": "https://www.zhipin.com/web/geek/job?query={keyword}&city={city}",
        "card_sel": ".job-card-wrapper, .job-card-box",
        "name_sel": ".job-name",
        "salary_sel": ".salary",
        "company_sel": ".company-name, .company-text a",
        "info_sel": ".tag-list",
        "link_sel": "a[href*='/job_detail/']",
        "jd_sel": ".job-sec-text, .job-detail-section, [class*='describe']",
    },
    # 其他网站可按需扩展
}

def ocr(img):
    """Swift Vision OCR"""
    if not os.path.exists('/tmp/ocr'):
        subprocess.run(['swiftc', os.path.expanduser('~/.hermes/skills/macos-gui-automation/scripts/ocr.swift'),
             '-o', '/tmp/ocr', '-framework', 'Vision', '-framework', 'AppKit', '-framework', 'CoreImage'],
            capture_output=True)
    r = subprocess.run(['/tmp/ocr', img], capture_output=True, text=True, timeout=10)
    return r.stdout.strip()

def main():
    config = SITE_CONFIG.get(SITE)
    if not config:
        print(f"❌ 不支持网站: {SITE}")
        sys.exit(1)
    
    search_url = config["search"].format(keyword=KEYWORD.replace(" ", "%20"), city=CITY)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
            locale="zh-CN",
        )
        page = context.new_page()
        
        # === Step 1: 先访问首页建立 session（关键反爬绕过步骤）===
        print(f"[1/4] 访问 {SITE} 首页建立 session...")
        page.goto(config["home"], wait_until="domcontentloaded")
        time.sleep(5)
        
        title = page.title()
        print(f"  首页 Title: {title}")
        
        # 如果首页就触发验证码
        if any(w in title for w in ["安全验证", "验证", "captcha", "verify"]):
            print("  ⚠️ 首页触发验证码！请手动操作浏览器窗口完成验证")
            print("  ⏳ 等待验证通过（最长5分钟）...")
            for i in range(100):
                if not any(w in page.title() for w in ["安全验证", "验证", "captcha", "verify"]):
                    print(f"  ✅ 验证通过！(等待 {i*3}s)")
                    break
                time.sleep(3)
            else:
                print("  ❌ 验证超时")
                browser.close()
                sys.exit(1)
        
        # === Step 2: 搜索 ===
        print(f"\n[2/4] 搜索 '{KEYWORD}'...")
        page.goto(search_url, wait_until="domcontentloaded")
        time.sleep(5)
        
        title = page.title()
        print(f"  搜索页 Title: {title}")
        
        # 再次检查验证码
        if any(w in title for w in ["安全验证", "验证"]):
            print("  ⚠️ 搜索页触发验证码，等待手动处理...")
            for i in range(100):
                if not any(w in page.title() for w in ["安全验证", "验证"]):
                    break
                time.sleep(3)
            time.sleep(3)
        
        # === Step 3: 提取职位列表 ===
        print(f"\n[3/4] 提取职位列表...")
        
        extract_js = f"""(() => {{
            let jobs = [];
            let items = document.querySelectorAll('{config["card_sel"]}');
            
            items.forEach(item => {{
                let j = {{}};
                let n = item.querySelector('{config["name_sel"]}');
                if (n) j.name = n.innerText.trim();
                let s = item.querySelector('{config["salary_sel"]}');
                if (s) j.salary = s.innerText.trim();
                let c = item.querySelector('{config["company_sel"]}');
                if (c) j.company = c.innerText.trim();
                let info = item.querySelector('{config["info_sel"]}');
                if (info) j.info = info.innerText.trim();
                let a = item.querySelector('{config["link_sel"]}');
                if (a) {{
                    let h = a.getAttribute('href');
                    j.link = h.startsWith('http') ? h : 'https://www.zhipin.com' + h;
                }}
                if (j.name) jobs.push(j);
            }});
            
            return JSON.stringify({{count: items.length, jobs: jobs}});
        }})()"""
        
        try:
            result = page.evaluate(extract_js)
            data = json.loads(result)
            jobs = data.get('jobs', [])[:MAX_JOBS]
            print(f"  找到 {data.get('count', 0)} 个职位，取前 {len(jobs)} 个")
        except Exception as e:
            print(f"  JS 提取失败: {e}")
            # OCR 备选
            page.screenshot(path="/tmp/job_search_debug.png")
            ocr_text = ocr("/tmp/job_search_debug.png")
            print(f"  OCR: {ocr_text[:300]}")
            jobs = []
        
        for i, j in enumerate(jobs):
            print(f"  {i+1}. {j.get('name','?')} | {j.get('salary','?')} | {j.get('company','?')}")
        
        if not jobs:
            print("  ❌ 没找到职位")
            with open("/tmp/job_search_debug.html", "w") as f:
                f.write(page.content())
            browser.close()
            sys.exit(1)
        
        # === Step 4: 获取 JD 详情 ===
        print(f"\n[4/4] 获取 JD 详情 (最多 {MAX_JD} 个)...")
        all_jds = []
        
        for i, job in enumerate(jobs[:MAX_JD]):
            link = job.get('link')
            if not link:
                continue
            
            print(f"\n  [{i+1}] {job['name']} @ {job.get('company','?')}")
            try:
                page.goto(link, wait_until="domcontentloaded", timeout=15000)
                time.sleep(3)
                
                if any(w in page.url for w in ["verify", "安全验证"]):
                    print("    ⚠️ 验证拦截，跳过")
                    page.goto(search_url, wait_until="domcontentloaded", timeout=15000)
                    time.sleep(2)
                    continue
                
                jd = page.evaluate(f"""(() => {{
                    let text = '';
                    let sels = '{config["jd_sel"]}'.split(', ');
                    for (let s of sels) {{
                        let el = document.querySelector(s);
                        if (el && el.innerText.trim().length > 30) {{ 
                            text = el.innerText.trim(); break; 
                        }}
                    }}
                    if (!text || text.length < 50) {{
                        let all = document.querySelectorAll('div, section, p');
                        for (let el of all) {{
                            let t = el.innerText.trim();
                            if ((t.includes('岗位职责') || t.includes('任职要求') || t.includes('职位描述')) 
                                && t.length > 100 && t.length < 5000) {{
                                text = t; break;
                            }}
                        }}
                    }}
                    return text;
                }})()""")
                
                if jd and len(jd) > 30:
                    job['jd'] = jd
                    print(f"    ✅ JD ({len(jd)} chars)")
                    all_jds.append(job)
                else:
                    page.screenshot(path=f"/tmp/job_jd_{i}.png")
                    jd_ocr = ocr(f"/tmp/job_jd_{i}.png")
                    if len(jd_ocr) > 50:
                        job['jd'] = jd_ocr
                        print(f"    ✅ JD via OCR ({len(jd_ocr)} chars)")
                        all_jds.append(job)
                    else:
                        print(f"    ⚠️ 内容不足")
                
            except Exception as e:
                print(f"    ❌ {e}")
            
            # 直接导航回搜索页（不用 go_back）
            try:
                page.goto(search_url, wait_until="domcontentloaded", timeout=15000)
                time.sleep(2)
            except:
                pass
        
        # === 保存结果 ===
        with open(OUTPUT, "w") as f:
            json.dump(all_jds, f, ensure_ascii=False, indent=2)
        
        print(f"\n{'='*50}")
        print(f"✅ 完成！保存了 {len(all_jds)} 个 JD 到 {OUTPUT}")
        print(f"{'='*50}")
        
        for j in all_jds:
            print(f"\n{'─'*40}")
            print(f"📌 {j.get('name','')}")
            print(f"💰 {j.get('salary','')}")
            print(f"🏢 {j.get('company','')}")
            print(f"📍 {j.get('info','')}")
            jd = j.get('jd', '')
            if jd:
                print(f"📝 {jd[:300]}...")
        
        browser.close()

if __name__ == "__main__":
    main()
