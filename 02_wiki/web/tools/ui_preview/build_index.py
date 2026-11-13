# -*- coding: utf-8 -*-
"""汇总 _ui_preview 下已导出的面板 → 一个本地入口页。

数据全部来自产物本身：每个面板的 .meta.json、thumbs/*.png，以及
02_wiki/web/data/boards/activity_master.json（只读）。

CLI
  build_index.py
"""
from __future__ import annotations

import html
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import la_paths  # noqa: E402

PROJ = la_paths.find_project_root()
OUT_ROOT = PROJ / "_ui_preview"
THUMB_DIR = OUT_ROOT / "thumbs"
ACTIVITY_MASTER = PROJ / "02_wiki/web/data/boards/activity_master.json"
CANDIDATES = HERE / "activity_panel_candidates.json"
SCHEME_JSON = OUT_ROOT / "scheme/scheme.json"
CD = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata"


def load_ui_group() -> dict[int, str]:
    """huodong_conf 行键 → ui_group_id（活动界面按它取 scheme）。

    走与 build_activity_master 相同的 mini-VM；失败就返回空，页面自动降级。
    """
    src = CD / "huodong_conf_data.py"
    if not src.is_file():
        return {}
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("vm_cdata_table",
                                                      HERE.parent / "vm_cdata_table.py")
        vm = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(vm)
        sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
        from toolkit_core import script_decode as SD
        _r, code, _e = SD.load_module(str(src))
        vm.run(code)
        out = {}
        for k, v in vm.MAPADD:
            if isinstance(v, dict) and v.get("ui_group_id") not in (None, ""):
                out[k] = str(v["ui_group_id"])
        return out
    except Exception as exc:                                  # noqa: BLE001
        print("  ⚠ ui_group_id 不可用（%s）" % exc)
        return {}


# 面板名前缀 → 中文分类。前缀取第一个下划线之前的部分，规则可复算。
CATEGORY = {
    "choujiang": "活动·抽奖", "huancai": "活动·抽奖", "activity": "活动·抽奖",
    "huodong": "活动·抽奖", "yunying": "活动·抽奖", "xinhuodong": "活动·抽奖",
    "hd": "活动·抽奖", "guoqing": "活动·抽奖", "yuanxiao": "活动·抽奖",
    "xiari": "活动·抽奖", "yingdi": "活动·抽奖", "baozhi": "活动·抽奖",
    "shizhuang": "时装", "shangcheng": "商店", "store": "商店",
    "shichao": "时装", "chenghao": "称号", "charm": "时装",
    "dianfengsaishi": "赛事", "zhengbasai": "赛事", "pvp": "赛事",
    "xiaer": "赛事", "zhanshen": "联动", "liandong": "联动",
    "main": "界面框架", "map": "界面框架", "tab": "界面框架",
    "common": "界面框架", "chat": "聊天", "control": "界面框架",
    "menu": "界面框架", "login": "界面框架", "inventory": "界面框架",
    "mail": "界面框架", "proto": "界面框架", "a": "场景",
    "fuben": "玩法", "gongfang": "玩法", "jixun": "玩法", "pata": "玩法",
    "haidiao": "玩法", "smugging": "玩法", "city": "玩法", "zaiju": "玩法",
    "zhuangyuan": "玩法", "recipe": "玩法", "worktable": "玩法",
    "weapon": "玩法", "texunzhanchang": "玩法", "baozang": "玩法",
    "guizi": "玩法", "chuwuxiang": "玩法", "nitai": "玩法", "chahua": "玩法",
    "yihua": "玩法", "daomoshi": "玩法", "daoju": "玩法", "team": "玩法",
    "tongxingzheng": "成长", "tongxingzhng": "成长", "yuekafu": "成长",
    "jishou": "成长", "richeng": "成长", "siyuwu": "成长", "ugc": "成长",
    "task": "界面框架", "shututonggui": "商店", "goumai": "商店",
}


def category_of(stem: str) -> str:
    return CATEGORY.get(stem.split("_")[0], "其他")


def collect_panels() -> list[dict]:
    rows = []
    for meta_file in sorted(OUT_ROOT.glob("*/*.meta.json")):
        try:
            m = json.loads(meta_file.read_text(encoding="utf-8"))
        except Exception:                                     # noqa: BLE001
            continue
        stem = meta_file.name[: -len(".meta.json")]
        if not (OUT_ROOT / stem / (stem + ".html")).exists():
            continue
        by_class = m.get("by_class") or {}
        rows.append({
            "stem": stem,
            "w": int(m["stage"][0]),
            "h": int(m["stage"][1]),
            "nodes": m.get("nodes", 0),
            "tex": m.get("textures", 0),
            "miss": len(m.get("missing_textures") or []),
            "state": m.get("state_hidden", 0),
            "cat": category_of(stem),
            "thumb": stem + ".png" if (THUMB_DIR / (stem + ".png")).exists() else "",
            "images": by_class.get("ImageView", 0) + by_class.get("Sprite", 0),
            "texts": by_class.get("Text", 0) + by_class.get("TextBMFont", 0),
        })
    return rows


def collect_activities() -> list[dict]:
    if not ACTIVITY_MASTER.exists():
        return []
    data = json.loads(ACTIVITY_MASTER.read_text(encoding="utf-8"))
    cand = {}
    if CANDIDATES.exists():
        cand = json.loads(CANDIDATES.read_text(encoding="utf-8")).get("map") or {}
    out = []
    groups = load_ui_group()
    scheme = {}
    if SCHEME_JSON.exists():
        scheme = (json.loads(SCHEME_JSON.read_text(encoding="utf-8"))
                  .get("classes") or {})
    n_scheme = 0
    for it in data["items"]:
        if it.get("activity_status") != "未开始":
            continue
        tech = (it.get("provenance") or {}).get("tech") or {}
        c = cand.get(str(it.get("item_id"))) or {}
        cls = tech.get("hd_class") or ""
        grp = groups.get(it.get("item_id")) or ""
        cg = scheme.get(cls) or {}
        if grp and grp in cg:                 # 配置里标了 ui_group_id：精确到组
            mods = len(cg[grp])
            glabel = "ui_group " + grp
        elif cg:                              # 没标组号：给整类的变体，页面里自己切
            mods = sum(len(v) for v in cg.values())
            glabel = "%d 组变体" % len(cg)
        else:
            mods, glabel = 0, ""
        if mods:
            n_scheme += 1
        out.append({
            "id": it.get("item_id"),
            "name": it.get("name") or "",
            "start": it.get("start") or "",
            "end": it.get("end") or "",
            "hdClass": cls,
            "hdType": tech.get("hd_type") or "",
            "uiClass": tech.get("ui_class") or "",
            "subTitle": it.get("sub_title") or "",
            "actType": it.get("activity_type") or "",
            "tab": it.get("first_level_tab") or "",
            "grp": grp if (grp and grp in cg) else "",
            "mods": mods,
            "glabel": glabel,
            "panels": c.get("panels") or [],
            "conf": c.get("confidence") or "",
            "evidence": c.get("evidence") or "",
        })
    out.sort(key=lambda r: (r["start"] or "9999", r["id"] or 0))
    print("  控件模块可看：%d / %d 条活动" % (n_scheme, len(out)))
    return out


def build(panels: list[dict], acts: list[dict]) -> pathlib.Path:
    cats = sorted({p["cat"] for p in panels},
                  key=lambda c: (-sum(1 for p in panels if p["cat"] == c), c))
    n_miss = sum(1 for p in panels if p["miss"])
    n_thumb = sum(1 for p in panels if p["thumb"])
    n_cand = sum(1 for a in acts if a["panels"])
    n_sch = sum(1 for a in acts if a.get("mods"))
    chips = "".join(
        f'<button class="chip" data-cat="{html.escape(c)}" aria-pressed="false">'
        f'{html.escape(c)}<b>{sum(1 for p in panels if p["cat"] == c)}</b></button>'
        for c in cats)
    data = json.dumps({"panels": panels, "acts": acts},
                      ensure_ascii=False, separators=(",", ":"))
    page = TEMPLATE.format(
        n_panel=len(panels), n_thumb=n_thumb, n_act=len(acts),
        n_miss=n_miss, n_cand=n_cand, n_sch=n_sch, chips=chips, data=data)
    out = OUT_ROOT / "index.html"
    out.write_text(page, encoding="utf-8")
    print(f"入口页 → {out}")
    print(f"  面板 {len(panels)}（缩略图 {n_thumb}，缺贴图 {n_miss}）")
    print(f"  未上线活动 {len(acts)}（有候选面板 {n_cand}，可看控件模块 {n_sch}）")
    return out


TEMPLATE = """<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>界面还原 · 本地入口</title>
<style>
:root {{ color-scheme: dark; }}
* {{ box-sizing: border-box; }}
body {{ margin:0; background:#13151a; color:#e6e9ee;
  font:400 13px/1.55 "Noto Sans SC","Microsoft YaHei",system-ui,sans-serif; }}
header {{ position:sticky; top:0; z-index:20; background:rgba(20,23,28,.97);
  border-bottom:1px solid #282d36; padding:12px 20px 10px; }}
.top {{ display:flex; gap:16px; align-items:baseline; flex-wrap:wrap; }}
h1 {{ font-size:16px; font-weight:600; margin:0; }}
.sub {{ color:#8b94a3; font-size:12px; }}
.sub b {{ color:#d6dbe4; font-weight:600; }}
.tools {{ display:flex; gap:8px; align-items:center; flex-wrap:wrap;
  margin-top:10px; }}
input[type=search] {{ background:#1b1f26; border:1px solid #303743;
  color:#e6e9ee; border-radius:7px; padding:6px 10px; font-size:13px;
  width:250px; }}
input[type=search]:focus {{ outline:none; border-color:#3f8cff; }}
select {{ background:#1b1f26; border:1px solid #303743; color:#d6dbe4;
  border-radius:7px; padding:6px 8px; font-size:12px; }}
.tabs {{ display:flex; gap:6px; }}
.tab {{ background:#1b1f26; border:1px solid #303743; color:#b7c0cd;
  border-radius:7px; padding:6px 14px; font-size:12.5px; cursor:pointer;
  text-decoration:none; display:inline-flex; align-items:center; line-height:1.2; }}
.tab[aria-selected=true] {{ background:#2f6feb; border-color:#2f6feb; color:#fff; }}
.chips {{ display:flex; gap:6px; flex-wrap:wrap; margin-top:8px; }}
.chip {{ background:#1b1f26; border:1px solid #2c323c; color:#9fa8b6;
  border-radius:999px; padding:3px 10px; font-size:12px; cursor:pointer; }}
.chip b {{ color:#7e8794; font-weight:500; margin-left:5px; font-size:11px; }}
.chip[aria-pressed=true] {{ background:#233a5e; border-color:#3f6fb5;
  color:#dbe7f8; }}
.chip[aria-pressed=true] b {{ color:#9dc0f0; }}
main {{ padding:16px 20px 60px; }}
#grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(228px,1fr));
  gap:14px; }}
.card {{ background:#191d24; border:1px solid #272c35; border-radius:10px;
  overflow:hidden; text-decoration:none; color:inherit; display:flex;
  flex-direction:column; transition:border-color .15s, transform .15s; }}
.card:hover {{ border-color:#3f6fb5; transform:translateY(-1px); }}
.card .shot {{ background:#0f1216; aspect-ratio:16/9; overflow:hidden;
  display:flex; align-items:center; justify-content:center; }}
.card .shot img {{ width:100%; height:100%; object-fit:contain; }}
.card .shot .none {{ color:#4b5563; font-size:11px; }}
.card .body {{ padding:8px 10px 10px; display:flex; flex-direction:column;
  gap:4px; }}
.card .nm {{ font-size:12.5px; color:#dfe5ee; word-break:break-all;
  line-height:1.35; }}
.card .meta {{ display:flex; gap:8px; color:#7d8794; font-size:11px;
  flex-wrap:wrap; }}
.badge {{ border-radius:4px; padding:0 5px; font-size:10.5px;
  border:1px solid #333a45; color:#8f99a6; }}
.badge.warn {{ border-color:#7a4a1f; color:#e0a166; }}
.badge.cat {{ border-color:#2f4a6f; color:#8fb6e6; }}
table {{ width:100%; border-collapse:collapse; font-size:12.5px; }}
th, td {{ text-align:left; padding:8px 10px; border-bottom:1px solid #252a33;
  vertical-align:top; }}
th {{ color:#8b94a3; font-weight:500; font-size:11.5px; background:#13151a;
  position:sticky; top:98px; }}
td.nm {{ color:#e6e9ee; white-space:nowrap; }}
.mono {{ font-family:ui-monospace,Consolas,monospace; font-size:11.5px;
  color:#8894a4; }}
.link {{ color:#6fa8ff; text-decoration:none; }}
.link:hover {{ text-decoration:underline; }}
.none-txt {{ color:#5b6472; }}
.note {{ color:#8b94a3; font-size:11.5px; line-height:1.75;
  border-top:1px solid #252a33; margin-top:26px; padding-top:14px; }}
.note code {{ color:#a9b6c7; }}
.hidden {{ display:none !important; }}
#empty {{ color:#7d8794; padding:40px 0; text-align:center; }}
</style></head>
<body>
<header>
  <div class="top">
    <h1>界面还原 · 本地入口</h1>
    <span class="sub">CSB 面板 <b>{n_panel}</b> ｜ 缩略图 <b>{n_thumb}</b> ｜
      缺贴图 <b>{n_miss}</b> ｜ 未上线活动 <b>{n_act}</b> ｜
      有候选面板 <b>{n_cand}</b>（名称语义）｜ 可看控件模块 <b>{n_sch}</b></span>
  </div>
  <div class="tools">
    <div class="tabs" role="tablist">
      <button class="tab" id="tab-panel" role="tab" aria-selected="true">面板</button>
      <button class="tab" id="tab-act" role="tab" aria-selected="false">未上线活动</button>
      <a class="tab" href="composer/index.html" target="_blank"
        title="把控件模块拖到画布，手工拼一屏">拼装器 ↗</a>
    </div>
    <input type="search" id="q" placeholder="搜索面板名 / 活动名 / 类名">
    <select id="sort">
      <option value="name">按名称</option>
      <option value="nodes">按节点数</option>
      <option value="miss">按缺贴图</option>
    </select>
    <label class="sub" id="missLabel"><input type="checkbox" id="onlyMiss"> 只看缺贴图</label>
  </div>
  <div class="chips" id="chips">{chips}</div>
</header>
<main>
  <div id="grid"></div>
  <div id="table" class="hidden"></div>
  <div id="empty" class="hidden">没有匹配项</div>
  <div class="note">
    <b>口径</b>：布局、贴图、文案全部来自
    <code>41_还原树/pe/资源/ui/*.csb</code> 与同目录 <code>.ktx</code>，未做人工调整。
    文字用系统字近似（原为位图字体）；时间轴取入场动画的<b>末帧</b>稳定态；
    同一控件的常态/按下/禁用贴图默认只显示常态，隐藏数量见卡片「状态」，页面内可叠回。<br>
    <b>缺贴图</b>：CSB 引用了 <code>.png</code> 但本地没有对应 <code>.ktx</code>，
    按缺图处理，不补假图。<br>
    <b>未上线活动</b>：<code>activity_master.json</code> 的「未开始」条目。
    这类活动的界面<b>不是 csb 面板</b>，而是由 <code>ui_class</code> 脚本调用
    <code>load_hd_ui_scheme(ui_group_id)</code> <b>动态搭建</b>；布局表
    <code>hd_ui_scheme_data_base</code> <b>不在本包内</b>（全树检索 0 命中）。
    四条独立验证均落空（详见 <code>ACTIVITY_PANEL_EVIDENCE.md</code>），
    因此活动与面板的对应只能按<b>名称语义候选</b>展示并写明依据；没有依据的标「无」，不硬凑。
  </div>
</main>
<script>
const DATA = {data};
let curCat = null, onlyMiss = false, q = '', sortBy = 'name', view = 'panel';

const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g,
  c => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}})[c]);

function panelCard(p) {{
  const thumb = p.thumb
    ? '<img loading="lazy" src="thumbs/' + esc(p.thumb) + '" alt="">'
    : '<span class="none">无缩略图</span>';
  const miss = p.miss ? '<span class="badge warn">缺 ' + p.miss + '</span>' : '';
  return '<a class="card" href="' + esc(p.stem) + '/' + esc(p.stem) + '.html" target="_blank">' +
    '<div class="shot">' + thumb + '</div>' +
    '<div class="body">' +
      '<div class="nm">' + esc(p.stem) + '</div>' +
      '<div class="meta"><span class="badge cat">' + esc(p.cat) + '</span>' +
        '<span>' + p.w + '×' + p.h + '</span>' +
        '<span>' + p.nodes + ' 节点</span>' + miss + '</div>' +
      '<div class="meta"><span>贴图 ' + p.tex + '</span>' +
        '<span>状态 ' + p.state + '</span>' +
        '<span>图 ' + p.images + ' / 字 ' + p.texts + '</span></div>' +
    '</div></a>';
}}

function renderPanels() {{
  const kw = q.trim().toLowerCase();
  const rows = DATA.panels.filter(p =>
    (!curCat || p.cat === curCat) && (!onlyMiss || p.miss > 0) &&
    (!kw || p.stem.toLowerCase().includes(kw)));
  const cmp = {{
    name: (a, b) => a.stem.localeCompare(b.stem),
    nodes: (a, b) => b.nodes - a.nodes,
    miss: (a, b) => b.miss - a.miss || a.stem.localeCompare(b.stem),
  }}[sortBy];
  rows.sort(cmp);
  document.getElementById('grid').innerHTML = rows.map(panelCard).join('');
  document.getElementById('empty').classList.toggle('hidden', rows.length > 0);
}}

function renderActs() {{
  const kw = q.trim().toLowerCase();
  const rows = DATA.acts.filter(a => !kw ||
    (a.name + a.hdClass + a.hdType + a.uiClass).toLowerCase().includes(kw));
  const body = rows.map(a => {{
    let cell = '';
    if (a.mods) {{
      let href = 'scheme/index.html?cls=' + encodeURIComponent(a.hdClass);
      if (a.grp) href += '&g=' + encodeURIComponent(a.grp);
      cell += '<div><a class="link" target="_blank" href="' + href + '">' +
        '控件模块 · ' + a.mods + ' 个 →</a>' +
        '<span class="none-txt"> ' + esc(a.glabel) + '</span></div>';
    }}
    let nameCell = esc(a.name);
    if (a.panels.length) {{
      nameCell = '<a class="link" target="_blank" href="' + esc(a.panels[0]) +
        '/' + esc(a.panels[0]) + '.html">' + esc(a.name) + '</a>';
      cell += a.panels.slice(0, 4).map(n =>
        '<a class="link" target="_blank" href="' + esc(n) + '/' + esc(n) +
        '.html">' + esc(n) + '</a>').join('<br>');
      cell += '<div class="none-txt" style="margin-top:4px">' +
        '<span class="badge ' + (a.conf === 'strong' ? '' : 'warn') + '">' +
        esc(a.conf) + '</span> ' + esc(a.evidence) + '</div>';
    }} else if (!a.mods) {{
      cell += '<span class="none-txt">界面由 <code>load_hd_ui_scheme</code>' +
        '（<code>ui_group_id</code>）动态搭建，该表不在本包 · 无面板可对应</span>';
    }}
    return '<tr>' +
      '<td class="mono">' + a.id + '</td>' +
      '<td class="nm">' + nameCell +
        (a.subTitle ? '<div class="none-txt">' + esc(a.subTitle) + '</div>' : '') + '</td>' +
      '<td class="mono" style="white-space:nowrap">' + esc(a.start) + '<br>' + esc(a.end) + '</td>' +
      '<td>' + esc(a.hdType) + '<div class="mono">' + esc(a.hdClass) + '</div></td>' +
      '<td class="mono">' + (esc(a.uiClass) || '—') +
        (a.tab ? '<div class="none-txt">' + esc(a.tab) + '</div>' : '') + '</td>' +
      '<td>' + cell + '</td></tr>';
  }}).join('');
  document.getElementById('table').innerHTML =
    '<table><thead><tr><th>ID</th><th>活动 / 副标题</th><th>时间</th>' +
    '<th>活动类型 / 类名</th><th>界面类</th><th>面板对应</th></tr></thead>' +
    '<tbody>' + body + '</tbody></table>';
  document.getElementById('empty').classList.toggle('hidden', rows.length > 0);
}}

function render() {{
  const isPanel = view === 'panel';
  document.getElementById('grid').classList.toggle('hidden', !isPanel);
  document.getElementById('table').classList.toggle('hidden', isPanel);
  document.getElementById('chips').style.display = isPanel ? '' : 'none';
  document.getElementById('sort').style.display = isPanel ? '' : 'none';
  document.getElementById('missLabel').style.display = isPanel ? '' : 'none';
  if (isPanel) renderPanels(); else renderActs();
}}

function setTab(v) {{
  view = v;
  document.getElementById('tab-panel').setAttribute('aria-selected', String(v === 'panel'));
  document.getElementById('tab-act').setAttribute('aria-selected', String(v === 'act'));
  render();
}}
document.getElementById('tab-panel').addEventListener('click', () => setTab('panel'));
document.getElementById('tab-act').addEventListener('click', () => setTab('act'));
document.getElementById('q').addEventListener('input', e => {{ q = e.target.value; render(); }});
document.getElementById('sort').addEventListener('change', e => {{ sortBy = e.target.value; render(); }});
document.getElementById('onlyMiss').addEventListener('change', e => {{ onlyMiss = e.target.checked; render(); }});
document.getElementById('chips').addEventListener('click', e => {{
  const b = e.target.closest('.chip');
  if (!b) return;
  curCat = (curCat === b.dataset.cat) ? null : b.dataset.cat;
  document.querySelectorAll('.chip').forEach(x =>
    x.setAttribute('aria-pressed', String(x.dataset.cat === curCat)));
  render();
}});
render();
if (new URLSearchParams(location.search).get('view') === 'act') setTab('act');
</script>
</body></html>
"""


def main() -> int:
    panels = collect_panels()
    if not panels:
        print("_ui_preview 下没有面板产物，先跑 export_all.py")
        return 2
    build(panels, collect_activities())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
