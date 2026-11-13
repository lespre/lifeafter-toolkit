# -*- coding: utf-8 -*-
"""CSB 节点树 JSON → 本地可看的 HTML 面板（贴图从 .ktx 解出）。

坐标换算：Cocos 是 y 向上、以锚点定位；网页是 y 向下。
每个节点在父节点坐标系里算 left/top，父高取父节点自身高度（未缩放），
旋转/缩放交给 CSS transform，transform-origin 落在锚点上。

CLI
  csb2html.py <csb 名或路径> [--out 目录]
"""
from __future__ import annotations

import html
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import la_paths  # noqa: E402
from csb2json import parse_csb, ui_dir  # noqa: E402

la_paths.ensure_shared_core_on_path()
from toolkit_core import android_gpk as AG  # noqa: E402

OUT_ROOT = la_paths.find_project_root() / "_ui_preview"
ASSET_DIR = OUT_ROOT / "assets"
FONT_STACK = ('"Noto Sans SC","Source Han Sans SC","Microsoft YaHei",'
              '"PingFang SC",sans-serif')


def tex_key(tex_path: str) -> str:
    """贴图逻辑路径 → 全局唯一的文件名。

    不同贴图目录下会有同名文件（如各活动自己的 btn_nor.png），
    只取 stem 会互相覆盖，这里把目录也编进来。
    """
    norm = tex_path.replace("\\", "/").rsplit(".", 1)[0]
    return re.sub(r"[^0-9A-Za-z_\-]+", "_", norm).strip("_")


def tex_png(tex_path: str, cache: pathlib.Path | None = None) -> str | None:
    """贴图路径（.png 逻辑名）→ 解码后的 png 文件名（位于全局 assets 目录）。"""
    src = ui_dir() / tex_path.replace(".png", ".ktx")
    if not src.exists():
        return None
    cache = cache or ASSET_DIR
    dst = cache / (tex_key(tex_path) + ".png")
    if not dst.exists():
        try:
            import numpy as np
            from PIL import Image
            data = src.read_bytes()
            info = AG.parse_ktx(data)
            rgba = AG._ktx_rgba(data, info)
            if rgba is None:
                return None
            Image.fromarray(np.asarray(rgba, dtype=np.uint8), "RGBA").save(dst)
        except Exception:                                    # noqa: BLE001
            return None
    return dst.name


def rgba(c, alpha=255):
    r, g, b = c[0], c[1], c[2]
    a = c[3] if len(c) > 3 else 255
    return f"rgba({r},{g},{b},{(a * alpha / 255) / 255:.3f})"


def rev(s: str) -> str:
    """CSB 里的文本是倒序存的，显示前还原。"""
    return s[::-1] if s else s


def style_of(n: dict, parent_h: float, cache: pathlib.Path) -> str:
    w, h = n["size"]
    ax, ay = n["anchor"]
    px, py = n["pos"]
    left = px - ax * w
    top = parent_h - (py - ay * h) - h
    css = [
        "position:absolute",
        f"left:{left:.2f}px",
        f"top:{top:.2f}px",
        f"width:{w:.2f}px",
        f"height:{h:.2f}px",
    ]
    alpha = n.get("alpha", 255)
    if alpha < 255:
        css.append(f"opacity:{alpha / 255:.3f}")
    rot = n.get("rot") or [0.0, 0.0]
    sx, sy = n.get("scale") or [1.0, 1.0]
    tf = []
    if rot[1]:
        tf.append(f"rotate({-rot[1]:.2f}deg)")
    if rot[0]:
        tf.append(f"rotateX({rot[0]:.2f}deg)")
    if sx != 1.0 or sy != 1.0:
        tf.append(f"scale({sx:.4f},{sy:.4f})")
    if tf:
        css.append(f"transform-origin:{ax * 100:.2f}% {(1 - ay) * 100:.2f}%")
        css.append("transform:" + " ".join(tf))
    tex = n.get("tex") or n.get("bg")
    if tex:
        png = tex_png(tex, cache)
        if png:
            css.append(f"background-image:url(../assets/{png})")
            css.append("background-size:100% 100%")
            css.append("background-repeat:no-repeat")
    if n["class"] in ("Panel", "ScrollView", "ListView", "PageView"):
        if n.get("colorType") == 1 and n.get("singleColor"):
            css.append("background-color:" + rgba(n["singleColor"],
                                                  n.get("bgAlpha", 255)))
        if n.get("clip"):
            css.append("overflow:hidden")
    if not n.get("visible", True):
        css.append("display:none")
    return ";".join(css)


def render(n: dict, parent_h: float, cache: pathlib.Path, depth=0) -> str:
    w, h = n["size"]
    cls = n["class"]
    label = html.escape(f'{cls} {n.get("name","")}'.strip())
    body = ""
    text = rev(n.get("text") or "")
    if cls in ("Text", "TextBMFont", "TextAtlas") and text:
        color = rgba(n.get("textColor") or n.get("color") or [255, 255, 255, 255],
                     n.get("alpha", 255))
        fs = n.get("fontSize") or 24
        ha = {0: "left", 1: "center", 2: "right"}.get(n.get("hAlign", 0), "left")
        va = {0: "flex-start", 1: "center", 2: "flex-end"}.get(n.get("vAlign", 0),
                                                              "flex-start")
        body = (f'<div style="width:100%;height:100%;display:flex;'
                f'align-items:{va};justify-content:{ha};overflow:visible">'
                f'<span style="font:400 {fs}px/1.15 {FONT_STACK};color:{color};'
                f'white-space:pre;text-align:{ha}">{html.escape(text)}</span></div>')
    elif cls in ("Button", "TextField") and text:
        fs = n.get("fontSize") or 24
        color = rgba(n.get("textColor") or [255, 255, 255, 255])
        body = (f'<div style="position:absolute;inset:0;display:flex;'
                f'align-items:center;justify-content:center">'
                f'<span style="font:400 {fs}px/1.1 {FONT_STACK};color:{color};'
                f'white-space:pre">{html.escape(text)}</span></div>')
    kids = ""
    if n.get("children"):
        kids = "".join(render(c, h, cache, depth + 1) for c in n["children"])
    klass = "n st" if n.get("hiddenByState") else "n"
    extra = ""
    if n.get("hiddenByState"):
        extra = f' data-hidden-by="{html.escape(n["hiddenByState"])}"'
    return (f'<div class="{klass}" data-cls="{html.escape(cls)}" '
            f'data-name="{html.escape(n.get("name",""))}"{extra} '
            f'data-hint="{label}" style="{style_of(n, parent_h, cache)}">'
            f"{body}{kids}</div>")


def build(csb: pathlib.Path, out_dir: pathlib.Path) -> pathlib.Path:
    data = parse_csb(csb)
    cache = ASSET_DIR
    cache.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    root = data["root"]
    rw, rh = root["size"]
    stage = "".join(render(c, rh, cache) for c in root.get("children", []))
    missing = [t for t in data["stats"]["textures"]
               if tex_png(t, cache) is None]
    meta = {
        "csb": data["csb"],
        "version": data["version"],
        "nodes": data["stats"]["nodes"],
        "by_class": data["stats"]["by_class"],
        "textures": len(data["stats"]["textures"]),
        "missing_textures": missing,
        "state_hidden": data["stats"].get("state_hidden", 0),
        "stage": [rw, rh],
    }
    page = TEMPLATE.format(
        font=FONT_STACK,
        title=html.escape(csb.stem),
        w=int(rw), h=int(rh),
        stage=stage,
        nodes=meta["nodes"],
        ntex=meta["textures"],
        nmiss=len(missing),
        nstate=meta["state_hidden"],
        ver=meta["version"],
        classes=html.escape(json.dumps(meta["by_class"], ensure_ascii=False)),
        miss_list=html.escape("\n".join(missing)) or "无",
    )
    out = out_dir / (csb.stem + ".html")
    out.write_text(page, encoding="utf-8")
    (out_dir / (csb.stem + ".meta.json")).write_text(
        json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{csb.name} → {out}")
    print(f"  节点 {meta['nodes']}  贴图 {meta['textures']}  缺 {len(missing)}")
    return out


TEMPLATE = """<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} · 界面还原</title>
<style>
:root {{ color-scheme: dark; }}
* {{ box-sizing: border-box; }}
body {{ margin:0; background:#14161a; color:#e8eaed;
  font:400 13px/1.5 {font}; }}
header {{ display:flex; gap:14px; align-items:center; flex-wrap:wrap;
  padding:10px 16px; background:#1b1e24; border-bottom:1px solid #2a2f37;
  position:sticky; top:0; z-index:9; }}
h1 {{ font-size:14px; font-weight:500; margin:0; }}
.tag {{ padding:2px 8px; border:1px solid #3a414b; border-radius:999px;
  color:#9aa4b2; font-size:12px; }}
button {{ background:#242a33; color:#dfe4ea; border:1px solid #3a414b;
  border-radius:6px; padding:4px 10px; font-size:12px; cursor:pointer; }}
button[aria-pressed="true"] {{ background:#2f6feb; border-color:#2f6feb;
  color:#fff; }}
#wrap {{ padding:16px; overflow:auto; }}
#fit {{ transform-origin:top left; }}
.stage {{ position:relative; background:
  repeating-conic-gradient(#20242b 0% 25%, #191d23 0% 50%) 50%/24px 24px;
  overflow:hidden; }}
.n.outline {{ outline:1px solid rgba(80,160,255,.85); }}
.n.st {{ display:none; }}
#stage.show-states .n.st {{ display:block; }}
body.thumb header, body.thumb footer {{ display:none; }}
body.thumb #wrap {{ padding:0; overflow:hidden; }}
footer {{ padding:10px 16px 40px; color:#8b95a3; font-size:12px; }}
code {{ color:#b9c2cf; }}
</style></head>
<body>
<header>
  <h1>{title}</h1>
  <span class="tag">CSB {ver}</span>
  <span class="tag">{w}×{h}</span>
  <span class="tag">{nodes} 节点</span>
  <span class="tag">贴图 {ntex} · 缺 {nmiss}</span>
  <span class="tag">状态折叠 {nstate}</span>
  <button id="fitBtn" aria-pressed="true">适应宽度</button>
  <button id="boxBtn" aria-pressed="false">显示节点框</button>
  <button id="stateBtn" aria-pressed="false">显示全部按钮状态</button>
</header>
<div id="wrap"><div id="fit"><div class="stage" id="stage"
  style="width:{w}px;height:{h}px">{stage}</div></div></div>
<footer>
  布局/贴图/文案来自 CSB 与还原树，未做人工调整；文字为近似字体（原为位图字体），
  动效与交互不在本页范围。同一控件的常态/按下/禁用贴图默认只显示常态，
  可用「显示全部按钮状态」叠回来。悬停任意区块可看节点名。缺贴图：<code>{miss_list}</code>
</footer>
<script>
const stage = document.getElementById('stage');
const fit = document.getElementById('fit');
const W = {w}, H = {h}, THUMB_W = 420;
const THUMB = new URLSearchParams(location.search).has('thumb');
let scaled = true;
function apply() {{
  if (THUMB) {{
    document.body.classList.add('thumb');
    const k = THUMB_W / W;
    fit.style.transform = 'scale(' + k + ')';
    fit.style.height = (H * k) + 'px';
    return;
  }}
  if (!scaled) {{ fit.style.transform = 'none'; return; }}
  const avail = document.getElementById('wrap').clientWidth - 32;
  const k = Math.min(1, avail / W);
  fit.style.transform = 'scale(' + k + ')';
  fit.style.height = (H * k) + 'px';
}}
document.getElementById('fitBtn').addEventListener('click', e => {{
  scaled = !scaled;
  e.currentTarget.setAttribute('aria-pressed', String(scaled));
  apply();
}});
document.getElementById('boxBtn').addEventListener('click', e => {{
  const on = e.currentTarget.getAttribute('aria-pressed') !== 'true';
  e.currentTarget.setAttribute('aria-pressed', String(on));
  document.querySelectorAll('.n').forEach(n => n.classList.toggle('outline', on));
}});
document.getElementById('stateBtn').addEventListener('click', e => {{
  const on = e.currentTarget.getAttribute('aria-pressed') !== 'true';
  e.currentTarget.setAttribute('aria-pressed', String(on));
  stage.classList.toggle('show-states', on);
}});
stage.addEventListener('mouseover', e => {{
  const n = e.target.closest('.n');
  stage.title = n ? (n.dataset.hint || '') : '';
}});
addEventListener('resize', apply);
apply();
</script>
</body></html>
"""


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    raw = args[0]
    p = pathlib.Path(raw)
    if not p.exists():
        p = ui_dir() / (raw if raw.endswith(".csb") else raw + ".csb")
    if not p.exists():
        print("找不到", raw)
        return 2
    out_dir = OUT_ROOT / p.stem
    build(p, out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
