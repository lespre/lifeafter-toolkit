import { chromium } from 'file:///C:/Users/Administrator/AppData/Local/hermes/hermes-agent/node_modules/playwright/index.mjs';
const b = await chromium.launch({ executablePath: 'C:/Users/Administrator/AppData/Local/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-win64/chrome-headless-shell.exe' });
const p = await b.newPage({ viewport: { width: 1500, height: 1200 } });
const errs = []; p.on('pageerror', e => errs.push(e.message));
async function shot(q, file){
  await p.goto('http://127.0.0.1:8792/board.html?b=fashion_wardrobe', { waitUntil:'networkidle' });
  await p.waitForTimeout(1500);
  await p.fill('#q', q); await p.waitForTimeout(1500);
  await p.locator('.fcard').first().click(); await p.waitForTimeout(1800);
  await p.screenshot({ path: file });
  await p.keyboard.press('Escape'); await p.waitForTimeout(500);
}
await shot('白月魁', '90_临时/shot_baiyuekui.png');
await shot('云烟成羽', '90_临时/shot_bud.png');
await shot('尼罗河传说-衣服', '90_临时/shot_flower.png');
console.log('errors', errs); await b.close();
