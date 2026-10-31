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
const d = page.locator("details.tech").first();
await d.evaluate((e) => (e.open = true));
await page.waitForTimeout(500);
const txt = await page.evaluate(() => {
  const m = document.querySelector(".c2-stage") || document.querySelector(".c2-mask");
  return m ? m.innerText : "";
});
const lines = txt.split("\n").map((s) => s.trim()).filter(Boolean);
console.log("lines", lines.length);
console.log(lines.filter((l) => /来源|字段|行 |图标|描述|魅力/.test(l)).slice(0, 40).join("\n"));
await page.screenshot({ path: "90_临时/shot_face_tech.png" });
await browser.close();
