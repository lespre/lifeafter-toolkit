# CB1_全局常量真值搜索报告（只读，2026-09-19，toolchain-auditor）

## 结论：**五个量全部取不到真值 ⇒ unresolved**（不是"对得上"，是"没得对"）

| 量 | 结果 | 出处/证据 |
|---|---|---|
| `u_ambient` | **只有声明，无值** | `E:\LifeAfter\Documents\gres\0049.gpk` @1602528278：`cbuffer NeoxUBOGlobal1 : register(b1) { float4 u_ambient : packoffset(c0); ... }`；@1594971328：`layout(std140) uniform NeoxUBOGlobalParamsBlock1 { highp vec4 u_ambient; ... }` |
| `u_dir_color` | **只有名字** | 0049.gpk（6 处命中，1594988596 等）；`u_dir_direction` 在 0049 **0 命中** |
| `u_env_day2night_exposure` | **只有名字（截断形）** | `E:\mrzh\Documents\gres\0041.gpk` 命中 `day2night_exposur(e)`（同处含 u_ambient/u_dir_color/u_hdr_luminance） |
| `u_hdr_luminance` | **只有名字** | 0049.gpk @1599129853（`u_hdr_luminance.x`）；0041.gpk 亦有 |
| `NeoxUBOGlobal1/3` | **cbuffer 名（声明）** | 0049.gpk 2 处；证明 cb1 由 HLSL/GLSL 声明、值由 CPU 填 —— 与 shader-auditor 结论一致 |

命中处的"float 读数"全为随机字节（例 `7.101e-31 / 1.854e-39 / 1.65e+22`），**无任何成组的三元组**（ambient 标量 + dir_color 三分量 + dir_direction 三分量）。

## 试过的路（逐条）
1. **`Documents\gres\*.gpk` 原始扫描**（`0049`/`0041`/`0048`，各 2.0 GB，rg -a + Python 偏移定位，各 4.2/4.2/3.8 s）
   ⇒ 命中全是**着色器源码/反汇编文本**（`NEOX_GLES_USE_UBO`、`_VTF`、`planet_pos`、`fog_color`、`row_major`、`_lastframe` 等）⇒ **声明，无值** ✗
2. **`03拆包产物\_nxs配置\`**（`1B249D5C9984E1B4.nxs` 900 KB · `weapon_skin_data.nxs` 9.8 KB）⇒ 5 个名字 **0 命中** ✗
3. **场景配置** `fpk_scene\013|020|021\strings.txt`（161/96/55 MB）⇒ 唯一相关键 **`enable_day2night = "1"`**（开关，非曝光值）✗ 无 ambient/dir/exposure 数值
4. **配置表**：`config_work\path_tables` 有 weather 族表（`camp_style_weather_far_ls_data` / `coral_boss_weather_data` / `music_light_conf_data` …）但**无 ambient/dir-light 数值表**；已解析 JSON（50 MB / 131 MB）只有脚本符号名（`set_ambient`、`set_ambient_color_intensity`、`u_ambient_lit_factor`（中文注释"暗部提亮系数"）、`u_dir_lighting_intx`、`u_dir_mode`）⇒ **名字与语义标签，无值** ✗
5. **全局字符串索引** `精拆\strings_index.jsonl`(58 MB) · `精拆新版`(16 MB) · `精拆py3` ⇒ 同上，仅脚本 doc 名；`NeoxUBOGlobal`/`u_hdr_luminance`/`u_env_day2night_exposure` **0 命中** ✗

## 对 `viewer.json` 的影响（**不裁，只报**）
`hemi 0.8 / key 1.5 / fill 0.5` **无法与源对照**（源真值不可得）⇒ **不能声称它们是源值** ✗；现状应继续标 **fitted/approximate** ✓。`uIblScale 0.25` 同样 **无源** ✗（本轮未找到任何 IBL 强度常量）。

## 可行但需另批授权的路径（仅建议）
cb1 由 **Weather 组件逐帧填充**（证据：Weather 表族 + `Weather.set_ambient` / `set_ambient_calibration_params` / `reset_ambient_calibration_params` / `do_set_ambient` + `enable_day2night` 开关）⇒ 静态包内不可能有真值 ⇒ 只能**运行时取**（hook 实进程 / 绘制帧读 cb1）※ 不在本次只读授权范围