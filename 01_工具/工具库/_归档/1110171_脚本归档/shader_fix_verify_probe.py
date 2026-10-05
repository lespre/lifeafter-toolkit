# -*- coding: utf-8 -*-
"""shader_fix_verify_probe.py — task-3 修复充分性验证（只读，不改项目文件）。

拿页面里实际编译失败的那份片元着色器源码（GL 侧 shaderSource 原样捕获，含 three 前缀），
在页面内新建一个独立 WebGL2 context，做三组编译 A/B：

  arm1 原样                      -> 预期 FAIL（复现）
  arm2 仅把 __xxx 标识符改名      -> 预期 FAIL 且报 'uIblStrength' : undeclared identifier
                                   （证明 uIblStrength 是独立的第二个致命错误）
  arm3 改名 + 补 uniform 声明     -> 预期 PASS（证明这两处修完即可编译）

输出仅写本目录，文件名前缀 shader_。
"""
import asyncio, json, os, shutil, subprocess, urllib.request
import websockets

CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
URL = ('http://127.0.0.1:8765/board.html?b=weapon_skin_sfx_text_sources'
       '&view=wiki&sort=id&dir=desc&lab=1')
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
PORT = 9975
REL = 'assets/3d/weapon_skin/1110171'

HOOK = r"""
(function(){
  window.__SH={fullSrc:[]};
  var P=(window.WebGL2RenderingContext||{}).prototype;
  if(!P) return;
  var _ss=P.shaderSource,_cs=P.compileShader,_gs=P.getShaderParameter,_gsil=P.getShaderInfoLog;
  var sSrc=new WeakMap();
  P.shaderSource=function(sh,src){ try{ sSrc.set(sh,String(src)); }catch(e){} return _ss.apply(this,arguments); };
  P.compileShader=function(sh){
    var r=_cs.apply(this,arguments);
    try{
      var ok=!!_gs.call(this,sh,this.COMPILE_STATUS);
      var src=sSrc.get(sh)||'';
      if(!ok && window.__SH.fullSrc.length<4 && src.indexOf('uCustomIbl')>=0) window.__SH.fullSrc.push(src);
    }catch(e){}
    return r;
  };
  window.__ARMTEST=function(idx){
    var src=(window.__SH.fullSrc||[])[idx||0];
    if(!src) return {error:'no captured source'};
    var cv=document.createElement('canvas'); cv.width=cv.height=8;
    var gl=cv.getContext('webgl2');
    if(!gl) return {error:'no webgl2'};
    function compile(code){
      var sh=gl.createShader(gl.FRAGMENT_SHADER);
      gl.shaderSource(sh,code); gl.compileShader(sh);
      var ok=!!gl.getShaderParameter(sh,gl.COMPILE_STATUS);
      var log=String(gl.getShaderInfoLog(sh)||'');
      gl.deleteShader(sh);
      return {ok:ok, log:log.slice(0,1500),
              errcount:(log.match(/ERROR:/g)||[]).length};
    }
    var renamed=src.replace(/\b__(rough|lod|Rr|R|c|s2|sm|Lc|L|env)\b/g,'q_$1');
    var arm2=compile(renamed);
    var arm3code=renamed.replace('uniform float uIblScale;','uniform float uIblScale;\nuniform float uIblStrength;');
    var arm3=compile(arm3code);
    return {src_len:src.length,
            arm1_asis:compile(src),
            arm2_renamed_only:arm2,
            arm3_renamed_plus_decl:arm3,
            arm3_decl_inserted:arm3code!==renamed,
            arm2_still_mentions_uIblStrength: /uIblStrength'\s*:\s*undeclared/.test(arm2.log)};
  };
})();
"""


async def main():
    prof = os.path.join(OUT, '_profSHADERFIX')
    shutil.rmtree(prof, ignore_errors=True)
    p = subprocess.Popen([CHROME, '--headless=new', '--disable-gpu', '--enable-unsafe-swiftshader',
                          '--no-first-run', '--hide-scrollbars', '--force-device-scale-factor=1',
                          '--window-size=1240,900', '--remote-debugging-port=%d' % PORT,
                          '--user-data-dir=%s' % prof, 'about:blank'],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(4)
    rep = {}
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
                    return 'EXC ' + str(r['exceptionDetails'].get('text'))[:400]
                return (r.get('result', {}) or {}).get('value')

            await send('Page.enable')
            await send('Runtime.enable')
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
            rep['captured_failing_sources'] = await ev("String((window.__SH.fullSrc||[]).length)")
            rep['arms'] = await ev("JSON.stringify(window.__ARMTEST(0))")
            task.cancel()
    finally:
        try:
            p.terminate()
        except Exception:
            pass
    with open(os.path.join(OUT, 'shader_fix_verify.json'), 'w', encoding='utf-8') as f:
        json.dump(rep, f, ensure_ascii=False, indent=1)

    arms = json.loads(rep.get('arms') or '{}')
    print('neox_applied =', rep.get('neox_applied'), '| captured sources =', rep.get('captured_failing_sources'))
    print('src_len =', arms.get('src_len'), '| decl_inserted =', arms.get('arm3_decl_inserted'))
    for k in ('arm1_asis', 'arm2_renamed_only', 'arm3_renamed_plus_decl'):
        a = arms.get(k) or {}
        print('\n[%s] ok=%s  ERROR 数=%s' % (k, a.get('ok'), a.get('errcount')))
        print('  ', (a.get('log') or '').replace('\n', '\n   ')[:1100])
    print('\narm2 仍报 uIblStrength undeclared:', arms.get('arm2_still_mentions_uIblStrength'))


asyncio.run(main())
