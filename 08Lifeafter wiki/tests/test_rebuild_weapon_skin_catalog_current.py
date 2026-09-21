# -*- coding: utf-8 -*-
"""Current BA8 full weapon-skin catalog contract with verified official names."""
from __future__ import annotations

import csv
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "rebuild_weapon_skin_catalog_current.py"
POLICY_MODULE = ROOT / "tools" / "publication_policy.py"
REFERENCE = ROOT / "data" / "reference_inputs" / "weapon_skin_catalog_user_reference_v3_2.csv"
def _registered_sha(source_id: str) -> str:
    """从登记锁动态读取 sha——热更会换 sha，写死会把正常工作变成假红。"""
    payload = json.loads((ROOT / "data" / "live_sources.json").read_text(encoding="utf-8"))
    for source in payload.get("sources", []):
        if source.get("source_id") == source_id:
            return source["expected_sha256"]
    raise AssertionError(f"source not registered: {source_id}")


CURRENT_SHA = _registered_sha("documents-py314-current")
ROOT_SHA = "0f824b35120f42e310a6f42e4ea20200d9465ad34c2e98f47c8ecaf9853b03b7"
REFERENCE_SHA = "827935d81e276c90559ae69401aed9a4e7cf7d75633a96f1ddc7277874998456"
# entry 号随快照漂移 → 契约用稳定 FID（skill：结论必须 FID 直查）
ITEM_BASE_FID = "B42760CCA41DBC25"
ITEM_CHS_FID = "EF3A8474A5E5F7A4"
# 2026-09-10 体验服热更后的当前快照事实（113 主 / 18 时限变体 / 2 行为预览）。
EXPECTED_STATS = {
    "weapon_skin_data_main_rows": 113,
    "time_limit_variant_rows": 18,
    "weapon_skin_data_total_rows": 131,
    "behavior_preview_rows": 2,
    "catalog_rows": 115,
    "nested_variant_rows": 18,
    "root_comparison_parent_rows": 121,
    "ba8_only_parent_rows": 10,
    "sfx_rows": 352,
    "sfx_parent_skins": 77,
    "sfx_on_variant_skins": 0,
    "main_with_official_name": 113,
    "variant_with_official_name": 18,
    "variant_without_official_name": 0,
    "reference_rows": 128,
    "reference_overlay_rows": 115,
    "behavior_preview_skin_ids": [1110185, 1110186],
    "release_state_counts": {"on_sale": 111, "upcoming": 0, "no_sale_field": 2, "behavior_only": 2},
    "upcoming_skin_ids": [],
    "catalog_main_pairs_without_reference_rows": [1110185],
    "name_status_counts": {"verified": 131, "candidate": 0, "unresolved": 2},
}


def load_policy_module():
    spec = importlib.util.spec_from_file_location("weapon_catalog_policy", POLICY_MODULE)
    if spec is None or spec.loader is None:
        raise AssertionError(POLICY_MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CurrentWeaponSkinCatalogContract(unittest.TestCase):
    def test_rebuilder_covers_official_names_variants_previews_and_reference_overlay(self):
        self.assertTrue(SCRIPT.is_file(), "missing full current weapon-skin catalog rebuilder")
        self.assertTrue(REFERENCE.is_file(), "missing user-provided catalog reference snapshot")
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "weapon_skin_sfx_text_sources.json"
            csv_out = Path(tmp) / "weapon_skin_catalog_current.csv"
            result = subprocess.run(
                [
                    sys.executable, str(SCRIPT), "--output", str(out), "--csv-output", str(csv_out),
                    "--reference-csv", str(REFERENCE),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
                timeout=600,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            board = json.loads(out.read_text(encoding="utf-8"))
            with csv_out.open("r", encoding="utf-8-sig", newline="") as handle:
                csv_rows = list(csv.DictReader(handle))

        self.assertEqual(board["meta"]["package_sha"], CURRENT_SHA)
        self.assertEqual(board["meta"]["name"], "当前包 · 武器皮肤图鉴（正式名 + 时限变体 + 预告层）")
        self.assertEqual(board["meta"]["provenance"]["audit_status"], "passed")
        self.assertEqual(
            {lock["sha256"] for lock in board["meta"]["provenance"]["source_locks"]},
            {CURRENT_SHA, ROOT_SHA},
        )
        self.assertEqual(board["stats"], EXPECTED_STATS)
        self.assertEqual(load_policy_module().publication_contract_errors(board), [])

        items = {item["skin_id"]: item for item in board["items"]}
        self.assertEqual(len(items), 115)
        # Top level: 111 main parents (all verified) + 3 previews; NO variants on top level
        self.assertEqual(
            {item["catalog_layer"] for item in board["items"]},
            {"current_parent", "behavior_preview_only"},
        )
        self.assertEqual(sum(item["catalog_layer"] == "current_parent" for item in board["items"]), 113)
        self.assertEqual(
            {item["skin_id"] for item in board["items"] if item["catalog_layer"] == "behavior_preview_only"},
            {1110185, 1110186},
        )
        # 2026-09-10 热更新上架的两款非遗联动皮肤：当前包已有道具行正式名（不再是预告层）
        self.assertEqual(items[1110184]["name"], "星火永传")
        self.assertEqual(items[1110184]["official_name_status"], "verified")
        self.assertEqual(items[1110190]["name"], "佳期如梦")
        self.assertEqual(items[1110190]["official_name_status"], "verified")

        # Official names from common_item_data_base
        self.assertEqual(items[1110001]["name"], "鎏金锐魄")
        self.assertEqual(items[1110001]["official_name_status"], "verified")
        self.assertEqual(items[1110001]["name_status"], "verified")
        self.assertEqual(items[1110001]["name_resolution"]["state"], "verified")
        self.assertIn(f"common_item_data_base.key={1110001}", items[1110001]["provenance"]["field_refs"])
        self.assertTrue(any(
            ref.startswith("common_item_data_base.name CHS field_slot=")
            for ref in items[1110001]["provenance"]["field_refs"]
        ))
        self.assertTrue(items[1110001]["official_desc"].startswith("这是黄金城的遗影"))
        self.assertEqual(items[1110181]["name"], "疾影枪")
        self.assertEqual(items[1110181]["name_resolution"]["state"], "verified")
        self.assertEqual(items[1110181]["sfx_consensus_state"], "sfx_consensus_unpromoted")
        self.assertEqual(len(items[1110181]["sfx_items"]), 2)
        # 1110182: official single name; former/alt names stay in the reference layer
        self.assertEqual(items[1110182]["name"], "火刑裁决")
        self.assertEqual(items[1110182]["reference_fields"]["name"], "火刑电光炮、火刑裁决")
        self.assertEqual(items[1110182]["name_resolution"]["state"], "verified")
        self.assertEqual(items[1110183]["name"], "战神烈火剑")
        self.assertNotIn(11101811, items)

        # Variants nested under their main skin, never top-level
        nested_variants = [variant for item in board["items"] for variant in item.get("variant_items", [])]
        self.assertEqual(len(nested_variants), 18)
        v_by_id = {v["skin_id"]: v for v in nested_variants}
        v1811 = v_by_id[11101811]
        self.assertEqual(v1811["main_skin_id"], 1110181)
        self.assertEqual(v1811["name"], "疾影枪（7天）")
        self.assertEqual(v1811["name_status"], "verified")  # 自带同快照道具行名
        self.assertEqual(v1811["name_resolution"]["state"], "verified")
        self.assertIsInstance(v1811["provenance"].get("business_chain"), dict)
        v61 = v_by_id[11100061]
        self.assertEqual(v61["main_skin_id"], 1110006)
        # 2026-09-21 热更：该变体在新快照中出现官方道具行（common_item_data_base key==11100061）
        # → 名称链闭环，由「候选·时限版」升为已核验（旧断言记录的是新包之前的无行状态）。
        self.assertEqual(v61["name"], "傲隼睨视（14天）")
        self.assertEqual(v61["display_name"], "傲隼睨视（14天）")
        self.assertEqual(v61["name_status"], "verified")
        self.assertEqual(v61["name_resolution"]["state"], "verified")
        self.assertEqual(v61["evidence_level"], "current-snapshot-verified")
        v1831 = v_by_id[11101831]
        self.assertEqual(v1831["main_skin_id"], 1110183)
        # 同上：新快照补了官方道具行（key==11101831 → 战神烈火剑（7天））。
        self.assertEqual(v1831["name"], "战神烈火剑（7天）")
        self.assertEqual(v1831["display_name"], "战神烈火剑（7天）")
        self.assertEqual(v1831["reference_fields"]["source_kind"], "no_user_reference_row")
        self.assertEqual(v_by_id[11100231]["name"], "玉饮琼花（14天）")
        # UI 短名层（effect_show）：锚点行类目命中
        self.assertEqual(items[1110181]["ui_short_name_match"], "user_anchor_20260903")
        self.assertIn("命中效果=疾影贯心", items[1110181]["ui_combat_short_names"])
        self.assertIn("攻击弹道=疾影破空", items[1110181]["ui_combat_short_names"])
        self.assertIn("命中效果=沙漠流光", items[1110161]["ui_combat_short_names"])
        self.assertIn("核芯联动=凝华效应", items[1110161]["ui_combat_short_names"])
        self.assertIn("命中效果=冰晶溅射", items[1110159]["ui_combat_short_names"])
        self.assertIn("命中效果=焚罪裁决", items[1110182]["ui_combat_short_names"])
        # variant ids never appear as top-level items
        self.assertEqual(
            {11100041, 11100061, 11100081, 11100231, 11100271, 11100281, 11100901, 11101141, 11101241,
             11101341, 11101451, 11101681, 11101691, 11101701, 11101771, 11101781, 11101811, 11101831},
            set(v_by_id),
        )
        # 2026-09-21 新快照补官方道具行 → 由「时限版」占位名变为正式名
        self.assertEqual(v_by_id[11100041]["display_name"], "萌豚霰击（14天）")
        self.assertEqual(v_by_id[11100081]["name"], "庆典绯梦（14天）")
        self.assertEqual(v_by_id[11101241]["name"], "未来刻印（14天）")
        self.assertTrue(set(items).isdisjoint(v_by_id))
        # previews stay unfilled（无父项、无道具行 → 名称保持空）
        for preview_id in (1110185, 1110186):
            self.assertIsNone(items[preview_id]["name"])
            self.assertEqual(items[preview_id]["name_status"], "unresolved")
            self.assertEqual(items[preview_id]["name_display"], f"未命名皮肤 · ID {preview_id}")
            self.assertEqual(items[preview_id]["display_name"], f"未命名皮肤 · ID {preview_id}")
            self.assertEqual(items[preview_id]["catalog_layer"], "behavior_preview_only")
        self.assertGreaterEqual(len(items[1110185]["behavior_resources"]), 1)

        # Reference overlay on every catalog entity (main/preview) + nested variants = 128 rows
        self.assertEqual(sum(1 for item in board["items"] if "reference_fields" in item), 115)
        self.assertEqual(len(csv_rows), 133)
        by_id = {row["皮肤ID"]: row for row in csv_rows}
        self.assertEqual(by_id["1110182"]["图鉴显示名"], "火刑裁决")
        self.assertEqual(by_id["1110182"]["历史曾用名（整理表）"], "火刑电光炮、火刑裁决")
        self.assertEqual(by_id["11101811"]["图鉴层级"], "time_limit_variant")
        self.assertEqual(by_id["11101811"]["所属主皮肤ID"], "1110181")
        # 同上：新快照官方行 → 显示名带时限后缀（14天）
        self.assertEqual(by_id["11100061"]["图鉴显示名"], "傲隼睨视（14天）")
        self.assertEqual(by_id["11100061"]["所属主皮肤ID"], "1110006")
        self.assertEqual(by_id["11101831"]["图鉴层级"], "time_limit_variant")
        self.assertEqual(by_id["11101831"]["所属主皮肤ID"], "1110183")
        self.assertTrue(by_id["1110001"]["当前官方描述"].startswith("这是黄金城的遗影"))
        layers = {row["图鉴层级"] for row in csv_rows}
        self.assertEqual(layers, {"current_parent", "time_limit_variant", "behavior_preview_only"})
        self.assertEqual(len(by_id), 133)

        # source entries include the two common_item_data_base payloads
        source_fids = {str(e.get("file_id", "")).upper() for e in items[1110001]["provenance"]["source_entries"]}
        self.assertIn(ITEM_BASE_FID, source_fids)
        self.assertIn(ITEM_CHS_FID, source_fids)
        self.assertEqual(items[1110001]["evidence_level"], "current-snapshot-verified")
        self.assertIsInstance(items[1110001]["provenance"].get("business_chain"), dict)


    def test_timed_variant_relation_is_published_by_runtime_rule(self):
        """时限→永久 变体关系：正式发布，依据 runtime //10；不得用末位数字做识别门槛。

        用户 2026-09-11 口径：get_perm_skin_id(timed_id)=timed_id//10 有运行时代码证据 →
        variant_type=timed / permanent_skin_id=timed_id//10 / variant_relation_state=verified_runtime_rule
        可发布；但 timed_id%10==1 无证据，不得附加、也不得作为识别门槛。
        """
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("% 10 == 1", source, "不得用末位 1 作为变体识别门槛")
        self.assertNotIn("%10 == 1", source)
        # 两步法：① is_timed_skin_id(k) 区间判定 ② permanent_skin_id = k // 10
        self.assertIn("is_timed_skin_id(k)", source, "识别必须走 is_timed_skin_id 区间判定")
        self.assertIn("def is_timed_skin_id(item_id: int) -> bool:", source)
        self.assertNotIn("variant_ids = {k for k in parent_set if k > 9", source,
                         "不得仅凭 parent_set 命中反推 timed 身份")
        self.assertIn("TIMED_SKIN_ID_MIN <= item_id <= TIMED_SKIN_ID_MAX", source, "必须是区间判定")

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "board.json"
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--output", str(out),
                 "--csv-output", str(Path(tmp) / "b.csv"), "--reference-csv", str(REFERENCE)],
                cwd=ROOT, text=True, capture_output=True, check=False, timeout=600,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            board = json.loads(out.read_text(encoding="utf-8"))

        mains = {it["skin_id"] for it in board["items"] if it.get("catalog_layer") == "current_parent"}
        variants = [v for it in board["items"] for v in (it.get("variant_items") or [])]
        self.assertEqual(len(variants), 18)
        for variant in variants:
            skin_id = variant["skin_id"]
            self.assertEqual(variant["variant_type"], "timed")
            self.assertEqual(variant["permanent_skin_id"], skin_id // 10)
            self.assertEqual(variant["variant_relation_state"], "verified_runtime_rule")
            self.assertIn(variant["permanent_skin_id"], mains, "父皮肤必须在主皮肤集合内")
            # parent_set 只做一致性审计
            self.assertEqual(variant["variant_relation_target_state"], "resolved")
        # 板内文字也不得出现未证明的末位假设
        self.assertNotIn("%10==1", json.dumps(board, ensure_ascii=False))


if __name__ == "__main__":
    unittest.main()
