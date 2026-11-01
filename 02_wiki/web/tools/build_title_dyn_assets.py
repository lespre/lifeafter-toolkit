# -*- coding: utf-8 -*-
"""动态称号资源：从 csb 里取出动画首帧（步骤 1），后续可扩成完整逐帧。

数据链（全部可复核）：
  title_catalog item.anim_csb（来自 title_conf_data.shining_style → shining_title_conf_data.cocos_csb）
    → 定位 .csb：① row_path_map.db（PC 容器 res/ui_*.gpk、Documents/res/gres/*.gpk）按 fid 查 (container,row)
                  ② PE 包 pe_gres_android（头 32B 解密 + 表在 table_offset）
    → 读载荷（gpk 行 8×u32；载荷自 block_base(16)+offset+20，zstd/lz4 解压）
    → 扫描 csb 内 PNG/KTX 资源名（Cocos 场景里直接写着贴图路径）
    → img_fetch 导出（PE .ktx 优先，回落 PC .bc7），首帧缩到 ≤ 480px 宽
    → 回填 item.dyn_png / dyn_frames / dyn_csb_texture

方案2（整段动画，同一条数据链）：
  同一 csb 的全部帧贴图（按文件名末尾序号还原帧序）
    → 只取「主尺寸」那一组（同 csb 里尺寸不同的是叠加层，位置信息未解析）
    → 超过 40 帧按等距抽帧，140 宽、quality 55 合成循环动画 WebP
    → assets/title_dyn/anim/<csb名>.webp（同 csb 的称号共用一份）
    → 回填 item.dyn_webp / dyn_anim_frames / dyn_anim_ms（循环总时长按原帧数折算）

用法：
  python build_title_dyn_assets.py         # 首帧 + 整段动画
  python build_title_dyn_assets.py anim    # 只重做整段动画（不动首帧）
不猜：csb 取不到或贴图取不到就不填，前端只显示已有内容。
"""
from __future__ import annotations

import json
import pathlib
import re
import sqlite3
import struct
import sys

PROJ = pathlib.Path(__file__).resolve().parents[3]
WEB = PROJ / "02_wiki/web"
BOARD = WEB / "data/boards/title_catalog.json"
OUT_DIR = WEB / "assets/title_dyn"
ANIM_DIR = WEB / "assets/title_dyn/anim"

# 方案2（整段动画）参数：卡片里只显示 54px 高，140 宽已够；帧数上限控体积。
ANIM_W = 140
ANIM_Q = 55
ANIM_MAX_FRAMES = 40
ANIM_FRAME_MS = 40          # 源 csb 没写时长，按 25fps 估；循环总时长按原帧数折算
FRAME_CACHE = PROJ / "90_临时/_title_dyn_frame_cache"

CORE = PROJ / "00_规范与工具/工具/工具库/00_共享核心"
SCAN = PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/解包与扫描"
for p in (str(CORE), str(SCAN)):
    if p not in sys.path:
        sys.path.insert(0, str(p))

from toolkit_core import img_fetch as IF  # noqa: E402
from toolkit_core.path_fid import fid_of  # noqa: E402
from gpk_reader import aes_ecb  # noqa: E402
import la_unpack_core as UC  # noqa: E402

MRZH = pathlib.Path(r"E:\mrzh")
RPMAP = PROJ / "01_索引与产物/10_索引/indexes/row_path_map.db"
PE_IDX = PROJ / "01_索引与产物/10_索引/热更检测/pe_index.sqlite3"
PE_PACKS = PROJ / "01_索引与产物/源包/pe_gres_android"
IMG_RE = re.compile(rb"[ -~]{5,200}\.(?:png|ktx|jpg)", re.I)

# ── csb 定位 ────────────────────────────────────────────────
def locate_pc(csb_paths):
    """row_path_map.db：fid → (容器相对路径, 行号)。"""
    out = {}
    con = sqlite3.connect("file:%s?mode=ro" % RPMAP.as_posix(), uri=True)
    cur = con.cursor()
    for p in csb_paths:
        key = p if p.lower().endswith(".csb") else p + ".csb"
        r = cur.execute("select container,row_index from rows where fid_hex=? limit 1",
                        ("%016X" % fid_of(key),)).fetchone()
        if r:
            out[p] = r
    con.close()
    return out


def locate_pe(csb_paths):
    """PE gres 包：fid → (pack 文件名, 行号)。"""
    con = sqlite3.connect("file:%s?mode=ro" % PE_IDX.as_posix(), uri=True)
    cur = con.cursor()
    out = {}
    for p in csb_paths:
        key = p if p.lower().endswith(".csb") else p + ".csb"
        r = cur.execute("select pack,row from rows where fid=? limit 1",
                        ("%016X" % fid_of(key),)).fetchone()
        if r:
            out[p] = r
    con.close()
    return out


def gpk_row_bytes(path, row):
    """HPGF 行 → 解压后的载荷。格式见 gpk_npk_index.py 文档。"""
    with open(path, "rb") as f:
        head = aes_ecb(f.read(4096))
        n = struct.unpack_from("<I", head, 20)[0]
        f.seek(64)
        table = aes_ecb(f.read(n * 32))
    off, packed, decoded = struct.unpack_from("<III", table, row * 32)
    with open(path, "rb") as f:
        f.seek(16 + off + 20)
        raw = f.read(packed)
    if raw[:4] == b"\x28\xb5\x2f\xfd":
        return UC.decompress_zstd(raw, decoded or None)
    if raw[:2] == b"\x04\x22" or raw[:4] == b"\x04\x22\x4d\x18":
        try:
            return UC.decompress_lz4_block(raw, decoded, prefer_native=True)
        except Exception:
            return raw
    return raw


def csb_textures(raw):
    names = sorted({m.decode("utf-8", "ignore").replace("\\", "/") for m in IMG_RE.findall(raw)})
    return names


def pick_first(names):
    """逐帧取第一帧（文件名里带 00/01 序号时取最小）；单图原样返回。"""
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    def key(n):
        m = re.search(r"(\d{2,4})(?=\.[a-z]+$)", n, re.I)
        return (int(m.group(1)) if m else 1e9, n)
    return sorted(names, key=key)[0]


def export_png(tex, out):
    base = tex
    for ext in (".png", ".ktx", ".jpg"):
        if base.lower().endswith(ext):
            base = base[: -len(ext)]
            break
    for cand in (base, "ui/" + base):
        if IF.export(cand, out):
            return True
    return False


def alpha_bbox(im, pad=2):
    """贴图实际内容框（alpha 非零区域，外扩 pad 像素）。全透明返回 None。"""
    bb = im.getbbox()
    if not bb:
        return None
    x0, y0, x1, y1 = bb
    return (max(0, x0 - pad), max(0, y0 - pad),
            min(im.width, x1 + pad), min(im.height, y1 + pad))


def trim_frames(imgs):
    """按全帧「并集内容框」裁边：去掉画布四周的透明留白，同时保留帧间运动位移。
    游戏 csb 的画布普遍比实际光效大很多（如 480×404 里只有 208×120），
    不裁边、按 contain 铺进文字盒就会显得特别小。"""
    boxes = [alpha_bbox(im) for im in imgs]
    valid = [b for b in boxes if b]
    if not valid:
        return imgs
    x0 = min(b[0] for b in valid)
    y0 = min(b[1] for b in valid)
    x1 = max(b[2] for b in valid)
    y1 = max(b[3] for b in valid)
    if all((x1 - x0, y1 - y0) == im.size for im in imgs):
        return imgs
    return [im.crop((x0, y0, x1, y1)) for im in imgs]


def shrink(out, max_w=480):
    """裁掉透明留白后缩到 ≤ max_w，控制体积（只是预览，不改变资源内容）。"""
    try:
        from PIL import Image
        im = Image.open(out).convert("RGBA")
        bb = alpha_bbox(im)
        if bb:
            im = im.crop(bb)
        if im.width > max_w:
            im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
        im.save(out, "PNG", optimize=True)
    except Exception as e:
        print("  缩放失败（保留原图）:", out.name, e)


def save_board(board):
    txt = json.dumps(board, ensure_ascii=False, indent=1)
    BOARD.write_text(txt, encoding="utf-8")
    (WEB / "data/boards/title_catalog.js").write_text(
        "window.WIKI_BOARD_title_catalog = " + txt + ";", encoding="utf-8")


def load_csb_raws(csbs):
    """csb → 解压后的载荷（PC 容器与 PE 包各只读需要的行）。"""
    from toolkit_core import android_gpk as AG
    pc = locate_pc(csbs)
    pe = locate_pe(csbs)
    print("定位：PC %d，PE %d，合计 %d" % (len(pc), len(pe), len(set(pc) | set(pe))))
    payloads = {}
    by_cont = {}
    for p, (cont, row) in pc.items():
        by_cont.setdefault(cont, set()).add(row)
    for cont, rows in by_cont.items():
        fp = MRZH / cont
        if not fp.is_file():
            print("  容器缺失:", cont)
            continue
        try:
            # 块感知读取：gres 族一包多块，不能按「表在 64、载荷 16+off+20」的单块公式硬算
            for row, raw in read_pack_rows(fp, rows).items():
                payloads[("pc", cont, row)] = raw
        except Exception as e:
            print("  读取失败:", cont, e)
    if pe:
        by_pack = {}
        for p, (pack, row) in pe.items():
            by_pack.setdefault(pack, set()).add(row)
        for pack, rows in by_pack.items():
            fp = PE_PACKS / pack
            if not fp.is_file():
                print("  PE 包缺失:", pack)
                continue
            for row, raw in read_pack_rows(fp, rows).items():
                payloads[("pe", pack, row)] = raw
    out = {}
    for p in csbs:
        key = None
        if p in pc:
            key = ("pc",) + pc[p]
        elif p in pe:
            key = ("pe",) + pe[p]
        raw = payloads.get(key, b"") if key else b""
        if raw:
            names = csb_textures(raw)
            if names:
                out[p] = names
    return out


# ── 方案2：整段动画（多帧 csb → 动画 WebP） ─────────────────
PE_IDX = PROJ / "01_索引与产物/10_索引/热更检测/pe_index.sqlite3"
PC_IDX = PROJ / "01_索引与产物/10_索引/热更检测/pc_index.sqlite3"
# 底图贴图自带整字（叠美术字会重影）的 csb，实测确认后列在这里，写入 item.dyn_has_text。
BAKED_TEXT_CSB = {"ui/main_chenghao_jiamianqishi.csb"}
PC_ROOTS = (MRZH, MRZH / "res", MRZH / "Documents/gres")
TEX_EXT = (".ktx", ".png", ".bc7", ".dds", ".jpg")


def tex_stem(p):
    low = p.lower()
    for e in TEX_EXT:
        if low.endswith(e):
            return p[: -len(e)]
    return p


def seq_key(n):
    """帧贴图按文件名末尾序号排序（csb 里的节点名就是帧序）。"""
    m = re.search(r"(\d{2,4})(?=\.[a-z]+$)", n, re.I)
    return (int(m.group(1)) if m else 10 ** 9, n)


class TexResolver:
    """贴图名 → (源, 包, 行)；PE(.ktx) 优先，未命中回 PC(.bc7)。
    一次连接查完全部帧，不重复开库（img_fetch 逐张走会反复读 CSV/扫整包）。"""

    def __init__(self):
        self.cons = {"pe": sqlite3.connect("file:%s?mode=ro" % PE_IDX.as_posix(), uri=True),
                     "pc": sqlite3.connect("file:%s?mode=ro" % PC_IDX.as_posix(), uri=True)}
        self.cache = {}

    def resolve(self, tex):
        if tex in self.cache:
            return self.cache[tex]
        stem = tex_stem(tex)
        base = stem if stem.lower().startswith("ui/") else "ui/" + stem
        hit = None
        for src in ("pe", "pc"):
            cur = self.cons[src].cursor()
            for e in TEX_EXT:
                r = cur.execute("select pack,row from rows where fid=? limit 1",
                                ("%016X" % fid_of(base + e),)).fetchone()
                if r:
                    hit = (src, r[0], r[1])
                    break
            if hit:
                break
        self.cache[tex] = hit
        return hit

    def close(self):
        for c in self.cons.values():
            c.close()


def pack_file(src, pack):
    if src == "pe":
        p = PE_PACKS / pack
        return p if p.is_file() else None
    for root in PC_ROOTS:
        p = root / pack
        if p.is_file():
            return p
    return None


def read_pack_rows(path, rows):
    """块感知定向读取（HPGF 块链可能不止一块，不能写死 +36）。"""
    from toolkit_core import android_gpk as AG
    _rec, spans, factory = AG.open_blocks(str(path))
    base_of = {}
    for lo, hi, b in spans:
        for r in range(lo, hi):
            if r in rows:
                base_of[r] = b
    meta = {}
    for row, _fid, off, packed, decoded, flag in factory():
        if row in rows:
            meta[row] = (off, packed, decoded, flag)
    out = {}
    with open(path, "rb") as f:
        for row, (off, packed, decoded, flag) in meta.items():
            f.seek(base_of.get(row, 16) + off + 20)
            raw = f.read(packed)
            if flag == 12:
                raw = UC.decompress_zstd(raw, decoded or None)
            elif flag == 2:
                raw = UC.decompress_lz4_block(raw, decoded)
            out[row] = raw
    return out


def read_rows(path, rows):
    """一个容器的若干行 → 解压后载荷；.npk 走条目表，.gpk 走块链。"""
    if str(path).lower().endswith(".npk"):
        out = {}
        for r in rows:
            try:
                out[r] = UC.read_entry(str(path), entry_index=r)
            except Exception:                        # noqa: BLE001
                continue
        return out
    return read_pack_rows(path, rows)


# ── 全容器 fid 回退 ─────────────────────────────────────────
# 为什么需要：PC/PE 索引（pe_index/pc_index/row_path_map）没覆盖 gres 多块包、
# 部分热更 gpk 与 npk 层；但这些容器表里同样按 fid 存行。按候选 fid 只读表扫一遍
# （全量 294 个容器约 10 秒），就能把索引漏掉的贴图找回来，再按行号定向读载荷。
NPK_DIRS = (PROJ / "01_索引与产物/源包/pe_npk_full",
            PROJ / "01_索引与产物/源包/pe_ui_npk",
            PROJ / "01_索引与产物/源包/pe_npk_20261029")
SKIP_DIRS = ("sound", "video", "script", "model", "scene", "building", "character")


def _scan_container(path, cand_arr):
    """只读表 → [(行号, fid)]；支持 HPGF 块链 gpk 与 NXPK npk。"""
    import numpy as np
    from toolkit_core.resource_resolver import aes_ecb
    import os
    size = os.path.getsize(path)
    with open(path, "rb") as f:
        head = aes_ecb(f.read(48))
    if len(head) >= 24 and head[8:12] == b"NXPK":
        tab_off = struct.unpack_from("<I", head, 16)[0]
        cnt = struct.unpack_from("<I", head, 20)[0]
        if tab_off >= size or cnt > 4_000_000:
            return []
        with open(path, "rb") as f:
            f.seek(tab_off)
            tab = aes_ecb(f.read(cnt * 48))
        arr = np.frombuffer(tab, dtype="<u4").reshape(-1, 12)
        fids = arr[:, 0].astype(np.uint64) | (arr[:, 1].astype(np.uint64) << np.uint64(32))
        idx = np.nonzero(np.isin(fids, cand_arr))[0]
        return [(int(j), int(fids[j])) for j in idx.tolist()]
    # HPGF 块链：头 [12] = 块数；块 base 16，+48 起为 cnt×32 B 表，行 <8I>
    _zero, masked, two, nblocks = struct.unpack("<IIII", head[:16])
    if two != 2 or (masked ^ 0x46475049) != nblocks or not (0 < nblocks < 100_000):
        return []
    out, B, row0 = [], 16, 0
    with open(path, "rb") as f:
        for _k in range(nblocks):
            f.seek(B)
            bh = aes_ecb(f.read(48))
            if len(bh) < 48:
                break
            cnt, bsize = struct.unpack_from("<II", bh, 4)
            cnt -= 1
            if cnt < 0 or B + 48 + cnt * 32 > size:
                break
            f.seek(B + 48)
            tab = aes_ecb(f.read(cnt * 32))
            arr = np.frombuffer(tab, dtype="<u4").reshape(-1, 8)
            # 表里第 6/7 个 u32 = fid 的低/高 32 位（与探针 scan_tables 口径一致）
            fids = (arr[:, 7].astype(np.uint64) << np.uint64(32)) | arr[:, 6].astype(np.uint64)
            idx = np.nonzero(np.isin(fids, cand_arr))[0]
            for j in idx.tolist():
                out.append((row0 + j, int(fids[j])))
            row0 += cnt
            if bsize <= 0 or B + bsize > size:
                break
            B += bsize
    return out


def build_full_tex_map(names):
    """贴图名 → (容器文件, 行号)。先查 pe/pc 索引，未命中的再扫全部容器表。"""
    import numpy as np
    from toolkit_core.path_fid import fid_of
    cands = {}
    for n in names:
        stem = tex_stem(n)
        for pre in ("", "ui/"):
            base = stem if stem.lower().startswith("ui/") else pre + stem
            for e in TEX_EXT:
                cands["%016X" % fid_of(base + e)] = n
    containers = []
    for p in sorted(MRZH.rglob("*")):
        if p.suffix.lower() not in (".gpk", ".npk") or not p.is_file():
            continue
        rel = str(p.relative_to(MRZH)).replace("\\", "/")
        if any(k in rel for k in SKIP_DIRS):
            continue
        containers.append(p)
    for p in sorted(PE_PACKS.glob("*.gpk")):
        containers.append(p)
    for d in NPK_DIRS:
        if d.is_dir():
            containers.extend(sorted(d.glob("*.npk")))
    cand_arr = np.array([int(h, 16) for h in cands], dtype=np.uint64)
    found = {}
    for p in containers:
        try:
            hits = _scan_container(p, cand_arr)
        except Exception:                            # noqa: BLE001
            continue
        for row, fid in hits:
            h = "%016X" % fid
            if h not in found:
                found[h] = (p, row)
    out = {}
    for h, loc in found.items():
        name = cands[h]
        out.setdefault(name, loc)
    print("全容器回退：候选贴图名 %d，扫到容器 %d，命中 %d"
          % (len(names), len(containers), len(out)))
    return out


def decode_payload(pl):
    """载荷 → RGBA PIL 图；认不出返回 None。"""
    from PIL import Image
    from toolkit_core import android_gpk as AG
    if pl.startswith(b"CompBlks"):
        sys.path.insert(0, str(PROJ / "01_索引与产物/10_索引/热更检测/pe_icon_bind"))
        import decoders as DEC
        rgba = DEC.decode_compblks(pl)
    elif pl.startswith(b"\xabKTX"):
        rgba = AG.decode_image({"kind": "ktx", "data": pl, "info": AG.parse_ktx(pl)})
    elif pl.startswith(b"DDS "):
        import tempfile
        d = str(PROJ / "00_规范与工具/工具/工具库/02_图文音频渲染/皮肤链与渲染")
        if d not in sys.path:
            sys.path.insert(0, d)
        from dds_rgba_canonical import decode_dds_rgba_u8
        with tempfile.NamedTemporaryFile(suffix=".dds", delete=False) as f:
            f.write(pl)
            tmp = f.name
        try:
            rgba, _prov = decode_dds_rgba_u8(tmp, verify_oiio=False)
        finally:
            pathlib.Path(tmp).unlink(missing_ok=True)
    elif pl.startswith(b"\x89PNG"):
        rgba = AG.decode_image({"kind": "png", "data": pl})
    else:
        return None
    return Image.fromarray(rgba, "RGBA")


def csb_anim_name(csb):
    base = csb.replace("\\", "/").rsplit("/", 1)[-1]
    if base.lower().endswith(".csb"):
        base = base[:-4]
    return re.sub(r"[^0-9A-Za-z_.-]", "_", base) + ".webp"


def build_anims(board, full_map=None):
    """每个多帧 csb 合成一个循环动画 WebP（同 csb 的称号共用一份）。"""
    from PIL import Image
    full_map = full_map or {}
    items = board["items"]
    csbs = sorted({str(it["anim_csb"]) for it in items if it.get("anim_csb")})
    nf = load_csb_raws(csbs)
    multi = {p: n for p, n in nf.items() if len(n) >= 2}
    print("整段动画：多帧 csb %d / 有贴图 csb %d" % (len(multi), len(nf)))

    res = TexResolver()
    ANIM_DIR.mkdir(parents=True, exist_ok=True)
    made = {}
    ok = skip = 0
    for csb, names in sorted(multi.items()):
        order = sorted(names, key=seq_key)
        tex_hits = []
        rows_by_pack = {}
        for tex in order:
            hit = res.resolve(tex)
            if hit:
                src, pack, row = hit
                fp = pack_file(src, pack)
            elif tex in full_map:
                fp, row = full_map[tex]
            else:
                continue
            if not fp:
                continue
            tex_hits.append((fp, row))
            rows_by_pack.setdefault(fp, set()).add(row)
        payloads = {}
        for fp, rows in rows_by_pack.items():
            payloads.update({(fp, r): raw for r, raw in read_rows(fp, rows).items()})
        # 按贴图名里的序号还原帧序（不能按包内行号排，跨包会乱）
        imgs = []
        for fp, row in tex_hits:
            im = decode_payload(payloads.get((fp, row), b""))
            if im is not None:
                imgs.append(im)
        if len(imgs) < 2:
            skip += 1
            continue
        sizes = {}
        for im in imgs:
            sizes[im.size] = sizes.get(im.size, 0) + 1
        dom = max(sizes.items(), key=lambda kv: kv[1])[0]
        seq = [im for im in imgs if im.size == dom]
        if len(seq) < 2:
            skip += 1
            continue
        n_orig = len(seq)
        k = min(n_orig, ANIM_MAX_FRAMES)
        if k < n_orig:
            seq = [seq[round(i * (n_orig - 1) / (k - 1))] for i in range(k)]
        seq = trim_frames(seq)          # 去透明留白（并集框，保留帧间位移）
        dom = seq[0].size
        canvas = (ANIM_W, max(1, round(dom[1] * ANIM_W / dom[0])))
        frames = [im.resize(canvas, Image.LANCZOS) for im in seq]
        dur = max(20, round(ANIM_FRAME_MS * n_orig / len(frames)))
        dst = ANIM_DIR / csb_anim_name(csb)
        # method=6 体积略小但慢 40 倍（实测 19s vs 0.4s/40 帧），method=4 够用
        frames[0].save(dst, "WEBP", save_all=True, append_images=frames[1:],
                       duration=dur, loop=0, quality=ANIM_Q, method=4)
        made[csb] = ("assets/title_dyn/anim/" + dst.name, len(frames), dur, n_orig,
                     dst.stat().st_size)
        ok += 1

    for it in items:
        p = str(it.get("anim_csb") or "")
        hit = made.get(p)
        for k in ("dyn_webp", "dyn_anim_frames", "dyn_anim_ms"):
            it.pop(k, None)
        if hit:
            it["dyn_webp"], it["dyn_anim_frames"], it["dyn_anim_ms"], _n, _sz = hit
    total = sum(v[4] for v in made.values())
    print("生成动画 %d 个（跳过 %d），引用称号 %d 条，合计 %.1f MB"
          % (ok, skip, sum(1 for it in items if it.get("dyn_webp")), total / 1024 / 1024))
    res.close()
    return made


def main() -> int:
    board = json.loads(BOARD.read_text(encoding="utf-8"))
    items = board["items"]
    # 底图贴图本身已经把称号字画进去了（实测：1214 骑士集结 的 vx 贴图是「徽章+整字」合成图）。
    # 这类条目前端只显示底图，不再把美术字叠上去，否则会重影。其余条目的底图是纯光效/场景，
    # 美术字要叠在它上面（与游戏内一致）。
    for it in items:
        if str(it.get("anim_csb") or "") in BAKED_TEXT_CSB:
            it["dyn_has_text"] = True
        else:
            it.pop("dyn_has_text", None)
    csbs = sorted({str(it["anim_csb"]) for it in items if it.get("anim_csb")})
    print("动态条目 %d，唯一 csb %d" % (sum(1 for it in items if it.get("anim_csb")), len(csbs)))
    only_anim = "anim" in sys.argv[1:]

    if not only_anim:
        tex_of = load_csb_raws(csbs)
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        all_names = sorted({n for ns in tex_of.values() for n in ns})
        full_map = build_full_tex_map(all_names)
        ok = miss = 0
        pending = []
        for it in items:
            for k in ("dyn_png", "dyn_frames", "dyn_tex"):
                it.pop(k, None)
            p = str(it.get("anim_csb") or "")
            names = tex_of.get(p)
            if not names:
                continue
            first = pick_first(names)
            rel = "assets/title_dyn/ta_%s.png" % it["item_id"]
            if export_png(first, WEB / rel):
                shrink(WEB / rel)
                it["dyn_png"] = rel
                it["dyn_frames"] = len(names)
                it["dyn_tex"] = first
                ok += 1
            else:
                pending.append((it, names, rel))
        # 首帧不在索引里时，回退到全容器映射：按帧序逐张试，解出第一张可用的即停
        # （有些 csb 的帧序号不从 000 起，如 vx_chenghao_reli_004.bc7，所以不能只试前几张）
        item_plans = []
        for it, names, rel in pending:
            frames = [(n,) + full_map[n] for n in sorted(names, key=seq_key) if n in full_map]
            if frames:
                item_plans.append((it, rel, frames))
        for it, rel, frames in item_plans:
            rows_by_file = {}
            for _n, fp, row in frames:
                rows_by_file.setdefault(fp, set()).add(row)
            payloads = {}
            for fp, rows in rows_by_file.items():
                try:
                    payloads.update({(fp, r): raw for r, raw in read_rows(fp, rows).items()})
                except Exception as e:               # noqa: BLE001
                    print("  回退读取失败:", fp, e)
            for n, fp, row in frames:
                im = decode_payload(payloads.get((fp, row), b""))
                if im is None:
                    continue
                im.save(WEB / rel, "PNG", optimize=True)
                shrink(WEB / rel)
                it["dyn_png"] = rel
                it["dyn_frames"] = len(tex_of.get(str(it.get("anim_csb") or ""), []))
                it["dyn_tex"] = n
                ok += 1
                break
        miss = len(pending) - len(item_plans) + sum(
            1 for it, _r, _f in item_plans if not it.get("dyn_png"))
        for it, names, rel in pending:
            if not it.get("dyn_png"):
                print("  贴图未命中:", it["item_id"], it["name"], pick_first(names))
        print("首帧导出 %d / 未命中 %d（其中全容器回退补 %d）；总动态条目 %d"
              % (ok, miss, sum(1 for it, _r, _f in item_plans if it.get("dyn_png")),
                 sum(1 for it in items if it.get("anim_csb"))))
        build_anims(board, full_map)
    else:
        tex_of = load_csb_raws(csbs)
        build_anims(board, build_full_tex_map(sorted({n for ns in tex_of.values() for n in ns})))
    labels = board["meta"].setdefault("field_labels", {})
    labels.update({"dyn_png": "动态预览", "dyn_frames": "动画帧数",
                   "dyn_tex": "动画贴图（csb 内引用）",
                   "dyn_webp": "动态动画（逐帧合成）",
                   "dyn_anim_frames": "动画实际帧数（过长则抽帧）",
                   "dyn_anim_ms": "每帧时长（毫秒）"})
    save_board(board)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
