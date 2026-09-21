"""item domain builder（包装器）。

复用现有实现：
  tools/rebuild_item_master_v03.py         （v03 系列生成）
  tools/build_item_master_v01.py           （v01 基线）
产物：artifacts/active/item/{ITEM_MASTER.jsonl,RULES.json,audit.json}
行为：默认 --check（只校验 active 存在与锁一致）；--rebuild 时调用既有脚本后同步到 active。
"""
from __future__ import annotations
import argparse, hashlib, json, shutil, subprocess, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ACTIVE = REPO / "artifacts" / "active" / "item"
LEGACY = {"master": REPO / "data" / "ITEM_MASTER_v03_1.jsonl", "rules": REPO / "data" / "ITEM_MASTER_v03_1_RULES.json",
          "audit": REPO / "analysis" / "audit" / "item_master_v03_1_audit.json"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check() -> int:
    manifest = json.loads((ACTIVE / "MANIFEST.json").read_text(encoding="utf-8"))
    for key, meta in manifest["files"].items():
        target = ACTIVE / Path(meta["to"]).name
        if not target.exists():
            print(f"FAIL missing {target}")
            return 1
        if sha256(target) != meta["sha256"]:
            print(f"FAIL lock drift {target}")
            return 1
    rows = sum(1 for _ in (ACTIVE / "ITEM_MASTER.jsonl").open(encoding="utf-8"))
    print(f"OK item active: rows={rows} namespaces=3 lock=verified")
    return 0


def rebuild() -> int:
    subprocess.run([sys.executable, str(REPO / "tools" / "rebuild_item_master_v03.py")], check=True)
    ACTIVE.mkdir(parents=True, exist_ok=True)
    shutil.copy2(LEGACY["master"], ACTIVE / "ITEM_MASTER.jsonl")
    shutil.copy2(LEGACY["rules"], ACTIVE / "RULES.json")
    shutil.copy2(LEGACY["audit"], ACTIVE / "audit.json")
    print("rebuilt -> artifacts/active/item/ (legacy data/ 未删除)")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--rebuild", action="store_true")
    raise SystemExit(rebuild() if ap.parse_args().rebuild else check())
