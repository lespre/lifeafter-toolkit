#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""snapshot.py — 灰度快照（可回滚基线 + 条目指纹）

每两周围热更重建前，先给「将被改写的板」拍一张快照：
  * boards/<board>.json      —— 产物原件，供 --restore 回滚
  * fingerprints.json        —— 每板 {条目id: 内容指纹}，供 diff_boards.py 做条目级 diff
  * meta.json                —— 时间、git commit、规则层指纹、条目数

指纹只覆盖「用户可见字段」，刻意排除 provenance/时间戳一类每轮都会变的字段，
避免把无关噪声算成「条目变更」。

用法:
  python 02_wiki/web/tools/build/snapshot.py --boards vehicle_full,fashion_wardrobe
  python 02_wiki/web/tools/build/snapshot.py --boards all
  python 02_wiki/web/tools/build/snapshot.py --boards all --label before_20261030
  python 02_wiki/web/tools/build/snapshot.py --list
  python 02_wiki/web/tools/build/snapshot.py --restore 20261030_0900 --board vehicle_full
  python 02_wiki/web/tools/build/snapshot.py --prune --keep 20

退出码: 0 成功 / 1 参数或文件错误
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys

PROJ = pathlib.Path(__file__).resolve().parents[4]
WEB = PROJ / "02_wiki" / "web"
BOARDS = WEB / "data" / "boards"
RULES = PROJ / "02_wiki" / "rules"
STATE = PROJ / "02_wiki" / "state"
SNAP_DIR = STATE / "snapshots"

# 指纹时忽略的键：这些字段每次重建都可能变化，算进指纹会产生假差异。
# 规则层铁律：provenance 属于「证据元数据」，条目可见性判定看的是内容字段。
# ★ _prov_shape（2026-10-30）：溯源常量上提后写入的**形态签名**，
#   是「回退口径的定位信息」而非条目内容 ⇒ 必须忽略，
#   否则上提/紧凑化这类**纯格式**改动会让 G4 指纹全部变红。
IGNORE_KEYS = {"provenance", "source", "source_lock_sha256", "generated",
               "_media_updated_at", "icon_state", "icon_via", "icon_verified_by_gpk_loc0",
               "_prov_shape"}


def now_stamp() -> str:
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


def git_rev() -> str:
    try:
        r = subprocess.run(["git", "-C", str(PROJ), "rev-parse", "--short", "HEAD"],
                           capture_output=True, text=True, timeout=20)
        return r.stdout.strip() or "nogit"
    except Exception:
        return "nogit"


def canonical(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def item_fingerprint(item: dict) -> str:
    """条目内容指纹：排除 IGNORE_KEYS 后的规范 JSON 的 sha256 前 16 位。"""
    if not isinstance(item, dict):
        return hashlib.sha256(canonical(item).encode("utf-8")).hexdigest()[:16]
    keep = {k: v for k, v in item.items() if k not in IGNORE_KEYS}
    return hashlib.sha256(canonical(keep).encode("utf-8")).hexdigest()[:16]


def board_fingerprint(path: pathlib.Path) -> tuple[dict, int]:
    """返回 ({id: 指纹}, 条目数)。解析失败时抛异常由调用方处理。"""
    d = json.loads(path.read_text(encoding="utf-8-sig"))
    items = d.get("items") or []
    fp: dict[str, str] = {}
    for it in items:
        if not isinstance(it, dict):
            continue
        key = it.get("id")
        if key is None:
            continue
        fp[str(key)] = item_fingerprint(it)
    return fp, len(items)


def rules_fingerprint() -> dict:
    """规则层指纹：口径变了必须在 diff 里单独呈现，不能混进「数据变更」。"""
    out = {}
    if RULES.exists():
        for p in sorted(RULES.rglob("*.yml")):
            try:
                out[str(p.relative_to(RULES)).replace("\\", "/")] = \
                    hashlib.sha256(p.read_bytes()).hexdigest()[:16]
            except Exception:
                continue
    return out


def resolve_boards(spec: str) -> list[str]:
    stems = sorted(p.stem for p in BOARDS.glob("*.json"))
    if spec.strip().lower() == "all":
        return stems
    want = [s.strip() for s in spec.split(",") if s.strip()]
    unknown = [w for w in want if w not in stems]
    if unknown:
        raise SystemExit(f"❌ 未知板：{unknown}\n可用板见 --list-boards")
    return want


def cmd_snapshot(args) -> int:
    boards = resolve_boards(args.boards)
    label = args.label or now_stamp()
    out = SNAP_DIR / label
    if out.exists() and not args.force:
        raise SystemExit(f"❌ 快照已存在：{out}（换 --label 或加 --force）")
    (out / "boards").mkdir(parents=True, exist_ok=True)

    fingerprints: dict[str, dict] = {}
    counts: dict[str, int] = {}
    errors: list[str] = []
    copied = 0
    for b in boards:
        src = BOARDS / f"{b}.json"
        if not src.exists():
            errors.append(f"{b}: 产物不存在")
            continue
        try:
            fp, n = board_fingerprint(src)
        except Exception as e:
            errors.append(f"{b}: 指纹失败 {e}")
            continue
        fingerprints[b] = fp
        counts[b] = n
        if not args.fingerprint_only:
            shutil.copy2(src, out / "boards" / f"{b}.json")
            copied += 1

    meta = {
        "label": label,
        "created": datetime.datetime.now().isoformat(timespec="seconds"),
        "git_commit": git_rev(),
        "boards": sorted(fingerprints),
        "items": counts,
        "total_items": sum(counts.values()),
        "rules_fingerprint": rules_fingerprint(),
        "fingerprint_only": bool(args.fingerprint_only),
        "errors": errors,
    }
    (out / "fingerprints.json").write_text(
        json.dumps(fingerprints, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    (out / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"✅ 快照 {label}（git {meta['git_commit']}）")
    print(f"   板 {len(fingerprints)} 块 / 条目 {meta['total_items']} 条"
          f"{'（仅指纹，未拷产物）' if args.fingerprint_only else f' / 拷产物 {copied} 份'}")
    for e in errors:
        print(f"   ⚠️ {e}")
    print(f"   → {out}")
    return 0


def cmd_list(args) -> int:
    if not SNAP_DIR.exists():
        print("（无快照）")
        return 0
    rows = []
    for d in sorted(SNAP_DIR.iterdir()):
        mf = d / "meta.json"
        if not mf.exists():
            continue
        try:
            m = json.loads(mf.read_text(encoding="utf-8"))
        except Exception:
            continue
        rows.append((m.get("label") or d.name, m.get("created", ""), m.get("git_commit", ""),
                     len(m.get("boards") or []), m.get("total_items", 0),
                     "fp-only" if m.get("fingerprint_only") else "full"))
    if not rows:
        print("（无有效快照）")
        return 0
    print(f"{'标签':26s} {'时间':20s} {'git':10s} {'板':>4s} {'条目':>9s}  模式")
    print("-" * 86)
    for r in rows:
        print(f"{r[0][:26]:26s} {r[1][:20]:20s} {r[2][:10]:10s} {r[3]:>4d} {r[4]:>9d}  {r[5]}")
    return 0


def cmd_restore(args) -> int:
    label = args.snapshot
    src = SNAP_DIR / label / "boards"
    if not src.exists():
        raise SystemExit(f"❌ 快照没有产物副本（可能是 fingerprint-only）：{src}")
    boards = resolve_boards(args.board or "all")
    # 恢复前先给当前产物再拍一张，避免恢复动作本身不可逆
    if not args.no_backup:
        backup_label = f"pre_restore_{now_stamp()}"
        bak = SNAP_DIR / backup_label / "boards"
        bak.mkdir(parents=True, exist_ok=True)
        for b in boards:
            cur = BOARDS / f"{b}.json"
            if cur.exists():
                shutil.copy2(cur, bak / f"{b}.json")
        print(f"ℹ️ 恢复前已备份当前产物 → {SNAP_DIR / backup_label}")

    n = 0
    for b in boards:
        s = src / f"{b}.json"
        if not s.exists():
            print(f"   ⚠️ {b}: 快照中无此板，跳过")
            continue
        shutil.copy2(s, BOARDS / f"{b}.json")
        n += 1
        print(f"   ↩️ {b} 已恢复")
    print(f"✅ 恢复 {n} 块（快照 {label}）")
    print("   提醒：恢复产物后需重跑 build_wiki.py 让 manifest 与产物一致")
    return 0


def cmd_prune(args) -> int:
    if not SNAP_DIR.exists():
        return 0
    snaps = sorted([d for d in SNAP_DIR.iterdir()
                     if d.is_dir() and (d / "meta.json").exists()],
                    key=lambda d: d.name)
    keep = snaps[-args.keep:] if args.keep > 0 else []
    drop = [d for d in snaps if d not in keep]
    for d in drop:
        shutil.rmtree(d)
        print(f"   🗑️ {d.name}")
    print(f"✅ 保留 {len(keep)} 个快照，删除 {len(drop)} 个")
    return 0


def cmd_list_boards(args) -> int:
    for p in sorted(BOARDS.glob("*.json")):
        print(p.stem)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="灰度快照 / 回滚")
    ap.add_argument("--boards", help="逗号分隔板名，或 all")
    ap.add_argument("--label", help="快照标签（默认时间戳）")
    ap.add_argument("--fingerprint-only", action="store_true", help="只算指纹不拷产物")
    ap.add_argument("--force", action="store_true", help="覆盖同名快照")
    ap.add_argument("--list", action="store_true", help="列出快照")
    ap.add_argument("--list-boards", action="store_true", help="列出全部板名")
    ap.add_argument("--restore", help="从指定快照恢复")
    ap.add_argument("--board", help="--restore 时限定单板")
    ap.add_argument("--no-backup", action="store_true", help="恢复前不备份当前产物")
    ap.add_argument("--prune", action="store_true", help="清理旧快照")
    ap.add_argument("--keep", type=int, default=20, help="--prune 保留个数")
    args = ap.parse_args()

    if args.list:
        return cmd_list(args)
    if args.list_boards:
        return cmd_list_boards(args)
    if args.restore:
        return cmd_restore(args)
    if args.prune:
        return cmd_prune(args)
    if args.boards:
        return cmd_snapshot(args)
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
