#!/usr/bin/env python3
"""Build the browser-readable weapon-skin 3D index from viewer.json files."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODEL_ROOT = ROOT / "assets" / "3d" / "weapon_skin"
OUTPUT_DIR = ROOT / "data" / "media"


def validate_config(path: Path, config: dict) -> None:
    skin_id = str(config.get("skin_id") or path.parent.name)
    states = config.get("states") or []
    if not isinstance(states, list) or not states:
        raise ValueError(f"{skin_id}: states 必须是非空数组")
    for state in states:
        model = state.get("model") if isinstance(state, dict) else None
        if not model:
            raise ValueError(f"{skin_id}: 每个形态都必须填写 model")
        if not (path.parent / model).is_file():
            raise FileNotFoundError(f"{skin_id}: 找不到模型 {model}")


def build() -> dict:
    skins = {}
    for path in sorted(MODEL_ROOT.glob("*/viewer.json")):
        if path.parent.name.startswith("_"):
            continue
        config = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(config, dict):
            raise ValueError(f"{path}: 根节点必须是对象")
        validate_config(path, config)
        skin_id = str(config.get("skin_id") or path.parent.name)
        if skin_id in skins:
            raise ValueError(f"重复 skin_id: {skin_id}")
        rel_dir = path.parent.relative_to(ROOT).as_posix()
        poster_name = str(config.get("poster") or "poster.webp")
        poster_path = path.parent / poster_name
        preview = {
            "status": "ready",
            "manifest": f"{rel_dir}/viewer.json",
            "material_fidelity": config.get("fidelity", {}).get("material", "approximate"),
            "sfx_fidelity": config.get("fidelity", {}).get("sfx", "none"),
        }
        record = {"skin_id": skin_id, "preview_3d": preview}
        if poster_path.is_file():
            record["poster"] = f"{rel_dir}/{poster_name}"
        skins[skin_id] = record
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "skins": skins,
    }


def main() -> None:
    payload = build()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    (OUTPUT_DIR / "weapon_skin_media.json").write_text(text, encoding="utf-8")
    js = "window.WEAPON_SKIN_MEDIA = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n"
    (OUTPUT_DIR / "weapon_skin_media.js").write_text(js, encoding="utf-8")
    print(f"weapon skin 3D index: {len(payload['skins'])} ready")


if __name__ == "__main__":
    main()
