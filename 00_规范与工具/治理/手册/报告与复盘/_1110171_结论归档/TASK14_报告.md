# TASK-14 证据汇总（1110129 修复后验收 + 背景图 + prim4 rad 登记）

只读项目文件；写入仅 `03拆包产物\_target_1110171\TASK14_*` 与 `1110129/poster.webp`。

## 1. 二值结论：**「有色可辨」**（不再是纯黑剪影）
- **修复前（Lead 亲存帧 `BLACK129_diag_default_1110129.png`, 02:39, 1178×658）**：目视 = **纯黑剪影**（步枪形状全黑、无任何色彩/高光）✓ 与 Lead 基线「剪影区平均亮度 15.2 ≈ 背景 15」一致。
- **修复后（本轮 `TASK14_1110129_board_full.png`, 1178×717）**：目视 = **深色金属 + 蓝紫镶边 + 白色高光 + 金色线圈**，有色可辨 ✓
- 修复后读数（board 入口，掩模=材料无关剪影 51,066 px = **6.05%** 画布）：
  `mean L=19.87 / p50=8.51 / p95=70.72 / max=255`；金 0.02% · 紫 0.50% · 银 0.95%。
- ⚠ **未做跨尺度像素对齐**：Lead 的修复前帧是 1178×**658**、我的是 1178×**717**（画布高不同 ⇒ 相机 fit 不同）⇒ 不做跨尺度 Δ，改用「Lead 基线数值 + 我的修复后同口径数值 + 目视二值判定」。
- 旁证（数据层已生效）：`__acceptanceReport().ibl_faces` = 每 prim 六面全齐
  `qiangpi_f0..f5_m0.png` ✓；`__cubeDirProbe` = `{"qiangpi":{"faces_glob":"src_cube/faces/qiangpi_f{0..5}_m0.png","urls":[f0..f5 六条]}}` ✓
- **另一条独立事实**：我 01:17 抓的帧（通配符事故之前）与修复后帧**逐像素几乎相同（Δmean=0.00，仅 2 px |Δ|>8）**
  ⇒ 本次修复的效果是**把画面恢复成通配符事故前的外观**（不是"新外观"）。

## 2. 两个入口（读数不一致，如实列出）
| 指标 | board 卡片（`openSkin3D`→`open(registry)`） | `?lab=1` |
|---|---|---|
| 剪影占画布 | 6.05% | 5.86% |
| 剪影 mean L | **19.87** | **28.86** |
| p50 / p95 | 8.51 / 70.72 | 14.07 / 78.23 |
| 金 / 紫 / 银 % | 0.02 / 0.50 / 0.95 | 0.99 / 2.20 / 2.33 |
| 帧 sha16 | `446c9572530d43a3` | `76eb4b9417864299` |
| 背景图请求 / `background` | true / `"texture"` | true / `"texture"` |
⇒ **lab 页明显更亮更彩（mean +45%、金 ×50）**，两入口**不一致** ✓

## 3. prim4 `rad` 不一致（只登记，未改 viewer）
| prim | board 默认页 | `?lab=1` |
|---|---|---|
| prim0–3 | len=24556 · q_envW=true · 079956=true · **rad=True** | 同左 |
| **prim4** | **len=0 · q_envW=false · 079956=false · rad=False** ✗ | len=24556 · q_envW=true · **rad=True** ✓ |
⇒ 默认页 prim4 **完全无注入**（`userData.__frag` 为空），lab 页正常注入。

## 4. 背景图确认：**8 个皮肤全部已应用**
- `_shared/bg_weapon_skin_ingame.png` = 1672×941, 1,255,811 B, sha16 `e60c1a1d5e16b1b4` ✓ 存在
- 8 皮肤逐一：`Network` 均请求到 `bg_weapon_skin_ingame.png` = **true** ✓；`__matDump().background` = `"texture"` ✓
- 像素级（取无-mesh 帧作纯背景）：7/8 与背景图重采样后**平均差 2.55**、像素差>8 仅 7.6% ⇒ 背景即该图 ✓（1110024/1110129/1110145/1110152/1110165/1110171/1110177）
- **1110169 例外**：无几何/无 canvas 帧可做像素确认（其 `neox_material.json` 404 已知），但其背景图请求已发出且 `background="texture"` ⇒ 仅"请求+类型"级证据，像素级**未确认**（如实登记）

## 5. 海报重拍
`1110129/poster.webp`：**1600×900** · **65,408 B**（旧 65,720）· sha16 **`265dc756e3b5f32e`** · 非背景 14.8% · 武器区 p50 **35.8** / p95 65.9 · **uiPix=0** · 主体高 **558 px = 62.0%** · bbox 未触边 · `rect_unchanged=true` · 旧图备份 `POSTER_1110129_old.webp`（sha16 `9da70e4aeb2915ff`）

## 6. 跑过的命令
```
venv\Scripts\python.exe %TEMP%\TASK14_verify.py      # 两入口测量 + 8 皮肤背景图
venv\Scripts\python.exe %TEMP%\TASK14_post.py        # 同一像素集对比 + 背景像素比对 + 重裁海报
venv\Scripts\python.exe %TEMP%\TASK14_ba.py          # 与 Lead 修复前帧配对（跨尺度，仅作背景说明）
```
