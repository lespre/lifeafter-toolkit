# -*- coding: utf-8 -*-
"""用「真实贴图」渲染 .sfx：贴图与节点按名字精确绑定（.tga 名 ↔ 同名 .ktx 导出图）。"""
from __future__ import annotations

import base64
import json
import pathlib
import sys

CACHE = pathlib.Path("C:/Users/Administrator/AppData/Local/hermes/cache/scratch")
TEX = pathlib.Path("E:/la拆包项目/_截图/sfx_textures_real")

CASES = [
    ("原版 · 球状闪电 3档", "orig_qiu3"),
    ("皮肤 · 受击 sj", "s1013_jinghe_sj"),
    ("皮肤 · 常驻 zishen", "s1013_jinghe_zishen"),
]


def b64(p: pathlib.Path) -> str:
    return "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode()


def payload(p: pathlib.Path) -> list[dict]:
    d = json.loads(p.read_text(encoding="utf-8"))
    out = []
    for n in d.get("nodes") or []:
        t = n.get("tracks") or {}
        tex = (n.get("texture") or "").replace("/", "\\")
        out.append({
            "n": n.get("name"), "tag": n.get("tag"),
            "s": float(n.get("start") or 0), "l": float(n.get("life") or 0),
            "p": n.get("pos_offset") or [0, 0, 0],
            "tex": pathlib.PureWindowsPath(tex).stem.lower() if tex else "",
            "c": t.get("ColorFramePar") or t.get("ColorFrame") or [],
            "sc": t.get("scale_XScale") or t.get("ScaleFrame") or [],
            "vmax": t.get("MaxSpriteVelocityFrame") or [],
            "grav": t.get("GravityFrame") or [],
        })
    return out


def main(out_path: pathlib.Path) -> int:
    data = {}
    for label, stem in CASES:
        p = CACHE / (stem + ".tracks.json")
        if p.is_file():
            data[label] = payload(p)
    tex = {}
    for p in sorted(TEX.glob("*.png")):
        tex[p.stem.lower()] = b64(p)
    print("贴图", len(tex), "场景", list(data))

    doc = """<!doctype html><meta charset="utf-8">
<style>
body{font-family:inherit;color:var(--foreground);margin:0;padding:12px 14px}
h2{font-size:15px;margin:0 0 2px}
.lead{color:var(--muted-foreground);font-size:12px;margin:0 0 12px}
.row{display:flex;flex-wrap:wrap;gap:14px}
.card{border:1px solid var(--border);border-radius:10px;padding:8px}
.card h3{font-size:12px;margin:0 0 6px;font-weight:600}
canvas{display:block;border-radius:8px;background:#04060d}
.bar{display:flex;align-items:center;gap:10px;margin:10px 0 0;font-size:11px;color:var(--muted-foreground)}
button{font:inherit;font-size:12px;padding:3px 10px;border-radius:6px;border:1px solid var(--border);background:transparent;color:inherit;cursor:pointer}
input[type=range]{width:260px}
</style>
<h2>核芯联动特效 · 真实贴图 2D 预览</h2>
<p class="lead">贴图按 .sfx 里的路径名精确绑定（.tga 名 ↔ 客户端同名 .ktx 导出）；颜色/缩放/出现时间取轨道关键帧；加法混合模拟发光。仍是 2D 近似，不含 3D 模型与曲线拖尾。</p>
<div class="row" id="row"></div>
<div class="bar"><button id="play">暂停</button><input id="seek" type="range" min="0" max="2000" value="0"><span id="tlab">0.00s</span></div>
<script>
const DATA=__DATA__, TEXS=__TEX__, DUR=2.0, SIZE=380;
const imgs={}; for(const k in TEXS){const i=new Image(); i.src=TEXS[k]; imgs[k]=i;}
function pick(name){
  if(!name) return null;
  if(imgs[name]) return imgs[name];
  const keys=Object.keys(imgs);
  const hit=keys.find(k=>k.includes(name)||name.includes(k));
  return hit?imgs[hit]:null;
}
function interp(tr,t,d){ if(!tr||!tr.length)return d;
  if(t<=tr[0].time)return tr[0].value;
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
  const cx=SIZE/2, cy=SIZE*0.62;
  for(const n of nodes){
    const local=t-n.s; if(local<0||local>n.l) continue;
    const k=local/Math.max(1e-6,n.l);
    const col=interp(n.c,t,[255,255,255,190]);
    const a=Math.max(0,Math.min(1,(col[3]??255)/255));
    const sc=(interp(n.sc,k,[1])[0])||1;
    const px=cx+(n.p[0]||0)*0.5, py=cy-(n.p[2]||0)*0.5;
    const img=pick(n.tex);
    if(n.tag==='ParticleSystem'){
      const vmax=(interp(n.vmax,k,[60])[0])||60;
      const g=(interp(n.grav,k,[0])[0])||0;
      const N=16;
      for(let i=0;i<N;i++){
        const birth=n.s+(i/N)*n.l, age=(t-birth)/(n.l*0.55);
        if(age<0||age>1) continue;
        const ang=(i*2.399)%(Math.PI*2);
        const r=vmax*age*0.8;
        const size=(14+30*sc)*(1-age*0.35);
        ctx.globalAlpha=a*(1-age)*0.85;
        const x=px+Math.cos(ang)*r, y=py+Math.sin(ang)*r*(0.7)+g*age*age*0.25;
        if(img&&img.complete) ctx.drawImage(img, x-size/2, y-size/2, size, size);
        else { const gr=ctx.createRadialGradient(x,y,0,x,y,size/2);
               gr.addColorStop(0,'#fff'); gr.addColorStop(1,'rgba(0,0,0,0)');
               ctx.fillStyle=gr; ctx.beginPath(); ctx.arc(x,y,size/2,0,7); ctx.fill(); }
      }
    } else {
      const size=(70+120*sc);
      if(img&&img.complete){
        ctx.globalAlpha=a*0.9;
        ctx.drawImage(img, px-size/2, py-size/2, size, size*((img.height/img.width)||1));
      }
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
    out_path.write_text(doc, encoding="utf-8")
    print("写出", out_path, round(len(doc) / 1024), "KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(pathlib.Path(sys.argv[1])))
