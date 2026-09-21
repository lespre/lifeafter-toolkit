# 武器皮肤自动出图规则 v1.4（weapon_skin_pipeline）

> v1.4 增补（2026-09-14，光影咏叹调盲测后的通用修复）：`--dual` 双持组合、`_input_manifest.json` 输入清单（通用源锚定）。
> 冻结 v1.2 快照 + 盲测交付：`E:\la拆包项目\03拆包产物\_freeze_v1.2\`（含回归证据）。**跨资产修复须双资产回归（029 + 1003_010，字节级对比）。**

> 目的：把极光剑（skin_2003_029）逐轮人工校准沉淀为**可复用管线**——以后新皮肤一条命令出图 + 自动质检，不再逐张人工调。
> 落地：`E:\la拆包项目\01拆包器本体\工具库\06_皮肤定位链\weapon_skin_pipeline.py`

## 一、用法

```bash
python weapon_skin_pipeline.py <mesh路径> <贴图目录> <输出目录> [--profile 皮肤名]
# 仅重跑后处理+质检（不重跑光栅渲染，需已有 _base.png）：
python weapon_skin_pipeline.py --qc-only <mesh> <贴图目录> <输出目录> [--profile 皮肤名]
# Source/material 模式（绕过 post_process 全部规则, 源材质直连 + 源纯度追溯）：
python weapon_skin_pipeline.py <mesh> <贴图目录> <输出目录> --profile 皮肤名 --source
# 源参数驱动（c159 路径参数 + 自动绑定 SubMesh→Material, 全部来源写入 provenance）：
python weapon_skin_pipeline.py <mesh> <贴图目录> <输出目录> --profile 皮肤名 --source --params-c159 <材质.c159>
# 材质分层渲染（正式路线, 8 张输出: BaseColor/Normal/Gloss/Reflection/Refraction/Subsurface/Fresnel/Composite_noSFX）：
python render_material_layers.py <mesh> <贴图目录> <输出目录> --materials <材质.c159> [--polarity smooth|rough|const]
# 测试: python test_c159_parser.py（跨LOD/跨资产 7 用例）· python test_provenance.py（单元 11 用例）· python test_provenance_e2e.py（端到端注入 7 用例）
```

输出：`render_final.png`（成品）+ `qc.json`（质检指标）+ `provenance.json`（源纯度追溯）。
贴图目录约定：`tex_4011.png`(基色源) `tex_4012.png`(法线, **GB 通道解码**) `tex_4013.png`(**材质遮罩：仅 B 通道 = 光滑度/光泽度语义**, 非发光层) `tex_4009.png`(护手银蓝源)。**`tex_4011_v19.png`（人工改色基色）已永久禁用, 出现即 provenance FAIL**。

## 二、渲染层规则（R 系列 = 渲染参数与材质规则）

| 规则 | 内容 | 依据 |
|---|---|---|
| R0 银蓝材质 | 护手银蓝 = 4009 源「去饱和53% + 冷偏(R*0.93/B*1.09) + 提亮1.05」 | 029 实证 |
| R0b 网格修复 | 顶点按位置焊接后再平滑法线（NeoX 顶点按 UV 缝分裂，不焊接=半球面平直） | 顶点 7943→位置 4013 |
| R0c 跨缝法线调和 | **相接的不同子网格在交叠带内互相平均法线**（默认 z 6.2–7.2 / ε0.12 / blend0.5）。修「两件硬拼」接缝 —— 这是法线断层，不是颜色问题（灰模复验证明） | 接缝夹角 80°→54° |
| R1' 刃口光（v1.1 源逻辑） | **几何耦合刃口光**：菲涅尔(edgek=0.68,pow=1.6) + 刃口定向光泽(基于**几何法线**的 ndv 窗口 exp，mu=0.52/sigma=0.22/k=0.55，冷白(0.78,0.87,1.00))。不涂白、随真实倒角结构、独立参数、Unlit 不出现不发黄。**证据：五张贴图边缘面逐通道对比无银白差异 → 刃缘银白系材质光照层（金属倒角反射+菲涅尔自发光 u_emissive_fresnel），非贴图区** | 边缘面UV采样实验 + c159 材质参数 |
| R1(deprecated) 银蓝刃片带 | 旧屏幕空间距离带（band 模式保留在参数 edge_mode='band'，默认已关闭） | 已被 R1' 取代 |
| R2 过渡区 | 剑身根部亮度向护手均值渐变匹配 + 接缝轻阴影 | 消「亮度突然变暗」 |
| R3 金色规整 | 去黄(R+6% G-3% B-1.5%) + 金褐暗部(lum<0.52 乘(1.02,0.93,0.86)) + 亮部高光提升；色度对齐游戏取样 | 原图取样校准 |
| R4 护手细碎冷光 | 护手区细噪声变化 ±4.5% + 冷偏移 | 消「平滑白金色」 |
| R5 宝石高光 | sub2 每个成块区域加左上高光点 | GPT 清单#6 |
| R6 圆孔内衬 | **自动检测**（FillHoles 找内部背景色区域）→ 金褐色内衬 + 上暗下亮 + 下缘反光 | 原图有内衬非黑洞 |
| R7 冷调阴影 | 暗部乘 (0.96,0.99,1.04) | 冷环境反射逻辑 |

## 三、质检层（QC 系列 = 自动质检，不通过即视为回退）

| 编号 | 检测 | 阈值 |
|---|---|---|
| QC1 连接处 | 护手侧 vs 剑身根侧：亮度差 dL / 色度差 dRB | dL<0.18 且 dRB<0.35 |
| QC2 刃口 | fresnel 模式=轮廓峰值比(局部峰值/内侧均值)及沿轮廓变化 | 1.10 < rim_peak_ratio < 2.8 且 var > 0.04 |
| QC3 材质分区 | 金区(R-B>0.16) / 银区(B≥R) / 红宝石(R-G>0.16) 三区并存 | gold>5000 且 silver>800 且 gem>200 |
| QC4 圆孔 | 孔内亮度 / 暖度 | luma>0.06 且 warm>0.05 |
| QC5 法线调和 | 跨缝平均前后夹角 (证据字段) | 记录 before/after（029: 80°→54°） |

**接入判据**：`qc.json` 中 `ok:true` 才可交付；任一 false = 该轮校准回退。
QA 扩展方向（GPT 建议）：同类金属子网格接缝的 颜色/金属度/粗糙度/法线 四通道比对 —— 目前 QC1+QC5 覆盖颜色与法线两通道。

## 四、逐皮肤参数（SKIN_PROFILES）

默认规则对武器皮肤通用；个别皮肤补充 profile 字段：
- `grip_z` + `grip_rgb` + `grip_blend`：手柄区提亮（029: z 9.6–11.6 → 象牙金 0.91,0.88,0.81）
- `spike`：尖晶/特殊凸起涂银（029: z 0.85–1.55 & y>0.76 面部 → 银白）
- `tex`：贴图文件名对照

## 五、实证记录（029）

- 白刃宽度：游戏原图 ≈ 刀宽 8–9%（逐像素量测），本管线出图 7.7% ✓
- 接缝法线断层：跨缝夹角 80.0° → 调和后 53.6°，灰模复验接缝暗线基本消失
- 金色色度：与原图取样对齐（通道比校正 R*0.96/G*0.94/B*1.20 后微暖回补）
- 已知边界：**特效层（火焰/粒子/自发光/环境反射）在引擎层与 effect3.wpk，不在本管线范围**；静态图还原极限即材质+结构层。

## 五之二、源参数与源纯度（v1.2 新增）

- **c159 通用解析器（v3, `c159_pair.py`）**：无固定偏移/固定组号/固定块数/固定文件名；名字表、槽位组（双字节对齐扫描）、数值块（簇检测）、块↔组评分配对、材料归属、`003997` 绑定解析全部按结构自动识别。`--params-c159` 接收**实际文件路径**并自动建立 SubMesh→Material 对应。跨 LOD（029 L0-L3）× 跨资产（028/034）测试 `test_c159_parser.py` 7/7 通过；"18/19"疑问 = 旧版按偏移区间取块的边界产物（18 条数值 + 1 条下一材料的字符串），v3 已按数值簇取块并显式报告消耗/剩余。名称-数值配对表见 `C159_PARAM_PAIRING.md`（宝石红三色跨 LOD 逐字节一致）。
- **provenance 两拆分 + 原始性锚定（fail-closed）**：`source_data_integrity`（输入是否全部来自原始文件：每张在用贴图与原始 DDS **像素级锚定比对**（BC7 重解码, maxdiff=0）+ 规范化路径检查 + 人工项标志）与 `shader_fidelity`（shader 是否按源语义实现；存在近似灯光/法线调和/过渡模型/后处理即 `approximate`，不再用单一 pass 表示忠实还原）。端到端注入测试 `test_provenance_e2e.py`（真实启动管线 7 用例：clean/v19/tint/face/band/post/哈希替换贴图）全部按预期 pass/fail。
- **4013 语义定案（受控实验）**：B vs 1-B vs 常数 三对照渲染 ⇒ **B = 光滑度/光泽度**（装饰/抛光处出现锐高光、平面收敛；反相则细节变哑、违反金属物理）。接入途径 = `render_material_layers.py --polarity smooth`（默认）。旧"发光层"标注全部废止。
- **材质分层渲染器（v1, `render_material_layers.py`）**：输出 BaseColor/Normal/Gloss/Reflection/Refraction/Subsurface/Fresnel/Composite_noSFX；`u_base_color`/`u_crystal_color`/`u_refraction_color`/`u_subsurface_color` **分别进入各自层**（不再合并为单一 Tint）；基色贴图 sRGB→线性、参数线性、合成线性→sRGB 输出；4012 法线=GB 通道（全部子网格）、**4010 = 灰度细节图（R=G, B≈1, 非法线）→ 以高度梯度 bump 接入晶体子网格**；光照=文档化固定 rig（记入 layers_trace.json，属 approximation）。护手发黑/衔接断层在白刃与宝石分层正确后自然缓解；剩余差距（护手亮度、冷色刃缘、宝石通透）= rig 与 Sub0 引擎默认值问题，列入下一轮。

## 六、留给下一轮（细化项）

- 手柄编织纹理/雕纹凹凸（目前仅颜色+法线贴图近似）
- 刀尖/下半段残留低模三角面感（已焊接平滑；剩余=真低模几何）
- 圆孔内衬可再提亮一档（质检通过但目视偏暗）
