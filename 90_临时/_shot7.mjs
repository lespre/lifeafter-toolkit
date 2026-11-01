import { chromium } from 'file:///C:/Users/Administrator/AppData/Local/hermes/hermes-agent/node_modules/playwright/index.mjs';
const b = await chromium.launch({ executablePath: 'C:/Users/Administrator/AppData/Local/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-win64/chrome-headless-shell.exe' });
const p = await b.newPage({ viewport: { width: 1500, height: 1000 } });
const errs=[]; p.on('pageerror',e=>errs.push(e.message));
async function shot(q, want, file){
  await p.goto('http://127.0.0.1:8793/board.html?b=fashion_wardrobe', { waitUntil:'networkidle' });
  await p.waitForTimeout(1400);
  await p.fill('#q', q); await p.waitForTimeout(1400);
  const c = p.locator('.fcard').filter({ hasText: want }).first();
  await c.click(); await p.waitForTimeout(1600);
  await p.screenshot({ path: file });
  const tags = await p.locator('.fcard').first().locator('.fr-alt').allTextContents();
  return tags;
}
console.log('白月魁 tags', await shot('白月魁','白月魁-衣服','90_临时/shot_f1.png'));
console.log('尼罗河 tags', await shot('尼罗河传说','衣服','90_临时/shot_f2.png'));
console.log('errors', errs); await b.close();
