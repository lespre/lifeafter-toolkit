import { chromium } from 'file:///C:/Users/Administrator/AppData/Local/hermes/hermes-agent/node_modules/playwright/index.mjs';
const b = await chromium.launch({ executablePath: 'C:/Users/Administrator/AppData/Local/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-win64/chrome-headless-shell.exe' });
const p = await b.newPage({ viewport: { width: 1500, height: 1100 } });
await p.goto('http://127.0.0.1:8765/board.html?b=fashion_wardrobe', { waitUntil:'networkidle' });
await p.waitForTimeout(1400);
await p.fill('#q','一串小饼干'); await p.waitForTimeout(1500);
await p.locator('.fcard').first().click(); await p.waitForTimeout(1500);
const rows = await p.evaluate(()=>[...document.querySelectorAll('.fd-row')].map(r=>[r.querySelector('.fd-k')?.textContent, (r.querySelector('.fd-v')?.textContent||'').slice(0,80)]));
console.log(JSON.stringify(rows.filter(r=>r[0]&&/模型|说明/.test(r[0])),null,1));
// 技术详情里的
const kv = await p.evaluate(()=>{
  const t=[...document.querySelectorAll('.fdesc,.fd-row,details')].map(e=>e.textContent).join('\n');
  const i=t.indexOf('模型路径');
  return i>=0? t.slice(i,i+200): 'not found';
});
console.log('上下文:', kv);
await b.close();
