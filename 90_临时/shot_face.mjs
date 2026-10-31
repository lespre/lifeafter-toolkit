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
const page = await browser.newPage({ viewport: { width: 1500, height: 1150 } });
const errs = [];
page.on("pageerror", (e) => errs.push(String(e)));
page.on("console", (m) => { if (m.type() === "error") errs.push(m.text()); });
await page.goto(`${BASE}/board.html?b=fashion_wardrobe&v=20261101facemedia`, { waitUntil: "networkidle" });
await page.waitForTimeout(1500);

for (const [chip, out] of [["头饰111", "90_临时/shot_toushi.png"], ["面饰53", "90_临时/shot_mianshi.png"]]) {
  await page.locator("button.fr-chip", { hasText: chip }).first().click();
  await page.waitForTimeout(1800);
  const info = await page.evaluate(() => ({
    cards: document.querySelectorAll(".fcard").length,
    imgs: document.querySelectorAll(".fcard .fr-rail img").length,
    count: (document.querySelector("#frCount") || {}).textContent || "",
  }));
  console.log(chip, JSON.stringify(info));
  await page.screenshot({ path: out });
  const card = page.locator(".fcard").first();
  await card.click();
  await page.waitForTimeout(1200);
  await page.screenshot({ path: out.replace(".png", "_detail.png") });
  await page.keyboard.press("Escape");
  await page.waitForTimeout(600);
}
console.log("errs", errs.length, errs.slice(0, 4));
await browser.close();
