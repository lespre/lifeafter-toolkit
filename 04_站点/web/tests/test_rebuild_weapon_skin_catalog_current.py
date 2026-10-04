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
REFERENCE = ROOT / "E:/la拆包项目/03_执行/10_索引/site_data" / "reference_inputs" / "weapon_skin_catalog_user_reference_v3_2.csv"
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
# 2026-09-24 体验服热更（cb85b4d1，目标版本 2026_06_release_260930）后的快照事实：
# 118 主 / 20 时限变体 / 1 行为预览；+5 主行（1110185/1110186/1110187/1110198/1110199，
# sale_ts=2026-09-30 ⇒ 全部 upcoming）+2 变体（11101851/11101861）；sfx 352→362；
# 行为预览由 1110185/1110186 收敛为 1110192。
EXPECTED_STATS = {
    "weapon_skin_data_main_rows": 118,
    "time_limit_variant_rows": 20,
    "weapon_skin_data_total_rows": 138,
    "behavior_preview_rows": 1,
    "catalog_rows": 119,
    "nested_variant_rows": 20,
    "root_comparison_parent_rows": 121,
    "ba8_only_parent_rows": 17,
    "sfx_rows": 362,
    "sfx_parent_skins": 79,
    "sfx_on_variant_skins": 0,
    "main_with_official_name": 118,
    "variant_with_official_name": 20,
    "variant_without_official_name": 0,
    "reference_rows": 128,
    "reference_overlay_rows": 119,
    "behavior_preview_skin_ids": [1110192],
    "release_state_counts": {"on_sale": 111, "upcoming": 5, "no_sale_field": 2, "behavior_only": 1},
    "upcoming_skin_ids": [1110185, 1110186, 1110187, 1110198, 1110199],
    "catalog_main_pairs_without_reference_rows": [1110185, 1110187, 1110192, 1110198, 1110199],
    "name_status_counts": {"verified": 138, "candidate": 0, "unresolved": 1},
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
        self.assertEqual(len(items), 119)
        # Top level: 118 main parents (all verified) + 1 preview; NO variants on top level（09-24）
        self.assertEqual(
            {item["catalog_layer"] for item in board["items"]},
            {"current_parent", "behavior_preview_only"},
        )
        self.assertEqual(sum(item["catalog_layer"] == "current_parent" for item in board["items"]), 118)
        self.assertEqual(
            {item["skin_id"] for item in board["items"] if item["catalog_layer"] == "behavior_preview_only"},
            # 09-24：1110185/1110186 升为正式主行（已有道具行名），行为预览收敛为 1110192
            {1110192},
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
        self.assertEqual(len(nested_variants), 20)  # 09-24：+11101851/+11101861
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
        # 09-24（cb85b4d1）：沙海月鸣行重组 ——「核芯联动=凝华效应 / 特殊交互=手握明月」两句仍在
        # CHS 池内（idx 27/28），但归属行变为 1110157（一/二阶锚点行）；三阶表现行只剩「沙漠流光组」。
        # 原断言记录的是 09-21 及更早的行组织，此处按新包事实收窄（沙海链仍保留，不静默丢）。
        self.assertNotIn("核芯联动=凝华效应", items[1110161]["ui_combat_short_names"])
        self.assertIn("命中效果=冰晶溅射", items[1110159]["ui_combat_short_names"])
        self.assertIn("命中效果=焚罪裁决", items[1110182]["ui_combat_short_names"])
        # variant ids never appear as top-level items
        self.assertEqual(
            # 09-24：+11101851/+11101861（本次新增的两条时限变体）
            {11100041, 11100061, 11100081, 11100231, 11100271, 11100281, 11100901, 11101141, 11101241,
             11101341, 11101451, 11101681, 11101691, 11101701, 11101771, 11101781, 11101811, 11101831,
             11101851, 11101861},
            set(v_by_id),
        )
        # 2026-09-21 新快照补官方道具行 → 由「时限版」占位名变为正式名
        self.assertEqual(v_by_id[11100041]["display_name"], "萌豚霰击（14天）")
        self.assertEqual(v_by_id[11100081]["name"], "庆典绯梦（14天）")
        self.assertEqual(v_by_id[11101241]["name"], "未来刻印（14天）")
        self.assertTrue(set(items).isdisjoint(v_by_id))
        # previews stay unfilled（无父项、无道具行 → 名称保持空）
        for preview_id in (1110192,):
            self.assertIsNone(items[preview_id]["name"])
            self.assertEqual(items[preview_id]["name_status"], "unresolved")
            self.assertEqual(items[preview_id]["name_display"], f"未命名皮肤 · ID {preview_id}")
            self.assertEqual(items[preview_id]["display_name"], f"未命名皮肤 · ID {preview_id}")
            self.assertEqual(items[preview_id]["catalog_layer"], "behavior_preview_only")
        self.assertGreaterEqual(len(items[1110192]["behavior_resources"]), 1)
        # 09-24 新增 5 款（全部 upcoming，sale_ts=2026-09-30），正式名来自同快照道具行
        for skin_id, name in ((1110185, "奇迹"), (1110186, "星辰刀"), (1110187, "前方禁行"),
                              (1110198, "拟化鳞渊"), (1110199, "拟化幽瞳")):
            self.assertEqual(items[skin_id]["name"], name)
            self.assertEqual(items[skin_id]["official_name_status"], "verified")
            self.assertEqual(items[skin_id]["catalog_layer"], "current_parent")

        # Reference overlay on every catalog entity (main/preview) + nested variants = 128 rows
        self.assertEqual(sum(1 for item in board["items"] if "reference_fields" in item), 119)
        self.assertEqual(len(csv_rows), 139)  # 119 目录实体 + 20 嵌套变体
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
        self.assertEqual(len(by_id), 139)

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
        self.assertEqual(len(variants), 20)  # 09-24：时限变体 18→20
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
