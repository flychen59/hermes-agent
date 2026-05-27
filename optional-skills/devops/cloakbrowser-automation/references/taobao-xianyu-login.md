# 淘宝/闲鱼登录自动化 — 完整踩坑记录

> 合并自 taobao-login.md 和 taobao-xianyu-login.md（2026-05-26 实测）

## 核心发现：JS value 赋值不生效

淘宝登录页使用前端框架绑定 input，直接修改 `input.value` 或 `nativeInputValueSetter` 都**不会触发框架内部状态更新**。

```javascript
// ❌ 无效——框架状态不更新，提交报"请输入验证码"
element.value = '9939';
element.dispatchEvent(new Event('input', {bubbles: true}));

const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
setter.call(element, '9939');
element.dispatchEvent(new Event('input', {bubbles: true}));
```

**两种有效方案：**

### 方案 A：execCommand insertText（推荐，纯 JS）

```javascript
// 在已 focus 的 input 上用 execCommand
document.getElementById('fm-smscode').focus();
document.execCommand('insertText', false, '9939');
```

这会触发完整的 input 事件链，框架能识别到值变化。

### 方案 B：browser_type 键盘模拟

```
browser_console → document.getElementById('fm-smscode').focus()
browser_type → 验证码数字（需要正确的 ref，但短信模式下 accessibility tree 被国家代码列表淹没，ref 可能不可见）
```

⚠️ 方案 B 有风险：短信模式下 191 个国家代码 option 淹没 accessibility tree，验证码输入框的 ref 不可见，browser_type 可能打错元素。

## 淘宝短信登录完整流程（Hermes browser 版）

```
1. browser_navigate → https://login.taobao.com/havanaone/login/login.htm?bizName=taobao&redirectURL=https%3A%2F%2Fwww.goofish.com%2F
2. browser_click → 协议 checkbox (#fm-agreement-checkbox)
3. browser_click → 短信登录 link
4. browser_console(JS) → 填手机号: nativeInputValueSetter + dispatchEvent (手机号可以用 JS 填)
5. browser_console(JS) → document.querySelector('.send-btn-link').click()
6. 等用户回复验证码（按钮变为 "N秒后重发" = 发送成功）
7. browser_console(JS) → document.getElementById('fm-smscode').focus()
8. browser_console(JS) → document.execCommand('insertText', false, '验证码') ← 关键！
9. browser_console(JS) → document.querySelector('.fm-submit').click()
10. 检查 URL 是否跳转到 goofish.com
```

## 关键选择器

| 元素 | 选择器 | 备注 |
|------|--------|------|
| 协议 checkbox | `#fm-agreement-checkbox` | 必须先勾选 |
| 短信登录 tab | `a` 文本 "短信登录" | 切换模式 |
| 手机号输入框 | `#fm-sms-login-id` | JS 可填值 |
| 获取验证码按钮 | `a.send-btn-link` | **不是** `div.send-btn`（那是容器） |
| 验证码输入框 | `#fm-smscode` | **必须 execCommand 或 browser_type** |
| 登录按钮 | `button.fm-submit` | class 含 `sms-login` |
| 验证码发送状态 | `.send-btn` 文本 | "N秒后重发"=成功，"重新发送"=可重试 |

## 踩坑记录

### 1. 验证码 JS value 赋值 → 框架不识别
`smsInput.value = '9844'` + dispatchEvent，DOM 显示有值，但提交报"请输入短信验证码"或"验证码错误"（空值发到后端）。
**解决**：用 `document.execCommand('insertText', false, '验证码')` 在已 focus 的 input 上输入。

### 2. browser_type 打错元素
短信模式下 accessibility tree 被 191 个国家代码 option 淹没，`browser_type ref=e19` 实际打到了国家代码 combobox 而非验证码框。
**解决**：不用 browser_type，改用 `browser_console` + `execCommand`。

### 3. 多点"获取验证码"导致旧码失效
第一次发了 9844，后来又误点了一次"重新发送"，9844 立即失效。
**教训**：点获取验证码只能点一次，拿到码后立刻输入登录，不要重试发送。

### 4. 国家代码下拉框淹没 accessibility tree
snapshot 被国家代码列表占满（191个 option），看不到手机号/验证码输入框。
**解决**：`browser_press('Escape')` 关闭下拉，或直接用 `browser_console` 操作 DOM。

### 5. Hermes browser session 频繁断开
browser 页面多次变成 about:blank 或 empty page，可能是 session 超时或页面跳转导致。
**解决**：每次操作前检查 `location.href`，断开了就重新 navigate。

### 6. CloakBrowser headless=False macOS 0 窗口
patchright launch(headless=False) 进程启动了（"Google Chrome for Testing"），但 osascript 报 0 个窗口。page.screenshot() 只返回 ~98KB 空白。可能与后台进程无法创建 GUI 有关。
**替代方案**：用 Hermes 内置 browser 工具操作页面。

### 7. execute_code sandbox 缺 patchright
sandbox Python 环境没有 patchright，必须用 `terminal()` 运行脚本文件。

### 8. vision 工具依赖模型能力
glm-5.1 纯文本模型下 `vision_analyze` 和 `browser_vision` 都被拦截。需要 VLM 模型才能用视觉分析。

## 闲鱼（goofish.com）封闭生态

| 方案 | 结果 | 原因 |
|------|------|------|
| 闲鱼 iOS App (Mac) | ❌ 0 窗口 | iOS App 通过 Apple Silicon 兼容层运行，无法 GUI 操控 |
| 闲鱼网页版 goofish.com | ❌ "非法访问" | 检测到非正常浏览器 |
| 淘宝登录 → 跳转闲鱼 | 🔄 可行路径 | 淘宝登录页正常，登录后 cookie 跳转 |
| 搜索引擎搜闲鱼商品 | ❌ 抓不到 | 闲鱼封闭生态，搜索引擎不索引商品页 |

**结论**：闲鱼无法通过自动化搜索商品或联系卖家。唯一可行路径是淘宝登录后 cookie 跳转。

## Multi-Agent 限制（glm-5.1）

3 个并行 delegate_task 子 agent 全部超时（600s）或达到 max_iterations（40-48 API calls），未能返回有效结果。模型能力不足导致循环重复操作。
**建议**：简单搜索任务直接在主 agent 完成，不要 delegate 给弱模型子 agent。

## 推荐方案：Hermes browser + CloakBrowser 分工

| 场景 | 用什么 | 原因 |
|------|--------|------|
| 普通网页操作 | **Hermes browser** | accessibility tree 可用、ref 定位可靠 |
| 反爬检测网站 | **CloakBrowser/patchright** | navigator.webdriver: false |
| 点选验证码 | **需要 VLM** | vision 被模型限制 |
| 闲鱼 goofish.com | **都不行** | 网页版"非法访问"，iOS App 0 窗口 |
