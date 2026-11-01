import { chromium } from 'file:///C:/Users/Administrator/AppData/Local/hermes/hermes-agent/node_modules/playwright/index.mjs';
const b = await chromium.launch({ executablePath: 'C:/Users/Administrator/AppData/Local/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-win64/chrome-headless-shell.exe' });
const p = await b.newPage({ viewport: { width: 1500, height: 1000 } });
const errs=[]; p.on('pageerror',e=>errs.push(e.message));
async function shot(q, want, file){
  await p.goto('http://127.0.0.1:8792/board.html?b=fashion_wardrobe', { waitUntil:'networkidle' });
  await p.waitForTimeout(1200);
  await p.fill('#q', q); await p.waitForTimeout(1200);
  const c = p.locator('.fcard').filter({ hasText: want }).first();
  await c.click(); await p.waitForTimeout(1600);
  await p.screenshot({ path: file });
}
await shot('白月魁', '白月魁-衣服', '90_临时/shot_bud2.png');
await shot('尼罗河传说', '衣服', '90_临时/shot_flower2.png');
console.log('tags', await p.locator('.fr-bud').count(), await p.locator('.fr-flower').count());
console.log('errors', errs); await b.close();
