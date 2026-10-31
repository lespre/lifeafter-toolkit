# -*- coding: utf-8 -*-
"""把 .sfx 的轨道数据做成可播放的 2D 近似预览（非引擎还原）。

做法：解析 parse_sfx_tracks.py 的 JSON → 每个节点按 start/life 出现，
ParticleSystem 按速度/重力发射粒子，Sprite/Model 画贴片，PolyTube 画拖尾。
颜色取 ColorFramePar / ColorFrame 关键帧插值，缩放取 scale 轨道。
"""
from __future__ import annotations

import html
import json
import pathlib
import sys

CACHE = pathlib.Path("C:/Users/Administrator/AppData/Local/hermes/cache/scratch")

CASES = [
    ("原版 · 球状闪电 3档", "orig_qiu3"),
    ("皮肤 · 受击 sj", "s1013_jinghe_sj"),
    ("皮肤 · 常驻球体 zishen", "s1013_jinghe_zishen"),
]


def payload(track_json: pathlib.Path) -> dict:
    d = json.loads(track_json.read_text(encoding="utf-8"))
    out = []
    for n in d.get("nodes") or []:
        t = n.get("tracks") or {}
        out.append({
            "name": n.get("name"),
            "tag": n.get("tag"),
            "start": float(n.get("start") or 0),
            "life": float(n.get("life") or 0),
            "pos": n.get("pos_offset") or [0, 0, 0],
            "blend": n.get("blend_mode"),
            "tex": (n.get("texture") or "").split("\\")[-1].split("/")[-1],
            "color": t.get("ColorFramePar") or t.get("ColorFrame") or [],
            "scale": t.get("scale_XScale") or t.get("ScaleFrame") or [],
            "gravity": t.get("GravityFrame") or [],
            "vmax": t.get("MaxSpriteVelocityFrame") or [],
            "vmin": t.get("MinSpriteVelocityFrame") or [],
            "rot": t.get("RotDegreeSpeedFrame") or [],
            "radius": t.get("EmissionRadiusFrame") or [],
        })
    return {"nodes": out}


def build(out: pathlib.Path) -> int:
    data = {}
    for label, stem in CASES:
        p = CACHE / (stem + ".tracks.json")
        if p.is_file():
            data[label] = payload(p)
    (out.parent).mkdir(parents=True, exist_ok=True)
    doc = """<!doctype html><meta charset="utf-8">
<style>
body{font-family:inherit;color:var(--foreground);margin:0;padding:12px 14px}
h2{font-size:15px;margin:0 0 2px}
.lead{color:var(--muted-foreground);font-size:12px;margin:0 0 12px}
.row{display:flex;flex-wrap:wrap;gap:14px}
.card{border:1px solid var(--border);border-radius:10px;padding:8px}
.card h3{font-size:12px;margin:0 0 6px;font-weight:600}
canvas{display:block;border-radius:8px;background:#0b1020}
.bar{display:flex;align-items:center;gap:10px;margin:8px 0 0;font-size:11px;color:var(--muted-foreground)}
button{font:inherit;font-size:12px;padding:3px 10px;border-radius:6px;border:1px solid var(--border);background:transparent;color:inherit;cursor:pointer}
input[type=range]{width:220px}
</style>
<h2>核芯联动特效 · 2D 近似预览</h2>
<p class="lead">按 .sfx 的轨道数据（出现时间 / 颜色关键帧 / 发射速度 / 重力 / 缩放）在 Canvas 上近似模拟。<b>不是引擎还原</b>：贴图未定位到具体文件，粒子用径向渐变代替，仅用于看层数与节奏。</p>
<div class="row" id="row"></div>
<div class="bar"><button id="play">暂停</button><span>进度 <input id="seek" type="range" min="0" max="2000" value="0"></span><span id="tlab">0.00s</span></div>
<script>
const DATA = __DATA__;
const DUR = 2.0, SIZE = 340;
function interp(track, t, dflt){
  if(!track || !track.length) return dflt;
  if(t <= track[0].time) return track[0].value;
  for(let i=1;i<track.length;i++){
    const a=track[i-1], b=track[i];
    if(t<=b.time){
      const k=(t-a.time)/Math.max(1e-6,(b.time-a.time));
      return a.value.map((v,j)=>v+(b.value[j]-v)*k);
    }
  }
  return track[track.length-1].value;
}
function makeCanvas(label, data){
  const card=document.createElement('div'); card.className='card';
  card.innerHTML=`<h3>${label} <span style="opacity:.6">节点 ${data.nodes.length}</span></h3>`;
  const cv=document.createElement('canvas'); cv.width=SIZE; cv.height=SIZE; card.appendChild(cv);
  document.getElementById('row').appendChild(card);
  return {cv, ctx:cv.getContext('2d'), nodes:data.nodes};
}
const scenes = Object.entries(DATA).map(([k,v])=>makeCanvas(k,v));
const q=new URLSearchParams(location.search);
const fixed=q.has('t')?parseFloat(q.get('t')):null;
let t=fixed!==null?fixed:0, playing=(fixed===null), last=performance.now();
function lerp(a,b,k){return a+(b-a)*k}
function drawScene(s){
  const {ctx,nodes}=s; ctx.clearRect(0,0,SIZE,SIZE);
  ctx.globalCompositeOperation='lighter';
  const cx=SIZE/2, cy=SIZE/2;
  for(const n of nodes){
    const local=t-n.start;
    if(local<0 || local>n.life) continue;
    const k=local/Math.max(1e-6,n.life);
    const col=interp(n.color,t,(n.tag==='ParticleSystem'?[255,255,255,200]:[255,255,255,120]));
    const a=(col[3]??255)/255;
    const rgb=`rgb(${col[0]|0},${col[1]|0},${col[2]|0})`;
    const sc=interp(n.scale,k,[1])[0]||1;
    const px=cx+(n.pos[0]||0)*0.6, py=cy-(n.pos[2]||0)*0.6;
    if(n.tag==='ParticleSystem'){
      const vmax=(interp(n.vmax,k,[60])[0])||60;
      const g=(interp(n.gravity,k,[0])[0])||0;
      const rad=(interp(n.radius,k,[30])[0])||30;
      const N=26, plife=Math.max(0.18,n.life*0.55);
      for(let i=0;i<N;i++){
        const birth=n.start+(i/N)*n.life;
        const age=(t-birth)/plife;
        if(age<0||age>1) continue;
        const ang=(i*2.399)%(Math.PI*2);
        const sp=vmax*(0.4+0.6*((i*37)%100)/100);
        const dx=Math.cos(ang)*(rad*0.35+sp*age*0.9);
        const dy=Math.sin(ang)*(rad*0.35+sp*age*0.9)+g*age*age*0.5;
        const size=(10+26*sc)*(1-age*0.45);
        const alpha=a*(1-age)*0.9;
        const grd=ctx.createRadialGradient(px+dx,py+dy,0,px+dx,py+dy,Math.max(3,size));
        grd.addColorStop(0,rgb); grd.addColorStop(0.55,rgb); grd.addColorStop(1,'rgba(0,0,0,0)');
        ctx.globalAlpha=Math.max(0,Math.min(1,alpha));
        ctx.fillStyle=grd;
        ctx.beginPath(); ctx.arc(px+dx,py+dy,Math.max(3,size),0,Math.PI*2); ctx.fill();
      }
    } else if(n.tag==='PolyTube' || /trail|tuowei/i.test(n.tex||'')){
      ctx.globalAlpha=Math.max(0,Math.min(1,a*0.8));
      ctx.strokeStyle=rgb; ctx.lineWidth=Math.max(2,8*sc);
      ctx.beginPath(); ctx.moveTo(px-140,py); ctx.lineTo(px+140*Math.min(1,local*3),py); ctx.stroke();
    } else {
      const r=Math.max(6,40*sc)*(0.6+0.4*Math.sin(local*10));
      const grd=ctx.createRadialGradient(px,py,0,px,py,r);
      grd.addColorStop(0,rgb); grd.addColorStop(1,'rgba(0,0,0,0)');
      ctx.globalAlpha=Math.max(0,Math.min(1,a*0.7));
      ctx.fillStyle=grd; ctx.beginPath(); ctx.arc(px,py,r,0,Math.PI*2); ctx.fill();
    }
  }
  ctx.globalAlpha=1; ctx.globalCompositeOperation='source-over';
}
function frame(now){
  const dt=Math.min(0.05,(now-last)/1000); last=now;
  if(playing){ t=(t+dt)%DUR; }
  document.getElementById('seek').value=Math.round(t/DUR*2000);
  document.getElementById('tlab').textContent=t.toFixed(2)+'s';
  scenes.forEach(drawScene);
  requestAnimationFrame(frame);
}
document.getElementById('play').onclick=e=>{playing=!playing; e.target.textContent=playing?'暂停':'播放';};
document.getElementById('seek').oninput=e=>{t=e.target.value/2000*DUR;};
if(fixed!==null){ scenes.forEach(drawScene); }
requestAnimationFrame(frame);
</script>
"""
    doc = doc.replace("__DATA__", json.dumps(data, ensure_ascii=False))
    out.write_text(doc, encoding="utf-8")
    print("写出", out, len(doc), "B", "场景", list(data))
    return 0


if __name__ == "__main__":
    raise SystemExit(build(pathlib.Path(sys.argv[1])))
