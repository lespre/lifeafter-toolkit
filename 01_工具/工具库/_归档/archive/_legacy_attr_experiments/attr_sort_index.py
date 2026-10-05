# -*- coding: utf-8 -*-
"""把已知属性名按字母排序，计算关键属性的索引"""
import json
from pathlib import Path

# 从 attribute_data_chs.nxs 英文属性名表提取的属性名（按字母顺序）
# 这个列表是从文件中逐字提取的，应该完整
ATTRS = [
    "abnormal_removal_level_from_drone", "accurate", "add_max_qili_rate",
    "affect_temp", "alienation_recover", "alive_time", "ammunition",
    "ammunition_cost_reduce_ratio", "ammunition_cost_reduce_ratio_MaxLimit",
    "anti_critical_rate", "armed_strength", "armor",
    "armor_durability_reduce_ratio", "armor_durability_reduce_ratio_MaxLimit",
    "armor_ignore_compress", "armor_life_reduce_ratio", "armor_penetration",
    "armor_ratio", "artifact_energy_recovery_rate", "artifact_reduce_cd_rate",
    "artifact_reset_cd_rate", "assault_rifle_hurt_additional_rate",
    "assault_rifle_hurt_reduction_rate", "attr_fish_king_addition_rate",
    "back_injured_rate", "back_reduction_rate", "back_speed_rate",
    "backstab_hurt_factor", "backstab_hurt_reduction_rate",
    "bad_weather_reduce_cost_ratio", "base_heal", "base_hurt", "base_power",
    "base_speed_inc", "base_speed_inc_rate", "bear_hurt_addition",
    "bear_hurt_duration_additional_rate", "beast_hurt_additional_rate",
    "blunt_force", "bombs_hurt_additional_rate", "bombs_radius_addition_rate",
    "bow_hurt_reduction_rate", "buff_duration", "buff_reduce_cost_ratio",
    "building_defense_hurt_additional_rate", "building_furniture_additional_rate",
    "building_hurt_additional_rate", "building_struct_hurt_additional_rate",
    "bullet_cost_additional_rate", "bullet_hurt_percent_reduce_ratio",
    "bullet_hurt_percent_reduce_ratio_display_only",
    "burst_fire_gun_clip_capacity_rate", "carry_repair_armor_life_reduce_ratio",
    "carry_repair_weapon_life_reduce_ratio", "caught_by_monster",
    "charge_speed_addition_rate", "climb_hurt_reduction_rate",
    "clip_capacity_num", "clip_capacity_rate", "cold_arm_distance_additional_rate",
    "cold_arms_hurt_reduction", "cold_resist_addition", "coldarm_additional_rate",
    "coldarm_force_move_target_rate", "coldarm_hurt_reduction_rate",
    "coldarms_shiled_hurt_addition_rate", "coldarms_shiled_hurt_reduction_rate",
    "collect_level", "collect_res_addition_rate", "collect_time_dec",
    "combat_coolant_cost_reduce", "combat_fighter_exp_extra_ratio",
    "composite_equip_recipe_addition_prob", "conscious_hurt_reduction_rate",
    "consumption_power", "control_resistance_display_only",
    "coolant_recovery_rate", "cost_hunger_additional_rate", "craft_acc_rate",
    "craft_res_addition_rate", "critical_hurt_addition_rate",
    "critical_hurt_reduction_rate", "critical_rate",
    "critical_rate_ignore_compress", "crouch_hurt_additional_rate",
    "crouch_hurt_reduction_rate", "cut_angle_additional_rate",
    "cut_res_addition_rate", "cut_speed", "cut_speed_addition_rate",
    "cut_speed_addition_rate_ignore_compress", "cut_tree_recover_hp",
    "cut_tree_recover_prob", "cut_tree_speed_additional_rate",
    "cyborg_max_hp_recovery_rate", "debt_duration_reduce_rate",
    "defense_building_hurt_additional_rate", "dig_res_addition_rate",
    "dig_rock_recover_hp", "dig_rock_recover_prob", "dig_rock_speed_addition_rate",
    "discard_rate", "distortion_monster_dmg_dec_rate",
    "distortion_monster_hurt_additional_rate", "dot_hurt_add_rate",
    "dot_hurt_red_rate", "dot_hurt_reduction", "drone_additional_rate",
    "drone_attack_rate", "drone_durability_reduce_rate",
    "drone_electric_effect_cof", "drone_energy", "drone_energy_cost_dec_rate",
    "drone_energy_ratio", "drone_fire_durability_reduce_rate",
    "drone_fly_distance", "drone_fly_distance_addition", "drone_fly_height",
    "drone_fly_pig_damage_cof", "drone_fly_speed", "drone_hp_recover",
    "drone_hurt_reduction_rate", "drone_lightshield_bear_rate",
    "drone_monster_hurt_additional_rate", "drone_player_hurt_additional_rate",
    "drone_power", "drone_release_interval_dec_rate", "drone_skill_cool_down_rate",
    "drone_skill_durability_reduce_rate", "drone_skill_effect_rate",
    "drone_tactic_additional_rate", "drone_type", "drone_weapon_type",
    "drone_weight_bearing", "drone_weight_bearing_expand", "durability",
    "durability_reduce_rate", "durability_reduce_ratio_MaxLimit", "duration",
    "dying_hurt_reduction_rate", "dz_map_jump_add_height_rate",
    "electrical_mind_shield_recover_cof", "em_shoot_fire_speed_inc_factor",
    "em_shoot_recover_rate", "emergency_defense_effect_addition_per_power",
    "energy", "equip_clip_capacity_rate", "equip_store_bullets_rate",
    "explode_hurt_additional_rate", "explode_hurt_reduction_rate",
    "explode_hurt_value", "explode_radius_addition_rate", "extra_bag_capacity",
    "extra_dish_bag_capacity", "extra_durability_ratio", "extra_equip_bag_capacity",
    "extra_get_rock_num", "extra_get_tree_num", "extra_life_ratio",
    "extra_stone_gain_rate", "extra_tree_gain_rate", "factor_belly",
    "factor_chest", "factor_foot", "factor_hand", "factor_head",
    "factor_hurt_belly", "factor_hurt_chest", "factor_hurt_foot",
    "factor_hurt_hand", "factor_hurt_head", "fall_dmg_dec_rate",
    "fertilize_plant_harvest_additional_rate",
    "fertilize_rock_harvest_additional_rate", "fibre_critical_rate",
    "fibre_extra_critical_rate", "fight_prof_require_level_reduce",
    "final_extra_hurt_reduction_rate", "fire_knife_player_hurt_rate_ratio",
    "fire_speed", "fire_speed_rate", "fire_speed_rate_ignore_compress",
    "firearm_additional_rate", "firearm_hurt_reduction",
    "firearm_hurt_reduction_rate", "fishing_dis_rate_addition_ratio",
    "fishing_hook_time_reduction_ratio", "fishing_proficiency_speeding_up",
    "food_time_addition_rate", "friends_explode_hurt_reduction_rate",
    "front_injured_factor", "front_reduction_factor", "frost_hurt_ratio_cof",
    "full_ship_speed_reduction", "gravity_coef", "group_speed_additional_rate",
    "hand_shield_extra_damage", "hand_shield_miss_rate",
    "hang_up_fishing_double_probability", "hang_up_fishing_increase_probability",
    "head_critical_chaos_rate", "head_critical_disability_rate",
    "head_critical_paralysis_rate", "head_critical_tremble_rate", "headshot_rate",
    "heal_addition_rate", "health_addition", "heavy_weapon_distance_additional_rate",
    "heavy_weapon_hurt_additional_rate", "heavy_weapon_hurt_reduction",
    "heavy_weapon_hurt_reduction_rate", "high_hurt_additional_rate",
    "hit_coolant_cost_reduce", "home_repair_cost_reduce_rate",
    "howitzer_hurt_additional_rate", "howitzer_hurt_reduction_rate",
    "howitzer_radius_addition_rate", "hp_additional_rate", "hp_auto_recover_value",
    "hp_recover", "hp_recovery_rate_from_drone", "hp_tisheng_icon",
    "human_monster_dmg_dec_rate", "humanoid_hurt_additional_rate", "hurt",
    "hurt_ignore_compress", "hurt_ratio", "hurt_reduction_rate",
    "hurt_reduction_rate_ignore_compress",
]

print(f"属性名总数: {len(ATTRS)}")
print()

# 按字母排序（已经是按字母顺序的，但确认一下）
sorted_attrs = sorted(ATTRS)
if sorted_attrs == ATTRS:
    print("列表已按字母顺序排列")
else:
    print("列表未按字母顺序排列，重新排序")
    ATTRS = sorted_attrs

# 关键属性索引
print("\n=== 关键属性索引 ===")
for kw in ["attack", "hurt", "fire_speed", "base_attack", "base_hurt",
           "base_power", "power", "damage", "armor_penetration",
           "critical_rate", "durability", "ammunition", "clip_capacity",
           "reload_speed", "spread", "stability", "range", "weapon_life",
           "player_hurt_additional_rate", "player_attack"]:
    for i, name in enumerate(ATTRS):
        if name == kw:
            print(f"  {kw:35s} = index {i:3d}")
            break
    else:
        # 模糊匹配
        for i, name in enumerate(ATTRS):
            if kw in name:
                print(f"  {kw:35s} ~ index {i:3d} ({name})")
                break
        else:
            print(f"  {kw:35s} = 未找到")

# field23=148 和 161
print("\n=== field23 对应的属性名 ===")
if 148 < len(ATTRS):
    print(f"  AUG field23=148: {ATTRS[148]}")
if 161 < len(ATTRS):
    print(f"  SCAR field23=161: {ATTRS[161]}")

# 看看 140-170
print("\n=== index 140-170 ===")
for i in range(140, min(170, len(ATTRS))):
    marker = " <-- AUG(148)" if i == 148 else (" <-- SCAR(161)" if i == 161 else "")
    print(f"  {i:3d}: {ATTRS[i]}{marker}")

# 保存
out = Path(r"E:\提取成果\attribute_data\attr_sorted_index.json")
out.write_text(json.dumps(ATTRS, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n已保存到 {out}")
