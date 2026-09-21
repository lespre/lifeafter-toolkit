from toolkit_core.reward_pool_export import normalize_rows


def test_normalize_rows_keeps_verified_name_and_marks_missing_name():
    source_rows = [
        {
            "pool_id": 391782,
            "slot": 0,
            "item_id": 94877,
            "quantity": 1,
            "prob_note": "0.00907",
            "initial_weights": 17158,
            "reward_jump": 122355,
            "row_start": 247286,
            "row_key": 570437055,
        },
        {
            "pool_id": 391782,
            "slot": 1,
            "item_id": 104999,
            "quantity": 1,
            "prob_note": "0.00532",
            "initial_weights": 1,
            "reward_jump": 2293,
            "row_start": 2313,
            "row_key": 3258032996,
        },
    ]

    rows = normalize_rows(source_rows, {94877: ("鸾鸟跷跷板", "common_item_data")})

    assert rows[0]["名称"] == "鸾鸟跷跷板"
    assert rows[0]["名称来源"] == "common_item_data"
    assert rows[1]["名称"] == "待回填"
    assert rows[1]["名称来源"] == "当前 common_item_data/gift_data/all_equips 均未按 ID 命中"
    assert rows[1]["reward_jump"] == 2293


def test_validate_slot_coverage_requires_a_gapless_unique_range():
    from toolkit_core.reward_pool_export import validate_slot_coverage

    coverage = validate_slot_coverage([
        {"slot": 0, "item_id": 100, "quantity": 1},
        {"slot": 1, "item_id": 101, "quantity": 1},
        {"slot": 2, "item_id": 102, "quantity": 1},
    ])

    assert coverage == {"row_count": 3, "slots": [0, 1, 2]}
