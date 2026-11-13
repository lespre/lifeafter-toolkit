# -*- coding: utf-8 -*-
"""build_related_boards.py — 生成「主表 → 专题板」关联入口配置

## 为什么（2026-11-13 用户口径）

用户要求把 11-12 热更的专题内容（宸世臻藏 / 神秘商店 / 甲虫无人机 / 新武器皮肤）
「补到」四块主表里。经核查，四块主表都是 `frozen-audited-artifact v3` 冻结产物，
源锁锁在旧包 `documents-py314-current`，专题板则是 11-12 实机包独立源锁
`pe-client-script-npk-20261112`。**直接并入条目会触发契约错**（实测每条 3 个：
`source_id` / `locator_chain.steps[0].source_id` / `source_lock_sha256`），
且主表构建脚本全量覆盖、手工合并下次重建即丢。

用户判定：**不放宽跨快照混源口径，主表冻结数据零改动，走关联入口**。
甲虫（战术无人机 270xxx）与 13 款新皮肤字段语义与目标主表不兼容，保持独立板。

于是本脚本只产出一份**只读的配置**：前端在四块主表页首渲染「相关专题」跳转区。
主表 `items` / `meta.provenance` / `source_locks` 一律不动 ⇒ 契约与幂等零风险。

## 可复算口径（全部由产物自身推得，不手填）

- 映射表 = 下方 `LINKS` 常量（用户 2026-11-13 逐项判定）。
- 每个目标专题板必须 `publication_status == "published"`，否则报错退出（不产出死链）。
- 板名 / 分类 / 条目数 / 一句话说明，实时读 `boards/<id>.json` 与 `publication_policy.json`。
- 独立展示页只在 `web/<page>.html` 真实存在时才写入；不存在则留空，不伪造。
- 输出不含时间戳 ⇒ 字节级幂等；内容未变则不写盘（默认 dry-run，`--apply` 落盘）。

用法：
    python 02_wiki/web/tools/build/build_related_boards.py            # dry-run
    python 02_wiki/web/tools/build/build_related_boards.py --apply    # 落盘
"""
from __future__ import annotations

import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
TOOLS = HERE.parent.parent
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(TOOLS / "build"))

from la_paths import WEB, DATA_DIR, BOARDS_DIR  # noqa: E402
from board_io import write_text  # noqa: E402

OUT_JSON = DATA_DIR / "related_boards.json"
OUT_JS = DATA_DIR / "related_boards.js"
POLICY = DATA_DIR / "publication_policy.json"

# 主表 → 关联专题板（用户 2026-11-13 口径：
#   宸世 + 神秘商店 → 1 活动总表 / 2 活动奖池；甲虫 → 无人机；新皮肤 → 武器皮肤）
LINKS: dict[str, list[str]] = {
    "activity_master": [
        "chenshi_zhencang_20261112",
        "shenmi_shangdian_20261112",
    ],
    "lottery_periods": [
        "chenshi_zhencang_20261112",
        "shenmi_shangdian_20261112",
    ],
    "drone_catalog": [
        "jiachong_wurenji_20261112",
    ],
    "weapon_skin_sfx_text_sources": [
        "weapon_skin_hotfix_20261112",
    ],
}

# 专题板 → 独立展示页（文件存在才写；缺省留空）
PAGES: dict[str, str] = {
    "chenshi_zhencang_20261112": "chenshi_zhencang.html",
    "shenmi_shangdian_20261112": "shenmi_shangdian.html",
    "jiachong_wurenji_20261112": "jiachong_wurenji.html",
    "weapon_skin_hotfix_20261112": "",
}

# 主表侧的说明文字（解释为什么主表里看不到 / 为什么走独立板）
HOST_NOTE: dict[str, str] = {
    "activity_master": "本表收录活动主记录（宸世臻藏主配置、神秘商店 35 期）。期次明细、规则与核查结论见右侧专题板。",
    "lottery_periods": "本表收录历史奖池与商品（宸世 969 条、神秘商店 1927 件）。11-12 实机包新解奖池、逐期概率与官方规则见右侧专题板。",
    "drone_catalog": "本表是机体无人机（drone_id 180000+）。战术无人机（270xxx，含独角仙/甲虫）是另一套 ID 体系，见右侧专题板，不混排。",
    "weapon_skin_sfx_text_sources": "本表是正式名图鉴（SFX 文本源基线）。11-12 热更新增 13 款皮肤用独立源锁，见右侧专题板，不并入本冻结基线。",
}

SCHEMA = "related-boards/v1"
README = (
    "主表与 11-12 专题板为不同客户端快照的独立源锁，按 frozen-audited-artifact v3 "
    "不做跨快照条目合并；此配置只提供页面级跳转入口，主表冻结数据零改动。"
)


def load_json(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build() -> dict:
    policy = load_json(POLICY)
    pb = policy.get("boards") or {}
    errors: list[str] = []

    # 主表自身也必须在 manifest/policy 里且已发布
    for host in LINKS:
        ent = pb.get(host)
        if not isinstance(ent, dict) or ent.get("publication_status") != "published":
            errors.append(f"主表未发布或缺失：{host}")

    boards_cache: dict[str, dict] = {}

    def board_of(bid: str) -> dict:
        if bid not in boards_cache:
            f = BOARDS_DIR / f"{bid}.json"
            if not f.exists():
                errors.append(f"板产物不存在：{f.name}")
                boards_cache[bid] = {}
            else:
                boards_cache[bid] = load_json(f)
        return boards_cache[bid]

    links: dict[str, list[dict]] = {}
    for host, targets in LINKS.items():
        rows: list[dict] = []
        for bid in targets:
            ent = pb.get(bid)
            if not isinstance(ent, dict) or ent.get("publication_status") != "published":
                errors.append(f"目标专题板未发布或缺失：{bid}")
                continue
            d = board_of(bid)
            meta = d.get("meta") or {}
            items = d.get("items") or []
            page = PAGES.get(bid, "")
            page_ok = bool(page) and (WEB / page).is_file()
            rows.append({
                "board": bid,
                "name": str(meta.get("name") or ent.get("name") or bid),
                "category": str(meta.get("category") or ent.get("category") or ""),
                "items": len(items),
                "reason": str(ent.get("reason") or "11-12 实机包独立源锁专题板"),
                "page": page if page_ok else "",
            })
        links[host] = rows

    if errors:
        raise SystemExit("关联配置校验失败：\n  - " + "\n  - ".join(errors))

    return {
        "schema": SCHEMA,
        "note": README,
        "hosts": {
            host: {"note": HOST_NOTE.get(host, ""), "links": rows}
            for host, rows in links.items()
        },
    }


def main() -> int:
    apply = "--apply" in sys.argv
    payload = build()
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    js = "window.WIKI_RELATED_BOARDS = " + text + ";\n"

    changed = []
    for path, new in ((OUT_JSON, text + "\n"), (OUT_JS, js)):
        old = path.read_text(encoding="utf-8") if path.exists() else None
        if old != new:
            changed.append(path.name)

    print(f"schema={SCHEMA} hosts={len(payload['hosts'])} "
          f"links={sum(len(v['links']) for v in payload['hosts'].values())}")
    for host, v in payload["hosts"].items():
        print(f"  {host} -> " + ", ".join(
            f"{r['board']}({r['items']})" for r in v["links"]))
    if not changed:
        print("字节级幂等：无变化，未写盘。")
        return 0
    if not apply:
        print(f"dry-run：将写入 {', '.join(changed)}（加 --apply 落盘）")
        return 0
    for path, new in ((OUT_JSON, text + "\n"), (OUT_JS, js)):
        if path.name in changed:
            write_text(path, new)
    print(f"已写入：{', '.join(changed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
