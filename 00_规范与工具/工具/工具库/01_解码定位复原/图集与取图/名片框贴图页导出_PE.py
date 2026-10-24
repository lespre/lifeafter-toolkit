# -*- coding: utf-8 -*-
"""从 PE 安卓包导出名片框 atlas 声明的贴图页 → PNG（与 atlas 同目录、用声明页名）。

只解目标行：非目标行不调用 decompress（跳过载荷），所以一个包只读一遍。
"""
import argparse, collections, pathlib, re, sqlite3, struct, sys

PROJ = pathlib.Path(r"E:/la拆包项目")
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core.path_fid import fids_for            # noqa: E402
from toolkit_core import android_gpk as G             # noqa: E402

DET = PROJ / "01_索引与产物/10_索引/热更检测"
PACKS = DET / "pe_packs"
IDX = DET / "pe_index.sqlite3"
CON = sqlite3.connect("file:%s?mode=ro" % str(IDX).replace("\\", "/"), uri=True, timeout=30)


def fid_lookup(path):
    for _spec, fid in fids_for(path):
        r = CON.execute("select pack,row,packed,decoded,flag from rows where fid=? limit 1",
                        ("%016X" % fid,)).fetchone()
        if r:
            return r
    return None


def pages(atlas):
    out = []
    for line in atlas.read_text(encoding="utf-8", errors="ignore").splitlines():
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


def declared_size(atlas):
    for line in atlas.read_text(encoding="utf-8", errors="ignore").splitlines()[:8]:
        m = re.match(r"size:\s*(\d+)\s*,\s*(\d+)", line.strip())
        if m:
            return int(m.group(1)), int(m.group(2))
    return None


def candidates(stem):
    v = [stem]
    m = re.match(r"^(.*)_(\d+)$", stem)
    if m:
        v.append(m.group(1))
    return v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=str(PROJ / "01_索引与产物/41_还原树/res/ui_02.gpk/ui/spine/mingpiankuang"))
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    d = pathlib.Path(a.dir)
    atlases = sorted(d.glob("*.atlas"))
    print("atlas %d 个" % len(atlases))

    plan = []           # (atlas, page, pack, row, size)
    miss = []
    seen = set()
    for at in atlases:
        sz = declared_size(at)
        for pg in pages(at):
            if pg in seen:
                continue
            seen.add(pg)
            hit = None
            for v in candidates(pg.rsplit(".", 1)[0]):
                for ext in (".ktx", ".png", ".dds"):
                    hit = fid_lookup("ui/spine/mingpiankuang/%s%s" % (v, ext))
                    if hit:
                        break
                if hit:
                    break
            if hit:
                plan.append((at, pg, hit[0], hit[1], sz))
            else:
                miss.append((at.name, pg))

    print("可导出 %d ｜ 包内无 %d" % (len(plan), len(miss)))
    by_pack = collections.defaultdict(list)
    for at, pg, pack, row, sz in plan:
        by_pack[pack].append((at, pg, row, sz))

    done, fail = [], []
    if not a.dry:
        from PIL import Image
        import numpy as np
        for pack, items in sorted(by_pack.items()):
            p = PACKS / pack
            if not p.is_file():
                fail += [(pg, "包缺失 " + pack) for _a, pg, _r, _s in items]
                continue
            rec, spans, factory = G.open_blocks(str(p))
            blob = p.read_bytes()
            want = {row: (at, pg, sz) for at, pg, row, sz in items}
            got = 0
            for row, fid, off, packed, decoded, flag in factory():
                if row not in want:
                    continue
                at, pg, sz = want[row]
                base = G._base_of(spans, row)
                h = base + off
                hp, hd, c1, c2, hf = struct.unpack_from("<5I", blob, h)
                if not (hp == packed and hd == decoded and hf == flag):
                    fail.append((pg, "行头自校验失败 row=%d" % row)); continue
                data = G.decompress(blob[h + 20:h + 20 + packed], flag, decoded)
                if data is None:
                    fail.append((pg, "解压失败 flag=%d" % flag)); continue
                try:
                    r = {"data": data, "kind": G.content_kind(data)}
                    if r["kind"] == "ktx":
                        r["info"] = G.parse_ktx(data)
                    rgba = G.decode_image(r)
                    im = Image.fromarray(rgba, "RGBA")
                    if sz and im.size != sz:
                        print("  ! 尺寸不符 %s 声明%s 实得%s" % (pg, sz, im.size))
                    out = d / pg
                    im.save(out)
                    got += 1
                    done.append((pg, pack, row, im.size, out.stat().st_size))
                except Exception as exc:      # noqa: BLE001
                    fail.append((pg, repr(exc)))
            print("  %s 导出 %d/%d" % (pack, got, len(items)))

    print("\n== 已导出 %d ==" % len(done))
    for pg, pack, row, size, nb in done:
        print("  %-28s %s row=%-6d %sx%s %d B" % (pg, pack, row, size[0], size[1], nb))
    print("== 失败 %d ==" % len(fail))
    for pg, why in fail:
        print("  ", pg, why)
    print("== 包内无（%d）==" % len(miss))
    for a_, pg in miss:
        print("  %-30s %s" % (a_, pg))


if __name__ == "__main__":
    main()
