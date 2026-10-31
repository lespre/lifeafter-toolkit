# -*- coding: utf-8 -*-
"""贴图版 2D 预览：把热更包里挑出的同类贴图贴到 .sfx 节点上。

贴图来源：_截图/ktx_lightning_candidates（从 res.layers 里按透明底+细结构筛出），
按节点 texture 名归类（lightning / trail / ring / glow），非精确文件映射。
"""
from __future__ import annotations

import base64
import html
import json
import pathlib
import sys

CACHE = pathlib.Path("C:/Users/Administrator/AppData/Local/hermes/cache/scratch")
TEX = pathlib.Path("E:/la拆包项目/_截图/ktx_lightning_candidates")
OUT_DIR = pathlib.Path("E:/la拆包项目/_截图")

CASES = [
    ("原版 · 球状闪电 3档", "orig_qiu3"),
    ("皮肤 · 受击 sj", "s1013_jinghe_sj"),
]
# 类别 → 素材
TEX_SETS = [("lightning", "16_layers_11199_256x256.png"),
            ("trail", "17_layers_79163_512x512.png"),
            ("ring", "10_layers_121235_256x256.png"),
            ("glow", "12_layers_67126_256x256.png")]


def b64(p: pathlib.Path) -> str:
    return "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode()


def payload(track_json: pathlib.Path) -> list[dict]:
    d = json.loads(track_json.read_text(encoding="utf-8"))
    out = []
    for n in d.get("nodes") or []:
        t = n.get("tracks") or {}
        out.append({
            "n": n.get("name"), "tag": n.get("tag"),
            "s": float(n.get("start") or 0), "l": float(n.get("life") or 0),
            "p": n.get("pos_offset") or [0, 0, 0],
            "tex": (n.get("texture") or "").lower(),
            "c": t.get("ColorFramePar") or t.get("ColorFrame") or [],
            "sc": t.get("scale_XScale") or t.get("ScaleFrame") or [],
        })
    return out


def build(out: pathlib.Path) -> int:
    data = {}
    for label, stem in CASES:
        p = CACHE / (stem + ".tracks.json")
        if p.is_file():
            data[label] = payload(p)
    tex = {k: b64(TEX / f) for k, f in TEX_SETS if (TEX / f).is_file()}
    doc = """<!doctype html><meta charset="utf-8">
<style>
body{font-family:inherit;color:var(--foreground);margin:0;padding:12px 14px}
h2{font-size:15px;margin:0 0 2px}
.lead{color:var(--muted-foreground);font-size:12px;margin:0 0 12px}
.row{display:flex;flex-wrap:wrap;gap:14px}
.card{border:1px solid var(--border);border-radius:10px;padding:8px}
.card h3{font-size:12px;margin:0 0 6px;font-weight:600}
canvas{display:block;border-radius:8px;background:#05070f}
.bar{display:flex;align-items:center;gap:10px;margin:10px 0 0;font-size:11px;color:var(--muted-foreground)}
button{font:inherit;font-size:12px;padding:3px 10px;border-radius:6px;border:1px solid var(--border);background:transparent;color:inherit;cursor:pointer}
input[type=range]{width:240px}
</style>
<h2>核芯联动特效 · 贴图版 2D 预览</h2>
<p class="lead">按 .sfx 轨道（时间/颜色/缩放/发射）+ 热更包里的同类贴图（闪电·拖尾·光环·光晕）合成。<b>贴图为同类素材，不是精确文件映射</b>；效果用来判断层叠与观感。</p>
<div class="row" id="row"></div>
<div class="bar"><button id="play">暂停</button><input id="seek" type="range" min="0" max="2000" value="0"><span id="tlab">0.00s</span></div>
<script>
const DATA=__DATA__, TEX=__TEX__, DUR=2.0, SIZE=360;
function pick(tex){
  if(/lightning|shandian|shandianqiu/.test(tex)) return TEX.lightning;
  if(/trail|tuowei|liudao/.test(tex)) return TEX.trail;
  if(/ring|quan|huan/.test(tex)) return TEX.ring;
  return TEX.glow;
}
const imgs={}; for(const k in TEX){const i=new Image(); i.src=TEX[k]; imgs[k]=i;}
function interp(tr,t,d){ if(!tr||!tr.length) return d;
  if(t<=tr[0].time) return tr[0].value;
  for(let i=1;i<tr.length;i++){const a=tr[i-1],b=tr[i];
    if(t<=b.time){const k=(t-a.time)/Math.max(1e-6,b.time-a.time);
      return a.value.map((v,j)=>v+(b.value[j]-v)*k);}}
  return tr[tr.length-1].value; }
const scenes=Object.entries(DATA).map(([label,nodes])=>{
  const card=document.createElement('div'); card.className='card';
  card.innerHTML=`<h3>${label} <span style="opacity:.6">节点 ${nodes.length}</span></h3>`;
  const cv=document.createElement('canvas'); cv.width=SIZE; cv.height=SIZE; card.appendChild(cv);
  document.getElementById('row').appendChild(card);
  return {nodes, ctx:cv.getContext('2d')};
});
const q=new URLSearchParams(location.search);
const fixed=q.has('t')?parseFloat(q.get('t')):null;
let t=fixed!==null?fixed:0, playing=(fixed===null), last=performance.now();
function draw(s){
  const {ctx,nodes}=s; ctx.clearRect(0,0,SIZE,SIZE);
  ctx.globalCompositeOperation='lighter';
  const cx=SIZE/2, cy=SIZE/2;
  for(const n of nodes){
    const local=t-n.s; if(local<0||local>n.l) continue;
    const k=local/Math.max(1e-6,n.l);
    const col=interp(n.c,t,[255,255,255,180]);
    const a=(col[3]??255)/255, rgb=`rgb(${col[0]|0},${col[1]|0},${col[2]|0})`;
    const sc=(interp(n.sc,k,[1])[0])||1;
    const px=cx+(n.p[0]||0)*0.5, py=cy-(n.p[2]||0)*0.5;
    const src=pick(n.tex), img=imgs[Object.keys(TEX).find(k=>TEX[k]===src)];
    if(!img||!img.complete) continue;
    if(n.tag==='ParticleSystem'){
      const N=14;
      for(let i=0;i<N;i++){
        const birth=n.s+(i/N)*n.l, age=(t-birth)/(n.l*0.6);
        if(age<0||age>1) continue;
        const ang=(i*2.4)%(Math.PI*2), r=28+age*70;
        const size=(28+26*sc)*(1-age*0.4);
        ctx.globalAlpha=Math.max(0,Math.min(1,a*(1-age)*0.55));
        ctx.drawImage(img, px+Math.cos(ang)*r-size/2, py+Math.sin(ang)*r-size/2, size, size);
      }
    } else {
      const size=(70+90*sc)*(0.85+0.15*Math.sin(local*8));
      ctx.globalAlpha=Math.max(0,Math.min(1,a*0.75));
      ctx.drawImage(img, px-size/2, py-size/2, size, size);
    }
  }
  ctx.globalAlpha=1; ctx.globalCompositeOperation='source-over';
}
function frame(now){
  const dt=Math.min(0.05,(now-last)/1000); last=now;
  if(playing) t=(t+dt)%DUR;
  document.getElementById('seek').value=Math.round(t/DUR*2000);
  document.getElementById('tlab').textContent=t.toFixed(2)+'s';
  scenes.forEach(draw); requestAnimationFrame(frame);
}
document.getElementById('play').onclick=e=>{playing=!playing; e.target.textContent=playing?'暂停':'播放';};
document.getElementById('seek').oninput=e=>{t=e.target.value/2000*DUR;};
if(fixed!==null) scenes.forEach(draw);
requestAnimationFrame(frame);
</script>
"""
    doc = doc.replace("__DATA__", json.dumps(data, ensure_ascii=False)).replace("__TEX__", json.dumps(tex))
    out.write_text(doc, encoding="utf-8")
    print("写出", out, round(len(doc)/1024), "KB", "贴图", list(tex))
    return 0


if __name__ == "__main__":
    raise SystemExit(build(pathlib.Path(sys.argv[1])))
