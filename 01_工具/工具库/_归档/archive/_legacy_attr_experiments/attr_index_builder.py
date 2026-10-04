# -*- coding: utf-8 -*-
"""从 attribute_data_chs.nxs 英文属性名表建立索引→属性名映射"""
import struct, json
from pathlib import Path

fp = Path(r'E:\提取成果\attribute_data\attribute_data_chs_4D97783A1FC8AFEC.bin')
data = fp.read_bytes()

# 英文属性名表从 @15557 开始，按字母顺序连续存放
# 用已知属性名字典做最长匹配
KNOWN_ATTRS = [
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
    "cut_tree_recover_prob", "cut_tree_speed_addition_rate",
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
    "hurt_reduction_rate_ignore_compress", "immune_blow", "immune_pure_blow",
    "immune_pure_blow_down", "immune_pure_repulse", "immuse_immuse_blow",
    "increase_in_duty_points", "increased_combat_proficiency",
    "increased_sound_when_move", "infect_hurt_reduction_rate",
    "infect_monster_dmg_dec_rate", "infection", "infection_recover",
    "infrastruct_cost_ratio", "infrastruct_hp_ratio",
    "infrastruct_hurt_additional_rate", "infrastruct_time_ratio",
    "init_hurt_additional_rate", "init_hurt_additional_rate_ignore_compress",
    "injured_instant_kill_rate", "inverse_tower_critical_hurt_addition_rate",
    "inverse_tower_critical_rate", "inverse_tower_hurt_additional_rate",
    "inverse_tower_hurt_weakness_additional_rate", "inverse_tower_vulnerable_rate",
    "item_store_bullets_rate", "jump_add_height_rate", "jump_cd_time_addition",
    "jump_hurt_additional_rate", "jump_hurt_reduction_rate",
    "jump_speed_addition", "kill_player_extra_drop_rate", "laiwenhuanghun_chase",
    "laiwenhuanghun_sight", "large_dot_hurt_reduction_rate", "life",
    "light_weapon_distance_additional_rate", "light_weapon_hurt_additional_rate",
    "light_weapon_hurt_reduction", "light_weapon_hurt_reduction_rate",
    "magazine_capacity", "mailing_costs_reduce_ratio", "maker_craft_exp_extra_ratio",
    "manor_plant_and_plant_growth_accelerated_ratio", "max_alienation_addition",
    "max_breath_addition", "max_breath_additional_rate", "max_bullet_count_num",
    "max_coolant_addition", "max_coolant_additional_rate", "max_hp",
    "max_hp_addition", "max_hp_additional_rate", "max_hp_additional_rate_final",
    "max_infection_addition", "max_move_sound", "max_place_amount", "max_shield",
    "max_shield_addition", "max_shield_additional_rate",
    "max_shield_additional_rate_final", "medicine_recovery_rate",
    "medicine_time_addition_rate", "melee_cd_cap", "mf_duration_addition_rate",
    "mislead", "monster_factor_head_add_rate", "monster_hurt_additional_rate",
    "monster_infection_addition", "monster_skill_cool_down_rate", "move_sound",
    "new_bag_capacity", "new_infection_change_percent_per_second",
    "new_infection_change_value_per_second", "new_infection_extra_max_value",
    "nucleus_bd_durability_reduce_rate", "nucleus_temp_level",
    "num_per_durability_addition", "on_vehicle_hurt_additional_rate",
    "on_vehicle_hurt_reduction_rate", "overflow_recover_radio",
    "overload_burn_damage_addition_rate", "overload_coolant_cost_reduce",
    "parry", "penetration_hurt_red_rate", "player_breath_fall_speed",
    "player_clip_capacity_num", "player_energy_cost_extra_ratio",
    "player_energy_exp_extra_ratio", "player_energy_exp_mission_ratio",
    "player_hurt_additional_rate", "player_hurt_reduction_rate", "player_max_hp",
    "player_sudden_event_rate_reduction", "player_suffocation_extra_hurt",
    "power", "power_addition_rate", "power_ratio_base_after_compress",
    "power_ratio_delta_after_compress", "prepare_time", "protect_hunger",
    "protect_sub_max_infection", "pursue_range", "qili_addition", "qili_attack",
    "qili_increase_ratio", "qili_jump", "qili_reduce_ratio",
    "qili_run_reduce_ratio", "radius", "range_hurt_reduction_rate",
    "rear_seat_force_dec", "recover_qili_rate", "reduce_collect_durability_ratio",
    "reduce_exp_with_durability_reduce_ratio", "reload_ammo_ratio",
    "reload_hurt_reduction_rate", "reload_speed_additional_rate",
    "res_critical_chance_up", "resist", "resist_blizzard_rate",
    "resist_infect_level", "resist_marsh_rate", "resist_sand_rate",
    "resist_storm_rate", "rock_critical_rate", "rock_extra_critical_rate",
    "run_speed_addition", "run_speed_additional_rate", "satiety",
    "satiety_addition", "satiety_recover", "serum_hp_recovery_rate",
    "serum_recover_addition_hp", "serum_recover_addition_rate",
    "serum_recover_addition_shield", "serum_shield_recovery_rate", "sharp",
    "sharp_addition", "sharp_display_1", "sharp_display_2", "sharp_force",
    "shield_overload", "shield_recover_reduce_rate", "shield_recovery",
    "shield_recovery_rate_from_drone", "shield_recovery_rate_from_drone_by_player",
    "shoot_fighter_exp_extra_ratio", "shoot_fighter_exp_reduce_ratio",
    "shooting_distance_addition", "shuxingzhanshi_armor",
    "sight_breath_recover_additional_rate", "sight_range",
    "silver_coin_addition_rate", "sniper_rifle_hurt_additional_rate",
    "sniper_rifle_hurt_reduction_rate", "sp_effect_cool_down_rate",
    "sp_effect_exempt_ts", "sp_effect_hurt_reduction_rate",
    "sp_effect_rate_addition", "sp_effect_value", "special_power_addition_rate",
    "speed_addition", "speed_additional_rate", "speed_change_proportion",
    "spore_hp_recover_addition_rate", "spore_progress_addition_rate",
    "spore_recover_addition_rate", "spore_recover_hp_addition_rate",
    "spore_recover_shield_addition_rate", "spread_dec", "stability_value",
    "store_bullets_extra_ratio", "store_spore",
    "strategy_equip_alive_time_addition_rate",
    "strategy_equip_cool_down_reduction_rate",
    "strategy_equip_hurt_additional_rate", "strategy_equip_hurt_reduction_rate",
    "strategy_equip_magazine_capacity_addition_rate",
    "stronghold_repair_cost_reduce_rate", "sudden_event_interval_addition",
    "survival_energy_recover", "survival_exploration_force_max_infection",
    "survival_exploration_force_min_infection",
    "survival_exploration_infection_not_change", "swim_speed_addition",
    "swim_speed_additional_rate", "switch_weapon_addition_rate",
    "tactic_aiming_time_reduction_rate", "tactic_blasting_blow_down_rate",
    "tactic_born_buff_extra_level", "tactic_buff_extra_duration",
    "tactic_cd_reduction_rate", "tactic_deployment_speed_addition_rate",
    "tactic_dot_range_addition_rate", "tactic_dot_sustained_damage_value",
    "tactic_drone_critical_addition_rate", "tactic_drone_hurt_reduction_rate",
    "tactic_drone_imprisoned_time", "tactic_drone_init_speed_reduction_rate",
    "tactic_drone_max_speed_reduction_rate", "tactic_drone_mf_shape_addition_rate",
    "tactic_drone_recovery_value", "tactic_drone_self_speed_addition_rate",
    "tactic_drone_speed_reduction_rate_per_second", "tactic_drone_supply_cd",
    "tactic_drone_supply_ratio", "tactic_emp_shield_hurt_addition_rate",
    "tactic_emp_speed_addition_rate", "tactic_entity_extra_alive_time",
    "tactic_extra_usable_num", "tactic_fire_distance_addition",
    "tactic_ice_wall_extra_alive_time", "tactic_imitation_hurt_addition_rate",
    "tactic_imitation_hurt_value", "tactic_imitation_speed_addition_rate",
    "tactic_mf_extra_duration", "tactic_mf_extra_level",
    "tactic_shoot_speed_addition_rate", "tactic_special_cd_reduction_rate",
    "tactic_split_bomb_hurt_add_rate", "tactic_throw_speed_additional_rate",
    "temp", "temp_addition", "temperature_down_speed_reduction_rate",
    "temperature_up_speed_reduction_rate", "throw_speed_addition_rate", "thump",
    "time_scale_addition_rate", "trap_target_time", "tree_critical_rate",
    "tree_extra_critical_rate", "tumble_additionnal_rate",
    "undead_hurt_additional_rate", "unlimited_bullet", "unlimited_bullet_works",
    "use_store_spore_time_cd_reduction_value", "vehicle_armor_addition",
    "vehicle_hurt_addition", "vehicle_hurt_addition_rate",
    "vehicle_max_hp_addition", "vehicle_max_speed_addition_rate",
    "vehicle_road_acceleration_additional_rate", "vehicle_road_speed_addition_rate",
    "virus_hurt", "virus_hurt_additional_rate", "virus_hurt_ratio",
    "virus_hurt_reduction_rate", "virus_resistance",
    "water_plant_growth_additional_rate", "water_rock_growth_additional_rate",
    "weak_time_reduction_rate", "weakness_burn_damage_addition",
    "weakness_electromagnetic_damage_addition", "weakness_freezing_damage_addition",
    "weapon_fighter_exp_extra_ratio", "weapon_life_reduce_ratio",
    "weather_effect_value_addition_rate", "weight_level",
    "wild_monster_dmg_dec_rate", "work_collector_exp_extra_ratio",
    "yh_base_infect_defense_up_ratio", "yh_break_level", "yh_extra_bag_capacity",
    "yh_infect_defense_level",
]

# 按长度降序，最长匹配
sorted_attrs = sorted(KNOWN_ATTRS, key=len, reverse=True)

str_start = 15557
attr_names = []
pos = str_start
while pos < len(data):
    matched = None
    for name in sorted_attrs:
        nb = name.encode('ascii')
        if data[pos:pos+len(nb)] == nb:
            matched = name
            break
    if matched:
        attr_names.append(matched)
        pos += len(matched)
    else:
        pos += 1
        if len(attr_names) > 0 and pos - str_start > 40000:
            break

print(f"属性名总数: {len(attr_names)}")
print()
print("=== index 140-170 ===")
for i in range(140, min(170, len(attr_names))):
    marker = " <-- AUG field23=148" if i == 148 else (" <-- SCAR field23=161" if i == 161 else "")
    print(f"  {i:3d}: {attr_names[i]}{marker}")

print()
print("=== 关键属性索引 ===")
for kw in ["attack", "hurt", "fire_speed", "base_attack", "base_hurt",
           "base_power", "power", "damage", "armor_penetration",
           "critical_rate", "durability", "ammunition", "clip_capacity",
           "reload_speed", "spread", "stability", "range", "weapon_life"]:
    for i, name in enumerate(attr_names):
        if name == kw:
            print(f"  {kw:30s} = index {i:3d}")
            break
    else:
        for i, name in enumerate(attr_names):
            if kw in name:
                print(f"  {kw:30s} ~ index {i:3d} ({name})")
                break

# 保存映射
out = Path(r"E:\提取成果\attribute_data\attr_index_map.json")
out.write_text(json.dumps(attr_names, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n映射已保存到 {out}")
