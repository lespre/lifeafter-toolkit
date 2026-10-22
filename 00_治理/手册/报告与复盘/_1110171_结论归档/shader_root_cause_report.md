# task-3 结论：链材质 lab 下完全不渲染 = 片元着色器编译失败（根因已实测锁定）

调查角度：着色器 / three.js 兼容性。全程只读，未修改项目内任何文件（viewer.js mtime/hash 未变：
`2026/9/16 23:32:10` / `203EFCA3355523B7866458700CE05F2F6CB928A08175B35E61ECC73982653F85`）。

## 0. 一句话根因

`assets/weapon_skin_viewer.js` L930-952 的 `onBeforeCompile` 注入代码用了 **10 个以双下划线开头的 GLSL 标识符**
（`__rough __lod __R __c __s2 __Rr __sm __L __Lc __env`）。GLSL ES 3.00 规范保留「含连续两个下划线的标识符」，
编译器直接拒绝这些**声明**，于是整段注入代码变成 43 个错误 → 片元着色器编译失败 → program 链接失败
（`VALIDATE_STATUS false` / `Fragment shader is not compiled.`）→ `useProgram: program not valid`
（实测 1604 次）→ 这些材质的 draw call 全部是空操作 → 武器**一个像素都不画**。

同一段注入里还有**第二个独立致命错误**：L948 使用了 `uIblStrength`，但 L936 的 uniform 前置声明清单里
**没有它**（只有 uCustomIbl / uIblRot / uIblMix / uIblScale）→ `'uIblStrength' : undeclared identifier`。

两者都必须修；只修 `pow(vec3, vec2)` 或只改名都不够 → 这正是「改 pow 后 A 帧 sha 仍是
`033495957ca13b69`（逐字节相同）」的原因：着色器**依然编译失败**，程序依旧 invalid，画面确定性不变。

## 1. 最小证据（实测输出，非推断）

### 1.1 编译失败日志（`renderer.info.programs` → `gl.getShaderInfoLog`，`__ladderCompile()`）
```
checkShaderErrors = True | EXT_shader_texture_lod = False
program 总数 = 23 | 失败 = 9 | 失败 cacheKey 全部以 physical,STANDARD, 开头
prog[2] vs_compile=True fs_compile=False link=False
 fragment_info_log:
ERROR: 0:1849: '__rough' : identifiers containing two consecutive underscores (__) are reserved as possible future keywords
ERROR: 0:1850: '__rough' : undeclared identifier
ERROR: 0:1850: '__lod' : identifiers containing two consecutive underscores (__) are reserved ...
ERROR: 0:1851: '__R' : identifiers containing two consecutive underscores (__) are reserved ...
ERROR: 0:1852: '__c' : identifiers containing two consecutive underscores (__) are reserved ...
ERROR: 0:1852: '__s2' : identifiers containing two consecutive underscores (__) are reserved ...
ERROR: 0:1854: '__Rr'/'__sm' : ... reserved ...（共 43 条 ERROR）
ERROR: 0:1859: 'uIblStrength' : undeclared identifier
 program_info_log: 'Fragment shader is not compiled.'
```
three 自身也以默认路径报了错（即 `onShaderError` 未设时的 else 分支）：
```
error|THREE.WebGLProgram: Shader Error 1282 - VALIDATE_STATUS false
      Material Type: MeshStandardMaterial
      Program Info Log: Fragment shader is not compiled.
      FRAGMENT ... ERROR: 0:1845: '__rough' : identifiers containing two consecutive underscores ...
```

### 1.2 注入**确实生效**（锚点存在 → 排除「锚点静默失败」）
GL 侧 `shaderSource` 抓到的**最终**片元源码（含 three 的 `#version 300 es` 前缀、include 已解析），
注入块原样出现，且紧跟其后就是展开后的 dithering chunk：
```glsl
#ifdef PREMULTIPLIED_ALPHA
	gl_FragColor.rgb *= gl_FragColor.a;
#endif
	  float __rough = max(roughnessFactor, 0.0019);
  float __lod = 5.0 + 1.2 * log2(__rough);                  /* asm 537-539 */
  vec3  __R  = reflect(normalize(vViewPosition), normal);   /* 源反射方向 */
  ...
  gl_FragColor.rgb += __env * uIblStrength;                  /* asm 550 ×反射率 */
#ifdef DITHERING
	gl_FragColor.rgb = dithering( gl_FragColor.rgb );
#endif
}
```
→ `sh.fragmentShader = sh.fragmentShader.replace('#include <dithering_fragment>', inj+'#include <dithering_fragment>')`
（L949 是**赋值**，不是被丢弃的返回值）**真的生效**；L936 的 uniform 前置块也在最终源码里。
注入体后已无未解析的 `#include <...>`。

### 1.3 `uIblStrength` 声明核对（最终源码 72574 字符）
```
has_uCustomIbl_decl = true      has_uIblRot_decl = true
has_uIblStrength_decl = false   uses_uIblStrength = true
declared_uniforms = ['uniform samplerCube uCustomIbl;','uniform float uIblRot;','uniform float uIblMix;','uniform float uIblScale;']
```
（正好就是 L936 那 4 条，缺 `uniform float uIblStrength;`）

### 1.4 因果闭环 A/B（同一批 mesh，只换材质程序）
`snapshot()` = 场景重渲染进 WebGLRenderTarget 后 readRenderTargetPixels，非缓存图。

| 状态 | 与 baseline 差异像素 | 强红像素 | bbox |
|---|---|---|---|
| baseline：链材质（程序 invalid） | 0 | 0 | — |
| `__l0({mode:'both'})`：同 mesh 换 **能编译** 的 MeshBasicMaterial + 纯红 | **31876 (4.04%)** | 31876 | 418,188–779,459 |
| `__primSolid(true)`：调色板 MeshBasicMaterial | **31876 (4.04%)** | 9666 | 418,188–779,459 |
| `__ladderL1({mode:'red'})`：锚点注入但 `uDiagColor` 未声明 | 0 | 0 | — |
| 还原链材质 | 0（sha 回到 `8ab1a26c160ec74d`） | 0 | — |

→ 同一几何/相机/可见性下，只要材质程序能编译，武器立刻占 31876 像素（bbox 与 `__primSolid` 完全一致）。
**几何、相机、可见性、prim 配对、frustum 全部被排除**；唯一变量就是 program 是否 valid。
`__l0` 的 21 次 draw 记录里 `matType` 全为 MeshBasicMaterial（即那批 mesh 真的进了 draw call）。

### 1.5 「修复充分性」三臂实验（在页面内用**实际那份失败源码**重编译，未改项目文件）
把 GL 抓到的 72574 字符失败源码拿进独立 WebGL2 context 编译：

| 臂 | 改动 | 结果 |
|---|---|---|
| arm1 | 原样 | **FAIL，43 条 ERROR**（复现） |
| arm2 | 仅把 `__xxx` 改名为 `q_xxx` | **FAIL，只剩 1 条 ERROR**：`ERROR: 0:1855: 'uIblStrength' : undeclared identifier` |
| arm3 | 改名 **+** 补 `uniform float uIblStrength;` | **ok=True，0 条 ERROR** |

→ 证明：① `uIblStrength` 是独立的第二个致命错误；② 这两处改完**足以**让该着色器编译通过；
③ `textureLod(samplerCube, vec3, float)`、`roughnessFactor`、`vViewPosition`、`normal`、`gl_FragColor`
在该语境下**全部合法**（arm3 零错误即证）。

## 2. 被排除的假设（逐条给依据）

| 假设 | 判定 | 依据 |
|---|---|---|
| 锚点 `#include <dithering_fragment>` 在该版本不存在 → 注入静默失败 | **排除** | ① r180 bundle `three.module.min.js` @141683：`meshphysical_frag` 结尾确有 `...\n#include <dithering_fragment>\n}`（MeshStandardMaterial 走 meshphysical_shader）；② 实测注入文本出现在最终编译源码里 |
| `gl_FragColor` 在 r180 无效 | **排除** | r180 非 raw 材质恒为 `#version 300 es` + `layout(location=0) out highp vec4 pc_fragColor;` + `#define gl_FragColor pc_fragColor`（bundle @214790/214848）；arm3 编译通过 |
| `vViewPosition` / `normal` / `roughnessFactor` 不在作用域 | **排除** | 注入点落在 main() 末尾（`roughnessmap_fragment` / `normal_fragment_begin` 之后、`dithering_fragment` 之前）；arm3 零错误 |
| three.js 版本/引入方式不匹配 | **排除** | `assets/vendor/three/VERSION` = `three 0.180.0`；viewer 用 `import()` 加载本地 `vendor/three/three.module.min.js`（r180 正常 ESM，bundle 首行 re-export `three.core.min.js`），无 CDN |
| `EXT_shader_texture_lod` 不支持导致 `textureCubeLodEXT` 失败 | **排除（红鲱鱼）** | `extension_shader_texture_lod=false` 属实，但 r180 WebGL2 前缀里有 `#define textureCubeLodEXT textureLod`，所以 L1820 那类注入不是本次原因 |
| 几何 / 相机 / 可见性 / prim 配对 / frustum | **排除** | §1.4：同一批 mesh 换成可编译材质即出 31876 像素，bbox 与 `__primSolid` 逐值相同 |
| 材质被 `m.visible=false` 丢弃 | **排除** | lab=1 下 L966 不置 `visible=false`（且 `__neox()` 报 `missing_required=[]`、`applied=7`） |
| 单改 `pow(vec3,vec2)→vec3(2.0)` 无效是别的原因 | **解释** | 该修是**对的但不够**：修前 3 类错误（pow + `__` 保留名 + uIblStrength）都让编译失败，修后剩 2 类，程序**仍然 invalid** → 像素确定性不变，故 sha 逐字节相同 |

## 3. 建议的最小修法（仅建议，未落地）

1. **L936** 前置声明补上 `uniform float uIblStrength;\n`。
   注：L932 的 `sh.uniforms.uIblStrength={value:1.0}` 生效后取值为 1.0（未读 `state.iblStrength`，与 L1147 的
   `applySourceEnvBright` 路径不一致，属语义小差异，非本次根因）。
2. **L938-948** 把 10 个标识符 `__rough __lod __R __c __s2 __Rr __sm __L __Lc __env`
   整体改名为无保留风险的名字（如 `q_rough q_lod q_R q_c q_s2 q_Rr q_sm q_L q_Lc q_env`），其余表达式一字不动。
   （arm3 已验证：改这两处后该着色器 0 错误编译通过。）

## 4. 同源已确认的第二个实例（顺带发现，同 bug 类）

`__ladderL1`（L2442-2444）同样只写 `sh.uniforms.uDiagColor` 并注入 `gl_FragColor = vec4(uDiagColor, 1.0);`，
**没有声明 `uniform vec3 uDiagColor;`** → 实测失败 program 由 9 增到 11，日志：
`ERROR: 0:454: 'uDiagColor' : undeclared identifier`。
这解释了「`__ladderL1({mode:'red'})` 画面 0 像素变化」——不是画面没变，是它自己的程序也没编译成。
对比：`__l1`（L2246-2250）在 L2248 有 `'uniform vec3 uDiagColor;\n'+` → 那条路径是对的。

## 5. 可运行的着色器编译错误捕获方法（本任务实测可用）

1. **无需拿到 renderer 对象**：`Page.addScriptToEvaluateOnNewDocument` 在页面任何脚本前
   hook `WebGL2RenderingContext.prototype.{shaderSource,compileShader,getShaderParameter,getShaderInfoLog,attachShader,linkProgram,getProgramParameter,getProgramInfoLog,useProgram}`，
   即可复现 `renderer.debug.onShaderError` 的能力（含**最终** GLSL 源码，已解析 include + 已加 three 前缀），
   并统计 `useProgram` 落在 invalid program 上的次数。
2. **viewer 自带**：`renderer.debug.checkShaderErrors` 在 r180 默认 true；`WikiWeaponViewer.__ladderCompile()`
   会遍历 `renderer.info.programs` 打 `gl.getShaderParameter/getShaderInfoLog/getProgramInfoLog`
   （`checkShaderErrors` / `programs[].fragment_compile` / `fragment_info_log`）。这是**最省事**的一条。
3. 想要真 `onShaderError`：必须拿到 renderer，而 viewer 未导出；hook 上述原型方法等价。

## 6. 未证实 / unresolved

- 断链后的**最终观感**（修好后武器长什么样、颜色是否与源一致）未验证：那需要改 viewer.js（超出只读边界）。
- `applyMaterialLayers` 的 `applySourceEnvBright`（L1130-1155）与链材质若**同时**作用会重复声明
  `uIblRot/uIblMix/uIblScale`；lab=1 路径下两者不会同时作用于同一材质（L1292 在 lab 下不重跑
  applyMaterialLayers），故**未观测到**该冲突，标 unresolved，不作结论。

## 7. 复现命令

```powershell
& "C:\Users\Administrator\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe" "E:\la拆包项目\03拆包产物\_target_1110171\shader_gl_compile_probe.py"
& "C:\Users\Administrator\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe" "E:\la拆包项目\03拆包产物\_target_1110171\shader_dump_evidence.py"
& "C:\Users\Administrator\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe" "E:\la拆包项目\03拆包产物\_target_1110171\shader_ab_causality_probe.py"
& "C:\Users\Administrator\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe" "E:\la拆包项目\03拆包产物\_target_1110171\shader_fix_verify_probe.py"
```
