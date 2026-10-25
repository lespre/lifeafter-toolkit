# -*- coding: utf-8 -*-
"""检查缺男图的「衣服/头饰」卡：其 model 的图标组里到底有没有男图。"""
import collections
import json
import pathlib
import struct
import sys

PROJ = pathlib.Path("E:/la拆包项目")
WEB = PROJ / "02_wiki/web"
CD = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT  # noqa: E402

v = lambda x: x[1] if isinstance(x, tuple) else x


def main() -> int:
    raw = (CD / "fashion_data.py").read_bytes()
    at = raw.find(b"x{")
    L = int.from_bytes(raw[at + 2:at + 6], "little")
    body = raw[at + 6:at + 6 + L]
    cnt = struct.unpack_from("<I", body, 0)[0]
    blob = body[8 + 4 * cnt:]
    pool = BT.parse_legacy_chs_pool((CD / "fashion_data_chs.py").read_bytes())
    rows = BT.decode_table_rows(body, pool, resolve_jumps=False, lenient=True)[0]

    model_icons: dict[str, list[str]] = {}
    for r in rows:
        val = r["values"]
        mid = v(val.get("model_id"))
        ic = val.get("icons")
        if mid is None or not isinstance(ic, tuple):
            continue
        try:
            grp = BT.read_27_group(blob, int(str(ic[1]).split(":")[1]))
        except Exception:  # noqa: BLE001
            continue
        if grp:
            model_icons.setdefault(str(mid), [])
            for i in grp[1]:
                if i < len(pool):
                    nm = str(pool[i]).split("/")[-1]
                    if nm not in model_icons[str(mid)]:
                        model_icons[str(mid)].append(nm)

    d = json.loads((WEB / "data/boards/fashion_wardrobe.json").read_text(encoding="utf-8"))
    miss = []
    for it in d["items"]:
        imgs = [x for x in ((it.get("_media") or {}).get("images") or []) if isinstance(x, dict)]
        if not imgs or any("男" in str(x.get("label", "")) for x in imgs):
            continue
        part = str(it.get("part_label") or it.get("part") or "")
        if "衣服" in part or "头饰" in part:
            miss.append(it)

    print("衣服/头饰 缺男图 %d 张" % len(miss))
    c = collections.Counter()
    samples = []
    for it in miss:
        names = model_icons.get(str(it.get("model_id")), [])
        if not names:
            c["model 无图标组"] += 1
        elif len(names) == 1:
            c["组里只有 1 张图"] += 1
            if len(samples) < 6:
                samples.append((it["name"], names))
        else:
            c["组里有 %d 张图（含男图候选）" % len(names)] += 1
            if len(samples) < 10:
                samples.append((it["name"], names))
    for k, n in c.most_common():
        print("  ", k, n)
    print("样例:")
    for s in samples:
        print("   ", s[0], s[1])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
