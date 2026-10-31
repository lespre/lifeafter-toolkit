import path from "node:path";
import { pathToFileURL } from "node:url";
const CAND = [process.env.PLAYWRIGHT_PKG || "", "playwright",
  path.join(process.env.LOCALAPPDATA || "", "npm-cache/_npx/e41f203b7505f1fb/node_modules/playwright"),
  path.join(process.env.USERPROFILE || "", "AppData/Local/npm-cache/_npx/e41f203b7505f1fb/node_modules/playwright")].filter(Boolean);
let pw = null;
for (const c of CAND) {
  try { const t = path.isAbsolute(c) ? pathToFileURL(path.join(c, "index.mjs")).href : c; const m = await import(t); if (m && m.chromium) { pw = m; break; } } catch {}
}
const BASE = "http://127.0.0.1:8765";
const browser = await pw.chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 1100 } });
await page.goto(`${BASE}/board.html?b=fashion_wardrobe&v=20261101facemedia`, { waitUntil: "networkidle" });
await page.waitForTimeout(1500);
await page.screenshot({ path: "90_临时/shot_init.png" });
const dump = await page.evaluate(() => {
  const out = [];
  document.querySelectorAll("[data-part], .fr-pill, .pill, .fr-chip, [class*=chip], #frParts *").forEach((e) => {
    const t = (e.textContent || "").trim();
    if (t && t.length < 20) out.push(e.tagName + "|" + (e.className || "") + "|" + t);
  });
  return out.slice(0, 80);
});
console.log(dump.join("\n"));
console.log("---- selects", await page.evaluate(() => [...document.querySelectorAll("select")].map((s) => s.id + ":" + [...s.options].map(o => o.textContent.trim()).join("/"))));
await browser.close();
