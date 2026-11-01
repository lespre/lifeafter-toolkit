import { chromium } from 'file:///C:/Users/Administrator/AppData/Local/hermes/hermes-agent/node_modules/playwright/index.mjs';
const b = await chromium.launch({ executablePath: 'C:/Users/Administrator/AppData/Local/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-win64/chrome-headless-shell.exe' });
const p = await b.newPage({ viewport: { width: 1500, height: 1050 } });
const errs=[]; p.on('pageerror',e=>errs.push(e.message));
async function shot(q, want, file){
  await p.goto('http://127.0.0.1:8765/board.html?b=fashion_wardrobe', { waitUntil:'networkidle' });
  await p.waitForTimeout(1400);
  await p.fill('#q', q); await p.waitForTimeout(1500);
  const c = p.locator('.fcard').filter({ hasText: want }).first();
  await c.click(); await p.waitForTimeout(1700);
  await p.screenshot({ path: file });
  const rows = await p.evaluate(()=>[...document.querySelectorAll('.fd-row')].map(r=>[r.querySelector('.fd-k')?.textContent,(r.querySelector('.fd-v')?.textContent||'').slice(0,60)]).filter(r=>r[0]&&/魅力/.test(r[0])));
  return rows;
}
console.log('一串小饼干:', JSON.stringify(await shot('一串小饼干','一串小饼干','90_临时/shot_e1.png')));
console.log('无暇的祝福:', JSON.stringify(await shot('无暇的祝福','无暇的祝福','90_临时/shot_e2.png')));
console.log('errors', errs); await b.close();
