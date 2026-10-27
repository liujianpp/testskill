#!/usr/bin/env node
/**
 * Parse test cases from Excel or Markdown into structured JSON.
 *
 * Usage:
 *   node scripts/parse-testcases.js --input cases.xlsx --out cases.json
 *   node scripts/parse-testcases.js --input cases.md --out cases.json
 *
 * Excel expected columns (header row, flexible aliases):
 *   顺序/order, 用例ID/id/TC, 标题/title/名称, 前置/precondition,
 *   步骤/steps, 预期/expected, 数据/data
 *
 * Markdown: table with same columns, or ## TC-XXX sections with bullet steps.
 */

const fs = require('fs');
const path = require('path');

function parseArgs(argv) {
  const args = { input: '', out: '' };
  for (let i = 2; i < argv.length; i += 1) {
    const key = argv[i];
    if (key === '--input') {
      args.input = argv[++i];
    } else if (key === '--out') {
      args.out = argv[++i];
    }
  }
  return args;
}

function normalizeHeader(h) {
  const s = String(h || '')
    .trim()
    .toLowerCase()
    .replace(/\s+/g, '');
  const map = {
    顺序: 'order',
    order: 'order',
    序号: 'order',
    用例id: 'id',
    id: 'id',
    tc: 'id',
    用例编号: 'id',
    标题: 'title',
    title: 'title',
    名称: 'title',
    用例名称: 'title',
    用例标题: 'title',
    前置: 'precondition',
    precondition: 'precondition',
    前置条件: 'precondition',
    步骤: 'steps',
    steps: 'steps',
    操作步骤: 'steps',
    测试步骤: 'steps',
    预期: 'expected',
    expected: 'expected',
    预期结果: 'expected',
    数据: 'data',
    data: 'data',
    测试数据: 'data',
  };
  return map[s] || s;
}

function parseExcel(filePath) {
  const XLSX = require('xlsx');
  const wb = XLSX.readFile(filePath);
  const sheet = wb.Sheets[wb.SheetNames[0]];
  const rows = XLSX.utils.sheet_to_json(sheet, { header: 1, defval: '' });
  if (rows.length < 2) return [];

  const headers = rows[0].map(normalizeHeader);
  const cases = [];

  for (let r = 1; r < rows.length; r += 1) {
    const row = rows[r];
    if (!row || row.every((c) => !String(c).trim())) continue;
    const item = {};
    headers.forEach((key, i) => {
      if (!key) return;
      item[key] = row[i] != null ? String(row[i]).trim() : '';
    });
    if (!item.id && !item.title) continue;
    if (item.order) item.order = Number(item.order) || item.order;
    if (item.steps && typeof item.steps === 'string') {
      item.steps = item.steps.split(/\n|；|;/).map((s) => s.trim()).filter(Boolean);
    }
    cases.push(item);
  }
  return cases;
}

function parseMarkdownTable(lines) {
  const cases = [];
  let headers = [];
  let inTable = false;

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed.startsWith('|')) {
      inTable = false;
      continue;
    }
    const cells = trimmed
      .split('|')
      .slice(1, -1)
      .map((c) => c.trim());
    if (cells.every((c) => /^[-:]+$/.test(c))) {
      inTable = true;
      continue;
    }
    if (!headers.length) {
      headers = cells.map(normalizeHeader);
      continue;
    }
    if (!inTable && headers.length) inTable = true;
    const item = {};
    headers.forEach((key, i) => {
      if (!key) return;
      item[key] = cells[i] || '';
    });
    if (!item.id && !item.title) continue;
    if (item.order) item.order = Number(item.order) || item.order;
    if (item.steps && typeof item.steps === 'string') {
      item.steps = item.steps.split(/\n|；|;/).map((s) => s.trim()).filter(Boolean);
    }
    cases.push(item);
  }
  return cases;
}

function parseMarkdownSections(content) {
  const cases = [];
  const sections = content.split(/^##\s+/m).slice(1);

  for (const block of sections) {
    const lines = block.split('\n');
    const titleLine = lines[0].trim();
    const idMatch = titleLine.match(/(TC-[A-Z]+-\d+)/i);
    const id = idMatch ? idMatch[1].toUpperCase() : titleLine.split(/\s+/)[0];
    const title = titleLine.replace(/^(TC-[A-Z]+-\d+)\s*[-–—]?\s*/i, '').trim() || titleLine;

    const item = { id, title, steps: [], expected: '', precondition: '' };
    let section = '';

    for (let i = 1; i < lines.length; i += 1) {
      const line = lines[i].trim();
      if (/^###?\s*前置/.test(line)) {
        section = 'precondition';
        continue;
      }
      if (/^###?\s*步骤/.test(line)) {
        section = 'steps';
        continue;
      }
      if (/^###?\s*预期/.test(line)) {
        section = 'expected';
        continue;
      }
      if (/^#/.test(line)) {
        section = '';
        continue;
      }
      if (!line) continue;

      if (section === 'precondition') {
        item.precondition += (item.precondition ? '\n' : '') + line.replace(/^[-*]\s*/, '');
      } else if (section === 'steps') {
        item.steps.push(line.replace(/^[-*\d.]+\s*/, ''));
      } else if (section === 'expected') {
        item.expected += (item.expected ? '\n' : '') + line.replace(/^[-*]\s*/, '');
      }
    }
    cases.push(item);
  }
  return cases;
}

function parseMarkdown(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  const tableCases = parseMarkdownTable(content.split('\n'));
  if (tableCases.length) return tableCases;
  return parseMarkdownSections(content);
}

function main() {
  const args = parseArgs(process.argv);
  if (!args.input) {
    console.error('Usage: node scripts/parse-testcases.js --input <file> --out <cases.json>');
    process.exit(1);
  }

  const inputPath = path.isAbsolute(args.input)
    ? args.input
    : path.join(process.cwd(), args.input);

  if (!fs.existsSync(inputPath)) {
    console.error(`Input not found: ${inputPath}`);
    process.exit(1);
  }

  const ext = path.extname(inputPath).toLowerCase();
  let cases = [];

  if (ext === '.xlsx' || ext === '.xls') {
    cases = parseExcel(inputPath);
  } else if (ext === '.md' || ext === '.txt') {
    cases = parseMarkdown(inputPath);
  } else {
    console.error(`Unsupported format: ${ext}. Use .xlsx, .md, or .txt`);
    process.exit(1);
  }

  cases = cases
    .map((c, i) => ({
      order: c.order != null && c.order !== '' ? Number(c.order) || c.order : i + 1,
      id: c.id || `TC-UNK-${String(i + 1).padStart(3, '0')}`,
      title: c.title || c.id,
      precondition: c.precondition || '',
      steps: Array.isArray(c.steps) ? c.steps : c.steps ? [c.steps] : [],
      expected: c.expected || '',
      data: c.data || '',
    }))
    .sort((a, b) => (Number(a.order) || 0) - (Number(b.order) || 0));

  const out = {
    source: path.basename(inputPath),
    parsedAt: new Date().toISOString(),
    cases,
  };

  if (args.out) {
    const outPath = path.isAbsolute(args.out) ? args.out : path.join(process.cwd(), args.out);
    fs.mkdirSync(path.dirname(outPath), { recursive: true });
    fs.writeFileSync(outPath, JSON.stringify(out, null, 2), 'utf8');
    console.log(`Parsed ${cases.length} case(s) -> ${outPath}`);
  } else {
    console.log(JSON.stringify(out, null, 2));
  }
}

main();
