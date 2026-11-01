import { chromium } from 'file:///C:/Users/Administrator/AppData/Local/hermes/hermes-agent/node_modules/playwright/index.mjs';
const b = await chromium.launch({ executablePath: 'C:/Users/Administrator/AppData/Local/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-win64/chrome-headless-shell.exe' });
const p = await b.newPage({ viewport: { width: 1500, height: 1000 } });
await p.goto('http://127.0.0.1:8765/board.html?b=title_catalog', { waitUntil:'domcontentloaded' });
await p.waitForTimeout(1500);
// 搜「明月入梦」（动态+美术字）
await p.fill('#q','明月入梦'); await p.waitForTimeout(900);
await p.evaluate(()=>{ document.querySelector('#grid > .i .i-head').click(); });
await p.waitForTimeout(900);
const t = await p.evaluate(()=>{
  const d=document.querySelector('.i-detail:not([hidden])');
  return d?d.textContent.replace(/\s+/g,' ').slice(0,500):null;
});
await p.screenshot({path:'90_临时/shot_title_detail2.png'});
console.log(t);
await b.close();
