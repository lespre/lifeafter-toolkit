import path from "node:path";
import fs from "node:fs";
import { pathToFileURL } from "node:url";
const CAND = ["playwright",
  path.join(process.env.LOCALAPPDATA || "", "npm-cache/_npx/e41f203b7505f1fb/node_modules/playwright"),
  path.join(process.env.USERPROFILE || "", "AppData/Local/npm-cache/_npx/e41f203b7505f1fb/node_modules/playwright")].filter(Boolean);
let pw = null;
for (const c of CAND) { try { const t = path.isAbsolute(c) ? pathToFileURL(path.join(c, "index.mjs")).href : c; const m = await import(t); if (m && m.chromium) { pw = m; break; } } catch {} }
const browser = await pw.chromium.launch();
const page = await browser.newPage({ viewport: { width: 1500, height: 1150 } });
await page.goto("http://127.0.0.1:8765/board.html?b=fashion_wardrobe&v=20261101facemedia", { waitUntil: "networkidle" });
await page.waitForTimeout(1500);
await page.locator("button.fr-chip", { hasText: "头饰111" }).first().click();
await page.waitForTimeout(1500);
const ids = await page.evaluate(() => [...document.querySelectorAll(".fcard")].map((e) => e.dataset.frid));
fs.writeFileSync("90_临时/ids.json", JSON.stringify(ids));
console.log(ids.length);
await browser.close();
