# 用户自动化仓库依赖（在仓库根执行）

```bash
npm install --save-dev jest@^29.7.0 miniprogram-automator@^0.12.1 xlsx@^0.18.5
```

| 包 | 用途 |
|----|------|
| `jest` | 跑 spec |
| `miniprogram-automator` | 连接微信开发者工具模拟器 |
| `xlsx` | `parse-testcases.js` 解析 Excel |

`package.json` scripts 建议：

```json
{
  "scripts": {
    "test": "jest --runInBand",
    "capture": "node scripts/capture-wxml.js",
    "parse-cases": "node scripts/parse-testcases.js",
    "scaffold": "bash <skills-root>/miniprogram-shared/scaffold.sh"
  }
}
```
