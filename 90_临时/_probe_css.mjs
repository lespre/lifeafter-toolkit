import { chromium } from 'file:///C:/Users/Administrator/AppData/Local/hermes/hermes-agent/node_modules/playwright/index.mjs';
const b = await chromium.launch({ executablePath: 'C:/Users/Administrator/AppData/Local/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-win64/chrome-headless-shell.exe' });
const p = await b.newPage({ viewport: { width: 1500, height: 1000 } });
await p.goto('http://127.0.0.1:8792/board.html?b=fashion_wardrobe', { waitUntil:'networkidle' });
await p.waitForTimeout(1200);
await p.fill('#q','云烟成羽'); await p.waitForTimeout(1200);
await p.locator('.fcard').first().click(); await p.waitForTimeout(1200);
const info = await p.evaluate(()=>{
  const k=[...document.querySelectorAll('.fd-k')].find(e=>e.textContent.includes('再生者'));
  if(!k) return 'no el';
  const cs=getComputedStyle(k);
  return {w:k.getBoundingClientRect().width, flex:cs.flex, ws:cs.whiteSpace, fs:cs.fontSize, parent:k.parentElement.className};
});
console.log(info);
await b.close();
