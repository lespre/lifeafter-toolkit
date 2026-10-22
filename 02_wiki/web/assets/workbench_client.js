/* Workbench Web Client 共享层（v1.3）
 *
 * 职责边界（成功标准 13）：前端只能 filter / sort / group / format / render。
 * 禁止在前端：按 raw_presence 推 namespace、按整数碰撞 join、自己决定 verified、
 * 自己计算 reward target type、自己合并 Fashion namespace。
 * 所有业务结论必须来自 services/domain（API）。
 */
window.WB = (function () {
  const PAGE_MAX = 200;

  const SECTION_CN = {
    identity: "身份", data: "数据", source: "来源（snapshot 基准）", raw_presence: "Raw 存在性",
    evidence: "证据", provenance: "溯源", residuals: "未决项（residual）", media: "媒体"
  };
  const VALUE_CN = {
    verified: "已核验", unresolved: "待确认", unresolved_replacement_overlay: "运行时最终未解析（replacement overlay）",
    not_tracked: "未跟踪", entry_not_in_snapshot_basis: "该 entry 不在本快照基准内",
    fid_not_present_in_snapshot: "FID 不在该快照", no_canonical_entry: "无 canonical entry",
    chs_not_found_in_snapshot: "该快照无 CHS 绑定", ok: "已绑定",
    verified_runtime_business_key: "运行时业务键已核验", runtime_namespace_raw_row_membership: "namespace 成员资格",
    common_item: "common_item（道具主表）", gift_data: "gift_data（礼盒）", recipe: "recipe（配方）",
    belt_chip: "belt_chip（腰带芯片）", reward_pool: "reward_pool（奖励池）", space_data: "space_data（空间）"
  };

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  }
  function zh(v) {
    if (v === null || v === undefined) return "—";
    if (typeof v === "boolean") return v ? "是" : "否";
    const k = String(v);
    return VALUE_CN[k] || k;
  }
  function badge(text, cls) { return '<span class="wb-badge ' + (cls || "") + '">' + esc(text) + "</span>"; }

  function qs(params) {
    const p = new URLSearchParams();
    Object.entries(params || {}).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== "") p.set(k, v);
    });
    const s = p.toString();
    return s ? "?" + s : "";
  }

  async function api(path, params) {
    const res = await fetch(path + qs(params));
    let data = null;
    try { data = await res.json(); } catch (e) { throw new Error("响应不是 JSON（API 未启动？）：" + path); }
    if (!res.ok || data.error) throw new Error(data.error + (data.detail ? "：" + data.detail : ""));
    return data;
  }

  function fmtJson(v, max) {
    if (v === null || v === undefined) return "—";
    if (typeof v !== "object") return esc(zh(v));
    let s = "";
    try { s = JSON.stringify(v, null, 1); } catch (e) { s = String(v); }
    if (max && s.length > max) s = s.slice(0, max) + "\n…（截断，共 " + s.length + " 字符）";
    return "<pre class='wb-pre'>" + esc(s) + "</pre>";
  }

  /* --- 快照基准区块：绝不允许把 BA8A 结论简化成 verified（硬规则） --- */
  function snapshotBanner(source) {
    if (!source || typeof source !== "object") return "";
    const basis = source.snapshot_basis || source.snapshot_basis_explicit;
    const cur = source.current_snapshot_binding || null;
    if (!basis && !cur) return "";
    const rows = [];
    if (basis) {
      rows.push('<div class="wb-basis"><b>Snapshot basis：</b><code>' + esc(basis) + "</code>" +
        (source.snapshot_basis_explicit ? badge("显式标注", "warn") : badge("由 provenance.snapshot 推导", "")) + "</div>");
    }
    if (cur) {
      const st = String(cur.status || "unresolved");
      rows.push('<div class="wb-basis"><b>Current snapshot binding：</b>' +
        badge(zh(st), st === "ok" ? "ok" : "warn") +
        (cur.snapshot_id ? " <code>" + esc(cur.snapshot_id) + "</code>" : "") +
        (cur.note ? ' <span class="wb-note">' + esc(cur.note) + "</span>" : "") + "</div>");
    }
    return '<div class="wb-snapshotbox">' + rows.join("") + '</div>';
  }

  function renderValue(k, v) {
    if (v === null || v === undefined) return "—";
    if (typeof v === "object") return fmtJson(v);
    if (k === "name_status" || k === "business_identity" || k === "identity_status" || k === "status") {
      return badge(zh(v), String(v).indexOf("verified") === 0 || v === "ok" ? "ok" : (String(v).indexOf("unresolved") >= 0 || v === "not_tracked" ? "warn" : ""));
    }
    return esc(zh(v));
  }

  function kvTable(obj) {
    const rows = Object.entries(obj || {}).map(([k, v]) =>
      "<tr><th>" + esc(k) + "</th><td>" + renderValue(k, v) + "</td></tr>").join("");
    return "<table class='wb-kv'>" + rows + "</table>";
  }

  /* --- 统一 Entity Detail 渲染（Identity/Data/Source/Raw presence/Evidence/Provenance/Residuals/Media） --- */
  function renderEntity(data) {
    const s = data.sections || {};
    const out = [];
    out.push('<div class="wb-entity-head"><span class="wb-kind">' + esc(data.kind) + "</span> <b>" + esc(data.title || data.id) + "</b></div>");
    out.push(snapshotBanner(s.source));
    ["identity", "data", "source"].forEach(sec => {
      if (s[sec] === undefined) return;
      out.push('<div class="wb-sec"><div class="wb-sec-h">' + SECTION_CN[sec] + "</div>" + kvTable(s[sec]) + "</div>");
    });
    if (s.raw_presence) {
      out.push('<div class="wb-sec"><div class="wb-sec-h">Raw 存在性 <span class="wb-note">（raw 表存在 ≠ business namespace）</span></div>' +
        kvTable(s.raw_presence) + "</div>");
    }
    const claims = (s.evidence && s.evidence.claims) || [];
    out.push('<div class="wb-sec"><div class="wb-sec-h">证据（' + claims.length + " 条）</div>" +
      (claims.length ? "<details><summary>展开证据链</summary>" + claims.map(c =>
        '<div class="wb-claim"><div>' + badge(zh(c.status), c.status === "verified" ? "ok" : "warn") +
        " <b>" + esc(c.claim || c.file) + "</b></div>" +
        '<div class="wb-note">' + esc(c.file) + " · " + esc(c.evidence_type || "") + " · relevance=" + esc(c.relevance) + "</div>" +
        (c.snapshot_source ? '<div class="wb-note">snapshot: ' + esc(c.snapshot_source) + "</div>" : "") +
        (c.symbols ? fmtJson(c.symbols, 1200) : "") + "</div>").join("") + "</details>"
        : '<div class="wb-note">该 Domain 无对应 evidence 文件</div>') + "</div>");
    out.push('<div class="wb-sec"><div class="wb-sec-h">溯源</div><details><summary>展开 provenance</summary>' +
      fmtJson(s.provenance, 4000) + "</details></div>");
    const res = s.residuals || {};
    out.push('<div class="wb-sec"><div class="wb-sec-h">未决项（residual）</div>' +
      ((res.files || []).length ? "<details><summary>展开 residual（总计数 " + esc(res.total_count) + "）</summary>" +
        fmtJson(res.files, 3000) + (res.per_id ? "<div><b>本条命中：</b>" + fmtJson(res.per_id, 1200) + "</div>" : "") + "</details>"
        : '<div class="wb-note">该 Domain 无 residual 文件</div>') + "</div>");
    const media = s.media || {};
    out.push('<div class="wb-sec wb-media"><div class="wb-sec-h">媒体（预留）</div>' +
      badge(zh(media.status || "not_implemented"), "warn") + " " + esc(media.note || "") + "</div>");
    return out.join("");
  }

  /* --- 分页控件 --- */
  function renderPager(el, meta, onGo) {
    const total = meta.total || 0, page = meta.page || 1, size = meta.page_size || 50, pages = meta.pages || 1;
    el.innerHTML = "";
    const from = total ? (page - 1) * size + 1 : 0, to = Math.min(page * size, total);
    const info = document.createElement("span");
    info.className = "wb-page-info";
    info.textContent = "共 " + total.toLocaleString() + " 条 · 第 " + page + "/" + pages + " 页 · 显示 " + from + "–" + to +
      (meta.clamped ? " · page_size 已被上限 " + PAGE_MAX + " 截断" : "");
    const mk = (label, target, disabled) => {
      const b = document.createElement("button");
      b.textContent = label; b.disabled = !!disabled;
      b.addEventListener("click", () => onGo(target));
      return b;
    };
    el.appendChild(mk("« 首页", 1, page <= 1));
    el.appendChild(mk("‹ 上一页", page - 1, page <= 1));
    el.appendChild(info);
    el.appendChild(mk("下一页 ›", page + 1, page >= pages));
    el.appendChild(mk("末页 »", pages, page >= pages));
  }

  /* --- View 模式（Wiki View / Workbench View 共用同一 Domain 数据） --- */
  function mode(def) {
    const url = new URLSearchParams(location.search).get("view");
    if (url === "wiki" || url === "workbench") { try { localStorage.setItem("wb_view", url); } catch (e) {} return url; }
    try { const saved = localStorage.getItem("wb_view"); if (saved) return saved; } catch (e) {}
    return def || "wiki";
  }
  function setMode(m) {
    try { localStorage.setItem("wb_view", m); } catch (e) {}
    const u = new URL(location.href); u.searchParams.set("view", m); location.href = u.toString();
  }

  function notice(el, html, cls) {
    el.innerHTML = '<div class="wb-notice ' + (cls || "") + '">' + html + "</div>";
  }
  function error(el, err) {
    notice(el, "<b>无法从 Workbench API 取数：</b>" + esc(err.message) +
      '<div class="wb-note">本轮不允许静默回退 legacy board / historical 数据；请启动 <code>python -m api.server --port 8770</code>' +
      "（静态打开页面时同样需要 API，或使用标记为 offline_full_projection 的显式离线导出）。</div>", "bad");
  }

  return { PAGE_MAX, SECTION_CN, esc, zh, badge, api, fmtJson, renderEntity, renderPager, mode, setMode,
           notice, error, snapshotBanner };
})();
