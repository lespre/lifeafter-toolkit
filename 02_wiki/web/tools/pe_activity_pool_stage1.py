# -*- coding: utf-8 -*-
"""Isolated, source-locked PE activity/pool rebuild. Never writes live boards."""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import re
import shutil
import sqlite3
import struct
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from la_paths import PROJ, TREE_ROOT, ANALYSIS_ROOT, TOOLKIT_CORE

if str(TOOLKIT_CORE) not in sys.path:
    sys.path.insert(0, str(TOOLKIT_CORE))

SCRATCH = pathlib.Path(os.environ.get("TMPDIR", pathlib.Path.home() / "AppData/Local/hermes/cache/scratch"))


def verify_package(path: pathlib.Path, expected_sha: str, expected_bytes: int) -> dict:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            h.update(chunk)
    actual = {"sha256": h.hexdigest(), "bytes": path.stat().st_size}
    if actual["sha256"] != expected_sha or actual["bytes"] != expected_bytes:
        raise ValueError("source lock mismatch: %s" % path)
    return actual


def validate_destination(path: pathlib.Path) -> pathlib.Path:
    path = path.resolve()
    allowed = (ANALYSIS_ROOT / "pe_activity_pool_stage1", TREE_ROOT / "_专项" / "pe_activity_pool_stage1")
    if not any(path.is_relative_to(base.resolve()) for base in allowed):
        raise ValueError("only isolated stage1 destinations are allowed: %s" % path)
    return path


def write_stable(path: pathlib.Path, data: bytes) -> None:
    path = validate_destination(path)
    if path.is_file() and path.read_bytes() == data:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def save_json(path: pathlib.Path, data) -> None:
    write_stable(path, (json.dumps(data, ensure_ascii=False, sort_keys=True, indent=1) + "\n").encode("utf-8"))


def freeze_source() -> dict:
    """Freeze the registered PE package; materialize selected inputs in an isolated restored tree."""
    from la_paths import INDEX_ROOT
    import build_lottery_pool_pe1103 as legacy
    from toolkit_core import hotfix_rows as HR
    import la_unpack_core as LC

    registry = json.loads((HERE.parent / "data/live_sources_pe.json").read_text(encoding="utf-8"))
    sources = [s for s in registry["sources"] if s["source_id"] == "documents-py314-current"]
    if len(sources) != 1:
        raise ValueError("source lock must name exactly one PE package")
    source = sources[0]
    package = pathlib.Path(source["path"])
    lock = verify_package(package, source["expected_sha256"], source["expected_bytes"])
    snapshot = lock["sha256"][:12]
    out = validate_destination(ANALYSIS_ROOT / "pe_activity_pool_stage1" / snapshot)
    tree = validate_destination(TREE_ROOT / "_专项/pe_activity_pool_stage1" / snapshot / "配置")
    frozen = out / "source/script.py314.lc.npk"
    if not frozen.is_file():
        frozen.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(package, frozen)
    verify_package(frozen, lock["sha256"], lock["bytes"])
    raw = frozen.read_bytes()
    entries = {e["fid"].upper(): e for e in HR._entries(frozen)}
    con = sqlite3.connect((INDEX_ROOT / "热更检测/names_join.sqlite3").as_uri() + "?mode=ro", uri=True)
    selected = {}
    pattern = re.compile(r"lottery|huodong_conf_data|only_fashion_hd|optional_|reward_pool|secret_fashion|fashion_diy|lottery_team|oversea_table_map|server_cluster_data", re.I)
    for fid, name in con.execute("SELECT fid,name FROM nm WHERE name LIKE ?", ("com\\cdata\\%",)):
        name = name.replace("\\", "/")
        if name.endswith(".py") and pattern.search(name.rsplit("/", 1)[-1]):
            selected[fid.upper()] = name
    for fid, name in con.execute("SELECT fid,name FROM nm WHERE name=? OR name=?", ("com\\utils\\SplitTableData.py", "com\\cdata\\__init__.py")):
        selected[fid.upper()] = name.replace("\\", "/")
    con.close()
    for component, dfid, cfid in legacy.COMPONENTS:
        if component == "base":
            selected[dfid] = "com/cdata/reward_pool_data_base.py"
            selected[cfid] = "com/cdata/reward_pool_data_base_chs.py"
        else:
            stem = "com/cdata/oversea/reward_pool_data_auto_oversea_data_" + component
            selected[dfid], selected[cfid] = stem + ".py", stem + "_chs.py"
    for shard, fid in legacy.SHARDS:
        selected[fid] = "com/cdata/reward_pool_data_" + shard + ".py"
    tables, absent, failures = [], [], []
    for fid, name in sorted(selected.items(), key=lambda v: v[1]):
        e = entries.get(fid)
        if e is None:
            absent.append({"file_id": fid, "path": name, "state": "not_in_this_package"})
            continue
        try:
            data = LC.npk_decode_entry(raw[e["offset"]:e["offset"] + e["packed"]], e["decoded"], e["flag"], declared_packed=e["packed"])
        except Exception as exc:
            failures.append({"file_id": fid, "path": name, "error": "%s: %s" % (type(exc).__name__, exc)})
            continue
        dest = tree / name
        if not dest.resolve().is_relative_to(tree):
            raise ValueError("unsafe source path: " + name)
        write_stable(dest, data)
        tables.append({"file_id": fid, "path": name, "entry_index": e.get("index"), "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)})
    # The installed Documents package is an overlay, not the entire PE baseline.
    # Supplement ONLY unchanged CHS from the authoritative current PE tree, with
    # an independent merge-ledger hash. Never borrow old data rows or PC/APK CHS.
    current_root = TREE_ROOT / "pe/配置"
    ledger_path = TREE_ROOT / "pe/pe_config_merge_ledger_v2.json"
    ledger_raw = ledger_path.read_bytes()
    ledger = {x["file"].replace("\\", "/"): x for x in json.loads(ledger_raw)["files"]}
    ledger_sha = hashlib.sha256(ledger_raw).hexdigest()
    known_paths = {x["path"] for x in tables}
    supplements, rejected = [], []
    for data_meta in list(tables):
        rel = data_meta["path"]
        if not rel.startswith("com/cdata/") or rel.endswith("_chs.py"):
            continue
        chs_rel = rel[:-3] + "_chs.py"
        if chs_rel in known_paths:
            continue
        source_path = current_root / chs_rel
        entry = ledger.get(chs_rel[len("com/cdata/"):])
        if not source_path.is_file() or not entry:
            rejected.append({"path": chs_rel, "reason": "no_current_PE_tree_and_ledger_pair"})
            continue
        data = source_path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if digest != entry["sha256"] or len(data) != entry["bytes"]:
            rejected.append({"path": chs_rel, "reason": "current_tree_differs_from_recorded_ledger"})
            continue
        meta = {"path": chs_rel, "file_id": None, "entry_index": None, "sha256": digest,
                "bytes": len(data), "source_path": str(source_path), "ledger_sha256": ledger_sha,
                "role": "ledger-verified-current-pe-tree-chs"}
        write_stable(tree / chs_rel, data)
        tables.append(meta)
        supplements.append(meta)
        known_paths.add(chs_rel)
    manifest = {
        "schema": "pe-activity-pool-source/v2", "platform": "pe", "snapshot": snapshot,
        "source_package": str(package), "package": str(frozen), "tree": str(tree), "output": str(out),
        "source_lock": lock, "package_entries": len(entries), "tables": tables,
        "absent_candidates": absent, "decode_failures": failures,
        "schema_supplements": supplements, "schema_supplement_rejections": rejected,
        "scope": "registered PE overlay plus ledger-verified current PE baseline CHS only; no PC/APK; existing PE tree and live boards untouched",
    }
    save_json(out / "source_manifest.json", manifest)
    if failures:
        raise ValueError("selected source decode failures: %d (see source_manifest.json)" % len(failures))
    return manifest


def project_components(components: dict) -> list[dict]:
    """Explicit static overlay projection, not a runtime-final payout assertion."""
    if not components.get("base"):
        raise ValueError("base pool component is empty")
    base = components["base"]
    records = []
    for component, own in components.items():
        keys = sorted(set(base) | set(own)) if component != "base" else sorted(base)
        for key in keys:
            source_component = component if key in own else "base"
            record = dict(own[key] if key in own else base[key])
            old = base.get(key)
            if component == "base":
                diff = "base"
            elif key not in own:
                diff = "inherit"
            elif old is None:
                diff = "added"
            else:
                diff = "same" if (record["item_id"], record["item_count"]) == (old["item_id"], old["item_count"]) else "replaced"
            record.update(component=component, source_component=source_component,
                          pool_key=key[0], item_no=key[1], diff=diff,
                          runtime_final_state="unknown",
                          projection="base-plus-component-static-projection")
            records.append(record)
    return records


def decode_pools(manifest: dict) -> dict:
    import build_lottery_pool_pe1103 as legacy
    from toolkit_core import bindict_table as BT
    from bindict_provenance import decode_table_rows_with_chs_slots

    tree = pathlib.Path(manifest["tree"])
    by_fid = {t["file_id"]: t for t in manifest["tables"]}
    components, checks = {}, []
    for component, data_fid, chs_fid in legacy.COMPONENTS:
        data_meta, chs_meta = by_fid[data_fid], by_fid[chs_fid]
        raw = (tree / data_meta["path"]).read_bytes()
        chs = (tree / chs_meta["path"]).read_bytes()
        body = legacy._xbody(raw)
        if body is None:
            raise ValueError("pool body missing: " + component)
        count = struct.unpack_from("<I", body, 0)[0]
        blob = body[8 + 4 * count:]
        rows, unbound = decode_table_rows_with_chs_slots(body, BT.parse_legacy_chs_pool(chs))
        if unbound:
            raise ValueError("unbound pool source rows: %s %d" % (component, len(unbound)))
        own = {}
        for row in rows:
            key = BT.resolve_jump_group(blob, row["key"])
            field = row["values"].get("reward")
            if not isinstance(key, list) or len(key) != 2 or not field or not str(field[1]).startswith("jump:"):
                raise ValueError("unresolved pool row key/reward: %s %s" % (component, row["key"]))
            reward = BT.resolve_jump_group(blob, int(field[1][5:]))
            if not isinstance(reward, list) or len(reward) != 2:
                raise ValueError("unresolved reward group: %s %s" % (component, key))
            key = tuple(int(x) for x in key)
            if key in own:
                raise ValueError("duplicate source pool key: %s %s" % (component, key))
            record = {"item_id": int(reward[0]), "item_count": int(reward[1]),
                      "source_file_id": data_fid, "source_sha256": data_meta["sha256"],
                      "source_key_offset": row["key"], "reward_offset": int(field[1][5:])}
            for name in legacy.FIELDS:
                value = row["values"].get(name)
                record[name] = value[1] if isinstance(value, tuple) else value
            own[key] = record
        components[component] = own
        checks.append({"component": component, "decoded_rows": len(rows), "mapped_rows": len(own),
                       "unbound": len(unbound), "pools": len({k[0] for k in own})})
    return {"components": checks, "rows": project_components(components),
            "completeness": "all rows of selected base/variant components; unresolved runtime and absent referenced shards excluded",
            "runtime_final_state": "unknown"}


def list_assignment(code, target: str) -> list | None:
    """Read only an exact literal list construction; never run imports/game functions."""
    import vm_cdata_table as VM
    names = [VM.unwrap(x) for x in code.names]
    consts = [VM.unwrap(x) for x in code.consts]
    instructions = [x[0] for x in code.dis_resolved()]
    for stop, ins in enumerate(instructions):
        if ins.name != "STORE_NAME" or ins.arg >= len(names) or names[ins.arg] != target:
            continue
        start = stop - 1
        while start >= 0:
            op = instructions[start]
            if op.name == "BUILD_LIST" and op.arg == 0:
                break
            if op.name not in {"LOAD_CONST", "LOAD_SMALL_INT", "LIST_APPEND", "LIST_EXTEND"}:
                return None
            start -= 1
        if start < 0:
            return None
        stack = []
        for op in instructions[start:stop]:
            if op.name == "BUILD_LIST":
                stack.append([])
            elif op.name == "LOAD_CONST":
                stack.append(consts[op.arg])
            elif op.name == "LOAD_SMALL_INT":
                stack.append(op.arg)
            elif op.name == "LIST_APPEND":
                value = stack.pop()
                stack[-1].append(value)
            elif op.name == "LIST_EXTEND":
                value = stack.pop()
                if not isinstance(value, (list, tuple)):
                    return None
                stack[-1].extend(value)
        return stack[0] if len(stack) == 1 and isinstance(stack[0], list) else None
    return None


def decode_table(manifest: dict, name: str) -> dict:
    """Decode one named table from the isolated same-package tree, retaining failures."""
    from toolkit_core import bindict_table as BT, script_decode as SD
    import vm_cdata_table as VM
    import build_lottery_pool_pe1103 as legacy

    rel = "com/cdata/" + name + ".py"
    meta = next((x for x in manifest["tables"] if x["path"] == rel), None)
    result = {"table": name, "rows": [], "unbound": [], "delete_keys": None,
              "source": meta, "decode_state": "absent_from_selected_package"}
    if meta is None:
        return result
    path = pathlib.Path(manifest["tree"]) / rel
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != meta["sha256"]:
        raise ValueError("table source lock mismatch: " + name)
    body = legacy._xbody(raw)
    pool_path = path.with_name(path.stem + "_chs.py")
    chs_rel = rel[:-3] + "_chs.py"
    chs_meta = next((x for x in manifest["tables"] if x["path"] == chs_rel), None)
    pool_raw = pool_path.read_bytes() if chs_meta is not None else None
    if pool_raw is not None and hashlib.sha256(pool_raw).hexdigest() != chs_meta["sha256"]:
        raise ValueError("CHS source lock mismatch: " + name)
    pool = BT.parse_legacy_chs_pool(pool_raw) if pool_raw is not None else []
    result["chs_source"] = chs_meta
    frame_ok = body is not None and len(body) >= 12 and struct.unpack_from("<I", body, 4)[0] == 0
    if frame_ok:
        expected_pool = struct.unpack_from("<I", body, 0)[0]
        if pool_raw is not None and expected_pool != len(pool):
            result["decode_state"] = "chs_count_mismatch"
            result["unbound"] = [{"expected_pool": expected_pool, "actual_pool": len(pool)}]
            return result
        result["field_name_state"] = "pool-count-and-source-lock-checked" if pool_raw is not None else "unnamed_schema"
        try:
            rows, unbound = BT.decode_table_rows(body, pool, resolve_jumps=False, lenient=True)
            result["rows"] = [{"key": r["key"], "values": {
                k: v[1] if isinstance(v, tuple) and len(v) == 2 else v
                for k, v in r.get("values", {}).items()}} for r in rows]
            result["unbound"] = unbound
            result["decode_state"] = "bindict" if not unbound else "partial_bindict"
            result["body"] = body
            count = struct.unpack_from("<I", body, 0)[0]
            result["blob"] = body[8 + 4 * count:]
        except Exception as exc:
            result["unbound"] = [{"error": "%s: %s" % (type(exc).__name__, exc)}]
            result["decode_state"] = "bindict_error"
    try:
        _, code, end = SD.load_module(str(path))
        result["parse_end"] = end
        result["file_bytes"] = len(raw)
        if code is not None:
            result["delete_keys"] = list_assignment(code, "region_delete_keys")
            result["module_names"] = [VM.unwrap(x) for x in code.names if isinstance(VM.unwrap(x), str)]
            if not frame_ok:
                VM.REG.clear()
                VM.MAPADD.clear()
                _, skipped = VM.run(code)
                rows = {}
                for key, value in VM.MAPADD:
                    if isinstance(key, int) and not isinstance(key, bool) and isinstance(value, dict) and isinstance(value.get("name"), str):
                        if key in rows:
                            raise ValueError("duplicate activity row: %s" % key)
                        rows[key] = value
                result["rows"] = [{"key": k, "values": v} for k, v in sorted(rows.items())]
                result["decode_state"] = "bytecode_activity" if rows else "module_without_decoded_rows"
                result["skipped_instructions"] = skipped
    except Exception as exc:
        result["module_error"] = "%s: %s" % (type(exc).__name__, exc)
    return result


def decode_activities(manifest: dict) -> dict:
    base = decode_table(manifest, "huodong_conf_data")
    if not base["rows"] or base.get("parse_end") != base.get("file_bytes"):
        raise ValueError("base activity module is incomplete")
    variants = {}
    prefix = "com/cdata/oversea/huodong_conf_data_auto_oversea_data_"
    for meta in manifest["tables"]:
        path = meta["path"]
        if path.startswith(prefix) and path.endswith(".py") and not path.endswith("_chs.py"):
            component = path[len(prefix):-3]
            variants[component] = decode_table(manifest, path[len("com/cdata/"):-3])
    return {"base": base, "variants": variants, "runtime_final_state": "unknown",
            "note": "raw base and server overlays/deletion lists; time windows alone do not prove current activation"}


DIRECT_ROUTES = {
    **{name: ("super_fashion_lottery_conf_data", "lottery_id") for name in (
        "SuperFashionLotteryHD", "BlessingsAlwaysLotteryHD", "DragonBlessingLotteryHD",
        "ScorpioSuperLotteryHD", "ChituSuperLotteryHD")},
    "MultiOptionalLotteryHD": ("multi_optional_lottery_conf_data", "lottery_id"),
    "T1BuildingObjectLotteryHDV2": ("T1_bobj_lottery_v2_base_conf_data", "lottery_pool_id"),
    "VehicleLotteryHD": ("vehicle_lottery_base_conf_data", "reward_pool_id"),
}


def bind_activity_pools(manifest: dict, activities: dict, pools: dict) -> dict:
    """Use explicit family/field contracts, never arbitrary equal-integer joins."""
    from functools import lru_cache
    from toolkit_core import bindict_table as BT

    pool_keys = {(r["component"], r["pool_key"]) for r in pools["rows"]}
    cache = lru_cache(maxsize=None)(lambda name: decode_table(manifest, name))
    bindings, unresolved, inventory = [], [], []
    base_by_id = {r["key"]: r["values"] for r in activities["base"]["rows"]}

    def keys(table, value):
        if isinstance(value, int) and not isinstance(value, bool):
            return [value]
        if isinstance(value, (list, tuple)):
            return [v for v in value if isinstance(v, int) and not isinstance(v, bool)]
        if isinstance(value, str) and value.startswith("jump:") and table.get("blob") is not None:
            group = BT.resolve_jump_group(table["blob"], int(value[5:]))
            return keys(table, group) if isinstance(group, list) else []
        return []

    def table_for(component, stem):
        name = stem if component == "base" else "oversea/%s_auto_oversea_data_%s" % (stem, component)
        t = cache(name)
        inventory.append({"component": component, "table": name, "rows": len(t["rows"]),
                          "unbound": len(t["unbound"]), "state": t["decode_state"], "source": t["source"]})
        return t

    def step(table, key, field):
        source = table.get("source") or {}
        return {"table": table["table"], "row_key": key, "field": field,
                "file_id": source.get("file_id"), "sha256": source.get("sha256")}

    sources = [("base", activities["base"])] + sorted(activities["variants"].items())
    for component, activity_table in sources:
        for activity in activity_table["rows"]:
            aid = activity["key"]
            own = activity["values"]
            values = dict(base_by_id.get(aid, {})) if component != "base" else {}
            values.update(own)
            cls = values.get("hd_class", "")
            if not isinstance(cls, str) or not re.search(r"Lottery|Roulette|PigeonWish|SecretFashion|WishFashion", cls):
                continue
            common = {"component": component, "activity_id": aid, "name": values.get("name"), "hd_class": cls,
                      "activity_definition": "raw-base" if component == "base" else "base-plus-explicit-variant-projection",
                      "runtime_final_state": "unknown"}
            source_steps = [step(activity_table, aid, "extra_param")]
            reason = "unsupported_family_route"
            target_table, target_rows, field = None, [], None
            if cls in DIRECT_ROUTES:
                stem, field = DIRECT_ROUTES[cls]
                target_table = table_for(component, stem)
                selected = set(keys(activity_table, values.get("extra_param")))
                target_rows = [x for x in target_table["rows"] if x["key"] in selected]
                reason = "configuration_key_or_table_unresolved"
            elif cls == "OnlyFashionLotteryHD":
                first = table_for(component, "only_fashion_hd_base_conf")
                rows = [x for x in first["rows"] if x["key"] == aid]
                target_table = table_for(component, "only_fashion_hd_lottery_conf")
                selected = set()
                for row in rows:
                    v = row["values"]
                    # Frozen-family contract, not an arbitrary scan across slots.
                    name = "lottery_conf_id" if "lottery_conf_id" in v else "<slot_7>"
                    selected.update(keys(first, v.get(name)))
                    source_steps.append(step(first, row["key"], name))
                target_rows = [x for x in target_table["rows"] if x["key"] in selected]
                field = "<slot_4>"
                reason = "only_fashion_period_or_pool_unresolved"
            elif cls == "OptionalLotteryHD":
                target_table = table_for(component, "optional_conf_data")
                target_rows = [x for x in target_table["rows"] if x["key"] == aid]
                field = "base_lottery_id"
                reason = "optional_activity_conf_unresolved"
            elif cls == "BuildingObjectLotteryHD":
                first = table_for(component, "T2_bobj_lottery_base_conf_data")
                selected = set(keys(activity_table, values.get("extra_param")))
                reward_keys = set()
                for row in first["rows"]:
                    if row["key"] in selected:
                        reward_keys.update(keys(first, row["values"].get("lottery_conf_ids")))
                        source_steps.append(step(first, row["key"], "lottery_conf_ids"))
                target_table = table_for(component, "T2_bobj_lottery_reward_conf_data")
                target_rows = [x for x in target_table["rows"] if x["key"] in reward_keys]
                field = "lottery_pool_id"
                reason = "furniture_reward_conf_unresolved"
            matched = 0
            for row in target_rows:
                name = field
                if cls == "OnlyFashionLotteryHD":
                    name = "reward_pool_id" if "reward_pool_id" in row["values"] else (
                        "lottery_id" if "lottery_id" in row["values"] else "<slot_4>")
                for pk in keys(target_table, row["values"].get(name)):
                    present = (component, pk) in pool_keys
                    bindings.append({**common, "pool_key": pk, "pool_present": present,
                                     "evidence": "typed-static-reference", "steps": source_steps + [step(target_table, row["key"], name)]})
                    matched += 1
            if not matched:
                unresolved.append({**common, "reason": reason, "steps": source_steps,
                                   "config_table": target_table["table"] if target_table else None})
    unique_inventory = {(x["component"], x["table"]): x for x in inventory}
    return {"bindings": bindings, "unresolved": unresolved,
            "table_inventory": [v for _, v in sorted(unique_inventory.items())],
            "scope": "explicit static family contracts; non-reward-pool namespaces and unknown routes are not coerced"}
