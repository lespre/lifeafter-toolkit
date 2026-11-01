import { chromium } from 'file:///C:/Users/Administrator/AppData/Local/hermes/hermes-agent/node_modules/playwright/index.mjs';
const b = await chromium.launch({ executablePath: 'C:/Users/Administrator/AppData/Local/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-win64/chrome-headless-shell.exe' });
const p = await b.newPage({ viewport: { width: 1500, height: 1000 } });
await p.goto('http://127.0.0.1:8765/board.html?b=fashion_wardrobe', { waitUntil:'networkidle' });
await p.waitForTimeout(1500);
await p.fill('#q','瑞秋的背包'); await p.waitForTimeout(1600);
await p.locator('.fcard').first().click(); await p.waitForTimeout(1500);
const info = await p.evaluate(()=>{
  const rows=[...document.querySelectorAll('.fd-row')].map(r=>[r.querySelector('.fd-k')?.textContent, r.querySelector('.fd-v')?.textContent?.slice(0,40)]);
  // 找全局板数据
  const keys=Object.keys(window).filter(k=>/board|data|items/i.test(k)).slice(0,12);
  return {rows, keys};
});
console.log(JSON.stringify(info,null,1));
await b.close();
