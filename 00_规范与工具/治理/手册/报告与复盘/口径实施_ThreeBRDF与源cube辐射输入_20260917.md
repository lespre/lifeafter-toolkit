# 口径实施报告 · 恢复 Three BRDF + 源 cube 仅作辐射输入（2026-09-17）

用户定版口径：
> 恢复 Three 的完整 BRDF，只用源 cube 替换环境辐射输入。
> 禁止对 `outgoingLight` 额外叠加，禁止整体覆盖最终颜色。

**本轮未调整灯光、曝光、颜色、金属度常数或人工 palette。**

---

## 一、第 1 条：删除整体替换 ✅

被删除的代码（原 `onBeforeCompile` 注入末尾）：

```glsl
gl_FragColor.rgb = q_albedo * uAlbedoGain + q_envF * uIblStrength * q_albedo;
```

连同其配套的 `q_albedo / q_NoV / q_fres / q_envF` 计算一并移除。
**不再触碰 `gl_FragColor`**，Three 的 direct/indirect diffuse、specular、Fresnel、遮蔽与
toneMapping 链全部原样保留。

---

## 二、第 2/3 条：cube 只产出 radiance，不乘 albedo ✅

**关键技术事实**：Three r180 的 `getIBLRadiance` **仅在 `ENVMAP_TYPE_CUBE_UV` 下有实现**
（原始 bundle 实测）：

```glsl
vec3 getIBLRadiance( const in vec3 viewDir, const in vec3 normal, const in float roughness ) {
  #ifdef ENVMAP_TYPE_CUBE_UV
    ... textureCubeUV( envMap, ..., roughness ) ...
  #else
    return vec3( 0.0 );          // ← 我方持有原始 CubeTexture，恒走这一支
  #endif
}
```

本项目明令禁止用 PMREM 冒充源 shader，故 Three 自带 IBL 恒为 0 —— 必须由我们提供 radiance 输入，
但**不得**接管最终颜色。

**实现**（避免函数重定义）：

```glsl
// ① 片元顶部：给 Three 原函数改名
#define getIBLRadiance getIBLRadiance_three

// ② void main() 之前：#undef 并重建
#undef getIBLRadiance
vec3 getIBLRadiance( const in vec3 viewDir, const in vec3 normal, const in float roughness ) {
  float q_rough = max( roughness, 0.0019 );
  float q_lod   = 5.0 + 1.2 * log2( q_rough );                  /* asm 537-539 */
  vec3  q_R     = reflect( -viewDir, normal );
  q_R           = normalize( mix( q_R, normal, roughness * roughness ) );
  q_R           = inverseTransformDirection( q_R, viewMatrix );
  float q_c = cos( uIblRot ), q_s2 = sin( uIblRot );            /* asm 531 */
  vec3  q_Rr = vec3( q_R.x*q_s2 + q_R.z*q_c, q_R.y, -q_R.x*q_c + q_R.z*q_s2 );  /* asm 535-536 */
  vec4  q_sm = textureLod( uCustomIbl, q_Rr, q_lod );           /* asm 541 */
  vec3  q_L  = pow( q_sm.rgb * q_sm.a * 16.0, vec3(2.0) );      /* asm 542-544 RGBM 解码 */
  vec3  q_Lc = min( q_L, vec3(1.5) );                           /* asm 545 */
  vec3  q_env= q_L + uIblMix * ( q_Lc * 0.299805 - q_L );      /* asm 546-548 */
  q_env *= uIblScale;                                           /* asm 549 曝光 */
  return q_env;   /* ← 只交 radiance；F0/Fresnel/BRDF/toneMapping 由 Three 负责 */
}
```

源公式链逐条保留（lod / 方向旋转 / sample_l / RGBM 解码 / lightmap 混合 / 曝光），
但**不再乘 `q_albedo`**、**不再写 `gl_FragColor`**。金属基色改为经 Three 的
`specularColor/F0` 进入镜面 BRDF。

> 说明：`uF0Scale` / `uAlbedoGain` 两个 lab 专有 uniform 已随整体替换一并移除。

---

## 三、第 4 条：晶体 roughness 接入 `t_basecolor.a` ✅

- 源公式：`Roughness = t_basecolor.a`（外审 §3.5 已证），实测 `012_a` 均值 **0.637**、`010_a` **0.732**
- Three 从 `roughnessMap.G` 读取，故生成派生贴图（**纯通道重排，无数值改动**）：
  - `src_tex/rough_repack_012.png`（G = `012_a.png` 的 alpha，min 0 / max 255 / mean 162.5）
  - `src_tex/rough_repack_010.png`（G = `010_a.png` 的 alpha，min 0 / max 255 / mean 186.6）
- 不再硬编码 `roughness: 1.0` 作为最终值
- **DetailMap 对 base/crystal/detail 混合的贡献仍缺 → 标 `incomplete`，未补常数**

---

## 四、第 5 条：全部材质保持不透明 ✅

7/7 prim 实测（`__chainMats()`）：

| 字段 | 值 |
|---|---|
| `transparent` | **False** |
| `opacity` | **1** |
| `alphaTest` | **0** |
| `blending` | **0（NoBlending）** |
| `depthTest` / `depthWrite` | **True / True** |

片元末尾强制 `gl_FragColor.a = 1.0`。
**表述已更正**：生产材质本来就不透明，不再称"透明排序"问题。

---

## 五、第 6 条：A/B/C 固定条件对照 ✅

实现：`window.__abcProbe('A'|'B'|'C'|null)` —— **同一套 Three BRDF，只变环境输入**；不改灯光/曝光/颜色/金属度。

| 图 | 条件 | 文件 | sha（前16） |
|---|---|---|---|
| **A** | Three BRDF，**不启用环境**（radiance 置 0） | `ABC_A_noenv.png` | `54d9c96eb42553d9` |
| **B** | Three BRDF + **正确源 cube** | `ABC_B_srccube.png` | `151446b08f0f7176` |
| **C** | Three BRDF + **交换 cube 负面对照** | `ABC_C_swapcube.png` | `a4ed7fb45df6970a` |

`__abcProbe` 返回 `{"touched":7,"skippedPrims":[],"scale":…}` —— 7/7 prim 全部参与，无跳过。

---

## 六、第 7 条：验收

| 判据 | 结果 |
|---|---|
| A 保留正常表面层次，不再是裸 albedo | ✅ **成立** —— A 有明确明暗渐变与高光层次，是 BRDF 结果而非贴图直出 |
| B 不得出现黑金横条 / 脏暗 / 平片感 | ✅ **成立** —— B 无横条、无脏暗、无平片感 |
| **B/C 应有明确差异，证明源 cube 真正进入 BRDF** | ✅ **成立** —— B `151446b0…` ≠ C `a4ed7fb4…` |
| 运行态输出实际 roughness / LOD / cube / F0 | ✅ 见下表 |

**运行态读数（`window.__brdfState()`）：**

| prim | kind | rough | roughMap | ibl 源 | iblScale | **真实 lod** | F0 |
|---|---|---|---|---|---|---|---|
| 0, 4 | weapon | 1.0 | ✓ | qiangpi | 0.25 | **0.26** | **baseColor(metal)** |
| 1,2,3,5,6 | crystal | 1.0 | ✓ | car_studio01 | 0.25 | **4.22** | **0.04(dielectric)** |

（真实 lod = `5 + 1.2·log2(roughness × roughnessMap.G均值)`；
晶体 **4.22 ≈ 用户预期的 4.2**，不再固定 5.0。）

---

## 七、第 8 条：路径定性 ✅

已在代码注释中标注：

```
source textures + source cube + Three BRDF approximation
```

并注明：**这不是完整 NeoX 源级复原**；完整源级版本需先恢复 ASM 中的 `r13` 及相关全局常量，
再替换 Three BRDF。

---

## 八、改动与回滚

| 文件 | 变化 |
|---|---|
| `assets/weapon_skin_viewer.js` | ① 删除整体颜色替换；② 重建 `getIBLRadiance` 只产 radiance；③ 晶体 roughness 接入 `t_basecolor.a`；④ 强制不透明 + 片元 alpha=1；⑤ 重写 `__abcProbe`；⑥ 新增 `__brdfState()`；⑦ 删除 crystal→transparent 错误路径 |
| `src_tex/rough_repack_012.png`、`rough_repack_010.png` | **新增**（派生自 `*_a.png` 的 alpha，纯通道重排） |

**备份**：`weapon_skin_viewer.js.bak_20260916_232432`

**运行**：`node --check` 通过；`__neox()` → `applied:7, failed:[]`；无 JS 异常、无 shader 编译错误。

---

## 九、仍未解决（如实登记）

1. **`getIBLIrradiance`（漫反射 IBL）仍返回 0** —— Three 的非 CUBE_UV 分支。本轮按口径只替换了
   **radiance**（镜面 IBL 输入）；漫反射环境项是否需要同样接入源 cube，需你确认。
2. **`DetailMap` 仍为降级渲染**（`d = q_mm`），标 incomplete。
3. **晶体仍缺 3 类源资源**（caustic / refraction / reflection）。
4. `prim3` / `prim6` 渲染像素仍偏少，**测量方法待重做**（此前两次几何面积测量均被污染）。
5. 完整源级版本仍需 ASM `r13` 与全局常量（本轮明确不越界）。
