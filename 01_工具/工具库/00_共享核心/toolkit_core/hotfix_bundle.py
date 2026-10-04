# -*- coding: utf-8 -*-
r"""hotfix_bundle —— 热更拆包交付物的【标准结构】生成器。

对标结论（其它拆包项目的共同约定）：
  · Intelli-verse-X asset-pipeline-standard：一个根目录下按类型分子目录
    （Sounds/{Music,SFX}/ Video/ UI/{Icons,Backgrounds}/ Localization/ Config/）
    + 顶层 manifest.json 作为主索引
  · evrFileTools：`inventory` 模式（按类型统计数量与体积）+ `diff` 模式
  · ree-pak-rs：`--skip-unknown`（名字不明的单独处理）
  · Source2Viewer：`.manifest.txt` 缓存做增量

本模块产出的标准结构：
     <out>/
       README.md                 人读：这次热更干了什么、怎么复现
       manifest.json             ★ 主索引（机器读）：每条含 路径/容器/行号/大小/sha256/来源
       inventory.json            ★ 类型统计（数量 + 体积，按扩展名与顶层目录）
       hotfix_report.json        原样保留的六步报告
       pkgs/                     原始下发包（保留，可复现）
       ├─ 01_还原树/             ★ 按名字还原的前端目录树（无名 → _未命名/<容器>/<行号>.<ext>）
       ├─ 02_文字表/             ★ 文字表单独汇总（索引 + 文案 + 分类）
       ├─ 03_影音图文表/         ★ 影音图文单独汇总
       │     ├─ 音频/ 视频/ 图片/ 特效定义/ 文本/
       ├─ 04_图集/               ★ spine 图集（atlas / 本体 / 切出的 sprite）
       ├─ 05_变更清单/           新增 / 移除 / 内容变更
       └─ 99_未归类/             ★ 取不到名字或格式不认的（--skip-unknown 的落点）

★ 铁律：
  · 不编造：取不到名字就进 `99_未归类` 并如实标注原因
  · manifest.json 是唯一真相源，所有分类目录都从它派生
  · 幂等：重复跑只补不改（已存在的文件不重复写）
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
import struct
import sys
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Dict, Iterable, List, Optional

# ── 目录名（★ 2026-09-28 按用户口径定稿：5 个顶层） ──────────────
# ★ 2026-09-29（S4）：交付结构去掉 `01_还原树` 顶层。
#   理由（用户口径）：「热更拆包的还原树改为在全量还原树上增增补补，不再单独交付」。
#   ⇒ 还原树只有一份（03_执行/41_还原树），由 `hotfix apply` 就地增补；
#     交付只给「变了什么」的可读视图（文字表 / 媒体 / 脚本与其他 / 变更清单）。
#   ★ D_TREE 保留常量仅为兼容旧调用点（值已改为「无」），别再往交付里铺树。
D_TREE = ""                        # ★ 已弃用：交付不再含还原树
D_TEXT = "01_文字表"                # 文字表汇总
D_MEDIA = "02_媒体文件"             # ★ 所有图 / 视频 / 音频，子路径再分类
D_OTHER = "03_脚本与其他"           # 脚本 / 图集 / 3D件 / 数据件 / 未解格式 / 未识别
D_DELTA = "04_变更清单与报告总结"   # 变更清单 + 报告文件

# 交付顶层（★ 4 个 —— 不含还原树）
TOP_DIRS = (D_TEXT, D_MEDIA, D_OTHER, D_DELTA)

# 03_媒体文件 下的分类
M_IMG = "图片"
M_IMG_R = "能看的图"                # 立绘大图 / 界面图 / UI图标 / 文字图
M_IMG_M = "看不懂的"                # 方块贴图图集 / 场景地表 / 特效图 / 角色 / 建筑 / …
M_VIDEO = "视频"
M_AUDIO = "音频"

# 04_脚本与其他 下的分类
O_SCRIPT = "脚本层"
O_ATLAS = "图集"
O_3D = "3D件"
O_FX = "特效数据"
O_CFG = "配置与界面数据"
O_UNSOLVED = "未解格式"
O_MISC = "未识别"
O_SHADER = "着色器"                   # ★ .ccaa5566 = NeoX .pipe 编译着色器变体（DXBC）

# 05 下的分类
V_CHANGES = "变更清单"

# ★ 兼容旧名（模块其余地方仍引用这些标识）
D_READABLE = D_MEDIA
D_MATERIAL = D_MEDIA
D_ATLAS = D_OTHER
D_SCRIPT = D_OTHER
D_ASSETS = D_OTHER
D_UNKNOWN = D_OTHER
D_TEXT2 = D_TEXT
SUB_AUDIO = M_AUDIO
SUB_VIDEO = M_VIDEO
SUB_IMAGE = M_IMG
SUB_FX = O_FX
SUB_TEXT = "文本"

# ══════════════════════════════════════════════════════════════════
# ★ 2026-09-28 重定的图片分类：按【人眼能不能看懂】分，不按文件格式分
#
#   实测依据（用户人工判定 4 组样本，我的判据与之一致）：
#     · 方块2幂（128/256/512/1024/2048 且 w==h）     → 看不懂的纹理/材质贴图
#     · 非方块 · 短边 ≥256                          → 人眼能看（立绘/海报级）
#     · 非方块 · 短边 64~255                        → 人眼能看（界面图）
#     · 非方块 · 短边 <64                           → 能看的 UI 小图（图标）
#   有名文件优先看【路径顶层目录 + 关键词】，无名文件靠【魔数 + 尺寸形状】。
# ══════════════════════════════════════════════════════════════════

# 03 下的子类
R_BIG = "立绘大图"
R_UI = "界面图"
R_ICON = "UI图标"
R_TXT = "文字图"

# 04 下的子类（按游戏自己的顶层目录分）
M_MAP = {
    "character": "角色贴图",
    "effect": "特效图",
    "scene": "场景地表",
    "building": "建筑贴图",
    "weapon": "武器贴图",
    "utility": "道具贴图",
    "model": "模型贴图",
    "model_high_2024": "模型贴图",
    "weather": "天气图",
    "instance": "场景地表",
    "judian_icon": "据点图标",
    "common_cj_v3": "通用贴图",
    "shader": "着色器",
}

# 顶层目录白名单：这些目录是「给玩家看的 UI」
TOP_READABLE = {"ui", "other_icon", "zhutihuodong", "all_txt_meishuzi_icon",
                "shizhuang_icon", "huodongrukou"}
# 文件名关键词
KW_READABLE = ("icon", "tujian", "xuanchuan", "poster", "haibao", "banner",
               "logo", "zengsong", "img_", "txt_", "card", "avatar", "touxiang",
               "zhenrong", "lihui", "juese", "head", "portrait", "preview")
KW_MATERIAL = ("textures/", "matidtex", "lightmap", "_uvva", "_lm.")

# 内容魔数（无名块只能靠它）+ 图片魔数
IMG_MAGIC = ((b"DDS ", True), (b"\x89PNG", True), (b"\xff\xd8\xff", True),
             (b"GIF8", True))
IMG_EXTS = {"dds", "tga", "png", "jpg", "jpeg", "webp", "bmp", "gif"}
POW2 = lambda x: x > 0 and (x & (x - 1)) == 0       # noqa: E731

# 内容魔数 → 大类（无名块靠这个分拣，比扩展名可靠）
MAGIC_CLASS = (
    (b"\x00\x00\x00 ftyp", "video"),      # MP4（32 位大端 box size + 'ftyp'）
    (b"ftyp", "video"),
    (b"FSB5", "audio"),
    (b"RIFF", "audio"),
    (b"OggS", "audio"),
    (b"DDS ", "image"),
    (b"\x89PNG", "image"),
    (b"\xff\xd8\xff", "image"),            # JPEG
    (b"GIF8", "image"),
    (b"<FxGroup", "fx"),
    (b"<?xml", "text"),
    (b"\xef\xbb\xbf", "text"),
    # ★★ 实证 2026-09-28（子代理独立复核 + 助手 400/400 复验）：
    #    cc aa 55 66 = NeoX 的 `.pipe` 编译着色器变体缓存容器。
    #    外层 0x20 字节自定义头；之后每 blob = {u64 阶段标志, u64 长度} + blob。
    #    内层 100% 是标准未加密 Microsoft DXBC（chunk 恒为 RDEF/ISGN/OSGN/SHEX/STAT）。
    #    阶段标志：0=vertex 1=pixel 2=compute。
    #    ★ 别写成 b"ccaa5566"（那是 8 字节 ASCII）—— 魔数只有 4 字节。
    #    全库 122,459 个 = effect_cache.gpk 97,590 + gres\0000.gpk 24,869。
    (b"\xcc\xaa\x55\x66", "shader"),
)


def magic_class(blk: bytes) -> str:
    """按内容魔数判大类（无名块用）。"""
    for sig, cls in MAGIC_CLASS:
        if blk.startswith(sig):
            return cls
    # marshal code object（0x73 = TYPE_CODE 带引用标志的变体）→ 脚本层
    if blk[:1] in (b"\x73", b"\xe3"):
        return "script"
    return ""


def classify_image(name: str | None, dims: tuple | None) -> tuple:
    """图片分类：→ (二级, 子类)。非图返回 (None, None)。

    二级取值：M_IMG_R（能看的图）/ M_IMG_M（看不懂的）。

    ★ 判据优先级（实测验证过，见文件头那段注释）：
      ① 有名 → 看路径顶层目录（游戏自己按用途分过区）与文件名关键词
      ② 无名/无特征 → 看形状与尺寸
            方块2幂            → 看不懂的贴图（废图）
            非方块 短边≥256    → 人眼能看（立绘/海报级）
            非方块 短边 64~255 → 人眼能看（界面图）
            非方块 短边 <64    → 能看的 UI 小图（图标）
    """
    nm = str(name or "").replace(chr(92), "/")
    low = nm.lower()
    top = low.split("/")[0] if low else ""
    is_mat = any(k in low for k in KW_MATERIAL)

    # ① 有名
    if nm:
        if top in TOP_READABLE:
            if is_mat:
                return M_IMG_M, "通用贴图"
            return M_IMG_R, (R_TXT if "txt_" in low else R_ICON)
        if top in M_MAP:
            return M_IMG_M, M_MAP[top]
        if is_mat:
            return M_IMG_M, "通用贴图"
        if any(k in low for k in KW_READABLE):
            return M_IMG_R, R_ICON

    # ② 无名 / 无特征 → 形状尺寸
    if dims:
        w, h = dims
        if w == h and POW2(w):
            return M_IMG_M, "方块贴图图集"
        m = min(w, h)
        if m >= 256:
            return M_IMG_R, R_BIG
        if m >= 64:
            return M_IMG_R, R_UI
        return M_IMG_R, R_ICON
    return None, None


def image_dims(p) -> tuple | None:
    """读图头拿 (宽, 高)。DDS / PNG 支持，其它返回 None。"""
    try:
        with Path(p).open("rb") as fh:
            h = fh.read(32)
    except OSError:
        return None
    if h[:4] == b"DDS " and len(h) >= 20:
        hh, ww = struct.unpack_from("<II", h, 12)
        return (ww, hh)
    if h[:8] == b"\x89PNG\r\n\x1a\n":
        ww, hh = struct.unpack_from(">II", h, 16)
        return (ww, hh)
    return None

# 扩展名 → 大类（用于影音图文表分拣）
EXT_CLASS = {
    # 音频
    "fsb5": "audio", "fsb": "audio", "wav": "audio", "mp3": "audio", "ogg": "audio",
    "fev": "audio", "bank": "audio", "riff": "audio",
    # 视频
    "mp4": "video", "webm": "video", "usm": "video", "bik": "video", "ivf": "video",
    # 图片
    "dds": "image", "png": "image", "jpg": "image", "jpeg": "image", "tga": "image",
    "webp": "image", "bmp": "image", "gif": "image",
    # 文本 / 特效定义
    "txt": "text", "xml": "text", "json": "text", "atlas": "text", "csv": "text",
    "plist": "text", "csb": "text", "mtg": "text", "c159": "text",
    # 图集/骨架
    "spine": "atlas",
}


def _sha256(p: Path, limit: int | None = None) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        while True:
            b = fh.read(1 << 20)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def _ext_of(name: str) -> str:
    s = str(name)
    if "." not in s:
        return ""
    return s.rsplit(".", 1)[-1].lower()


def _safe(rel: str) -> Path:
    """把游戏内路径转成安全的相对路径（禁 .. / 绝对路径 / 盘符）。"""
    s = str(rel).replace("\\", "/").lstrip("/")
    parts = [p for p in s.split("/") if p and p not in (".", "..")]
    if not parts:
        return Path("_")
    return Path(*parts)


class Bundle:
    """热更交付物标准结构。"""

    def __init__(self, out: str | Path, *, names_dict=None, db_path=None,
                 index_root=None, tool_root=None):
        self.out = Path(out)
        self.names = {}
        if names_dict:
            p = Path(names_dict)
            if p.is_file():
                self.names = json.loads(p.read_text(encoding="utf-8"))
        self.db_path = db_path
        self.tool_root = Path(tool_root) if tool_root else Path(__file__).resolve().parents[1]
        self.rows: List[dict] = []
        self._seen: Dict[tuple, dict] = {}
        self.unknown: List[dict] = []
        self._loc = None

    # ── 目录（★ 5 顶层：还原树 / 文字表 / 媒体文件 / 脚本与其他 / 变更清单与报告总结）──
    def ensure_dirs(self) -> None:
        # ★ S4：不再创建 01_还原树（交付不含还原树）
        for d in TOP_DIRS:
            (self.out / d).mkdir(parents=True, exist_ok=True)
        # 02_媒体文件
        for s in (M_VIDEO, M_AUDIO):
            (self.out / D_MEDIA / s).mkdir(parents=True, exist_ok=True)
        for s in (R_BIG, R_UI, R_ICON, R_TXT):
            (self.out / D_MEDIA / M_IMG / M_IMG_R / s).mkdir(parents=True, exist_ok=True)
        for s in sorted(set(M_MAP.values())) + ["通用贴图", "方块贴图图集"]:
            (self.out / D_MEDIA / M_IMG / M_IMG_M / s).mkdir(parents=True, exist_ok=True)
        # 03_脚本与其他
        for s in (O_SCRIPT, O_ATLAS, O_3D, O_FX, O_CFG, O_UNSOLVED, O_MISC, O_SHADER):
            (self.out / D_OTHER / s).mkdir(parents=True, exist_ok=True)
        # 04_变更清单与报告总结
        (self.out / D_DELTA / V_CHANGES).mkdir(parents=True, exist_ok=True)

    # ── 定位 ────────────────────────────────────────────────
    def locator(self):
        if self._loc is None:
            if str(self.tool_root) not in sys.path:
                sys.path.insert(0, str(self.tool_root))
            from toolkit_core import artifact_locator as AL
            self._loc = AL.Locator()
        return self._loc

    # ── 登记一条产物 ────────────────────────────────────────
    def add(self, *, container: str, row: int, name: str | None,
            source: str = "", size: int | None = None,
            sha256: str | None = None, note: str = ""):
        """登记一条产物。★ 按 (容器, 行) 去重 —— overlay 块与新增行会指向同一行，
        重复登记会让 manifest 与分类目录计数虚高（实测出现过 ×2）。"""
        key = (str(container), int(row))
        if key in self._seen:
            old = self._seen[key]
            # 合并来源说明，不新增条目
            if source and source not in old.get("source", ""):
                old["source"] = (old.get("source", "") + " + " + source).strip(" +")
            if note and note not in old.get("note", ""):
                old["note"] = (old.get("note", "") + " | " + note).strip(" |")
            return old
        rec = {
            "container": container,
            "row": int(row),
            "name": name or "",
            "ext": _ext_of(name or ""),
            "size": size,
            "sha256": sha256,
            "source": source,
            "note": note,
            "named": bool(name),
        }
        self._seen[key] = rec
        self.rows.append(rec)
        return rec

    # ── 物化 ────────────────────────────────────────────────
    def materialize(self, *, link=True, do_sha=True, workers=None, png=False) -> dict:
        """把登记的产物铺成标准结构。link=True 时用硬链接（省空间、幂等）。
        png=True 时把 DDS 额外转出 PNG（用户要的「能看的图」）。

        workers：★ 不给就走智能调度（`throttle.global_jobs("io")`）。
                 铺产物 = 读源 + 建链接/复制，I/O 主导。
        """
        if workers is None:
            try:
                from toolkit_core import throttle as _TH
                workers = _TH.global_jobs("io")
            except Exception:
                workers = 16
        self.ensure_dirs()
        loc = self.locator()
        stat = Counter()
        self._png = bool(png)
        self._dec = None
        if png:
            try:
                # ★ 02_图文音频渲染 在【工具库/】下，不在 00_共享核心/ 下
                for cand in (self.tool_root.parent / "02_图文音频渲染" / "皮肤链与渲染",
                             self.tool_root / "02_图文音频渲染" / "皮肤链与渲染"):
                    if cand.is_dir():
                        sys.path.insert(0, str(cand))
                        break
                from dds_rgba_canonical import decode_dds_rgba_u8  # noqa
                self._dec = decode_dds_rgba_u8
                print("  ✓ PNG 转换已就绪：%s" % self._dec.__module__)
            except Exception as exc:
                print("  ⚠ PNG 转换不可用（%s: %s），只放原始 DDS"
                      % (type(exc).__name__, str(exc)[:60]))
                self._png = False

        def to_png(src: Path, dst: Path) -> bool:
            """图片 → PNG。DDS 走解码器，TGA/其它走 PIL。失败返回 False（不编造）。"""
            if not self._png:
                return False
            head = src.read_bytes()[:4]
            try:
                import numpy as np
                from PIL import Image
                if head == b"DDS ":
                    if self._dec is None:
                        return False
                    tmp = dst.parent / ("_t_%d.dds" % (hash(str(dst)) & 0xFFFFFF))
                    try:
                        tmp.write_bytes(src.read_bytes())
                        u8, prov = self._dec(str(tmp), verify_oiio=False)
                        Image.fromarray(
                            np.asarray(u8).reshape(prov["height"], prov["width"], 4),
                            "RGBA").save(dst)
                        return True
                    finally:
                        try:
                            tmp.unlink()
                        except OSError:
                            pass
                # TGA / PNG / JPG 等：PIL 直接开
                with Image.open(src) as im:
                    im.convert("RGBA").save(dst)
                return True
            except Exception:
                return False

        def place(r):
            src = loc.path(r["container"], r["row"])
            if src is None:
                r["note"] = (r["note"] + " | 产物缺失").strip(" |")
                self.unknown.append(r)
                return None
            # ★ S4：不再先铺一份到 01_还原树。
            #   交付里每件只出现一次（分类目录），还原树由 `hotfix apply` 就地增补。
            #   size/sha 从【源】算，而不是从刚落的副本算。
            try:
                r["size"] = src.stat().st_size
            except OSError:
                r["size"] = None
            if do_sha and not r.get("sha256"):
                try:
                    r["sha256"] = _sha256(src)
                except OSError:
                    r["sha256"] = ""
            # ── 分类落脚 ────────────────────────────────────────
            # ★ 2026-09-28 重定：按【人眼能不能看懂】分（见文件头那段注释），
            #   不再按「文件格式」分。原 03_影音图文表 + 04_图集 已合并进这套结构。
            base = (Path(r["name"]).name if r["name"] else
                    "%s_%08d%s" % (Path(str(r["container"]).replace(chr(92), "/")).stem,
                                   r["row"], src.suffix))
            cls = EXT_CLASS.get(r["ext"], "")
            if not cls and not r["named"]:
                try:
                    cls = magic_class(src.read_bytes()[:16])
                except OSError:
                    cls = ""

            top_dir = sub_dir = None
            parts = None                  # 图片用三级路径：媒体文件/图片/{能看的图|看不懂的}/子类
            if cls == "image" or (not cls and r["named"] and r["ext"] in IMG_EXTS):
                dims = image_dims(src)
                lv2, sub_dir = classify_image(r["name"], dims)
                if lv2 is None:
                    # 是图但读不出尺寸（损坏/非常见头）→ 如实标注，不进「能看的图」
                    self.unknown.append({
                        "container": r["container"], "row": r["row"],
                        "name": r["name"], "ext": r["ext"], "size": r.get("size"),
                        "note": "识别为图但读不出尺寸（无法判可读性）"})
                    stat["img_nodims"] += 1
                    return r
                top_dir, parts = D_MEDIA, (M_IMG, lv2, sub_dir)
            elif cls == "audio":
                top_dir, sub_dir = D_MEDIA, M_AUDIO
            elif cls == "video":
                top_dir, sub_dir = D_MEDIA, M_VIDEO
            elif cls == "atlas" or r["ext"] in ("atlas", "json"):
                top_dir, sub_dir = D_OTHER, O_ATLAS
            elif cls == "script":
                top_dir, sub_dir = D_OTHER, O_SCRIPT
            # ── 已知的「其它素材件」：给它们一个家，别一律塞未归类 ──
            elif cls == "shader" or r["ext"] == "ccaa5566":
                # ★★ .ccaa5566 = NeoX .pipe 编译着色器变体（内层标准 DXBC）
                #    全库 12.2 万；本次热更 10,733 条无名块里占 ~81%
                top_dir, sub_dir = D_OTHER, O_SHADER
            elif r["ext"] in ("gim", "mesh", "gis", "mtg", "spr", "stb", "array"):
                top_dir, sub_dir = D_OTHER, O_3D
            elif cls == "fx" or r["ext"] in ("sfx", "fev"):
                top_dir, sub_dir = D_OTHER, O_FX
            elif r["ext"] in ("c159", "octl", "cvis", "rgis", "bin"):
                top_dir, sub_dir = D_OTHER, O_UNSOLVED
            elif r["ext"] in ("csb", "plist", "xml", "text", "txt", "csv"):
                top_dir, sub_dir = D_OTHER, O_CFG
            else:
                # ★ 真·不认识：无名 + 魔数不认 + 扩展名未知
                b0 = b""
                try:
                    b0 = src.read_bytes()[:8]
                except OSError:
                    pass
                top_dir, sub_dir = D_OTHER, O_MISC
                self.unknown.append({
                    "container": r["container"], "row": r["row"], "name": r["name"],
                    "ext": r["ext"], "size": r.get("size"),
                    "note": "魔数=%s 扩展名=%s（已放入 %s/%s）"
                            % (b0.hex() or "?", r["ext"] or "?", D_OTHER, O_MISC)})
                stat["unclassified"] += 1

            if parts:
                d2 = self.out.joinpath(top_dir, *parts, base)
            else:
                d2 = (self.out / top_dir / sub_dir / base) if sub_dir else (self.out / top_dir / base)
            # ★ 分类落脚：图片 + --png 时【只写 PNG】，不留 DDS（用户要求：别让 dds 和 png 并存浪费空间）；
            #   转失败才退回原始文件（宁可有损也不丢内容）。01_还原树 保持原始不动。
            only_png = (parts is not None and self._png
                        and src.suffix.lower() in (".dds", ".tga", ".bmp", ".webp"))
            if only_png:
                d2 = d2.with_suffix(".png")
            d2.parent.mkdir(parents=True, exist_ok=True)
            r["classified"] = str(d2.relative_to(self.out))

            wrote = False
            if only_png:
                if d2.exists() or to_png(src, d2):
                    wrote = True
                    stat["png"] += 1
                else:
                    stat["png_fail"] += 1
                    d2 = d2.with_suffix(src.suffix)        # 退回原始
                    r["classified"] = str(d2.relative_to(self.out))
            if not wrote and not d2.exists():
                try:
                    d2.hardlink_to(src)
                except FileExistsError:
                    pass
                except OSError:
                    try:
                        shutil.copy2(src, d2)
                    except (FileExistsError, PermissionError):
                        pass
            stat["%s/%s" % (top_dir, sub_dir or "-")] += 1
            stat["placed"] += 1
            return r

        with ThreadPoolExecutor(max_workers=workers) as ex:
            for _ in ex.map(place, self.rows):
                pass
        return dict(stat)

    # ── 汇总文件 ────────────────────────────────────────────
    def write_manifest(self, *, meta: dict | None = None) -> Path:
        p = self.out / "manifest.json"
        named = [r for r in self.rows if r["named"]]
        body = {
            "schema": "lifeafter-hotfix-bundle-v1",
            "generated": __import__("time").strftime("%Y-%m-%dT%H:%M:%S"),
            "meta": meta or {},
            "counts": {
                "total": len(self.rows),
                "named": len(named),
                "unnamed": len(self.rows) - len(named),
                "unknown": len(self.unknown),
            },
            "entries": self.rows,
        }
        p.write_text(json.dumps(body, ensure_ascii=False, indent=1), encoding="utf-8")
        return p

    def write_inventory(self) -> Path:
        by_ext = Counter()
        bytes_ext = Counter()
        by_top = Counter()
        for r in self.rows:
            e = r["ext"] or "(无扩展名)"
            by_ext[e] += 1
            bytes_ext[e] += r.get("size") or 0
            if r["name"]:
                by_top[r["name"].replace("\\", "/").split("/")[0]] += 1
            else:
                by_top["(未命名)"] += 1
        body = {
            "total_files": len(self.rows),
            "total_bytes": sum(r.get("size") or 0 for r in self.rows),
            "by_ext": [{"ext": k, "count": v, "bytes": bytes_ext[k]}
                       for k, v in by_ext.most_common()],
            "by_top_dir": [{"dir": k, "count": v} for k, v in by_top.most_common()],
        }
        p = self.out / D_DELTA / "inventory.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(body, ensure_ascii=False, indent=1), encoding="utf-8")
        return p

    def write_readme(self, *, hotfix_ts: str = "", packages: Iterable[str] = (),
                     locate: str = "", extra: str = "") -> Path:
        self.ensure_dirs()
        L = [
            "# 本次热更交付物",
            "",
            "热更时间戳 **%s**" % (hotfix_ts or "（未提供）"),
            "",
            "## 结构",
            "",
            "| 目录 | 内容 |",
            "|---|---|",
            "| `manifest.json` | ★ 主索引（机器读）：每条含 路径 / 容器 / 行号 / 大小 / sha256 / 来源 |",
            "| `inventory.json` | ★ 类型统计（按扩展名与顶层目录的数量、体积） |",
            "| `hotfix_report.json` | 六步流程报告 |",
            "| `pkgs/` | 原始下发包（保留以便复现） |",
            "| `%s/` | 文字表单独汇总（索引 / 文案去重 / 按表 TSV / 分类） |" % D_TEXT,
            "| `%s/` | ★ **所有图 / 视频 / 音频**，子路径再分类 |" % D_MEDIA,
            "|     `%s/%s/%s/` | ★ **人眼能看懂**：立绘大图 / 界面图 / UI图标 / 文字图 |"
            % (D_MEDIA, M_IMG, M_IMG_R),
            "|     `%s/%s/%s/` | ★ **看不懂的素材底图**：方块图集 / 场景地表 / 特效 / 角色 / 建筑 / 道具 |"
            % (D_MEDIA, M_IMG, M_IMG_M),
            "|     `%s/%s/` · `%s/%s/` | 视频 · 音频 |" % (D_MEDIA, M_VIDEO, D_MEDIA, M_AUDIO),
            "| `%s/` | 脚本层 · 图集 · 3D件 · 特效数据 · **着色器** · 配置数据 · 未解格式 · 未识别 |" % D_OTHER,
            "| `%s/` | 变更清单 + inventory / hotfix_report |" % D_DELTA,
            "",
            "## 本次统计",
            "",
            "- 条目 **%d**（有名 %d ｜ 无名 %d ｜ 未落实 %d）"
            % (len(self.rows), sum(1 for r in self.rows if r["named"]),
               sum(1 for r in self.rows if not r["named"]), len(self.unknown)),
            "- 定位：%s" % (locate or "—"),
        ]
        if packages:
            L += ["", "## 下发包", ""] + ["- `%s`" % x for x in packages]
        if extra:
            L += ["", extra]
        L += [
            "",
            "## 复现",
            "",
            "```bash",
            "cd E:/la拆包项目",
            'export PYTHONPATH="E:/la拆包项目/01_工具/工具库/00_共享核心"',
            'E:/la拆包项目/.venv/Scripts/python.exe "01_工具/工具库/00_共享核心/命令行/toolkit_cli.py" \\',
            '    hotfix bundle --out <本目录>',
            "```",
            "",
            "> ★ 本目录由 `toolkit_core/hotfix_bundle.py` 生成；`manifest.json` 是唯一真相源，",
            "> 各分类目录都从它派生。不编造：取不到名字的进 `%s`。" % D_UNKNOWN,
        ]
        p = self.out / "README.md"
        p.write_text("\n".join(L), encoding="utf-8")
        return p

    def write_unknown_list(self) -> Path:
        self.ensure_dirs()
        p = self.out / D_OTHER / O_MISC / "未归类清单.csv"
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["container", "row", "name", "ext", "size", "saved_as", "sha256", "note"])
            for r in self.unknown:
                w.writerow([r.get("container", ""), r.get("row", -1), r.get("name", ""),
                            r.get("ext", ""), r.get("size") or "", r.get("saved_as", ""),
                            r.get("sha256", ""), r.get("note", "")])
        return p

    # ── 文字表汇总 ──────────────────────────────────────────
    def write_text_tables(self, *, tables: Dict[str, List[str]] | None = None,
                          source_note: str = "") -> Path:
        """把文字表抽出的中文按表落盘。tables = {表路径: [文案...]}"""
        self.ensure_dirs()
        d = self.out / D_TEXT
        d.mkdir(parents=True, exist_ok=True)
        if not tables:
            (d / "说明.md").write_text(
                "# 文字表\n\n本次热更未涉及文字表变更。\n" if source_note == "" else
                "# 文字表\n\n%s\n" % source_note, encoding="utf-8")
            return d
        uniq = []
        for k in sorted(tables):
            uniq += tables[k]
        seen, out = set(), []
        for s in uniq:
            if s not in seen:
                seen.add(s)
                out.append(s)
        (d / "文案_去重.txt").write_text("\n".join(out), encoding="utf-8")
        with (d / "文案_按表.tsv").open("w", encoding="utf-8", newline="") as fh:
            for k in sorted(tables):
                for s in tables[k]:
                    fh.write("%s\t%s\n" % (k, s))
        (d / "索引.json").write_text(json.dumps(
            {"schema": "lifeafter-text-tables-v1", "n_tables": len(tables),
             "n_strings": sum(len(v) for v in tables.values()), "n_unique": len(out),
             "tables": {k: len(v) for k, v in sorted(tables.items())}},
            ensure_ascii=False, indent=1), encoding="utf-8")
        L = ["# 文字表汇总", "",
             "表 %d 个 ｜ 文案 %d 条 ｜ 去重 %d 条" % (len(tables), sum(len(v) for v in tables.values()), len(out)),
             ""]
        if source_note:
            L += [source_note, ""]
        for k in sorted(tables)[:200]:
            L.append("\n## %s（%d）\n" % (Path(k).name, len(tables[k])))
            L += ["- %s" % s for s in tables[k][:80]]
        (d / "分类.md").write_text("\n".join(L), encoding="utf-8")
        return d
