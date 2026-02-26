# CAPTCHA自动解决方案

## 方案1: 2Captcha（推荐）
- 价格: $2.99/1000次
- 支持: reCAPTCHA v2/v3, hCAPTCHA, Cloudflare等
- API: 简单易用

## 方案2: Anti-Captcha
- 价格: 类似
- 支持: 多种CAPTCHA类型

## 方案3: Buster插件（免费）
- 浏览器插件
- 自动点击"我不是机器人"
- 成功率较低

## 实施步骤

1. 注册2Captcha账号并充值
2. 获取API Key
3. 集成到Playwright脚本
4. 遇到CAPTCHA时调用API
5. 等待人工解决并获取token

## 代码示例

```javascript
const solver = require('2captcha');

// 初始化
const captcha = new solver.Solver('YOUR_API_KEY');

// 遇到CAPTCHA时
const result = await captcha.recaptcha({
  pageurl: 'https://github.com/signup',
  sitekey: '6Lc...' // 从页面获取
});

// 填入结果
document.getElementById('g-recaptcha-response').value = result.data;
```

## 需要用户提供
- 2Captcha API Key（需要注册并充值）
- 或 Anti-Captcha API Key

## 成本估算
- GitHub注册: 约 $0.003（一次）
- 充值最低: $5-10
