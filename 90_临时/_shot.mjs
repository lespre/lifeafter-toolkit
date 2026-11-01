import { chromium } from 'file:///C:/Users/Administrator/AppData/Local/hermes/hermes-agent/node_modules/playwright/index.mjs';
const b = await chromium.launch({ executablePath: 'C:/Users/Administrator/AppData/Local/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-win64/chrome-headless-shell.exe' });
const p = await b.newPage({ viewport: { width: 1500, height: 1200 } });
const errs = [];
p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
p.on('pageerror', e => errs.push('pageerror: ' + e.message));
await p.goto('http://127.0.0.1:8792/board.html?b=fashion_wardrobe', { waitUntil: 'networkidle' });
await p.waitForTimeout(2500);
console.log('cards', await p.locator('.fcard').count());
console.log('藏花', await p.locator('.fr-flower').count(), '遮花苞', await p.locator('.fr-bud').count());
await p.screenshot({ path: '90_临时/shot_dim1.png' });
// 打开白月魁卡详情
const card = p.locator('.fcard', { hasText: '白月魁-衣服' }).first();
if (await card.count()) { await card.click({ force: true }); await p.waitForTimeout(1200); }
await p.screenshot({ path: '90_临时/shot_dim2.png' });
console.log('errors', errs.slice(0, 5));
await b.close();
