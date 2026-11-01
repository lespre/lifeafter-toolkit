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


def shrink(out, max_w=480):
    """缩到 ≤ max_w，控制体积（只是预览，不改变资源内容）。"""
    try:
        from PIL import Image
        im = Image.open(out)
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
        for row in rows:
            try:
                payloads[("pc", cont, row)] = gpk_row_bytes(fp, row)
            except Exception as e:
                print("  读取失败:", cont, row, e)
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


def build_anims(board):
    """每个多帧 csb 合成一个循环动画 WebP（同 csb 的称号共用一份）。"""
    from PIL import Image
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
            if not hit:
                continue
            src, pack, row = hit
            fp = pack_file(src, pack)
            if not fp:
                continue
            tex_hits.append((fp, row))
            rows_by_pack.setdefault(fp, set()).add(row)
        payloads = {}
        for fp, rows in rows_by_pack.items():
            payloads.update({(fp, r): raw for r, raw in read_pack_rows(fp, rows).items()})
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
    csbs = sorted({str(it["anim_csb"]) for it in items if it.get("anim_csb")})
    print("动态条目 %d，唯一 csb %d" % (sum(1 for it in items if it.get("anim_csb")), len(csbs)))
    only_anim = "anim" in sys.argv[1:]

    if not only_anim:
        tex_of = load_csb_raws(csbs)
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        ok = miss = 0
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
                miss += 1
                print("  贴图未命中:", it["item_id"], it["name"], first)
        print("首帧导出 %d / 未命中 %d；总动态条目 %d"
              % (ok, miss, sum(1 for it in items if it.get("anim_csb"))))

    build_anims(board)
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
