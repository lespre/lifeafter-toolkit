import path from "node:path";
import { pathToFileURL } from "node:url";
const CAND = ["playwright",
  path.join(process.env.LOCALAPPDATA || "", "npm-cache/_npx/e41f203b7505f1fb/node_modules/playwright"),
  path.join(process.env.USERPROFILE || "", "AppData/Local/npm-cache/_npx/e41f203b7505f1fb/node_modules/playwright")].filter(Boolean);
let pw = null;
for (const c of CAND) { try { const t = path.isAbsolute(c) ? pathToFileURL(path.join(c, "index.mjs")).href : c; const m = await import(t); if (m && m.chromium) { pw = m; break; } } catch {} }
const browser = await pw.chromium.launch();
const page = await browser.newPage({ viewport: { width: 1500, height: 1300 } });
await page.goto("http://127.0.0.1:8765/board.html?b=fashion_wardrobe&v=20261101facemedia", { waitUntil: "networkidle" });
await page.waitForTimeout(1200);
await page.locator("button.fr-chip", { hasText: "面饰53" }).first().click();
await page.waitForTimeout(1200);
await page.locator(".fcard", { hasText: "绮绚燃焰" }).first().click();
await page.waitForTimeout(900);
const r = await page.evaluate(() => {
  const ds = [...document.querySelectorAll("details.tech")];
  return ds.map((d) => ({ open: d.open, len: d.innerHTML.length, head: d.innerHTML.slice(0, 300) }));
});
console.log(JSON.stringify(r, null, 1).slice(0, 1600));
await browser.close();
