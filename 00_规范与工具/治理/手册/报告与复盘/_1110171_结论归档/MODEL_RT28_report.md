# task-28 结论：**不是回归**（稳定性门 + 同会话 A/B 双证）；暗帧根因 = IBL cube 未绑定 ⇒ 武器全黑（受控复现）

**adapter 现状**：`2E61C5234BB37CED`（55,263 B，20:43:46）—— 已确认在树上，未被我的 A/B 留在备份版（见文末运维）。
**结论一句话**：`2E61C5234BB37CED`（当前）与 `FFF6180DF4ED5BAB`（备份）在**同一浏览器会话内、稳定性门下逐字节等价**；
零星暗帧在两版**都**出现，且能用"屏蔽 IBL cube 面"**受控复现到完全相同的帧 sha**。⇒ **汇总里"变黑回归"那条应更正**。

## 一、稳定性门 A/B（同会话，`Network.setCacheDisabled=true`，门=连续 5 帧 sha 完全相同）
| 皮肤 | 当前 adapter meanL (n) | 备份 adapter meanL (n) | 当前稳定 sha | 备份稳定 sha | 暗帧 |
|---|---|---|---|---|---|
| **1110129** | **24.82** (5) | **24.82** (5) | `35b58bc5ae59203e` (5/5) | `35b58bc5ae59203e` (5/5) | 0/5 · 0/5 |
| **1110171** | **51.53** (3) | **51.53** (3) | `94dbd1006bb48a38` (2/3)、`5bb12eb31ea449f9` (1/3) | `94dbd1006bb48a38` (3/3) | 0/3 · 0/3 |
| 1110024（对照） | **82.54** (2) | **82.54** (2) | `9afe94527d730f96` (2/2) | `1476e0a3293d3191` (2/2) | 0/2 · 0/2 |
| 1110152（对照） | **28.81** (2) | **28.81** (3) | `8caeab368ca0cd85` / `2e8abb874ce3429b` | `d384a68fce420917` (3/3) | 0/2 · 0/3 |

- 门通过率 **24/24**，每例都是**第 5 帧**即满足（`gate_tries=5`）。
- 每例 `handle_present=false`、`__sfxTime(0)=false`：测量流程（board 默认页）**从不点 SFX 按钮**，而 `viewer.js:771-780` 的 `attachEffects()` **唯一调用点**在 `toggleEffects()` 里 ⇒ 适配器**根本没进入调用路径**（1110129 的 `effects.status="none"`、按钮 `disabled=true`，连点都不可能）。
- 数据：`MODEL_RT28B_gate.json`（21 例）+ `MODEL_RT28B_gate2.json`（3 例，补完对照）；截图 `MODEL_RT28B_<phase>_<skin>_<k>.png`。

## 二、暗帧频率（非门控、含更早的独立会话，仅作频率参考）
| adapter | 1110129 暗帧(meanL<5) |
|---|---|
| 当前 `2E61C5234BB37CED` | 2/6（0.28、0.28；其余 37.86） |
| 备份 `FFF6180DF4ED5BAB` | 1/8（0.28；其余 37.86） |
| 门控样本（两版合计 24 例） | 0/24 |

**暗帧的 sha 在两版**完全相同：`516b56cc43081bdf`、meanL `0.28`、p50 `0.0`、mask `7.27%`。
⇒ 暗帧与 adapter 版本**无关**（这是"两版都会偶发"的直接证据）。非门控频率 3/14 ≈ 21%，样本小、只作量级参考；门控 0/24 与前者不完全一致（门多取 ~6 帧/~7 s，可能本身有"等一等"的保护效应），**这一点我不下结论，标 unresolved**。

## 三、暗帧根因：**已受控复现（这是关键证据）**
| 受控实验（CDP `Network.setBlockedURLs`，只读、不改文件） | 帧 sha16 | meanL | p50 | mask |
|---|---|---|---|---|
| **屏蔽 IBL cube 面 `*qiangpi*`** | **`516b56cc43081bdf`** | **0.28** | **0.0** | 7.27% |
| 屏蔽 `*param_repack_008*`（metalness/roughnessMap 共用位） | `d2755d1592e3ff24` | **75.40** | 64.47 | 7.57% |
| 正常（对照） | `35b58bc5ae59203e`… | 24.82 | 14.06 | — |

- 屏蔽 cube 面得到的那一帧**与零星暗帧逐字节相同**（sha 一致），且此时 **map/normalMap/metalnessMap/roughnessMap 全部已加载**（1024×1024）、`handle_present=false` ⇒ **不是贴图加载、不是 adapter**，而是 **IBL cube 六面未就绪/未绑定**。
- 机理与数一致：该链材质 `metalness=1 / roughness=1`（`__matDump` 实测，两版一样），外观**几乎全部来自 IBL/env**；cube 一空 ⇒ 全黑。这正是 env-auditor task-4 当初问的"渲染为黑还是未绘制"——**答案：绘制了，但黑**（mask 7.27% 非 0，说明几何在画）。
- 也排除了"材质没编译完"：暗帧下每 mesh `matVisible=True · fragLen=24556 · hasMap/hasEnv=True · inFrustum=True`。
- 暗帧是**黏滞态**：同一载入内 t1/t2/t3（相隔 ~45 s）三次采样 sha 完全不变（`MODEL_RT28_cur_time.json`）⇒ 不是"慢加载会自己好"，而是首帧时机决定后不再恢复。
- **可复现判据（给任何人跑）**：在 `Page.navigate` 之前 `Network.setBlockedURLs(urls=['*qiangpi*'])` → 打开皮肤 → 取帧 ⇒ 必得 `sha16=516b56cc43081bdf / meanL 0.28`（脚本 `%TEMP%\rt28_block2.py`，参数即 pattern）。

## 四、数字对不上的原因（请一并更正汇总）
我 ungated（21:0x）与 gated（21:3x）两批数字不同：1110129 `37.86→24.82`、1110171 `78.96→51.53`。**不是我改的**，而是期间输入文件被改：
| 文件 | 现 sha16 | mtime |
|---|---|---|
| `assets/weapon_skin_viewer.js` | `DC3D0CE4C00EC8D0` (277,657 B) | **21:04:53** |
| `assets/weapon_skin_viewer.js`（我 ungated 时） | `BA2A84695E53F865` (270,234 B) | 03:06:59 |
| `board.html` | `194CC6DCBD8D6CBE` (102,622 B) | **21:34:40** |
| 四个皮肤 `viewer.json` | 见下 | **21:25:29** |
| `1110129/neox_material.json`（你 20:58 的 Tex0 `_b_m`→`_a`） | `C885A25D8D66EE94` | 20:58:02 |

⇒ 20:43/20:50 那批 `19.90 / 10.07 / 6.59 / 53.45` 是在**旧 viewer.js + 旧 Tex0 + 无稳定性门**下取的，**现在都不可复现**，不能当验收靶。门控现值：**1110129 = 24.82、1110171 = 51.53**。

## 五、稳定性门建议写法（可直接推广）
```python
# 门：连续 N 帧逐字节相同；不满足就重试，重试完还不满足 -> 显式失败（不拿"最后一次"当样本）
shas = []
for t in range(MAX_TRIES):            # 20
    raw = capture(clip=canvas_rect)   # Page.captureScreenshot(clip=..., captureBeyondViewport=True)
    shas.append(sha16(raw))
    if len(shas) >= 5 and len(set(shas[-5:])) == 1:
        return {"gate_ok": True, "gate_tries": t + 1, "stable_sha16": shas[-1], "raw": raw}
    await sleep(1.2)
raise GateFailed(f"distinct_in_last5={len(set(shas[-5:]))}")
```
**必须一起记录并在报告里给出**：`gate_ok / gate_tries / distinct_in_last5`、**输入指纹**（adapter + viewer.js + board.html + 皮肤 `viewer.json`/`neox_material.json` 的 sha16）、`handle_present`、`__cfgEffects().effects_status`、截图 sha16。
**三条硬规则（都有实测反例）**：
1. **门只保证"载入内稳定"，不保证"跨载入确定"**：1110152 当前版两次载入**都过门**，但 sha 不同（`8caeab36…` vs `2e8abb87…`）而 meanL 完全一致（28.81）；1110024 `9afe9452…` vs `1476e0a3…` 同样 meanL 82.54。⇒ **判定用统计量（meanL/mask/p50），sha 相同当加分项，"0 px 差"只有在同会话同载入才算数**。
2. **A/B 必须同一浏览器会话内**（切文件后 `Network.setCacheDisabled=true` 再导航），跨会话不可比（本文第四节就是反例）。
3. **收尾必须杀进程树**：`pr.terminate()` 只杀父进程；要 `taskkill /PID <browser_pid> /T /F`，并**复查 `Get-NetTCPConnection -State Listen` 无该端口**。

## 六、运维（按要求逐条）
- 我起的浏览器：**已关闭**；端口 `9915/10003/10011/10013/10015/10017/10019/10021/10023/10025/10027/10063/10071/10073/10075/10077/10079/10081` **全部无 LISTEN**（`Get-NetTCPConnection` 为空）；按 `remote-debugging-port=` + `user-data-dir` 双条件枚举，匹配我的标记的 chrome 进程 **0 个**。
- 单浏览器、不并发；后续脚本一律加 `taskkill /T /F` 收尾。
- **如实披露一次事故**：我的 10025 门控脚本被命令执行器的 600 s 上限强杀，`finally` 未跑到 ⇒ **adapter 文件一度停在备份版 `FFF6180DF4ED5BAB`**；我随即检测到并用 `MODEL_RT28_adapter_current_2E61C5234BB37CED.js` **还原并校验为 `2E61C5234BB37CED`（55,263 B）**，期间未做任何测量结论。当前树上就是当前版。
- 另：`_target_1110171\_t29ab_ab` 那份 headless Chrome（PID 34028 + 8 子进程，父 python 36016 存活）**不是我的**，我没动。

## 六之二、追加：1110171 补样时被"并发改文件"污染（如实记录，不作为 A/B 证据）
为把 1110171 也凑到每组 5 次，我又跑了一轮（21:47-21:52，`MODEL_RT28B_gate3.json`，4 例），结果：
| phase | skin | 门 | mask | meanL | 贴图就绪 | sha |
|---|---|---|---|---|---|---|
| cur | 1110171 | ok(5) | 3.16% | 51.53 | 全 1024 | `94dbd1006bb48a38` |
| cur | 1110171 | ok(5) | **0.00%** | **None（武器未绘制）** | **全 None** | `7ad37f89f32f4148` |
| bak | 1110171 | ok(5) | **0.00%** | None | 全 None | `7ad37f89f32f4148` |
| bak | 1110171 | ok(5) | **0.00%** | None | 全 None | `7ad37f89f32f4148` |

原因（有 mtime 为证，**不是我改的**）：这 4 例期间输入又被改 ——
`assets/3d/weapon_skin/1110171/neox_material.json` 21:38:57（`5B6D2020…`→`80526E54…`, 38,277→44,318 B）、
`1110129/neox_material.json` 21:38:57（`C885A25D…`→`BF45B184…`, 25,754→28,473 B）、
`assets/weapon_skin_viewer.js` 21:40:03（`DC3D0CE4…`→**`AF725621DA5B9E46`**, 284,101 B）。

⇒ 在这三个新输入下 1110171 **当前是"武器未绘制"**（mask 0、全部贴图未绑定），而且**两版 adapter 给出同一个 sha**（再次一致，仍与 adapter 无关）。
⇒ **A/B 表（第一节）仍然成立**（那一批 24 例的输入是冻结的：viewer.js `DC3D0CE4`、四皮肤 viewer.json 21:25:29、manifest 20:58）；
但 **1110171 只拿到每组 3 例干净样本**（不是 5 例），补齐需要**先冻结输入**。1110129 是 5/5 干净。
⇒ **建议**：定稿任何"验收数"前先冻结这四个文件的 sha，并在报告里连 sha 一起给；否则每次别人改 viewer.js/manifest 都会让上一批数字作废（本文第四节已是第二次）。

## 七、我没做的事（纪律）
- **未改任何代码**（adapter 除 A/B 临时替换外无改动；替换已还原并给两版 sha）。
- 未用曝光/灯光/自发光常数把亮度凑回来；未改 viewer.js / manifest / viewer.json / 贴图 / 海报。
