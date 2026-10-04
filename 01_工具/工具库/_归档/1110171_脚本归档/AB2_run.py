# -*- coding: utf-8 -*-
"""AB2_run.py — task-23：1110024 的 t_custom_ibl 两组渲染（A=源声明 indoor.dds，B=现状 gdansk）。
   沿用 task-15 的冻结快照 + fetch 包装 + 固定布局；只写 AB2_*。
   用法: AB2_run.py <A|B> <repeat> <port>
"""
import asyncio, base64, hashlib, json, os, shutil, subprocess, sys, urllib.request
import websockets

CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
BOARD = 'http://127.0.0.1:8765/board.html?b=weapon_skin_sfx_text_sources&view=wiki&sort=id&dir=desc'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
WIKI_ROOT = r'E:\la拆包项目\08Lifeafter wiki'
SKIN = '1110024'
WIN = '1400,1000'
GROUP = sys.argv[1] if len(sys.argv) > 1 else 'A'
REP = sys.argv[2] if len(sys.argv) > 2 else '1'
PORT = int(sys.argv[3]) if len(sys.argv) > 3 else 9961
PROF = os.path.join(os.environ.get('TEMP', OUT), 'AB2_%s_r%s_prof' % (GROUP, REP))
DEFAULT_FILES = [os.path.join(WIKI_ROOT, 'assets', '3d', 'weapon_skin', SKIN, f) for f in ('neox_material.json', 'viewer.json')] + [
    os.path.join(WIKI_ROOT, 'assets', 'weapon_skin_viewer.js'),
    os.path.join(WIKI_ROOT, 'assets', 'weapon_skin_sfx_adapter.js')]

INSTALL = r"""
(function(){
  if(window.__abInstalled) return 'already';
  window.__AB_GROUP='%s';
  window.__AB_REW=0; window.__AB_REWERR=null; window.__AB_PINNED=0;
  window.__AB_IBL={'local_file':'src_cube/indoor.dds','faces_glob':'src_cube/faces/indoor_f{i}_m0.png','logical_path':'common\\env_map\\indoor.cube'};
  window.__abRewrite=function(txt){
    if(window.__AB_GROUP!=='A') return txt;
    try{
      var d=JSON.parse(txt); var n=0; var tgt=window.__AB_IBL;
      (d.primitives||[]).forEach(function(pr){
        var T=pr.textures||{}; var t=T.t_custom_ibl; if(!t) return;
        t.__ab_orig={local_file:t.local_file,faces_glob:t.faces_glob,logical_path:t.logical_path};
        t.local_file=tgt.local_file; t.faces_glob=tgt.faces_glob; t.logical_path=tgt.logical_path; n++;
      });
      window.__AB_REW=(window.__AB_REW||0)+n;
      return JSON.stringify(d);
    }catch(e){ window.__AB_REWERR=String((e&&e.message)||e); return txt; }
  };
  var of=window.fetch;
  window.fetch=function(u,o){
    var url=(typeof u==='string')?u:((u&&u.url)||'');
    var m=url.match(/weapon_skin\/(\d+)\/(neox_material|viewer)\.json/);
    if(m && window.__AB_FROZEN && window.__AB_FROZEN[m[1]]){
      var f=window.__AB_FROZEN[m[1]];
      var txt=(m[2]==='neox_material')?f.neox:f.viewer;
      if(m[2]==='neox_material' && window.__AB_GROUP==='A') txt=window.__abRewrite(txt);
      window.__AB_PINNED=(window.__AB_PINNED||0)+1;
      return Promise.resolve(new Response(txt,{status:200,headers:{'Content-Type':'application/json'}}));
    }
    return of.call(this,u,o);
  };
  window.__abInstalled=true; return 'ok';
})()
""" % GROUP

OPEN = ("(()=>{window.__AB_REW=0;window.__AB_PINNED=0;window.WikiWeaponViewer.open({skin_id:'%s',poster:'assets/3d/weapon_skin/%s/poster.webp',"
        "preview_3d:{status:'ready',manifest:'assets/3d/weapon_skin/%s/viewer.json'}},{title:'%s'});return 1;})()") % (SKIN, SKIN, SKIN, SKIN)


def default_hashes():
    out = {}
    for p in DEFAULT_FILES:
        try:
            out[os.path.relpath(p, WIKI_ROOT)] = hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]
        except Exception as e:
            out[os.path.relpath(p, WIKI_ROOT)] = 'ERR:' + e.__class__.__name__
    return out


async def main():
    shutil.rmtree(PROF, ignore_errors=True)
    pr = subprocess.Popen([CHROME, '--headless=new', '--disable-gpu', '--enable-unsafe-swiftshader', '--no-first-run',
                           '--hide-scrollbars', '--force-device-scale-factor=1', '--window-size=' + WIN,
                           '--remote-debugging-port=%d' % PORT, '--user-data-dir=%s' % PROF, 'about:blank'],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(4)
    res = {'group': GROUP, 'repeat': REP, 'skin': SKIN, 'window': WIN, 'default_files_before': default_hashes()}
    nx = open(os.path.join(WIKI_ROOT, 'assets', '3d', 'weapon_skin', SKIN, 'neox_material.json'), encoding='utf-8').read()
    vj = open(os.path.join(WIKI_ROOT, 'assets', '3d', 'weapon_skin', SKIN, 'viewer.json'), encoding='utf-8').read()
    FROZEN = {SKIN: {'neox': nx, 'viewer': vj, 'neox_sha16': hashlib.sha256(nx.encode()).hexdigest()[:16],
                     'viewer_sha16': hashlib.sha256(vj.encode()).hexdigest()[:16]}}
    res['frozen'] = {SKIN: {k: v for k, v in FROZEN[SKIN].items() if k.endswith('sha16')}}
    try:
        pg = next(t for t in json.load(urllib.request.urlopen('http://127.0.0.1:%d/json' % PORT)) if t.get('type') == 'page')
        async with websockets.connect(pg['webSocketDebuggerUrl'], max_size=512 << 20) as ws:
            _i = 0; pending = {}
            reqs = {}

            def on_event(m):
                me = m.get('method'); p = m.get('params') or {}
                if me == 'Network.responseReceived':
                    r = p.get('response') or {}
                    u = str(r.get('url'))
                    if 'src_cube' in u:
                        reqs[u.split('8765')[-1]] = r.get('status')

            async def pump():
                while True:
                    try:
                        raw = await ws.recv()
                    except Exception:
                        return
                    m = json.loads(raw)
                    if 'id' in m:
                        f = pending.pop(m['id'], None)
                        if f and not f.done():
                            f.set_result(m)
                    else:
                        on_event(m)
            task = asyncio.create_task(pump())

            async def send(method, **params):
                nonlocal _i
                _i += 1
                fut = asyncio.get_event_loop().create_future(); pending[_i] = fut
                await ws.send(json.dumps({'id': _i, 'method': method, 'params': params}))
                return await asyncio.wait_for(fut, timeout=240)

            async def ev(expr):
                r = await send('Runtime.evaluate', expression=expr, returnByValue=True, awaitPromise=True, timeout=240000)
                rr = r.get('result', {})
                if rr.get('exceptionDetails'):
                    return 'EXC:' + str(rr['exceptionDetails'].get('text'))[:120]
                return (rr.get('result', {}) or {}).get('value')

            await send('Page.enable'); await send('Runtime.enable'); await send('Network.enable')
            await send('Page.navigate', url=BOARD); await asyncio.sleep(10)
            await ev("window.__AB_FROZEN=" + json.dumps(FROZEN) + ";1")
            res['install'] = await ev(INSTALL)
            await ev(OPEN)
            await asyncio.sleep(14)
            res['rew_count'] = await ev("window.__AB_REW||0")
            res['pinned'] = await ev("window.__AB_PINNED||0")
            res['rew_err'] = await ev("window.__AB_REWERR||null")
            res['hidePanels'] = await ev("window.WikiWeaponViewer.__hidePanels(true)")
            await asyncio.sleep(0.6)
            res['sfx'] = await ev("(function(){var a=null,b=null;try{a=window.WikiWeaponViewer.__sfxTime(0);}catch(e){a='err'}try{b=window.WikiWeaponViewer.__sfxSeed(0);}catch(e){b='err'}return JSON.stringify({time:a,seed:b});})()")
            await asyncio.sleep(0.4)
            res['state'] = await ev("(function(){try{var s=window.WikiWeaponViewer.__state();if(!s)return null;return JSON.stringify({buffer:s.buffer,fov:s.fov,proj:s.proj,dpr:s.dpr,camPos:s.camPos});}catch(e){return 'err:'+e.message}})()")
            res['acceptance'] = await ev("(function(){try{return window.__acceptanceReport();}catch(e){return 'err:'+e.message}})()")
            res['viewer_sha'] = await ev("window.__VIEWER_SHA||null")
            snap = await ev("(function(){try{var s=window.WikiWeaponViewer.snapshot();if(!s||!s.png)return null;return JSON.stringify({w:s.w,h:s.h,mean:s.mean,mag:s.magenta_pct,gray:s.gray_pct,png:s.png});}catch(e){return 'err:'+e.message}})()")
            if isinstance(snap, str) and snap.startswith('{'):
                s = json.loads(snap); b64 = s.pop('png', None)
                res['snapshot'] = s
                if b64:
                    raw = base64.b64decode(b64.split(',', 1)[1])
                    name = 'AB2_%s_%s%s.png' % (SKIN, GROUP, '' if REP == '1' else '_r' + REP)
                    open(os.path.join(OUT, name), 'wb').write(raw)
                    res['png'] = name
                    res['png_sha16'] = hashlib.sha256(raw).hexdigest()[:16]
                    res['png_bytes'] = len(raw)
            else:
                res['snapshot'] = snap
            res['cube_requests'] = reqs
    finally:
        try:
            pr.terminate()
        except Exception:
            pass
    res['default_files_after'] = default_hashes()
    res['default_files_changed_during_run'] = sorted(k for k in res['default_files_before'] if res['default_files_before'][k] != res['default_files_after'].get(k))
    out = os.path.join(OUT, 'AB2_raw_%s_r%s.json' % (GROUP, REP))
    json.dump(res, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('[AB2 %s r%s] rew=%s pinned=%s viewer_sha=%s snapshot=%s sha16=%s' % (
        GROUP, REP, res['rew_count'], res['pinned'], res['viewer_sha'], json.dumps(res.get('snapshot'), ensure_ascii=False), res.get('png_sha16')))
    acc = res.get('acceptance')
    if isinstance(acc, str) and acc.strip().startswith('{'):
        a = json.loads(acc)
        for m in a.get('meshes', []):
            print('   prim%-2s map=%-26s ibl_faces=%s env=%s' % (m.get('chain_prim'), m.get('map'),
                  (len(m['ibl_faces']) if m.get('ibl_faces') is not None else None), m.get('envMap')))
    for u, st in sorted(reqs.items()):
        print('   %-5s %s' % (st, u))
    print('默认文件运行期变更:', res['default_files_changed_during_run'] or '无')
    print('raw ->', out)


asyncio.run(main())
