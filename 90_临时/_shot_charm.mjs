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
  const rows = await p.evaluate(()=>[...document.querySelectorAll('.fd-row')]
    .map(r=>[r.querySelector('.fd-k')?.textContent,(r.querySelector('.fd-v')?.textContent||'').replace(/\s+/g,' ').slice(0,140)])
    .filter(r=>r[0]&&/魅力/.test(r[0])));
  const chip = await p.evaluate(()=>{
    const el=document.querySelector('.fcard .fr-charm'); return el?el.getAttribute('title'):null; });
  return { rows, chip };
}

console.log('八载蜜语-背包:', JSON.stringify(await shot('八载蜜语','八载蜜语-背包','90_临时/shot_c1.png'),null,1));
console.log('浮光花序典藏-头饰:', JSON.stringify(await shot('浮光花序典藏','浮光花序典藏-头饰','90_临时/shot_c2.png'),null,1));
console.log('errors', errs); await b.close();
