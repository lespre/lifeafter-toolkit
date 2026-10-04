# -*- coding: utf-8 -*-
"""shader_ab_causality_probe.py — task-3 因果 A/B（只读）：
  baseline(链材质,程序编译失败)  vs  __l0(同一批 mesh 换成能编译的 MeshBasicMaterial+纯红)
  vs  __primSolid(MeshBasicMaterial 调色板) vs __ladderL1(锚点注入但 uniform 未声明)
同时抓取失败片元着色器的完整源码，核对 uniform 声明。
输出仅写本目录，文件名前缀 shader_。
"""
import asyncio, json, os, shutil, subprocess, urllib.request, base64, hashlib, io
import websockets
import numpy as np
from PIL import Image

CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
URL = ('http://127.0.0.1:8765/board.html?b=weapon_skin_sfx_text_sources'
       '&view=wiki&sort=id&dir=desc&lab=1')
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
PORT = 9973
REL = 'assets/3d/weapon_skin/1110171'

HOOK = r"""
(function(){
  window.__SH = {fails:[], linkFails:[], useInvalid:0, logs:[], fullSrc:[], seen:{}};
  var back = window.console;
  ['error','warn'].forEach(function(k){
    var o = back[k] ? back[k].bind(back) : function(){};
    back[k] = function(){ try{ window.__SH.logs.push(k+'|'+String([].slice.call(arguments).join(' ')).slice(0,2500)); }catch(e){} return o.apply(null, arguments); };
  });
  var P = (window.WebGL2RenderingContext||{}).prototype;
  if(!P){ window.__SH.note='no WebGL2'; return; }
  var _ss=P.shaderSource,_cs=P.compileShader,_gs=P.getShaderParameter,_gsil=P.getShaderInfoLog,
      _att=P.attachShader,_lp=P.linkProgram,_gpa=P.getProgramParameter,_gpil=P.getProgramInfoLog,
      _up=P.useProgram;
  var sSrc=new WeakMap(), pSh=new WeakMap(), pOk=new WeakMap();
  P.shaderSource=function(sh,src){ try{ sSrc.set(sh,String(src)); }catch(e){} return _ss.apply(this,arguments); };
  P.compileShader=function(sh){
    var r=_cs.apply(this,arguments);
    try{
      var ok=false, log='', src='';
      try{ ok=!!_gs.call(this,sh,this.COMPILE_STATUS); }catch(e){}
      try{ log=_gsil.call(this,sh)||''; }catch(e){}
      try{ src=sSrc.get(sh)||''; }catch(e){}
      if(!ok){
        window.__SH.fails.push(String(log).slice(0,3000));
        if(window.__SH.fullSrc.length<3 && src.indexOf('uCustomIbl')>=0){ window.__SH.fullSrc.push(src); }
      }
    }catch(e){}
    return r;
  };
  P.attachShader=function(pr,sh){ try{ var a=pSh.get(pr)||[]; a.push(sh); pSh.set(pr,a); }catch(e){} return _att.apply(this,arguments); };
  P.linkProgram=function(pr){
    var r=_lp.apply(this,arguments);
    try{ var ok=!!_gpa.call(this,pr,this.LINK_STATUS); pOk.set(pr,ok);
         if(!ok){ window.__SH.linkFails.push(String(_gpil.call(this,pr)||'').slice(0,300)); } }catch(e){}
    return r;
  };
  P.useProgram=function(pr){ try{ if(pOk.has(pr)&&pOk.get(pr)===false) window.__SH.useInvalid++; }catch(e){} return _up.apply(this,arguments); };
  window.__SH.stat=function(){ return {fails:window.__SH.fails.length, linkFails:window.__SH.linkFails.length,
      useInvalid:window.__SH.useInvalid, fullSrc:window.__SH.fullSrc.length, logs:window.__SH.logs.length}; };
  window.__SH.dump=function(){ return {stat:window.__SH.stat(),
      fails:window.__SH.fails.map(function(s){return String(s).slice(0,2500);}),
      logs:window.__SH.logs.slice(-30)}; };
})();
"""


def png_stats(png_b64):
    raw = base64.b64decode(png_b64.split(',', 1)[-1])
    a = np.asarray(Image.open(io.BytesIO(raw)).convert('RGB')).astype(np.int16)
    return raw, a


def main_cmp(name, a, base):
    diff = (np.abs(a - base).max(axis=2) > 30)
    red = (a[:, :, 0] > 150) & (a[:, :, 1] < 80) & (a[:, :, 2] < 80)
    ys, xs = np.where(diff)
    box = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())] if len(xs) else None
    return {'state': name, 'changed_px_vs_baseline': int(diff.sum()),
            'changed_pct': round(100.0 * diff.sum() / diff.size, 2),
            'strong_red_px': int(red.sum()), 'bbox': box,
            'mean': [round(float(v), 1) for v in a.reshape(-1, 3).mean(0)]}


async def main():
    prof = os.path.join(OUT, '_profSHADERAB')
    shutil.rmtree(prof, ignore_errors=True)
    p = subprocess.Popen([CHROME, '--headless=new', '--disable-gpu', '--enable-unsafe-swiftshader',
                          '--no-first-run', '--hide-scrollbars', '--force-device-scale-factor=1',
                          '--window-size=1240,900', '--remote-debugging-port=%d' % PORT,
                          '--user-data-dir=%s' % prof, 'about:blank'],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(4)
    rep = {'results': [], 'commands': []}
    try:
        pg = next(t for t in json.load(urllib.request.urlopen('http://127.0.0.1:%d/json' % PORT))
                  if t.get('type') == 'page')
        async with websockets.connect(pg['webSocketDebuggerUrl'], max_size=256 << 20) as ws:
            _i = {'n': 0}
            pending = {}

            async def reader():
                try:
                    async for raw in ws:
                        m = json.loads(raw)
                        if 'id' in m:
                            pending[m['id']] = m
                except Exception:
                    pass

            task = asyncio.create_task(reader())

            async def send(method, **pp):
                _i['n'] += 1
                i = _i['n']
                await ws.send(json.dumps(dict(id=i, method=method, params=pp)))
                for _ in range(800):
                    if i in pending:
                        return pending.pop(i).get('result', {})
                    await asyncio.sleep(0.02)
                return {}

            async def ev(expr):
                r = await send('Runtime.evaluate', expression=expr, returnByValue=True, awaitPromise=True)
                if r.get('exceptionDetails'):
                    return 'EXC ' + str(r['exceptionDetails'].get('text'))[:300]
                return (r.get('result', {}) or {}).get('value')

            async def shot(tag):
                d = await ev("JSON.stringify(window.WikiWeaponViewer.snapshot())")
                try:
                    s = json.loads(d or '{}')
                except Exception:
                    s = {}
                if not s.get('png'):
                    return None, None, {'error': str(s)[:200]}
                raw, a = png_stats(s['png'])
                open(os.path.join(OUT, 'shader_AB_%s.png' % tag), 'wb').write(raw)
                return a, raw, {'png_sha16': hashlib.sha256(raw).hexdigest()[:16]}

            await send('Page.enable')
            await send('Runtime.enable')
            await send('Log.enable')
            await send('Page.addScriptToEvaluateOnNewDocument', source=HOOK)
            await send('Page.navigate', url=URL)
            await asyncio.sleep(10)
            await ev("(()=>{window.WikiWeaponViewer.open({skin_id:'1110171',poster:'%s/poster.webp',"
                     "preview_3d:{status:'ready',manifest:'%s/viewer.json'}},{title:'x'});return 1;})()"
                     % (REL, REL))
            for _ in range(45):
                nx = await ev("JSON.stringify(window.WikiWeaponViewer.__neox&&window.WikiWeaponViewer.__neox())")
                if nx and 'applied' in str(nx):
                    break
                await asyncio.sleep(2)
            await asyncio.sleep(8)

            rep['neox_applied'] = 'applied' in str(nx)
            rep['gl_stat_chain'] = await ev("JSON.stringify(window.__SH.stat())")
            rep['programs_chain'] = await ev("JSON.stringify((()=>{const c=window.WikiWeaponViewer.__ladderCompile();"
                                             "return {n:c.program_count,bad:c.programs.filter(p=>p.fragment_compile===false||p.program_link===false).length,"
                                             "keys:c.programs.filter(p=>p.fragment_compile===false).map(p=>String(p.cacheKey).slice(0,34)),"
                                             "firstlog:(c.programs.find(p=>p.fragment_compile===false)||{}).fragment_info_log};})())")

            base_a, base_raw, base_m = await shot('baseline_chain')
            rep['commands'].append('snapshot() @ chain material')
            rep['baseline'] = base_m
            rep['baseline']['png_sha16'] = hashlib.sha256(base_raw).hexdigest()[:16] if base_raw else None

            # --- A/B 1: __l0 把 chain mesh 换成可编译的 MeshBasicMaterial + 纯红 ---
            r = await ev("JSON.stringify(window.WikiWeaponViewer.__l0({mode:'both'}))")
            await asyncio.sleep(3)
            a1, raw1, m1 = await shot('l0_both_red')
            if a1 is not None:
                rep['results'].append(main_cmp('__l0 both -> 纯红 (可编译程序)', a1, base_a))
            rep['commands'].append('__l0({mode:"both"}) -> snapshot() -> __l0({mode:"off"})')
            rep['l0_draws'] = await ev("JSON.stringify((()=>{const j=JSON.parse(window.WikiWeaponViewer.__l0Info()||'{}');"
                                       "return {draws:(j.draws||[]).length, per_prim_visible:(j.draws||[]).map(d=>d.prim+':'+d.visible).slice(0,10),"
                                       "matTypes:[...new Set((j.draws||[]).map(d=>d.matType))]};})())")
            await ev("JSON.stringify(window.WikiWeaponViewer.__l0({mode:'off'}))")
            await asyncio.sleep(2)

            # --- A/B 2: __primSolid 调色板 ---
            await ev("window.__primSolid(true)")
            await asyncio.sleep(3)
            a2, raw2, m2 = await shot('primsolid_on')
            if a2 is not None:
                rep['results'].append(main_cmp('__primSolid(true) 调色板 MeshBasicMaterial', a2, base_a))
            rep['commands'].append('window.__primSolid(true) -> snapshot() -> window.__primSolid(false)')
            await ev("window.__primSolid(false)")
            await asyncio.sleep(2)

            # --- A/B 3: __ladderL1（锚点注入 + 未声明的 uDiagColor） ---
            await ev("JSON.stringify(window.WikiWeaponViewer.__ladderL1({mode:'red'}))")
            await asyncio.sleep(3)
            a3, raw3, m3 = await shot('ladder_l1_red')
            if a3 is not None:
                rep['results'].append(main_cmp('__ladderL1 red (锚点注入,uDiagColor 未声明)', a3, base_a))
            rep['gl_stat_after_ladder'] = await ev("JSON.stringify(window.__SH.stat())")
            rep['commands'].append('__ladderL1({mode:"red"}) -> snapshot() -> __ladderL1({mode:"off"})')
            await ev("JSON.stringify(window.WikiWeaponViewer.__ladderL1({mode:'off'}))")
            await asyncio.sleep(2)

            # 还原链材质后基线复现
            await ev("JSON.stringify(window.WikiWeaponViewer.__l0({mode:'off'}))")
            await asyncio.sleep(2)
            a4, raw4, m4 = await shot('restored_chain')
            if a4 is not None and base_a is not None:
                rep['results'].append(main_cmp('还原链材质（应与 baseline 逐字节一致）', a4, base_a))
            if a4 is not None:
                rep['restored_png_sha16'] = hashlib.sha256(raw4).hexdigest()[:16]

            # 失败片元着色器源码中的 uniform 声明核对
            rep['uniform_decl_check'] = await ev("""JSON.stringify((()=>{
              var P=window.__SH; if(!P||!P.fullSrc||!P.fullSrc.length) return {n:0};
              var s=P.fullSrc[0];
              var out={n:P.fullSrc.length, len:s.length};
              out.has_uCustomIbl_decl = /uniform\\s+samplerCube\\s+uCustomIbl\\s*;/.test(s);
              out.has_uIblStrength_decl = /uniform\\s+float\\s+uIblStrength\\s*;/.test(s);
              out.has_uIblRot_decl = /uniform\\s+float\\s+uIblRot\\s*;/.test(s);
              out.has_uIblMix_decl = /uniform\\s+float\\s+uIblMix\\s*;/.test(s);
              out.has_uIblScale_decl = /uniform\\s+float\\s+uIblScale\\s*;/.test(s);
              out.uses_uIblStrength = /uIblStrength/.test(s);
              var m=s.match(/uniform\\s+\\w+\\s+u[A-Za-z0-9_]+\\s*;/g)||[];
              out.declared_uniforms = m.slice(0,40);
              return out;})())""")

            rep['gl'] = await ev("JSON.stringify(window.__SH.dump())")
            task.cancel()
    finally:
        try:
            p.terminate()
        except Exception:
            pass
    with open(os.path.join(OUT, 'shader_ab_causality.json'), 'w', encoding='utf-8') as f:
        json.dump(rep, f, ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in rep.items() if k != 'gl'}, ensure_ascii=False, indent=1))


asyncio.run(main())
