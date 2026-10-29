import sys
# -*- coding: utf-8 -*-
"""生成「加成-伤害」实测反推工具：填数据 → 自动判线性/找拐点。"""
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import WEB  # noqa: E402

OUT = pathlib.Path(WEB / "analysis")

HTML = r"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<title>加成收益实测反推</title>
<style>
body{margin:0;padding:24px;background:#0b1116;color:#dfe7ec;font:14px/1.6 "Segoe UI","Microsoft YaHei",sans-serif}
h1{font-size:19px;margin:0 0 4px}
.sub{color:#7d8e99;font-size:12px;margin-bottom:16px}
.card{background:#121a20;border:1px solid #1e2b33;border-radius:10px;padding:16px 18px;margin-bottom:14px}
table{width:100%;border-collapse:collapse;font-size:13px}
th,td{padding:6px 8px;border-bottom:1px solid #1e2b33;text-align:left}
th{color:#7d8e99;font-weight:500;font-size:12px}
input{background:#0d151b;border:1px solid #243039;color:#dfe7ec;border-radius:6px;padding:5px 8px;width:110px;font-family:ui-monospace,Consolas,monospace}
button{background:#1b2a33;border:1px solid #2f4a58;color:#dfe7ec;border-radius:6px;padding:6px 14px;cursor:pointer;font-size:13px}
button:hover{background:#22343f}
.out{margin-top:12px;font-family:ui-monospace,Consolas,monospace;font-size:13px;color:#a9b8c2;white-space:pre-wrap}
.ok{color:#8fbf7f}.warn{color:#d9a441}.bad{color:#c0392b}
code{color:#d9a441}
</style></head><body>
<h1>加成收益实测反推</h1>
<div class="sub">固定武器、固定目标、固定部位，只改一项加成；每行填「加成值 %」和「实测伤害」。工具会算每段斜率，斜率明显下降的位置就是拐点。</div>

<div class="card">
<table id="t">
<thead><tr><th>#</th><th>加成 %</th><th>实测伤害</th><th>段斜率 Δ伤害/Δ加成</th></tr></thead>
<tbody></tbody>
</table>
<div style="margin-top:12px"><button onclick="addRow()">+ 加一行</button> <button onclick="calc()">计算</button> <button onclick="reset()">清空</button></div>
<div class="out" id="out">填两行以上再点计算</div>
</div>

<div class="card">
<div class="sub" style="margin:0">怎么用：① 先测一个基准（不加成，或最低加成）② 每次只加一档，记录伤害 ③ 至少 5 档，跨度拉开 ④ 斜率接近常数 = 无衰减；某点后斜率掉一半 = 拐点在那。</div>
</div>

<script>
const tb = document.querySelector("#t tbody");
function addRow(v1="", v2=""){
  const i = tb.children.length;
  const tr = document.createElement("tr");
  tr.innerHTML = `<td>${i+1}</td>
    <td><input type="number" step="0.01" value="${v1}" placeholder="如 40"></td>
    <td><input type="number" step="1" value="${v2}" placeholder="如 1234"></td>
    <td class="slope">—</td>`;
  tb.appendChild(tr);
}
function reset(){ tb.innerHTML=""; for(let i=0;i<6;i++) addRow(); document.getElementById("out").textContent="填两行以上再点计算"; }
function calc(){
  const rows = [...tb.children].map(tr => ({
    x: parseFloat(tr.querySelectorAll("input")[0].value),
    y: parseFloat(tr.querySelectorAll("input")[1].value),
    cell: tr.querySelector(".slope")
  })).filter(r => !isNaN(r.x) && !isNaN(r.y)).sort((a,b)=>a.x-b.x);

  if (rows.length < 2){ document.getElementById("out").textContent = "至少两行有效数据"; return; }

  const slopes = [];
  rows.forEach((r,i)=>{ r.cell.textContent = "—"; r.cell.className = "slope"; });
  for (let i=1;i<rows.length;i++){
    const dx = rows[i].x - rows[i-1].x;
    const dy = rows[i].y - rows[i-1].y;
    const k = dx === 0 ? null : dy/dx;
    slopes.push({from: rows[i-1].x, to: rows[i].x, k});
    if (k !== null){
      rows[i].cell.textContent = k.toFixed(3);
      rows[i].cell.className = "slope " + (k < 0 ? "bad" : "");
    }
  }

  const ks = slopes.map(s=>s.k).filter(k=>k!==null && k>0);
  let msg = "分段斜率：\n";
  slopes.forEach(s=>{ if(s.k!==null) msg += `  ${s.from}% → ${s.to}%   ${s.k.toFixed(3)}\n`; });

  if (ks.length >= 2){
    const maxK = Math.max(...ks), minK = Math.min(...ks);
    const ratio = minK / maxK;
    msg += "\n";
    if (ratio > 0.85){
      msg += `判定：斜率基本恒定（最低/最高 = ${ratio.toFixed(2)}）→ 没有明显递减\n`;
    } else {
      const idx = slopes.findIndex(s => s.k !== null && s.k < maxK * 0.7);
      msg += `判定：存在递减，拐点落在 ${slopes[idx].from}% ~ ${slopes[idx].to}% 之间\n`;
      msg += `      该段斜率 ${slopes[idx].k.toFixed(3)}，是最高斜率 ${maxK.toFixed(3)} 的 ${(slopes[idx].k/maxK*100).toFixed(0)}%\n`;
    }
  }
  msg += "\n提示：斜率单位是「每 1% 加成带来的伤害」，所以数值大小取决于你的基础伤害，只看相对变化。";
  document.getElementById("out").textContent = msg;
}
reset();
</script>
</body></html>"""

dest = OUT / "bonus_curve_test.html"
dest.write_text(HTML, encoding="utf-8")
print("写出", dest, len(HTML), "字节")
