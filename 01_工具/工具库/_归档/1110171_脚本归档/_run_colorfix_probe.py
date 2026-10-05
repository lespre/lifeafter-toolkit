# -*- coding: utf-8 -*-
"""补充定证（只读）：
 P1 `COLOR_ORDER` 作用域遮蔽：模块级默认 'argb' 是否真的到达三条消费路径？
    —— 冻结同一帧，比较 colorOrder('argb'|'rgba') 的帧 sha；并读 attach 期自适应报告里的 color_order 值。
 P2 1110171 的 4 个 Sprite 到底有没有画进帧里？—— `__probe()`/`__sfxDiag()` 逐 sprite 的
    visible/opacity/scale/worldPos/hasMap，及 renderer.info.render.triangles/calls，
    以及在 sprite 世界位置处做"该 sprite 单独隐藏"的像素差（sprite.material.opacity=0 前后）。
 单浏览器 profile FXVA95_prof / 端口 10169。
"""
import asyncio, base64, hashlib, io, json, os, shutil, subprocess, sys, time, urllib.request

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass
import websockets
import numpy as np
from PIL import Image

CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
W = r'E:\la拆包项目\08Lifeafter wiki'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
SHOTS = os.path.join(OUT, 'sfx_verify_shots12')
TMP = os.environ['TEMP']
PORT = 10169
PROFILE = os.path.join(TMP, 'FXVA95_prof')
BOARD = 'http://127.0.0.1:8765/board.html?b=weapon_skin_sfx_text_sources&view=wiki'
J = os.path.join(OUT, 'COLORFIX_probe_20260920.json')

RES = {'stage': 'init'}
dump = lambda: json.dump(RES, open(J, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


class CDP:
    def __init__(self, ws):
        self.ws, self._i, self._f = ws, 0, {}
        self.console, self.exc, self.eval_exc = [], [], []

    async def start(self):
        self._r = asyncio.create_task(self._read())

    async def _read(self):
        try:
            async for raw in self.ws:
                m = json.loads(raw)
                if 'id' in m:
                    f = self._f.pop(m['id'], None)
                    if f and not f.done():
                        f.set_result(m)
                elif m.get('method') == 'Runtime.exceptionThrown':
                    x = m['params'].get('exceptionDetails', {})
                    self.exc.append({'text': (x.get('text') or '')[:140]})
        except Exception:
            pass

    async def send(self, m, **p):
        self._i += 1
        fut = asyncio.get_running_loop().create_future()
        self._f[self._i] = fut
        await self.ws.send(json.dumps({'id': self._i, 'method': m, 'params': p}))
        r = await asyncio.wait_for(fut, 90)
        if 'error' in r:
            raise RuntimeError(str(r['error']))
        return r.get('result', {})

    async def ev(self, e, awaitP=True):
        r = await self.send('Runtime.evaluate', expression=e, returnByValue=True, awaitPromise=awaitP)
        if r.get('exceptionDetails'):
            x = r['exceptionDetails']
            self.eval_exc.append({'expr': e[:70], 'text': (x.get('text') or '')[:120]})
            return {'__exc__': (x.get('text') or '')[:120]}
        return (r.get('result') or {}).get('value')


async def shot(c):
    s = await c.send('Page.captureScreenshot', format='png')
    return base64.b64decode(s.get('data', ''))


async def gate(c, n=5, tries=16):
    shas, raw = [], None
    for _ in range(tries):
        raw = await shot(c)
        shas.append(hashlib.sha256(raw).hexdigest()[:16])
        if len(shas) >= n and len(set(shas[-n:])) == 1:
            return raw, shas[-1], True, shas
        await asyncio.sleep(0.9)
    return raw, shas[-1], False, shas


def rgb(x):
    img = Image.open(io.BytesIO(x)) if isinstance(x, bytes) else Image.open(x)
    return np.asarray(img.convert('RGB')).astype(np.float32) / 255.0


def diff_info(a, b, thr=0.0):
    h = min(a.shape[0], b.shape[0]); w = min(a.shape[1], b.shape[1])
    d = np.abs(a[:h, :w] - b[:h, :w])
    dd = d.max(axis=2)
    n = int((dd > thr).sum())
    o = {'changed_px': n, 'max_diff': round(float(dd.max()), 5)}
    if n:
        ys, xs = np.nonzero(dd > thr)
        o['bbox'] = [int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max())]
    return o


PROBE_JS = """(function(){try{
 var A=window.WikiSfxAdapter; var p=(typeof A.__probe==='function')?A.__probe():null;
 var d=(typeof A.__sfxDiag==='function')?A.__sfxDiag():null;
 var out={colorOrder_report:(d&&d.color_order)||null,
          sprites:(p&&p.sprites)?p.sprites:null,
          groupVisible:(p&&p.groupVisible), enabled:(p&&p.enabled), fixedTime:(p&&p.fixedTime)};
 try{
   var r=window.WikiWeaponViewer;
   var st=null;
   // 找 viewer 的 state（通过 __texReady 拿不到 renderer；改用全局搜 canvas 的 __three）
 }catch(e){}
 return JSON.stringify(out);
}catch(e){return 'ERR '+e.message;}})()"""

# 直接遍历场景里由 adapter 建的 sprite：通过 __probe().sprites 的名字 + 手动开关 material.opacity
HIDE_JS = """(function(){
 try{
  var A=window.WikiSfxAdapter; var p=A.__probe?A.__probe():null;
  if(!p||!p.sprites) return 'NO_PROBE';
  var rep={};
  // adapter 的 sprite 挂在 scene 上：用同名 Object3D 找（name 由 adapter 设置或 userData.nodeName）
  var hits=[];
  function walk(o,depth){ if(!o) return; if(o.isMesh||o.isSprite){ var nm=(o.userData&&o.userData.nodeName)||o.name||null;
      if(nm) hits.push({nm:nm, type:o.type, vis:!!o.visible, op:(o.material?(+o.material.opacity).toFixed(4):null),
                        blending:(o.material?o.material.blending:null), hasMap:!!(o.material&&o.material.map),
                        scale:o.scale?+(o.scale.x).toFixed(4):null,
                        wpos:(o.getWorldPosition?[(+o.getWorldPosition(new (o.position.constructor)()).x).toFixed(3),(+o.getWorldPosition(new (o.position.constructor)()).y).toFixed(3),(+o.getWorldPosition(new (o.position.constructor)()).z).toFixed(3)]:null)}); }
    for(var i=0;i<(o.children||[]).length;i++) walk(o.children[i], depth+1); }
  try{ var sc=window.WikiWeaponViewer; }catch(e){}
  return 'NEED_SCENE';
 }catch(e){return 'ERR '+e.message;}})()"""

SCENE_JS = """(function(){
 try{
  var out={};
  // 通过 three 的 Object3D 反查：找挂点 root —— viewer 把 adapter 的 group 加到 scene 上
  var found=null;
  // three 实例：从 canvas 的 WebGLRenderer 无从取；改用 adapter 内 __probe().sprites 的名字 +
  // 全局 THREE 若存在
  var T=window.THREE;
  if(!T) return 'NO_THREE';
  return 'HAS_THREE';
 }catch(e){return 'ERR '+e.message;}})()"""


async def main():
    os.makedirs(SHOTS, exist_ok=True)
    dump()
    shutil.rmtree(PROFILE, ignore_errors=True)
    pr = subprocess.Popen([CHROME, '--headless=new', '--disable-gpu', '--enable-unsafe-swiftshader', '--no-first-run',
                           '--hide-scrollbars', '--force-device-scale-factor=1', '--force-color-profile=srgb',
                           '--window-size=1600,1000', '--remote-debugging-port=%d' % PORT,
                           '--user-data-dir=%s' % PROFILE, 'about:blank'],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    killed = []
    try:
        pg = None
        for _ in range(30):
            await asyncio.sleep(1)
            try:
                pg = next((t for t in json.load(urllib.request.urlopen('http://127.0.0.1:%d/json' % PORT, timeout=3))
                           if t.get('type') == 'page'), None)
                if pg:
                    break
            except Exception:
                pass
        async with websockets.connect(pg['webSocketDebuggerUrl'], max_size=1 << 28, max_queue=None) as ws:
            c = CDP(ws)
            await c.start()
            await c.send('Page.enable'); await c.send('Runtime.enable')
            hook = ("window.__errs=[];window.addEventListener('error',function(e){try{window.__errs.push(String((e&&e.message)||e));}catch(x){}});")
            await c.send('Page.addScriptToEvaluateOnNewDocument', source=hook)
            await c.send('Page.navigate', url=BOARD); await asyncio.sleep(20)
            for _ in range(3):
                await shot(c); await asyncio.sleep(1.0)

            # --- P1: 1110177 冻结同一帧，切 colorOrder，看帧 sha 是否变 ---
            await c.ev("(async function(id){var s=(window.WEAPON_SKIN_MEDIA||{}).skins||{};await window.WikiWeaponViewer.open(s[id],{title:'x'});return 'ok';})('1110177')")
            await asyncio.sleep(12)
            await c.ev("String(window.WikiWeaponViewer.__post(false))")
            await c.ev("String(window.WikiWeaponViewer.__hidePanels(true))")
            await asyncio.sleep(1.0)
            await c.ev("(function(){var b=document.querySelector('.wv-sfx');if(b&&!b.disabled&&b.getAttribute('aria-pressed')!=='true')b.click();return 'on';})()")
            await asyncio.sleep(2.5)
            await c.ev("String(window.WikiWeaponViewer.__sfxTime(0.3))")
            await asyncio.sleep(1.0)
            P1 = {'note': '同一冻结帧 t=0.30，只切 colorOrder，看帧是否逐字节相同'}
            seq = []
            for v in ('argb', 'rgba', 'argb'):
                await c.ev("(function(){return JSON.stringify(window.WikiSfxAdapter.colorOrder('%s'));})()" % v)
                await asyncio.sleep(2.0)
                raw, sha, okg, series = await gate(c, 5)
                fn = 'c177_colororder_%s_t0030.png' % v
                open(os.path.join(SHOTS, fn), 'wb').write(raw)
                pr_ = await c.ev(PROBE_JS)
                try:
                    pj = json.loads(pr_)
                except Exception:
                    pj = {'raw': str(pr_)[:200]}
                seq.append({'call': "colorOrder('%s')" % v, 'file': fn, 'sha16': sha, 'gate_ok': okg,
                            'series': series, 'color_order_report': pj.get('colorOrder_report'),
                            'sprites': pj.get('sprites')})
                print('P1 colorOrder(%s) -> %s (report=%s)' % (v, sha, pj.get('colorOrder_report')))
                dump()
            P1['seq'] = seq
            P1['sha_argb'] = seq[0]['sha16']; P1['sha_rgba'] = seq[1]['sha16']
            P1['frames_identical'] = (seq[0]['sha16'] == seq[1]['sha16'])
            P1['pixel_diff_argb_vs_rgba'] = diff_info(rgb(os.path.join(SHOTS, seq[0]['file'])), rgb(os.path.join(SHOTS, seq[1]['file'])))
            P1['audit_colorOrder_on_attach'] = await c.ev("(function(){try{return JSON.stringify(window.WikiSfxAdapter.__audit&&{colorOrder:window.WikiSfxAdapter.__audit.colorOrder,colorFormatFromSource:window.WikiSfxAdapter.__audit.colorFormatFromSource});}catch(e){return 'ERR '+e.message;}})()")
            seq2 = []
            for v in ('argb', 'rgba'):
                await c.ev("(function(){return JSON.stringify(window.WikiSfxAdapter.colorOrder('%s'));})()" % v)
                await asyncio.sleep(2.0)
                raws, shas, _, _ = await gate(c, 5)
                open(os.path.join(SHOTS, 'c177_co_%s_t0030.png' % v), 'wb').write(raws)
                # 逐 sprite 的 opacity（颜色列序会改 alpha）—— 若变了但帧不变 ⇒ 该 sprite 不可见
                pp = await c.ev("(function(){try{return JSON.stringify((window.WikiSfxAdapter.__probe()||{}).sprites);}catch(e){return 'ERR '+e.message;}})()")
                seq2.append({'co': v, 'sha16': shas, 'probe_sprites': pp})
                print('P1b co=%s sha=%s' % (v, shas))
                dump()
            P1['seq2'] = seq2
            P1['audit_probe_after_switch'] = await c.ev("(function(){try{return JSON.stringify({a:window.WikiSfxAdapter.__audit&&window.WikiSfxAdapter.__audit.colorOrder});}catch(e){return 'ERR '+e.message;}})()")
            RES['P1_colorOrder_effect'] = P1
            dump()

            # --- P2: 1110171 sprite 是否画进帧 ---
            await c.ev("(function(){return JSON.stringify(window.WikiSfxAdapter.colorOrder('argb'));})()")
            await c.ev("(async function(id){var s=(window.WEAPON_SKIN_MEDIA||{}).skins||{};await window.WikiWeaponViewer.open(s[id],{title:'x'});return 'ok';})('1110171')")
            await asyncio.sleep(12)
            await c.ev("String(window.WikiWeaponViewer.__post(false))")
            await c.ev("String(window.WikiWeaponViewer.__hidePanels(true))")
            await asyncio.sleep(1.0)
            await c.ev("(function(){var b=document.querySelector('.wv-sfx');if(b&&!b.disabled&&b.getAttribute('aria-pressed')!=='true')b.click();return 'on';})()")
            await asyncio.sleep(2.5)
            await c.ev("String(window.WikiWeaponViewer.__sfxTime(0.55))")
            await asyncio.sleep(1.0)
            P2 = {}
            raw, sha, okg, series = await gate(c, 5)
            open(os.path.join(SHOTS, 'c171_probe_sfxon_t0055.png'), 'wb').write(raw)
            P2['sfx_on_frame'] = {'sha16': sha, 'gate_ok': okg, 'series': series}
            P2['probe'] = await c.ev("(function(){try{return JSON.stringify(window.WikiSfxAdapter.__probe());}catch(e){return 'ERR '+e.message;}})()")
            P2['sfxDiag'] = await c.ev("(function(){try{return JSON.stringify(window.WikiSfxAdapter.__sfxDiag());}catch(e){return 'ERR '+e.message;}})()")
            P2['errs'] = await c.ev("(function(){return JSON.stringify(window.__errs);})()")
            print('P2 probe:', str(P2['probe'])[:1500]); dump()
            RES['P2_1110171_sprites'] = P2
            dump()

            RES['exceptions'] = c.exc
            RES['eval_exceptions'] = c.eval_exc[-8:]
            RES['stage'] = 'done'; dump()
    finally:
        try:
            ps = subprocess.run(['powershell', '-NoProfile', '-Command',
                                 "(Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'chrome' -and $_.CommandLine -match 'FXVA95_prof' } | Select-Object -ExpandProperty ProcessId) -join ','"],
                                capture_output=True, text=True, timeout=90)
            for x in (ps.stdout or '').strip().split(','):
                if x.strip().isdigit() and int(x) != pr.pid:
                    subprocess.run(['taskkill', '/PID', x.strip(), '/T', '/F'], capture_output=True, timeout=30)
                    killed.append(int(x))
        except Exception as e:
            killed.append('ERR ' + str(e)[:60])
        try:
            pr.terminate(); pr.wait(timeout=5)
        except Exception:
            pass
        try:
            subprocess.run(['taskkill', '/PID', str(pr.pid), '/T', '/F'], capture_output=True, timeout=30)
        except Exception:
            pass
        await asyncio.sleep(1.5)
        RES['killed_pids'] = killed
    RES['stage'] = 'finished'; dump()
    print('killed:', killed)


asyncio.run(main())
