# 武器皮肤音效定位链（Weapon Skin Audio Locator Chain）

> 归档：2026-09-13 · 状态：**收口**（典藏 + 传世 34 卡 / 386 条，34/34 全部上音）
> 范围：音效定位专项；Weapon Skin Domain 本体已毕业（identity/grade/variant 不重开）。
> 关联：`docs/WEAPON_SKIN_GRADUATION.md` · `artifacts/active/weapon_skin_audio/`（含 `SCAN_ROUND2_REPORT.json`、`BATCH2_MATCH.json`）

## 0. 全景

```
① 业务      图鉴卡（典藏 19 + 传世 15 = 34 卡 / 24 皮；含 5 组三阶皮）
② 结构      skin_id = 111xxxx  ｜  stem = skin_XXXX_YYY
③ 引用层    ① sfx 函数行    weapon_skin_sfx_function_data（entry 19681 + CHS 9885；352 行，含 skin_id）
             ② 行为资源行    weapon_skin_behavior_res_data（entry 17205 + CHS 24842；81 行）
             ③ fx 文档      SKIN_FX_DOCS_INDEX（stem → docs / sfx_names）
④ 事件层    ① 事件池 CHS 15545（皮肤专用，175 条）
             ② FxGroup      AUDIO_FXGROUP_INDEX（7,694；EventName 2,363 / SfxName 5,331）
             ③ FEV 文件     361 riffs（g66_weapon.fev 等；事件 → 样本清单）
             ④ 动画事件表   .c159（gres 包内：EventTrack + sound\*.fev:event 绑定）← 最底牌
⑤ 样本层    FSB5：sound.gpk = 1,068 bank / 22,284 样本；样本名 ↔ 批次目录 sample/weapon/<lib>_<日期>
⑥ 匹配层    机械优先级（零 fuzzy）：①样本前缀 ②stem 直对 ③联动批次+日期 ④主题+结构；听辨=终审
⑦ 导出层    bank(.fsb) → extract_fsb → WAV；按前缀 cherry-pick
⑧ 交付层    assets/audio/weapon_skin/<dir>/ → attachments.json/js → board.html「皮肤音效」区块 → 守护测试
```

## 1. 口径（构建期纪律）

- 只覆盖 **典藏 + 传世**；以下档位视为无皮肤音效（用户口径）。
- 升格分层：**id 大→小 = 三/二/一阶**；一阶=二阶同组；`lv1/_1` 一阶专属、`lv3/_3` 三阶专属；无后缀进「通用」。
- 构建只用机械证据；**人工听辨仅作最终 validation**（不参与构建）。
- 红线：fuzzy 代号 join、entry adjacency、按面板/序号顺序猜、听辨构建、跨基准混 FID —— 违者打回。

## 2. 各层要点与坑

### ③ 引用层
- sfx 函数行 = skin_id **机械直链**（金钥匙）；`jump:N` 只算候选引用，落到 decoded row 才升级。
- 行为资源的 `fire_sfx_path / hit_sfx_path / extension_defeat_sfx` = 开火/命中/击败正主路径（.sfx）。
- 覆盖不全：函数行 75 皮、行为行 77 皮 —— **没命中 ≠ 没音**，继续往下走。

### ④ 事件层
- 事件池给"事件路径"（wskin_shoot、shuijinmeigui_fire_lv1…）= 皮肤代号主要来源。
- `.c159`（gres）能判"到底有没有声音事件"：极狐/焚古的结论就是靠它钉死的。

### ⑤ 样本层
- FSB5 = 最终真相；批次目录日期一般早于上线 2–4 周（bank 766≈2024-10 → 879≈2026-02 校准过）。

### ⑥ 匹配层（机械优先级）
1. **样本名前缀 = 皮肤代号**（全库前缀扫）
2. **stem 直对**（skin_2003_005 ↔ weapon_2003_05_*）
3. **联动批次 + 日期交叉**（同批 lib 成对武器组 ↔ 同批皮肤；事件树 g66_YYYYMMDD_*）
4. **主题 + 结构交叉**（霰弹 bolt/fire/hit/reload；弓 draw/stretch；升格 lv1/lv3）
- 假阳性先看上下文：`jihu`→激活/科技会/计划；`longxi`→龙虾；`desired`→shader 文档；`prix`/`baishe`→噪声。
- 3/4 结果：能听辨 → `confirmed`；不能 → 如实标 `inferred`（挂账，不装已证）。

### ⑦⑧ 导出与交付
- `extract_fsb(bank, outdir)` 直出 `<样本名>.wav`；多套皮肤用**组级目录**（渲染取 `(g.dir||rec.dir)`）。
- 站点区块与「时限变体」「特效与战斗表现」同级、排最后；标注由文件名语义生成（非听辨）。
- 守护：`tests/test_weapon_skin_audio_section.py`（34 块 / 逐块计数 / 阶段标记 / 文件存在 / 真实 Chrome 探针）。

## 3. 单皮定位 SOP

```
1  取钥匙：skin_id（111xxxx）+ stem（skin_XXXX_YYY）
2  引用层：rg "<skin_id>|<stem>" artifacts/active/weapon_skin_audio/*.jsonl
3  事件层：rg "<代号>" AUDIO_FXGROUP_INDEX.jsonl / FEV_SAMPLE_INDEX.jsonl
4  样本层：FSB_SAMPLE_INDEX 前缀扫（含变体）
5  未果 → 批次交叉：FEV 目录全表 ↔ 上线日期 ↔ 同批成对组
6  仍未果 → 全容器穷举（六层，见 §5）
7  导出 → 挂站 → pytest → commit
8  听辨（若有）→ 台账更新（verified / confirmed / inferred / pending）
```

## 4. 证据等级

| 等级 | 含义 | 例子 |
|---|---|---|
| 拆包直证 | 前缀 / stem / 事件链机械命中 | 极光剑、墨隐麒麟、九霄狐啸…（32 卡主体） |
| confirmed_by_user | 推断 + 用户听辨确认 | 诡秘之颅、熔炉寒霜、极狐破坏者（专属音） |
| inferred_unverified | 推断、无参考 | 焚古龙息（flame_loop / flame_shoot） |
| pending | 待定 | 水晶玫瑰 xuli_loop_layer1/2 |
| dead_ref | 声明未打包（不可听） | 见 §5 |

## 5. 死引用与例外（精确对账）

- **死引用 19 条**（FEV 声明、客户端未打包）：`shym_reload` / `shym_switch`；`1013_003_fire_loop02/03`；左轮系 `-2` 层 ×15（atk_zl×4、nucleus_atk_16×8、reload_zl×3）。
- **反向 1 条**：`nucleus_atk_16_07(1)`（打包了、未声明）。
- **例外卡 2 张**：极狐破坏者 = 专属音、与 2.5 手枪同批打包（6 条）；焚古龙息 = 推断（2 条，待参考）。
- 全库级 FEV↔FSB 完整对账未做（本次仅对 6 组皮肤族对账），留作后续专项。

## 6. 扫描边界（负证据的方法）

六层穷举：sound.gpk（全枚举）→ gres ×35（含 .c159 事件层）→ res gpk ×65 → res fpk ×64 → Documents 全树 → 动画轨道。
工具注意：rg 原生版必须 `E:/` 路径 + `-a -o -e`；窗口上下文用正则 `.{0,70}token.{0,90}`；批量扫描走 bash 后台 + 落盘（execute_code 有 5 分钟上限且超时丢输出）。全档见 `SCAN_ROUND2_REPORT.json`。

## 7. 关键文件速查

- 台账：`artifacts/active/weapon_skin_audio/`（`BATCH2_MATCH.json` 匹配总表 · `SCAN_ROUND2_REPORT.json` 扫描档 · `COVERAGE_126.json` · `WEAPON_SKIN_AUDIO_AUDIT.json`）
- 站点：`data/weapon_skin_audio_attachments.{json,js}` · `assets/audio/weapon_skin/`（285 WAV）· `board.html`
- 容器：`E:\mrzh\res\sound.gpk`（主库）· `E:\mrzh\Documents\gres\*`（含 c159）· `C:\...\Temp\snd_5ni93kzq\*.fsb`（开凿件）
- 工具：`tools/carve_fsb5_banks.py` · `extract_fsb`（lifeafter_unpacker_full）· `tools/aggregate_skin_audio.py`
- 试听：`03拆包产物/audio_review/`（历史页 + `复核_第三波/试听.html`）

## 8. 现状

- **34/34 卡上音** · 386 条 · 285 WAV · 5 组升格三层 · 测试 6/6。
- commit 链：`33005d5 → bcce2fd → 910324c → 7e12ee6 → 1db253b → 58a8954 → cf2b072`
