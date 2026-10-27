const fs = require('fs');
const path = require('path');

/**
 * 尽力截图。须调用 miniProgram.screenshot（Page 无此 API）。
 * 仅开发者工具模拟器可用；失败返回 null，不抛错。
 *
 * @param {object} miniProgram
 * @param {string} filePath 绝对路径
 */
async function tryScreenshot(miniProgram, filePath) {
  if (!miniProgram || typeof miniProgram.screenshot !== 'function' || !filePath) {
    return null;
  }
  try {
    fs.mkdirSync(path.dirname(filePath), { recursive: true });
    await miniProgram.screenshot({ path: filePath });
    if (fs.existsSync(filePath)) return filePath;
    return null;
  } catch (err) {
    if (process.env.DEBUG_SCREENSHOT === 'true') {
      console.warn('[screenshot]', err && (err.message || err));
    }
    return null;
  }
}

/**
 * 收尾截图（RECORD_SCREENSHOT=true 且设置 ARTIFACT_DIR 时）。
 */
async function captureScreenshotIfEnabled(miniProgram, filename = 'screenshot.png') {
  if (String(process.env.RECORD_SCREENSHOT || '').toLowerCase() !== 'true') {
    return null;
  }
  const dir = process.env.ARTIFACT_DIR;
  if (!miniProgram || !dir) return null;
  fs.mkdirSync(dir, { recursive: true });
  const out = path.join(dir, filename);
  return tryScreenshot(miniProgram, out);
}

module.exports = { tryScreenshot, captureScreenshotIfEnabled };
