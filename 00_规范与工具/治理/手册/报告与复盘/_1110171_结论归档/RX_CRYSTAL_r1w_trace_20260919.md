# RX_CRYSTAL · `r1.w` 写点独立追踪（交叉验证 shader-auditor）

> 只读取证；**未改任何代码/manifest/皮肤目录**，**未开浏览器**。靶子与上一份一致：`weapon_skin_viewer.js` sha16 `113692F0F38362C4`（本文件只引反汇编，不引 viewer 行号）。
> 入口（反汇编树）：`03拆包产物\render_1003_010\_disasm\`；代表变体 **`cand\03e9e23d_b2d62c97_d11.pipe_blob1_blob.asm`**（PS · d11_deferred_quality2_shader_pbr_crystal · 784 条指令）。
> 工具：`%TEMP%\RXW1W2.py`（写点/读点/回溯链，三变体）· `RXW1W3.py`（r8 消费者窗 + 变体3结构）· `v3check.py`（变体3 detail 预乘核对）。

---

## 1. `r1.w` 的全部写点（代表变体）

**只有 1 个**：

```
L438   mul r1.w, r6.x, r8.w
```

（该文件里对 `r1` 的写入共 1 条含 `w` 掩码的指令 ⇒ **不存在多分支写点**，`ctrl=[]` 即不在任何 `if/else` 内 ✓）

## 2. 写点源链（一路追到纹理采样 / cb 常量）—— **闭环**

对 `L438` 的 `r1.w` 做深度优先回溯，得到唯一一条链（每个读点回溯源完全相同）：

```
L392   sample_b_indexable(texture2d)(...) r6.xyzw, v0.xyxx, t0.xyzw, s1, l(-1.000000)   ; t0 = Tex0 (b_m)
L393   mov_sat r6.xyzw, r6.xyzw                                                          ; r6 = saturate(Tex0)
L396   add r8.xy, v0.xyxx, cb0[317].xyxx                                                ; uv + (u_detail_offset_x, u_detail_offset_y)
L397   mul r8.xy, r8.xyxx, cb0[316].wwww                                                ; × u_detail_tilling
L398   sample_indexable(texture2d)(...) r8.xyzw, r8.xyxx, t2.xyzw, s3                   ; t2 = DetailMap, s3 = s_detailmap
L405   mul r8.xyzw, r6.xxxx, r8.xyzw                                                     ; r8.w = m × DetailMap.a   (m = r6.x = saturate(Tex0.r))
L438   mul r1.w, r6.x, r8.w                                                              ; ★ r1.w = m × r8.w
```
**⇒ `w = r1.w = saturate(Tex0.r)² × DetailMap.a`** —— 即：
- **不是**常量、**不是**光照项、**不是** caustic 链的结果；
- 它是 **掩码 `m = saturate(Tex0.r)` 的平方 × `DetailMap` 的 alpha** ✓✓
- 本项目的 `crystal_bump_n_uvva.png` 实测 **A ≡ 1.000**（`RX_CRYSTAL_recon.json`）⇒ **这些皮肤上 `w ≈ m²`** ✓
（与 viewer `L355-361` 自述的 `m = saturate(Tex0.r)`、`d = m × DetailMap.a` 口径**一致** ✓ —— 源里 `r1.w` 恰好是 `m × d`，而 `m` 又乘了一次。）

## 3. `r1.w` 的读点（8 处，均作**混合权重**）

| 行 | 指令 | 语义 |
|---|---|---|
| L440 | `mad r2.w, r1.w, r2.w, r6.z` | `r2.w = lerp(r6.z, r2.w, w)` |
| **L442** | `mad r3.w, r1.w, r3.w, cb0[320].y` | **`specular = lerp(u_base_specular, r3.w, w)`**（`r3.w` 由 L441 `= u_crystal_specular − u_base_specular`） |
| **L444** | `mad_sat r4.w, r1.w, r4.w, cb0[319].w` | **`metallic = saturate(lerp(u_base_metallic, r4.w, w))`**（`r4.w` 由 L443 `= u_crystal_metallic − u_base_metallic`） |
| L466 | `mad r1.xyz, r1.xyzx, r1.wwww, r9.xyzx` | caustic.rgb × caustic.a 累加（此处 `r1.w` 是 **caustic 的 alpha**，不是权重 —— 同寄存器复用） |
| L532 | `mul r6.z, r1.w, r6.z` | 权重乘 |
| L539 | `mul_sat r9.xyz, r1.wwww, r9.xyzx` | 权重乘 + sat |
| L1120 | `mad r0.xyz, r1.wwww, r8.xyzx, r0.xyzx` | 权重混合到输出累加器 |
| L1124 | `mad_sat r0.x, r0.x, r1.w, r6.w` | 权重混合 + sat |

⇒ **shader-auditor 的结论（`w = r1.w` 作 specular/metallic 的 lerp 权重）成立** ✓，并且**权重本身**现在追到源头：`m² × DetailMap.a` ✓。

## 4. 变体一致性核对（3 个变体、2 个 shader hash 族）

| 变体文件 | PS 指令 | `r1` 含 w 写点 | 权重写点 | 源链（等价） | cbuffer 槽位 |
|---|---|---|---|---|---|
| `03e9e23d_b2d62c97`（代表） | 784 | **1** | `L438 mul r1.w, r6.x, r8.w` | L392 sample Tex0 → L393 mov_sat → L396/397 detail UV → L398 sample DetailMap → **L405 `mul r8.xyzw, r6.xxxx, r8.xyzw`** → L438 | specular `cb0[320].y` · metallic `cb0[319].w`/`cb0[320].x` |
| `2490ff82_b2d62c97` | 693 | **1** | `L434 mul r1.w, r6.x, r8.w` | L388 sample Tex0 → L389 mov_sat → L392/393 → L394 sample DetailMap → **L401 `mul r8.xyzw, r6.xxxx, r8.xyzw`** → L434 | specular `cb0[11].y` · metallic `cb0[10].w` |
| `598c3c59_e852d979` | — | **3** ⚠ | 真正的权重写点是 `L369 mul r1.w, r5.x, r7.w` | L325 `mov_sat r5.xyz`(Tex0) → L328/329 detail UV → L337 **`mul r7.xyzw, r5.xxxx, r7.xyzw`**（DetailMap×m）→ L369 | specular `cb0[137].w`/`cb0[138].x` · metallic `cb0[137].y`/`.z` |

- **两个 `b2d62c97` 变体：公式与写点数完全一致**（`r1.w = saturate(Tex0.r) × (m × DetailMap.a)` = `m² × D.a`）✓
- **第三个变体（`e852d979` 族）：语义同为 `m² × D.a`**（`L337` 先做 `r7 *= m`，`L369` 再乘 `r5.x`）✓，**但 `r1` 在本变体被复用为 scratch**：另有 `L285 max r1.w, cb0[136].x, l(0.001)`（除法保护）与 `L297 ineg r1.w, r0.x`（符号翻转）两处写点 ⇒ **"r1 被写过"≠"权重被写过"**，识别权重写点必须看**其读点是否作 lerp 权重**（本变体的 `L371/L373/L375`）。
- **⚠ cbuffer 槽位在各变体不同**（`cb0[320]` / `cb0[11]` / `cb0[137]`）⇒ **任何实现都不得硬编码偏移**，应按名绑定（viewer 侧走 manifest 的 `crystal_params` 名称路径 ✓）。

## 5. U-2 闭环：detail 结果 `r8` 的四分量去向（代表变体，窗口 L405→L439）

我上一份 MD 的 §4/U-2 结论**需要精确化**（先前只说"`.w` 进 `d`"，实测四分量**都被消费**）：

| 分量 | 行 | 指令 | 去向 |
|---|---|---|---|
| `r8.xy`（detail 法线，已 ×u_detail_intensity） | L410 / L416 / L420 | `mad r8.xy, r0.wwww, -r8.xyxx, r8.xyxx` · `dp2 r0.w, r8.xyxx, r8.xyxx` · `mov r9.xy, -r8.xyxx` | **法线扰动链**（进入光照/反射计算） |
| `r8.z` | L439 | `mad r2.w, r6.z, r8.z, -r6.z` | `r2.w = r6.z·(r8.z − 1)`（另一混合权重） |
| `r8.w` | L431 / **L435** / **L438** | `mad r0.w, r8.w, r0.w, cb0[319].z` · `mad r9.xyz, r8.wwww, r9.xyzx, cb0[184].xyzx` · `mul r1.w, r6.x, r8.w` | **① 晶体权重 `w`；② 与 `u_base_color`(cb0[184]) 的基色混合** |
⇒ **U-2 已闭环**：detail 层在源里**同时**贡献「法线扰动（xy）」「r2.w（z）」「晶体权重 w 与基色混合（w）」；
⇒ 并且 viewer 现有 `d = m × DetailMap.a` 抓的是**权重那条路径**（= 本次关心的 `w`）✓，而 **xy/z 的法线/权重路径在 wiki 链里没有对应实现**（另记）。

## 6. 对 task-43 的直接可用结论（F0 / metallic 能否接）

1. **`w = saturate(Tex0.r)² × DetailMap.a`**（本项目 `DetailMap.a ≡ 1` ⇒ `w ≈ m²`）—— 有完整指令级证据链（§2），**三变体一致**（§4）。
2. `metallic = saturate(lerp(u_base_metallic, u_crystal_metallic, w))`（`L443 add` + `L444 mad_sat`）✓
   `specular = lerp(u_base_specular, u_crystal_specular, w)`（`L441 add` + `L442 mad`）✓
   ⇒ **F0/metallic 可以接**：按名取 `u_base_metallic/u_crystal_metallic/u_base_specular/u_crystal_specular`（c159 有值 ✓），权重用 `w`；**不要硬编码 cbuffer 偏移**（§4 已证各变体不同）。
3. 注意 `w` 依赖 `Tex0`（`m`）与 `DetailMap`：**两输入都必须先绑对**，否则 `w` 会整体退化（`m²` ⇒ 掩码不准会被平方放大）。

## 7. unresolved（不猜，附已试入口）

| id | 未闭环项 | 已试入口 |
|---|---|---|
| U-A | `L440 r2.w` / `L431 r0.w` / `L435 r9.xyz` / `L532` / `L539` / `L1120` / `L1124` 这些**含 w 的中间量**最终分别进哪个输出（我只闭环了 specular/metallic 两条 + caustic 一条） | 已打印全部 8 个读点与其回溯链；进一步需从这些消费者继续向前追到 `o0/o1/o2` 写出 |
| U-B | `e852d979` 族的**其余变体**是否同样复用 `r1` 作 scratch | 本轮核了 3 个变体（2 族）；15 个 PS 的逐条变体一致性未全量比对（上一份 §7 U-5 同项） |
| U-C | `DetailMap.a` 在**其它皮肤**是否也 ≡1（决定 `w=m²` 是否普适） | 本轮只核了 1110171/1110177 的 `crystal_bump_n_uvva.png`（A≡1）；其余皮肤未核 |

## 8. 复现命令
```
venv\Scripts\python.exe %TEMP%\RXW1W2.py     # r1.w 写/读点 + 回溯链（3 变体）→ RXW1W_out.txt / RXW1W_result.json
venv\Scripts\python.exe %TEMP%\RXW1W3.py     # r8 消费者窗（U-2）+ 变体3 的 r1 写点明细
venv\Scripts\python.exe %TEMP%\v3check.py    # 变体3 的 detail 预乘（L337）与权重写点（L369）上下文
```
