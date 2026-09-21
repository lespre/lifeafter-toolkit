"""weapon_skin domain builder（包装器）。"""
from __future__ import annotations
import argparse, hashlib, json, subprocess, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ACTIVE = REPO / "artifacts" / "active" / "weapon_skin"


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def check() -> int:
    man = json.loads((ACTIVE / "MANIFEST.json").read_text(encoding="utf-8"))
    for meta in man["files"].values():
        t = ACTIVE / Path(meta["to"]).name
        if sha256(t) != meta["sha256"]:
            print(f"FAIL {t}"); return 1
    rows = sum(1 for _ in (ACTIVE / "WEAPON_SKIN_RESOLVED.jsonl").open(encoding="utf-8"))
    print(f"OK weapon_skin active: rows={rows} lock=verified")
    return 0


def rebuild() -> int:
    subprocess.run([sys.executable, str(REPO / "tools" / "rebuild_weapon_skin_resolved_v01.py")], check=True)
    print("rebuilt via tools/rebuild_weapon_skin_resolved_v01.py")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--rebuild", action="store_true")
    raise SystemExit(rebuild() if ap.parse_args().rebuild else check())
