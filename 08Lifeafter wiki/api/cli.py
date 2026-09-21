"""Workbench CLI —— 无 Wiki 也可独立使用（成功标准 12）。

用法（v1.3：列表命令全部支持分页/过滤）：
    python -m api.cli status | chains | namespaces | sources | coverage
    python -m api.cli item 150005
    python -m api.cli items --q 木头 --namespace common_item --page-size 20 --page 2 --sort name
    python -m api.cli entity item 150005
    python -m api.cli entity lottery_reward --pool-key 390000 --item-no 0
    python -m api.cli skins [--id 1110001] [--limit 20]
    python -m api.cli fashion
    python -m api.cli pools [--pool-key 390000] [--page-size 20] [--component base]
    python -m api.cli rewards --type unresolved --unresolved-only --page-size 20
    python -m api.cli residuals [--domain item]
    python -m api.cli evidence
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from services import (CoverageService, EntityService, FashionService, ItemService,  # noqa: E402
                      LotteryService, StatusService, WeaponSkinService)
from services.query import PAGE_SIZE_MAX  # noqa: E402
from services.store import RESIDUALS  # noqa: E402


def _out(payload) -> int:
    print(json.dumps(payload, ensure_ascii=False, indent=1)[:6000])
    return 0


def _paging(p) -> None:
    p.add_argument("--page", type=int, default=1)
    p.add_argument("--page-size", type=int, default=20)
    p.add_argument("--sort")
    p.add_argument("--desc", action="store_true")


def main() -> int:
    ap = argparse.ArgumentParser(prog="workbench")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("status", "chains", "namespaces", "sources", "coverage", "evidence"):
        sub.add_parser(name)
    p_item = sub.add_parser("item"); p_item.add_argument("item_id", type=int)
    p_entity = sub.add_parser("entity")
    p_entity.add_argument("kind", choices=["item", "weapon_skin", "lottery_pool", "lottery_reward"])
    p_entity.add_argument("ident", nargs="?")
    p_entity.add_argument("--pool-key", type=int); p_entity.add_argument("--item-no", type=int)
    p_items = sub.add_parser("items")
    p_items.add_argument("--q", default=""); p_items.add_argument("--namespace")
    p_items.add_argument("--name-status"); p_items.add_argument("--identity-status"); _paging(p_items)
    p_skin = sub.add_parser("skins"); p_skin.add_argument("--id", type=int); p_skin.add_argument("--limit", type=int, default=20)
    p_skin.add_argument("--listing-status"); p_skin.add_argument("--name-status"); p_skin.add_argument("--grade")
    p_skin.add_argument("--vocab", action="store_true"); _paging(p_skin)
    sub.add_parser("fashion")
    p_pool = sub.add_parser("pools"); p_pool.add_argument("--pool-key", type=int)
    p_pool.add_argument("--component"); p_pool.add_argument("--q", default=""); p_pool.add_argument("--stats", action="store_true"); _paging(p_pool)
    p_rew = sub.add_parser("rewards"); p_rew.add_argument("--pool-key", type=int); p_rew.add_argument("--type")
    p_rew.add_argument("--item-namespace"); p_rew.add_argument("--runtime-final-status")
    p_rew.add_argument("--unresolved-only", action="store_true"); p_rew.add_argument("--q", default="")
    p_rew.add_argument("--limit", type=int); _paging(p_rew)
    p_res = sub.add_parser("residuals"); p_res.add_argument("--domain")
    p_ex = sub.add_parser("explain", help="按 Locator Chain 逐跳解释（只读；断链即停）")
    p_ex.add_argument("kind", choices=["item", "weapon_skin", "belt_chip", "gift", "recipe", "fashion",
                                       "lottery_reward", "lottery_pool"])
    p_ex.add_argument("key"); p_ex.add_argument("key2", nargs="?"); p_ex.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.cmd == "status": return _out(StatusService().status())
    if args.cmd == "chains": return _out(StatusService().chains())
    if args.cmd == "namespaces": return _out(StatusService().namespaces())
    if args.cmd == "sources": return _out(StatusService().sources())
    if args.cmd == "coverage": return _out(CoverageService().coverage())
    if args.cmd == "item": return _out(ItemService().get_item(args.item_id) or {"error": "not found"})
    if args.cmd == "entity":
        row = EntityService().detail(args.kind, args.ident, pool_key=args.pool_key, item_no=args.item_no)
        return _out(row or {"error": "entity not found"})
    if args.cmd == "items":
        return _out(ItemService().page(q=args.q, namespace=args.namespace, name_status=args.name_status,
                                       identity_status=args.identity_status, sort=args.sort or "item_id",
                                       desc=args.desc, page=args.page, page_size=args.page_size))
    if args.cmd == "skins":
        svc = WeaponSkinService()
        if args.vocab:
            return _out(svc.status_vocab())
        if args.id:
            return _out(svc.get_skin(args.id) or {"error": "not found"})
        if args.listing_status or args.name_status or args.level or args.page != 1 or args.limit != 20:
            return _out(svc.skins_page(listing_status=args.listing_status, name_status=args.name_status,
                                       level=args.level, page=args.page,
                                       page_size=args.limit if args.limit != 20 else args.page_size,
                                       sort=args.sort or "skin_item_id", desc=args.desc))
        return _out(svc.list_skins(args.limit))
    if args.cmd == "fashion": return _out(FashionService().status())
    if args.cmd == "pools":
        svc = LotteryService()
        if args.stats or (args.pool_key is None and args.page == 1 and not args.component and not args.q and args.page_size == 20):
            if args.stats: return _out(svc.pool_stats())
        if args.pool_key is not None and args.page == 1 and not args.component and not args.q:
            return _out(svc.get_pool(args.pool_key))
        return _out(svc.pools_page(pool_key=args.pool_key, component=args.component, q=args.q,
                                   sort=args.sort or "pool_key", desc=args.desc,
                                   page=args.page, page_size=args.page_size))
    if args.cmd == "rewards":
        return _out(LotteryService().reward_targets_page(
            pool_key=args.pool_key, reward_target_type=args.type, item_namespace=args.item_namespace,
            runtime_final_status=args.runtime_final_status, unresolved_only=args.unresolved_only, q=args.q,
            sort=args.sort or "pool_key", desc=args.desc, page=args.page,
            page_size=args.limit or args.page_size))
    if args.cmd == "residuals":
        if args.domain:
            payload = {}
            for name in ("unresolved_namespace_ids", "binding_residuals", "unresolved_ids", "unresolved_targets", "replacement_overlay"):
                p = RESIDUALS / args.domain / f"{name}.json"
                if p.exists():
                    doc = json.loads(p.read_text(encoding="utf-8"))
                    payload[name] = {k: v for k, v in doc.items() if k not in ("ids", "per_id", "sample")}
            return _out(payload)
        return _out(StatusService().residual_manifest())
    if args.cmd == "evidence": return _out(StatusService().evidence_list())
    if args.cmd == "explain":
        from locator_chains.explain import explain, render
        doc = explain(args.kind, args.key, args.key2)
        if args.json:
            print(json.dumps(doc, ensure_ascii=False, indent=1))   # 不截断
            return 0 if not doc.get("error") else 1
        print(render(doc))
        return 0 if not doc.get("error") else 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
