import { chromium } from 'file:///C:/Users/Administrator/AppData/Local/hermes/hermes-agent/node_modules/playwright/index.mjs';
const b = await chromium.launch({ executablePath: 'C:/Users/Administrator/AppData/Local/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-win64/chrome-headless-shell.exe' });
const p = await b.newPage({ viewport: { width: 1500, height: 1000 } });
await p.goto('http://127.0.0.1:8765/board.html?b=fashion_wardrobe', { waitUntil:'networkidle' });
await p.waitForTimeout(1500);
await p.fill('#q','不湮之花'); await p.waitForTimeout(1600);
const info = await p.evaluate(()=>{
  const out=[];
  document.querySelectorAll('.fcard').forEach(c=>{
    out.push({name:(c.querySelector('.fr-name,.fcard-title,.fc-title')||{}).textContent||c.textContent.slice(0,14),
              tags:[...c.querySelectorAll('.fr-alt')].map(x=>x.textContent.trim()),
              html:c.innerHTML.length});
  });
  return out.slice(0,6);
});
console.log(JSON.stringify(info,null,1));
const data = await p.evaluate(()=>{
  const it=(window.__BOARD_DATA__||window.BOARD||{});
  return 'x';
});
await b.close();
