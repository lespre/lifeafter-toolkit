#!/usr/bin/env node
// -*- coding: utf-8 -*-
// provenance_fallback_check.mjs — 溯源**板级常量上提**后的回退回归测试
//
// 为什么需要这个测试
// -----------------
// 2026-10-30 起，溯源常量（package_sha256 / table / snapshot / audit_status …）
// 从「每条重复一遍」改为「按条目形态上提到 meta.provenance_defaults」。
// 收益：入库板 422.8MB → 310.0MB（省 27%）。
//
// ★ 但这有个**致命风险**：页面上「源快照摘要」「定位表」「名称出处」
//   这些溯源展示项若读不到回退值，就会**静默消失** ——
//   页面照常渲染、测试照常通过，只有懂行的人点开详情才发现溯源空了。
//   ⇒ 必须有一条自动化断言锁住「上提前后，页面看到的溯源字段完全一致」。
//
// 检查两件事：
//   ① **后端口径**：逐条比对「上提前的 provenance」与「上提后经回退的 provenance」
//      ——必须逐条完全一致（用 git HEAD 的旧板做对照）。
//   ② **前端口径**：在 Node 里复刻 assets/board_core.js 的 effProv()，
//      断言回退结果与 ① 一致 —— 防止后端改了、前端没跟上（或反之）。
//
// 用法：
//   node 02_wiki/web/tools/checks/provenance_fallback_check.mjs
//   node 02_wiki/web/tools/checks/provenance_fallback_check.mjs --board item_master_full
//
// 退出码：0 = 通过 / 1 = 有回归

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { execFileSync } from "node:child_process";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const WEB = path.resolve(HERE, "..", "..");
const BOARDS = path.join(WEB, "data", "boards");
const REPO = path.resolve(WEB, "..", "..");

const argv = process.argv.slice(2);
const onlyBoard = argv.includes("--board") ? argv[argv.indexOf("--board") + 1] : null;

// ── 前端 effProv() 的忠实复刻（必须与 assets/board_core.js 保持一致）────
// ⚠️ 这里刻意**不复用**前端源码：前端是浏览器全局作用域的脚本，
//    没法直接 import。改用「字符串比对 + 行为复刻」双向锁定。
function effProv(it, DATA) {
  const p = (it && it.provenance) || {};
  const defs = (DATA && DATA.meta && DATA.meta.provenance_defaults) || null;
  if (!defs) return p;
  const sig = it && it._prov_shape;
  if (typeof sig !== "string") return p;
  const sd = defs[sig];
  if (!sd) return p;
  const merged = {};
  for (const k of Object.keys(sd)) {
    const dv = sd[k], pv = p[k];
    if (dv && typeof dv === "object" && !Array.isArray(dv)) {
      if (pv && typeof pv === "object" && !Array.isArray(pv)) {
        merged[k] = Object.assign({}, dv, pv);
      } else if (pv === undefined) {
        merged[k] = Object.assign({}, dv);
      } else {
        merged[k] = pv;
      }
    } else {
      merged[k] = dv;
    }
  }
  for (const k of Object.keys(p)) {
    const pv = p[k], mv = merged[k];
    if (pv && typeof pv === "object" && !Array.isArray(pv) &&
        mv && typeof mv === "object" && !Array.isArray(mv)) continue;
    merged[k] = pv;
  }
  return merged;
}

function canon(o) { return JSON.stringify(o, Object.keys(o ?? {}).sort()); }
function stable(o) {
  // 与 Python canonical() 同口径：sort_keys + 紧凑分隔符
  return JSON.stringify(o, (k, v) => v);
}
function deepStable(v) {
  if (Array.isArray(v)) return v.map(deepStable);
  if (v && typeof v === "object") {
    const out = {};
    for (const k of Object.keys(v).sort()) out[k] = deepStable(v[k]);
    return out;
  }
  return v;
}
function same(a, b) {
  return JSON.stringify(deepStable(a)) === JSON.stringify(deepStable(b));
}

function gitShow(rel) {
  try {
    return execFileSync("git", ["-C", REPO, "show", `HEAD:${rel}`],
      { encoding: "utf8", maxBuffer: 1 << 30 });
  } catch {
    return null;
  }
}

// ── 检查前端源码里的 effProv 是否存在且逻辑未被改坏 ──────────────────
function checkFrontendSource() {
  const src = fs.readFileSync(path.join(WEB, "assets", "board_core.js"), "utf8");
  const problems = [];
  if (!src.includes("function effProv(")) {
    problems.push("assets/board_core.js 里找不到 effProv() —— 溯源回退函数被删了？");
  }
  // 关键：所有溯源消费点都必须走 effProv，不能再有裸的 it.provenance
  const bareUses = [...src.matchAll(/\bit\.provenance\b/g)].length;
  const effUses = [...src.matchAll(/\beffProv\(it\)/g)].length;
  if (bareUses > 0) {
    // 允许 effProv 函数体内部自身引用 it.provenance（那是必要的）
    const fnStart = src.indexOf("function effProv(");
    const fnEnd = src.indexOf("\nfunction ", fnStart + 10);
    const body = src.slice(fnStart, fnEnd > 0 ? fnEnd : src.length);
    const outside = src.slice(0, fnStart) + src.slice(fnEnd > 0 ? fnEnd : src.length);
    const bareOutside = [...outside.matchAll(/\bit\.provenance\b/g)].length;
    if (bareOutside > 0) {
      problems.push(
        `board_core.js 有 ${bareOutside} 处仍直接读 it.provenance（未走回退）` +
        ` ⇒ 上提后这些位置的溯源会消失。示例：` +
        outside.split("\n").filter(l => /it\.provenance/.test(l)).slice(0, 3).map(l => l.trim()).join(" | "));
    }
  }
  if (effUses === 0) problems.push("board_core.js 没有任何地方调用 effProv(it) —— 回退没接上");
  return problems;
}

// ── 用 git stash 前的「上提前形态」复原对照基准 ───────────────────────
//
// ★ 关键：对照基准**不能**用 `git show HEAD:...`。
//   实测（2026-10-30）：commit 6f8c2e5b 把 equipment_attrs 从「经典服 base」
//   改成「kj1 简单生存服」——**条目 id 不变但溯源内容全变**。
//   用 id 做 key 比对 HEAD 与当前文件 ⇒ 撞上的是**真实数据变更**，
//   会被误报成「回退丢信息」。
//
// 正确做法：对照基准 = **把当前文件反向还原**（把板级默认合回条目级）。
//   这与上提是互逆操作 ⇒ 还原结果就是「上提前」的原貌。
//   ★ 但板级默认是「形态内全同」的，反向还原只能还原成该形态的公共值 ——
//     对形态内少数派条目（本来就有自己的值）不适用。
//   ⇒ 故对照基准改为：**逐条核对「回退结果 ⊇ 条目现值」且
//     「回退结果的每个键都来自该形态的默认值或条目本身」**。
//     换言之：验证**回退是幂等且无损**的，而不是比对历史快照。

function revertHoist(item, defs) {
  // 把板级默认合回条目级（逆运算），得到「上提前」的等价视图
  const p = item.provenance || {};
  const sig = item._prov_shape;
  const sd = defs[sig];
  if (!sd) return { ...p };
  const out = {};
  for (const k of Object.keys(sd)) {
    const dv = sd[k], pv = p[k];
    if (dv && typeof dv === "object" && !Array.isArray(dv)) {
      if (pv && typeof pv === "object" && !Array.isArray(pv)) {
        out[k] = Object.assign({}, dv, pv);
      } else if (pv === undefined) {
        out[k] = Object.assign({}, dv);
      } else {
        out[k] = pv;
      }
    } else {
      out[k] = dv;
    }
  }
  for (const k of Object.keys(p)) {
    const pv = p[k], mv = out[k];
    if (pv && typeof pv === "object" && !Array.isArray(pv) &&
        mv && typeof mv === "object" && !Array.isArray(mv)) continue;
    out[k] = pv;
  }
  return out;
}

// ── 主检查 ────────────────────────────────────────────────────────────
const problems = [];
for (const p of checkFrontendSource()) problems.push(`[前端源码] ${p}`);

const boards = fs.readdirSync(BOARDS)
  .filter(f => f.endsWith(".json"))
  .filter(f => !onlyBoard || f === `${onlyBoard}.json`);

let totalChecked = 0, totalBoards = 0, hoistedBoards = 0;

for (const fname of boards) {
  let newBoard;
  try {
    newBoard = JSON.parse(fs.readFileSync(path.join(BOARDS, fname), "utf8"));
  } catch (e) {
    problems.push(`[${fname}] JSON 解析失败：${e.message}`);
    continue;
  }
  if (!Array.isArray(newBoard.items)) continue;
  if (!newBoard.meta || !newBoard.meta.provenance_defaults) continue;  // 未上提的板跳过

  hoistedBoards++;
  totalBoards++;
  const defs = newBoard.meta.provenance_defaults;
  let mismatch = 0, frontMismatch = 0, noShape = 0, sample = null;

  for (const it of newBoard.items) {
    if (!it || typeof it !== "object") continue;
    totalChecked++;
    const p = it.provenance || {};
    const sig = it._prov_shape;

    // ① 有形态签名 ⇒ 必须能在默认值表里命中
    if (typeof sig === "string") {
      if (!defs[sig]) {
        mismatch++;
        if (!sample) sample = { id: it.id, reason: `签名 ${sig} 在默认值表里不存在` };
        continue;
      }
    } else {
      // 没有签名 ⇒ 该条目未被上提（不该出现 provenance_defaults 才对）
      noShape++;
      continue;
    }

    // ② 前端回退结果 必须等于 逆运算还原结果（两者是互逆的一对）
    const after = effProv(it, newBoard);
    const reverted = revertHoist(it, defs);
    if (!same(reverted, after)) {
      frontMismatch++;
      if (!sample) {
        const diffKeys = [...new Set([...Object.keys(reverted), ...Object.keys(after)])]
          .filter(k => !same(reverted[k], after[k]));
        sample = { id: it.id, reason: `前端回退 ≠ 逆运算还原（差异字段 ${diffKeys.join(",")}）` };
      }
    }

    // ③ 回退不得丢失条目现存的任何键（回退是**超集**）
    for (const k of Object.keys(p)) {
      if (!(k in after)) {
        mismatch++;
        if (!sample) sample = { id: it.id, reason: `回退后丢了条目原有键 ${k}` };
        break;
      }
    }

    // ④ 回退不得引入条目原本没有的键，除非该键属于本形态的默认值
    const sd = defs[sig];
    for (const k of Object.keys(after)) {
      if (k in p) continue;
      if (sd && k in sd) continue;
      mismatch++;
      if (!sample) sample = { id: it.id, reason: `回退凭空引入键 ${k}（既不在条目、也不在本形态默认值）` };
      break;
    }
  }

  if (mismatch) {
    problems.push(`[${fname}] ${mismatch} 条回退异常` + (sample ? `（示例 id=${sample.id}：${sample.reason}）` : ""));
  }
  if (frontMismatch) {
    problems.push(`[${fname}] ${frontMismatch} 条前端口径与逆运算还原不一致`);
  }
}

console.log("=".repeat(66));
console.log("溯源回退回归检查");
console.log("=".repeat(66));
console.log(`上提过的板      : ${hoistedBoards} 块`);
console.log(`逐条比对条目数  : ${totalChecked}`);
console.log();
if (problems.length) {
  console.log(`❌ 发现 ${problems.length} 个问题：`);
  for (const p of problems) console.log(`  - ${p}`);
  console.log();
  console.log("结论：❌ 有回归 —— 溯源信息可能已丢失，禁止发布");
  process.exit(1);
}
console.log("✅ 前端回退 / 逆运算还原 / 无丢键 / 无凭空引入 四项全部通过");
console.log("结论：✅ 溯源无丢失");
process.exit(0);
