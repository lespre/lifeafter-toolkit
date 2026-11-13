# -*- coding: utf-8 -*-
"""CSB（Cocos Studio 2.x / CSParseBinary flatbuffers）→ 节点树 JSON。

用途：把活动面板的**原始布局**（位置/尺寸/锚点/旋转/缩放/颜色/贴图/文案）
解成结构化 JSON，供本地预览页渲染。只读还原树，不写回、不改动任何产物。

格式依据：cocos2d-x CSLoader 同源的 CSParseBinary schema（version 2.1.0.0）。
读取方式为手写 flatbuffer vtable 解析，无第三方依赖。

CLI
  csb2json.py <csb 路径>              # 单面板，打印摘要 + 写同名 .json
  csb2json.py --all [--limit N]       # 全量扫 资源/ui/*.csb，出覆盖率报告
  csb2json.py <csb 路径> --stdout     # 只打印，不落盘
"""
from __future__ import annotations

import json
import pathlib
import struct
import sys
from collections import Counter

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import la_paths  # noqa: E402

OUT_DIR = HERE / "panel_json"


def restored_root() -> pathlib.Path:
    """PE 还原树根（数据源铁律：只用还原树，不扫线上 npk）。"""
    import os
    env = os.environ.get("LA_RESTORE_ROOT")
    if env:
        return pathlib.Path(env)
    return la_paths.find_project_root() / "01_索引与产物" / "41_还原树" / "pe"


def ui_dir() -> pathlib.Path:
    return restored_root() / "资源" / "ui"

# ---------------------------------------------------------------- flatbuffers


class FB:
    """极简 flatbuffers 读取器：只实现 table / struct / string / vector。"""

    __slots__ = ("b",)

    def __init__(self, buf: bytes):
        self.b = buf

    def u8(self, p): return self.b[p]
    def u16(self, p): return struct.unpack_from("<H", self.b, p)[0]
    def u32(self, p): return struct.unpack_from("<I", self.b, p)[0]
    def i32(self, p): return struct.unpack_from("<i", self.b, p)[0]
    def f32(self, p): return struct.unpack_from("<f", self.b, p)[0]

    def root(self) -> int:
        return self.u32(0)

    def field(self, t: int, idx: int) -> int:
        """返回字段绝对偏移，字段缺省返回 0。"""
        if not t:
            return 0
        vt = t - self.i32(t)
        vsize = self.u16(vt)
        pos = 4 + idx * 2
        if pos >= vsize:
            return 0
        off = self.u16(vt + pos)
        return t + off if off else 0

    def string(self, p: int):
        if not p:
            return None
        s = p + self.u32(p)
        n = self.u32(s)
        return self.b[s + 4:s + 4 + n].decode("utf-8", "replace")

    def table(self, p: int) -> int:
        return p + self.u32(p) if p else 0

    def vector(self, p: int):
        if not p:
            return 0, 0
        v = p + self.u32(p)
        return v + 4, self.u32(v)

    def vec_tables(self, p: int) -> list[int]:
        start, n = self.vector(p)
        return [self.table(start + 4 * i) for i in range(n)]

    def vec_strings(self, p: int) -> list[str]:
        start, n = self.vector(p)
        return [self.string(start + 4 * i) for i in range(n)]

    # ---- 便捷取标量（带默认值）
    def s_str(self, t, i, default=""):
        return self.string(self.field(t, i)) or default

    def s_int(self, t, i, default=0):
        p = self.field(t, i)
        return self.i32(p) if p else default

    def s_float(self, t, i, default=0.0):
        p = self.field(t, i)
        return self.f32(p) if p else default

    def s_bool(self, t, i, default=False):
        p = self.field(t, i)
        return bool(self.u8(p)) if p else default

    def s_ubyte(self, t, i, default=0):
        p = self.field(t, i)
        return self.u8(p) if p else default

    def s_vec2(self, t, i, default=(0.0, 0.0)):
        p = self.field(t, i)
        if not p:
            return list(default)
        return [self.f32(p), self.f32(p + 4)]

    def s_color(self, t, i, default=(255, 255, 255, 255)):
        p = self.field(t, i)
        if not p:
            return list(default)
        a, r, g, b = self.b[p], self.b[p + 1], self.b[p + 2], self.b[p + 3]
        return [r, g, b, a]

    def s_table(self, t, i) -> int:
        return self.table(self.field(t, i))


# ---------------------------------------------------------------- 选项表

# 每个 classname 对应的 options 表结构：字段名 → (类型, 下标)
# 只描述渲染需要的字段；其余字段忽略但不影响结构（vtable 按位寻址）。
COMMON = {
    "name": ("str", 0),
    "actionTag": ("int", 1),
    "rot": ("vec2", 2),
    "z": ("int", 3),
    "visible": ("bool_true", 4),
    "alpha": ("ubyte", 5),
    "tag": ("int", 6),
    "pos": ("vec2", 7),
    "scale": ("vec2", 8),
    "anchor": ("vec2", 9),
    "color": ("color", 10),
    "size": ("vec2", 11),
    "flipX": ("ubyte", 12),
    "flipY": ("ubyte", 13),
}

# widgetOptions 一律在 options 表的 0 号字段
SPEC = {
    "ImageView": {"tex": ("res", 1), "scale9": ("bool", 4),
                  "cap": ("quad", 2), "scale9size": ("vec2", 3)},
    "Sprite": {"tex": ("res", 1)},
    "Button": {"tex": ("res", 1), "texDown": ("res", 2), "texDis": ("res", 3),
               "text": ("str", 5), "font": ("str", 6), "fontSize": ("int", 7),
               "textColor": ("color", 8)},
    "Text": {"text": ("str", 4), "font": ("str", 2), "fontSize": ("int", 3),
             "areaW": ("int", 5), "areaH": ("int", 6),
             "hAlign": ("int", 7), "vAlign": ("int", 8),
             "custom": ("bool", 10), "textColor": ("color", None)},
    "TextBMFont": {"tex": ("res", 1), "text": ("str", 2)},
    "TextAtlas": {"tex": ("res", 1), "text": ("str", 2)},
    "TextField": {"text": ("str", 4), "placeholder": ("str", 5),
                  "font": ("str", 2), "fontSize": ("int", 3)},
    "Panel": {"bg": ("res", 1), "clip": ("bool", 2), "colorType": ("int", 6),
              "bgAlpha": ("ubyte", 7), "singleColor": ("color", 3)},
    "ScrollView": {"bg": ("res", 1), "clip": ("bool", 2), "colorType": ("int", 6),
                   "bgAlpha": ("ubyte", 7), "singleColor": ("color", 3),
                   "inner": ("vec2", 12), "dir": ("int", 13)},
    "ListView": {"bg": ("res", 1), "clip": ("bool", 2), "colorType": ("int", 6),
                 "bgAlpha": ("ubyte", 7), "singleColor": ("color", 3),
                 "inner": ("vec2", 12), "margin": ("int", 15)},
    "PageView": {"bg": ("res", 1), "clip": ("bool", 2), "colorType": ("int", 6),
                 "bgAlpha": ("ubyte", 7), "singleColor": ("color", 3)},
    "CheckBox": {"tex": ("res", 1), "checked": ("bool", 6)},
    "LoadingBar": {"tex": ("res", 1), "percent": ("int", 2), "dir": ("int", 3)},
    "Slider": {"tex": ("res", 1), "ball": ("res", 2), "percent": ("int", 6)},
    "ParticleSystem": {"tex": ("res", 1)},
    "GameMap": {"tex": ("res", 1)},
    "ProjectNode": {"file": ("str", 1), "speed": ("float", 2)},
    "Component": {"comType": ("str", 1)},
    "Armature": {"file": ("str", 1)},
}


def is_widget_options(fb: FB, t: int) -> bool:
    """WidgetOptions 的特征：21 个字段（vtable 46 字节）。"""
    if not t:
        return False
    vt = t - fb.i32(t)
    if vt < 0 or vt >= t:
        return False
    return fb.u16(vt) == 46


def resolve_widget_options(fb: FB, data: int) -> int:
    """options.data 一般包一层 *Options（field0 = widgetOptions）；
    classname 为 Node 时导出器把它拍平，data 本身就是 WidgetOptions。"""
    if not data:
        return 0
    inner = fb.s_table(data, 0)
    if is_widget_options(fb, inner):
        return inner
    if is_widget_options(fb, data):
        return data
    return inner or data


def read_value(fb: FB, t: int, spec) -> object:
    kind, idx = spec
    if kind == "str":
        return fb.s_str(t, idx)
    if kind == "int":
        return fb.s_int(t, idx)
    if kind == "float":
        return fb.s_float(t, idx)
    if kind == "bool":
        return fb.s_bool(t, idx)
    if kind == "bool_true":
        return fb.s_bool(t, idx, True)
    if kind == "ubyte":
        return fb.s_ubyte(t, idx, 255)
    if kind == "vec2":
        return fb.s_vec2(t, idx)
    if kind == "color":
        return fb.s_color(t, idx)
    if kind == "quad":
        p = fb.field(t, idx)
        if not p:
            return [0.0, 0.0, 0.0, 0.0]
        return [fb.f32(p + 4 * i) for i in range(4)]
    if kind == "res":
        sub = fb.s_table(t, idx)
        if not sub:
            return None
        path = fb.s_str(sub, 0)
        return path or None
    raise ValueError(kind)


def parse_action(fb: FB, root: int) -> dict:
    """解 NodeAction：按 actionTag 收稳定态。

    CSB 的 WidgetOptions 存的是时间轴**首帧**（常见 alpha=0、位置在屏幕外），
    直接渲染会得到一张空面板。这里：位置/缩放/旋转取**末帧**（动画收敛处），
    alpha 取整条轨道的**最大值**（见下，末帧缺字段不能当 0）。
    """
    act = fb.s_table(root, 4)
    if not act:
        return {}
    out = {
        "name": fb.s_str(act, 3),
        "duration": fb.s_int(act, 0),
        "tags": {},
    }
    def frame_index(f: int) -> int:
        for i in range(9):
            sub = fb.s_table(f, i)
            if sub:
                return fb.s_int(sub, 0)
        return 0

    for tl in fb.vec_tables(fb.field(act, 2)):
        prop = fb.s_str(tl, 0)
        tag = fb.s_int(tl, 1)
        frames = fb.vec_tables(fb.field(tl, 2))
        if not frames:
            continue
        last = max(frames, key=frame_index)
        slot = out["tags"].setdefault(tag, {})
        if prop == "Alpha":
            # IntFrame.value 缺省是 0（flatbuffers 省略默认值），所以「末帧没写 value」
            # 不等于「末帧 alpha=0」。按末帧取会把已经淡入完成的面板整片淡出。
            # 静态预览要的是可见态 ⇒ 取该轨道出现过的**最大 alpha**。
            best = None
            for f in frames:
                cf = fb.s_table(f, 2)
                if cf:
                    p = fb.field(cf, 2)
                    if not p:
                        continue
                    v = fb.b[p]
                else:
                    itf = fb.s_table(f, 5)
                    if not itf:
                        continue
                    p = fb.field(itf, 2)
                    if not p:
                        continue
                    v = fb.s_int(itf, 2)
                if best is None or v > best:
                    best = v
            if best is not None:
                slot["alpha"] = max(0, min(255, best))
        elif prop == "Position":
            pf = fb.s_table(last, 0)
            if pf:
                slot["pos"] = fb.s_vec2(pf, 2)
        elif prop == "Scale":
            sf = fb.s_table(last, 1)
            if sf:
                slot["scale"] = fb.s_vec2(sf, 2)
        elif prop == "RotationSkew":
            pf = fb.s_table(last, 0)
            if pf:
                slot["rot"] = fb.s_vec2(pf, 2)
    return out


def parse_node(fb: FB, t: int, depth: int = 0, anim: dict | None = None) -> dict:
    cls = fb.s_str(t, 0) or "Node"
    custom = fb.s_str(t, 3)
    opts = fb.s_table(t, 2)          # Options
    data = fb.s_table(opts, 0)       # Options.data → 具体 *Options 表

    node = {"class": cls}
    if custom:
        node["customClass"] = custom

    # widgetOptions 通常在 0 号字段；Armature/Component 等也一致
    wo = resolve_widget_options(fb, data)
    for key, spec in COMMON.items():
        node[key] = read_value(fb, wo, spec)

    spec = SPEC.get(cls, {})
    for key, sp in spec.items():
        if sp[1] is None:
            continue
        node[key] = read_value(fb, data, sp)

    # Text 的 color：TextOptions 没有独立 textColor 字段，
    # 引擎取 widgetOptions.color；这里显式标记来源，避免误判。
    if cls in ("Text", "TextBMFont", "TextAtlas"):
        node["textColor"] = node.get("color")

    slot = (anim or {}).get("tags", {}).get(node.get("actionTag") or 0)
    if slot:
        if "alpha" in slot:
            # 取「设计值」与「动画最大 alpha」的较大者：动画只应让元素更明显，
            # 不该因为一条淡出轨道把设计上不透明的面板渲染成空白。
            node["alpha"] = max(node.get("alpha", 255), slot["alpha"])
        if "pos" in slot:
            node["pos"] = slot["pos"]
        if "scale" in slot:
            node["scale"] = slot["scale"]
        if "rot" in slot:
            node["rot"] = slot["rot"]
        node["animated"] = True

    kids = fb.vec_tables(fb.field(t, 1))
    if kids:
        node["children"] = [parse_node(fb, k, depth + 1, anim) for k in kids]
    return node


STATE_SUFFIXES = ("_nor", "_down", "_dis", "_disable", "_sel", "_off", "_on")
# 同一父节点下同名不同后缀的贴图，是同一个控件的多种状态（常态/按下/禁用/选中）。
# 静态预览只应保留一种，默认取常态；没有常态时按下面顺序退。
STATE_PREF = ("_nor", "_on", "_sel", "_down", "_disable", "_dis", "_off")


def state_of(node: dict) -> tuple[str, str] | None:
    """返回 (去后缀的前缀, 状态后缀)，不是状态图则 None。"""
    tex = node.get("tex") or node.get("bg") or ""
    if not tex:
        return None
    base = tex.replace("\\", "/").rsplit("/", 1)[-1]
    if base.lower().endswith(".png"):
        base = base[:-4]
    for suf in STATE_SUFFIXES:
        if base.endswith(suf):
            return base[:-len(suf)], suf
    return None


def collapse_states(node: dict) -> int:
    """按前缀折叠同一控件的多状态贴图，标 hiddenByState，返回隐藏数量。

    只处理**同一父节点下的兄弟**：不同父节点下的同名贴图可能是不同控件，
    跨父节点合并会误伤。
    """
    hidden = 0
    kids = node.get("children") or []
    groups: dict[str, list[tuple[str, dict]]] = {}
    for c in kids:
        st = state_of(c)
        if st:
            groups.setdefault(st[0], []).append((st[1], c))
    for stem, arr in groups.items():
        if len({s for s, _ in arr}) < 2:
            continue
        order = {s: i for i, s in enumerate(STATE_PREF)}
        keep = min(arr, key=lambda t: (order.get(t[0], 99),
                                       t[1].get("z") or 0))[1]
        keep["state"] = next(s for s, c in arr if c is keep)
        keep["stateStem"] = stem
        for suf, c in arr:
            if c is not keep:
                c["hiddenByState"] = keep.get("name") or stem
                c["state"] = suf
                hidden += 1
    for c in kids:
        hidden += collapse_states(c)
    return hidden


def count_visible_textures(node: dict, eff: bool = True) -> int:
    """按层级算「真正能看见」的带贴图节点数（父级不可见则子级也不算）。"""
    vis = eff and node.get("visible", True) and (node.get("alpha", 255) > 0)
    n = 1 if (vis and (node.get("tex") or node.get("bg"))) else 0
    for c in node.get("children", []):
        n += count_visible_textures(c, vis)
    return n


def relax_hidden_alpha(node: dict) -> int:
    """整页没有任何可见贴图时，把 alpha=0 的节点放开。

    这些面板的设计态是「容器透明、脚本运行时淡入」，静态预览若照抄就是一张空页。
    只在**整页全隐**时兜底，不做逐节点放开，避免把原本该藏的层也翻出来。
    """
    changed = 0
    for n in walk(node):
        if n.get("alpha", 255) == 0 and (n.get("tex") or n.get("bg")
                                         or n.get("children")):
            n["alpha"] = 255
            n["alphaRelaxed"] = True
            changed += 1
    return changed


def parse_csb(path: pathlib.Path) -> dict:
    buf = path.read_bytes()
    fb = FB(buf)
    root = fb.root()
    tree = fb.s_table(root, 3)
    if not tree:
        raise ValueError(f"{path.name}: 无 nodeTree")
    anim = parse_action(fb, root)
    out = {
        "csb": path.name,
        "version": fb.s_str(root, 0),
        "textures": fb.vec_strings(fb.field(root, 1)),
        "texturePngs": fb.vec_strings(fb.field(root, 2)),
        "animation": {"name": anim.get("name", ""),
                      "duration": anim.get("duration", 0),
                      "tracks": len(anim.get("tags", {})),
                      "applied": "last-frame"},
        "root": parse_node(fb, tree, 0, anim),
        "bytes": len(buf),
    }
    out["stats"] = summarize(out["root"])
    out["stats"]["state_hidden"] = collapse_states(out["root"])
    out["stats"]["alpha_relaxed"] = (
        relax_hidden_alpha(out["root"]) if count_visible_textures(out["root"]) == 0
        else 0)
    return out


def walk(node: dict):
    yield node
    for k in node.get("children", []):
        yield from walk(k)


def summarize(root: dict) -> dict:
    nodes = list(walk(root))
    by_class = Counter(n["class"] for n in nodes)
    tex = sorted({n[k] for n in nodes for k in ("tex", "bg") if n.get(k)})
    return {
        "nodes": len(nodes),
        "by_class": dict(by_class.most_common()),
        "textures": tex,
        "texts": [n.get("text") for n in nodes if n.get("text")][:20],
    }


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("-")]
    flags = {a for a in argv if a.startswith("-")}

    base = ui_dir()
    if "--all" in flags:
        limit = 0
        for a in argv:
            if a.startswith("--limit="):
                limit = int(a.split("=", 1)[1])
        files = sorted(base.glob("*.csb"))
        if limit:
            files = files[:limit]
        ok = 0
        fails = []
        total_nodes = 0
        classes = Counter()
        tex_missing = 0
        for p in files:
            try:
                d = parse_csb(p)
            except Exception as e:                              # noqa: BLE001
                fails.append((p.name, str(e)))
                continue
            ok += 1
            total_nodes += d["stats"]["nodes"]
            classes.update(d["stats"]["by_class"])
            for t in d["stats"]["textures"]:
                if not (base / t.replace(".png", ".ktx")).exists():
                    tex_missing += 1
        print(f"CSB 总数 {len(files)}  解析成功 {ok}  失败 {len(fails)}")
        print(f"节点总数 {total_nodes}  平均 {total_nodes / max(ok, 1):.1f}")
        print("节点类型:", dict(classes.most_common(12)))
        print(f"缺贴图引用 {tex_missing}")
        for n, e in fails[:10]:
            print("  失败", n, e)
        return 0 if not fails else 1

    if not args:
        print(__doc__)
        return 2
    p = pathlib.Path(args[0])
    d = parse_csb(p)
    if "--stdout" not in flags:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        (OUT_DIR / (p.stem + ".json")).write_text(
            json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{p.name}  {d['version']}  {d['bytes']}B")
    print(f"节点 {d['stats']['nodes']}  类型 {d['stats']['by_class']}")
    print(f"贴图 {len(d['stats']['textures'])}  文本 {d['stats']['texts'][:6]}")
    r = d["root"]
    print(f"根 {r['class']} size={r['size']} anchor={r['anchor']} pos={r['pos']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
