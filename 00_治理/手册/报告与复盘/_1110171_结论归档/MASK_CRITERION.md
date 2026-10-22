# 测量判据（MASK 口径）—— 逐位复刻说明

> 目的：把「我（viewer-auditor）在 task-42/48/53 用的五读数」钉死到可复刻程度。
> 结论先说：**我的口径 = 全窗口截图 + 「背景差分掩模」，不是固定武器框裁剪**。所以与「整帧口径」的差异来自 **criterion**，不是数据。

## 0. 一句话定义
**MASK 口径**：`frame`（开特效/当前态）与 `bg`（同布局、武器隐藏态）两张**全窗口 PNG** 逐像素求差，**差值 > 24/255 的像素构成掩模（= 武器/特效像素）**；五个读数**全部在该掩模内**统计。
**CANVAS 口径（整帧）**：同一张 `frame`，**不做任何掩模**，在整幅图像（1578×902）上统计同样的公式。

## 1. 采样前对页面做什么（顺序固定）
| 步 | 调用 | 作用 | 备注 |
|---|---|---|---|
| 1 | `await WikiWeaponViewer.open(rec, {title:'x'})`（或 board 卡片入口） | 打开皮肤 | `rec` 取自 `window.WEAPON_SKIN_MEDIA.skins[id]` |
| 2 | 轮询 `WikiWeaponViewer.__neox()` 直到字符串含 `"applied"` | 等链应用 | 之后固定 `await asyncio.sleep(8.0)` 作为 settle 余量 |
| 3 | `WikiWeaponViewer.__post(false)` | **关闭后处理** | 保证不引入 bloom 等差异 |
| 4 | `WikiWeaponViewer.__hidePanels(true)` | **隐藏面板/UI** | viewer 自身的隐藏实现；我**不再额外隐藏 DOM**、**不注入 CSS** |
| 5 | `WikiWeaponViewer.__sfxTime(<t>)` | 固定动画时间 | 默认态取 `0`；闪光取证时按 25 ms 步进扫描 `t` |
| 5b | **（SFX 相关测量）点击 `.wv-sfx` 后**再调用 adapter API | **adapter 方法门控** | **★ 2026-09-19 我独立发现并被 Lead 写入全员口径**：`window.WikiSfxAdapter` 在 `readyState==='complete'` 时、`open()` 之后仍只是 `object`，`sprites/adaptSwitches/__sfxDiag/psFallback/sprSlice/colorOrder` **全为 `undefined`**；**点开 SFX（attach）后 1 ms 内才全部变 `function`** ⇒ 正确门控是"attach 之后"，不是 `readyState` |
| 6 | `Page.captureScreenshot {format:'png'}` | **全窗口**截图（无 `clip`） | Chrome 以 `--window-size=1600,1000`、`--force-device-scale-factor=1`、`--force-color-profile=srgb`、`--hide-scrollbars` 启动 ⇒ 得到 **1578×902** PNG（窗口边框/滚动条差异） |

**（补）viewer 侧 task-45 开关 API（现行）**：`window.__cubeBright(on)` → JSON 字符串 `{cubeBright:'on'|'off', mats, rows:[{prim,value,source,on}], note:'值来源=manifest source_uniforms.u_cube_brightness；缺失不覆盖；默认 OFF'}`（`viewer.js` L2500-2515）；配套探针 `__cubeBrightProbe()`（L2498 说明）。逐 prim 归属用 **`__primShow(i)`**（保留链材质，只看可见性），**不要**用 `__primOnly(i)`（纯白材质，只适合看几何）。

**没有**做的事：不裁剪、不改 CSS、不动曝光/灯光/bloom/ACES、不改 `devicePixelRatio`、不读 canvas backing store（不依赖 `preserveDrawingBuffer`）。

## 2. "武器框 rect"的来源与数值（澄清）
- 我的掩模**不是**由一个固定 rect 得到；rect 只用于**健康检查**：`document.querySelector('.wv-canvas canvas').getBoundingClientRect()`（`RECT_JS`），在取帧前后各读一次并比较（记为 `rect_unchanged`）。历史实测：多轮均为 `1178×658`（canvas 元素尺寸）且前后一致。
- **DPR/像素比**：Chrome 以 `--force-device-scale-factor=1` 启动，viewer 内部 `setPixelRatio(min(dpr,2))` ⇒ 实际 `dpr=1`；截图坐标 = CSS 像素 1:1，**无需**再乘 DPR。
- 掩模本身来自 `bg`（见 §3），因此**自动贴合武器在画面中的真实位置/尺寸**，不依赖任何硬编码框。

## 3. 掩模（bg 差分）定义
> **★ 2026-09-19 口径变更（Lead 通报 + shader-auditor 实测）**：bg 采集**改用 `window.__primShow(-1)`**（只改 `visible`，保留链材质；实测帧中性、逐位可复现）。
> **旧写法 `window.__primOnly(-1)` 已弃用**：它会把材质换成纯白 MeshBasic，且**往返还非帧中性**（切回后留残差）⇒ OFF 帧不可复现。
> **历史读数处理**：task-42 / 48 / 56 / 58 的全部读数均用旧写法采集，**按原样保留**，仅在本文件与本报告注明"bg 采集方式=旧 `__primOnly`"；**后续一切复测一律用 `__primShow(-1)`**，新表另记 `bg_method`。

1. `bg` 帧：在**同一相机/布局/时间**下执行 `window.__primShow(-1)`（`__primShow` 定义于 `viewer.js` L2277：`i===null/undefined ⇒ 全部 visible`，否则只让 `prim===i` 的网格 visible；`-1` 无匹配 ⇒ 全部隐藏）→ 取门控帧 → 再 `__primShow(null)` 还原。
2. 取两图 `np.float32 / 255.0`，按短边对齐（`h=min(...), w=min(...)`）。
3. **掩模**：`m = (|frame − bg| 逐通道取 max) > 24/255`（严格大于）。
4. `mask_px = m.sum()`；`mask_pct = 100 · mask_px / m.size`。
5. 掩模包含：武器本体像素 + 任何"相对 bg 发生变化"的像素（特效/阴影差异）；**不包含**完全等同背景的像素。
6. 阈值 24/255 ≈ 9.4% 通道差 —— 与项目既有 `POSTER/PM4/RT28` 系列口径一致（同阈值），便于历史对比。

### 3b. ★ 帧 sha 的可比性规则（2026-09-19 Lead 升级为全队口径，来自 task-45 实测）
- **帧 sha 只在"同一 harness + 同一取帧管线"内可比**；**跨 harness 一律只比五读数**（+ 自洽性：`OFF→ON→OFF` 回到同一 OFF sha、逐 prim 归属正确）。
- 由此"锚/N0"必须是**本轮自己 harness 的改前基线**，**不得套用别人的旧锚**——task-45 实测：我（viewer-auditor）的 OFF `e62c1c58e5bdc383` / `09611e2e90b49bc0` 与 shader-auditor 报的 `49c6f3adcaea235b` / `9b08a1134bfc484e` 逐字节不同，但两条协议各自内部自洽、五读数逐项一致 ⇒ 判**跨 harness 差异，非缺陷**。

## 4. 五个读数的确切公式（均在掩模内；分母 = mask_px）
设掩模内像素的归一化 RGB 为 `R,G,B ∈ [0,1]`：
- `L = 0.2126·R + 0.7152·G + 0.0722·B`（Rec.709 亮度，**不**再做 tone map）
- **p50** = `np.median(L)`（分位数）
- **p95** = `np.percentile(L, 95)`（分位数）
- **>0.5%** = `100 · count(L > 0.5) / mask_px`
- **>0.75%** = `100 · count(L > 0.75) / mask_px`
- **暖色%** = `100 · count(R > 0.9 且 G > 0.85) / mask_px`（**不是色相判据**，是"近白偏暖高光"的双通道阈值；B 不设限）
- 另附 `meanRGB`（掩模内均值，仅作诊断）

**CANVAS 口径**：同一公式，但分母换成**整幅图像像素**（`m.size` → `h·w`），统计对象换成**全部像素**（不做任何掩模）。
> 换算关系：`>0.5`/`>0.75`/`暖色%` 在两种口径下的比值 ≈ `mask_px / (h·w)`（因为掩模内统计只覆盖一部分像素）。历史 1110177 的 `mask_px/(h·w) = 25,995/1,423,356 ≈ 1.826%`，与 `mask_pct` 一致。

## 5. 稳定门（取帧合格判据）
- **N = 5**：连续 5 帧 `sha256(PNG)[:16]` **完全相同**才接受，接受帧 = 这 5 帧的最后一帧。
- 每帧间隔 `await asyncio.sleep(1.0)`，最多 20 次尝试；`bg` 帧用 **N = 4**。
- 记录：`gate_ok` / `gate_tries` / `gate_secs` / 完整 `series`（每帧 sha16）。
- **只保证"载入内稳定"**：同一载入内不同时刻可能给出不同 sha（历史实测 1110177 `t1/t3/settled` 三帧 sha 相同=稳定；但跨载入逐字节会变）⇒ **不要用单一 sha 当跨会话基线**，跨会话用五读数。
- settle 判据（另一条独立门）：`__texReady().meshes[*].envMode` 全为 `source_ibl`（100 ms 轮询、上限 20 s）⇒ 用于避开 task-40 的 IBL 空窗。

### 5b. ★ 层分离实验的判据修正（2026-09-19，task-62(c) 实测 + Lead 裁决采纳）
- **`WikiSfxAdapter.sprites(on)` / `models(on)` 不控制 ParticleSystem**：SFX 开启期间 PS 一直在逐帧动画 ⇒ **"间隔 ≥1 s 两帧同 sha"这条稳定性判据在层分离实验里不适用**（不是缺陷，是开关粒度）。
- **替代判据（已用并被采纳）**：① `effect-only` 与**默认 OFF**（SFX 未动、关掉层开关后重新门控得到的帧）逐层比较 → 分离各层贡献；② `__probe()` 计数（`sprites[].visible`、`models[].visible`、`systems[]`）；③ 全白像素占比（画布 + 掩模内）。
- **必守**：层开关往返结束后要**关掉 SFX 并重新门控**取得 OFF 帧，要求与默认 OFF 逐字节一致（**不得复用更早的帧当 OFF 基线**）。task-62(c) 实测该一致性成立（`e62c1c58e5bdc383`）。
- **已知限制（不要美化）**：`models(true)` 会让无贴图的 `<Model>` 节点以"实心卡片"呈现 ⇒ 画面出现**大面积白块**（画布全白 5.65%、掩模内 45.79%；默认态 0.09%）。根因是源 `.sfx` 里 Model 节点不声明贴图（`diffuse+emissive` 缺 `e` 采样塑形）⇒ **`models` 保持默认关**，不为其加尺寸/不透明度/朝向"美化"约束。

### 5c. 来源字段读法（清单统计口径）
- 节点来源请用 **`source_sfx_id ?? source_sfx`**：`_hit.sfx` / `_jisha.sfx` 的节点带 `source_sfx`；**新并入的 23 个 `_dg.sfx` 节点只有 `source_sfx_id="gres\0057.gpk#32153"`**（`source_sfx_name_inferred` 为推断名），且 dg 的 Dummy 带 `__dg` 命名空间后缀、dg Model 以 `model_name` 指向 `mod_skin_2003_029_dg_*.gim` ⇒ 只按 `source_sfx` 统计会把这 23 个漏成"无来源"。

## 6. 脚本与函数（可直接调用，勿重写）
所有脚本在 `%TEMP%`（测量机同一用户）：
| 脚本 | 用途 | 关键函数（行号） |
|---|---|---|
| `%TEMP%\reg48_followup.py` | 通用「默认帧 + bg + 五读数」；1110024/1110177 复核 | `gate()` L125、`five()` L137、`open_skin()` L152、`capture()` L169、`RECT_JS` L24、Chrome 启动参数 L193-194 |
| `%TEMP%\reg48_swp.py` | 固定时间扫描（25 ms 步进）抓闪光窗口 | `gate()` L144、逐帧差分 L196-200、`STEP_JS`（逐步对象读数）L60 |
| `%TEMP%\reg48_flash.py` | 墙钟突发采样（80 ms 名义）+ 包围盒/贴图 | `gate()` L163、`capture` L192-203、差分 L238、`FXINFO_JS`（Box3/贴图）L60 |
| `%TEMP%\reg48_ibl_ab2.py` | 同会话 A/B（Fetch 拦截换资源字节） | `handle()`（拦截处理器）、`capture()` |
| `%TEMP%\ab42_final.py` | 早期 task-42 A/B（Fetch 拦截） | `_handle_paused()`、`five()` |
| `%TEMP%\reg48_settle.py` / `reg48_settle_pre.py` | settle 判据 + 窗口/稳定态对照 | `SETTLE_JS` |

复刻最小步骤（伪码）：
```python
# 1) 打开皮肤 → wait neox → sleep(8)
# 2) __post(false); __hidePanels(true); __sfxTime(0)
# 3) frame = await gate(c, n=5)          # 5 帧同 sha
# 4) __primOnly(-1); bg = await gate(c, n=4); __primOnly(null)
# 5) m = (|frame-bg|.max(axis=2) > 24/255)
#    L = 0.2126R+0.7152G+0.0722B
#    p50=median(L[m]); p95=percentile(L[m],95)
#    gt0.5 = 100*mean(L[m]>0.5); gt0.75 = 100*mean(L[m]>0.75)
#    warm  = 100*mean((R[m]>0.9)&(G[m]>0.85))
```

## 7. 历史读数（同口径，供换算对照）
| 皮肤 / 状态 | 口径 | p50 | p95 | >0.5% | >0.75% | 暖色% | mask% | 帧 sha16 |
|---|---|---|---|---|---|---|---|---|
| 1110177 默认（settle 后门控） | mask | 0.2829 | 0.5745 | 18.242 | 0.989 | 0.689 | 1.826 | `e62c1c58e5bdc383`（跨载入会变） |
| 1110171 默认（settle 后门控） | mask | 0.1232 | 0.4865 | 3.394 | 0.273 | 0.106 | 2.449 | `48b6c95c1165c80a` |
| 1110024 默认（改后） | mask | 0.4262 | 0.7866 | 16.968 | 5.616 | 3.775 | 4.368 | `c336d323330c1166` |
| 1110145 改后 | mask | 0.228 | 0.4443 | 2.158 | 0.020 | 0.000 | 4.531 | `fe7c9a231358b3ce` |

> 与整帧口径的换算示例（1110177 默认）：mask 口径的 `>0.5%=18.242` 若换成整帧分母，约 `18.242 × 1.826% ≈ 0.333%`；`p50/p95` 是分位数、**不能**用比例换算（掩模改变了样本集合）。
