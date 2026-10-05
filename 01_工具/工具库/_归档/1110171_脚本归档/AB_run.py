# -*- coding: utf-8 -*-
"""AB_run.py — task-15：A/B 两组渲染（运行时 fetch 拦截改写 neox_material.json 的 Tex0，唯一变量；不改任何默认文件）。
   用法: AB_run.py <A|B> <repeat> <port>
   产物: AB_<skin>_<G>[_r2].png / sha16 + AB_raw_<G>_r<rep>.json
"""
import asyncio, base64, hashlib, json, os, shutil, subprocess, sys, urllib.request
import websockets

CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
BOARD = 'http://127.0.0.1:8765/board.html?b=weapon_skin_sfx_text_sources&view=wiki&sort=id&dir=desc'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
SKINS = [s for s in os.environ.get('AB_SKINS', '1110024,1110129,1110145,1110152,1110165,1110171,1110177').split(',') if s]
WIN = '1400,1000'

GROUP = sys.argv[1] if len(sys.argv) > 1 else 'A'
REP = sys.argv[2] if len(sys.argv) > 2 else '1'
PORT = int(sys.argv[3]) if len(sys.argv) > 3 else 9931
PROF = os.path.join(os.environ.get('TEMP', OUT), 'AB_%s_r%s_prof' % (GROUP, REP))

# A 组映射：仅 weapon(非 crystal) prim 的 Tex0，且磁盘上存在同名 `_a`
b = json.load(open(os.path.join(OUT, 'AB_bindings.json'), encoding='utf-8'))
AMAP = {}
for skin, info in b['skins'].items():
    for r in info['prims']:
        t0 = (r['slots'].get('Tex0') or {})
        if r['kind'] == 'crystal':
            continue
        if t0.get('local_file') and t0.get('A_on_disk'):
            AMAP[t0['local_file']] = t0['A_local_file']

INSTALL = r"""
(function(){
  if(window.__abInstalled) return 'already';
  window.__AB_GROUP='%s';
  window.__AB_MAP=%s;
  window.__AB_REW=0; window.__AB_REWERR=null; window.__AB_PINNED=0;
  window.__abRewrite=function(txt){
    if(window.__AB_GROUP!=='A') return txt;
    try{
      var d=JSON.parse(txt); var M=window.__AB_MAP||{}; var n=0;
      (d.primitives||[]).forEach(function(pr){
        var T=pr.textures||{}; var t0=T.Tex0; if(!t0) return;
        var lf=t0.local_file;
        /* crystal 判定优先用 manifest 的 shader_kind（1110171 的 crystal prim 无 shader 字段，仅有 shader_kind）*/
        var kind=String(pr.shader_kind||'').toLowerCase();
        if(!kind) kind=(String(pr.shader||'').toLowerCase().indexOf('crystal')>=0)?'crystal':'weapon';
        if(lf && M[lf] && kind.indexOf('crystal')<0){ t0.__ab_orig=lf; t0.local_file=M[lf]; n++; }
      });
      window.__AB_REW=(window.__AB_REW||0)+n;
      return JSON.stringify(d);
    }catch(e){ window.__AB_REWERR=String((e&&e.message)||e); return txt; }
  };
  /* ★ 冻结基线：manifests/viewer.json 一律用会话开始时抓到的快照文本返回（A 组仅在其上改 Tex0），
     从而免疫其它成员对默认文件的并发编辑 —— A/B 的差异只剩 Tex0 一个变量。 */
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
""" % (GROUP, json.dumps(AMAP))

OPEN = "(()=>{window.__AB_REW=0;window.__AB_PINNED=0;window.WikiWeaponViewer.open({skin_id:'%s',poster:'assets/3d/weapon_skin/%s/poster.webp',preview_3d:{status:'ready',manifest:'assets/3d/weapon_skin/%s/viewer.json'}},{title:'%s'});return 1;})()"

WIKI_ROOT = r'E:\la拆包项目\08Lifeafter wiki'
DEFAULT_FILES = ([os.path.join(WIKI_ROOT, 'assets', '3d', 'weapon_skin', s, f)
                  for s in SKINS for f in ('neox_material.json', 'viewer.json')]
                 + [os.path.join(WIKI_ROOT, 'assets', 'weapon_skin_viewer.js')])


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
    res = {'group': GROUP, 'repeat': REP, 'port': PORT, 'window': WIN, 'a_map': AMAP, 'skins': {},
           'default_files_before': default_hashes()}
    FROZEN = {}
    for s in SKINS:
        try:
            nx = open(os.path.join(WIKI_ROOT, 'assets', '3d', 'weapon_skin', s, 'neox_material.json'), encoding='utf-8').read()
            vj = open(os.path.join(WIKI_ROOT, 'assets', '3d', 'weapon_skin', s, 'viewer.json'), encoding='utf-8').read()
            FROZEN[s] = {'neox': nx, 'viewer': vj,
                         'neox_sha16': hashlib.sha256(nx.encode()).hexdigest()[:16],
                         'viewer_sha16': hashlib.sha256(vj.encode()).hexdigest()[:16]}
        except Exception as ex:
            FROZEN[s] = {'neox': '{}', 'viewer': '{}', 'error': str(ex)}
    res['frozen'] = {s: {k: v for k, v in f.items() if k.endswith('sha16') or k == 'error'} for s, f in FROZEN.items()}
    try:
        pg = next(t for t in json.load(urllib.request.urlopen('http://127.0.0.1:%d/json' % PORT)) if t.get('type') == 'page')
        async with websockets.connect(pg['webSocketDebuggerUrl'], max_size=512 << 20) as ws:
            _i = 0; pending = {}

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
                    return 'EXC:' + json.dumps(rr['exceptionDetails'].get('text'))[:120]
                return (rr.get('result', {}) or {}).get('value')

            await send('Page.enable'); await send('Runtime.enable')
            await send('Page.navigate', url=BOARD); await asyncio.sleep(10)
            await ev("window.__AB_FROZEN=" + json.dumps(FROZEN) + ";1")
            res['install'] = await ev(INSTALL)
            res['hidePanels_page'] = await ev("(()=>{document.documentElement.style.margin='0';return JSON.stringify({w:window.innerWidth,h:window.innerHeight});})()")
            for skin in SKINS:
                await ev(OPEN % (skin, skin, skin, skin))
                await asyncio.sleep(14)
                row = {}
                row['rew_count'] = await ev("window.__AB_REW||0")
                row['pinned'] = await ev("window.__AB_PINNED||0")
                row['rew_err'] = await ev("window.__AB_REWERR||null")
                row['hidePanels'] = await ev("window.WikiWeaponViewer.__hidePanels(true)")
                await asyncio.sleep(0.6)
                row['sfx_frozen'] = await ev("(function(){var a=null,b=null;try{a=window.WikiWeaponViewer.__sfxTime(0);}catch(e){a='err'}try{b=window.WikiWeaponViewer.__sfxSeed(0);}catch(e){b='err'}return JSON.stringify({time:a,seed:b});})()")
                await asyncio.sleep(0.4)
                row['state'] = await ev("(function(){try{var s=window.WikiWeaponViewer.__state();if(!s)return null;return JSON.stringify({buffer:s.buffer,fov:s.fov,proj:s.proj,distance:s.distance,dpr:s.dpr,camPos:s.camPos});}catch(e){return 'err:'+e.message}})()")
                row['acceptance'] = await ev("(function(){try{return window.__acceptanceReport();}catch(e){return 'err:'+e.message}})()")
                row['viewer_sha'] = await ev("window.__VIEWER_SHA||null")
                snap = await ev("(function(){try{var s=window.WikiWeaponViewer.snapshot();if(!s||!s.png)return null;return JSON.stringify({w:s.w,h:s.h,mean:s.mean,mag:s.magenta_pct,gray:s.gray_pct,png:s.png});}catch(e){return 'err:'+e.message}})()")
                png_path = None
                if isinstance(snap, str) and snap.startswith('{'):
                    s = json.loads(snap); pngb64 = s.pop('png', None)
                    row['snapshot'] = s
                    if pngb64:
                        raw = base64.b64decode(pngb64.split(',', 1)[1])
                        name = 'AB_%s_%s%s.png' % (skin, GROUP, '' if REP == '1' else '_r' + REP)
                        png_path = os.path.join(OUT, name)
                        open(png_path, 'wb').write(raw)
                        row['png'] = name
                        row['png_sha16'] = hashlib.sha256(raw).hexdigest()[:16]
                        row['png_bytes'] = len(raw)
                else:
                    row['snapshot'] = snap
                res['skins'][skin] = row
                acc = row.get('acceptance')
                first = ''
                if isinstance(acc, str) and acc.strip().startswith('{'):
                    try:
                        a = json.loads(acc)
                        first = ' | '.join('%s->%s' % (m.get('chain_prim'), m.get('map')) for m in a.get('meshes', [])[:8])
                    except Exception:
                        pass
                print('[%s r%s] %-8s rew=%-3s snap=%s sha16=%s  map=%s' % (
                    GROUP, REP, skin, row.get('rew_count'), json.dumps(row.get('snapshot'), ensure_ascii=False),
                    row.get('png_sha16'), first[:220]))
                sys.stdout.flush()
    finally:
        try:
            pr.terminate()
        except Exception:
            pass
    out = os.path.join(OUT, 'AB_raw_%s_r%s.json' % (GROUP, REP))
    res['default_files_after'] = default_hashes()
    res['default_files_changed_during_run'] = sorted(k for k in res['default_files_before']
                                                     if res['default_files_before'][k] != res['default_files_after'].get(k))
    json.dump(res, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('默认文件运行期变更:', res['default_files_changed_during_run'] or '无')
    print('raw ->', out)


asyncio.run(main())
