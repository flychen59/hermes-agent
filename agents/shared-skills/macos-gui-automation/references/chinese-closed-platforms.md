# 中国封闭平台自动化经验（2026-05）

> 记录闲鱼、淘宝、微信等封闭生态平台的自动化尝试和结论。

## 闲鱼 (goofish.com)

### 三条路全部走不通

| 方案 | 问题 | 状态 |
|------|------|------|
| **闲鱼 iOS App** (Mac App Store) | iOS App 通过 Apple Silicon 兼容层运行，System Events 报 `count of windows = 0`，无法 GUI 操控 | ❌ 不可用 |
| **闲鱼网页版** (goofish.com) | 检测到非正常浏览器，返回 "非法访问 — 为了保障您的体验，请使用正常浏览器访问闲鱼~"，Cloudflare 拦截 | ❌ 不可用 |
| **闲鱼移动端 H5** (h5.m.goofish.com) | 跳转淘宝登录页，需要手机号+验证码或扫码登录 | ⚠️ 需要用户配合 |

### 搜索引擎也无法抓取

- Google: 502 被人机验证拦截
- Bing: Cloudflare 人机验证
- DuckDuckGo: 超时或空结果
- 闲鱼商品页基本不被搜索引擎收录（封闭生态）

### 唯一可行路径

1. **用户手机扫码登录** → 浏览器获得 session → 自动化操作
2. **scrcpy + Android 手机** → 投屏操控闲鱼 App
3. **用户手动操作** → 我们提供搜索关键词和比价信息

## 淘宝登录页

- URL: `https://login.taobao.com/havanaone/login/login.htm`
- 支持密码登录和短信登录
- 短信登录需要手机号 → 获取验证码 → 输入验证码
- 通过 `browser_console` 可以操作 DOM：`document.getElementById('fm-sms-login-id')` 等
- 协议 checkbox 必须先勾选

### DOM 元素 ID（截至 2026-05）

```javascript
// 短信登录模式
phoneInput: 'fm-sms-login-id'          // 手机号
smsCodeInput: 'fm-smscode'             // 验证码
checkCodeInput: 'fm-login-checkcode'   // 图片验证码
agreementCheckbox: 'fm-agreement-checkbox'

// 密码登录模式
accountInput: 'fm-sms-login-id'        // 账号名/邮箱/手机号
passwordInput: '请输入登录密码'          // placeholder
loginButton: 'btn-login' (或通过 button text "登录" 定位)
```

### 自动填值技巧

```javascript
// React/Vue controlled input 需要用 native setter
const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
  window.HTMLInputElement.prototype, 'value'
).set;
nativeInputValueSetter.call(inputElement, 'value_to_set');
inputElement.dispatchEvent(new Event('input', { bubbles: true }));
inputElement.dispatchEvent(new Event('change', { bubbles: true }));
```

## 搜索引擎反爬现状（2026-05）

| 引擎 | 拦截方式 | 绕过方案 |
|------|----------|----------|
| Google | Cloudflare 人机验证 (sorry/index) | 需代理 + residential IP |
| Bing | Cloudflare checkbox 验证 | 需要手动勾选 |
| DuckDuckGo | 超时/空结果 | HTML版有时可用 |
| SearXNG | 需要公开实例 | `searx.be` 等 |

### 可用的替代搜索方案

1. **GitHub 搜索** — `browser_navigate` 到 GitHub 仓库/搜索页，通常不被拦截
2. **浏览器 console JS** — 在已登录页面上用 `fetch()` 调内部 API
3. **curl + 代理** — `curl -x http://127.0.0.1:7897` 走 Clash 代理

## 结论

闲鱼是**完全封闭生态**，API 不公开、网页反爬、iOS App 0 窗口。要在闲鱼上做自动化操作（搜索、联系卖家、发消息），必须：
1. 用户配合登录（扫码或验证码）
2. 或者用物理设备操控（scrcpy/Android）
