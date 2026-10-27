#!/usr/bin/env bash
# Run Jest mini program specs with execution ledger and batch report.
# Config: <skills-root>/miniprogram-run/miniprogram-run.config
# Usage (from mini program automation repo root):
#   <skills-root>/miniprogram-run/run-with-reports.sh single [--screenshot] <spec.js>
#   <skills-root>/miniprogram-run/run-with-reports.sh suite [--file miniprogram/suite.json] [--from TC-xxx|spec.js]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

find_repo_root() {
  local dir="$SCRIPT_DIR"
  while [[ "$dir" != "/" ]]; do
    if [[ -f "$dir/miniprogram/suite.json" ]]; then
      echo "$dir"
      return 0
    fi
    dir="$(dirname "$dir")"
  done
  echo "Error: cannot find miniprogram/suite.json above $SCRIPT_DIR" >&2
  return 1
}

REPO_ROOT="$(find_repo_root)"
cd "$REPO_ROOT"

CONFIG_FILE="$SCRIPT_DIR/miniprogram-run.config"
CONFIG_SCREENSHOT_DEFAULT=false
CONFIG_TRACE_DEFAULT=true
CONFIG_OPEN_HTML_DEFAULT=true
CONFIG_STOP_ON_FAIL_DEFAULT=false

load_run_config() {
  if [[ ! -f "$CONFIG_FILE" ]]; then
    return 0
  fi
  # shellcheck disable=SC1090
  source "$CONFIG_FILE"
  case "${RECORD_SCREENSHOT:-false}" in
    true|TRUE|1|yes|YES)
      CONFIG_SCREENSHOT_DEFAULT=true
      ;;
    *)
      CONFIG_SCREENSHOT_DEFAULT=false
      ;;
  esac
  case "${RECORD_TRACE:-true}" in
    true|TRUE|1|yes|YES)
      CONFIG_TRACE_DEFAULT=true
      ;;
    *)
      CONFIG_TRACE_DEFAULT=false
      ;;
  esac
  case "${OPEN_HTML:-true}" in
    true|TRUE|1|yes|YES)
      CONFIG_OPEN_HTML_DEFAULT=true
      ;;
    *)
      CONFIG_OPEN_HTML_DEFAULT=false
      ;;
  esac
  case "${STOP_ON_FAIL:-false}" in
    true|TRUE|1|yes|YES)
      CONFIG_STOP_ON_FAIL_DEFAULT=true
      ;;
    *)
      CONFIG_STOP_ON_FAIL_DEFAULT=false
      ;;
  esac
}

# 用系统默认浏览器打开 batch HTML 报告（失败不改变脚本 exit code）
open_html_report() {
  local html_path="$1"
  if [[ "$CONFIG_OPEN_HTML_DEFAULT" != "true" ]]; then
    return 0
  fi
  if [[ -z "$html_path" || ! -f "$html_path" ]]; then
    echo "Warning: HTML report not found, skip open: ${html_path:-<empty>}" >&2
    return 0
  fi
  case "$(uname -s)" in
    Darwin)
      if open "$html_path" 2>/dev/null; then
        echo "Opened HTML report: $(relative_path "$html_path")"
      else
        echo "Warning: failed to open HTML report: $html_path" >&2
      fi
      ;;
    *)
      if command -v xdg-open >/dev/null 2>&1; then
        if xdg-open "$html_path" >/dev/null 2>&1; then
          echo "Opened HTML report: $(relative_path "$html_path")"
        else
          echo "Warning: failed to open HTML report: $html_path" >&2
        fi
      else
        echo "Warning: no open/xdg-open available for HTML report: $html_path" >&2
      fi
      ;;
  esac
}

load_run_config

SESSION_ID=""
SESSION_HEADER_WRITTEN=false
EXECUTIONS_MD="$REPO_ROOT/reports/miniprogram-executions.md"

init_session() {
  if [[ -z "$SESSION_ID" ]]; then
    SESSION_ID="$(date '+%Y%m%d-%H%M%S')"
  fi
  mkdir -p "$REPO_ROOT/reports/artifacts/$SESSION_ID"
  mkdir -p "$(dirname "$EXECUTIONS_MD")"
  touch "$EXECUTIONS_MD"
}

ensure_session_header() {
  if [[ "$SESSION_HEADER_WRITTEN" == "false" ]]; then
    {
      echo ""
      echo "## Session $SESSION_ID"
      echo ""
    } >> "$EXECUTIONS_MD"
    SESSION_HEADER_WRITTEN=true
  fi
}

relative_path() {
  local abs="$1"
  if [[ "$abs" == "$REPO_ROOT/"* ]]; then
    echo "${abs#$REPO_ROOT/}"
  elif [[ "$abs" == "$REPO_ROOT" ]]; then
    echo "."
  else
    echo "$abs"
  fi
}

parse_case_key() {
  local spec_path="$1"
  local base
  base="$(basename "$spec_path" .spec.js)"
  base="${base%.js}"
  if [[ "$base" =~ (TC-[A-Z]+-[0-9]+) ]]; then
    echo "${BASH_REMATCH[1]}"
  else
    echo "$base"
  fi
}

resolve_spec_path() {
  local spec="$1"
  if [[ -f "$spec" ]]; then
    echo "$(cd "$(dirname "$spec")" && pwd)/$(basename "$spec")"
    return 0
  fi
  if [[ -f "$REPO_ROOT/$spec" ]]; then
    echo "$(cd "$(dirname "$REPO_ROOT/$spec")" && pwd)/$(basename "$spec")"
    return 0
  fi
  if [[ -f "$REPO_ROOT/miniprogram/$spec" ]]; then
    echo "$(cd "$(dirname "$REPO_ROOT/miniprogram/$spec")" && pwd)/$(basename "$spec")"
    return 0
  fi
  return 1
}

read_suite_specs() {
  local suite_abs="$1"
  SUITE_SPECS=()
  SUITE_CASE_IDS=()
  if ! command -v node >/dev/null 2>&1; then
    echo "Error: node is required to parse suite.json" >&2
    return 1
  fi
  local json_out
  # 每行：id<TAB>file（id 可空，兼容旧布局）
  json_out="$(node -e "
    const fs = require('fs');
    const p = process.argv[1];
    const suite = JSON.parse(fs.readFileSync(p, 'utf8'));
    const cases = (suite.cases || []).slice().sort((a, b) => (a.order || 0) - (b.order || 0));
    for (const c of cases) {
      if (!c.file) continue;
      const rel = c.file.startsWith('miniprogram/') ? c.file : 'miniprogram/' + c.file;
      const id = (c.id || '').trim();
      console.log(id + '\t' + rel);
    }
  " "$suite_abs")"
  while IFS= read -r line || [[ -n "$line" ]]; do
    [[ -z "$line" ]] && continue
    local case_id="${line%%$'\t'*}"
    local spec_rel="${line#*$'\t'}"
    SUITE_CASE_IDS+=("$case_id")
    SUITE_SPECS+=("$spec_rel")
  done <<< "$json_out"
}

flow_matches_from_marker() {
  local spec_abs="$1"
  local marker="$2"
  local case_id="${3:-}"
  local base tc order_num
  base="$(basename "$spec_abs")"
  tc="$(parse_case_key "$spec_abs")"

  [[ -n "$case_id" && "$marker" == "$case_id" ]] && return 0
  [[ "$marker" == "$base" ]] && return 0
  [[ "$marker" == "$tc" ]] && return 0
  [[ "$base" == "$marker"* ]] && return 0
  if [[ "$base" =~ ^([0-9]+)_ ]]; then
    order_num="${BASH_REMATCH[1]}"
    [[ "$marker" == "${order_num}_"* || "$marker" == "$order_num" ]] && return 0
  fi
  return 1
}

run_jest_spec() {
  local spec_abs="$1"
  local out_dir="$2"
  local case_key="${3:-}"
  local name_pattern="${4:-}"
  local log_file="$out_dir/console.log"
  local json_file="$out_dir/jest-results.json"
  mkdir -p "$out_dir"
  local exit_code=0
  local shot_flag=false
  local trace_flag=false
  [[ "$CONFIG_SCREENSHOT_DEFAULT" == "true" ]] && shot_flag=true
  [[ "$CONFIG_TRACE_DEFAULT" == "true" ]] && trace_flag=true
  if [[ -z "$case_key" ]]; then
    case_key="$(parse_case_key "$spec_abs")"
  fi
  local jest_args=("$spec_abs" --runInBand --testTimeout=60000 --json --outputFile="$json_file")
  if [[ -n "$name_pattern" ]]; then
    jest_args+=(--testNamePattern="$name_pattern")
  fi
  ARTIFACT_DIR="$out_dir" \
  RECORD_SCREENSHOT="$shot_flag" \
  RECORD_TRACE="$trace_flag" \
  CASE_KEY="$case_key" \
  npx jest "${jest_args[@]}" \
    2>&1 | tee "$log_file" || exit_code=$?
  return "$exit_code"
}

append_execution() {
  local case_key="$1"
  local status="$2"
  local exit_code="$3"
  local spec_rel="$4"
  local out_rel="$5"
  local json_rel="$6"

  ensure_session_header
  local line="- **${case_key}** | ${status} | exit=${exit_code} | spec=\`${spec_rel}\` | artifacts=\`${out_rel}\`"
  if [[ -f "$REPO_ROOT/$json_rel" ]]; then
    line="${line} | json=\`${json_rel}\`"
  fi
  echo "$line" >> "$EXECUTIONS_MD"
}

BATCH_SPECS=()
BATCH_STATUSES=()
BATCH_CASE_KEYS=()
SUITE_SPECS=()
SUITE_CASE_IDS=()

generate_batch_report() {
  local source_label="$1"
  local pass_count="$2"
  local fail_count="$3"
  local parse_note="${4:-}"
  local not_run_count="${5:-0}"
  local total="${#BATCH_SPECS[@]}"

  local report_file="$REPO_ROOT/reports/miniprogram-report-${SESSION_ID}.md"
  local timestamp
  timestamp="$(date '+%Y-%m-%d %H:%M:%S')"

  {
    echo "# 小程序自动化测试报告"
    echo ""
    echo "## 执行顺序"
    local i=0
    for spec in "${BATCH_SPECS[@]}"; do
      i=$((i + 1))
      echo "${i}. \`${spec}\` — ${BATCH_STATUSES[$((i - 1))]}"
    done
    echo ""
    echo "## 运行汇总"
    echo "- 总数：${total}"
    echo "- 通过：${pass_count}"
    echo "- 失败：${fail_count}"
    if [[ "$not_run_count" -gt 0 ]]; then
      echo "- 未执行：${not_run_count}"
    fi
    echo ""
    echo "## 失败用例"
    i=0
    local has_fail=false
    for spec in "${BATCH_SPECS[@]}"; do
      if [[ "${BATCH_STATUSES[$i]}" == "FAIL" ]]; then
        has_fail=true
        local ck="${BATCH_CASE_KEYS[$i]}"
        echo "- \`${spec}\`：见 \`reports/artifacts/${SESSION_ID}/${ck}/jest-results.json\`、\`console.log\`、\`trace/viewer.html\`"
      fi
      i=$((i + 1))
    done
    if [[ "$has_fail" == "false" ]]; then
      echo "- （无）"
    fi
    echo ""
    echo "## 环境"
    echo "- 时间：${timestamp}"
    echo "- Session：${SESSION_ID}"
    echo "- 顺序来源：${source_label}"
    echo ""
    echo "## 备注"
    echo "- 逐条摘要见 \`reports/miniprogram-executions.md\` Session ${SESSION_ID}"
    echo "- 产物根目录：\`reports/artifacts/${SESSION_ID}/\`"
    if [[ -n "$parse_note" ]]; then
      echo "- ${parse_note}"
    fi
  } > "$report_file"

  echo "Batch report: $(relative_path "$report_file")"

  # HTML 报告（无 Playwright video/trace；可链到 artifacts / 截图）
  local html_file="$REPO_ROOT/reports/miniprogram-report-${SESSION_ID}.html"
  {
    echo "<!DOCTYPE html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\"/>"
    echo "<title>小程序自动化报告 ${SESSION_ID}</title>"
    echo "<style>"
    echo "body{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;margin:24px;background:#f6f8fa;color:#24292f}"
    echo "h1{font-size:1.4rem}table{border-collapse:collapse;width:100%;background:#fff;border-radius:8px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.08)}"
    echo "th,td{border-bottom:1px solid #eaecef;padding:10px 12px;text-align:left;font-size:14px}"
    echo "th{background:#f0f3f6}.pass{color:#1a7f37;font-weight:600}.fail{color:#cf222e;font-weight:600}.skip{color:#6e7781}"
    echo "a{color:#0969da;text-decoration:none}a:hover{text-decoration:underline}.meta{color:#57606a;margin:12px 0 20px}"
    echo "</style></head><body>"
    echo "<h1>小程序自动化测试报告</h1>"
    echo "<p class=\"meta\">Session <code>${SESSION_ID}</code> · ${timestamp} · 通过 ${pass_count} / 失败 ${fail_count} / 未执行 ${not_run_count} · 共 ${total}</p>"
    echo "<table><thead><tr><th>#</th><th>用例</th><th>状态</th><th>产物</th><th>Trace</th></tr></thead><tbody>"
    i=0
    for spec in "${BATCH_SPECS[@]}"; do
      i=$((i + 1))
      local st="${BATCH_STATUSES[$((i - 1))]}"
      local ck="${BATCH_CASE_KEYS[$((i - 1))]}"
      local cls="skip"
      [[ "$st" == "PASS" ]] && cls="pass"
      [[ "$st" == "FAIL" ]] && cls="fail"
      local art="artifacts/${SESSION_ID}/${ck}/"
      local trace_link="—"
      if [[ -f "$REPO_ROOT/reports/artifacts/${SESSION_ID}/${ck}/trace/viewer.html" ]]; then
        trace_link="<a href=\"artifacts/${SESSION_ID}/${ck}/trace/viewer.html\">viewer</a>"
      fi
      echo "<tr><td>${i}</td><td><code>${spec}</code></td><td class=\"${cls}\">${st}</td><td><a href=\"${art}\">${art}</a></td><td>${trace_link}</td></tr>"
    done
    echo "</tbody></table>"
    echo "<p class=\"meta\">说明：伪 Trace 为步骤时间线（meta/wxml/截图），非 Playwright video/trace.zip。RECORD_TRACE 控制是否录制。</p>"
    echo "</body></html>"
  } > "$html_file"

  echo "HTML report: $(relative_path "$html_file")"
  open_html_report "$html_file"
}

run_one_spec() {
  local spec_abs="$1"
  local case_key="${2:-}"
  local name_pattern="${3:-}"
  local out_dir exit_code=0 status spec_rel out_rel json_rel=""

  if [[ -z "$case_key" ]]; then
    case_key="$(parse_case_key "$spec_abs")"
  fi
  out_dir="$REPO_ROOT/reports/artifacts/$SESSION_ID/$case_key"

  run_jest_spec "$spec_abs" "$out_dir" "$case_key" "$name_pattern" || exit_code=$?

  status="PASS"
  [[ "$exit_code" -ne 0 ]] && status="FAIL"

  spec_rel="$(relative_path "$spec_abs")"
  out_rel="$(relative_path "$out_dir")"
  json_rel="${out_rel}/jest-results.json"

  append_execution "$case_key" "$status" "$exit_code" "$spec_rel" "$out_rel" "$json_rel"

  RUN_ONE_STATUS="$status"
  RUN_ONE_CASE_KEY="$case_key"
  return "$exit_code"
}

cmd_single() {
  local spec=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --screenshot|--no-screenshot)
        shift
        ;;
      -*)
        echo "Unknown option: $1" >&2
        exit 1
        ;;
      *)
        if [[ -n "$spec" ]]; then
          echo "Unexpected extra argument: $1" >&2
          exit 1
        fi
        spec="$1"
        shift
        ;;
    esac
  done

  if [[ -z "$spec" ]]; then
    echo "Usage: $0 single <spec.js>" >&2
    exit 1
  fi

  init_session

  local spec_abs
  if ! spec_abs="$(resolve_spec_path "$spec")"; then
    echo "Spec not found: $spec" >&2
    exit 1
  fi

  local exit_code=0
  run_one_spec "$spec_abs" || exit_code=$?

  BATCH_SPECS=("$(relative_path "$spec_abs")")
  BATCH_STATUSES=("$RUN_ONE_STATUS")
  BATCH_CASE_KEYS=("$RUN_ONE_CASE_KEY")
  local pass_count=0
  local fail_count=0
  if [[ "$RUN_ONE_STATUS" == "PASS" ]]; then
    pass_count=1
  else
    fail_count=1
  fi
  generate_batch_report "single" "$pass_count" "$fail_count" "" 0

  return "$exit_code"
}

cmd_suite() {
  local suite_file="$REPO_ROOT/miniprogram/suite.json"
  local from_marker=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --file)
        suite_file="$2"
        shift 2
        ;;
      --from)
        from_marker="$2"
        shift 2
        ;;
      --screenshot|--no-screenshot)
        shift
        ;;
      *)
        echo "Unknown option: $1" >&2
        exit 1
        ;;
    esac
  done

  if [[ ! -f "$suite_file" ]]; then
    echo "Suite file not found: $suite_file" >&2
    exit 1
  fi

  init_session

  local suite_abs
  suite_abs="$(cd "$(dirname "$suite_file")" && pwd)/$(basename "$suite_file")"

  read_suite_specs "$suite_abs"

  BATCH_SPECS=()
  BATCH_STATUSES=()
  BATCH_CASE_KEYS=()
  local pass_count=0
  local fail_count=0
  local not_run_count=0
  local parse_note=""
  local overall_exit=0
  local start_reached=false
  local stopped=false

  [[ -z "$from_marker" ]] && start_reached=true

  local i child_spec child_id child_abs child_key name_pattern spec_rel child_exit
  for i in "${!SUITE_SPECS[@]}"; do
    child_spec="${SUITE_SPECS[$i]}"
    child_id="${SUITE_CASE_IDS[$i]:-}"
    if ! child_abs="$(resolve_spec_path "$child_spec")"; then
      echo "Warning: spec not found: $child_spec" >&2
      continue
    fi
    if [[ -n "$child_id" ]]; then
      child_key="$child_id"
      name_pattern="$child_id"
    else
      child_key="$(parse_case_key "$child_abs")"
      name_pattern=""
    fi
    spec_rel="$(relative_path "$child_abs")"

    if [[ "$stopped" == "true" ]]; then
      BATCH_SPECS+=("$spec_rel")
      BATCH_STATUSES+=("NOT_RUN")
      BATCH_CASE_KEYS+=("$child_key")
      not_run_count=$((not_run_count + 1))
      continue
    fi

    if [[ "$start_reached" == "false" ]]; then
      if flow_matches_from_marker "$child_abs" "$from_marker" "$child_id"; then
        start_reached=true
      else
        BATCH_SPECS+=("$spec_rel")
        BATCH_STATUSES+=("NOT_RUN")
        BATCH_CASE_KEYS+=("$child_key")
        not_run_count=$((not_run_count + 1))
        continue
      fi
    fi

    echo ""
    echo ">>> [$((pass_count + fail_count + 1))/${#SUITE_SPECS[@]}] ${child_key} $spec_rel"
    child_exit=0
    run_one_spec "$child_abs" "$child_key" "$name_pattern" || child_exit=$?

    BATCH_SPECS+=("$spec_rel")
    BATCH_STATUSES+=("$RUN_ONE_STATUS")
    BATCH_CASE_KEYS+=("$child_key")

    if [[ "$RUN_ONE_STATUS" == "PASS" ]]; then
      pass_count=$((pass_count + 1))
    else
      fail_count=$((fail_count + 1))
      overall_exit=1
      if [[ "$CONFIG_STOP_ON_FAIL_DEFAULT" == "true" ]]; then
        stopped=true
      fi
    fi
  done

  if [[ -n "$from_marker" && "$start_reached" == "false" ]]; then
    echo "Error: --from marker not found in suite: $from_marker" >&2
    exit 1
  fi

  if [[ "$not_run_count" -gt 0 ]]; then
    if [[ -n "$from_marker" ]]; then
      parse_note="${not_run_count} 条未执行（--from ${from_marker} 之前跳过）。"
    elif [[ "$CONFIG_STOP_ON_FAIL_DEFAULT" == "true" ]]; then
      parse_note="${not_run_count} 条未执行（STOP_ON_FAIL=true，前序失败后停止；可用 suite --from 续跑）。"
    else
      parse_note="${not_run_count} 条未执行。"
    fi
  fi

  generate_batch_report "$(relative_path "$suite_file")" "$pass_count" "$fail_count" "$parse_note" "$not_run_count"
  return "$overall_exit"
}

usage() {
  cat <<EOF
Usage:
  $0 single <spec.js>              # 跑模块文件全部 describe（模块级调试）
  $0 suite [--file miniprogram/suite.json] [--from TC-xxx|spec.js]

Batch regression: each suite case runs jest on cases[].file with --testNamePattern=cases[].id
(so one-module-one-file layouts only execute that TC's describe). CASE_KEY uses cases[].id.
Legacy one-file-per-TC (filename contains TC-id, no pattern needed) still works.
Default: continue after failure (STOP_ON_FAIL=false); all results stay in one Session.
Set STOP_ON_FAIL=true to stop on first failure; use --from to resume.

Config file: $(relative_path "$CONFIG_FILE")

Run from repository root. Writes:
  reports/miniprogram-executions.md
  reports/artifacts/<sessionId>/<caseKey>/jest-results.json
  reports/artifacts/<sessionId>/<caseKey>/console.log
  reports/miniprogram-report-<sessionId>.md
  reports/miniprogram-report-<sessionId>.html  (OPEN_HTML=true 时自动打开)
EOF
}

main() {
  if [[ $# -lt 1 ]]; then
    usage >&2
    exit 1
  fi

  local cmd="$1"
  shift

  case "$cmd" in
    single)
      cmd_single "$@"
      ;;
    suite|suite-json)
      cmd_suite "$@"
      ;;
    -h|--help|help)
      usage
      ;;
    *)
      echo "Unknown command: $cmd" >&2
      usage >&2
      exit 1
      ;;
  esac
}

main "$@"
