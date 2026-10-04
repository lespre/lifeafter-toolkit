# -*- coding: utf-8 -*-
"""T5 验收：在 lab=1 与生产两种模式下打开 1110177，取 __neox() / 槽位绑定表 / 截图 / 编译状态。"""
import asyncio, json, os, shutil, subprocess, urllib.request, base64, hashlib
import websockets

CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
BASE = 'http://127.0.0.1:8765/board.html?b=weapon_skin_sfx_text_sources&view=wiki&sort=id&dir=desc'
OUT = os.path.dirname(os.path.abspath(__file__))
REL = 'assets/3d/weapon_skin/1110177'
PORT = 9981

HOOK = r"""
(function(){
  window.__SH={fails:[],linkFails:[],useInvalid:0,logs:[]};
  var P=(window.WebGL2RenderingContext||{}).prototype; if(!P) return;
  var _cs=P.compileShader,_gs=P.getShaderParameter,_gsil=P.getShaderInfoLog,_lp=P.linkProgram,
      _gpa=P.getProgramParameter,_gpil=P.getProgramInfoLog,_up=P.useProgram;
  var pOk=new WeakMap();
  P.compileShader=function(sh){ var r=_cs.apply(this,arguments);
    try{ if(!_gs.call(this,sh,this.COMPILE_STATUS)) window.__SH.fails.push(String(_gsil.call(this,sh)||'').slice(0,1200)); }catch(e){} return r; };
  P.linkProgram=function(pr){ var r=_lp.apply(this,arguments);
    try{ var ok=!!_gpa.call(this,pr,this.LINK_STATUS); pOk.set(pr,ok);
         if(!ok) window.__SH.linkFails.push(String(_gpil.call(this,pr)||'').slice(0,300)); }catch(e){} return r; };
  P.useProgram=function(pr){ try{ if(pOk.has(pr)&&pOk.get(pr)===false) window.__SH.useInvalid++; }catch(e){} return _up.apply(this,arguments); };
})();
"""


async def run(url, tag, wait_render=26):
    prof = os.path.join(OUT, '_prof_' + tag)
    shutil.rmtree(prof, ignore_errors=True)
    p = subprocess.Popen([CHROME, '--headless=new', '--disable-gpu', '--enable-unsafe-swiftshader',
                          '--no-first-run', '--hide-scrollbars', '--force-device-scale-factor=1',
                          '--window-size=1400,950', '--remote-debugging-port=%d' % PORT,
                          '--user-data-dir=%s' % prof, 'about:blank'],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(4)
    out = {'url': url, 'tag': tag}
    try:
        pg = next(t for t in json.load(urllib.request.urlopen('http://127.0.0.1:%d/json' % PORT))
                  if t.get('type') == 'page')
        async with websockets.connect(pg['webSocketDebuggerUrl'], max_size=256 << 20) as ws:
            i = {'n': 0}; pend = {}

            async def rd():
                try:
                    async for raw in ws:
                        m = json.loads(raw)
                        if 'id' in m: pend[m['id']] = m
                except Exception: pass
            t = asyncio.create_task(rd())

            async def send(method, **pp):
                i['n'] += 1; k = i['n']
                await ws.send(json.dumps(dict(id=k, method=method, params=pp)))
                for _ in range(900):
                    if k in pend: return pend.pop(k).get('result', {})
                    await asyncio.sleep(0.02)
                return {}

            async def ev(e):
                r = await send('Runtime.evaluate', expression=e, returnByValue=True, awaitPromise=True)
                if r.get('exceptionDetails'): return 'EXC ' + str(r['exceptionDetails'].get('text'))[:300]
                return (r.get('result', {}) or {}).get('value')

            await send('Page.enable'); await send('Runtime.enable'); await send('Log.enable')
            await send('Page.addScriptToEvaluateOnNewDocument', source=HOOK)
            await send('Page.navigate', url=url); await asyncio.sleep(10)
            out['hook'] = await ev("typeof window.__SH")
            await ev("(()=>{window.WikiWeaponViewer.open({skin_id:'1110177',poster:'%s/poster.webp',"
                     "preview_3d:{status:'ready',manifest:'%s/viewer.json'}},{title:'极光剑'});return 1;})()" % (REL, REL))
            nx = None
            for _ in range(60):
                nx = await ev("JSON.stringify(window.WikiWeaponViewer.__neox&&window.WikiWeaponViewer.__neox())")
                if nx and 'applied' in str(nx): break
                await asyncio.sleep(2)
            await asyncio.sleep(wait_render)
            out['neox'] = nx
            # 槽位状态表
            out['slots'] = await ev("""JSON.stringify((()=>{
              const r=window.WikiWeaponViewer, st=r.neoxState?r.neoxState():null;
              const rep=JSON.parse((r.__neox&&r.__neox())||'{}');
              const rows=[];
              (rep.prims||rep.report&&rep.report.prims||[]).forEach(function(pr){
                Object.keys(pr.slots||{}).forEach(function(k){
                  rows.push({prim:pr.prim, mtl:pr.material, status:pr.status, slot:k,
                             file:(pr.slots[k]||{}).file||null, logical:(pr.slots[k]||{}).logical||null,
                             cs:(pr.slots[k]||{}).color_space||null}); }); });
              return {rows:rows, materials:(st&&st.materials||[]).map(function(m){return {type:m.type,map_loaded:m.map_loaded,uuid:m.uuid};}),
                      report_ok:(rep.report?{applied:rep.report.applied,failed:rep.report.failed,missing:rep.report.missing}:null)};})())""")
            out['gl'] = await ev("JSON.stringify({fails:(window.__SH.fails||[]).length,linkFails:(window.__SH.linkFails||[]).length,useInvalid:window.__SH.useInvalid,first:(window.__SH.fails||[])[0]||null})")
            await ev("(()=>{document.querySelectorAll('.wv-poster,.wv-loading,.wv-status,.wv-tools,.wv-params,.wv-tabs').forEach(e=>e.style.display='none');return 1;})()")
            await asyncio.sleep(1)
            box = await ev("JSON.stringify((()=>{const c=document.querySelector('.wv-canvas canvas')||document.querySelector('canvas');if(!c)return null;const b=c.getBoundingClientRect();return {x:Math.round(b.x),y:Math.round(b.y),w:Math.round(b.width),h:Math.round(b.height)};})())")
            try:
                bx = json.loads(box or 'null')
            except Exception:
                bx = None
            if bx and bx['w'] > 10:
                s = await send('Page.captureScreenshot', format='png',
                               clip=dict(x=bx['x'], y=bx['y'], width=bx['w'], height=bx['h'], scale=1))
                raw = base64.b64decode(s['data'])
                fn = 'T5_1110177_%s.png' % tag
                open(os.path.join(OUT, fn), 'wb').write(raw)
                out['screenshot'] = {'file': fn, 'sha16': hashlib.sha256(raw).hexdigest()[:16], 'box': bx, 'bytes': len(raw)}
            else:
                out['screenshot'] = {'error': 'canvas not found', 'box': bx}
            t.cancel()
    finally:
        try: p.terminate()
        except Exception: pass
    return out


async def main():
    res = []
    res.append(await run(BASE + '&lab=1', 'lab'))
    res.append(await run(BASE, 'prod'))
    json.dump(res, open(os.path.join(OUT, '_t5_accept.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for r in res:
        print('=' * 30, r['tag'], '=' * 30)
        print('  neox:', str(r.get('neox'))[:260])
        print('  gl:', str(r.get('gl'))[:300])
        print('  shot:', str(r.get('screenshot'))[:200])
        try:
            sl = json.loads(r.get('slots') or '{}')
            for row in sl.get('rows', []):
                print('   prim%d %-26s %-9s %-16s file=%-22s cs=%s' % (row['prim'], row['mtl'], row['status'],
                                                                       row['slot'], row['file'], row['cs']))
        except Exception as e:
            print('  slots parse fail', e)
    print('[saved] _t5_accept.json')


asyncio.run(main())
