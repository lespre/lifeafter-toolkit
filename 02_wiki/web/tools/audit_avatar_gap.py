# -*- coding: utf-8 -*-
"""对失败的 Spine 条目做「贴图页真实存在性」严格判定。

判定链（逐级收紧，杜绝误判）：
  1. +1 邻近 DDS 且宽高与 atlas 的 `size: W,H` **完全相等** → 候选
  2. 候选必须过**像素级校验**：把 DDS 解码成 RGBA，按 atlas 每个 region 的
     xy/size 去页图对应位置采样；若所有 region 的采样点全透明 → 配对错误
     （尺寸撞车导致误配，实测 touxiang_ani_17 会误取 _18 的贴图页）
  3. 通过 → 判「包内可取」（回源器未覆盖）
     不通过 → 判「实测缺失」（本包快照里确实没有该贴图页）
"""
from __future__ import annotations

import json
import pathlib
import struct
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ                                        # noqa: E402
sys.path.insert(0, str(PROJ / "02_wiki/web/tools"))
import avatar_resolve as AR                                       # noqa: E402
from toolkit_core import android_gpk as AG                        # noqa: E402

CAT = PROJ / "02_wiki/web/data/boards/avatar_catalog.json"
DIAG = PROJ / "01_索引与产物/30_分析/avatar_anim_render_report.json"
OUT = PROJ / "01_索引与产物/30_分析/avatar_anim_gap_audit.json"


def dds_wh(d: bytes):
    if not d or d[:4] != b"DDS ":
        return None
    h, w = struct.unpack("<II", d[12:20])
    return w, h


def parse_regions(t: str):
    """atlas 文本 → [(x,y,w,h,rotate)]。"""
    out = []
    cur = None
    for raw in t.splitlines():
        if not raw.strip():
            continue
        s = raw.strip()
        if not raw.startswith((" ", "\t")):
            cur = {"name": s}
            continue
        if cur is None:
            continue
        if s.startswith("xy:"):
            p = s[3:].split(",")
            cur["x"], cur["y"] = int(p[0]), int(p[1])
        elif s.startswith("size:"):
            p = s[5:].split(",")
            cur["w"], cur["h"] = int(p[0]), int(p[1])
        elif s.startswith("rotate:"):
            cur["rotate"] = s.split(":", 1)[1].strip() == "true"
        if "w" in cur and "h" in cur and "x" in cur and "y" in cur:
            out.append((cur["x"], cur["y"], cur["w"], cur["h"], cur.get("rotate", False)))
            cur = None
    return out


def atlas_meta(d: bytes):
    if not d or not d.startswith(b"\n"):
        return None
    t = d.decode("utf-8", "ignore")
    ls = [l.strip() for l in t.splitlines() if l.strip()]
    if not ls or not ls[0].lower().endswith((".png", ".jpg")):
        return None
    page = ls[0]
    wh = None
    for l in ls[1:6]:
        if l.lower().startswith("size:"):
            p = l.split(":", 1)[1].split(",")
            try:
                wh = (int(p[0]), int(p[1]))
            except (ValueError, IndexError):
                pass
            break
    return page, wh, parse_regions(t)


def pixel_ok(img, regions):
    """按 region 采样页图：任一 region 命中非透明像素即认为配对正确。"""
    import numpy as np
    W, H = img.size
    arr = np.asarray(img.convert("RGBA"))
    for (x, y, w, h, rot) in regions:
        if rot:
            x, y, w, h = x, y, h, w
        if x >= W or y >= H or w <= 0 or h <= 0:
            continue
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(W, x + w), min(H, y + h)
        if x1 <= x0 or y1 <= y0:
            continue
        sub = arr[y0:y1, x0:x1]
        if sub.size and float(sub[..., 3].max()) > 8:
            return True
    return False


class Packs:
    def __init__(self, res):
        self.res = res
        self._c = {}

    def entries(self, tag, pack):
        k = (tag, pack)
        if k not in self._c:
            p = self.res._pack_file(tag, pack)
            self._c[k] = list(AG.iter_entries(str(p))) if p and p.is_file() else []
        return self._c[k]

    def at(self, tag, pack, row):
        for e in self.entries(tag, pack):
            if e.get("row") == row:
                return e.get("payload") or b""
        return b""


def judge(it, res, packs):
    iid = it["id"]
    base = (it.get("spine_path") or "").strip().replace("\\", "/").rstrip("/")
    r = {"id": iid, "kind": it.get("kind"), "name": it.get("name"), "base": base,
         "page": None, "page_size": None, "verdict": "", "evidence": ""}
    hit = res.locate(base + ".atlas")
    if not hit:
        r["verdict"] = "atlas不可得"
        r["evidence"] = "PE/PC 索引与 PC 校准表三路均未收录 .atlas"
        return r
    tag, pack, row = hit
    meta = atlas_meta(packs.at(tag, pack, row))
    if meta is None:
        r["verdict"] = "atlas内容异常"
        r["evidence"] = "按索引行取回的载荷首字节不是 atlas 文本"
        return r
    page, wh, regions = meta
    r["page"] = page
    r["page_size"] = wh
    nxt = packs.at(tag, pack, row + 1)
    w2 = dds_wh(nxt)
    if not (w2 and wh and w2 == wh):
        k = "JSON" if nxt[:1] == b"{" else "其它"
        r["verdict"] = "实测缺失"
        r["evidence"] = ("%s:%s#%d 下一条目为 %s，非同尺寸 DDS（需 %sx%s）"
                         "→ 本包快照确无该贴图页"
                         % (tag, pack, row + 1, k, wh[0] if wh else "?", wh[1] if wh else "?"))
        return r
    try:
        img = res.image(tag, pack, row + 1)
    except Exception as ex:                                      # noqa: BLE001
        img = None
        r["evidence"] = "DDS 解码异常 %s" % str(ex)[:80]
    if img is None:
        r["verdict"] = "实测缺失"
        if r["evidence"]:
            r["evidence"] += "；"
        r["evidence"] += "候选 DDS 无法解码为位图"
        return r
    if pixel_ok(img, regions):
        r["verdict"] = "包内可取"
        r["evidence"] = ("%s:%s#%d 是 %dx%d DDS，尺寸与 atlas size 一致且 region "
                         "像素校验通过 → 回源器未覆盖，可直接取"
                         % (tag, pack, row + 1, w2[0], w2[1]))
    else:
        r["verdict"] = "实测缺失"
        r["evidence"] = ("%s:%s#%d 是 %dx%d DDS，尺寸撞车但 region 像素校验不通过"
                         "（该 DDS 属于别的 atlas）→ 本包快照确无该贴图页"
                         % (tag, pack, row + 1, w2[0], w2[1]))
    return r


def main():
    res = AR.Resolver()
    packs = Packs(res)
    cat = json.loads(CAT.read_text(encoding="utf-8"))
    by_id = {it["id"]: it for it in cat["items"]}
    failed = []
    if DIAG.is_file():
        d = json.loads(DIAG.read_text(encoding="utf-8"))
        failed = [r["id"] for r in d.get("records", []) if not r.get("ok")]
    if not failed:
        failed = [it["id"] for it in cat["items"] if (it.get("spine_path") or "").strip()]
    t0 = time.time()
    recs = []
    for n, iid in enumerate(failed, 1):
        it = by_id.get(iid)
        if not it:
            continue
        recs.append(judge(it, res, packs))
        if n % 15 == 0:
            print("  judge %d/%d %.0fs" % (n, len(failed), time.time() - t0), flush=True)
    import collections
    tally = collections.Counter(r["verdict"] for r in recs)
    by_kind = collections.Counter((r["kind"], r["verdict"]) for r in recs)
    payload = {"generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
               "scope": "诊断失败项", "total": len(recs),
               "verdict_breakdown": dict(tally),
               "by_kind_verdict": {"%s|%s" % k: v for k, v in by_kind.items()},
               "records": recs}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"total": len(recs), "verdict_breakdown": dict(tally),
                      "by_kind_verdict": payload["by_kind_verdict"]},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
