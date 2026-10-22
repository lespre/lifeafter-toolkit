# PM7FIX2 验收：`progFamilyOf` 回退修复（靶子冻结 `viewer.js` sha16 `41EFDE0A316DEBB7` / 288,700 B）

只读磁盘；证据 `_target_1110171/PM7FIX2_*`。**未改任何文件**（负控仅改内存响应）。
**靶子稳定性**：开跑 `41efde0a316debb7` → 结束 `41efde0a316debb7` ⇒ **全程稳定 = True**（读数有效）
**浏览器卫生**：只起 1 个 Chrome（独立 profile，端口 10016）→ `taskkill /T /F` 杀整树 → `netstat` LISTENING=`[]`、残留 chrome.exe=**0** ⇒ **已关闭、无残留**

## A) 7 皮肤总表（board/默认页；expected = 磁盘 manifest 的 primitives 数）

| 皮肤 | applied / expected | applied_ok | failed | missing | family_source | 逐 prim matVisible | 全 map 非 None | mask% | 帧 sha16 |
|---|---|---|---|---|---|---|---|---|---|
| 1110024 | 5 / 5 | ✓ | [] | [] | `shader` | 全 True | ✓ | 6.74% | `1476e0a3293d3191` |
| 1110129 | 5 / 5 | ✓ | [] | [] | `shader` | 全 True | ✓ | 7.00% | `35b58bc5ae59203e` |
| 1110145 | 7 / 7 | ✓ | [] | [] | `shader` | 全 True | ✓ | 9.15% | `16a5ae74d102e07c` |
| 1110152 | 2 / 2 | ✓ | [] | [] | `shader` | 全 True | ✓ | 7.49% | `d384a68fce420917` |
| 1110165 | 4 / 4 | ✓ | [] | [] | `shader` | 全 True | ✓ | 6.81% | `7dbfc3f591a16624` |
| **1110171** | **7 / 7** | ✓ | [] | [] | **`shader_kind`** | 全 True | ✓ | **3.16%**（原 0.00%） | **`94dbd1006bb48a38`** |
| 1110177 | 3 / 3 | ✓ | [] | [] | `shader` | 全 True | ✓ | 1.78% | `4c4b8db1d2d4dada` |

- **判据全中**：`applied == expected_prims` 7/7 全过 ✓ · `failed=[]` · **不再出现 `mapW=None` 全体** ✓ · `mask` 回到常态量级（1110171 = **3.16%** 而非 0.00%）✓
- 逐 prim `map/metal/rough/normal`：**`map/rough/normal` 全部非 None**；`metal=None` 仅出现在**晶体族 prim**（1110171 prim1/2/3/5/6、1110177 prim1/2）——晶体族本就不绑定 `metalnessMap` ⇒ 属预期，不是缺失 ✓
- **`family_source`（第 6 项）**：**1110171 = `shader_kind`**（7/7 prim）✓；**其余 6 皮肤 = `shader`** ✓ —— 与你给的期望完全一致
- 逐 prim family：1110171 = prim0/4 `pbr_weapon` + prim1/2/3/5/6 `pbr_crystal`；`required_slots` 与 family 匹配（crystal = `['Tex0','NormalMap','t_basecolor']`，prim6 仅 `['Tex0','NormalMap']`）✓ 全部 `status=applied`、`runtime_missing=[]`、`hidden=None`

## B) 1110171 截图（我看过）
`_target_1110171/PM7FIX2_board_1110171.png`（1178×717）**sha16 `94dbd1006bb48a38`**
**目视**：武器**已正常出画** —— 蓝紫晶体尖刺 + 中央粉紫核心 + 深色金属枪身，构图居中、**无 UI 残留、无全黑、无洋红占位** ✓（此前为 `mask=0.00% / sha 7ad37f89f32f4148` 的不出画状态）

## C) 负控（专项：报告与实际可见性是否一致）—— **一致，无静默通过** ✓
方式：`Page.addScriptToEvaluateOnNewDocument` 注入 `window.fetch` 包装，**仅对内存响应**把 `1110171` prim1 的 `textures.t_basecolor.local_file` 置为 `null`（**键保留** ✓），**未碰磁盘**。
命中证据：`window.__negCtrlPatched = {"url":"…/1110171/neox_material.json?t=1789739797274","prim":1}` ✓

| 观测 | 读数 |
|---|---|
| `__neox().applied` | **6**（7−1，仅该 prim 掉出） |
| `__neox().failed` | `[{prim:1, material:"skin_1003_012_1", runtime_missing:["t_basecolor"], family:"pbr_crystal", **hidden:true**}]` |
| `__neox().missing` | `[{prim:1, slots:["t_basecolor"], family:"pbr_crystal", **hidden:true**}]` |
| 该 prim 状态 | `status=**failed_hidden**` · `runtime_fail_closed=true` · `hidden=true` |
| **实际可见性**（`__meshDump`） | mesh「_2」prim1：**`matVisible=False` · `fragLen=0` · `hasMap=False`**（其余 6 个 mesh `matVisible=True` / `fragLen=24556`）✓ |
| `__matDump` | mesh1 `map=None`，其余 mesh `map=1024` ✓ |
| mask / 帧 | 3.06%（对比修好态 3.16%，差异小是因为该皮肤 5–7 个 prim 为**同几何叠壳**）· `d3b62a2789be45f5` |

⇒ **报告（`hidden:true`）与实际可见性（`matVisible=false/fragLen=0`）逐条一致** ✓ 缺必需槽时**明确标 hidden、不静默通过** ✓

## D) 命令
```
venv\Scripts\python.exe %TEMP%\PM7FIX2.py     # A/B/C 一次跑完（含开跑/结束 viewer sha 记录）
```
产物：`PM7FIX2_result.json` · `PM7FIX2_board_<7皮肤>.png` · `PM7FIX2_negctrl_1110171.png` · 本报告
