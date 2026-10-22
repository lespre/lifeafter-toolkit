# -*- coding: utf-8 -*-
"""生成 3 个 wiki 首页布局方案（真实数据抽样），供用户挑选。"""
import json
import pathlib
import random

WEB = pathlib.Path(r"E:/la拆包项目/02_wiki/web")
OUT = WEB / "design"
OUT.mkdir(exist_ok=True)

d = json.loads((WEB / "data/boards/fashion_wardrobe.json").read_text(encoding="utf-8"))
items = [i for i in d["items"] if (i.get("_media") or {}).get("images")]
random.seed(7)
sample = random.sample(items, 18)

def icon(it):
    im = it["_media"]["images"][0]
    return im.get("png") or im.get("src") or ""

def grade(it):
    g = it.get("grade_level") or it.get("grade") or ""
    return str(g)

cards = []
for it in sample:
    cards.append({
        "name": (it.get("name") or "")[:14],
        "part": it.get("part") or "",
        "charm": it.get("charm_value") or 0,
        "icon": icon(it),
        "grade": grade(it),
    })

DATA = json.dumps(cards, ensure_ascii=False)

BASE_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:"Microsoft YaHei","PingFang SC",system-ui,sans-serif;background:#0c0e12;color:#e8ecf2}
img{display:block}
a{color:inherit;text-decoration:none}
"""

# ---------------- 方案 A：档案馆（密集卡片网格） ----------------
A = """<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8"><title>方案A · 档案馆</title>
<style>{BASE_CSS}
.top{display:flex;align-items:center;gap:18px;padding:1px 22px;border-bottom:1px solid #1d232c;background:#0f1319}
.brand{font-weight:800;letter-spacing:.12em;font-size:14px;padding:14px 0}
.brand em{font-style:normal;color:#5d6b7c;font-size:10px;letter-spacing:.28em;margin-left:8px}
nav{display:flex;gap:2px;flex:1}
nav a{padding:14px 12px;font-size:12.5px;color:#9aa7b6;border-bottom:2px solid transparent}
nav a.on{color:#fff;border-bottom-color:#c0392b}
.search{background:#121821;border:1px solid #232c38;border-radius:3px;padding:7px 10px;color:#cfd8e3;font-size:12px;width:220px}
.wrap{display:grid;grid-template-columns:186px 1fr;gap:20px;max-width:1320px;margin:0 auto;padding:18px 20px 50px}
aside{font-size:12.5px}
aside h4{font-size:10px;letter-spacing:.22em;color:#5d6b7c;margin:4px 0 8px}
aside a{display:flex;justify-content:space-between;padding:6px 8px;color:#9aa7b6;border-left:2px solid transparent}
aside a.on{color:#fff;background:#151b24;border-left-color:#c0392b}
aside a i{font-style:normal;color:#55637a;font-size:10.5px}
.chips{display:flex;gap:6px;flex-wrap:wrap;margin:2px 0 14px}
.chip{padding:4px 9px;border:1px solid #26303d;border-radius:2px;font-size:11.5px;color:#94a3b3;background:#11161e}
.chip.on{border-color:#c0392b;color:#fff;background:#1b1412}
h2.sec{font-size:15px;letter-spacing:.1em;margin:16px 0 10px;padding-bottom:8px;border-bottom:1px solid #1e2631;color:#eef3f8}
h2.sec span{color:#c0392b;font-size:11px;margin-left:8px;letter-spacing:.16em}
h3.sub{font-size:12px;color:#8f9dad;margin:14px 0 8px;display:flex;gap:7px;align-items:center}
h3.sub::before{content:"";width:3px;height:11px;background:#c0392b}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:8px}
.card{background:#11161d;border:1px solid #1e2631;border-radius:3px;padding:8px;display:flex;gap:9px;align-items:center;transition:.15s}
.card:hover{border-color:#c0392b;background:#151c25;transform:translateY(-1px)}
.card img{width:48px;height:48px;object-fit:contain;background:#0a0e13;border:1px solid #1b232e;border-radius:2px}
.card .n{font-size:12px;font-weight:700;line-height:1.35;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.card .m{font-size:10.5px;color:#6b7a8b;margin-top:3px}
.tag{display:inline-block;font-size:10px;padding:1px 5px;border:1px solid #2a3542;color:#8fa1b3;border-radius:2px;margin-right:4px}
</style></head><body>
<div class="top">
  <div class="brand">明日之后 · 资料档案馆<em>ARCHIVE</em></div>
  <nav><a class="on">置顶、预告专栏</a><a>一、时装类</a><a>二、战力类</a><a>三、活动奖池</a><a>四、综合资料</a></nav>
  <input class="search" placeholder="搜索：时装 / 皮肤 / 核芯">
</div>
<div class="wrap">
  <aside>
    <h4>资料分类</h4>
    <a class="on">一 时装类 <i>5</i></a><a>（一）人物时装 <i>1623</i></a><a>（二）武器皮肤 <i>122</i></a>
    <a>（三）载具 <i>205</i></a><a>（四）击败播报 <i>38</i></a><a>（五）头像·框·名片 <i>673</i></a>
    <a>二 战力类 <i>9</i></a><a>三 活动奖池 <i>2</i></a><a>四 综合资料 <i>11</i></a>
  </aside>
  <main>
    <h2 class="sec">一、时装类 /（一）人物时装<span>1,623 条</span></h2>
    <div class="chips">
      <span class="chip on">全部 1623</span><span class="chip">头饰 67</span><span class="chip">衣服 372</span>
      <span class="chip">套装 435</span><span class="chip">背包 263</span><span class="chip">挂饰 124</span>
      <span class="chip">面饰 77</span><span class="chip">发饰 105</span><span class="chip">投影 43</span><span class="chip">光源 121</span>
    </div>
    <h3 class="sub">（一）人物时装</h3>
    <div class="grid" id="g"></div>
  </main>
</div>
<script>
const D=%DATA%;
document.getElementById('g').innerHTML=D.map(d=>`<a class="card"><img src="/${d.icon}" onerror="this.style.opacity=.15"><div><div class="n">${d.name}</div><div class="m"><span class="tag">${d.part||'—'}</span>魅力 ${d.charm}</div></div></a>`).join('');
</script></body></html>"""

# ---------------- 方案 B：数据库（三栏 + 表格） ----------------
B = """<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8"><title>方案B · 数据库</title>
<style>{BASE_CSS}
body{background:#f6f7f9;color:#1d2430}
.top{display:flex;align-items:center;gap:20px;padding:0 20px;background:#14181f;color:#e8ecf2}
.brand{font-weight:800;font-size:14px;padding:13px 0;letter-spacing:.1em}
.top input{margin-left:auto;width:280px;padding:7px 10px;border-radius:3px;border:1px solid #2b333f;background:#0e1218;color:#dbe3ec;font-size:12px}
.tabs{display:flex;gap:1px;background:#14181f;padding:0 20px;color:#8c9aab;font-size:12.5px}
.tabs a{padding:9px 14px;border-bottom:2px solid transparent}
.tabs a.on{color:#fff;border-bottom-color:#e0a83f}
.wrap{display:grid;grid-template-columns:220px minmax(0,1fr) 320px;gap:0;height:calc(100vh - 92px)}
.filters{background:#fff;border-right:1px solid #e3e6ec;padding:14px}
.filters h4{font-size:11px;letter-spacing:.16em;color:#7a8798;margin:12px 0 7px}
.filters label{display:flex;gap:7px;align-items:center;font-size:12.5px;color:#3b4757;padding:4px 0}
.list{overflow:auto;background:#fff}
table{width:100%;border-collapse:collapse;font-size:12.5px}
th{position:sticky;top:0;background:#eef1f5;color:#5d6b7c;font-weight:600;text-align:left;padding:9px 10px;font-size:11.5px;letter-spacing:.06em;border-bottom:1px solid #e3e6ec}
td{padding:8px 10px;border-bottom:1px solid #eef1f5}
tr:hover td{background:#f2f6fb}
td img{width:34px;height:34px;object-fit:contain;background:#fafbfc;border:1px solid #e6e9ef;border-radius:3px}
.detail{background:#fff;border-left:1px solid #e3e6ec;padding:16px;overflow:auto}
.detail h3{font-size:15px;margin-bottom:6px}
.kv{display:grid;grid-template-columns:76px 1fr;gap:6px 8px;font-size:12.5px;color:#48566a;margin-top:10px}
.kv b{color:#8b97a8;font-weight:600}
</style></head><body>
<div class="top"><div class="brand">明日之后 · 数据库</div><input placeholder="搜索条目 / 编号 / 名称…"></div>
<div class="tabs"><a class="on">人物时装</a><a>武器皮肤</a><a>载具</a><a>核芯</a><a>道具总表</a></div>
<div class="wrap">
  <div class="filters">
    <h4>部位</h4>
    <label><input type="checkbox" checked>头饰 (67)</label><label><input type="checkbox" checked>衣服 (372)</label>
    <label><input type="checkbox">整套 (435)</label><label><input type="checkbox">背包 (263)</label>
    <label><input type="checkbox">挂饰 (124)</label><label><input type="checkbox">面饰 (77)</label>
    <label><input type="checkbox">发饰 (105)</label><label><input type="checkbox">投影 (43)</label>
    <h4>品级</h4>
    <label><input type="checkbox">典藏</label><label><input type="checkbox">传世</label><label><input type="checkbox">稀有</label>
    <h4>魅力值</h4>
    <label><input type="range" min="0" max="2000" value="0"> ≥ 0</label>
  </div>
  <div class="list">
    <table><thead><tr><th>图</th><th>编号</th><th>名称</th><th>部位</th><th>魅力值</th><th>品级</th></tr></thead>
    <tbody id="tb"></tbody></table>
  </div>
  <div class="detail">
    <h3 id="dn">选择一个条目</h3>
    <div class="kv" id="dkv"><b>提示</b><span>点左侧表格的行，这里显示详情</span></div>
  </div>
</div>
<script>
const D=%DATA%;
const tb=document.getElementById('tb');
tb.innerHTML=D.map((d,i)=>`<tr onclick="pick(${i})"><td><img src="/${d.icon}" onerror="this.style.opacity=.12"></td><td>${1000+i}</td><td>${d.name}</td><td>${d.part}</td><td>${d.charm}</td><td>${d.grade||'—'}</td></tr>`).join('');
function pick(i){const d=D[i];document.getElementById('dn').textContent=d.name;
document.getElementById('dkv').innerHTML=`<b>部位</b><span>${d.part}</span><b>魅力值</b><span>${d.charm}</span><b>品级</b><span>${d.grade||'—'}</span><b>图标</b><span><img src="/${d.icon}" style="width:64px"></span>`;}
</script></body></html>"""

# ---------------- 方案 C：图鉴墙（大图卡片） ----------------
C = """<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8"><title>方案C · 图鉴墙</title>
<style>{BASE_CSS}
body{background:radial-gradient(1200px 500px at 70% -10%,rgba(120,150,180,.10),transparent 60%),#0a0d12}
.top{display:flex;align-items:center;gap:16px;padding:0 24px;border-bottom:1px solid #1b222c}
.brand{font-size:15px;font-weight:800;letter-spacing:.14em;padding:15px 0}
.top nav{display:flex;gap:4px;margin-left:26px}
.top nav a{padding:8px 12px;font-size:12.5px;color:#93a1b2;border-radius:3px}
.top nav a.on{background:#171e28;color:#fff}
.hero{max-width:1360px;margin:0 auto;padding:26px 24px 8px}
.hero h1{font-size:26px;letter-spacing:.08em}
.hero p{color:#7f8da0;font-size:12.5px;margin-top:8px}
.wall{max-width:1360px;margin:0 auto;padding:8px 24px 60px}
h3.g{font-size:13px;color:#a9b7c7;margin:22px 0 10px;letter-spacing:.1em;display:flex;align-items:center;gap:10px}
h3.g:after{content:"";flex:1;height:1px;background:#1b222c}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(168px,1fr));gap:12px}
.tile{position:relative;border:1px solid #1c2531;border-radius:6px;overflow:hidden;background:linear-gradient(180deg,#121821,#0d1219);transition:.18s}
.tile:hover{transform:translateY(-3px);border-color:#3a4b60;box-shadow:0 14px 30px rgba(0,0,0,.55)}
.tile .ph{height:132px;display:flex;align-items:center;justify-content:center;background:radial-gradient(closest-side,rgba(110,150,190,.12),transparent 70%)}
.tile img{width:96px;height:96px;object-fit:contain;filter:drop-shadow(0 8px 16px rgba(0,0,0,.7))}
.tile .cap{padding:9px 10px 11px;border-top:1px solid #1a232e}
.tile .nm{font-size:12.5px;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.tile .sb{font-size:10.5px;color:#7b8b9d;margin-top:4px;display:flex;justify-content:space-between}
.ribbon{position:absolute;top:8px;left:8px;font-size:10px;padding:2px 6px;border-radius:2px;background:rgba(192,57,43,.18);border:1px solid rgba(192,57,43,.5);color:#ffb3a7}
</style></head><body>
<div class="top"><div class="brand">明日之后 · 图鉴</div>
<nav><a>置顶、预告专栏</a><a class="on">一、时装类</a><a>二、战力类</a><a>三、活动奖池</a><a>四、综合资料</a></nav></div>
<div class="hero"><h1>一、时装类 ·（一）人物时装</h1><p>共 1,623 条 · 按部位分组 · 悬停查看大图</p></div>
<div class="wall">
  <h3 class="g">头饰 · 衣服 · 整套</h3><div class="grid" id="g1"></div>
  <h3 class="g">背包 · 挂饰 · 面饰 · 发饰</h3><div class="grid" id="g2"></div>
</div>
<script>
const D=%DATA%;
const tpl=d=>`<div class="tile"><div class="ph"><img src="/${d.icon}" onerror="this.style.opacity=.12"></div>
<div class="cap"><div class="nm">${d.name}</div><div class="sb"><span>${d.part||'—'}</span><span>魅力 ${d.charm}</span></div></div>
${d.grade?`<div class="ribbon">${d.grade}</div>`:''}</div>`;
document.getElementById('g1').innerHTML=D.slice(0,12).map(tpl).join('');
document.getElementById('g2').innerHTML=D.slice(12).map(tpl).join('');
</script></body></html>"""

for name, html in (("A_archives.html", A), ("B_database.html", B), ("C_gallery.html", C)):
    (OUT / name).write_text(html.replace("%DATA%", DATA).replace("{BASE_CSS}", BASE_CSS), encoding="utf-8")
print("生成", [p.name for p in OUT.glob("*.html")])
