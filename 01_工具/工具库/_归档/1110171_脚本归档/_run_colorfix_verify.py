# -*- coding: utf-8 -*-
"""task-90v 终验（只读）：COLOR_ORDER=argb / COLOR_TRACK_PAR / blendOf 三处补丁的浏览器实测
A 页内自证（adapter 108,517 B / A2DE92CB9E5CF4C6；board 7BE7638389715FD3）
B 1110177 默认态四冻结时刻（N>=5 稳定门）+ 五读数
C 负控 colorTrackPar(false) 逐字节回补丁前 task-93 四帧 + 往返 colorTrackPar(true)
D 1110171 三态（默认 argb+par / rgba+par / rgba+nopar）
E 7 皮肤回归 applied==expected / failed / missing / SFX 默认关 / __errs / 404 只 favicon
F 开关往返 colorTrackPar(true/false/true)、colorOrder(argb/rgba/argb)
单浏览器 profile FXVA94_prof / 端口 10159；结束按 user-data-dir 反查 PID 杀自己的进程树。
只读 08Lifeafter wiki/**；写：COLORFIX_verify_20260920.{md,json} + sfx_verify_shots12/**。
"""
import asyncio, base64, hashlib, io, json, os, re, shutil, subprocess, sys, time, urllib.request

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
PREV10 = os.path.join(OUT, 'sfx_verify_shots10')
PREV11 = os.path.join(OUT, 'sfx_verify_shots11')
TMP = os.environ['TEMP']
PORT = 10159
PROFILE = os.path.join(TMP, 'FXVA94_prof')
BOARD = 'http://127.0.0.1:8765/board.html?b=weapon_skin_sfx_text_sources&view=wiki'
J = os.path.join(OUT, 'COLORFIX_verify_20260920.json')
TS = [0.10, 0.30, 0.55, 1.15]
# 补丁前（task-93 记录的默认态 = rgba + 只读 color_track）
PRE93 = {'0.1': '2f1d02498aef6c5b', '0.3': 'a3e63c2fbb3dfa8c', '0.55': '6c2c384ed52d62bd', '1.15': '61c1e08b18b9f921'}
PRE93_FILE = {'0.1': 'r177_t0010.png', '0.3': 'r177_t0030.png', '0.55': 'r177_t0055.png', '1.15': 'r177_t0115.png'}
PRE93_COLORFIX_FILE = {'0.1': 'c177_t0010_default.png', '0.3': 'c177_t0030_default.png',
                       '0.55': 'c177_t0055_default.png', '1.15': 'c177_t0115_default.png'}
# 补丁前 1110171 默认态（task-93：SFX 关的锚）
PRE171_OFF = '48b6c95c1165c80a'
PRE171_OFF_PNG = 's171_off.png'
NODES5 = ['H_p_闪电', 'H_ shandian01_1_1', 'M_lizi_闪电_01', 'H_p_烟雾_02', 'H_鬼火_星点_1']
REG7 = ['1110024', '1110129', '1110145', '1110152', '1110165', '1110171', '1110177']
EXPECT = {'1110024': 5, '1110129': 5, '1110145': 7, '1110152': 2, '1110165': 4, '1110171': 7, '1110177': 3}
ATLAS5 = ['lightning07_cs__atlas207659.png', 'lightning_01__atlas207671.png', 'shandian_05_yh_djs__atlas207712.png',
          'smoke25__atlas208478.png', 'tex_special_fangkuai_tp52__atlas211384.png']
GLB3 = ['mod_skin_1003_010_zs_ql07_djs.glb', 'mod_skin_1003_012_zs_qiu03_djs.glb', 'mod_skin_1003_012_zs_qiu04_djs.glb']
EXPECT_ADAPTER = 'A2DE92CB9E5CF4C6'
EXPECT_BOARD = '7BE7638389715FD3'
EXPECT_V = 'A2DE92CB9E5CF4C6'


def h16(p):
    try:
        return hashlib.sha256(io.open(p, 'rb').read()).hexdigest()[:16].upper()
    except Exception:
        return 'MISSING'


def h16b(b):
    return hashlib.sha256(b).hexdigest()[:16].upper()


def pins():
    d = {'viewer_js': h16(os.path.join(W, r'assets\weapon_skin_viewer.js')),
         'adapter': h16(os.path.join(W, r'assets\weapon_skin_sfx_adapter.js')),
         'board': h16(os.path.join(W, 'board.html')),
         'v1110177': h16(os.path.join(W, r'assets\3d\weapon_skin\1110177\viewer.json')),
         'e1110177': h16(os.path.join(W, r'assets\3d\weapon_skin\1110177\effects.json')),
         'v1110171': h16(os.path.join(W, r'assets\3d\weapon_skin\1110171\viewer.json')),
         'e1110171': h16(os.path.join(W, r'assets\3d\weapon_skin\1110171\effects.json')),
         'm1110177': h16(os.path.join(W, r'assets\3d\weapon_skin\1110177\neox_material.json')),
         'atlas171': h16(os.path.join(W, r'assets\3d\weapon_skin\1110171\sfx\tex\tex_glow_tp07_02__atlas207414.png'))}
    for a in ATLAS5:
        d['atlas177_' + a[:12]] = h16(os.path.join(W, r'assets\3d\weapon_skin\1110177\sfx\tex', a))
    for g in GLB3:
        d['glb_' + g[:20]] = h16(os.path.join(W, r'assets\3d\weapon_skin\1110171\sfx', g))
    return d


RES = {'pins_start': pins(), 'stage': 'init', 'freeze_ts': TS, 'prev93_sha': PRE93, 'nodes5': NODES5,
       'expect_adapter': EXPECT_ADAPTER, 'expect_board': EXPECT_BOARD, 'expect_viewer': EXPECT_V,
       'backend': {}, 'verdicts': {}}
try:
    bt = io.open(os.path.join(W, 'board.html'), encoding='utf-8', errors='replace').read()
    RES['board_v_query'] = sorted(set(re.findall(r'\?v=([0-9a-f]{6,})', bt)))
except Exception as e:
    RES['board_v_query'] = 'ERR ' + str(e)[:60]
json.dump(RES, open(J, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
dump = lambda: json.dump(RES, open(J, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


class CDP:
    def __init__(self, ws):
        self.ws, self._i, self._f = ws, 0, {}
        self.console, self.http, self.exc, self.eval_exc = [], [], [], []
        self.net = {'glb': {}, 'tex': {}, 'js': {}}

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
                elif m.get('method') == 'Log.entryAdded':
                    e = m['params']['entry']
                    if e.get('level') == 'error':
                        self.console.append({'url': e.get('url'), 'text': (e.get('text') or '')[:160]})
                elif m.get('method') == 'Runtime.consoleAPICalled':
                    p = m['params']
                    if p.get('type') in ('error', 'assert'):
                        self.console.append({'url': '', 'text': 'consoleAPICalled: ' + str(p.get('args'))[:150]})
                elif m.get('method') == 'Network.responseReceived':
                    r = m['params']['response']
                    u, s = r.get('url', ''), r.get('status')
                    if u.endswith('.glb'):
                        self.net['glb'][u] = s
                    if '/sfx/tex/' in u or '/src_tex/' in u:
                        self.net['tex'][u] = s
                    if 'weapon_skin_sfx_adapter.js' in u or 'weapon_skin_viewer.js' in u:
                        self.net['js'][u] = s
                    if s and s >= 400:
                        self.http.append({'status': s, 'url': u})
                elif m.get('method') == 'Runtime.exceptionThrown':
                    x = m['params'].get('exceptionDetails', {})
                    self.exc.append({'text': (x.get('text') or '')[:140], 'scriptId': x.get('scriptId'),
                                     'line': x.get('lineNumber'), 'col': x.get('columnNumber')})
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
        shas.append(h16b(raw))
        if len(shas) >= n and len(set(shas[-n:])) == 1:
            return raw, shas[-1], True, shas
        await asyncio.sleep(0.9)
    return raw, shas[-1], False, shas


def rgb(x):
    img = Image.open(io.BytesIO(x)) if isinstance(x, bytes) else Image.open(x)
    return np.asarray(img.convert('RGB')).astype(np.float32) / 255.0


def mask_stats(fr, bg, thr=24.0 / 255.0):
    h = min(fr.shape[0], bg.shape[0]); w = min(fr.shape[1], bg.shape[1])
    fr2, bg2 = fr[:h, :w], bg[:h, :w]
    m = np.abs(fr2 - bg2).max(axis=2) > thr
    n = int(m.sum())
    out = {'mask_pct': round(100.0 * n / m.size, 3), 'n_px': n}
    if n:
        ys, xs = np.nonzero(m)
        out['bbox'] = [int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max())]
        out['bbox_wh'] = [int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1)]
        out['bbox_diag_px'] = round(float(np.hypot(xs.max() - xs.min() + 1, ys.max() - ys.min() + 1)), 1)
        out['centroid_px'] = [round(float(xs.mean()), 1), round(float(ys.mean()), 1)]
    px = fr2[m]
    if len(px):
        L = 0.2126 * px[:, 0] + 0.7152 * px[:, 1] + 0.0722 * px[:, 2]
        white = (px[:, 0] > 0.9) & (px[:, 1] > 0.9) & (px[:, 2] > 0.9)
        out.update({'p50': round(float(np.median(L)), 4), 'p95': round(float(np.percentile(L, 95)), 4),
                    'gt0.5_pct': round(100.0 * float((L > 0.5).mean()), 3),
                    'gt0.75_pct': round(100.0 * float((L > 0.75).mean()), 3),
                    'warm_pct': round(100.0 * float(((px[:, 0] > 0.9) & (px[:, 1] > 0.85)).mean()), 3),
                    'white_pct_in_mask': round(100.0 * float(white.mean()), 3)})
    return out


def diff_info(a, b, thr=6.0 / 255.0):
    h = min(a.shape[0], b.shape[0]); w = min(a.shape[1], b.shape[1])
    d = np.abs(a[:h, :w] - b[:h, :w])
    dd = d.max(axis=2) > thr
    n = int(dd.sum())
    o = {'changed_px': n, 'changed_pct_canvas': round(100.0 * n / dd.size, 4), 'max_diff': round(float(d.max()), 5)}
    if n:
        ys, xs = np.nonzero(dd)
        o['bbox'] = [int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max())]
        o['bbox_wh'] = [int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1)]
    return o


def byte_equal(a, b):
    """PNG 级逐字节：解码后逐像素完全相同（含通道）"""
    ia = np.asarray(Image.open(io.BytesIO(a) if isinstance(a, bytes) else a).convert('RGBA')).astype(np.int16)
    ib = np.asarray(Image.open(io.BytesIO(b) if isinstance(b, bytes) else b).convert('RGBA')).astype(np.int16)
    h = min(ia.shape[0], ib.shape[0]); w = min(ia.shape[1], ib.shape[1])
    d = np.abs(ia[:h, :w] - ib[:h, :w]).max(axis=2)
    n = int((d > 0).sum())
    return {'diff_px_strict': n, 'max_abs': int(d.max()) if d.size else 0, 'shape_a': list(ia.shape[:2]),
            'shape_b': list(ib.shape[:2]), 'identical': bool(n == 0 and ia.shape == ib.shape)}


DIAG_JS = "(function(){try{return JSON.stringify(window.WikiSfxAdapter.__sfxDiag());}catch(e){return 'ERR '+e.message;}})()"
STATUS_JS = ("(function(){try{var t=JSON.parse(window.__texReady());var ms=(t.meshes||[]).map(function(m){return m.envMode;});"
             "var nx=JSON.parse(JSON.stringify((window.WikiWeaponViewer.__neox&&window.WikiWeaponViewer.__neox())||{}));var rep=nx.report||{};"
             "return JSON.stringify({applied:rep.applied||null,prims:(rep.prims||[]).length,failed:(rep.failed||[]).length,"
             "missing:(rep.missing||[]).length,env_warn:rep.env_warn?rep.env_warn.length:null,"
             "pending:ms.filter(function(x){return x==='ibl_pending';}).length});}catch(e){return 'ERR '+e.message;}})()")
SW_JS = "(function(){try{return JSON.stringify(window.WikiSfxAdapter.adaptSwitches());}catch(e){return 'ERR '+e.message;}})()"
ERRS_JS = "(function(){try{var e=window.__errs;return JSON.stringify({n:(e||[]).length,items:(e||[]).slice(0,6)});}catch(x){return 'ERR '+x.message;}})()"


def node_alive(dj):
    out = {}
    for x in (dj.get('particles') or []):
        if isinstance(x, dict) and x.get('name') in NODES5:
            out[x['name']] = {'alive_now': x.get('alive_now'), 'in_pool': x.get('in_pool'), 'quad': x.get('quad'),
                              'sliced_frames': x.get('sliced_frames'), 'fallback': x.get('fallback')}
    return out


async def wait_settle(c, tries=25):
    for _ in range(tries):
        await asyncio.sleep(1.2)
        st = await c.ev(STATUS_JS)
        j = json.loads(st) if isinstance(st, str) and st.startswith('{') else {}
        if j.get('applied') and j.get('pending', 1) == 0 and j.get('env_warn') in (0, None):
            return j
    return None


async def wait_adapter(c, tries=80):
    t0 = time.time()
    for _ in range(tries):
        s = await c.ev("(function(){return JSON.stringify({d:typeof (window.WikiSfxAdapter&&window.WikiSfxAdapter.__sfxDiag),"
                       "p:typeof (window.WikiSfxAdapter&&window.WikiSfxAdapter.colorTrackPar),"
                       "o:typeof (window.WikiSfxAdapter&&window.WikiSfxAdapter.colorOrder)});})()")
        try:
            j = json.loads(s) if isinstance(s, str) else {}
        except Exception:
            j = {}
        if j.get('d') == 'function' and j.get('p') == 'function' and j.get('o') == 'function':
            return {'ok': True, 'ms': round((time.time() - t0) * 1000)}
        await asyncio.sleep(0.5)
    return {'ok': False, 'ms': round((time.time() - t0) * 1000)}


async def open_skin(c, sid):
    await c.send('Page.navigate', url=BOARD)
    await asyncio.sleep(9)
    r = await c.ev("(async function(id){var s=(window.WEAPON_SKIN_MEDIA||{}).skins||{};var rec=s[id];if(!rec) return 'NO_RECORD';"
                   "await window.WikiWeaponViewer.open(rec,{title:'x'});return 'opened';})('%s')" % sid)
    st = await wait_settle(c)
    return st, r


async def grab(c, t, fn, bg):
    await c.ev("String(window.WikiWeaponViewer.__sfxTime(%s))" % t)
    await asyncio.sleep(0.7)
    raw, sha, okg, series = await gate(c, 5)
    open(os.path.join(SHOTS, fn), 'wb').write(raw)
    st = mask_stats(rgb(os.path.join(SHOTS, fn)), bg)
    dg = await c.ev(DIAG_JS)
    try:
        dj = json.loads(dg)
    except Exception:
        dj = {}
    return {'file': fn, 'sha16': sha, 'gate_ok': okg, 'series': series, 'MASK': st,
            'alive_total': dj.get('alive_now'), 'nodes': node_alive(dj),
            'diag_color_order': dj.get('color_order')}


def crop_pair(fa, fb, out, pad=70, scale=2, tag=''):
    a = rgb(os.path.join(SHOTS, fa)); b = rgb(os.path.join(SHOTS, fb))
    h = min(a.shape[0], b.shape[0]); w = min(a.shape[1], b.shape[1])
    d = np.abs(a[:h, :w] - b[:h, :w]).max(axis=2) > (6.0 / 255.0)
    ys, xs = np.nonzero(d)
    if len(xs) == 0:
        return {'note': 'no diff', 'tag': tag}
    x0, x1 = max(0, int(xs.min()) - pad), min(w, int(xs.max()) + pad)
    y0, y1 = max(0, int(ys.min()) - pad), min(h, int(ys.max()) + pad)
    ta = Image.fromarray((a[y0:y1, x0:x1] * 255).astype(np.uint8)).resize(((x1 - x0) * scale, (y1 - y0) * scale), Image.NEAREST)
    tb = Image.fromarray((b[y0:y1, x0:x1] * 255).astype(np.uint8)).resize(((x1 - x0) * scale, (y1 - y0) * scale), Image.NEAREST)
    cv = Image.new('RGB', (ta.width * 2 + 12, ta.height), (255, 0, 0))
    cv.paste(ta, (0, 0)); cv.paste(tb, (ta.width + 12, 0))
    cv.save(os.path.join(SHOTS, out))
    return {'file': out, 'size': list(cv.size), 'bbox': [x0, x1, y0, y1],
            'diff_px': int(d.sum()), 'tag': tag,
            'note': 'left=%s right=%s' % (fa, fb)}


def crop_hot(f, out, bbox, scale=2):
    a = rgb(os.path.join(SHOTS, f))
    x0, x1, y0, y1 = bbox
    x0 = max(0, x0); y0 = max(0, y0)
    x1 = min(a.shape[1], x1); y1 = min(a.shape[0], y1)
    t = Image.fromarray((a[y0:y1, x0:x1] * 255).astype(np.uint8)).resize(((x1 - x0) * scale, (y1 - y0) * scale), Image.NEAREST)
    t.save(os.path.join(SHOTS, out))
    return {'file': out, 'size': list(t.size), 'src_bbox': [x0, x1, y0, y1]}


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
            await c.send('Page.enable'); await c.send('Runtime.enable'); await c.send('Log.enable'); await c.send('Network.enable')
            # 错误收集器（页内 __errs）：在文档开始前注入
            hook = ("window.__errs=[];window.addEventListener('error',function(e){try{window.__errs.push("
                    "String((e&&e.message)||e)+' @'+(e&&e.filename)+':'+(e&&e.lineno));}catch(x){}});"
                    "window.addEventListener('unhandledrejection',function(e){try{window.__errs.push('rejection: '+String(e&&e.reason));}catch(x){}});")
            await c.send('Page.addScriptToEvaluateOnNewDocument', source=hook)
            print('pins:', json.dumps(RES['pins_start'], ensure_ascii=False))
            print('board ?v=:', json.dumps(RES['board_v_query'], ensure_ascii=False)); dump()
            await c.send('Page.navigate', url=BOARD); await asyncio.sleep(20)
            for _ in range(3):
                await shot(c); await asyncio.sleep(1.0)

            # ---------- A 页内自证 ----------
            RES['bytes_inpage'] = {}
            for k, u in (('adapter', '/assets/weapon_skin_sfx_adapter.js'), ('viewer_js', '/assets/weapon_skin_viewer.js'),
                         ('v1110177', '/assets/3d/weapon_skin/1110177/viewer.json'), ('e1110177', '/assets/3d/weapon_skin/1110177/effects.json'),
                         ('v1110171', '/assets/3d/weapon_skin/1110171/viewer.json'), ('e1110171', '/assets/3d/weapon_skin/1110171/effects.json'),
                         ('m1110177', '/assets/3d/weapon_skin/1110177/neox_material.json'),
                         ('board', '/board.html')):
                js = ("(async function(u){var r=await fetch(u,{cache:'no-store'});var b=await r.arrayBuffer();"
                      "var h=await crypto.subtle.digest('SHA-256',b);return JSON.stringify({status:r.status,bytes:b.byteLength,"
                      "sha:[].slice.call(new Uint8Array(h)).map(function(x){return x.toString(16).padStart(2,'0');}).join('').slice(0,16).toUpperCase()});})('%s')" % u)
                try:
                    RES['bytes_inpage'][k] = json.loads(await c.ev(js))
                except Exception as e:
                    RES['bytes_inpage'][k] = 'ERR ' + str(e)[:80]
            RES['A_selfproof'] = {
                'adapter_bytes_ok': RES['bytes_inpage'].get('adapter', {}).get('bytes') == 108517,
                'adapter_sha_ok': RES['bytes_inpage'].get('adapter', {}).get('sha') == EXPECT_ADAPTER,
                'board_sha_ok': RES['bytes_inpage'].get('board', {}).get('sha') == EXPECT_BOARD,
                'viewer_sha_ok': RES['bytes_inpage'].get('viewer_js', {}).get('sha') == EXPECT_V,
                'v1110177_ok': RES['bytes_inpage'].get('v1110177', {}).get('sha') == 'BF7288193E092AA2',
                'e1110177_ok': RES['bytes_inpage'].get('e1110177', {}).get('sha') == '140E27ABB3E40694',
                'v1110171_ok': RES['bytes_inpage'].get('v1110171', {}).get('sha') == '4D6CAE69DCE8CFC9',
                'e1110171_ok': RES['bytes_inpage'].get('e1110171', {}).get('sha') == '2B0127E574A32CBD',
                'm1110177_ok': RES['bytes_inpage'].get('m1110177', {}).get('sha') == 'A05C4F2C8DDFCF9A'}
            print('A in-page:', json.dumps(RES['bytes_inpage'], ensure_ascii=False)); dump()

            # ---------- F-1 开关读数（默认态） ----------
            RES['F_switches'] = {}
            RES['F_switches']['default_adapt'] = await c.ev(SW_JS)
            RES['F_switches']['default_colorOrder'] = await c.ev("(function(){try{return JSON.stringify(window.WikiSfxAdapter.colorOrder());}catch(e){return 'ERR '+e.message;}})()")
            RES['F_switches']['default_colorTrackPar'] = await c.ev("(function(){try{return JSON.stringify(window.WikiSfxAdapter.colorTrackPar());}catch(e){return 'ERR '+e.message;}})()")
            print('F default:', json.dumps(RES['F_switches'], ensure_ascii=False)); dump()

            # ---------- B 1110177 默认态 ----------
            A = {}
            A['settle'], A['open_ret'] = await open_skin(c, '1110177')
            await c.ev("String(window.WikiWeaponViewer.__post(false))")
            await c.ev("String(window.WikiWeaponViewer.__hidePanels(true))")
            await asyncio.sleep(1.0)
            rawo, shao, oko, _ = await gate(c, 5)
            open(os.path.join(SHOTS, 'c177_off.png'), 'wb').write(rawo)
            await c.ev("window.__primShow(-1)"); await asyncio.sleep(1.2)
            rawb, shab, okb, _ = await gate(c, 4)
            open(os.path.join(SHOTS, 'c177_bg.png'), 'wb').write(rawb)
            await c.ev("window.__primShow(null)"); await asyncio.sleep(0.8)
            bg = rgb(os.path.join(SHOTS, 'c177_bg.png'))
            A['sfx_off_anchor'] = {'sha16': shao, 'gate_ok': oko, 'mask': mask_stats(rgb(os.path.join(SHOTS, 'c177_off.png')), bg)}
            A['click_sfx'] = await c.ev("(function(){var b=document.querySelector('.wv-sfx');if(!b||b.disabled)return 'NO_BTN';b.click();return 'clicked';})()")
            A['adapter_ready'] = await wait_adapter(c)
            await asyncio.sleep(2.0)
            A['colorTrackPar_default'] = await c.ev("(function(){try{return JSON.stringify(window.WikiSfxAdapter.colorTrackPar());}catch(e){return 'ERR '+e.message;}})()")
            A['colorOrder_default'] = await c.ev("(function(){try{return JSON.stringify(window.WikiSfxAdapter.colorOrder());}catch(e){return 'ERR '+e.message;}})()")
            A['adaptSwitches_default'] = await c.ev(SW_JS)
            print('A 177 default:', A['colorTrackPar_default'], A['colorOrder_default'], A['adaptSwitches_default'])

            # 逐冻结时刻：默认(argb+par) → colorTrackPar(false) → colorTrackPar(true)
            A['per_t'] = {}
            for t in TS:
                key = str(t)
                e = {}
                e['DEFAULT'] = await grab(c, t, 'c177_t%04d_default.png' % int(round(t * 100)), bg)
                await c.ev("(function(){return JSON.stringify(window.WikiSfxAdapter.colorTrackPar(false));})()")
                await asyncio.sleep(2.0)
                e['PAR_OFF'] = await grab(c, t, 'c177_t%04d_paroff.png' % int(round(t * 100)), bg)
                await c.ev("(function(){return JSON.stringify(window.WikiSfxAdapter.colorTrackPar(true));})()")
                await asyncio.sleep(2.0)
                e['BACK'] = await grab(c, t, 'c177_t%04d_back.png' % int(round(t * 100)), bg)
                iD = rgb(os.path.join(SHOTS, e['DEFAULT']['file']))
                iP = rgb(os.path.join(SHOTS, e['PAR_OFF']['file']))
                iB = rgb(os.path.join(SHOTS, e['BACK']['file']))
                e['diff_DEFAULT_vs_PAROFF'] = diff_info(iD, iP)
                e['diff_DEFAULT_vs_BACK'] = diff_info(iD, iB)
                e['neg_control_sha93'] = {'paroff_sha': e['PAR_OFF']['sha16'], 'task93_sha': PRE93.get(key),
                                          'sha_equal': e['PAR_OFF']['sha16'] == PRE93.get(key)}
                pf = PRE93_FILE.get(key)
                if pf and os.path.exists(os.path.join(PREV10, pf)):
                    e['neg_control_vs_task93_png'] = diff_info(iP, rgb(os.path.join(PREV10, pf)))
                    e['neg_control_vs_task93_png_strict'] = byte_equal(os.path.join(SHOTS, e['PAR_OFF']['file']),
                                                                       os.path.join(PREV10, pf))
                e['roundtrip_sha_equal'] = e['DEFAULT']['sha16'] == e['BACK']['sha16']
                A['per_t'][key] = e
                print('B t=%-5s DEFAULT=%s PAROFF=%s BACK=%s | D-vs-PAROFF=%s | PAROFF==task93:%s | roundtrip:%s' % (
                    t, e['DEFAULT']['sha16'], e['PAR_OFF']['sha16'], e['BACK']['sha16'],
                    json.dumps(e['diff_DEFAULT_vs_PAROFF'], ensure_ascii=False)[:100],
                    e['neg_control_sha93']['sha_equal'], e['roundtrip_sha_equal']))
                dump()
            # 关闭 SFX 回到锚
            await c.ev("(function(){var b=document.querySelector('.wv-sfx');if(b&&b.getAttribute('aria-pressed')==='true')b.click();return 'off';})()")
            await asyncio.sleep(2.5)
            rawo2, shao2, oko2, _ = await gate(c, 5)
            A['sfx_off_after'] = {'sha16': shao2, 'gate_ok': oko2, 'equals_before': shao2 == shao}
            RES['B_1110177'] = A
            RES['B_1110177']['__errs'] = await c.ev(ERRS_JS)
            dump()

            # 亲眼图：1110177 变化区并排（t=0.30 与 0.55）
            RES['B_eyes'] = {}
            for t in ('0.3', '0.55', '0.1'):
                try:
                    RES['B_eyes']['t' + t] = crop_pair('c177_t%04d_default.png' % int(round(float(t) * 100)),
                                                       'c177_t%04d_paroff.png' % int(round(float(t) * 100)),
                                                       'c177_side_default_left_paroff_right_t%04d.png' % int(round(float(t) * 100)),
                                                       tag='default(left) vs colorTrackPar(false)(right)')
                except Exception as ex:
                    RES['B_eyes']['t' + t] = 'ERR ' + str(ex)[:80]
            dump()

            # ---------- D 1110171 三态 ----------
            D = {}
            D['settle'], D['open_ret'] = await open_skin(c, '1110171')
            await c.ev("String(window.WikiWeaponViewer.__post(false))")
            await c.ev("String(window.WikiWeaponViewer.__hidePanels(true))")
            await asyncio.sleep(1.0)
            rawo, shao, oko, _ = await gate(c, 5)
            open(os.path.join(SHOTS, 'c171_off.png'), 'wb').write(rawo)
            await c.ev("window.__primShow(-1)"); await asyncio.sleep(1.2)
            rawb, shab, okb, _ = await gate(c, 4)
            open(os.path.join(SHOTS, 'c171_bg.png'), 'wb').write(rawb)
            await c.ev("window.__primShow(null)"); await asyncio.sleep(0.8)
            bg1 = rgb(os.path.join(SHOTS, 'c171_bg.png'))
            D['sfx_off_anchor'] = {'sha16': shao, 'gate_ok': oko, 'prev93': PRE171_OFF, 'equals_prev': shao == PRE171_OFF}
            if os.path.exists(os.path.join(PREV10, PRE171_OFF_PNG)):
                D['sfx_off_diff_vs_task93'] = byte_equal(os.path.join(SHOTS, 'c171_off.png'), os.path.join(PREV10, PRE171_OFF_PNG))
            D['click_sfx'] = await c.ev("(function(){var b=document.querySelector('.wv-sfx');if(!b||b.disabled)return 'NO_BTN';b.click();return 'clicked';})()")
            D['adapter_ready'] = await wait_adapter(c)
            await asyncio.sleep(2.5)
            D['sprites_diag'] = await c.ev(DIAG_JS)
            T171 = 0.55
            D['freeze_t'] = T171
            await c.ev("String(window.WikiWeaponViewer.__sfxTime(%s))" % T171)
            await asyncio.sleep(1.0)
            states = {}
            for name, co, cp in (('S1_default_argb_par', None, None), ('S2_rgba_par', 'rgba', None), ('S3_rgba_nopar', 'rgba', False)):
                if co:
                    await c.ev("(function(){return JSON.stringify(window.WikiSfxAdapter.colorOrder('%s'));})()" % co)
                if cp is not None:
                    await c.ev("(function(){return JSON.stringify(window.WikiSfxAdapter.colorTrackPar(false));})()")
                await asyncio.sleep(2.0)
                raw, sha, okg, series = await gate(c, 5)
                fn = 'c171_%s_t0055.png' % name
                open(os.path.join(SHOTS, fn), 'wb').write(raw)
                dj = {}
                try:
                    dj = json.loads(await c.ev(DIAG_JS))
                except Exception:
                    pass
                spr = [{'name': s.get('name'), 'kind': s.get('kind'), 'texture': s.get('texture'), 'visible': s.get('visible'),
                        'opacity': s.get('opacity'), 'quad': s.get('quad_size_world'), 'blend': s.get('blend_mode_used'),
                        'blend_unresolved': s.get('blend_mode_used')}
                       for s in (dj.get('sprites') or [])]
                states[name] = {'file': fn, 'sha16': sha, 'gate_ok': okg, 'series': series,
                                'MASK': mask_stats(rgb(os.path.join(SHOTS, fn)), bg1),
                                'color_order_read': dj.get('color_order'), 'sprites': spr,
                                'adaptSwitches': dj.get('sprite_fix')}
                print('D %s sha=%s mask%%=%s' % (name, sha, states[name]['MASK'].get('mask_pct')))
                dump()
            # 复位
            await c.ev("(function(){return JSON.stringify(window.WikiSfxAdapter.colorOrder('argb'));})()")
            await c.ev("(function(){return JSON.stringify(window.WikiSfxAdapter.colorTrackPar(true));})()")
            await asyncio.sleep(1.5)
            raw, sha, okg, _ = await gate(c, 5)
            open(os.path.join(SHOTS, 'c171_S1b_back_default_t0055.png'), 'wb').write(raw)
            states['S1b_back'] = {'file': 'c171_S1b_back_default_t0055.png', 'sha16': sha, 'gate_ok': okg,
                                  'equals_S1': sha == states['S1_default_argb_par']['sha16'],
                                  'MASK': mask_stats(rgb(os.path.join(SHOTS, 'c171_S1b_back_default_t0055.png')), bg1)}
            D['states'] = states
            # 三态两两 diff
            i1 = rgb(os.path.join(SHOTS, states['S1_default_argb_par']['file']))
            i2 = rgb(os.path.join(SHOTS, states['S2_rgba_par']['file']))
            i3 = rgb(os.path.join(SHOTS, states['S3_rgba_nopar']['file']))
            D['diffs'] = {'S1_vs_S2': diff_info(i1, i2), 'S1_vs_S3': diff_info(i1, i3), 'S2_vs_S3': diff_info(i2, i3)}
            D['__errs'] = await c.ev(ERRS_JS)
            RES['D_1110171'] = D
            dump()
            # 亲眼图：三态裁剪并排（只裁效果区，避免整幅缩小看不清）
            hot = D['states']['S1_default_argb_par']['MASK'].get('bbox')
            if hot:
                x0, x1, y0, y1 = hot
                pad = 40
                bb = [max(0, x0 - pad), min(1600, x1 + pad), max(0, y0 - pad), min(1000, y1 + pad)]
                RES['D_eyes'] = {'src_bbox': bb, 'crops': []}
                for nm in ('S1_default_argb_par', 'S2_rgba_par', 'S3_rgba_nopar'):
                    RES['D_eyes']['crops'].append(crop_hot(D['states'][nm]['file'], 'c171_crop_%s.png' % nm, bb, scale=3))
                # 三态横向拼一张
                ims = [Image.open(os.path.join(SHOTS, 'c171_crop_%s.png' % nm)) for nm in ('S1_default_argb_par', 'S2_rgba_par', 'S3_rgba_nopar')]
                Wt = sum(i.width for i in ims) + 24
                Ht = max(i.height for i in ims)
                cv = Image.new('RGB', (Wt, Ht), (255, 0, 0))
                x = 0
                for i in ims:
                    cv.paste(i, (x, 0)); x += i.width + 12
                cv.save(os.path.join(SHOTS, 'c171_three_state_S1_S2_S3.png'))
                RES['D_eyes']['strip'] = 'c171_three_state_S1_S2_S3.png'
            dump()

            # ---------- E 7 皮肤回归 ----------
            reg = {}
            for sid in REG7:
                st, ret = await open_skin(c, sid)
                btn = await c.ev("(function(){var b=document.querySelector('.wv-sfx');return b?JSON.stringify({text:b.textContent,disabled:!!b.disabled,pressed:b.getAttribute('aria-pressed')}):'NO_BTN';})()")
                errs = await c.ev(ERRS_JS)
                reg[sid] = {'status': st, 'open_ret': ret, 'btn': btn, 'expected_applied': EXPECT.get(sid, None),
                            'applied_eq_expected': bool(st and st.get('applied') == EXPECT.get(sid)),
                            'failed_empty': bool(st and st.get('failed') == 0), 'missing_empty': bool(st and st.get('missing') == 0),
                            '__errs': errs}
                print('E reg', sid, json.dumps(st, ensure_ascii=False), '|', btn, '| errs', errs)
                dump()
            RES['E_regression'] = reg

            # ---------- F 开关往返 ----------
            F = RES['F_switches']
            await open_skin(c, '1110177')
            await c.ev("(function(){var b=document.querySelector('.wv-sfx');if(b&&!b.disabled&&b.getAttribute('aria-pressed')!=='true')b.click();return 'on';})()")
            await asyncio.sleep(2.5)
            seq = []
            for v in (True, False, True):
                r = await c.ev("(function(){try{return JSON.stringify(window.WikiSfxAdapter.colorTrackPar(%s));}catch(e){return 'ERR '+e.message;}})()" % ('true' if v else 'false'))
                s = await c.ev(SW_JS)
                seq.append({'call': 'colorTrackPar(%s)' % v, 'ret': r, 'adaptSwitches': s, '__errs': await c.ev(ERRS_JS)})
            for v in ('argb', 'rgba', 'argb'):
                r = await c.ev("(function(){try{return JSON.stringify(window.WikiSfxAdapter.colorOrder('%s'));}catch(e){return 'ERR '+e.message;}})()" % v)
                s = await c.ev(SW_JS)
                seq.append({'call': "colorOrder('%s')" % v, 'ret': r, 'adaptSwitches': s, '__errs': await c.ev(ERRS_JS)})
            F['roundtrip'] = seq
            F['final_state'] = {'colorTrackPar': await c.ev("(function(){return JSON.stringify(window.WikiSfxAdapter.colorTrackPar());})()"),
                                'colorOrder': await c.ev("(function(){return JSON.stringify(window.WikiSfxAdapter.colorOrder());})()"),
                                'adaptSwitches': await c.ev(SW_JS), '__errs': await c.ev(ERRS_JS)}
            print('F roundtrip done; final:', json.dumps(F['final_state'], ensure_ascii=False)); dump()

            RES['net'] = {k: dict(v) for k, v in c.net.items()}
            RES['http_all'] = c.http
            RES['console_all'] = c.console
            RES['exceptions_all'] = c.exc
            RES['eval_exceptions'] = c.eval_exc[-10:]
            RES['stage'] = 'done'; dump()
    finally:
        try:
            ps = subprocess.run(['powershell', '-NoProfile', '-Command',
                                 "(Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'chrome' -and $_.CommandLine -match 'FXVA94_prof' } | Select-Object -ExpandProperty ProcessId) -join ','"],
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
    RES['pins_end'] = pins()
    RES['pins_unchanged'] = {k: (RES['pins_start'][k] == RES['pins_end'][k]) for k in RES['pins_start']}
    RES['final_pin'] = dict(RES['pins_end'])
    RES['stage'] = 'finished'; dump()
    print('pins unchanged:', json.dumps(RES['pins_unchanged'], ensure_ascii=False))
    print('killed:', killed)
    print('->', J)


asyncio.run(main())
