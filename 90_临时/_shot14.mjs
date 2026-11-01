import { chromium } from 'file:///C:/Users/Administrator/AppData/Local/hermes/hermes-agent/node_modules/playwright/index.mjs';
const b = await chromium.launch({ executablePath: 'C:/Users/Administrator/AppData/Local/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-win64/chrome-headless-shell.exe' });
const p = await b.newPage({ viewport: { width: 1500, height: 1100 } });
const errs=[]; p.on('pageerror',e=>errs.push(e.message));
async function shot(q, want, file){
  await p.goto('http://127.0.0.1:8765/board.html?b=fashion_wardrobe', { waitUntil:'networkidle' });
  await p.waitForTimeout(1400);
  await p.fill('#q', q); await p.waitForTimeout(1500);
  const c = p.locator('.fcard').filter({ hasText: want }).first();
  await c.click(); await p.waitForTimeout(1700);
  await p.screenshot({ path: file });
}
await shot('一串小饼干','一串小饼干','90_临时/shot_g1.png');
await shot('无暇的祝福','无暇的祝福','90_临时/shot_g2.png');
await shot('星河流淌','星河流淌','90_临时/shot_g3.png');
console.log('errors', errs); await b.close();
