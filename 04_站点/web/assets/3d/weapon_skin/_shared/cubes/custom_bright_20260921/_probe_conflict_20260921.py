# -*- coding: utf-8 -*-
"""_probe_conflict_20260921.py —— 并发冲突下**实际渲染的是哪套 cube**（只读）。

背景：另一路代理（SNOWCUBE）在 12:26:50 改了 viewer.js / viewer.json / board.html / cubes_custom.js，
把 `viewer.json.cube_default_selection.cube` 指向 `custom_bright_snow_20260921`，并给 viewer.js 加了
`cube_default_selection` 消费器 + `product_default*` 探针字段。
我这边的机制是改 `neox_material.json` 的 t_custom_ibl（仍指向 custom_bright_20260921）。
⇒ 两个产品档声明同时存在。本探针只回答：**引擎实际绑的是哪一套**。

判据（按证据强度从强到弱）：
  ① `__acceptanceReport()` 的逐 mesh `ibl_faces`（面文件名 ⇒ 直接看到实绑 cube 的六面）；
  ② `__cubeDirProbe` 里哪些 iblName 被装载过、其 urls 指向哪；
  ③ `__cubePickerState()` 的 product_default* / product_default_applied。
"""
import asyncio
import base64
import hashlib
import json
import os
import subprocess
import sys
import urllib.request

import websockets

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = r'E:\la拆包项目\03_执行\\30_分析\_target_1110025'
sys.path.insert(0, TARGET)
from accept_1110025 import CDP, CHROME_CANDS, URL          # noqa: E402


async def main(port):
    chrome = next((c for c in CHROME_CANDS if os.path.exists(c)), None)
    pr = subprocess.Popen([chrome, '--headless=new', '--disable-gpu', '--enable-unsafe-swiftshader',
                           '--no-first-run', '--hide-scrollbars', '--window-size=1240,900',
                           '--remote-debugging-port=%d' % port,
                           '--user-data-dir=%s' % os.path.join(os.environ.get('TEMP', '.'), 'cf_%d' % port),
                           'about:blank'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(5)
    rep = {}
    try:
        pg = next(t for t in json.load(urllib.request.urlopen('http://127.0.0.1:%d/json' % port))
                  if t.get('type') == 'page')
        async with websockets.connect(pg['webSocketDebuggerUrl'], max_size=256 << 20) as ws:
            c = CDP(ws)
            await c.send('Page.enable')
            await c.send('Runtime.enable')
            await c.send('Page.navigate', url=URL)
            await asyncio.sleep(10)
            await c.ev("(()=>{window.WikiWeaponViewer.open({skin_id:'1110025',preview_3d:{status:'ready',"
                       "manifest:'assets/3d/weapon_skin/1110025/viewer.json'}},{title:'冰蕊银华'});return 1;})()")
            for _ in range(40):
                st = await c.ev("JSON.stringify((window.WikiWeaponViewer.__neox&&window.WikiWeaponViewer.__neox())||null)")
                if st and st not in ('null', 'undefined'):
                    break
                await asyncio.sleep(1)
            await asyncio.sleep(8)
            # ① 实绑六面（最强证据）
            rep['acceptance_ibl'] = await c.ev(
                "(function(){try{var r=window.__acceptanceReport();"
                "return JSON.stringify((r.meshes||[]).map(function(m){return {mesh:m.mesh,"
                "env_mode:m.env_mode,ibl_faces:m.ibl_faces,ibl_faces_count:m.ibl_faces_count};}));}"
                "catch(e){return 'ERR '+e.message;}})()")
            # ② 装载过的 cube
            rep['cubeDirProbe'] = await c.ev("JSON.stringify(window.__cubeDirProbe||null)")
            # ③ 产品档探针
            rep['picker'] = await c.ev("String(window.WikiWeaponViewer.__cubePickerState())")
            rep['product_default'] = await c.ev(
                "(function(){try{return (typeof window.WikiWeaponViewer.__cubeProductDefault==='function')"
                "?String(window.WikiWeaponViewer.__cubeProductDefault()):'NO_API';}catch(e){return 'ERR '+e.message;}})()")
            rep['config_cds'] = await c.ev(
                "(function(){try{var s=window.WikiWeaponViewer.__state?window.WikiWeaponViewer.__state():null;"
                "return JSON.stringify(s&&s.config?s.config.cube_default_selection:null);}catch(e){return 'ERR '+e.message;}})()")
            s = await c.send('Page.captureScreenshot', format='png')
            raw = base64.b64decode(s['data'])
            rep['shot_sha16'] = hashlib.sha256(raw).hexdigest()[:16]
    finally:
        try:
            pr.terminate()
        except Exception:
            pass
    print(json.dumps(rep, ensure_ascii=False, indent=1))
    json.dump(rep, open(os.path.join(HERE, '_conflict_state_20260921.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    return 0


if __name__ == '__main__':
    sys.exit(asyncio.run(main(int(sys.argv[1]) if len(sys.argv) > 1 else 10479)))
