import sys
# -*- coding: utf-8 -*-
"""生成 PvP 伤害倍率计算器（公式来自 HurtCalc 反编译）。"""
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import WEB  # noqa: E402

OUT = pathlib.Path(WEB / "analysis")

HTML = """<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<title>PvP 伤害倍率计算器</title>
<style>
body{margin:0;padding:24px;background:#0b1116;color:#dfe7ec;font:14px/1.6 "Segoe UI","Microsoft YaHei",sans-serif}
h1{font-size:19px;margin:0 0 4px}
.sub{color:#7d8e99;font-size:12px;margin-bottom:18px}
.card{background:#121a20;border:1px solid #1e2b33;border-radius:10px;padding:16px 18px;margin-bottom:14px}
.row{display:grid;grid-template-columns:180px 1fr 78px;gap:12px;align-items:center;margin:10px 0}
label{color:#a9b8c2;font-size:13px}
input[type=range]{width:100%;accent-color:#6f9fba}
.val{font-family:ui-monospace,Consolas,monospace;color:#d9a441;text-align:right}
.out{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:6px}
.box{background:#16212a;border:1px solid #243039;border-radius:8px;padding:12px}
.box .k{color:#7d8e99;font-size:11.5px}
.box .v{font-size:20px;color:#dfe7ec;font-family:ui-monospace,Consolas,monospace}
.note{color:#7d8e99;font-size:12px;margin-top:10px}
code{color:#d9a441}
</style></head><body>
<h1>PvP 伤害倍率计算器</h1>
<div class="sub">公式来自 com/formula/HurtCalc.py 反编译：<code>伤害 = 基础 × (1+Σ加成) × (1−Σ减免) × 部位 × 暴击</code>；140/141 属性经压缩表为恒等，直接相加。</div>

<div class="card">
  <div class="row"><label>攻击方 对玩家伤害加成</label><input id="a" type="range" min="0" max="200" value="40"><span class="val" id="av">40%</span></div>
  <div class="row"><label>攻击方 通用伤害加成</label><input id="a2" type="range" min="0" max="200" value="60"><span class="val" id="a2v">60%</span></div>
  <div class="row"><label>防守方 受到玩家减免</label><input id="r" type="range" min="0" max="100" value="30"><span class="val" id="rv">30%</span></div>
  <div class="row"><label>防守方 通用伤害减免</label><input id="r2" type="range" min="0" max="100" value="20"><span class="val" id="r2v">20%</span></div>
  <div class="row"><label>部位系数</label><input id="p" type="range" min="50" max="300" value="100"><span class="val" id="pv">100%</span></div>
  <div class="row"><label>暴击倍率</label><input id="c" type="range" min="100" max="300" value="150"><span class="val" id="cv">150%</span></div>
</div>

<div class="card">
  <div class="out">
    <div class="box"><div class="k">加成桶 (1+A)</div><div class="v" id="oa">—</div></div>
    <div class="box"><div class="k">减免桶 (1−R)</div><div class="v" id="or">—</div></div>
    <div class="box"><div class="k">非暴击倍率</div><div class="v" id="on">—</div></div>
    <div class="box"><div class="k">暴击倍率</div><div class="v" id="oc">—</div></div>
  </div>
  <div class="note">加成/减免上限按 100% 夹逼（减免桶不会为负）。部位系数与暴击为独立乘区。</div>
</div>

<script>
const ids = ["a","a2","r","r2","p","c"];
function calc(){
  const v = {};
  ids.forEach(i => v[i] = +document.getElementById(i).value / 100);
  ["a","a2","r","r2","p","c"].forEach(i => {
    document.getElementById(i+"v").textContent = Math.round(v[i]*100) + "%";
  });
  const A = v.a + v.a2;
  const R = Math.min(v.r + v.r2, 1);
  document.getElementById("oa").textContent = (1+A).toFixed(2) + "×";
  document.getElementById("or").textContent = (1-R).toFixed(2) + "×";
  document.getElementById("on").textContent = ((1+A)*(1-R)*v.p).toFixed(2) + "×";
  document.getElementById("oc").textContent = ((1+A)*(1-R)*v.p*v.c).toFixed(2) + "×";
}
ids.forEach(i => document.getElementById(i).addEventListener("input", calc));
calc();
</script>
</body></html>"""

dest = OUT / "pvp_calc.html"
dest.write_text(HTML, encoding="utf-8")
print("写出", dest, len(HTML), "字节")
