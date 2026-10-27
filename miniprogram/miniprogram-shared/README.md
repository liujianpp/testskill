# 小程序 UI 自动化 Skill 包（三件套）

只交付本目录上级的三个 skill：`miniprogram-script-author`、`miniprogram-run`、`miniprogram-shared`。

## 安装

1. 将三个目录放到用户 Cursor skills 路径（如 `.cursor/skills/`）。
2. 在用户**自动化仓库根**执行脚手架：

```bash
bash <skills-root>/miniprogram-shared/scaffold.sh .
```

3. 编辑 `miniprogram.local.config`（从 example 复制，**勿提交 Git**）。
4. 安装依赖：见 [templates/package.deps.md](templates/package.deps.md)。
5. 设置 `MP_ACCOUNT` / `MP_PASSWORD`（及可选 `MP_ID_CARD`）。

## 交付内容

| 目录/文件 | 交付？ |
|-----------|--------|
| 各 `SKILL.md`、`conventions.md`、`selectors.md` | 是 |
| `miniprogram-run/run-with-reports.sh`、`miniprogram-run.config` | 是 |
| `miniprogram-shared/templates/**`、`scaffold.sh` | 是 |
| `miniprogram.local.config.example` | 是 |
| `miniprogram.local.config`（含本机路径） | **否** |
| 业务 `tests/*.spec.js`、inspect、reports、用例 Excel | **否**（用户仓生成） |

## 工作流

1. `@miniprogram-script-author` — 探索 + 写 spec + 维护 suite  
2. `@miniprogram-run` — 执行 + artifacts / 伪 Trace / Session 报告  

不依赖 `wechatide-skill`；需自行开启开发者工具服务端口并 `cli auto`（或配置 `wsEndpoint`）。
