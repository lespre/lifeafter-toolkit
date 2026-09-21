"""lottery domain builder（包装器，两层永久分层）。"""
from __future__ import annotations
import argparse, hashlib, json, subprocess, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ACTIVE = REPO / "artifacts" / "active" / "lottery"


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def check() -> int:
    man = json.loads((ACTIVE / "MANIFEST.json").read_text(encoding="utf-8"))
    for meta in man["files"].values():
        t = ACTIVE / Path(meta["to"]).name
        if sha256(t) != meta["sha256"]:
            print(f"FAIL {t}"); return 1
    pool = sum(1 for _ in (ACTIVE / "LOTTERY_POOL.jsonl").open(encoding="utf-8"))
    tgt = sum(1 for _ in (ACTIVE / "LOTTERY_REWARD_TARGETS.jsonl").open(encoding="utf-8"))
    print(f"OK lottery active: pool={pool} targets={tgt} layers=2 lock=verified")
    return 0


def rebuild() -> int:
    subprocess.run([sys.executable, str(REPO / "tools" / "build_lottery_pool_resolved_v01.py")], check=True)
    print("pool rebuilt；reward targets 层由 P4-D 分类工具生成（未纳入本 wrapper）")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--rebuild", action="store_true")
    raise SystemExit(rebuild() if ap.parse_args().rebuild else check())
