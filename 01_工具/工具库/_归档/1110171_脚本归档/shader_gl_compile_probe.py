# -*- coding: utf-8 -*-
"""shader_gl_compile_probe.py — task-3 只读取证：在 lab=1 页面实测 three.js r180 链材质的
WebGL 编译/链接状态、最终 GLSL 源码（含 three 前缀与已解析 include）、以及 console 日志。

只读：不修改项目内任何既有文件；输出仅写本目录（_target_1110171），文件名前缀 shader_。

手段：Page.addScriptToEvaluateOnNewDocument 在页面任何脚本之前 hook
      WebGL2RenderingContext.prototype.{shaderSource,compileShader,getShaderParameter,
      getShaderInfoLog,attachShader,linkProgram,getProgramParameter,getProgramInfoLog,useProgram}
      → 等价于 renderer.debug.onShaderError 的可观测替代（无需拿到 renderer 对象）。
"""
import asyncio, json, os, shutil, subprocess, urllib.request, base64, hashlib, sys
import websockets

CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
URL = ('http://127.0.0.1:8765/board.html?b=weapon_skin_sfx_text_sources'
       '&view=wiki&sort=id&dir=desc&lab=1')
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
PORT = 9971
REL = 'assets/3d/weapon_skin/1110171'

HOOK = r"""
(function(){
  window.__SH = {sources:[], fails:[], linkFails:[], useInvalid:0, logs:[], exceptions:[]};
  var back = window.console;
  ['error','warn','log'].forEach(function(k){
    var o = back[k] ? back[k].bind(back) : function(){};
    back[k] = function(){
      try{ window.__SH.logs.push(k + '|' + String([].slice.call(arguments).join(' ')).slice(0,3000)); }catch(e){}
      return o.apply(null, arguments);
    };
  });
  window.addEventListener('error', function(e){ try{ window.__SH.exceptions.push('onerror: '+String(e.message).slice(0,400)); }catch(_){} });
  window.addEventListener('unhandledrejection', function(e){ try{ window.__SH.exceptions.push('rej: '+String((e.reason&&e.reason.message)||e.reason).slice(0,400)); }catch(_){} });
  var P = (window.WebGL2RenderingContext||{}).prototype;
  if(!P){ window.__SH.note='no WebGL2RenderingContext'; return; }
  var _ss=P.shaderSource, _cs=P.compileShader, _gs=P.getShaderParameter, _gsil=P.getShaderInfoLog,
      _att=P.attachShader, _lp=P.linkProgram, _gpa=P.getProgramParameter, _gpil=P.getProgramInfoLog,
      _up=P.useProgram;
  var sSrc = new WeakMap(), pSh = new WeakMap(), pOk = new WeakMap(), nSeen = {sh:0, pr:0};
  P.shaderSource = function(sh, src){
    try{ sSrc.set(sh, String(src)); }catch(e){}
    return _ss.apply(this, arguments);
  };
  P.compileShader = function(sh){
    var r = _cs.apply(this, arguments);
    try{
      var ok = !!_gs.call(this, sh, this.COMPILE_STATUS);
      var log = '';
      try{ log = _gsil.call(this, sh) || ''; }catch(e){}
      var src = '';
      try{ src = sSrc.get(sh) || ''; }catch(e){}
      window.__SH.sources.push({n: ++nSeen.sh, len: src.length, ok: ok,
        tail: src.slice(-1800), has_ver300: src.indexOf('#version 300 es') === 0});
      if(window.__SH.sources.length > 30) window.__SH.sources.shift();
      if(!ok){
        window.__SH.fails.push({kind:'compile', log:String(log).slice(0,4000)});
      }
    }catch(e){ window.__SH.fails.push({kind:'probe_exc', msg:String(e&&e.message||e)}); }
    return r;
  };
  P.attachShader = function(pr, sh){
    try{ var a = pSh.get(pr) || []; a.push(sh); pSh.set(pr, a); }catch(e){}
    return _att.apply(this, arguments);
  };
  P.linkProgram = function(pr){
    var r = _lp.apply(this, arguments);
    try{
      var ok = !!_gpa.call(this, pr, this.LINK_STATUS);
      pOk.set(pr, ok);
      if(!ok){
        var shs = [];
        try{ shs = (pSh.get(pr) || []).map(function(sh){ try{ return String(_gsil.call(this, sh) || ''); }catch(e){ return ''; } }, this); }catch(e){}
        var plog = ''; try{ plog = _gpil.call(this, pr) || ''; }catch(e){}
        window.__SH.linkFails.push({n: ++nSeen.pr, prog:String(plog).slice(0,2000),
          shaders: shs.map(function(s){ return String(s).slice(0,4000); })});
      }
    }catch(e){ window.__SH.linkFails.push({kind:'link_probe_exc', msg:String(e&&e.message||e)}); }
    return r;
  };
  P.useProgram = function(pr){
    try{ if(pOk.has(pr) && pOk.get(pr) === false) window.__SH.useInvalid++; }catch(e){}
    return _up.apply(this, arguments);
  };
  window.__SH.len = function(){
    return {sources: window.__SH.sources.length, fails: window.__SH.fails.length,
            linkFails: window.__SH.linkFails.length, useInvalid: window.__SH.useInvalid,
            logs: window.__SH.logs.length};
  };
  window.__SH.get = function(){
    return {note: window.__SH.note || null, len: window.__SH.len(),
            fails: window.__SH.fails, linkFails: window.__SH.linkFails,
            useInvalid: window.__SH.useInvalid,
            exceptions: window.__SH.exceptions,
            logs: window.__SH.logs.slice(-60),
            sources: window.__SH.sources};
  };
})();
"""


async def main():
    prof = os.path.join(OUT, '_profSHADER')
    shutil.rmtree(prof, ignore_errors=True)
    p = subprocess.Popen([CHROME, '--headless=new', '--disable-gpu', '--enable-unsafe-swiftshader',
                          '--no-first-run', '--hide-scrollbars', '--force-device-scale-factor=1',
                          '--window-size=1240,900', '--remote-debugging-port=%d' % PORT,
                          '--user-data-dir=%s' % prof, 'about:blank'],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(4)
    report = {}
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
                for _ in range(600):
                    if i in pending:
                        return pending.pop(i).get('result', {})
                    await asyncio.sleep(0.02)
                return {}

            async def ev(expr):
                r = await send('Runtime.evaluate', expression=expr, returnByValue=True, awaitPromise=True)
                if r.get('exceptionDetails'):
                    return 'EXC ' + str(r['exceptionDetails'].get('text'))[:300]
                return (r.get('result', {}) or {}).get('value')

            await send('Page.enable')
            await send('Runtime.enable')
            await send('Log.enable')
            add = await send('Page.addScriptToEvaluateOnNewDocument', source=HOOK)
            print('hook id:', add.get('identifier'))
            await send('Page.navigate', url=URL)
            await asyncio.sleep(10)
            print('hook alive:', await ev("JSON.stringify(window.__SH?window.__SH.len():null)"))

            # 打开 1110171 的 3D viewer（与既有诊断脚本相同路径）
            await ev("(()=>{window.WikiWeaponViewer.open({skin_id:'1110171',poster:'%s/poster.webp',"
                     "preview_3d:{status:'ready',manifest:'%s/viewer.json'}},{title:'x'});return 1;})()"
                     % (REL, REL))
            neox = None
            for _ in range(45):
                neox = await ev("JSON.stringify(window.WikiWeaponViewer.__neox&&window.WikiWeaponViewer.__neox())")
                if neox and 'applied' in str(neox):
                    break
                await asyncio.sleep(2)
            await asyncio.sleep(8)
            report['url'] = URL
            report['neox'] = neox
            report['gl_len_after_chain'] = await ev("JSON.stringify(window.__SH.len())")

            # three 侧 program 诊断（走 viewer 内部 state.renderer）
            cp = await ev("JSON.stringify(window.WikiWeaponViewer.__ladderCompile&&window.WikiWeaponViewer.__ladderCompile())")
            report['ladderCompile'] = cp

            # 链材质的最终（注入后、未加 three 前缀的）fragmentShader
            frag = await ev("""JSON.stringify((()=>{
              const out=[];
              const r=window.WikiWeaponViewer;
              try{
                const st=r.neoxState();
                // 通过 __ladderL1 之外的路径拿不到 state；用 __srcChain/__iblDiag 之外暴露的 __l0Info
              }catch(e){}
              return out;})())""")
            # 直接抓 GL 侧源码（含 three 前缀 + include 已解析）
            report['gl'] = await ev("JSON.stringify(window.__SH.get())")

            snap = await ev("JSON.stringify(window.WikiWeaponViewer.snapshot&&window.WikiWeaponViewer.snapshot())")
            try:
                s = json.loads(snap or '{}')
            except Exception:
                s = {}
            report['snapshot'] = {k: s.get(k) for k in ('w', 'h', 'mean', 'magenta_pct', 'gray_pct', 'error')}
            if s.get('png'):
                raw = base64.b64decode(s['png'].split(',', 1)[-1])
                open(os.path.join(OUT, 'shader_lab_chain_frame.png'), 'wb').write(raw)
                report['snapshot']['png_sha16'] = hashlib.sha256(raw).hexdigest()[:16]

            # 用 __ladderL1 做一个锚点有效性对照：同一个 #include <dithering_fragment> 锚点，
            # MeshBasicMaterial + 简单注入是否真的生效（红/绿体）
            for mode in ('red', 'green'):
                r = await ev("JSON.stringify(window.WikiWeaponViewer.__ladderL1&&window.WikiWeaponViewer.__ladderL1({mode:'%s'}))" % mode)
                await asyncio.sleep(2)
                s2 = await ev("JSON.stringify(window.WikiWeaponViewer.snapshot())")
                try:
                    d2 = json.loads(s2 or '{}')
                except Exception:
                    d2 = {}
                report['ladderL1_' + mode] = {'res': str(r)[:600],
                                              'mean': d2.get('mean'),
                                              'sha16': hashlib.sha256(base64.b64decode(d2['png'].split(',', 1)[-1])).hexdigest()[:16] if d2.get('png') else None}
                if d2.get('png'):
                    open(os.path.join(OUT, 'shader_ladderL1_%s.png' % mode), 'wb').write(
                        base64.b64decode(d2['png'].split(',', 1)[-1]))
            # 还原
            await ev("JSON.stringify(window.WikiWeaponViewer.__ladderL1({mode:'off'}))")
            report['gl_after_ladder'] = await ev("JSON.stringify(window.__SH.len())")
            task.cancel()
    finally:
        try:
            p.terminate()
        except Exception:
            pass
    with open(os.path.join(OUT, 'shader_gl_compile_probe.json'), 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=1)
    print(json.dumps(report, ensure_ascii=False, indent=1)[:12000])


asyncio.run(main())
