# Skill 交付清单（PACKAGING）

## 必须交付（三目录）

- `miniprogram-script-author/SKILL.md`
- `miniprogram-run/`（`SKILL.md`、`run-with-reports.sh`、`miniprogram-run.config`）
- `miniprogram-shared/`（`README.md`、`PACKAGING.md`、`conventions.md`、`selectors.md`、`scaffold.sh`、`miniprogram.local.config.example`、`templates/**`）

## 禁止随 Skill 分发

- `miniprogram.local.config`（本机路径）
- 业务 `miniprogram/tests/**/*.spec.js`、`inspect/`、`probes/`、`reports/`
- 用例 Excel / 业务账号明文
- `wechatide-skill`（非本三件套依赖）

## 用户仓库（脚手架 + 生成物）

由 `scaffold.sh` 创建空壳；spec / suite / inspect / reports 由 Agent 与执行产生。
