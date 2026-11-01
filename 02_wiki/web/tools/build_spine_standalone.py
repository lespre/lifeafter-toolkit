# -*- coding: utf-8 -*-
"""把 spine_play 播放页压成零依赖单文件 HTML（只含「头像」那 49 套）。

原理：AssetManager 自带 setRawDataURI(url, dataURI)，downloadText/downloadBinary 会优先取它，
     所以素材全部 base64 内嵌后，正常 load 也能在 file:// 下跑。
three 不涉及；spine 的 runtime 是 UMD 全局脚本，用 data:text/javascript 的 <script src> 加载。
"""
import json, base64, pathlib, collections

WEB = pathlib.Path(r"E:/la拆包项目/02_wiki/web")
SRC = WEB / "spine_play"
OUT_DIR = pathlib.Path(r"E:/la拆包项目/01_索引与产物/交付/spine播放页_头像")
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT = OUT_DIR / "双击这个就能看.html"

GROUP = "touxiang"
html = (SRC / "index.html").read_text(encoding="utf-8")
lst = json.loads((SRC / "list.json").read_text(encoding="utf-8"))

items = [it for it in lst["items"] if it["group"] == GROUP]
print("内嵌套数:", len(items))

assets = {}
total = 0
for it in items:
    for key in ("json", "atlas", "png"):
        rel = it[key]
        p = (SRC / rel).resolve()
        if not p.is_file():
            print("  缺:", rel); continue
        b = p.read_bytes()
        total += len(b)
        mime = "image/png" if p.suffix.lower() == ".png" else "text/plain"
        assets[rel] = "data:%s;base64,%s" % (mime, base64.b64encode(b).decode())
print("素材 %.1f MB" % (total / 1e6))

# runtime：UMD 脚本 → data URL
rt = {}
for f in ("spine-core-3.8.js", "spine-webgl-3.8.js"):
    b = (SRC / "runtime" / f).read_bytes()
    rt[f] = "data:text/javascript;base64," + base64.b64encode(b).decode()

# 1) 换 runtime 引用
html = html.replace('<script src="./runtime/spine-core-3.8.js"></script>',
                    '<script src="%s"></script>' % rt["spine-core-3.8.js"], 1)
html = html.replace('<script src="./runtime/spine-webgl-3.8.js"></script>',
                    '<script src="%s"></script>' % rt["spine-webgl-3.8.js"], 1)

# 2) 内嵌清单 + 素材注入（在资产管理器创建之后注册）
inject = ("<script>\nwindow.__LIST=" + json.dumps({"count": len(items), "items": items}, ensure_ascii=False) + ";\n"
          "window.__ASSETS=" + json.dumps(assets) + ";\n</script>\n")
html = html.replace("<script>\nconst $ = id => document.getElementById(id);", inject +
                    "<script>\nconst $ = id => document.getElementById(id);", 1)

# 3) 用内嵌清单代替 fetch
old_fetch = "fetch('./list.json').then(r => r.json()).then(buildList).catch(e => fail('读不到 list.json：' + e));"
assert old_fetch in html
html = html.replace(old_fetch, "buildList(window.__LIST);", 1)

# 4) 创建 AssetManager 后注册 raw data URI
old_am = "  assetManager = new spine.webgl.AssetManager(gl);"
assert old_am in html
html = html.replace(old_am, old_am +
    "\n  try { for (const k in window.__ASSETS) assetManager.setRawDataURI(k, window.__ASSETS[k]); }"
    "\n  catch (e) { window.__rawUriErr = String(e); }", 1)

# 5) 标题标注
html = html.replace("<title>Spine 动画播放 · 明日之后</title>",
                    "<title>Spine 头像动画（单文件版）· 明日之后</title>", 1)

OUT.write_text(html, encoding="utf-8")
print("写出:", OUT, "%.1f MB" % (OUT.stat().st_size / 1e6))
