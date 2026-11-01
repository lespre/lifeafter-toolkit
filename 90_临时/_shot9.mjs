import { chromium } from 'file:///C:/Users/Administrator/AppData/Local/hermes/hermes-agent/node_modules/playwright/index.mjs';
const b = await chromium.launch({ executablePath: 'C:/Users/Administrator/AppData/Local/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-win64/chrome-headless-shell.exe' });
for (const url of ['http://127.0.0.1:8765/index.html','http://127.0.0.1:8765/board.html?b=fashion_wardrobe']) {
  const p = await b.newPage({ viewport: { width: 1400, height: 900 } });
  const errs=[]; p.on('pageerror',e=>errs.push(e.message));
  p.on('console', m=>{ if(m.type()==='error') errs.push('console: '+m.text()); });
  const resp = await p.goto(url, { waitUntil:'networkidle' });
  await p.waitForTimeout(2000);
  const cards = await p.locator('.fcard').count();
  console.log(url, '| status', resp.status(), '| cards', cards, '| errors', errs.slice(0,3));
  await p.close();
}
await b.close();
