# Task 1 Report: 转换器 convert_25col_to_ui_xlsx.py

- 状态: **DONE_WITH_CONCERNS**（功能完成、8/8 测试通过、冒烟通过；但存在 4 处对简报逐字代码的最小偏差修复，见「自审发现」）
- 日期: 2026-08-24
- 环境: win32 / Git Bash / Python 3.14.3 / pytest 9.1.1 / openpyxl（已安装）

## 产物

| 文件 | 状态 |
|------|------|
| `e:/AI/skills/testflow/scripts/convert_25col_to_ui_xlsx.py` | 已创建（简报代码 + 2 处 bug 修复） |
| `e:/AI/skills/testflow/scripts/tests/test_convert_25col_to_ui_xlsx.py` | 已创建（简报代码 + 2 处断言修复） |

未修改简报范围外的任何文件。非 git 仓库，无 commit 步骤。

## 各步骤执行结果

### Step 1: 依赖检查 — PASS
`python -c "import openpyxl, pytest; print('ok')"` → 输出 `ok`，无需安装。

### Step 2: 写失败单测 — DONE
按简报逐字创建测试文件（当时 8 个测试与简报完全一致）。

### Step 3: 确认失败（TDD 红灯）— PASS，符合 Expected
```
ImportError while importing test module ... test_convert_25col_to_ui_xlsx.py
E   ModuleNotFoundError: No module named 'convert_25col_to_ui_xlsx'
1 error in 0.80s
```
与简报 Expected（FAIL + ModuleNotFoundError）逐字吻合。

### Step 4: 写实现 — DONE（含 2 处必要修复）
先逐字写入简报实现，首跑 **3 failed / 5 passed**，TDD 暴露出 1 个实现 bug 与 2 个测试断言缺陷（详见自审），随后做最小修复。

### Step 5: 确认通过（TDD 绿灯）— PASS，符合 Expected
```
tests/test_convert_25col_to_ui_xlsx.py::test_standard_mapping PASSED
tests/test_convert_25col_to_ui_xlsx.py::test_api_url_rows_excluded PASSED
tests/test_convert_25col_to_ui_xlsx.py::test_fallback_id_generation PASSED
tests/test_convert_25col_to_ui_xlsx.py::test_dedup_keeps_first PASSED
tests/test_convert_25col_to_ui_xlsx.py::test_types_filter_on_coverage_dim PASSED
tests/test_convert_25col_to_ui_xlsx.py::test_missing_source_column_no_crash PASSED
tests/test_convert_25col_to_ui_xlsx.py::test_empty_rows_skipped PASSED
tests/test_convert_25col_to_ui_xlsx.py::test_wrong_sheet_errors PASSED
8 passed in 0.92s
```
**测试输出摘要: 8 passed / 0 failed**（修复前红绿轨迹: Step 3 1 error → 修复前实现 3 failed 5 passed → 最终 8 passed）

### Step 6: 真实产物冒烟 — PASS（含 1 个环境路径注意事项）
`e:/AI/skills/spectest/test_output.xlsx` 存在，执行转换：
```
总行数: 98 | 导出: 6 | 跳过: API用例 2, 类型不符 0, 重复编号 90, 空行 0
```
输出验证（UTF-8）：
```
sheet=UI用例
headers=['用例编号', '用例名称', '功能模块', '优先级', '前置条件', '测试步骤', '测试数据', '预期结果']
rows=6
```
8 个 runner 表头逐字正确。

注意事项（非代码缺陷）：简报原文命令中内嵌于 `python -c "..."` 字符串里的 `/tmp/ui_cases_smoke.xlsx` 不会被 Git Bash 转换为 Windows 路径，导致验证半程 FileNotFoundError；实际产物被写到 `C:/Users/admin/AppData/Local/Temp/ui_cases_smoke.xlsx`，用该路径完成验证。后续在 win32 下引用 /tmp 产物建议用 `$TMP` 或 `$(cygpath -w /tmp/...)`。

90 个重复编号已核实为源数据真实特征：该文件 98 行的「测试项/测试点」列仅 6 个不同值（如「营销平台 - 优惠券管理（投放功能）」出现 20 次，此列被用作功能分类标签而非唯一编号），转换器按规格「同编号只保留首行」正确工作。

## 自审发现（对照简报逐条检查）

### 简报内部矛盾：逐字代码无法达到 Step 5 的 Expected（8 passed）

逐字实现首跑 3 failed / 5 passed。根因均已用最小探针实验证实（`tuple` 返回类型 + openpyxl 空串不落盘读回 `None`）：

| # | 位置 | 类型 | 根因 | 最小修复 |
|---|------|------|------|----------|
| 1 | 实现 `convert()` 输出行 | **实现 bug** | 回退生成的 `case_id` 只用于去重，从未写入输出，输出「用例编号」仍是空的源值——与模块 docstring「为空时按模块-功能-行号生成」直接矛盾。`test_fallback_id_generation` 抓到 | 输出行改 3 行：`row_out = [src(c) ...]; row_out[0] = case_id; out_rows.append(row_out)` |
| 2 | 实现 `needed` 集合 | **实现 bug** | `needed = set(SOURCE_COLS) \| {"API URL", "用例类型"}` 缺「功能」列（映射表用的是「模块」，「功能」仅回退编号需要），`col_idx` 无此列 → `src('功能')` 恒空 → 回退编号成 `"登录--1"` | `needed` 集合补 `\"功能\"` 并加注释 |
| 3 | 测试 `test_standard_mapping` | 测试断言缺陷 | `iter_rows(values_only=True)` 返回 tuple，`tuple == list` 恒 False，该断言在任何正确实现下都不可能通过 | `assert headers ==` → `assert list(headers) ==`（链式比较与意图不变） |
| 4 | 测试 `test_missing_source_column_no_crash` | 测试断言缺陷 | openpyxl 不持久化空字符串，写入 `""` 读回 `None`，`== \"\"` 恒 False | `assert rows[0][6] == \"\"` → `in (\"\", None)` 并加注释 |

其中 #1、#2 是 TDD 抓到的简报实现真实 bug；#3、#4 是测试断言与 openpyxl 实际行为不符。四处的断言意图/功能语义均未改变。

### 逐条对照其余项 — 无偏差

- [x] 文件路径两个都与简报一致（scripts/ + scripts/tests/）
- [x] CLI 签名 `-i/-o/--sheet/--types` 未变（Task 3 依赖不受影响）
- [x] `convert(input_path, output_path, sheet_name=\"测试用例\", include_types=None) -> dict` 签名与 6 个统计键完全一致
- [x] `RUNNER_HEADERS` 常量存在且为 8 列表头
- [x] 25 列表头、Sheet 名、8 列输出表头逐字一致（冒烟已验证）
- [x] Python 命令用 `python`；win32 + bash；无 commit 步骤
- [x] 未派发子代理；未修改简报范围外文件（冒烟产物在系统临时目录）

### 遗留给协调者的判断

1. **简报的「逐字使用」约束与 Step 5 Expected（8 passed）在本机环境下互斥**。我选择了达成 Expected（绿灯优先），4 处偏差均为最小修复且已逐条记录。若后续 Task 的测试同样由计划文档逐字生成，需注意这两类 openpyxl 断言陷阱（tuple vs list、空串→None）。
2. 真实冒烟暴露的数据形态问题（非本任务缺陷）：存量 `test_output.xlsx` 的「测试项/测试点」列是分类标签而非唯一编号，98 行去重后仅剩 6 行。Task 3+ 若用此类文件做端到端演示，导出行数会远小于预期；更合适的是 spectest-generate 新产出的 25 列文件（其「测试项/测试点」为唯一编号）。
