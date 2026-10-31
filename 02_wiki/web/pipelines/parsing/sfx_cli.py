# -*- coding: utf-8 -*-
"""sfx_cli.py — .sfx 特效渲染 & CDN 索引查询（供 la.py 调用）

能力：
  render <a.sfx> [b.sfx ...] -o out.html
      解析 .sfx 轨道 → 按贴图名在 CDN 索引里定位 .ktx → 导出 png → 出可播放 HTML
  tex <a.sfx>
      只列出该特效引用的贴图及其定位结果（不渲染）
  cdn-find <路径或fid>
      查 CDN 全库索引：这个路径/fid 在哪个包、第几行
  cdn-status
      索引概况

贴图定位要点：.sfx 写 .tga，客户端实际存同名 .ktx（换扩展名后命中率 33/33）。
"""
from __future__ import annotations

import base64
import json
import pathlib
import re
import sqlite3
import struct
import subprocess
import sys

import numpy as np
from PIL import Image

ROOT = pathlib.Path("E:/la拆包项目")
WEB = ROOT / "02_wiki/web"
CDN_DB = ROOT / "01_索引与产物/10_索引/cdn_index.sqlite3"
NAMES_DB = ROOT / "01_索引与产物/10_索引/热更检测/names_join.sqlite3"
PACKS = ROOT / "01_索引与产物/源包/pe_npk_20261029"
TEXDIR = ROOT / "_截图/sfx_tex_cache"
TRACKS = pathlib.Path("C:/Users/Administrator/AppData/Local/hermes/cache/scratch")
PARSER = ROOT / "00_规范与工具/工具/工具库/02_图文音频渲染/皮肤链与渲染/parse_sfx_tracks.py"
PY = sys.executable

sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/01_解码定位复原/解包与扫描"))
from toolkit_core.path_fid import fid_of  # noqa: E402
from toolkit_core import android_gpk as AG  # noqa: E402
from la_unpack_core import NpkArchive  # noqa: E402

PAT = re.compile(r"[A-Za-z0-9_\\/\.\-]+\.(?:tga|spr|ktx|dds)")


def _norm(p: str) -> str:
    return p.replace("/", "\\")


def texture_names(sfx: pathlib.Path) -> list[str]:
    t = sfx.read_text(encoding="utf-8", errors="ignore")
    out = set()
    for m in PAT.finditer(t):
        out.add(pathlib.PureWindowsPath(_norm(m.group(0))).name)
    return sorted(out)


def resolve(names: list[str]) -> dict[str, dict]:
    """名字 → {full, fid, pack, row}。.tga 名换 .ktx 后查 CDN 索引。"""
    nj = sqlite3.connect(NAMES_DB)
    cdn = sqlite3.connect(CDN_DB)
    out: dict[str, dict] = {}
    for n in names:
        low = n.lower()
        cur = nj.execute("select name from nm where lower(name) like ?", ("%" + low,))
        full = next((r[0] for r in cur.fetchall()
                     if pathlib.PureWindowsPath(r[0]).name.lower() == low), None)
        if not full:
            out[n] = {"status": "no_path"}
            continue
        got = None
        for cand in (full, re.sub(r"\.tga$", ".ktx", full, flags=re.I),
                     re.sub(r"\.tga$", ".dds", full, flags=re.I)):
            fid = fid_of(cand)
            row = cdn.execute(
                "select pack,row from entries where fid_hi=? and fid_lo=? limit 1",
                ((fid >> 32) & 0xFFFFFFFF, fid & 0xFFFFFFFF)).fetchone()
            if row:
                got = {"status": "ok", "full": cand, "fid": "%016X" % fid,
                       "pack": row[0], "row": row[1]}
                break
        if got and n.lower().endswith(".spr"):
            at = _read_spr(got)
            if at:
                page, frames = at
                sub = resolve([page])
                ent = sub.get(page) or {"status": "miss"}
                ent = dict(ent)
                ent["frames"] = frames
                ent["atlas"] = n
                out[n] = ent
                continue
        out[n] = got or {"status": "miss", "full": full}
    return out


def _read_spr(h: dict) -> tuple[str, list[tuple[int, int, int, int]]] | None:
    """从 npk 里取出 .spr（atlas 描述），返回 (页贴图名, 帧矩形)。"""
    pack = h["pack"].split("/")[-1]
    try:
        a = NpkArchive(str(PACKS / pack))
        d = a.read_entry(entry_index=h["row"]).decode("gbk", errors="replace")
    except Exception:                                          # noqa: BLE001
        return None
    lines = [l.strip() for l in d.splitlines() if l.strip()]
    if len(lines) < 4:
        return None
    frames = []
    page = None
    for ln in lines[3:]:
        parts = ln.split()
        if len(parts) >= 5:
            page = page or parts[0]
            frames.append(tuple(int(x) for x in parts[1:5]))
    return (page, frames) if page else None


def export_png(hits: dict[str, dict]) -> dict[str, pathlib.Path]:
    TEXDIR.mkdir(parents=True, exist_ok=True)
    cache: dict[str, NpkArchive] = {}
    done: dict[str, pathlib.Path] = {}
    for name, h in hits.items():
        if h.get("status") != "ok":
            continue
        dst = TEXDIR / (pathlib.PureWindowsPath(name).stem + ".png")
        if dst.is_file():
            done[name] = dst
            continue
        pack = h["pack"].split("/")[-1]
        a = cache.get(pack) or NpkArchive(str(PACKS / pack))
        cache[pack] = a
        try:
            d = a.read_entry(entry_index=h["row"])
            info = AG.parse_ktx(d)
            rgba = AG._ktx_rgba(d, info)
            Image.fromarray(np.asarray(rgba, dtype=np.uint8), "RGBA").save(dst)
            done[name] = dst
        except Exception as exc:                                # noqa: BLE001
            print("  ✗ 解码失败 %-24s %s" % (name, str(exc)[:50]))
    return done


def tracks_of(sfx: pathlib.Path) -> pathlib.Path | None:
    out = TRACKS / (sfx.stem + ".tracks.json")
    if not out.is_file():
        subprocess.run([PY, str(PARSER), str(sfx), str(out)], capture_output=True, timeout=600)
    return out if out.is_file() else None


def _payload(tj: pathlib.Path) -> list[dict]:
    d = json.loads(tj.read_text(encoding="utf-8"))
    rows = []
    for n in d.get("nodes") or []:
        t = n.get("tracks") or {}
        tex = (n.get("texture") or "")
        rows.append({
            "n": n.get("name"), "tag": n.get("tag"),
            "s": float(n.get("start") or 0), "l": float(n.get("life") or 0),
            "p": n.get("pos_offset") or [0, 0, 0],
            "tex": pathlib.PureWindowsPath(_norm(tex)).stem.lower() if tex else "",
            "c": t.get("ColorFramePar") or t.get("ColorFrame") or [],
            "sc": t.get("scale_XScale") or t.get("ScaleFrame") or [],
            "vmax": t.get("MaxSpriteVelocityFrame") or [],
            "grav": t.get("GravityFrame") or [],
            "frames": None,
        })
    return rows


HTML = """<!doctype html><meta charset="utf-8">
<style>
body{font-family:inherit;color:var(--foreground);margin:0;padding:12px 14px}
h2{font-size:15px;margin:0 0 2px}.lead{color:var(--muted-foreground);font-size:12px;margin:0 0 12px}
.row{display:flex;flex-wrap:wrap;gap:14px}
.card{border:1px solid var(--border);border-radius:10px;padding:8px}
.card h3{font-size:12px;margin:0 0 6px;font-weight:600}
canvas{display:block;border-radius:8px;background:#04060d}
.bar{display:flex;align-items:center;gap:10px;margin:10px 0 0;font-size:11px;color:var(--muted-foreground)}
button{font:inherit;font-size:12px;padding:3px 10px;border-radius:6px;border:1px solid var(--border);background:transparent;color:inherit;cursor:pointer}
input[type=range]{width:260px}
</style>
<h2>__TITLE__</h2>
<p class="lead">贴图按 .sfx 里的路径名精确绑定（.tga ↔ 客户端同名 .ktx）；颜色/缩放/出现时间取轨道关键帧；加法混合。2D 近似，不含 3D 模型与曲线拖尾。</p>
<div class="row" id="row"></div>
<div class="bar"><button id="play">暂停</button><input id="seek" type="range" min="0" max="2000" value="0"><span id="tlab">0.00s</span></div>
<script>
const DATA=__DATA__, TEXS=__TEX__, DUR=__DUR__, SIZE=380;
const imgs={}; for(const k in TEXS){const i=new Image(); i.src=TEXS[k]; imgs[k]=i;}
function pick(name){ if(!name) return null; if(imgs[name]) return imgs[name];
  const ks=Object.keys(imgs); const hit=ks.find(k=>k.includes(name)||name.includes(k));
  return hit?imgs[hit]:null; }
function interp(tr,t,d){ if(!tr||!tr.length)return d; if(t<=tr[0].time)return tr[0].value;
  for(let i=1;i<tr.length;i++){const a=tr[i-1],b=tr[i];
    if(t<=b.time){const k=(t-a.time)/Math.max(1e-6,b.time-a.time);
      return a.value.map((v,j)=>v+(b.value[j]-v)*k);}}
  return tr[tr.length-1].value; }
const scenes=Object.entries(DATA).map(([label,nodes])=>{
  const card=document.createElement('div'); card.className='card';
  card.innerHTML=`<h3>${label} <span style="opacity:.6">节点 ${nodes.length}</span></h3>`;
  const cv=document.createElement('canvas'); cv.width=SIZE; cv.height=SIZE; card.appendChild(cv);
  document.getElementById('row').appendChild(card);
  return {nodes, ctx:cv.getContext('2d')};});
const q=new URLSearchParams(location.search);
const fixed=q.has('t')?parseFloat(q.get('t')):null;
let t=fixed!==null?fixed:0, playing=(fixed===null), last=performance.now();
function draw(s){
  const {ctx,nodes}=s; ctx.clearRect(0,0,SIZE,SIZE); ctx.globalCompositeOperation='lighter';
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
      const vmax=(interp(n.vmax,k,[60])[0])||60, g=(interp(n.grav,k,[0])[0])||0, N=16;
      for(let i=0;i<N;i++){
        const birth=n.s+(i/N)*n.l, age=(t-birth)/(n.l*0.55);
        if(age<0||age>1) continue;
        const ang=(i*2.399)%(Math.PI*2), r=vmax*age*0.8, size=(14+30*sc)*(1-age*0.35);
        ctx.globalAlpha=a*(1-age)*0.85;
        const x=px+Math.cos(ang)*r, y=py+Math.sin(ang)*r*0.7+g*age*age*0.25;
        if(img&&img.complete){
          if(n.fr&&n.fr.length){
            const fi=Math.min(n.fr.length-1,Math.floor(((i/N+age*0.3)%1)*n.fr.length));
            const f=n.fr[fi], fw=f[2]-f[0], fh=f[3]-f[1];
            ctx.drawImage(img,f[0],f[1],fw,fh,x-size/2,y-size/2,size,size*(fh/fw||1));
          } else ctx.drawImage(img,x-size/2,y-size/2,size,size);
        }
        else { const gr=ctx.createRadialGradient(x,y,0,x,y,size/2);
               gr.addColorStop(0,'#fff'); gr.addColorStop(1,'rgba(0,0,0,0)');
               ctx.fillStyle=gr; ctx.beginPath(); ctx.arc(x,y,size/2,0,7); ctx.fill(); }
      }
    } else {
      const size=(70+120*sc);
      if(img&&img.complete){
        ctx.globalAlpha=a*0.9;
        if(n.fr&&n.fr.length){
          const fi=Math.min(n.fr.length-1,Math.floor(k*n.fr.length));
          const f=n.fr[fi];
          const fw=f[2]-f[0], fh=f[3]-f[1];
          ctx.drawImage(img,f[0],f[1],fw,fh,px-size/2,py-size/2,size,size*(fh/fw||1));
        } else {
          ctx.drawImage(img,px-size/2,py-size/2,size,size*((img.height/img.width)||1));
        }
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


def render(files: list[pathlib.Path], out: pathlib.Path) -> int:
    cases, allhits = {}, {}
    for f in files:
        tj = tracks_of(f)
        if not tj:
            print("✗ 轨道解析失败", f)
            continue
        cases[f.stem] = _payload(tj)
        hits = resolve(texture_names(f))
        allhits.update(hits)
        fr = {pathlib.PureWindowsPath(k).stem.lower(): v.get("frames")
              for k, v in hits.items() if v.get("frames")}
        for node in cases[f.stem]:
            if node["tex"] in fr:
                node["fr"] = [list(map(int, r)) for r in fr[node["tex"]]]
        ok = sum(1 for v in hits.values() if v.get("status") == "ok")
        print("  %-28s 节点 %-3d 贴图 %d/%d 命中" % (f.name, len(cases[f.stem]), ok, len(hits)))
    tex = export_png(allhits)
    b64 = {k: "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode()
           for k, p in tex.items()}
    dur = max([(n["s"] + n["l"]) for rows in cases.values() for n in rows] + [1.0])
    doc = (HTML.replace("__TITLE__", "特效 2D 预览 · " + " / ".join(cases))
               .replace("__DATA__", json.dumps(cases, ensure_ascii=False))
               .replace("__TEX__", json.dumps(b64))
               .replace("__DUR__", "%.2f" % max(dur, 0.5)))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")
    print("写出 %s（%.0f KB，贴图 %d 张）" % (out, len(doc) / 1024, len(b64)))
    return 0


def cmd_sfx(a) -> int:
    if a.action == "render":
        return render([pathlib.Path(p) for p in a.files], pathlib.Path(a.out))
    if a.action == "tex":
        for p in a.files:
            hits = resolve(texture_names(pathlib.Path(p)))
            print("==", p)
            for n, h in hits.items():
                if h.get("status") == "ok":
                    print("  ✓ %-32s %s row=%s" % (n, h["pack"], h["row"]))
                else:
                    print("  ✗ %-32s %s" % (n, h.get("status")))
        return 0
    return 2


def cmd_cdn(a) -> int:
    if a.action == "status":
        con = sqlite3.connect(CDN_DB)
        pk = con.execute("select count(*) from packs where ok=1").fetchone()[0]
        rows = con.execute("select count(*) from entries").fetchone()[0]
        print("CDN 索引：包 %d ｜ 条目 %d ｜ %s" % (pk, rows, CDN_DB))
        return 0
    if a.action == "find":
        q = a.query
        con = sqlite3.connect(CDN_DB)
        if re.fullmatch(r"[0-9A-Fa-f]{16}", q):
            fid = int(q, 16)
        else:
            fid = fid_of(_norm(q))
        row = con.execute("select pack,row,decoded from entries where fid_hi=? and fid_lo=? limit 1",
                          ((fid >> 32) & 0xFFFFFFFF, fid & 0xFFFFFFFF)).fetchone()
        print("fid %016X → %s" % (fid, row or "未命中"))
        if a.alt and not row:
            for ext in (".ktx", ".dds"):
                alt = re.sub(r"\.tga$", ext, q, flags=re.I)
                if alt == q:
                    continue
                f2 = fid_of(_norm(alt))
                r2 = con.execute("select pack,row from entries where fid_hi=? and fid_lo=? limit 1",
                                 ((f2 >> 32) & 0xFFFFFFFF, f2 & 0xFFFFFFFF)).fetchone()
                print("  换扩展 %-6s %016X → %s" % (ext, f2, r2 or "未命中"))
        return 0
    return 2
