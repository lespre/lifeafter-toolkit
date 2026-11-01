# -*- coding: utf-8 -*-
r"""从装备表（all_equips_data）补时装板挂饰/戒指等的魅力值与品级（幂等）。

## 为什么需要（2026-11-01 用户提问触发）

用户问「挂饰绝对有魅力值，你再想想看是不是别的表」—— **用户是对的，我先前说「源表没有」是错的**。

### 我先前错在哪

我只查了时装三表（`fashion_data` / `player_appear_data` / `player_module_appear_data`），
这三张表里的挂饰行**确实没有 `charm_value` 字段**：
- `player_appear_data` 的 pendant 行（part=5 / part_type=pendant，200 行）字段并集只有 14 个，
  **不含 charm_value**；
- `fashion_data` 里根本没有挂饰行（part=5 全是 light 荧光棒，903 行 charm 也全空）。

### 真正的来源：装备表 `all_equips_data`

挂饰/戒指在游戏里是**装备**（挂在身上），魅力值记在装备表：

| | |
|---|---|
| 表 | `all_equips_data`（经典服，3,237 行） |
| 载荷位置 | `03_执行/pe_all_equips_基线分片/all_equips_data__fid1F8E.py`（834 KB） |
| 字符池 | 同目录 `all_equips_data_chs__fid94AB.py`（1.2 MB） |
| 字段 | **800+ 个**，含 `charm_value` / `level` / `equip_type` / `icon` / `model_path` |
| 挂饰分类 | `equip_type == "0"`（355 行，其中 141 行有 charm_value） |
| 挂饰的 charm 分布 | 10×71 / 200×45 / 50×21 / 100×3 / 500×1 |

★ **为什么还原树里的表解不出来**：`01_索引与产物/41_还原树/pe/配置/com/cdata/all_equips_data.py`
只有 **808 字节的字节码壳**（表体缺失 —— 属于已知的 1,952 张缺口之一，导出时带了
"Translate Error"）。完整载荷在 `03_执行/pe_all_equips_基线分片/` 下。

### 关联方式

按**名字 + 装备类型**关联（不猜 id）：
- `player_appear_data` 的 pendant 行（100 个唯一名）→ 装备表 `equip_type=0` 同名行
  → **80/100 同名命中，其中 79 个有 charm_value**
- `player_appear_data` 的 part=6（戒指，10 个唯一名）→ 装备表同名行
  → **8/10 命中**，charm 10~100
- 板上 147 张挂饰卡 → **110 张能补上 charm_value**
- 板上 10 张戒指卡 → **8 张能补上**

★ 同一名字在装备表可能有多行（不同等级/时限），取 **charm 一致的那档**；
若多行 charm 不同则记 `equip_charm_candidates` 供核对（不擅自取 max）。

## 幂等

写入前先把旧键 pop 掉再按源表重算；同输入重跑字节不变。
`meta.notes` 走 `notes_util.append_note`（★ 一条 note 内部不能含分隔符 `" ｜ "`）。

用法：
    python 02_wiki/web/tools/fill_equip_charm.py --dry   # 只报统计
    python 02_wiki/web/tools/fill_equip_charm.py         # 写盘
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import struct
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402

sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))

from board_io import write_board_pair  # noqa: E402
import notes_util  # noqa: E402
from toolkit_core import bindict_table as BT  # noqa: E402

CD = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata"
# 装备表完整载荷（还原树里只有 808 字节的字节码壳，表体缺失）
AE_DIR = PROJ / "03_执行/pe_all_equips_基线分片"
AE_BODY = "all_equips_data__fid1F8E.py"
AE_POOL = "all_equips_data_chs__fid94AB.py"
BOARD = PROJ / "02_wiki/web/data/boards/fashion_wardrobe.json"

NOTE = ("装备表补齐：挂饰/戒指等的魅力值来自 all_equips_data（equip_type=0 装备类），"
        "按「名字 + 装备类型」关联 player_appear_data 的 pendant/part=6 行；"
        "板上挂饰 110 张、戒指 8 张补上 charm_value 与装备品级")


def load_legacy(cd: pathlib.Path, stem: str):
    raw = (cd / f"{stem}.py").read_bytes()
    at = raw.find(b"x{")
    ln = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6: at + 6 + ln]
    cnt = struct.unpack_from("<I", body, 0)[0]
    blob = body[8 + 4 * cnt:]
    pool = BT.parse_legacy_chs_pool((cd / f"{stem}_chs.py").read_bytes())
    return BT.decode_table_rows(body, pool, resolve_jumps=False, lenient=True)[0]


def load_equip_rows():
    """装备表完整载荷 → 行列表。"""
    raw = (AE_DIR / AE_BODY).read_bytes()
    at = raw.find(b"x{")
    ln = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6: at + 6 + ln]
    cnt = struct.unpack_from("<I", body, 0)[0]
    blob = body[8 + 4 * cnt:]
    pool = BT.parse_legacy_chs_pool((AE_DIR / AE_POOL).read_bytes())
    return BT.decode_table_rows(body, pool, resolve_jumps=False, lenient=True)[0]


def sv(x):
    return x[1] if isinstance(x, tuple) else x


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true", help="只报统计，不写盘")
    args = ap.parse_args()

    ae_rows = load_equip_rows()
    ap_rows = load_legacy(CD, "player_appear_data")

    # 装备表按名字索引（只取 equip_type=0 的时装类装备：挂饰/徽章/挂件/戒指）
    equip_by_name: dict[str, list[dict]] = collections.defaultdict(list)
    for r in ae_rows:
        if str(sv(r["values"].get("equip_type"))) != "0":
            continue
        d = r["values"]
        equip_by_name[str(sv(d.get("name")) or "")].append({
            "key": r["key"],
            "charm": sv(d.get("charm_value")),
            "level": sv(d.get("level")),
            "icon": sv(d.get("icon")),
            "model_path": sv(d.get("model_path")),
            "desc": sv(d.get("desc")),
        })

    board = json.loads(BOARD.read_text(encoding="utf-8"))
    stat = collections.Counter()

    for it in board["items"]:
        # 旧键清理
        for key in ("equip_charm", "equip_charm_source", "equip_level", "equip_charm_candidates"):
            it.pop(key, None)

        # ★ 防误配：只对「挂饰 / 戒指 / 半感染者花苞」三类生效。
        #   装备表 equip_type=0 里混着普通装备（休闲T / 墨绿棉帽…），
        #   它们与时装卡同名但不属时装体系 —— 按名字匹配会误伤衣服/头发桶（实测 46 张）。
        bucket = (it.get("part_bucket") or [""])[0]
        if bucket not in ("挂饰", "戒指", "半感染者花苞"):
            stat["skip_bucket"] += 1
            continue

        name = str(it.get("name") or "")
        rows = equip_by_name.get(name)
        if not rows:
            it["charm_note"] = ("魅力值未收录：该部位表无 charm_value，"
                                "且 all_equips_data 装备表里也无同名行")
            stat["no_equip_match"] += 1
            continue

        charms = sorted({r["charm"] for r in rows if r["charm"] is not None})
        if not charms:
            # 同名装备行存在但 charm 全空（例：心易俱乐部挂饰、旧世遗风会员之戒）
            it["charm_note"] = ("魅力值未收录：该部位表无 charm_value，"
                                "且 all_equips_data 装备表同名行也没有 charm_value")
            stat["equip_no_charm"] += 1
            continue

        if len(charms) == 1:
            charm = charms[0]
        else:
            # 同名多行 charm 不一致 → 不擅自取 max，列出候选等核对
            charm = charms[0]
            it["equip_charm_candidates"] = charms
            stat["charm_ambiguous"] += 1

        it["equip_charm"] = charm
        it.pop("charm_note", None)
        it["equip_charm_source"] = ("all_equips_data.charm_value（equip_type=0 装备行 %s，"
                                    "按名字关联）" % rows[0]["key"])
        stat["equip_charm_set"] += 1

        lv = next((r["level"] for r in rows if r["level"] is not None), None)
        if lv is not None:
            it["equip_level"] = lv
            stat["equip_level_set"] += 1

    print("装备表补齐统计：")
    for k, v in sorted(stat.items()):
        print("  %-22s %d" % (k, v))

    if args.dry:
        print("--dry：未写盘")
        return 0

    notes_util.append_note(board, NOTE)
    write_board_pair(BOARD, board)
    print("已写盘：%s" % BOARD)
    return 0


if __name__ == "__main__":
    sys.exit(main())
