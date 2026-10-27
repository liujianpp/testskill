# testflow 全景流程图

## 端到端流程（7 阶段）

| 阶段 | 入口技能 | 产物 | 触发条件 |
|------|---------|------|---------|
| 0 预热（可选） | api-doc-generator | 接口文档（目标项目 docs/） | 只有源码、没需求文档时 |
| 1 需求评审 | prd-review | 5 维评审报告 MD → 附入 proposal.md | 默认链路起点 |
| 2 用例设计 | spectest-new / -analysis / -plan(可选) / -points / -generate / -review / -fix | test-plan.md(可选) + design.md + artifacts/<name>_testcases.xlsx（25列）+ testcases.json | 阶段 1 完成后 |
| 3A 接口支线 | api-doc-generator → api-scenario-generator → api-test-generator → api-test-runner | docs/ 下 scenario/cases + Allure | **用户显式要求**或有源码且确认 |
| 3B UI 支线 | testflow 转换器 + browser-use-case-runner | artifacts/ui_cases.xlsx + MD 报告 + 截图 | 默认支线 |
| 3C 小程序支线 | testflow 转换器 + miniprogram-script-author → miniprogram-run | artifacts/mp_cases.xlsx + Jest spec + suite.json + Session 报告 | 用户显式声明被测端含微信小程序 |
| 4 统一报告 | testflow 汇总器 | artifacts/unified-report.md | 任一执行支线完成后 |
| 5 归档 | spectest-archive（可选 operation-manual） | 归档目录 / 操作手册 | 用户确认后 |

**边界说明**：prd-review 输出需求视角评审（可测性/阻塞点/风险提示）；spectest-plan 输出测试管理视角计划（范围/人天/进度/进出标准）——二者互补，test-plan 将评审报告的阻塞点吸收为「风险与应对」输入，不重复评审内容。

## 状态目录与产物

```
spectest/changes/<name>/
├── proposal.md                  # 阶段1 评审报告附于其后或被引用
├── test-plan.md                 # 测试计划（可选，spectest-plan 产物）
├── design.md                    # 用例设计方案（spectest-generate from-specs 产物）
├── project_info/                # spectest-analysis 产物
├── specs/                       # 测试点
├── artifacts/
│   ├── requirements-extracted.md # 需求文档抽取正文（可选，spectest-analysis 产物）
│   ├── <name>_testcases.xlsx    # 25列用例（三支线源头）
│   ├── ui_cases.xlsx            # 3B 入口产物（testflow 转换器输出）
│   ├── mp_cases.xlsx            # 3C 入口产物（同一转换器，仅换输出名）
│   ├── api/                     # 3A 记录（allure-results 路径等）
│   ├── mp/                      # 3C 记录（Session 报告/台账路径，如 report_path.txt）
│   └── unified-report.md        # 统一报告（testflow 汇总器输出）
└── db_info/                     # DB 断言信息（api-test-generator 用）
```

## 格式契约

- **25 列表头**：系统/项目, 模块, 功能, 测试项/测试点, 用例标题, 前置条件, 涉及相关数据库表, 测试数据准备, 测试步骤, 预期结果, 验证SQL, 实际结果, 是否通过, 预估工时, 执行时间, 测试进度, 用例类型, 用例优先级, 是否回归用例, 是否阻塞上线, 关联需求ID, API URL, BUG数, BUG未解决数, 用例版本
- **runner 8 列表头**：用例编号, 用例名称, 功能模块, 优先级, 前置条件, 测试步骤, 测试数据, 预期结果
- **3C 入口格式**：`mp_cases.xlsx` 与 `ui_cases.xlsx` 同为 runner 8 列（同一转换器输出）；miniprogram 的 `parse-testcases.js` 表头兼容——用例编号→id、用例名称→title、前置条件→precondition、测试步骤→steps、测试数据→data、预期结果→expected（功能模块/优先级被忽略）
- **列映射**（转换器 HEADER_MAP）：用例编号←测试项/测试点，用例名称←用例标题，功能模块←模块，优先级←用例优先级，前置条件←前置条件，测试步骤←测试步骤，测试数据←测试数据准备，预期结果←预期结果
- **API 用例判定**：25 列中「API URL」非空
- **统计口径**：通过率 = 通过/(通过+失败)，阻塞单列不进分母

## 双链路独立性

- **需求驱动链路**（prd-review → spectest）：源头是需求文档
- **代码驱动链路**（api-doc-generator → … → api-test-runner）：源头是后端源码
- 两链路互不转换、各自独立，**仅在阶段 4 统一报告处汇合**（不做用例级关联）
- 3B 与 3C 同属需求驱动链路：共用 25 列分流（「API URL」非空 → 3A），各自转换为 `ui_cases.xlsx` / `mp_cases.xlsx` 分别执行，互不转换
