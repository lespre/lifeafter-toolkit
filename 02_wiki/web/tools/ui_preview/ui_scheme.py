# -*- coding: utf-8 -*-
r"""解 `com/cdata/hd_ui_scheme_reverse_data.py` —— 活动界面「控件模块库」。

═══════════════════════════════════════════════════════════════════════════
★ 这张表是什么（实测，2026-11-07）
   活动界面不是 csb：`ui_class` 脚本调用 `load_hd_ui_scheme(ui_group_id)` 动态搭建，
   布局数据在 `hd_ui_scheme` 表里。该表的 **_base 在包里没有副本**（见
   `ACTIVITY_PANEL_EVIDENCE.md` 验证 1），所以「活动 → 整块面板」拼不出来。
   但 **reverse 表是真数据、能解**，它给的是**可复用控件模块**：
   一个模块 = 一个容器 + 若干子控件（按钮底图/常态/按下、文案、折扣标签、任务格…），
   并且**按 ui_group_id 存多套变体**。

★ 布局（与 toolkit_core.bindict_73 头注释一致，逐字节核对过）
   payload:
     [0:4]   u32 count          = CHS 池长度（11951）
     [4:8]   u32 reserved       = 0
     [8:..]  count × u32 ends   = 全 0（基表不带字面量池）
             u32 de             → blob[de] = 0x76 05 0b 索引尾（327 桶 / 327 节点）
   row:
     key = 模块 id；每个列名 = 活动处理器类（FashionSuitLotteryHD …）
     列值 = 0x0b jump → blob[off] = 0x36 映射帧
   0x36 映射帧： 36 <kt> <vt> <n> (uleb ui_group, uleb 目标偏移) × n
   目标偏移：    0x27 列表帧 → 27 <type> <n> (uleb 子控件偏移) × n
   子控件：      0x86 行（schema 32）→ id / widget_name / texture / pnl_offset …
   坐标：        pnl_offset → 27 12 02 + 2×float32（y 轴向上）

★ 用法
   python ui_scheme.py                # 全量导出 JSON + 生成预览页
   python ui_scheme.py --dump-only    # 只落 JSON
"""
from __future__ import annotations

import html
import json
import pathlib
import struct
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import la_paths  # noqa: E402

CD = la_paths.find_project_root() / "01_索引与产物/41_还原树/pe/配置/com/cdata"
OUT = la_paths.find_project_root() / "_ui_preview" / "scheme"
BASE = "hd_ui_scheme_reverse_data.py"
CHS = "hd_ui_scheme_reverse_data_chs.py"

sys.path.insert(0, str(la_paths.find_project_root() / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT  # noqa: E402
from toolkit_core import script_decode as SD  # noqa: E402
from toolkit_core.bindict_73 import decode_73_table  # noqa: E402

FRAME_MAP = 0x36
FRAME_LIST = 0x27
MAPPING_KEYS = ("ui_group",)


# ───────────────────────────────────────────────────────────── 读取原始字节
def const_blob(path: pathlib.Path, idx: int | None = None) -> bytes:
    """取 .py 里那个 bytes 常量（表体）。基表在 consts[2]，chs 在 consts[0]。"""
    _r, code, _end = SD.load_module(str(path))
    vals = [c.v if hasattr(c, "v") else c for c in code.consts]
    if idx is not None:
        return vals[idx]
    blobs = [v for v in vals if isinstance(v, bytes)]
    if not blobs:
        raise SystemExit("常量池里没有 bytes：%s" % path.name)
    return max(blobs, key=len)


def uleb(buf: bytes, pos: int, end: int) -> tuple[int, int]:
    val = shift = 0
    while pos < end:
        c = buf[pos]
        pos += 1
        val |= (c & 0x7F) << shift
        shift += 7
        if not c & 0x80:
            return val, pos
    raise ValueError("ULEB 越界 @%d" % pos)


def vec2(blob: bytes, off: int) -> list[float] | None:
    """坐标/尺寸：27 12 <n> + n×float32。"""
    if off < 0 or off + 3 > len(blob) or blob[off] != FRAME_LIST:
        return None
    n = blob[off + 2]
    if not 1 < n <= 8:
        return None
    try:
        return [round(v, 3) for v in struct.unpack_from("<%df" % n, blob, off + 3)]
    except struct.error:
        return None


def list_offsets(blob: bytes, off: int) -> list[int]:
    """0x27 列表帧 → 元素偏移列表。"""
    if off < 0 or off + 3 > len(blob) or blob[off] != FRAME_LIST:
        return []
    n = blob[off + 2]
    pos, out = off + 3, []
    try:
        for _ in range(n):
            v, pos = uleb(blob, pos, len(blob))
            out.append(v)
    except ValueError:
        pass
    return out


def map_frame(blob: bytes, off: int) -> list[tuple[int, int]]:
    """0x36 映射帧 → [(ui_group, 目标偏移)]。"""
    if off < 0 or off + 4 > len(blob) or blob[off] != FRAME_MAP:
        return []
    n = blob[off + 3]
    pos, out = off + 4, []
    try:
        for _ in range(n):
            k, pos = uleb(blob, pos, len(blob))
            v, pos = uleb(blob, pos, len(blob))
            out.append((k, v))
    except ValueError:
        pass
    return out


# ───────────────────────────────────────────────────────────── 控件模块提取
_TEX: dict[str, str | None] = {}
_SIZE: dict[str, tuple[int, int] | None] = {}


def _tex_png(tex: str) -> str | None:
    """贴图逻辑名（.png）→ 全局 assets 里的解码后文件名；缺图返回 None。

    ★ 这张表里的贴图路径带 `ui/` 前缀（csb 里的不带），而 `ui_dir()` 已经是
      `…/pe/资源/ui`，直接 join 会变成 `资源/ui/ui/…` ⇒ 必须先剥掉。
    """
    if not tex:
        return None
    if tex not in _TEX:
        norm = tex.replace("\\", "/")
        if norm.startswith("ui/"):
            norm = norm[3:]
        try:
            from csb2html import tex_png
            _TEX[tex] = tex_png(norm)
        except Exception:                                    # noqa: BLE001
            _TEX[tex] = None
    return _TEX[tex]


def _png_size(name: str | None) -> tuple[int, int] | None:
    """解码后 PNG 的原始像素尺寸，用于给「只有贴图没有 size」的控件兜底。"""
    if not name:
        return None
    if name not in _SIZE:
        try:
            from PIL import Image
            from csb2html import ASSET_DIR
            with Image.open(ASSET_DIR / name) as im:
                _SIZE[name] = im.size
        except Exception:                                    # noqa: BLE001
            _SIZE[name] = None
    return _SIZE[name]


def extract() -> dict:
    pool = BT.parse_chs_pool(const_blob(CD / CHS))
    raw = const_blob(CD / BASE, 2)
    count = struct.unpack_from("<I", raw, 0)[0]
    blob = raw[8 + 4 * count:]
    rows, unbound = BT.decode_table_rows(raw, pool, lenient=True)
    print("  行 %d（宽松；未解 %d）｜ 池 %d 项" % (len(rows), len(unbound), len(pool)))

    def jump_off(val) -> int | None:
        """列值可能是 ('0x0b','jump:N') 元组，也可能是合并后的 'jump:N' 字符串。"""
        if isinstance(val, (list, tuple)) and len(val) == 2 and val[0] == "0x0b":
            val = val[1]
        if isinstance(val, str) and val.startswith("jump:"):
            try:
                return int(val.split(":")[1])
            except (IndexError, ValueError):
                return None
        return None

    modules: dict[tuple[str, int], dict[int, dict]] = {}
    for row in rows:
        mid = row["key"]
        for cls, val in row["values"].items():
            off = jump_off(val)
            if off is None:
                continue
            for group, target in map_frame(blob, off):
                kids: dict[int, dict] = {}
                for e in list_offsets(blob, target):
                    rec = BT.read_nested_row(blob, e, pool)
                    if not rec:
                        continue
                    d = dict(rec["values"])
                    wid = d.get("id")
                    if wid is None:
                        continue
                    kids.setdefault(wid, {}).update(
                        {k: v for k, v in d.items() if k != "id"})
                if kids:
                    modules.setdefault((cls, group), {})[mid] = kids

    out = {"classes": {}, "stats": {"rows": len(rows), "unbound": len(unbound),
                                    "modules": 0, "pairs": len(modules)}}
    for (cls, group), mods in sorted(modules.items()):
        g = out["classes"].setdefault(cls, {})
        items = []
        for mid, kids in sorted(mods.items()):
            ws = []
            for wid, d in sorted(kids.items()):
                tex = (d.get("texture") or "").replace("\\", "/")
                png = _tex_png(tex)
                pos = vec2(blob, jump_off(d["pnl_offset"])) if "pnl_offset" in d else None
                size = vec2(blob, jump_off(d["pnl_size"])) if "pnl_size" in d else None
                if size is None and png:
                    t = _png_size(png)
                    if t:
                        size = [float(t[0]), float(t[1])]
                ws.append({
                    "id": wid,
                    "name": d.get("widget_name") or "",
                    "tex": tex,
                    "png": png,
                    "pos": pos,
                    "size": size,
                    "text": d.get("str") or "",
                    "font": d.get("font_size") or "",
                    "visible": str(d.get("visible", "1")) != "0",
                })
            items.append({"id": mid, "widgets": ws})
            out["stats"]["modules"] += 1
        g[str(group)] = items
    return out


# ───────────────────────────────────────────────────────────── 渲染
PAGE = """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>活动界面控件模块 · hd_ui_scheme_reverse</title>
<style>
:root{{--bg:#f6f7f9;--panel:#fff;--line:#e3e6ea;--ink:#1d2129;--dim:#6b7280;
--accent:#2563eb;--warn:#b45309;}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);
font:14px/1.55 "Noto Sans SC","Microsoft YaHei",system-ui,sans-serif}}
header{{padding:16px 22px;border-bottom:1px solid var(--line);background:var(--panel)}}
h1{{margin:0 0 4px;font-size:17px}}
.sub{{color:var(--dim);font-size:12.5px}}
.wrap{{display:grid;grid-template-columns:260px 1fr;gap:0;min-height:calc(100vh - 74px)}}
aside{{border-right:1px solid var(--line);background:var(--panel);padding:12px;overflow:auto;
max-height:calc(100vh - 74px)}}
aside input{{width:100%;padding:7px 9px;border:1px solid var(--line);border-radius:7px;
font:inherit;margin-bottom:10px}}
.cls{{padding:6px 8px;border-radius:7px;cursor:pointer;display:flex;justify-content:space-between;
gap:8px;font-size:13px}}
.cls:hover{{background:#eef2ff}}
.cls[aria-current="true"]{{background:var(--accent);color:#fff}}
.cls b{{font-weight:600;opacity:.75;font-size:12px}}
main{{padding:16px 20px;overflow:auto;max-height:calc(100vh - 74px)}}
.bar{{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:14px;align-items:center}}
.chip{{border:1px solid var(--line);background:var(--panel);border-radius:999px;padding:4px 11px;
font:inherit;font-size:12.5px;cursor:pointer}}
.chip[aria-pressed="true"]{{background:var(--accent);color:#fff;border-color:var(--accent)}}
.grid{{display:flex;flex-wrap:wrap;gap:14px}}
.mod{{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:10px;
box-shadow:0 1px 2px rgba(16,24,40,.05);max-width:520px}}
.mod h3{{margin:0 0 8px;font-size:12px;color:var(--dim);font-weight:600}}
.stage{{position:relative;background:
repeating-conic-gradient(#f0f2f5 0 25%,#fff 0 50%) 0 0/16px 16px;border-radius:6px;
overflow:hidden;margin-bottom:8px}}
.w{{position:absolute;overflow:hidden;font-size:11px;color:#111;display:flex;
align-items:center;justify-content:center;background-repeat:no-repeat;
background-size:100% 100%;outline:1px solid rgba(37,99,235,.16)}}
.w.txt{{background:none;outline:none;color:#1f2937;font-weight:600;white-space:nowrap}}
.rows{{display:grid;grid-template-columns:1fr 1fr;gap:2px 10px;font-size:12px}}
.rw{{display:flex;align-items:center;gap:6px;padding:2px 0;border-bottom:1px dashed #eef0f3}}
.rw img,.rw i{{width:22px;height:22px;flex:0 0 22px;object-fit:contain;border-radius:3px;
background:#f3f4f6;display:block}}
.rw span{{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.rw b{{font-weight:500;color:#374151}}
.rw em{{color:#b45309;font-style:normal}}
.more{{color:var(--dim);font-size:11.5px;margin-top:6px}}
.none{{color:var(--dim);font-size:12px}}
.note{{margin:0 0 14px;padding:10px 12px;border-left:3px solid var(--warn);background:#fffbeb;
border-radius:0 8px 8px 0;font-size:12.5px;color:#78350f}}
</style></head><body>
<header>
  <h1>活动界面「控件模块库」</h1>
  <div class="sub">数据源 <code>com/cdata/hd_ui_scheme_reverse_data.py</code>（444 KB，已解）
   ｜ 模块 <b>{n_mod}</b> ｜ 活动类 <b>{n_cls}</b> ｜ (类, ui_group) 组合 <b>{n_pair}</b>
   ｜ <span id="cur"></span>
   ｜ <a href="../composer/index.html" target="_blank" style="color:#2563eb">拖到画布拼一屏 ↗</a></div>
</header>
<div class="wrap">
  <aside><input id="q" placeholder="搜索活动类…"><div id="clist"></div></aside>
  <main>
    <p class="note"><b>这是什么</b>：活动界面由 <code>load_hd_ui_scheme(ui_group_id)</code>
    动态搭建，不是 csb。这张表给的是<b>可复用控件模块</b>（按钮组、折扣标签、任务格…），
    含每个子控件的名字、贴图、模块内坐标、文案、字号。<br>
    <b>不能当整块面板看</b>：模块之间互不嵌套，「面板由哪些模块组成 + 模块摆在哪」
    存在缺失的 <code>hd_ui_scheme_data_base</code> 里，本包没有该表。</p>
    <div class="bar" id="groups"></div>
    <div class="grid" id="mods"></div>
    <div id="empty" class="none hidden"></div>
  </main>
</div>
<script>
const DATA = {data};
let curCls = null, curGrp = null, q = '';
const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g,
  c => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}})[c]);

function sync() {{
  const u = new URL(location.href);
  u.searchParams.set('cls', curCls || '');
  u.searchParams.set('g', curGrp || '');
  history.replaceState(null, '', u);
}}

function renderList() {{
  const kw = q.trim().toLowerCase();
  const names = Object.keys(DATA.classes).filter(n => !kw || n.toLowerCase().includes(kw));
  document.getElementById('clist').innerHTML = names.map(n => {{
    const grps = Object.keys(DATA.classes[n]);
    const tot = grps.reduce((a, g) => a + DATA.classes[n][g].length, 0);
    return '<div class="cls" data-c="' + esc(n) + '" aria-current="' + (n === curCls) +
      '"><span>' + esc(n) + '</span><b>' + tot + '</b></div>';
  }}).join('') || '<div class="none">无匹配</div>';
  document.querySelectorAll('.cls').forEach(el => el.onclick = () => {{
    curCls = el.dataset.c; curGrp = Object.keys(DATA.classes[curCls])[0]; sync(); render();
  }});
}}

function renderGroups() {{
  const grps = Object.keys(DATA.classes[curCls] || {{}}).sort((a, b) => a - b);
  document.getElementById('groups').innerHTML = grps.map(g =>
    '<button class="chip" data-g="' + g + '" aria-pressed="' + (g === curGrp) + '">' +
    'ui_group ' + g + ' · ' + DATA.classes[curCls][g].length + ' 模块</button>').join('');
  document.querySelectorAll('.chip').forEach(el => el.onclick = () => {{
    curGrp = el.dataset.g; sync(); render();
  }});
}}

function renderMods() {{
  const mods = (DATA.classes[curCls] || {{}})[curGrp] || [];
  const box = document.getElementById('mods');
  box.innerHTML = mods.map(m => {{
    const ws = m.widgets;
    const placed = ws.filter(w => w.pos);
    let x0 = 0, y0 = 0, x1 = 1, y1 = 1;
    placed.forEach(w => {{
      const s = w.size || [40, 40];
      x0 = Math.min(x0, w.pos[0]); x1 = Math.max(x1, w.pos[0] + s[0]);
      y1 = Math.max(y1, w.pos[1]); y0 = Math.min(y0, w.pos[1] - s[1]);
    }});
    const pad = 6, W = Math.max(140, x1 - x0 + pad * 2), H = Math.max(70, y1 - y0 + pad * 2);
    const inner = placed.map(w => {{
      const s = w.size || [40, 40];
      const L = w.pos[0] - x0 + pad, T = (y1 - w.pos[1]) + pad;
      const st = ['left:' + L.toFixed(1) + 'px', 'top:' + T.toFixed(1) + 'px',
        'width:' + s[0].toFixed(1) + 'px', 'height:' + s[1].toFixed(1) + 'px'];
      if (w.png) st.push('background-image:url(../assets/' + w.png + ')');
      const isTxt = !!w.text;
      const fs = w.font ? 'font-size:' + Math.min(22, Number(w.font) || 12) + 'px;' : '';
      return '<div class="w' + (isTxt ? ' txt' : '') + '" title="' + esc(w.name) +
        '" style="' + st.join(';') + ';' + fs + '">' + (isTxt ? esc(w.text) : '') + '</div>';
    }}).join('');
    const rows = ws.slice(0, 60).map(w => {{
      const ic = w.png ? '<img src="../assets/' + w.png + '" alt="">' : '<i></i>';
      const tx = w.text ? ' <em>' + esc(w.text) + '</em>' : '';
      return '<div class="rw" title="' + esc(w.tex || w.name) + '">' + ic +
        '<span><b>' + esc(w.name || ('#' + w.id)) + '</b>' + tx + '</span></div>';
    }}).join('');
    const more = ws.length > 60 ? '<div class="more">另有 ' + (ws.length - 60) +
      ' 个控件未列出</div>' : '';
    return '<div class="mod"><h3>模块 #' + m.id + ' · ' + ws.length + ' 控件 · ' +
      '带坐标 ' + placed.length + ' 个 · 画布 ' + W.toFixed(0) + '×' + H.toFixed(0) +
      '</h3>' +
      (placed.length ? '<div class="stage" style="width:' + W.toFixed(0) + 'px;height:' +
        H.toFixed(0) + 'px">' + inner + '</div>' : '') +
      '<div class="rows">' + rows + '</div>' + more + '</div>';
  }}).join('');
  document.getElementById('empty').textContent = mods.length ? '' : '该组无模块';
  document.getElementById('cur').textContent = curCls ? curCls + ' · ui_group ' + curGrp : '';
}}

function render() {{
  renderList();
  if (!curCls) return;
  renderGroups();
  renderMods();
}}
document.getElementById('q').oninput = e => {{ q = e.target.value; renderList(); }};
const P = new URLSearchParams(location.search);
if (P.get('cls') && DATA.classes[P.get('cls')]) {{
  curCls = P.get('cls');
  const g = P.get('g');
  curGrp = (g && DATA.classes[curCls][g]) ? g : Object.keys(DATA.classes[curCls])[0];
}} else {{
  const first = Object.keys(DATA.classes)[0];
  if (first) {{ curCls = first; curGrp = Object.keys(DATA.classes[first])[0]; }}
}}
render();
</script></body></html>
"""


def build_page(data: dict) -> pathlib.Path:
    OUT.mkdir(parents=True, exist_ok=True)
    n_mod = sum(len(v) for g in data["classes"].values() for v in g.values())
    page = PAGE.format(
        n_mod=n_mod, n_cls=len(data["classes"]), n_pair=data["stats"]["pairs"],
        data=json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    out = OUT / "index.html"
    out.write_text(page, encoding="utf-8")
    return out


def main(argv: list[str]) -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    js = OUT / "scheme.json"
    if "--from-json" in argv:                 # 只重出页面，不重解表（改模板时用）
        data = json.loads(js.read_text(encoding="utf-8"))
        print("复用 %s" % js)
        print("  页面 → %s" % build_page(data))
        return 0
    print("解 hd_ui_scheme_reverse …")
    data = extract()
    js.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print("  JSON → %s（%d 类 / %d 组）" % (OUT / "scheme.json",
                                        len(data["classes"]), data["stats"]["pairs"]))
    if "--dump-only" in argv:
        return 0
    out = build_page(data)
    print("  页面 → %s" % out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
