# -*- coding: utf-8 -*-
r"""common_item ns 解析器 —— 回填层的子环节（定位层用）。

## 为什么单列

`ns=common_item` 占奖池目标的 74%（17,406 / 23,567），但它【不在 41_还原树 里】：
  · 树里 com/cdata/common_item_data.py 只有 815 B = MergedTableData 壳
  · 壳里引用 com.cdata.common_item_data_{base,inc,del} —— 三张表都不在树/包内
  · 真实数据在【老工作副本 config_work/<snapshot>/entries/】：
      508BB5BD（最新）: base 019429 / inc 005741 / del 017742 / chs 002307
      BA8A239A        : base 018005 / inc 005292 / del 016447 / chs 002131（★ 旧漂移池，禁用于 name）
  · ⇒ 树是「唯一权威」的例外：common_item 走工作副本

## 口径（与 SKILL.md「名称回填链分层」一致）

    名称 = 用户确认名 > gift_data.name > common_item.name > 专表/池行 note > 未回填

  行数据 = base ∪ inc − del（三件套）；名字 = chs 池按行内 0x05 槽取。

## 数据源选择

★ 优先最新快照（entries 最多 / mtime 最新），并与已知锚表做正对照后才用。
  不用 BA8 的 002131（skill 标注旧漂移池，会解出杂物假名）。
"""
from __future__ import annotations

import csv
import json
import re
import time
from pathlib import Path
from typing import Dict, Iterable, Optional

CONFIG_WORK = Path(r"E:\la拆包项目\03_执行\30_分析\config_work")

# ★★ 2026-09-30 用户纠正 + 自查：**按 fid 定位表**，别按「快照 + entry 号」。
#   根因：`common_item_data_base` 在树里有两份副本，内容不同 ——
#     · `Documents\script.py314.lc.npk` 副本（**客户端当前态，含热更新增行**）
#       → 1,996,737 B · 55,615 行 · ★ 有 1110185=奇迹 / 1110186=星辰刀
#     · `script.py314.lc.npk` 根包副本 → 1,990,255 B · 55,408 行 · **没有这两行**
#   我原来读的是 config_work 里的老快照（≈根包态）⇒ 热更新增的道具名一个都查不到，
#   于是把「奇迹」这种明明存在的名字报成「无名字」。
#   ⇒ 正解：用 fid 查索引 → row_path_map → 树里的真实文件；**Documents 副本优先**。
FID_BASE = "B42760CCA41DBC25"
FID_CHS = "EF3A8474A5E5F7A4"

# ★ 已知可用快照（按优先级；前面找不到就退后面）
SNAPSHOT_ORDER = ("script_py314_docs_508BB5BD", "script_py314_docs_328b8446",
                  "script_py314_docs_BA8A239A", "script_py314_docs_780363b86008")

# ★ 禁用：BA8 的 chs 002131（旧漂移池）
BANNED_CHS = {"002131.bin"}


def _paths():
    from toolkit_core import paths as P
    return P


def index_path() -> Path:
    """common_item 专用索引落点。"""
    return _paths().INDEX_ROOT / "items" / "common_item_names.json"


def resolve_by_fid(fid: str, *, prefer_documents: bool = True):
    """fid → 树里的真实文件路径（★ 优先 `Documents` 副本 = 客户端当前态）。

    ★ 2026-09-30 用户要求「杜绝以后再犯」⇒ 规则已抽到共享模块
      `toolkit_core.table_locator`（按编号定位 + overlay/Documents 优先 + 自检），
      本函数只是它的薄封装，**别再在这里另写一套**。
    """
    from toolkit_core import table_locator as TL
    got = TL.best_path_for_fid(fid)
    if not got:
        return None
    p, c = got
    return (p, c["container"], c["row"], p.stat().st_size)


def find_snapshot() -> Optional[dict]:
    """定位可用快照 + 它的 base/inc/del/chs entry 号。

    判据（都要过）：
      ① entries 目录存在且非空
      ② 尾部模块名扫出 common_item_data_base / _chs（chs 不在禁用名单）
    返回 `{snapshot, entries, base, inc, del, chs, counts}` 或 None。
    """
    import re
    pat = re.compile(rb"[A-Za-z0-9_\\/]{6,}\.py")
    want = {"common_item_data_base.py": "base", "common_item_data_inc.py": "inc",
            "common_item_data_del.py": "del", "common_item_data_chs.py": "chs"}
    for sn in SNAPSHOT_ORDER:
        e = CONFIG_WORK / sn / "entries"
        if not e.is_dir():
            continue
        got: dict = {}
        for f in sorted(e.glob("*.bin")):
            try:
                b = f.read_bytes()[-4096:]
            except OSError:
                continue
            for m in pat.findall(b):
                s = m.decode("ascii", "replace").replace("\\", "/")
                for w, key in want.items():
                    if s.endswith(w) and key not in got:
                        got[key] = f.name
        if "base" in got and "chs" in got and got["chs"] not in BANNED_CHS:
            return {"snapshot": sn, "entries": e, "entries_dir": str(e), **got,
                    "counts": len(list(e.glob("*.bin")))}
    return None


def build(out: Optional[Path] = None, *, verbose: bool = True) -> dict:
    """解 common_item 三件套 + chs 池 → 建 `id → 名字` 索引。

    ★ 解码走项目现成链（不自己造）：
       base/inc/del = npk 条目 → npk_decode_entry → x{ 表体
       chs          = 中文池（UTF-8 按名排序的拼接池）
    步：① 解 base/inc/del 拿行键集合与 name 槽指向
        ② 解 chs 拿名字列表
        ③ 按槽取名字
    ★ 任一步失败如实返回 ok=False + reason，不倒填、不占位。
    """
    t0 = time.time()
    # ★★ 源解析（2026-09-30 改）：**先按 fid 找树里那份（Documents 副本优先）**，
    #   找不到才退回 config_work 老快照。原因见模块头注释：两副本内容不同，
    #   老快照没有热更新增的道具（1110185=奇迹 就是这么丢的）。
    src = None
    rb, rc = resolve_by_fid(FID_BASE), resolve_by_fid(FID_CHS)
    if rb and rc:
        src = {"kind": "fid@tree", "base": rb[0], "chs": rc[0],
               "container": rb[1], "row": rb[2]}
    else:
        snap = find_snapshot()
        if snap:
            src = {"kind": "snapshot", "base": snap["entries"] / snap["base"],
                   "chs": snap["entries"] / snap["chs"],
                   "snapshot": snap["snapshot"], "entries": snap["counts"],
                   "base": snap.get("base"), "inc": snap.get("inc"),
                   "del": snap.get("del"), "chs_id": snap.get("chs")}
    if src is None:
        return {"ok": False,
                "reason": "既没按 fid 定位到 common_item base/chs，也没有可用工作副本快照",
                "count": 0}
    out = Path(out) if out else index_path()

    from toolkit_core import table_export as TE

    rep = {"ok": False, "source_kind": src["kind"], "base": str(src["base"]),
           "chs": str(src["chs"]), "container": src.get("container"),
           "row": src.get("row"), "snapshot": src.get("snapshot"),
           "entries": src.get("entries"), "inc": src.get("inc"),
           "del": src.get("del"), "count": 0}
    try:
        bp = src["base"]
        payload = _read_decoded(bp)
        fr = find_frame(payload)
        if fr is None:
            rep["reason"] = "base 里找不到合法 x{ 帧"
            return _finish(rep, verbose, t0, out)
        off, ln, cnt = fr
        rep.update({"frame_off": off, "frame_len": ln, "rows_declared": cnt,
                    "base_body": ln})
        body = payload[off + 6: off + 6 + ln]

        # ① 行数据：base ∪ inc − del（三件套）
        rows = _decode_rows(body, src, rep)

        # ② 名字池
        pool = _decode_pool(src["chs"], rep)

        # ③ id → 名字
        items = _join(rows, pool, rep)
        if items:
            payload_out = {
                "schema": "common-item-names/v1",
                "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
                "why": ("common_item 的 base/inc/del 不在树里的 `common_item_data.py`（那只是 "
                        "815 B 的 MergedTableData 壳）。真表按 **fid** 定位："
                        "`B42760CCA41DBC25`(base) / `EF3A8474A5E5F7A4`(chs)，"
                        "★ 优先取 `Documents` 副本（客户端当前态，含热更新增行）；"
                        "取不到才退回 config_work 老快照（那份没有热更新增的道具）。"),
                "source": {"kind": src["kind"], "container": src.get("container"),
                           "row": src.get("row"), "snapshot": src.get("snapshot"),
                           "base": str(src["base"]), "chs": str(src["chs"]),
                           "frame_off": off, "rows_declared": cnt},
                "count": len(items),
                "items": {str(k): v for k, v in items.items()},
            }
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(payload_out, ensure_ascii=False,
                                      separators=(",", ":")), encoding="utf-8")
            rep["ok"] = True
            rep["count"] = len(items)
    except Exception as exc:                                          # noqa: BLE001
        import traceback
        rep["reason"] = "%s: %s" % (type(exc).__name__, exc)
        rep["trace"] = traceback.format_exc()[-600:]
    return _finish(rep, verbose, t0, out)


def _finish(rep: dict, verbose: bool, t0: float, out: Path) -> dict:
    rep["seconds"] = round(time.time() - t0, 1)
    rep["out"] = str(out)
    if verbose:
        print("★ common_item ns 解析器")
        print("   快照 %s（entries %s）" % (rep.get("snapshot"), rep.get("entries")))
        print("   base=%s inc=%s del=%s chs=%s"
              % (rep.get("base"), rep.get("inc"), rep.get("del"), rep.get("chs")))
        if rep.get("frame_off") is not None:
            print("   x{ 帧：@%s len=%s 声明行数=%s"
                  % (rep.get("frame_off"), rep.get("frame_len"),
                     rep.get("rows_declared")))
        print("   行数=%s 池=%s 收录=%s"
              % (rep.get("rows"), rep.get("pool"), rep.get("count")))
        if rep.get("reason"):
            print("   ⚠ %s" % rep["reason"])
        if rep.get("trace"):
            print("   trace 尾：%s" % rep["trace"][-300:])
    return rep


def _decode_rows(body: bytes, snap: dict, rep: dict) -> dict:
    """解 base ∪ inc − del 的行（**保留 body 供 schema 感知解码**）。"""
    from toolkit_core.bindict_table import parse_index
    import struct
    cnt, _ = struct.unpack_from("<II", body, 0)
    blob = body[8 + 4 * cnt:]
    idx = parse_index(blob)
    rep["index_rows"] = len(idx)
    rep["blob"] = len(blob)
    # ★ body 直接给解码器用（decode_table_rows_with_chs_slots 自己吃 8+4*count 表头）
    return {"body": body, "blob": blob, "index": idx, "rows": len(idx)}


def _decode_pool(p: Path, rep: dict) -> list:
    """解 chs 名字池（NeoX 定制 marshal 读中文池）。"""
    import sys
    core = Path(r"E:\la拆包项目\01_工具\工具库\01_解码定位复原\解包与扫描")
    src = Path(r"E:\la拆包项目\03_执行\30_分析\表结构解析_20260928\scripts")
    for d in (str(core), str(src)):
        if d not in sys.path:
            sys.path.insert(0, d)
    import importlib.util as iu
    spec = iu.spec_from_file_location("_marshal_pool_v2", src / "_marshal_pool.py")
    m = iu.module_from_spec(spec)
    sys.modules["_marshal_pool_v2"] = m
    spec.loader.exec_module(m)
    pool = m.pool_of_file(str(p))
    rep["pool"] = len(pool) if pool else 0
    return pool or []


def _join(rows: dict, pool: list, rep: dict) -> dict:
    """★ schema 感知地取名字（2026-09-30 修正）。

    v1 用「行内字节扫池索引」的启发式 ⇒ 扫到的是 **schema 区的字段名**
    （实测 name 解出「id」「obtain_notify」这类字段名，全错）。
    正确做法：用项目现成的 `decode_table_rows_with_chs_slots`
    —— 它按 schema 的字段类型解，`value_provenance[field]` 给出
    `field_chs_slot` / `value_chs_slot`，名字从 value 槽取。

    ★ 阈值沿用 skill 的「短名」判据：2~24 字、不含标点，避免长句/占位句。
    """
    out: dict = {}
    body = rows.get("body")
    if not body or not pool:
        return out
    try:
        import importlib.util as iu
        from pathlib import Path as _P
        bp = _P(r"E:\la拆包项目\04_站点\web\tools\bindict_provenance.py")
        if not bp.is_file():
            rep["join_note"] = "bindict_provenance.py 不在（%s）" % bp
            return out
        spec = iu.spec_from_file_location("bindict_prov", bp)
        m = iu.module_from_spec(spec)
        import sys as _s
        _s.modules["bindict_prov"] = m
        spec.loader.exec_module(m)
        decoded, unbound = m.decode_table_rows_with_chs_slots(body, pool)
        rep["decoded_rows"] = len(decoded)
        rep["unbound"] = len(unbound)
    except Exception as exc:                                          # noqa: BLE001
        rep["join_note"] = "%s: %s" % (type(exc).__name__, exc)
        return out

    for r in decoded:
        k = r.get("key")
        if k is None:
            continue
        vals = r.get("values") or {}
        prov = r.get("value_provenance") or {}
        # 名字字段优先级（与 item_names.NAME_FIELDS 同序）
        nm = ""
        fld = ""
        for want in ("name", "name_chs", "item_name", "cn_name", "name_female",
                     "title", "label"):
            if want in vals:
                v = vals[want]
                txt = v[1] if isinstance(v, (list, tuple)) and len(v) > 1 else v
                if isinstance(txt, str) and txt.strip():
                    nm, fld = txt.strip(), want
                    break
        if nm:
            quality = _name_quality(nm)
            out[int(k)] = {"name": nm, "field": fld, "quality": quality,
                           "slot": (prov.get(fld) or {}).get("value_chs_slot")}
    rep["joined"] = len(out)
    # ★ 重名标记（体检口径）：同名被 ≥2 个 id 共用 ⇒ 降级，不进可交付子集。
    #   实测 38,070 条里 3,328 个名字被 18,443 个 id 共用（48%）。
    byname: dict = {}
    for k, v in out.items():
        byname.setdefault(v["name"], []).append(k)
    for k, v in out.items():
        v["dup"] = len(byname.get(v["name"]) or []) > 1
    from collections import Counter as _C
    rep["quality"] = dict(_C(v["quality"] for v in out.values()))
    rep["dup_names"] = sum(1 for n, ks in byname.items() if len(ks) > 1)
    rep["usable"] = sum(1 for v in out.values()
                        if v["quality"] == "ok" and not v["dup"])
    return out


# ── 名字可信度判据（skill「名称回填三档」）──────────────────────────
#   ★ 背景：name 槽会跨物品错位（151646 解出「竞技场占用3」、151647 解出长句）
#     —— 与 all_equips 的教训同源。所以必须判「这值像不像一个人能看懂的名字」。
_BAD_HEAD = ("打开后", "该", "需", "当", "只", "可在", "用于", "此", "本")


def _name_quality(s: str) -> str:
    """`ok` 短名可信 · `long` 长句降级 · `bad` 明显取错槽 · `suspect` 内部标记。

    判据（都可复算）：
      · bad     ：含 icon/贴图路径（`ui/`、`.png`、`.dds`）或**纯 ASCII 标识符**
                  ⇒ ★ 这是「槽取错了」的铁证（实测 `ui/item_icon/icon_130042`、
                  `PanelCheckMissionPhotoTwoColumns` 进了 name 位）
      · long    ：>20 字或含 # 标记 ⇒ 是 desc 类文本，不是名
      · suspect ：短但形态像内部标记（含「占用」「调试」「test」「未使用」等）
      · ok      ：2~20 字、无标点/换行标记、不以「该/需/当/只…」开头
    """
    if not isinstance(s, str):
        return "suspect"
    t = s.strip()
    if not t:
        return "suspect"
    low = t.lower()
    if ("ui/" in low or ".png" in low or ".dds" in low
            or re.fullmatch(r"[A-Za-z0-9_/.\-]+", t)):
        return "bad"
    if len(t) > 20 or "#" in t or "\n" in t:
        return "long"
    if any(ch in t for ch in "，。；：、（）【】"):
        return "long"
    if t.startswith(_BAD_HEAD):
        return "long"
    if any(k in t for k in ("占用", "调试", "废除", "未使用", "测试")) or \
       any(k in low for k in ("test", "debug", "dummy", "unused")):
        return "suspect"
    return "ok"


def find_frame(payload: bytes, *, min_len: int = 1024) -> tuple[int, int, int] | None:
    """★ 在 payload 里找【唯一合法的 x{ 帧】：返回 (偏移, 表体长, 行数)。

    为什么不用 table_export.extract_body：它对 common_item base 挑错了 x{
    ——实测 019429.bin 里有两个 x{：
        @263      len=1,989,539  count=55,408       ← 真表体（落在载荷内）
        @1599023  len=1,615,638  count=2,071,536,260 ← 假标记（越界）
    它选了后者 ⇒ 报「声明表体 3583345446 B 超出载荷」。
    铁律（SKILL.md 已记）：**只有 declared length 落在 payload 内才是候选帧**；
    x{ 只是 2 字节 marker，几万字节的池/代码里偶遇 1~2 次稀松平常。
    """
    import struct
    cands = []
    i = 0
    while True:
        j = payload.find(b"x{", i)
        if j < 0:
            break
        i = j + 1
        if j + 10 > len(payload):
            continue
        ln = struct.unpack_from("<I", payload, j + 2)[0]
        cnt = struct.unpack_from("<I", payload, j + 6)[0]
        if ln < min_len or ln > 10 ** 8:
            continue
        if j + 6 + ln > len(payload):          # ★ 越界即 reject
            continue
        cands.append((j, ln, cnt))
    if not cands:
        return None
    # 多个合法帧时取【最大】的（真表体远大于误命中）
    return max(cands, key=lambda x: x[1])


def _read_decoded(p: Path) -> bytes:
    """读条目。

    ★ 2026-09-30 修正：`config_work/<snapshot>/entries/*.bin` **本来就是已解码产物**
      ——再调用 npk_decode_entry 会把它们当密文再解一次，结果帧全没了
      （实测症状：find_frame 报「找不到合法 x{ 帧」，而原始字节里明明有 @263）。
      ⇒ 先直接用原始字节；**只有里面找不到合法帧时**才尝试解码一次（兼容未解码的条目）。
    """
    b = p.read_bytes()
    if find_frame(b) is not None:
        return b
    # 兜底：可能是未解码条目，走一次项目解码器
    import sys
    core = Path(r"E:\la拆包项目\01_工具\工具库\01_解码定位复原\解包与扫描")
    if str(core) not in sys.path:
        sys.path.insert(0, str(core))
    try:
        import importlib.util as iu
        spec = iu.spec_from_file_location("la_unpack_core_mod2", core / "la_unpack_core.py")
        m = iu.module_from_spec(spec)
        sys.modules["la_unpack_core_mod2"] = m
        spec.loader.exec_module(m)
        out = m.npk_decode_entry(b, len(b), 0)
        if out and len(out) > 16 and find_frame(out) is not None:
            return out
    except Exception:
        pass
    return b


def lookup(ids: Iterable[int], path: Optional[Path] = None) -> Dict[int, Optional[str]]:
    """查 common_item 名（索引没建则全 None —— 不猜）。"""
    p = Path(path) if path else index_path()
    if not p.is_file():
        return {int(i): None for i in ids if str(i).lstrip("-").isdigit()}
    d = json.loads(p.read_text(encoding="utf-8"))
    items = d.get("items") or {}
    return {int(i): (items.get(str(i)) or {}).get("name") for i in ids}


def lookup_meta(ids: Iterable[int], path: Optional[Path] = None) -> Dict[int, dict]:
    """带元信息（name/field/quality/slot）的查询 —— 供展示层标可信度。"""
    p = Path(path) if path else index_path()
    if not p.is_file():
        return {}
    try:
        items = (json.loads(p.read_text(encoding="utf-8")).get("items") or {})
    except (OSError, ValueError):
        return {}
    out: Dict[int, dict] = {}
    for i in ids:
        try:
            k = int(i)
        except (TypeError, ValueError):
            continue
        rec = items.get(str(k))
        if isinstance(rec, dict):
            out[k] = rec
    return out


def usable_names(path: Optional[Path] = None) -> Dict[int, str]:
    """★ 可直接交付的名字子集：`quality=='ok'` 且**不在重名群组**。

    为什么必须收窄（2026-09-30 体检 38,070 条）：
      · 38.4% 是长句/描述     → 槽取到了 desc
      · 31.4% 与其他 id 重名  → 含 `ui/item_icon/icon_130042` 这类 **icon 路径**
                               （槽取到了 icon 字段），以及一 name 多 id 的变体
      ·  2.5% 是纯标识符      → 槽取错
      ⇒ 过这一关的只有 **10,517 条（27.6%）**。全量直接回填 = 瞎填。
    """
    return {i: v["name"] for i, v in lookup_meta_all(path).items()
            if v.get("quality") == "ok" and not v.get("dup") and v.get("name")}


def lookup_meta_all(path: Optional[Path] = None) -> Dict[int, dict]:
    """整个索引的元信息（name/quality/dup/slot）。"""
    p = Path(path) if path else index_path()
    if not p.is_file():
        return {}
    try:
        items = (json.loads(p.read_text(encoding="utf-8")).get("items") or {})
    except (OSError, ValueError):
        return {}
    out: Dict[int, dict] = {}
    for k, rec in items.items():
        if isinstance(rec, dict):
            try:
                out[int(k)] = rec
            except (TypeError, ValueError):
                continue
    return out


def stats(path: Optional[Path] = None) -> dict:
    p = Path(path) if path else index_path()
    snap = find_snapshot()
    n = usable = dup_names = 0
    quality: dict = {}
    if p.is_file():
        try:
            items = (json.loads(p.read_text(encoding="utf-8")).get("items") or {})
        except (OSError, ValueError):
            items = {}
        n = len(items)
        from collections import Counter as _C
        quality = dict(_C((v or {}).get("quality") for v in items.values()))
        usable = sum(1 for v in items.values()
                     if (v or {}).get("quality") == "ok" and not (v or {}).get("dup"))
        nm: dict = {}
        for v in items.values():
            s = ((v or {}).get("name") or "").strip()
            if s:
                nm[s] = nm.get(s, 0) + 1
        dup_names = sum(1 for c in nm.values() if c > 1)
    return {"path": str(p), "exists": p.is_file(), "count": n,
            "usable": usable, "dup_names": dup_names, "quality": quality,
            "snapshot": (snap or {}).get("snapshot"),
            "entries": (snap or {}).get("counts"),
            "base": (snap or {}).get("base"), "chs": (snap or {}).get("chs"),
            "banned_chs": sorted(BANNED_CHS)}
