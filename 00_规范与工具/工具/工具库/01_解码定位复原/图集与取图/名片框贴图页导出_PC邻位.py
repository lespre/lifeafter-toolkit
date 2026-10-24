# -*- coding: utf-8 -*-
"""PC ui_02.gpk 邻位取页：atlas 行相邻的图片行 == 该 atlas 的贴图页。

判据（不猜）：① 行内 20B 头自校验通过；② 载荷是 DDS/KTX；③ 解码后的 (w,h) 与 atlas
`size:` 声明完全一致。三条全过才落盘，否则如实记 miss。
"""
import collections, json, pathlib, re, sqlite3, struct, sys

PROJ = pathlib.Path(r"E:/la拆包项目")
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core.path_fid import fids_for            # noqa: E402
from toolkit_core import android_gpk as G             # noqa: E402

WEB = PROJ / "02_wiki/web"
LIVE = WEB / "assets/spine_live"
DET = PROJ / "01_索引与产物/30_分析/热更检测"
TREE = PROJ / "01_索引与产物/41_还原树/res/ui_02.gpk"
GAME = pathlib.Path("E:/mrzh")
PC = sqlite3.connect("file:%s?mode=ro" % str(DET / "pc_index.sqlite3").replace("\\", "/"), uri=True, timeout=30)
PE = sqlite3.connect("file:%s?mode=ro" % str(DET / "pe_index.sqlite3").replace("\\", "/"), uri=True, timeout=30)


def fid_of_path(p):
    for _s, fid in fids_for(p):
        return "%016X" % fid
    return None


def pc_row(p):
    return PC.execute("select pack,row,decoded from rows where fid=? limit 1", (fid_of_path(p),)).fetchone()


def pages(at):
    out = []
    for line in at.read_text(encoding="utf-8", errors="ignore").splitlines():
        s = line.strip()
        if not s:
            if out:
                break
            continue
        if s.startswith(("size:", "format:", "filter:", "repeat:", "pma:")):
            break
        if s.lower().endswith((".png", ".jpg", ".ktx", ".webp")):
            out.append(s)
    return out


def dsize(at):
    for line in at.read_text(encoding="utf-8", errors="ignore").splitlines()[:8]:
        m = re.match(r"size:\s*(\d+)\s*,\s*(\d+)", line.strip())
        if m:
            return int(m.group(1)), int(m.group(2))
    return None


def decode_img(data):
    """DDS(DX10/DX9 fourCC) 或 KTX → (h,w,4) RGBA。不支持的格式抛异常。"""
    import numpy as np
    from PIL import Image
    import io
    import texture2ddecoder as t2d
    if data.startswith(bytes([0xAB]) + b"KTX"):
        info = G.parse_ktx(data)
        return G._ktx_rgba(data, info)
    if data.startswith(b"DDS "):
        h, w = struct.unpack_from("<II", data, 12)
        fourcc = struct.unpack_from("<I", data, 84)[0]
        src = data[128:]
        if struct.pack("<I", fourcc) == b"DX10":
            dxgi = struct.unpack_from("<I", data, 128)[0]
            src = data[148:]
            fn = {98: t2d.decode_bc7, 99: t2d.decode_bc7, 77: t2d.decode_bc3,
                  72: t2d.decode_bc3, 71: t2d.decode_bc1}.get(dxgi)
            if fn is None:
                raise ValueError("DXGI %d 未支持" % dxgi)
            raw = fn(src, w, h)
        elif struct.pack("<I", fourcc) == b"DXT5":
            raw = t2d.decode_bc3(src, w, h)
        elif struct.pack("<I", fourcc) == b"DXT1":
            raw = t2d.decode_bc1(src, w, h)
        else:
            raise ValueError("DDS fourCC 未支持 %r" % struct.pack("<I", fourcc))
        a = np.frombuffer(raw, np.uint8).reshape(h, w, 4)
        return a[..., [2, 1, 0, 3]]
    raise ValueError("未知图片格式 " + repr(data[:8]))


def load(pack, rows):
    """一次读一个包，只解目标行。"""
    p = GAME / "res" / pack
    if not p.is_file():
        return {}, "包缺失"
    rec, spans, factory = G.open_blocks(str(p))
    blob = p.read_bytes()
    out = {}
    for row, fid, off, packed, decoded, flag in factory():
        if row not in rows:
            continue
        h = G._base_of(spans, row) + off
        hp, hd, c1, c2, hf = struct.unpack_from("<5I", blob, h)
        if (hp, hd, hf) != (packed, decoded, flag):
            continue
        d = G.decompress(blob[h + 20:h + 20 + packed], flag, decoded)
        if d:
            out[row] = d
    return out, None


def main():
    rep = json.loads((WEB / "assets/avatar_frames_report.json").read_text(encoding="utf-8"))
    tasks = []                       # (bid, dir, page_name, atlas_stem, atlas_path)
    for bid, sp, why in rep["fail"]:
        d = LIVE / sp.rsplit("/", 1)[0]
        at = d / (sp.rsplit("/", 1)[-1] + ".atlas")
        if not at.is_file():
            print("skip 无 atlas:", sp)
            continue
        for pg in pages(at):
            if (d / pg).is_file() and (d / pg).stat().st_size > 1024:
                continue
            tasks.append((bid, sp.rsplit("/", 1)[0], pg, sp.rsplit("/", 1)[-1], at))
    print("待补页 %d（来自 %d 条失败项）" % (len(tasks), len(rep["fail"])))

    from PIL import Image
    import numpy as np
    done, miss = [], []
    per_pack = collections.defaultdict(list)   # pack -> [(row, dir, pg, size)]
    noddl = []
    for bid, dirp, pg, stem, at in tasks:
        r = pc_row(dirp + "/" + stem + ".atlas")
        if not r:
            noddl.append((bid, dirp, pg, "PC 索引无 atlas 行"))
            continue
        pack, arow, _dec = r
        sz = dsize(at)
        cands = []
        for delta in (1, 2, -1):
            rr = PC.execute("select row,decoded from rows where pack=? and row=? limit 1",
                            (pack, arow + delta)).fetchone()
            if rr and rr[1] and rr[1] > 100000:
                cands.append(rr[0])
        if not cands:
            miss.append((bid, dirp, pg, "相邻无图片行"))
            continue
        for row in cands:
            if any(x[0] == bid and x[2] == pg for x in done):
                break
            per_pack[pack].append((row, dirp, pg, sz, bid))

    print("邻位候选 %d 行 / %d 包" % (sum(len(v) for v in per_pack.values()), len(per_pack)))
    for pack, items in per_pack.items():
        rows = {r for r, *_ in items}
        payloads, err = load(pack, rows)
        if err:
            print("  ✗", pack, err)
            continue
        for row, dirp, pg, sz, bid in items:
            data = payloads.get(row)
            if not data:
                miss.append((bid, dirp, pg, "行取不到 row=%d" % row))
                continue
            try:
                im = Image.fromarray(decode_img(data), "RGBA")
            except Exception as exc:               # noqa: BLE001
                miss.append((bid, dirp, pg, "解码失败 " + repr(exc)[:60]))
                continue
            if sz and im.size != sz:
                miss.append((bid, dirp, pg, "尺寸不符 声明%s 实得%s row=%d" % (sz, im.size, row)))
                continue
            dst = LIVE / dirp / pg
            dst.parent.mkdir(parents=True, exist_ok=True)
            im.save(dst)
            tdir = TREE / dirp
            if tdir.is_dir():
                (tdir / pg).write_bytes(dst.read_bytes())
            done.append((bid, dirp, pg, im.size, f"{pack} row={row}"))

    print("\n== 补齐 %d ==" % len(done))
    for bid, dirp, pg, size, where in done:
        print("  %-12s %-34s %-28s %sx%s  %s" % (bid, dirp, pg, size[0], size[1], where))
    print("== 仍失败 %d ==" % len(miss))
    for bid, dirp, pg, why in miss:
        print("  ", bid, pg, "|", why)
    print("== 无 PC atlas 行 %d ==" % len(noddl))
    for bid, dirp, pg, why in noddl:
        print("  ", bid, pg, "|", why)


if __name__ == "__main__":
    main()
