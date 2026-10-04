# -*- coding: utf-8 -*-
"""task-61 测量夹具（**只写、不自动跑**）：SFX 适配器 Model 分支 · 皮肤 1110177 : FX029_models_measure.json

跑法（Lead 先把新 effects.json 重新内联进 viewer.json，再执行）：
    C:\\Users\\Administrator\\AppData\\Local\\hermes\\hermes-agent\\venv\\Scripts\\python.exe ^
        "E:\\la拆包项目\\03拆包产物\\_target_1110171\\fx061_measure.py"

产物目录：%TEMP%\\fx061\\   （PNG + FX029_models_measure.json）
浏览器：**一个** chrome，profile=%TEMP%\\FX061_prof，CDP 端口 **10087**；收尾按 profile 反查 PID + taskkill /T /F，
        并核对 chrome.exe 残留 = 0、端口已释放（try/finally，异常路径同样执行）。

依赖：stdlib + websocket-client（本机未装 ⇒ 自动回落本机已有的 websockets 15.0.1，走线程内 asyncio 事件循环，
      对外仍是同一套同步 API）。像素统计优先 PIL+numpy，缺失则用 zlib+struct 手写 PNG 解码（不装任何新包）。

步骤（严格按 order，全部只读 + 开关；不改 adapter/viewer.js/viewer.json/effects.json/board/manifest/registry）：
  1  pin 表（sha256[:16].upper + size）跑前 / 跑后各一次
  2  点 `.wv-sfx` 让适配器 attach → 读 diag：modelsOn + models[] 汇总 + 逐行数组
  3  默认关 + 零操作：同相位两帧 sha16 必须逐字节相同，且断言 modelsOn===false
  4  WikiSfxAdapter.models(false)          → 1 帧 + diag（期望 0 可见）
  5  WikiSfxAdapter.models(true)           → 轮询（≤20s / 250ms）直到无 models[].state==='loading' → 1 帧 + diag + 页面错误
  6  WikiSfxAdapter.modelsHighlight(false) → 1 帧 + diag（emissiveIntensity / highlight_state 必须变）
  7  WikiSfxAdapter.modelMaterial('normal')→ 1 帧（负控）+ diag blending → 复原 additive + highlight(true)
  8  每个 PNG：全页 sha16 / size / 全白像素占比（255 精确 + 255±2 两口径）/ 平均亮度 / nonBlackRatio
  9  收尾清理（profile 反查 + taskkill /T /F + 无残留 chrome + 端口空闲）
 10  紧凑汇总 + 写 JSON

⚠ 与参考夹具（reg48_flash.py / fx58v_verify.py）的差异（假设）：
  ① 计数状态用 `modelsForce`（模型分支真实的强制开关）而非按源 `modelsOnAtAttach/effects.models_enabled`
     —— 参考夹具用 `.wv-sfx` 点击 → `setEnabled()`，它只切**特效组**（精灵/粒子），不切 Model 分支。
     默认关的字节同一性由 attempt1（零操作两帧）保证；`modelsOn` 若适配器给出也会一并记录。
  ② 「同相位」= 开跑前一次性 `__sfxTime(PHASE)` 冻结，两帧之间**不再调用任何 API**；若两帧仍不同，
     attempt2 会在每次截图前重放 `__sfxTime(PHASE)`（这是唯一的"触碰"，如实记录 phase_hold=true）。
  ③ 「全白像素占比」参考夹具未定义，本夹具同时给 255 精确口径与 255±2 容差口径。
  ④ 板文件：`08Lifeafter wiki\\board.html`（无 `assets\\board.html`）。
"""
import asyncio
import base64
import hashlib
import io
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import concurrent.futures
import threading
import time
import urllib.request
import zlib

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')   # 控制台是 GBK，Python 输出强制 UTF-8
except Exception:
    pass

# ----------------------------------------------------------------------------------
# 常量 / 路径
# ----------------------------------------------------------------------------------
CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
W = r'E:\la拆包项目\08Lifeafter wiki'
TGT = r'E:\la拆包项目\03拆包产物\_target_1110171'
SELF = os.path.join(TGT, 'fx061_measure.py')
TMP = os.environ.get('TEMP') or r'C:\Users\<user>\AppData\Local\Temp'
OUT = os.path.join(TMP, 'fx061')
PROFILE = os.path.join(TMP, 'FX061_prof')
PORT = 10087
SKIN = '1110177'
BOARD_URL = 'http://127.0.0.1:8765/board.html?b=weapon_skin_sfx_text_sources&view=wiki&sort=id&dir=desc'
JSON_OUT = os.path.join(OUT, 'FX029_models_measure.json')
PHASE = 1.175                       # 名义相位（参考夹具 fx58v_verify.py 的 A/B 取样点之一）
LOAD_POLL_S, LOAD_POLL_MS = 20.0, 250
SETTLE = 1.2                        # 每次开关后的静置（参考夹具用 1.2–2.5s）
# 默认：step3 的「默认关」是硬门（modelsOn 必须存在且为 false，且两帧逐字节相同）。
# 若适配器尚未暴露 modelsOn 字段、Lead 只想取证不想被门挡住：设 FX061_ALLOW_DEFAULT_ON=1。
STRICT_STEP3 = (os.environ.get('FX061_ALLOW_DEFAULT_ON', '') != '1')

PIN_FILES = [
    ('adapter', r'assets\weapon_skin_sfx_adapter.js'),
    ('effects_1110177', r'assets\3d\weapon_skin\1110177\effects.json'),
    ('viewer_1110177', r'assets\3d\weapon_skin\1110177\viewer.json'),
    ('viewer_js', r'assets\weapon_skin_viewer.js'),
    ('board', r'board.html'),
]
PIN_OPTIONAL = [r'board.html.bak_cachebust_20260919_184423']
PIN_EXTRA = [r'assets\3d\weapon_skin\1110171\viewer.json',
             r'assets\3d\weapon_skin\1110171\effects.json']
ROW_KEYS = ['name', 'class', 'glb', 'state', 'hasObj', 'objVisible', 'groupVisible', 'visible',
            'opacity', 'opacity_src', 'emissive_src', 'diffuse_src', 'fallback_reason', 'tex_bound',
            'drivers_used', 'blending', 'depthWrite', 'depthTest', 'polygonOffset',
            'highlight_state', 'highlight_src', 'emissiveIntensity', 'omitted_undeclared', 'confidence']

# ----------------------------------------------------------------------------------
# 依赖探测（PIL / numpy 可选；websocket-client 优先，回落 websockets）
# ----------------------------------------------------------------------------------
try:
    import numpy as _np
except Exception:
    _np = None
try:
    from PIL import Image as _PILImage
except Exception:
    _PILImage = None
try:
    import websocket as _wsc                      # websocket-client
except Exception:
    _wsc = None
try:
    from websockets.asyncio.client import connect as _ws_connect
except Exception:
    try:
        from websockets.legacy.client import connect as _ws_connect
    except Exception:
        _ws_connect = None

TRANSPORT = ('websocket-client ' + str(getattr(_wsc, '__version__', '?'))) if _wsc else \
            (('websockets(asyncio) ' + str(getattr(sys.modules.get('websockets'), '__version__', '?')))
             if _ws_connect else 'NONE')
PIXEL_ENGINE = ('PIL ' + str(getattr(_PILImage, '__version__', '?'))) if _PILImage else 'zlib+struct(manual)'

RES = {
    'task': 'task-61 / FX029 Model 分支测量',
    'harness': os.path.abspath(__file__),
    'harness_sha16': None,
    'skin': SKIN,
    'board_url': BOARD_URL,
    'cdp_port': PORT,
    'profile': PROFILE,
    'out_dir': OUT,
    'phase': PHASE,
    'started_at': time.strftime('%Y-%m-%d %H:%M:%S'),
    'transport': TRANSPORT,
    'pixel_engine': PIXEL_ENGINE,
    'numpy': (getattr(_np, '__version__', '?') if _np is not None else None),
    'note': '只读 + 开关；单浏览器（专用 profile）；按 profile 反查 PID taskkill /T /F 收尾',
    'steps': [],
    'frames': [],
    'errors': [],
    'warnings': [],
}


def log(msg):
    print('[%s] %s' % (time.strftime('%H:%M:%S'), msg))


def warn(msg):
    RES['warnings'].append(msg)
    log('WARN ' + msg)


def dump():
    try:
        with io.open(JSON_OUT, 'w', encoding='utf-8') as f:
            json.dump(RES, f, ensure_ascii=False, indent=1)
    except Exception as e:
        print('!! JSON 写入失败: %s' % e)


# ----------------------------------------------------------------------------------
# pin 表
# ----------------------------------------------------------------------------------
def file_pin(rel):
    p = os.path.join(W, rel)
    try:
        b = io.open(p, 'rb').read()
        return {'path': p, 'sha16': hashlib.sha256(b).hexdigest()[:16].upper(), 'size': len(b)}
    except Exception as e:
        return {'path': p, 'sha16': 'MISSING', 'size': None, 'error': '%s: %s' % (type(e).__name__, e)}


def pins():
    out = {}
    for k, rel in PIN_FILES:
        out[k] = file_pin(rel)
    for rel in PIN_OPTIONAL:
        p = os.path.join(W, rel)
        if os.path.exists(p):
            out['board_backup:' + os.path.basename(rel)] = file_pin(rel)
    for rel in PIN_EXTRA:
        p = os.path.join(W, rel)
        if os.path.exists(p):
            out['extra:' + os.path.basename(os.path.dirname(rel)) + '_' + os.path.basename(rel)] = file_pin(rel)
    return out


def pin_diff(a, b):
    diff = {}
    for k in sorted(set(a) | set(b)):
        x = (a.get(k) or {}).get('sha16')
        y = (b.get(k) or {}).get('sha16')
        if x != y:
            diff[k] = {'before': x, 'after': y}
    return diff


# ----------------------------------------------------------------------------------
# PNG → 像素（PIL 优先；否则 zlib+struct 手写解码：8bit / 非隔行 / color type 0|2|4|6）
# ----------------------------------------------------------------------------------
def png_header(b):
    if b[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError('not a PNG')
    i, w, h, bd, ct, inter, idat = 8, None, None, None, None, None, []
    while i + 8 <= len(b):
        ln = struct.unpack_from('>I', b, i)[0]
        typ = b[i + 4:i + 8]
        data = b[i + 8:i + 8 + ln]
        if typ == b'IHDR':
            w, h, bd, ct, _comp, _filt, inter = struct.unpack('>IIBBBBB', data[:13])
        elif typ == b'IDAT':
            idat.append(data)
        elif typ == b'IEND':
            break
        i += 12 + ln
    return w, h, bd, ct, inter, b''.join(idat)


def png_rgb_bytes(raw):
    w, h, bd, ct, inter, idat = png_header(raw)
    if bd != 8 or inter != 0 or ct not in (0, 2, 4, 6):
        raise ValueError('unsupported PNG fmt bd=%s inter=%s ct=%s' % (bd, inter, ct))
    nch = {0: 1, 2: 3, 4: 2, 6: 4}[ct]
    stride = w * nch
    d = zlib.decompress(idat)
    out = bytearray(h * stride)
    pos, prev = 0, bytearray(stride)
    for y in range(h):
        ft = d[pos]
        pos += 1
        line = bytearray(d[pos:pos + stride])
        pos += stride
        if ft == 1:
            for x in range(nch, stride):
                line[x] = (line[x] + line[x - nch]) & 255
        elif ft == 2:
            for x in range(stride):
                line[x] = (line[x] + prev[x]) & 255
        elif ft == 3:
            for x in range(stride):
                a = line[x - nch] if x >= nch else 0
                line[x] = (line[x] + ((a + prev[x]) >> 1)) & 255
        elif ft == 4:
            for x in range(stride):
                a = line[x - nch] if x >= nch else 0
                c = prev[x - nch] if x >= nch else 0
                bb = prev[x]
                p = a + bb - c
                pa, pb, pc = abs(p - a), abs(p - bb), abs(p - c)
                pr = a if (pa <= pb and pa <= pc) else (bb if pb <= pc else c)
                line[x] = (line[x] + pr) & 255
        elif ft != 0:
            raise ValueError('bad filter %s' % ft)
        out[y * stride:(y + 1) * stride] = line
        prev = line
    if ct == 2:
        return bytes(out), w, h
    rgb = bytearray(w * h * 3)
    if ct == 6:
        for i in range(w * h):
            rgb[3 * i:3 * i + 3] = out[4 * i:4 * i + 3]
    elif ct == 0:
        for i in range(w * h):
            v = out[i]
            rgb[3 * i] = rgb[3 * i + 1] = rgb[3 * i + 2] = v
    else:                                        # ct == 4: gray+alpha，合成到黑底
        for i in range(w * h):
            v = out[2 * i]
            a = out[2 * i + 1]
            v = (v * a + 0 * (255 - a)) // 255
            rgb[3 * i] = rgb[3 * i + 1] = rgb[3 * i + 2] = v
    return bytes(rgb), w, h


def png_stats(raw):
    """全页 sha16 / size / 全白占比（255 精确 + 255±2）/ 平均亮度 / nonBlackRatio。"""
    st = {'sha16': hashlib.sha256(raw).hexdigest()[:16].upper(), 'size': len(raw)}
    try:
        if _PILImage is not None and _np is not None:
            im = _PILImage.open(io.BytesIO(raw)).convert('RGB')
            a = _np.asarray(im, dtype=_np.uint8).reshape(-1, 3).astype(_np.int16)
            st['w'], st['h'] = im.size
            st['engine'] = 'pillow+numpy'
        else:
            buf, w, h = png_rgb_bytes(raw)
            st['w'], st['h'] = w, h
            st['engine'] = 'zlib+struct'
            a = (_np.frombuffer(buf, dtype=_np.uint8).reshape(-1, 3).astype(_np.int16)
                 if _np is not None else None)
            if a is None:
                n = w * h
                w255 = wn = 0
                nz = 0
                ls = 0
                for i in range(0, n * 3, 3):
                    r, g, b = buf[i], buf[i + 1], buf[i + 2]
                    if r == 255 and g == 255 and b == 255:
                        w255 += 1
                    if r >= 253 and g >= 253 and b >= 253:
                        wn += 1
                    if r > 8 or g > 8 or b > 8:
                        nz += 1
                    ls += 0.2126 * r + 0.7152 * g + 0.0722 * b
                st.update({'n_px': n, 'white255_ratio': round(w255 / float(n), 8),
                           'white_near_ratio': round(wn / float(n), 8),
                           'mean_luminance_0_255': round(ls / float(n), 4),
                           'nonblack_ratio': round(nz / float(n), 8)})
                return st
        n = int(a.shape[0])
        m255 = (a[:, 0] == 255) & (a[:, 1] == 255) & (a[:, 2] == 255)
        mnear = (a[:, 0] >= 253) & (a[:, 1] >= 253) & (a[:, 2] >= 253)
        nz = (a[:, 0] > 8) | (a[:, 1] > 8) | (a[:, 2] > 8)
        lum = 0.2126 * a[:, 0] + 0.7152 * a[:, 1] + 0.0722 * a[:, 2]
        st.update({'n_px': n,
                   'white255_px': int(m255.sum()), 'white255_ratio': round(float(m255.mean()), 8),
                   'white_near_px': int(mnear.sum()), 'white_near_ratio': round(float(mnear.mean()), 8),
                   'mean_luminance_0_255': round(float(lum.mean()), 4),
                   'nonblack_px': int(nz.sum()), 'nonblack_ratio': round(float(nz.mean()), 8)})
    except Exception as e:
        st['stat_error'] = '%s: %s' % (type(e).__name__, str(e)[:200])
    return st


# ----------------------------------------------------------------------------------
# Chrome 进程 / 端口
# ----------------------------------------------------------------------------------
def pid_alive(pid):
    try:
        r = subprocess.run(['tasklist', '/FI', 'PID eq %d' % pid, '/NH'],
                           capture_output=True, text=True, timeout=30)
        return str(pid) in (r.stdout or '')
    except Exception:
        return False


def kill_tree(pid):
    try:
        subprocess.run(['taskkill', '/PID', str(pid), '/T', '/F'], capture_output=True, timeout=60)
        return True
    except Exception:
        return False


def chrome_pids_by_profile(tag):
    """按命令行里的 profile 目录名反查 chrome.exe（与参考夹具同口径）。"""
    ps = ("(Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'chrome' -and "
          "$_.CommandLine -match '%s' } | Select-Object -ExpandProperty ProcessId) -join ','" % tag)
    try:
        r = subprocess.run(['powershell', '-NoProfile', '-Command', ps],
                           capture_output=True, text=True, timeout=90)
        return [int(x) for x in (r.stdout or '').strip().split(',') if x.strip().isdigit()]
    except Exception:
        return []


def chrome_count():
    try:
        r = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq chrome.exe', '/NH'],
                           capture_output=True, text=True, timeout=30)
        return sum(1 for ln in (r.stdout or '').splitlines() if 'chrome.exe' in ln.lower())
    except Exception:
        return -1


def port_listening(port):
    ps = ("(Get-NetTCPConnection -LocalPort %d -State Listen -ErrorAction SilentlyContinue | "
          "Measure-Object).Count" % port)
    try:
        r = subprocess.run(['powershell', '-NoProfile', '-Command', ps],
                           capture_output=True, text=True, timeout=60)
        return int((r.stdout or '0').strip() or 0) > 0
    except Exception:
        return None


def http_json(url, timeout=3):
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return json.loads(r.read().decode('utf-8', 'replace'))


# ----------------------------------------------------------------------------------
# CDP：websocket-client 优先；否则线程内 asyncio + websockets（对外同一套同步 API）
# ----------------------------------------------------------------------------------
def _on_event(d, m):
    """★ 注意：d 是 Driver **实例**（不是 dict）。旧版写成 d['events'] 会在**第一条页面事件**
    （consoleAPICalled/exceptionThrown/Log.entryAdded）上抛 TypeError，读线程随即静默退出 ⇒
    之后所有 call() 只能等到超时。这是"桩自检"抓到的第 2 个真 bug。"""
    meth = m.get('method')
    if meth == 'Runtime.consoleAPICalled':
        p = m.get('params') or {}
        if p.get('type') in ('error', 'assert', 'warning'):
            args = []
            for a in (p.get('args') or [])[:6]:
                v = a.get('value')
                if v is None:
                    v = a.get('description') or a.get('unserializableValue')
                args.append(str(v)[:160])
            d.events.append({'kind': 'console', 'type': p.get('type'),
                             'text': ' | '.join(args)[:400], 't': round(time.time(), 3)})
    elif meth == 'Runtime.exceptionThrown':
        dd = (m.get('params') or {}).get('exceptionDetails') or {}
        d.events.append({'kind': 'exceptionDetails', 'text': str(dd.get('text'))[:200],
                         'desc': str((dd.get('exception') or {}).get('description'))[:300],
                         'url': (dd.get('url') or '')[-80:], 'line': dd.get('lineNumber'),
                         'col': dd.get('columnNumber'),
                         'scriptId': str(dd.get('scriptId') or '')[-12:], 't': round(time.time(), 3)})
    elif meth == 'Log.entryAdded':
        e = (m.get('params') or {}).get('entry') or {}
        if e.get('level') == 'error' and 'favicon' not in (e.get('url') or ''):
            d.events.append({'kind': 'log', 'text': (e.get('text') or '')[:200],
                             'url': (e.get('url') or '')[-80:], 't': round(time.time(), 3)})


class Driver(object):
    # task-61 修复（chain-auditor）：go() 里部分调用点把 Driver 自身当作会话对象传入（render_now(C, …) 内再写 C.d.ev），
    # 于是访问 Driver.d 抛 AttributeError。Driver 已具备 ev/jv/shot/call，故自引用别名即可让两种调用风格都成立。
    # （不改变任何测量语义，只修对象别名。）
    d = None
    def __init__(self, ws_url, timeout=90):
        self.url, self.timeout, self.i = ws_url, timeout, 0
        self.pend, self.events, self.notes = {}, [], []
        self.mode = None
        self.reader_err = None
        self._lock = threading.Lock()
        self._loop = self._ws = self._th = None
        self._closed = False
        self._sync_ws = None

    # ---------- 连接 ----------
    def open(self):
        if _wsc is not None:
            try:
                self._open_sync()
                self.mode = 'websocket-client'
                return self.mode
            except Exception as e:
                self.notes.append('websocket-client 连接失败，回落 websockets：%s' % str(e)[:120])
        if _ws_connect is None:
            raise RuntimeError('无可用 websocket 实现（websocket-client 与 websockets 都不可用）')
        self._open_async()
        self.mode = 'websockets(asyncio/thread)'
        return self.mode

    def _open_sync(self):
        self._sync_ws = _wsc.create_connection(self.url, timeout=self.timeout, max_size=None,
                                               enable_multithread=True)
        try:
            self._sync_ws.settimeout(0.25)
        except Exception:
            pass
        self._sync_ws.send(json.dumps({'id': 0, 'method': 'Runtime.enable'}))

    def _open_async(self):
        c = {'ready': threading.Event(), 'err': None}

        async def main():
            try:
                async with _ws_connect(self.url, max_size=None, max_queue=None,
                                       open_timeout=30, close_timeout=5) as ws:
                    self._ws = ws
                    try:
                        ws.transport.get_extra_info('socket').settimeout(0.25)
                    except Exception:
                        pass
                    c['ready'].set()
                    async for raw in ws:
                        try:
                            m = json.loads(raw)
                        except Exception:
                            continue
                        i = m.get('id')
                        if i is not None:
                            f = self.pend.pop(i, None)
                            if f is not None and not f.done():
                                f.set_result(m)
                        else:
                            try:
                                _on_event(self, m)
                            except Exception as ee:
                                # 事件解析出错绝不能拖死读线程（否则后续调用只会超时，症状被掩盖）
                                self.notes.append('on_event_err: %s: %s' % (type(ee).__name__, str(ee)[:120]))
            except Exception as e:
                self.reader_err = '%s: %s' % (type(e).__name__, str(e)[:200])
                c['err'] = self.reader_err
                c['ready'].set()
                # ★ 读线程死了 ⇒ 立刻叫醒所有等待者（否则表现为"CDP 莫名超时"）
                for k, f in list(self.pend.items()):
                    self.pend.pop(k, None)
                    if not f.done():
                        f.set_exception(RuntimeError('reader died: %s' % self.reader_err))

        self._loop = asyncio.new_event_loop()
        self._th = threading.Thread(target=lambda: self._loop.run_until_complete(main()),
                                    name='fx061-ws', daemon=True)
        self._th.start()
        if not c['ready'].wait(45) or c['err']:
            raise RuntimeError('websockets 连接失败：%s' % (c['err'] or 'timeout'))
        self.call('Runtime.enable')

    # ---------- 同步外观 ----------
    def call(self, method, timeout=None, **params):
        if self._closed:
            raise RuntimeError('driver closed')
        to = float(timeout or self.timeout)
        with self._lock:
            self.i += 1
            i = self.i
            # task-61 修复（chain-auditor）：跨线程等待必须用 concurrent.futures.Future ——
            # asyncio 的 Future.result() **不接受 timeout 参数**，原先在调用线程里 fut.result(to)
            # 会抛 `TypeError: Future.result() takes no arguments (1 given)`，导致 CDP 首个调用即失败。
            # 接收协程里用的 f.set_result(m) 对两种 Future 都成立，故只需换构造。
            fut = concurrent.futures.Future() if self._loop is not None else None
            if fut is not None:
                self.pend[i] = fut
            msg = json.dumps({'id': i, 'method': method, 'params': params})
            try:
                if self._loop is not None:
                    asyncio.run_coroutine_threadsafe(self._ws.send(msg), self._loop).result(20)
                else:
                    self._sync_ws.send(msg)
            except Exception as e:
                if fut is not None:
                    self.pend.pop(i, None)
                raise RuntimeError('send %s failed: %s' % (method, str(e)[:160]))
        if fut is not None:
            r = fut.result(to)
        else:
            r = self._recv_until(i, to)
        if r is None:
            raise RuntimeError('CDP timeout %.0fs: %s' % (to, method))
        if 'error' in r:
            raise RuntimeError('CDP error %s: %s' % (method, str(r['error'])[:200]))
        return r.get('result') or {}

    def _recv_until(self, i, to):
        end = time.time() + to
        while time.time() < end:
            try:
                raw = self._sync_ws.recv()
            except Exception:
                time.sleep(0.01)
                continue
            if not raw:
                continue
            try:
                m = json.loads(raw)
            except Exception:
                continue
            j = m.get('id')
            if j == 0:
                continue
            if j is not None:
                if j == i:
                    return m
                self.notes.append('orphan response id=%s' % j)
            else:
                _on_event(self, m)
        return None

    def ev(self, js, timeout=None):
        try:
            r = self.call('Runtime.evaluate', timeout=timeout, expression=js,
                          returnByValue=True, awaitPromise=True)
        except Exception as e:
            return {'__exc__': 'call_fail: %s' % str(e)[:200]}
        if r.get('exceptionDetails'):
            d = r['exceptionDetails']
            return {'__exc__': '%s | %s' % (d.get('text'),
                                            str((d.get('exception') or {}).get('description'))[:220])}
        v = (r.get('result') or {}).get('value')
        if v is None and (r.get('result') or {}).get('type') == 'object' and \
                (r.get('result') or {}).get('subtype') == 'null':
            return None
        return v

    def jv(self, js, timeout=None):
        """evaluate → JSON.parse（页面侧 JSON.stringify ⇒ returnByValue 直接给对象）。"""
        v = self.ev(js, timeout=timeout)
        if isinstance(v, (dict, list)):
            return v
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return {'__raw__': v[:400]}
        return v

    def shot(self, timeout=120):
        r = self.call('Page.captureScreenshot', timeout=timeout, format='png')
        return base64.b64decode(r.get('data', ''))

    def close(self):
        if self._closed:
            return
        self._closed = True
        try:
            if self._sync_ws is not None:
                try:
                    self._sync_ws.send(json.dumps({'id': 999999, 'method': 'Browser.close'}))
                except Exception:
                    pass
                time.sleep(0.4)
                try:
                    self._sync_ws.close()
                except Exception:
                    pass
            if self._loop is not None:
                for f in list(self.pend.values()):
                    if not f.done():
                        f.set_result(None)
                self.pend.clear()
                try:
                    asyncio.run_coroutine_threadsafe(self._ws.close(), self._loop).result(5)
                except Exception:
                    pass
                try:
                    self._loop.call_soon_threadsafe(self._loop.stop)
                except Exception:
                    pass
                self._th.join(timeout=5)
        except Exception:
            pass


# ----------------------------------------------------------------------------------
# 页面侧探针 JS（全部 JSON.stringify ⇒ 一次 returnByValue）
# ----------------------------------------------------------------------------------
JS_READY = ("(function(){try{var A=window.WikiWeaponViewer;return JSON.stringify({rs:document.readyState,"
            "adapter:typeof window.WikiSfxAdapter,"
            "hasSprites:typeof (window.WikiSfxAdapter&&window.WikiSfxAdapter.sprites),"
            "hasSw:typeof (window.WikiSfxAdapter&&window.WikiSfxAdapter.adaptSwitches),"
            "hasModels:typeof (window.WikiSfxAdapter&&window.WikiSfxAdapter.models),"
            "hasHL:typeof (window.WikiSfxAdapter&&window.WikiSfxAdapter.modelsHighlight),"
            "hasMat:typeof (window.WikiSfxAdapter&&window.WikiSfxAdapter.modelMaterial)});}catch(e){return 'ERR '+e.message;}})()")

JS_BTN = ("(function(){var b=document.querySelector('.wv-sfx');"
          "return b?JSON.stringify({text:b.textContent,disabled:!!b.disabled,pressed:b.getAttribute('aria-pressed'),"
          "title:b.title}):'NO_BTN';})()")

# 「适配器是否已经 attach」——参考夹具靠 adaptSwitches，这里直接看 diag 是否已脱离 no_attach
JS_ATTACH = ("(function(){try{var A=window.WikiSfxAdapter;if(!A)return JSON.stringify({attached:false,why:'no_adapter'});"
             "var d=(typeof A.__sfxDiag==='function')?A.__sfxDiag():null;"
             "var p=(typeof A.__probe==='function')?A.__probe():null;"
             "return JSON.stringify({attached:!!(d&&d.weapon_diag!==undefined)||!!p,"
             "diagErr:(d&&d.err)||null,hasDiag:!!d,hasProbe:!!p,"
             "keys:d?Object.keys(d).slice(0,40):null,modelsInDiag:!!(d&&d.models)});}catch(e){return 'ERR '+e.message;}})()")

JS_LOADING = ("(function(){var A=window.WikiSfxAdapter;if(!A)return -1;"
              "var p=(typeof A.__probe==='function')?A.__probe():null;"
              "var r=(p&&p.models)||null;if(!r)return -1;var n=0;"
              "for(var i=0;i<r.length;i++){if(r[i]&&r[i].state==='loading')n++;}return n;})()")

JS_DIAG_FULL = r"""
(function(){
  try{
    var A = window.WikiSfxAdapter;
    if(!A) return JSON.stringify({err:'no_adapter'});
    var d = (typeof A.__sfxDiag === 'function') ? A.__sfxDiag() : null;
    var p = (typeof A.__probe === 'function') ? A.__probe() : null;
    if(!d && !p) return JSON.stringify({err:'no_probe'});
    var arr = null, src = null;
    if(d && d.models){ arr = d.models; src = '__sfxDiag.models'; }
    else if(d && d.modelRows){ arr = d.modelRows; src = '__sfxDiag.modelRows'; }
    else if(p && p.models){ arr = p.models; src = '__probe.models'; }
    else if(p && p.modelRows){ arr = p.modelRows; src = '__probe.modelRows'; }
    var KEYS = ['name','class','glb','state','hasObj','objVisible','groupVisible','visible','scale',
                'opacity','opacity_src','emissive_src','diffuse_src','fallback_reason','tex_bound',
                'drivers_used','drivers','unwired','omitted_undeclared','blending','blending_asserted',
                'depthWrite','depthTest','polygonOffset','polygonOffsetUnits','depth_bias_state',
                'highlight_state','highlight_src','emissiveIntensity','confidence','approx','approx_reason',
                'measured','expectedSpan','spelling_variant'];
    var rows = [];
    if(arr) for(var i=0;i<arr.length;i++){
      var r = arr[i] || {}, o = {}, k;
      for(var j=0;j<KEYS.length;j++){ k = KEYS[j]; if(r[k] !== undefined) o[k] = r[k]; }
      o.__min = (r.drivers_used !== undefined) ? null : true;
      rows.push(o);
    }
    function cnt(key){
      var m = {};
      for(var i=0;i<rows.length;i++){ var v = rows[i][key]; if(v===undefined||v===null) v='(null)'; v=String(v); m[v]=(m[v]||0)+1; }
      return m;
    }
    var vis=0, hasObj=0, gv=0, loading=0;
    for(var i=0;i<rows.length;i++){
      if(rows[i].visible) vis++;
      if(rows[i].hasObj) hasObj++;
      if(rows[i].groupVisible) gv++;
      if(rows[i].state==='loading') loading++;
    }
    var inv = [];
    for(var i=0;i<rows.length;i++){
      var exp = !!(rows[i].groupVisible && rows[i].hasObj);
      if(!!rows[i].visible !== exp) inv.push(rows[i].name);
    }
    var st = {};
    for(var i=0;i<rows.length;i++){ var s = rows[i].state; if(st[s]===undefined) st[s]=0; st[s]++; }
    /* ★ 显式保留「键是否存在」与「值是否为 false」的区别（undefined 会被 JSON 丢掉，
       而 modelsOn===false 是本测量里最重要的断言之一） */
    var out = { src: src, counts: {rows: rows.length, visible: vis, hasObj: hasObj, groupVisible: gv,
                                    loading: loading, by_class: cnt('class'), by_state: st,
                                    by_fallback_min: cnt('__min')},
                invariants: {visible_neq_groupVisible_and_hasObj: inv}, rows: rows };
    function pick(dst, srco, k){
      if(srco && srco[k] !== undefined){ dst[k] = srco[k]; }
      else { dst[k] = {__absent__: true, __from__: k}; }
    }
    pick(out, d, 'modelsOn'); if(out.modelsOn && out.modelsOn.__absent__ && p && p.modelsOn !== undefined){ out.modelsOn = p.modelsOn; }
    pick(out, d, 'modelsForce'); if(out.modelsForce && out.modelsForce.__absent__ && p && p.modelsForce !== undefined){ out.modelsForce = p.modelsForce; }
    pick(out, d, 'modelsOnAtAttach'); if(out.modelsOnAtAttach && out.modelsOnAtAttach.__absent__ && p && p.modelsOnAtAttach !== undefined){ out.modelsOnAtAttach = p.modelsOnAtAttach; }
    pick(out, d, 'modelBlend'); if(out.modelBlend && out.modelBlend.__absent__ && p && p.modelBlend !== undefined){ out.modelBlend = p.modelBlend; }
    pick(out, d, 'modelBlendK'); if(out.modelBlendK && out.modelBlendK.__absent__ && p && p.modelBlendK !== undefined){ out.modelBlendK = p.modelBlendK; }
    pick(out, d, 'modelNodes'); if(out.modelNodes && out.modelNodes.__absent__ && p && p.modelNodes !== undefined){ out.modelNodes = p.modelNodes; }
    pick(out, d, 'modelsLoaded'); pick(out, d, 'modelsFailed'); pick(out, d, 'modelsNoMeshField');
    pick(out, d, 'modelsBase'); if(out.modelsBase && out.modelsBase.__absent__ && p && p.modelsBaseOverride !== undefined){ out.modelsBase = p.modelsBaseOverride; }
    pick(out, d, 'loadErrors'); if(out.loadErrors && out.loadErrors.__absent__ && p && p.loadErrors !== undefined){ out.loadErrors = p.loadErrors.slice(0,20); }
    pick(out, d, 'spriteNodes'); pick(out, d, 'particleSystems');
    pick(out, p, 'groupVisible'); pick(out, p, 'enabled'); pick(out, p, 'fixedTime');
    out.aliveNow = (p && p.sprites) ? p.sprites.filter(function(s){return s.visible;}).length
                                    : ((d && d.alive_now !== undefined) ? d.alive_now : null);
    return JSON.stringify(out);
  }catch(e){ return JSON.stringify({err:String((e&&e.message)||e)}); }
})()
"""

JS_MARKS = ("(function(){var A=window.WikiSfxAdapter;var out={hl:null,blend:null,ev:[]};try{out.hl="
            "(typeof A.modelsHighlight==='function')?A.modelsHighlight():null;}catch(e){out.hl='ERR '+e.message;}"
            "try{var d=(typeof A.__sfxDiag==='function')?A.__sfxDiag():null;var p=A.__probe?A.__probe():null;"
            "out.blend=(d&&d.modelBlend!==undefined)?d.modelBlend:(p?p.modelBlend:null);"
            "var arr=(d&&d.models)||(p&&p.models)||[];"
            "for(var i=0;i<arr.length;i++){var r=arr[i]||{};if(r.class==='A')out.ev.push([r.name,r.emissiveIntensity,r.highlight_state]);}}"
            "catch(e){out.ev='ERR '+e.message;}"
            "return JSON.stringify(out);})()")

JS_REPORT = ("(function(){try{var s=(window.WikiWeaponViewer.__neox&&window.WikiWeaponViewer.__neox())||null;"
             "var rep=(s&&s.report)||{};return JSON.stringify({applied:rep.applied,"
             "prims_n:(rep.prims||[]).length,failed:rep.failed,missing:rep.missing,"
             "env_warn:rep.env_warn,neoxMode:(s&&s.mode)||null});}catch(e){return 'ERR '+e.message;}})()")


def summarize(diag):
    """把 JS_DIAG_FULL 的结果压成紧凑摘要（JSON 里两个都留）。"""
    rows = (diag or {}).get('rows') or []
    by_class, by_state, hl, bl = {}, {}, {}, {}
    vis = hasobj = 0
    for r in rows:
        c = str(r.get('class'))
        by_class[c] = by_class.get(c, 0) + 1
        s = str(r.get('state'))
        by_state[s] = by_state.get(s, 0) + 1
        h = str(r.get('highlight_state'))
        hl[h] = hl.get(h, 0) + 1
        b = str(r.get('blending'))
        bl[b] = bl.get(b, 0) + 1
        if r.get('visible'):
            vis += 1
        if r.get('hasObj'):
            hasobj += 1
    return {'src': (diag or {}).get('src'), 'modelsOn': (diag or {}).get('modelsOn'),
            'modelsForce': (diag or {}).get('modelsForce'),
            'modelsOnAtAttach': (diag or {}).get('modelsOnAtAttach'),
            'modelBlend': (diag or {}).get('modelBlend'), 'modelBlendK': (diag or {}).get('modelBlendK'),
            'rows': len(rows), 'visible': vis, 'hasObj': hasobj,
            'by_class': by_class, 'by_state': by_state, 'by_highlight_state': hl, 'by_blending': bl,
            'loading': sum(1 for r in rows if r.get('state') == 'loading'),
            'fallback_reasons': sorted({str(r.get('fallback_reason')) for r in rows if r.get('fallback_reason')}),
            'invariants': (diag or {}).get('invariants'), 'err': (diag or {}).get('err')}


def flat(diag):
    rows = (diag or {}).get('rows') or []
    return [{k: r.get(k) for k in ROW_KEYS} for r in rows]


def marks_line(diag):
    """diag 里的 A 类（name, emissiveIntensity, highlight_state）三元组，用于证明高光开关真的生效。"""
    out = []
    for r in ((diag or {}).get('rows') or []):
        if str(r.get('class')) == 'A':
            out.append([r.get('name'), r.get('emissiveIntensity'), r.get('highlight_state')])
    return out


def mark_delta(a, b):
    da = {str(x[0]): x for x in a}
    db = {str(x[0]): x for x in b}
    changed_ev, changed_hl, only_a, only_b = [], [], [], []
    for k in sorted(set(da) | set(db)):
        if k not in da:
            only_b.append(k)
            continue
        if k not in db:
            only_a.append(k)
            continue
        if da[k][1] != db[k][1]:
            changed_ev.append({'name': k, 'before': da[k][1], 'after': db[k][1]})
        if da[k][2] != db[k][2]:
            changed_hl.append({'name': k, 'before': da[k][2], 'after': db[k][2]})
    return {'emissiveIntensity_changed': changed_ev, 'highlight_state_changed': changed_hl,
            'only_before': only_a, 'only_after': only_b}


# ----------------------------------------------------------------------------------
# 运行时（线程内 asyncio 事件循环；主线程顺序阻塞）
# ----------------------------------------------------------------------------------
class Runtime(object):
    def __init__(self, ws_url):
        self.d = Driver(ws_url)
        self.d.d = self.d          # task-61 修复：自引用别名（见类定义处说明）
        self.loop = asyncio.new_event_loop()
        self.th = threading.Thread(target=self._run, name='fx061-loop', daemon=True)

    def _run(self):
        try:
            self.loop.run_until_complete(self._main())
        except Exception as e:
            RES['errors'].append('runtime: %s: %s' % (type(e).__name__, str(e)[:300]))

    async def _main(self):
        self.d.open()
        log('CDP 已连接（%s）' % self.d.mode)
        while not self.d._closed:
            await asyncio.sleep(0.2)

    def start(self):
        self.th.start()
        t0 = time.time()
        while self.d.mode is None and time.time() - t0 < 50:
            time.sleep(0.2)
        if self.d.mode is None:
            raise RuntimeError('CDP 连接超时；notes=%s' % str(self.d.notes)[:300])
        return self.d

    def close(self):
        try:
            if not self.loop.is_closed():
                fut = asyncio.run_coroutine_threadsafe(self._shutdown(), self.loop)
                fut.result(10)
        except Exception:
            pass
        try:
            self.loop.call_soon_threadsafe(self.loop.stop)
        except Exception:
            pass
        self.th.join(timeout=5)

    async def _shutdown(self):
        try:
            self.d.close()
        except Exception:
            pass


# ----------------------------------------------------------------------------------
# 取值采样
# ----------------------------------------------------------------------------------
def snap(C, tag, note=''):
    t = time.time()
    raw = C.shot()
    st = png_stats(raw)
    fn = 'FX061_%s.png' % tag
    fp = os.path.join(OUT, fn)
    with io.open(fp, 'wb') as f:
        f.write(raw)
    rec = {'tag': tag, 'file': fn, 'path': fp, 'note': note, 't': round(t, 3), 'stats': st}
    RES['frames'].append(rec)
    return rec


def show(C, tag, note=''):
    """截图 + 一次 diag 全量（紧凑摘要 + 逐行数组）。"""
    diag = C.d.jv(JS_DIAG_FULL)
    if not isinstance(diag, dict):
        diag = {'err': 'diag_not_dict: %s' % str(diag)[:200]}
    fr = snap(C, tag, note)
    rec = {'tag': tag, 'note': note, 'at': time.strftime('%H:%M:%S'), 'file': fr['file'],
           'stats': fr['stats'], 'summary': summarize(diag), 'rows': flat(diag),
           'diag_extra': {k: diag.get(k) for k in
                          ('modelsOn', 'modelsForce', 'modelsOnAtAttach', 'modelBlend', 'modelBlendK',
                           'modelNodes', 'modelsLoaded', 'modelsFailed', 'modelsNoMeshField', 'modelsBase',
                           'loadErrors', 'groupVisible', 'enabled', 'fixedTime', 'spriteNodes',
                           'particleSystems', 'aliveNow', 'src', 'err')}}
    RES['steps'].append(rec)
    s = rec['summary']
    log('%-22s sha16=%s white255=%.5f class=%s state=%s visible=%s hasObj=%s' % (
        tag, fr['stats'].get('sha16'), (fr['stats'].get('white255_ratio') or 0.0),
        json.dumps(s.get('by_class'), ensure_ascii=False), json.dumps(s.get('by_state'), ensure_ascii=False),
        s.get('visible'), s.get('hasObj')))
    dump()
    return rec


def render_now(C, n=1, phase=None):
    """强制渲染 n 帧（每次 WebGL 调用后清空缓冲，否则 headless 截图可能是旧帧）。"""
    C.d.ev("(function(){var A=window.WikiWeaponViewer;var v=(typeof __wv==='function')?__wv():null;"
           "v=v||(A&&A.__state&&A.__state());"
           "var f=0;if(v&&v.renderer&&v.scene&&v.camera){for(var i=0;i<%d;i++)v.renderer.render(v.scene,v.camera);f=1;}"
           "if(A&&A.__sfxTime&&%s!==null)A.__sfxTime(%s);"
           "return String(f);})()" % (n, 'null' if phase is None else phase,
                                      'null' if phase is None else phase))


# ----------------------------------------------------------------------------------
# 主流程
# ----------------------------------------------------------------------------------
async def go():
    os.makedirs(OUT, exist_ok=True)
    # ---- 开机自检：控制台/JSON 的 UTF-8 往返 + 选择器字面量（不依赖浏览器）----
    try:
        probe = '选择器 .wv-sfx / 文本 SFX 关闭 ↔ SFX 开启 / 全白占比'
        rt = json.loads(json.dumps({'s': probe}, ensure_ascii=False))['s'] == probe
        sel = bool(re.search(r'\.wv-sfx', "var b=document.querySelector('.wv-sfx');"))
        RES['_static_ok'] = bool(rt and sel)
        RES['_static_detail'] = {'utf8_json_roundtrip': rt, 'selector_literal_matches': sel,
                                 'stdout_encoding': (getattr(sys.stdout, 'encoding', None) or '?'),
                                 'sample': probe}
    except Exception as e:
        RES['_static_ok'] = False
        RES['_static_detail'] = {'err': str(e)[:120]}
    run = {'pins_before': pins(), 'cdp_port': PORT, 'profile': PROFILE,
           'chrome_exe': CHROME, 'board_url': BOARD_URL, 'phase': PHASE,
           'transport': TRANSPORT, 'pixel_engine': PIXEL_ENGINE,
           'preflight': {}, 'steps': [], 'cleanup': {}}
    RES['run'] = run
    RES['harness_sha16'] = file_pin(os.path.relpath(SELF, W))['sha16'] if SELF.startswith(W) else \
        {'sha16': hashlib.sha256(io.open(SELF, 'rb').read()).hexdigest()[:16].upper(),
         'size': os.path.getsize(SELF)}['sha16']
    RES['pins_start'] = run['pins_before']
    dump()
    log('pins(before): ' + json.dumps({k: v.get('sha16') for k, v in run['pins_before'].items()}, ensure_ascii=False))

    # ---------- 预检 ----------
    pre = run['preflight']
    pre['chrome_exe'] = os.path.exists(CHROME)
    pre['port_free_before'] = (port_listening(PORT) is False)
    pre['chrome_procs_before'] = chrome_count()
    try:
        pre['board_http'] = urllib.request.urlopen(BOARD_URL.split('?')[0], timeout=5).status
    except Exception as e:
        pre['board_http'] = 'ERR %s' % str(e)[:120]
    try:
        pre['board_js_http'] = urllib.request.urlopen(
            'http://127.0.0.1:8765/assets/weapon_skin_sfx_adapter.js', timeout=5).status
    except Exception as e:
        pre['board_js_http'] = 'ERR %s' % str(e)[:120]
    pre['pins_before'] = {k: {'sha16': v.get('sha16'), 'size': v.get('size')} for k, v in run['pins_before'].items()}
    log('preflight: ' + json.dumps(pre, ensure_ascii=False)[:600])
    dump()
    if not pre['chrome_exe']:
        raise RuntimeError('chrome 不存在: %s' % CHROME)
    if pre['port_free_before'] is False:
        raise RuntimeError('端口 %d 已被占用 —— 先清干净再跑' % PORT)

    # ---------- 起 chrome（专用 profile） ----------
    shutil.rmtree(PROFILE, ignore_errors=True)
    proc = subprocess.Popen([CHROME, '--headless=new', '--disable-gpu', '--enable-unsafe-swiftshader',
                             '--no-first-run', '--hide-scrollbars', '--force-device-scale-factor=1',
                             '--force-color-profile=srgb', '--window-size=1600,1000',
                             '--remote-debugging-port=%d' % PORT, '--user-data-dir=%s' % PROFILE,
                             'about:blank'],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    run['chrome_pid'] = proc.pid
    log('chrome 已启动 pid=%d profile=%s port=%d' % (proc.pid, PROFILE, PORT))
    try:
        pg, last = None, None
        for _ in range(40):
            time.sleep(0.75)
            try:
                tl = http_json('http://127.0.0.1:%d/json' % PORT, timeout=3)
                pg = next((t for t in tl if t.get('type') == 'page' and t.get('webSocketDebuggerUrl')), None)
                if pg:
                    break
                last = tl
            except Exception as e:
                last = str(e)[:120]
        if not pg:
            raise RuntimeError('找不到 CDP page target：%s' % str(last)[:200])
        run['target'] = {'url': pg.get('url'), 'id': pg.get('id')}
        RT = Runtime(pg['webSocketDebuggerUrl'])
        C = RT.start()
        C.ev("(function(){var A=window.WikiWeaponViewer;var v=(typeof __wv==='function')?__wv():null;"
             "v=v||(A&&A.__state&&A.__state());var n=0;"
             "if(v&&v.renderer){(function(){var o=v.renderer.render;v.renderer.render=function(){o.apply(this,arguments);"
             "try{this.getContext().flush();}catch(e){}};})();n=1;}return String(n);})()")
        try:
            C.call('Page.enable'); C.call('Runtime.enable'); C.call('Log.enable')
        except Exception as e:
            warn('enable 域失败（忽略）：%s' % str(e)[:160])

        # ---------- 菜单看板 → 打开 1110177 ----------
        run['steps'].append({'name': 'boot', 'navigate': BOARD_URL})
        C.call('Page.navigate', url=BOARD_URL, timeout=90)
        rdy = None
        for i in range(60):
            time.sleep(0.5)
            rdy = C.jv(JS_READY)
            if isinstance(rdy, dict) and rdy.get('rs') == 'complete' and rdy.get('adapter') == 'object' \
                    and rdy.get('hasModels') == 'function':
                break
        run['ready'] = rdy
        log('ready: ' + json.dumps(rdy, ensure_ascii=False)[:400])
        if not isinstance(rdy, dict) or rdy.get('adapter') != 'object':
            raise RuntimeError('适配器未就绪：%s' % str(rdy)[:200])
        if rdy.get('hasModels') != 'function':
            warn('适配器没有 models() —— 本夹具的开关步骤会全部落空，请先确认已重新内联新 adapter')

        opn = C.ev("(async function(id){var s=(window.WEAPON_SKIN_MEDIA||{}).skins||{};"
                   "var rec=s[id];if(!rec)return 'NO_RECORD';"
                   "await window.WikiWeaponViewer.open(rec,{title:'fx061'});return 'opened';})('%s')" % SKIN,
                   timeout=180)
        run['open'] = opn
        log('open(1110177) -> %s' % str(opn)[:120])
        settle = {'applied_ms': None, 'tries': 0}
        t0 = time.time()
        for i in range(40):
            time.sleep(1.5)
            settle['tries'] = i + 1
            s = C.ev("JSON.stringify((window.WikiWeaponViewer.__neox&&window.WikiWeaponViewer.__neox())||null)")
            if isinstance(s, str) and '"applied"' in s:
                settle['applied_ms'] = int((time.time() - t0) * 1000)
                break
        time.sleep(4.0)
        run['settle'] = settle
        run['report_after_open'] = C.jv(JS_REPORT)
        C.ev("String(window.WikiWeaponViewer.__post(false))")
        C.ev("String(window.WikiWeaponViewer.__hidePanels(true))")
        time.sleep(0.8)
        run['report_panel_hidden'] = C.jv(JS_REPORT)
        dump()

        # ---------- ①(S2) 点 .wv-sfx 让适配器 attach ----------
        b0 = C.jv(JS_BTN)
        clk = C.ev("(function(){var b=document.querySelector('.wv-sfx');"
                   "if(!b)return 'NO_BTN';if(b.disabled)return 'BTN_DISABLED';b.click();return 'clicked';})()")
        log('.wv-sfx: before=%s click=%s' % (json.dumps(b0, ensure_ascii=False)[:200], str(clk)[:60]))
        ad, tries_attach = None, 0
        for i in range(80):
            time.sleep(0.25)
            ad = C.jv(JS_ATTACH)
            tries_attach = i + 1
            if isinstance(ad, dict) and ad.get('attached'):
                break
        b1 = C.jv(JS_BTN)
        run['attach'] = {'btn_before': b0, 'click': clk, 'btn_after': b1, 'attach': ad,
                         'tries': tries_attach}
        if not (isinstance(ad, dict) and ad.get('attached')):
            raise RuntimeError('适配器未 attach：%s' % json.dumps(run['attach'], ensure_ascii=False)[:400])
        log('attach ok: %s' % json.dumps(ad, ensure_ascii=False)[:300])
        time.sleep(SETTLE)
        dump()

        # ---------- ②(S3) 默认关 + 零操作两帧 ----------
        C.ev("String(window.WikiWeaponViewer.__sfxTime(%s))" % PHASE)
        time.sleep(0.6)
        render_now(C, 2, PHASE)
        time.sleep(0.4)
        a1 = snap(C, 's03_default_off_attempt1_a', 'attempt1 第1帧（两帧之间零 API 调用）')
        time.sleep(0.8)
        a2 = snap(C, 's03_default_off_attempt1_b', 'attempt1 第2帧（与第1帧同相位，零操作）')
        same1 = a1['stats'].get('sha16') == a2['stats'].get('sha16')
        s3 = {'attempt1': {'a': a1['file'], 'b': a2['file'], 'sha_a': a1['stats'].get('sha16'),
                           'sha_b': a2['stats'].get('sha16'), 'identical': same1, 'phase_hold': False}}
        if not same1:
            # attempt2：每次截图前重放 __sfxTime(PHASE)（唯一的"触碰"，如实标注）
            C.ev("String(window.WikiWeaponViewer.__sfxTime(%s))" % PHASE)
            time.sleep(0.5)
            render_now(C, 2, PHASE)
            b1f = snap(C, 's03_default_off_attempt2_a', 'attempt2 第1帧（截图前重放 __sfxTime）')
            C.ev("String(window.WikiWeaponViewer.__sfxTime(%s))" % PHASE)
            time.sleep(0.5)
            render_now(C, 2, PHASE)
            b2f = snap(C, 's03_default_off_attempt2_b', 'attempt2 第2帧（截图前重放 __sfxTime）')
            s3['attempt2'] = {'a': b1f['file'], 'b': b2f['file'], 'sha_a': b1f['stats'].get('sha16'),
                              'sha_b': b2f['stats'].get('sha16'),
                              'identical': b1f['stats'].get('sha16') == b2f['stats'].get('sha16'),
                              'phase_hold': True}
        s3['default_state'] = show(C, 's03_default_off_diag', '默认态 diag（零开关操作）')['summary']
        s3['modelsOn_is_false'] = (s3['default_state'].get('modelsOn') is False)
        s3['modelsOn_present'] = not (isinstance(s3['default_state'].get('modelsOn'), dict)
                                      and s3['default_state']['modelsOn'].get('__absent__'))
        s3['byte_identical'] = bool(s3['attempt1']['identical'] or (s3.get('attempt2') or {}).get('identical'))
        if not s3['modelsOn_present']:
            warn('适配器未暴露 modelsOn（__sfxDiag/__probe 都没有）—— 默认关只能靠 attempt1 的字节同一性 + modelsForce 佐证')
        elif not s3['modelsOn_is_false']:
            warn('默认态 modelsOn=%s（期望 false）；modelsForce=%s modelsOnAtAttach=%s'
                 % (json.dumps(s3['default_state'].get('modelsOn'), ensure_ascii=False),
                    json.dumps(s3['default_state'].get('modelsForce'), ensure_ascii=False),
                    json.dumps(s3['default_state'].get('modelsOnAtAttach'), ensure_ascii=False)))
        if not s3['attempt1']['identical']:
            warn('attempt1（零操作两帧）不完全逐字节相同 —— 见 attempt2（phase_hold=true）')
        run['steps'].append({'name': 'S3_default_off', 'result': s3})
        log('S3: attempt1 identical=%s | attempt2=%s | modelsOn=%s' % (
            same1, (s3.get('attempt2') or {}).get('identical'),
            json.dumps(s3['default_state'].get('modelsOn'))))
        dump()

        # ---------- ③(S4) models(false) ----------
        r4 = C.jv("(function(){try{return JSON.stringify(window.WikiSfxAdapter.models(false));}"
                  "catch(e){return JSON.stringify({err:String(e&&e.message||e)});}})()")
        log('models(false) -> %s' % json.dumps(r4, ensure_ascii=False)[:200])
        time.sleep(SETTLE)
        C.ev("String(window.WikiWeaponViewer.__sfxTime(%s))" % PHASE)
        time.sleep(0.4)
        render_now(C, 2, PHASE)
        s4 = show(C, 's04_models_false', 'WikiSfxAdapter.models(false)')
        s4['call_ret'] = r4
        s4['expect_visible_0_ok'] = (s4['summary'].get('visible') == 0)
        run['steps'].append({'name': 'S4_models_false', 'result': {'call_ret': r4,
                                                                  'summary': s4['summary'],
                                                                  'visible_0_ok': s4['expect_visible_0_ok']}})
        dump()

        # ---------- ④(S5) models(true) + 轮询 loading ----------
        r5 = C.jv("(function(){try{return JSON.stringify(window.WikiSfxAdapter.models(true));}"
                  "catch(e){return JSON.stringify({err:String(e&&e.message||e)});}})()")
        log('models(true) -> %s' % json.dumps(r5, ensure_ascii=False)[:200])
        poll = {'n': 0, 'elapsed_ms': 0, 'loading_series': [], 'state_series': {}, 'converged': False}
        t0 = time.time()
        while time.time() - t0 < LOAD_POLL_S:
            n = C.ev(JS_LOADING)
            poll['n'] += 1
            poll['loading_series'].append(n if isinstance(n, int) else str(n)[:40])
            if n == 0:
                poll['converged'] = True
                break
            await asyncio.sleep(LOAD_POLL_MS / 1000.0)
        poll['elapsed_ms'] = int((time.time() - t0) * 1000)
        if not poll['converged']:
            warn('models(true) 后 %ss 内仍有 state===\"loading\"（series=%s）' %
                 (LOAD_POLL_S, str(poll['loading_series'][-6:])))
        time.sleep(SETTLE)
        C.ev("String(window.WikiWeaponViewer.__sfxTime(%s))" % PHASE)
        time.sleep(0.4)
        render_now(C, 2, PHASE)
        s5 = show(C, 's05_models_true', 'WikiSfxAdapter.models(true)（已轮询至无 loading）')
        s5['call_ret'] = r5
        s5['poll'] = poll
        s5['page_errors'] = [e for e in C.events if e.get('kind') in ('exceptionDetails', 'log', 'console')]
        s5['exceptionDetails_count'] = sum(1 for e in C.events if e.get('kind') == 'exceptionDetails')
        s5['adapter_loadErrors'] = s5['diag_extra'].get('loadErrors')
        s5['diag_applied_failed_missing'] = s5['diag_extra']
        s5['neox_report'] = C.jv(JS_REPORT)
        run['steps'].append({'name': 'S5_models_true', 'result': {
            'call_ret': r5, 'poll': poll, 'summary': s5['summary'],
            'exceptionDetails_count': s5['exceptionDetails_count'],
            'page_errors': s5['page_errors'][-20:],
            'adapter_loadErrors': s5['adapter_loadErrors'],
            'neox_report': s5['neox_report'],
            'diag_applied_failed_missing': {k: s5['diag_extra'].get(k) for k in
                                            ('modelsLoaded', 'modelsFailed', 'modelsNoMeshField',
                                             'modelNodes', 'modelsForce', 'modelsOn')}}})
        log('S5: visible=%s hasObj=%s states=%s exc=%d' % (
            s5['summary'].get('visible'), s5['summary'].get('hasObj'),
            json.dumps(s5['summary'].get('by_state'), ensure_ascii=False), s5['exceptionDetails_count']))
        dump()

        # ---------- ⑤(S6) modelsHighlight(false) ----------
        m_before = C.jv(JS_MARKS)
        r6 = C.jv("(function(){try{return JSON.stringify({hl:window.WikiSfxAdapter.modelsHighlight(false)});}"
                  "catch(e){return JSON.stringify({err:String(e&&e.message||e)});}})()")
        time.sleep(SETTLE)
        C.ev("String(window.WikiWeaponViewer.__sfxTime(%s))" % PHASE)
        time.sleep(0.4)
        render_now(C, 2, PHASE)
        s6 = show(C, 's06_highlight_false', 'WikiSfxAdapter.modelsHighlight(false)')
        m_after = C.jv(JS_MARKS)
        delta = mark_delta((m_before or {}).get('ev') or [], (m_after or {}).get('ev') or [])
        s6['call_ret'] = r6
        s6['marks_before'] = m_before
        s6['marks_after'] = m_after
        s6['mark_delta'] = delta
        s6['highlight_effect_ok'] = bool(delta['emissiveIntensity_changed'] or delta['highlight_state_changed'])
        if not s6['highlight_effect_ok']:
            warn('modelsHighlight(false) 后 A 类 emissiveIntensity / highlight_state 都没变 '
                 '（marks_before=%s marks_after=%s）' % (json.dumps(m_before, ensure_ascii=False)[:200],
                                                         json.dumps(m_after, ensure_ascii=False)[:200]))
        run['steps'].append({'name': 'S6_highlight_false', 'result': {
            'call_ret': r6, 'summary': s6['summary'], 'mark_delta': delta,
            'highlight_effect_ok': s6['highlight_effect_ok'],
            'by_highlight_state': s6['summary'].get('by_highlight_state')}})
        log('S6: highlight_effect_ok=%s changed_ev=%d changed_hl=%d' % (
            s6['highlight_effect_ok'], len(delta['emissiveIntensity_changed']),
            len(delta['highlight_state_changed'])))
        dump()

        # ---------- ⑥(S7) 负控 modelMaterial('normal') → 复原 ----------
        r7 = C.jv("(function(){try{return JSON.stringify(window.WikiSfxAdapter.modelMaterial('normal'));}"
                  "catch(e){return JSON.stringify({err:String(e&&e.message||e)});}})()")
        log("modelMaterial('normal') -> %s" % json.dumps(r7, ensure_ascii=False)[:200])
        time.sleep(SETTLE)
        C.ev("String(window.WikiWeaponViewer.__sfxTime(%s))" % PHASE)
        time.sleep(0.4)
        render_now(C, 2, PHASE)
        s7 = show(C, 's07_model_material_normal', "负控：modelMaterial('normal')")
        s7['call_ret'] = r7
        rr = C.jv("(function(){var A=window.WikiSfxAdapter;var o={};"
                  "try{o.hl=A.modelsHighlight(true);}catch(e){o.hl='ERR '+e.message;}"
                  "try{o.blend=A.modelMaterial('additive');}catch(e){o.blend='ERR '+e.message;}"
                  "return JSON.stringify(o);})()")
        log("restore additive+highlight(true) -> %s" % json.dumps(rr, ensure_ascii=False)[:200])
        time.sleep(SETTLE)
        C.ev("String(window.WikiWeaponViewer.__sfxTime(%s))" % PHASE)
        time.sleep(0.4)
        render_now(C, 2, PHASE)
        s7b = show(C, 's07b_restored_additive_hl_on', "复原：modelMaterial('additive') + modelsHighlight(true)")
        s7b['call_ret'] = rr
        s7['restore'] = {'call_ret': rr, 'summary': s7b['summary'], 'file': s7b['file'],
                         'stats': s7b['stats']}
        run['steps'].append({'name': 'S7_material_negative_control', 'result': {
            'call_ret': r7, 'summary': s7['summary'], 'by_blending': s7['summary'].get('by_blending'),
            'restore': s7['restore']}})
        dump()

        # ---------- 收尾：事件汇总 ----------
        run['events_all'] = C.events
        run['console_errors'] = [e for e in C.events if e.get('kind') in ('console', 'log')]
        run['exceptionDetails'] = [e for e in C.events if e.get('kind') == 'exceptionDetails']
        run['driver_notes'] = list(C.notes)[:20]
        run['report_end'] = C.jv(JS_REPORT)
        try:
            RT.close()
        except Exception:
            pass
    finally:
        # ---------- 清理（异常路径同样执行） ----------
        cl = run['cleanup']
        cl['chrome_pid'] = proc.pid
        try:
            proc.terminate()
            proc.wait(timeout=10)
        except Exception:
            pass
        kill_tree(proc.pid)
        time.sleep(1.0)
        found = chrome_pids_by_profile(os.path.basename(PROFILE))
        cl['pids_by_profile'] = found
        for pid in found:
            kill_tree(pid)
        if found:
            time.sleep(1.2)
            cl['pids_by_profile_after_kill'] = chrome_pids_by_profile(os.path.basename(PROFILE))
        for i in range(12):
            time.sleep(1.0)
            cnt = chrome_count()
            busy = port_listening(PORT)
            if cnt == 0 and busy is False:
                break
        cl['chrome_count_after'] = chrome_count()
        cl['port_busy_after'] = port_listening(PORT)
        cl['ok'] = (cl['chrome_count_after'] == 0 and cl['port_busy_after'] is False)
        try:
            shutil.rmtree(PROFILE, ignore_errors=True)
        except Exception:
            pass
        log('cleanup: %s' % json.dumps(cl, ensure_ascii=False))
    return run


def step_of(name):
    for st in (RES.get('run') or {}).get('steps') or []:
        if st.get('name') == name:
            return st.get('result') or {}
    return {}


def collect_assertions():
    """把所有门集中成一处，避免"门自己撒谎"：每个门都带 pass 与证据字段。"""
    r3, r4, r5 = step_of('S3_default_off'), step_of('S4_models_false'), step_of('S5_models_true')
    r6, r7 = step_of('S6_highlight_false'), step_of('S7_material_negative_control')
    A = {}
    s3 = r3.get('default_state') or {}
    mo = s3.get('modelsOn')
    present = not (isinstance(mo, dict) and mo.get('__absent__'))
    ident = bool((r3.get('attempt1') or {}).get('identical')
                 or ((r3.get('attempt2') or {}) or {}).get('identical'))
    g3 = bool(ident and present and mo is False)
    A['step3_default_off'] = {'pass': g3, 'byte_identical': ident,
                              'attempt1_identical': (r3.get('attempt1') or {}).get('identical'),
                              'attempt2_identical': (r3.get('attempt2') or {}).get('identical'),
                              'modelsOn': mo, 'modelsOn_present': present,
                              'modelsForce': s3.get('modelsForce'), 'visible': s3.get('visible'),
                              'strict': STRICT_STEP3}
    if STRICT_STEP3 and not g3:
        RES['errors'].append('step3 门未过：byte_identical=%s modelsOn_present=%s modelsOn=%s'
                             % (ident, present, json.dumps(mo, ensure_ascii=False)))
    v4 = (r4.get('summary') or {}).get('visible')
    A['step4'] = {'pass': (v4 == 0), 'visible_after_models_false': v4,
                  'call_ret': json.dumps(r4.get('call_ret'), ensure_ascii=False)[:200],
                  'sha16': r4.get('sha16')}
    v5 = (r5.get('summary') or {}).get('visible')
    A['step5'] = {'pass': bool((r5.get('poll') or {}).get('converged') and (v5 or 0) > 0),
                  'no_loading': (r5.get('poll') or {}).get('converged'),
                  'visible_after_models_true': v5, 'exceptionDetails_count': r5.get('exceptionDetails_count'),
                  'loadErrors': r5.get('adapter_loadErrors'),
                  'by_state': (r5.get('summary') or {}).get('by_state')}
    A['step6'] = {'pass': bool(r6.get('highlight_effect_ok')),
                  'emissiveIntensity_changed': len((r6.get('mark_delta') or {}).get(
                      'emissiveIntensity_changed') or []),
                  'highlight_state_changed': len((r6.get('mark_delta') or {}).get(
                      'highlight_state_changed') or [])}
    bl = (r7.get('by_blending') or {})
    blr = (((r7.get('restore') or {}).get('summary') or {}).get('by_blending') or {})
    A['step7_negative_control'] = {'pass': bool(bl != blr and bl), 'normal_frame_blending': bl,
                                   'restored_blending': blr,
                                   'restore_call': json.dumps(r7.get('restore', {}).get('call_ret'),
                                                              ensure_ascii=False)[:200]}
    A['static'] = {'checked': RES.get('_static_ok'), 'ui_text_io': RES.get('_static_detail'),
                   'note': '自检①控制台/JSON 编码 ②_.wv-sfx_/_SFX_ 字面量能否安全往返；不设硬门（仅作假设登记）'}
    cl = (RES.get('run') or {}).get('cleanup') or {}
    A['cleanup'] = {'pass': bool(cl.get('ok')), 'chrome_count_after': cl.get('chrome_count_after'),
                    'port_busy_after': cl.get('port_busy_after'),
                    'pids_by_profile': cl.get('pids_by_profile')}
    A['pins'] = {'changed': RES.get('pin_diff'), 'differs': bool(RES.get('pin_diff')),
                 'note': '跑前跑后应完全一致（这些开关不写盘）；这里只登记不设硬门'}
    RES['assertions'] = A
    return A


def compact():
    L = []
    w = L.append
    w('== FX029 Model 分支测量 · 皮肤 %s ==' % SKIN)
    w('harness sha16=%s | transport=%s | pixels=%s | out=%s' %
      (RES.get('harness_sha16'), TRANSPORT, PIXEL_ENGINE, OUT))
    ok3 = ((RES.get('assertions') or {}).get('step3_default_off') or {})
    w('门: 默认关(step3)=%s | models(false) 0 可见=%s | 无 loading=%s | highlight 生效=%s | 负控 normal=%s | 清理=%s' % (
        ok3.get('pass'), ((RES.get('assertions') or {}).get('step4') or {}).get('pass'),
        ((RES.get('assertions') or {}).get('step5') or {}).get('pass'),
        ((RES.get('assertions') or {}).get('step6') or {}).get('pass'),
        ((RES.get('assertions') or {}).get('step7_negative_control') or {}).get('pass'),
        ((RES.get('run') or {}).get('cleanup') or {}).get('ok')))
    if not ok3.get('pass'):
        w('  step3 依据: %s' % json.dumps(ok3, ensure_ascii=False)[:400])
    pb, pa = RES.get('pins_start') or {}, RES.get('pins_end') or {}
    for k in sorted(pb):
        w('pin %-26s %s %-10s -> %s %s' % (k, (pb[k] or {}).get('sha16'), (pb[k] or {}).get('size'),
                                           (pa.get(k) or {}).get('sha16'), (pa.get(k) or {}).get('size')))
    d = RES.get('pin_diff') or {}
    w('pin_diff: %s' % (json.dumps(d, ensure_ascii=False) if d else 'OK（跑前跑后一致）'))
    for st in (RES.get('run') or {}).get('steps') or []:
        nm = st.get('name')
        if nm in ('S3_default_off',):
            r = st['result']
            w('%-28s attempt1_identical=%s attempt2=%s modelsOn=%s visible=%s class=%s state=%s' % (
                nm, r['attempt1']['identical'], (r.get('attempt2') or {}).get('identical'),
                json.dumps(r['default_state'].get('modelsOn')), r['default_state'].get('visible'),
                json.dumps(r['default_state'].get('by_class'), ensure_ascii=False),
                json.dumps(r['default_state'].get('by_state'), ensure_ascii=False)))
        elif nm == 'S4_models_false':
            r = st['result']
            w('%-28s visible=%s (expect 0 ok=%s) call=%s' % (
                nm, r['summary'].get('visible'), r['visible_0_ok'],
                json.dumps(r['call_ret'], ensure_ascii=False)[:80]))
        elif nm == 'S5_models_true':
            r = st['result']
            w('%-28s visible=%s hasObj=%s converged=%s(%sms) exc=%s class=%s state=%s' % (
                nm, r['summary'].get('visible'), r['summary'].get('hasObj'),
                r['poll'].get('converged'), r['poll'].get('elapsed_ms'), r['exceptionDetails_count'],
                json.dumps(r['summary'].get('by_class'), ensure_ascii=False),
                json.dumps(r['summary'].get('by_state'), ensure_ascii=False)))
            w('%-28s loadErrors=%s neox=%s' % ('', json.dumps(r.get('adapter_loadErrors'), ensure_ascii=False)[:180],
                                               json.dumps(r.get('neox_report'), ensure_ascii=False)[:160]))
        elif nm == 'S6_highlight_false':
            r = st['result']
            w('%-28s ok=%s changed_ev=%s changed_hl=%s hl_state=%s' % (
                nm, r['highlight_effect_ok'], len(r['mark_delta']['emissiveIntensity_changed']),
                len(r['mark_delta']['highlight_state_changed']),
                json.dumps(r.get('by_highlight_state'), ensure_ascii=False)))
        elif nm == 'S7_material_negative_control':
            r = st['result']
            w('%-28s blending=%s call=%s restore_blend=%s' % (
                nm, json.dumps(r.get('by_blending'), ensure_ascii=False),
                json.dumps(r.get('call_ret'), ensure_ascii=False)[:90],
                json.dumps((r.get('restore') or {}).get('summary', {}).get('by_blending'), ensure_ascii=False)))
    w('-- 逐帧像素统计（全页）--')
    w('%-34s %-16s %9s %11s %11s %9s %9s' % ('tag', 'sha16', 'size', 'white255', 'white±2', 'meanL', 'nonBlack'))
    for f in RES.get('frames') or []:
        s = f['stats']
        w('%-34s %-16s %9s %11s %11s %9s %9s' % (
            f['tag'], s.get('sha16'), s.get('size'),
            ('%.5f' % s['white255_ratio']) if 'white255_ratio' in s else s.get('stat_error', 'ERR')[:11],
            ('%.5f' % s['white_near_ratio']) if 'white_near_ratio' in s else '-',
            ('%.3f' % s['mean_luminance_0_255']) if 'mean_luminance_0_255' in s else '-',
            ('%.4f' % s['nonblack_ratio']) if 'nonblack_ratio' in s else '-'))
    cl = (RES.get('run') or {}).get('cleanup') or {}
    w('cleanup: chrome=%s port_busy=%s ok=%s pids_by_profile=%s' % (
        cl.get('chrome_count_after'), cl.get('port_busy_after'), cl.get('ok'),
        json.dumps(cl.get('pids_by_profile'))))
    w('warnings(%d): %s' % (len(RES.get('warnings') or []), ' ;; '.join((RES.get('warnings') or [])[:6])))
    w('errors(%d): %s' % (len(RES.get('errors') or []), ' ;; '.join((RES.get('errors') or [])[:6])))
    w('-> %s' % JSON_OUT)
    return '\n'.join(L)


def main():
    log('fx061_measure 启动（writer-only harness；transport=%s pixels=%s）' % (TRANSPORT, PIXEL_ENGINE))
    if _np is None and _PILImage is None:
        log('注意：无 numpy ⇒ 走纯 Python 像素统计（较慢）')
    dump()
    try:
        asyncio.run(asyncio.wait_for(go(), 1500))
    except Exception as e:
        import traceback as _tb
        RES['errors'].append('fatal: %s: %s' % (type(e).__name__, str(e)[:400]) + ' || TRACE: ' + _tb.format_exc()[:2000])
        log('FATAL %s: %s' % (type(e).__name__, str(e)[:400]))
    collect_assertions()
    try:
        RES['pins_end'] = pins()
        RES['pin_diff'] = pin_diff(RES.get('pins_start') or {}, RES['pins_end'])
        if RES['pin_diff']:
            warn('跑前跑后 pin 不一致：%s（正常情况下这些开关不写盘，应完全一致）'
                 % json.dumps(RES['pin_diff'], ensure_ascii=False))
    except Exception as e:
        RES['errors'].append('pin_end: %s' % str(e)[:200])
    RES['finished_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
    dump()
    print(compact())
    print('-> %s' % JSON_OUT)
    # 退出码：致命异常 / 门失败 → 非 0（但 JSON 一定已经落盘）
    gates = [v.get('pass') for v in (RES.get('assertions') or {}).values() if isinstance(v, dict) and 'pass' in v]
    if RES.get('errors') or any(g is False for g in gates):
        print('EXIT 2（有致命错误或门未通过；产物已写出）')
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
