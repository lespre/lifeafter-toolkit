# GLSL 着色器错误取证报告（只读）

- 取证时间：2026-09-18
- 页面：`http://127.0.0.1:8765/board.html?b=weapon_skin_sfx_text_sources&view=wiki&sort=id&dir=desc`
- 被测文件：`08Lifeafter wiki/assets/weapon_skin_viewer.js`
  - 磁盘 SHA256 = `6938828F82F5849A0E11BB0DAB164B3AE2DDA4564B3F2AF8B522D3981AD625CB`
  - 字节数 = 221043，mtime = 2026/9/17 22:17:14
  - **HTTP 实际下发字节与该文件逐字节相同**（已用 urllib 取回比对，`identical to served: True`），
    故"浏览器跑的是哪一版"不存在疑问。
- 硬件/软件：Chrome 152.0.7977.83，`ANGLE (NVIDIA GeForce RTX 5080 Direct3D11 vs_5_0 ps_5_0)`，
  `KHR_parallel_shader_compile=true`，`EXT_shader_texture_lod=false`。
- 环境：另用 `--use-angle=swiftshader` 复跑一遍，结论相同。

---

## 0. 一句话结论

**当前 viewer 版本抓不到任何 GLSL 编译错误——因为它已经没有编译错误了。**
我在两种 GL 后端（NVIDIA D3D11 / SwiftShader）各跑一遍，`console.error` 覆盖层 + `Runtime.consoleAPICalled`
（**监听器在 `Page.navigate` 之前挂好**）双双为 0 条；viewer 自带诊断 `__ladderCompile()` 报告 14 个 program
**全部** `vertex_compile=true, fragment_compile=true, program_link=true`，`fragment_info_log` / `vertex_info_log` 全为空串。

lead 手上的 `Shader Error 0 / 1282 - VALIDATE_STATUS false` 原文，我在
`03拆包产物/_target_1110171/env_probe_*.json`（**2026-09-16 23:36–23:41**）里找到了**逐字节相同**的原始记录，
并已把两代错误各自锁定到**具体的历史版本**上（见 §2）。结论：**那批错误属于旧版本，不是本轮改动引入的。**

---

## 1. 抓取方法（可复现的最小命令）

关键点：**先 `Page.enable` + `Runtime.enable` + `Page.addScriptToEvaluateOnNewDocument`，最后才 `Page.navigate`。**

脚本（在 `%TEMP%`，不污染项目）：
- `%TEMP%\glsl_forensic_probe.py` —— 全量原始事件（consoleAPICalled 的**每个 arg 单独保留**，不 `str()` 拼接）
- `%TEMP%\glsl_probe3.py` / `%TEMP%\glsl_probe4.py` —— 加跑 viewer 自带诊断

```powershell
$py="C:\Users\Administrator\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe"
# 纯 DEVTOOLS 模式（GPU）
& $py "$env:TEMP\glsl_probe4.py" 9871 final
# SwiftShader 模式
& $py "$env:TEMP\glsl_probe2.py" 9862 swiftshader
```

脚本内注入的页面侧钩子（`Page.addScriptToEvaluateOnNewDocument`，在任何页面脚本之前执行）：

```js
const _e=console.error;
console.error=function(){ window.__errc=(window.__errc||[]).concat([Array.from(arguments).map(String)]); return _e.apply(console,arguments); };
// 外加 WebGL2RenderingContext.prototype 的 shaderSource/compileShader/attachShader/linkProgram/
// getShaderInfoLog/getProgramInfoLog/validateProgram 包装：失败即抓 shaderSource + infoLog
```

事后一次性取回（`Runtime.evaluate ... returnByValue`）：
`window.__errc`、`window.__glHook{shaders,compileFail,linkFail,progLogs}`、
`window.WikiWeaponViewer.__ladderCompile()`。

> 注意：**必须**在 `Page.navigate` 之前 `Runtime.enable`，否则首次编译期的 console 事件全部丢失——
> 这正是 lead 上次"监听器挂上时错误已发完"的原因，已复现并修正。

---

## 2. 抓到的错误原文（原文照抄，未概括）

### 2.1 第一代：`__` 双下划线保留标识符（原始记录 `env_probe_1.json`，2026-09-16 23:36）

三条 header 完全相同的短记录（CDP 对 `text` 有 300 字符截断）+ 一条 4000 字符的完整记录：

```
THREE.WebGLProgram: Shader Error 0 - VALIDATE_STATUS false

Material Name: 
Material Type: MeshStandardMaterial

Program Info Log: Fragment shader is not compiled.
 

FRAGMENT

ERROR: 0:1845: '__rough' : identifiers containing two consecutive underscores (__) are reserved as possible future keywords
```

```
THREE.WebGLProgram: Shader Error 1282 - VALIDATE_STATUS false

Material Name: 
Material Type: MeshStandardMaterial

Program Info Log: Fragment shader is not compiled.
 

FRAGMENT

ERROR: 0:1852: '__rough' : identifiers containing two consecutive underscores (__) are reserved as possible future keywords
```

完整记录（`env_probe_2.json`，含 three 自己的源码上下文行）：

```
THREE.WebGLProgram: Shader Error 1282 - VALIDATE_STATUS false

Material Name: 
Material Type: MeshStandardMaterial

Program Info Log: Fragment shader is not compiled.
 

FRAGMENT

ERROR: 0:1847: '__rough' : identifiers containing two consecutive underscores (__) are reserved as possible future keywords
ERROR: 0:1848: '__rough' : undeclared identifier
WARNING: 0:1848: 'log2' : operation result is undefined for the values passed in
ERROR: 0:1848: '__lod' : identifiers containing two consecutive underscores (__) are reserved as possible future keywords
ERROR: 0:1849: '__R' : identifiers containing two consecutive underscores (__) are reserved as possible future keywords
ERROR: 0:1850: '__c' : identifiers containing two consecutive underscores (__) are reserved as possible future keywords
ERROR: 0:1850: '__s2' : identifiers containing two consecutive underscores (__) are reserved as possible future keywords
ERROR: 0:1851: '__R' : undeclared identifier
ERROR: 0:1851: 'x' :  field selection requires structure, vector, or interface block on left hand side
ERROR: 0:1851: '__s2' : undeclared identifier
ERROR: 0:1851: '__R' : undeclared identifier
ERROR: 0:1851: 'z' :  field selection requires structure, vector, or interface block on left hand side
ERROR: 0:1851: '__c' : undeclared identifier
ERROR: 0:1851: '__R' : undeclared identifier
ERROR: 0:1851: 'y' :  field selection requires structure, vector, or interface block on left hand side
ERROR: 0:1851: '__R' : undeclared identifier
ERROR: 0:1851: 'x' :  field selection requires structure, vector, or interface block on left hand side
ERROR: 0:1851: '__c' : undeclared identifier
ERROR: 0:1851: '__R' : undeclared identifier
ERROR: 0:1851: 'z' :  field selection requires structure, vector, or interface block on left hand side
ERROR: 0:1851: '__s2' : undeclared identifier
ERROR: 0:1851: '__Rr' : identifiers containing two consecutive underscores (__) are reserved as possible future keywords
ERROR: 0:1852: '__Rr' : undeclared identifier
ERROR: 0:1852: '__lod' : undeclared identifier
ERROR: 0:1852: 'textureLod' : no matching overloaded function found
ERROR: 0:1852: '__sm' : identifiers containing two consecutive underscores (__) are reserved as possible future keywords
ERROR: 0:1853: '__sm' : undeclared identifier
ERROR: 0:1853: 'rgb' :  field selection requires structure, vector, or interface block on left hand side
ERROR: 0:1853: '__sm' : undeclared identifier
ERROR: 0:1853: 'a' :  field selection requires structure, vector, or interface block on left hand side
ERROR: 0:1853: 'pow' : no matching overloaded function found
ERROR: 0:1853: 'xyz' :  field selection requires structure, vector, or interface block on left hand side
ERROR: 0:1854: '__L' : identifiers containing two consecutive underscores (__) are reserved as possible future keywords
ERROR: 0:1854: '__L' : undeclared identifier
ERROR: 0:1854: 'min' : no matching overloaded function found
ERROR: 0:1854: '__Lc' : identifiers containing two consecutive underscores (__) are reserved as possible future keywords
ERROR: 0:1855: '__L' : undeclared identifier
ERROR: 0:1855: '__Lc' : undeclared identifier
ERROR: 0:1855: '__L' : undeclared identifier
ERROR: 0:1855: '__env' : identifiers containing two consecutive underscores (__) are reserved as possible future keywords
ERROR: 0:1856: '__env' : undeclared identifier
ERROR: 0:1856: 'assign' : l-value required (can't modify a const)
ERROR: 0:1857: '__env' : undeclared identifier
ERROR: 0:1857: 'uIblStrength' : undeclared identifier
 

  1842: 	gl_FragColor.rgb = mix( gl_FragColor.rgb, fogColor, fogFactor );
  1843: #endif
  1844: #ifdef PREMULTIPLIED_ALPHA
  1845: 	gl_FragColor.rgb *= gl_FragColor.a;
  1846: #endif
> 1847: 	  float __rough = max(roughnessFactor, 0.0019);
  1848:   float __lod = 5.0 + 1.2 * log2(__rough);                  /* asm 537-539 */
  1849:   vec3  __R  = reflect(normalize(vViewPosition), normal);   /* 源反射方向 */
  1850:   float __c = cos(uIblRot), __s2 = sin(uIblRot);       
```

**归属（已用文件比对证明）**：
`08Lifeafter wiki/assets/weapon_skin_viewer.js.bak_20260916_232432`（166272 B，2026/9/16 22:04）
内含字符串 `float __rough` **1 次**，上下文正是：

```js
sh.fragmentShader='uniform samplerCube uCustomIbl;\nuniform float uIblRot;\nuniform float uIblMix;\nuniform float uIblScale;\n'+sh.fragmentShader;
var inj='  float __rough = max(roughnessFactor, 0.0019);\n'+
        '  float __lod = 5.0 + 1.2 * log2(__rough);   ...
```

当前文件里 `float __rough` 出现 **0 次**（仅剩两处 JS 变量名 `__roughMode`，与 GLSL 无关）。
→ 这 43 条 ERROR 属于**已删除的旧注入块**。

### 2.2 第二代：`uIblStrength` 未声明（原始记录 `env_probe_4.json`，2026-09-16 23:41，共 21 条）

```
THREE.WebGLProgram: Shader Error 0 - VALIDATE_STATUS false

Material Name: 
Material Type: MeshStandardMaterial

Program Info Log: Fragment shader is not compiled.
 

FRAGMENT

ERROR: 0:1862: 'uIblStrength' : undeclared identifier
 

  1857:   vec4  _sm = textureLod(uCustomIbl, _Rr, _lod);
  1858:   vec3  _L  = pow(_sm.rgb * _sm.a * 16.0, vec3(2.0)).xyz;
  1859:   vec3  _Lc = min(_L, vec3(1.5));
  1860:   vec3  _env= _L + uIblMix * (_Lc * 0.299805 - _L);
  1861:   _env *= uIblScale;
> 1862:   gl_FragColor.rgb += _env * uIblStrength;
  1863: #ifdef DITHERING
  1864: 	gl_FragColor.rgb = dithering( gl_FragColor.rgb );
  1865: #endif
  1866: }
```

同一批里 `Shader Error 1282` 版本逐字相同，只有行号不同（`0:1857 / 0:1859 / 0:1962 / 0:1959` 等，
即不同 program 的 shader 前缀长度不同）。**全部 21 条的唯一 ERROR 就是这一条 `uIblStrength : undeclared identifier`。**

**归属**：关键行 `gl_FragColor.rgb += _env * uIblStrength;`
- `bak_20260916_232432`（22:04 版）：`gl_FragColor.rgb +=` 出现 **1 次**
- `bak_20260917_220023`（2026/9/17 21:40 版）：**0 次**
- **当前文件：0 次**（全项目已无该行任何形态）

### 2.3 当前文件里仍存在的"同类地雷"（**死代码，但值得知道**）

`weapon_skin_viewer.js` L1535–1549 的 `SRC_ENV_GLSL` 数组：

```js
const SRC_ENV_GLSL=[
  '/* 源 IBL：直接叠加到最终输出，不依赖 Three 的 USE_ENVMAP 路径 */',
  'float _rgh = max(uSrcRough, 0.0019);',
  'float _lod = 5.0 + 1.2 * log2( _rgh );',
  'vec3 _Rv = reflect( normalize( vViewPosition ), normal );',
  'float _c = cos(uIblRot), _sn = sin(uIblRot);',
  'vec3 _Rs = vec3( _Rv.x*_c + _Rv.z*_sn, _Rv.y, -_Rv.x*_sn + _Rv.z*_c );',
  'vec4 _sm = textureLod( uSrcIbl, _Rs, _lod );',
  'vec3 _L = pow( _sm.rgb * _sm.a * 16.0, vec3(2.0) ).xyz;',
  'vec3 _Lc = min( _L, vec3(1.5) );',
  'vec3 _env = _L + uIblMix * ( _Lc * 0.299805 - _L );',
  ...
].join('\n\t\t\t');
const applySourceEnvBright=(mat,primIdx,mode)=>{
  if(mat&&mat.userData){ mat.userData.__srcEnvBright='removed_by_policy_20260918'; }
  return;                       // ← L1556 无条件早退，后面整段（含 onBeforeCompile 注入）不可达
  ...不可达代码...
};
```

- 该数组**引用了 `uSrcRough / uIblRot / uIblMix / uSrcIbl`**，其中 **`uSrcRough` 在项目里再无任何
  `uniform float uSrcRough;` 声明**（当前文件仅有 L1574 那处，且在被停用的不可达分支里）。
- 也就是说：**一旦把 L1556 的 `return;` 删掉，`uIblStrength`/`uSrcRough` 未声明的那一类错误会立刻复活。**
- 目前它安全，仅仅因为 `applySourceEnvBright` 是无条件早退的死函数。
  （`SRC_ENV_GLSL` 作为常量在模块加载时求值，不会发给 GL。）

---

## 3. 本轮三遍实测：0 编译错误

| 运行 | 后端 | console.error | consoleAPICalled 中 Shader Error | compileFail | linkFail(link=false) | `__ladderCompile()` |
|---|---|---|---|---|---|---|
| run1 `glsl_forensic_probe.py` | SwiftShader | 0 | 0 | 0 | 0（30 shader 全 COMPILE_STATUS=true） | — |
| run2 `glsl_probe2.py` | NVIDIA D3D11 | 0 | 0 | 0 | 0 | — |
| run3 `glsl_probe3.py` a | NVIDIA D3D11 | 0 | 0 | 0 | 0 | 14/14 program vs/fs/link 全 true，info_log 全空 |
| run4 `glsl_probe4.py` final | NVIDIA D3D11 | 0 | 0 | 0 | 0 | 14/14 program vs/fs/link 全 true，info_log 全空 |

`renderer.debug.checkShaderErrors = True`（viewer 自己设的，`__ladderCompile()` 回读确认为 true），
说明 three 的报错分支是**开启**的——它没报，就是因为真的没失败。

### 3.1 唯一在跑的"类报错"：ANGLE 校验器警告，**不是 GLSL 错误**

```
THREE.WebGLProgram: Program Info Log:
Two textures of different types use the same sampler location.
```

- 走的是 `console.warn` 分支（`getProgramInfoLog` 非空 && `LINK_STATUS` 为真），**不是** `console.error` 分支。
- 涉及的 program：7 个（`MeshStandardMaterial`，带 `uCustomIbl` samplerCube 的那些，cacheKey 前缀 `srcIblRad_`）。
- 是 ANGLE/SwiftShader 对"samplerCube 与 sampler2D 被分到同一 texture unit"发出的校验器提示，
  当前 SwiftShader 下 `validateProgram()` 返回 false、**但 info log 为空、`gl.getError()==0`**。
  这批 program 随后 `validateAfter=true`（绑定纹理后重验通过），**照常 draw，画面正常**。
- **`Shader Error 0 - VALIDATE_STATUS false` 字面上的"0"就是这个 `getError()==0`**。

### 3.2 `Shader Error 1282` 的由来（供参考）

three r180 (`three.module.min.js` @215734) 的报错分支原文：

```js
if(!1===i.getProgramParameter(_,i.LINK_STATUS))
  if(c=!1,"function"==typeof e.debug.onShaderError) e.debug.onShaderError(i,_,M,x);
  else{ const e=Si(i,M,"vertex"), n=Si(i,x,"fragment");
        console.error("THREE.WebGLProgram: Shader Error "+i.getError()+" - VALIDATE_STATUS "
          +i.getProgramParameter(_,i.VALIDATE_STATUS)+"\n\nMaterial Name: "+t.name
          +"\nMaterial Type: "+t.type+"\n\nProgram Info Log: "+o+"\n"+e+"\n"+n) }
```

- **`Material Name:` 后面为空** ⇒ 这些材质从未设过 `mat.name`。
- **`Material Type: MeshStandardMaterial`** ⇒ 失败 program 就是链材质（`MeshPhysical/Standard` 家族）。
- `Si()` 只在 info log 命中 `/ERROR: 0:(\d+)/` 时才附带源码上下文行 —— 所以
  **"带 `ERROR: 0:NNN:` + 源码片段" 只可能来自 driver 真的报编译错**，不可能是 `validateProgram` 的假警报。
- `1282` = `GL_INVALID_OPERATION`（three 取 `getError()` 的时刻有别的 INVALID_OP 在飞）；
  `0` = 取到 `GL_NO_ERROR`。二者是**同一个编译失败**的两种取值。

---

## 4. 对 lead 的直接建议

1. **不要再去抓 GLSL 正文了——当前版本没有 GLSL 正文可抓。** 若要复现旧错误，必须回滚到
   `weapon_skin_viewer.js.bak_20260916_232432`（`__rough` 代）或 `bak_20260917_220023`（`uIblStrength` 代）。
2. 判断"错误是否只在本轮改动后出现"：**不是。** 两代错误分别锚定在
   `bak_20260916_232432`（2026/9/16 22:04）与其中间态；当前版本（2026/9/17 22:17，SHA256 `6938828F…`）两处都已消除。
3. 若仍看到 `Shader Error 0 - VALIDATE_STATUS false`：请**先确认它是否带 `ERROR: 0:NNN:` 正文**。
   不带正文 = ANGLE 校验器噪声（本轮实测的那 7 个 program 即此），不影响渲染，不必当 P0。
4. 真正需要盯的是 §2.3：`applySourceEnvBright` 的 `return;` 是当前唯一的护栏，
   一旦有人为了"恢复旧口径"去掉它，`uIblStrength` / `uSrcRough` 未声明错误**必然立刻重现**。
   建议直接把 L1535–1581 的死代码删掉，或把 `uniform float uSrcRough;` 补进 `SRC_ENV_GLSL` 的声明清单。
