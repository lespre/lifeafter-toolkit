# 拆包器进展与交接日志 -- Hermes 规范重整版

> **逆向对象**：`E:\mrzh`（体验服；默认简单生存服，结论必须声明服务器分支）  
> **对照基准**：`E:\lifeafter`（正式服；只作格式/结构对照，禁止混入体验服业务结论）  
> **唯一活跃产物根**：`E:\la拆包项目\03拆包产物`  
> **本日志状态**：当前可信结论的唯一入口。历史原稿不删除，见文末“原稿备份”。  
> **最近重整**：2026-09-01（新增顶部对接快照，历史章节内容不改写）

---

## ★ 最新对接快照（2026-09-01，接手先读这一节）

> 本节是全局权威导航，结论以最新章节为准；下方历史章节保留完整审计轨迹。引用任何旧结论前先回这里核对是否已被后续章节覆盖。

### A. 格式解码能力现状（别重复造轮子）

| 格式/能力 | 状态 | 依据章节 |
|---|---|---|
| .gpk 外层（AES-ECB KEY `606308d8a32c782013d26c2f226f686d` + 32B 条目表 + lz4/zstd，flag 0/2/12） | **已破可复跑** | 一、工具库 |
| .npk 外层条目提取 | **已破** | 一 |
| WPK/IDX 的 **1DPW**（AC/PC/XC 派生 key + ENON/DTSZ→zstd，端到端出 DDS，含错 key 负对照） | **已破** | 接力包 run_004 |
| BinDict 行结构 D6/C6/96/0x36/0x27、CHS 字符串池、uleb/标量流 | **已破，值解码精确** | 十七（walkthrough 证明 CHS 槽位 100% 精确、解码器无 bug，**勿再改 bindict_table 核心**） |
| FSB5 音频（vgmstream 逐轨转 wav） | **已破** | 早期成果 |
| .fpk（32B 头 + **独立 Zstd 帧流**，`iter_fpk_frames` 按真实 eof 顺序解帧、`extract-fpk-full` 全量拆、能解出 .mtg 材质；递归全索引 216 包 / 300.7 万条 / 0 失败） | **常规包已破**；仅 013/020/021 三个 OpenWorld/PVE 场景包=明文 float 头+加密体（熵 6.84、非 AES、流变换未破），低价值已搁置 | 14B、fpk_frames.py / fpk_toolkit.py / test_fpk_frames.py |
| THFB .thx/.thh（**27.3 万** THX hash 提取 + hash↔IDX merge 映射 + weapon SKPW→1DPW→DDS 复验；纹理本体走 1DPW 链出图） | **索引与桥接已破**，不是"数据区未破" | thfb_toolkit.py、14B |
| gres 分卷：**KPGF 已破**（36B 明文头+多帧 zstd 跨帧读，textures.gpk 564 条目→493 张 BC7_UNORM DDS）、FPGH/HPGF 可识别；**RPGF/CPGF 仅 AES 解头/早期脚本探索，主解包链未固化** | KPGF 已破、RPGF/CPGF 部分 | 14B、resource_resolver.iter_kpgf_entries |
| BinDict **多 schema_ref 字段名配对**（22470 有 8 个 schema_ref，值解码对、字段名按 slot 错位） | 部分→**时装表已用值分类法稳定落地（见二十章）**：显示名在 charm_value 槽（格式 `名`/`名-N天`时限）、part 槽实为模型/图标路径、desc/name 槽存整数文案ID、描述句槽逐行跨记录错位（同 slot 在不同行混装 part/desc/path/color，0% 可按字段名锚定）；治本=按 schema_ref 分别配字段名池（P3，仍开放） | 十六、十七、**二十** |
| nxs 数值表 attrs（武器攻击力/火力） | **已破并固化为可复跑脚本** `weapon_attrs_table.py`：直接从 npk 提 BASE(A130A31532FAF63C)+CHS(94AB0B3F)，武器行 schema=164051 的 **`attrs` 字段**(只有它，非其他 type=11) → attrs 对象 schema=6109，**field23=`hurt` 攻击力、field35=`power` 火力**；输出 147 条装备 CSV/JSON。硬验证：**AUG 突击步枪 hurt=148/power=2.0/射速550/耐久600**（普通·雪地·雨战三版一致）；hurt=161 族当前中文名=斯泰尔狙击枪（旧接力包内部代号 SCAR）。伤害=攻击力×火力。fid 漂移时用 `relocate_equips_base_mp.py`（25 进程）重定位 | 05_BinDict解码器/weapon_attrs_table.py、relocate_equips_base_mp.py；2026-09-01 |
| 文件名还原 | **部分**：字典 + 配置表 bindict path_id 通道已还原 **170 条**带名路径；但 gpk 匿名条目的**全局自研 64 位 namehash 未破**（双 Murmur/多种子 0 匹配；8-30 验证 c1/c2 是内容指纹而非名字哈希），缺全局 fid→路径名表 | filename_restore.py、06_文件名还原/、14.1 六路证伪 |
| 3D：NeoX `.mesh`/`.c159`/`.rgis` | **部分（非纯搁置）**：mesh 头+顶点流格式已解析（u16+u16+AABB+u32×8+f32）、`.mtg` 材质链配置→gim→mesh→mtg→四通道 PBR 100% 闭合、有顶点提取/3D 预览脚本；**完整渲染未成品**（索引/骨骼绑定/渲染器待做） | parse_neox_mesh.py、14B、P1 成果 |
| lifeafter.exe（改 UPX + 整体加密） | **未破**：仅完成 PE/节区熵/壳特征/导入表侦察，未脱壳 | 12_EXE脱壳分析/ |
| ~~enc_jpg 伪装时装图标~~ | **已证伪、不是加密格式**（7.2 作废结论，勿再当硬骨头/待解格式） | 7.2 |

### B. Wiki 现状（`08Lifeafter wiki`，git 已提交，**11 板块 3935 条**（2026-09-01 晚武器数值+载具后，HEAD 见 git log）；`python tools/build_wiki.py` 重建）

> **快照更新（2026-09-01 20:40）**：体验服推送二期实装，`script.py314.lc.npk` SHA 由 780363b86008 → **BA8A239A891D6230…**（25485 条目，比旧快照多 120 条），新 workcopy `config_work/script_py314_docs_BA8A239A/`（解包脚本 `dump_BA8A239A.py`，0 解码错误）。**引用 9-1 晚之后结论用 BA8A239A。**

| 板块 | 条数 | 证据 | 备注 |
|---|---|---|---|
| 核芯图鉴 | 108 | 32 verified / 76 structure | 主线 8 期+返场 24 |
| 武器皮肤（含特效组） | 128 | 97 structure / 31 candidate | |
| 未上线武器贴图候选 | 324 | 全 candidate | weapon.gpk 匿名 DDS，待复证 |
| 抽奖奖池·帝皇铠甲 | 54 | **全 verified** | 391762 五层闭环，见十八 |
| 抽奖奖池·铠甲再临(刑天飞影) | **10** | **9 verified + 1 structure**（commit fdb86bb） | **二期已实装，导出器 export_kaijia_phase2.py**：旧 83 条未上线版、reward 逐格历史复用旧行**均剔除**，只列本期 panel_show_item_ids 面板 10 件：左大奖刑天铠甲139292/右大奖飞影铠甲139293、**刑天载具「火刑战驱」194190**、疾影枪1110181/火刑电光炮1110182/战神烈火剑1110183、刑天召唤器633070140(verified)/飞影召唤器633080140(仅 ID 段推断 structure)、球状闪电134061/酸焰激流132694核芯。主池391782/福袋391783/UI PanelSuperFashionLotteryV15/宣传视频 kaijiayongshixia.mp4。**命名只用 gift 礼盒表/武器皮肤总表/硬证据；all_equips 的 name/desc/icon 跨记录错位（194190 被错写成“火箭筒体验版/盾补金木研”，实为载具，结构字段 vehicle_type=3、carrier2025/car_2001005 可靠），不参与命名** |
| 人物·铠甲勇士联动外观 | 9 | structure | **2026-09-01 晚重建（BA 快照，经 tools/lib_fashion 统一解码 + 面饰专池补充）**：刑天铠甲(本体model32710)/帝皇铠甲(31643)/帝皇战翼(30950)/刑天召唤器(32709)/飞影召唤器(80185)/铠甲飞兔(80610)/飞影浮澜头饰(80185) + 面饰刑天面甲/飞影锋眸；期限档1/3/5/7/14/30，900开头=时限版model。**双源确认无独立「飞影铠甲」整套衣服本体**。导出器 export_fashion_kaijia.py |
| 人物·全量时装衣柜 | 1093 | structure | **2026-09-01 晚重写（旧457→1093）**：直接从 BA entry022570(base)+020834(chs) 用 lib_fashion 解码，不再依赖旧内容驱动 json；整套751/头饰66/头饰·衣服200/衣服75/套装1；可靠字段=显示名/部件/时限/本体model/资源路径，**desc 一律不挂（本表描述槽逐行错位、0% 可锚定，待 name 文案ID→i18n 表桥接）**；导出器 export_fashion_wardrobe.py |
| 人物·面饰/挂饰 | 180 | structure | **2026-09-01 晚新增**：面饰专池 BA entry010816/009169（0x73 legacy 自带 CHS 池，fid 6CD197C9670A961C / 5D094B94133851D2），名+时限可靠；**描述需解 legacy 表行 name→desc 槽才能配对（池内邻接配对仅21%不可靠，暂留空）**；导出器 export_fashion_face.py |
| 武器·本体数值（攻/火力/理论伤害） | 147 | **全 verified** | **2026-09-01 晚新增**：weapon_attrs_table.py 出表→export_weapon_attrs.py 转板块；hurt攻击力/power火力/理论伤害=攻×火力/射速/耐久，AUG 148×2.0/射速550/耐久600 硬锚点，hurt=161族=斯泰尔狙击枪；weapon_type/kind 内部码名称待映射 |
| 载具·模型清单 | 125 | verified1/structure53/candidate71 | **2026-09-01 晚新增**：export_vehicle_catalog.py。**关键事实：all_equips 载具行 name/desc/icon 槽错位比时装更严重（混入鱼竿/霰弹枪/材料机），不能逐行命名**；以 body_model 为锚（124 去重型号），类型从路径目录推断（car/motorcycle/aircraft…比 vehicle_type 数字码可靠），候选名经同系列投票+载具语素白名单+物品黑名单；**火刑战驱(194190)当前不在 all_equips（无此行/无 car_2001005），按二期奖池 gift 硬证据 verified 单列**；71 个型号系列名可回填但具体皮肤名待 gift/item 专表 |

### C. 已 verified 的硬锚点 / 已 BLOCKED 的事
- **verified**：帝皇铠甲奖池 `lottery_id=391762`，`super_fashion_lottery → reward_pool(slot) → gift_data` 五层闭环；极光剑=皮肤、帝皇铠甲=时装、帝皇裁决/帝皇瑞昭交易盒；稳定 **file_id**（不随热更漂移，entry 号会漂移）见 18.1。
- **BLOCKED（时装全量名册，2026-09-04 终判）**：时装外观表（22570）name/desc 列存在但存 **int 文案 ID**（0x01，100% 稳定），中文需文案表映射；文案表 BA 仅 176B 壳（fashion_id_2_season_id，FID 18F80BE7F5D44EF2），**正式服 45687-entry 包内不存在该 FID**→服务端专属，客户端不可得。`fashion_wardrobe_slots`（1489 条）即客户端可达文字层上限（内嵌 CHS 名，值分类+富文本解析），**不得宣称全量/列直读**。desc 混入名的句子防护（_SENTENCE_WORDS/长度/截断三层）已在解析器 v3 词表落地但**全表重建与测试未跑**（卡点登记时工作区状态）。
- **BLOCKED（武器皮肤 UI 特效名匹配，27.19 定论）**：es 行=热更档案行；改名/升格皮肤 UI 显示行=运行时选择，静态包内不可推；**UI 短名=用户实机锚点唯一可靠源**（11 锚点逐类目精确 + content 22 + 注册行 50 已达静态上限）。
- **BLOCKED（时装类细分系列，2026-09-04 用户指示：大分类（1）头饰套装衣服（2）发饰面饰（3）背包挂件（4）投影荧光棒先行，细分进卡点）**：
  ① 发饰/面饰/挂件细分口径：face 槽 180 板（player_module_appear_data part_type=face 单一值）内眼镜/面具/帽子/头顶装饰/挂饰的游戏内格归属待实机或专表（27.36 板已发布大分类，细分不裁决）。
  ② 挂件格：时装表内 0 行、face 板 3 条挂饰（不在线/入侵者/救救我）——背包格 vs 挂件格边界待实机。
  ③ 背包行级全量：行身份判别被"每行配套背包模型引用"三重污染（27.41/27.42 穷尽）；138 裸名候选家族 + 513 纯 bag 家族待实机锚点裁决（用户当前无法查看样本）。
  ④ 投影：无同快照可定位表（BA8 全表名扫描无投影数据表）。
  ⑤ 荧光棒 2 条已全量发布（fashion_glow_slots）；更多形态待专表。
- **BLOCKED**：臻藏/宸世臻石完整兑换表——detail alias 不唯一、缺 runtime 当前店铺选择器，结论 `BLOCKED_NO_TRUTHFUL_EXCHANGE_CSV`，**不生成/不覆盖 CSV**，恢复三条件见 19.3。
- **证伪记录（勿复活）**：「五行合璧本地 0 命中」早期说法已被 nxs 解密池推翻；「fpk=55 个独有」是把 gpk/fpk 混写，独有数要按正式服目录差集实时算；「宽 schema 是解码器 bug」已被十七章 walkthrough 证伪；「22470 缺字段名池」已被 16.5 证伪（20739 含全部英文 key，真因是 8 个 schema_ref 字段名排布不同）；「FPK 数据区自研加密未破 / THFB 19.8 万且数据区未破 / KPGF 分卷数据未破」三条旧表述已被 14B 与实际代码证伪——FPK 常规包是 Zstd 帧流已全量可解、THFB 为 27.3 万 hash 可桥接出图、KPGF 已解出 493 张 DDS（2026-09-01 核对代码修正，见 A 表）。
- **命名规则（2026-09-01 新增，勿再踩）**：`all_equips_data` 的 **name/desc/icon 字段在载具/道具行上会跨记录错位**（实例：panel 194190 被错命名“火箭筒体验版/盾补:金木研/icon_194192”，但 vehicle_type=3、body_model=carrier2025/car_2001005 等结构字段是它自己的，用户确认实为**刑天载具「火刑战驱」**）。故 all_equips 只可信**数值/结构字段**（hurt/power/model/sfx/vehicle_type），**不可用 name/desc/icon 给物品命名**。可靠命名优先级：gift_data 礼盒表(key=item_id) ＞ 专门表（武器皮肤总表/时装表）＞ 硬证据交叉 ＞ 用户确认；都没有就标 candidate，不硬套。

### D. 下一步队列（按优先级，恢复时照做）
1. ~~**P0 修 fashion_kaijia 的 desc**~~【**已完成 2026-09-01** commit 8a91391】：已删逐条 desc、改按基名主题 + meta.liaison_descs 6 段全局描述，board.html 新增绿色联动描述区块，浏览器实测无错配。
2. ~~**P1 用 18.1 的 verified join 重建「铠甲再临」**~~【已完成 2026-09-01】二期实装后，用更直接的 **super_fashion_lottery_conf_data key232 → panel_show_item_ids 面板清单 + left/right_item_id** 锚点（比靠 broadcast_content 播报语分类可靠：奖励格大多无播报语，旧法只认出 2 个涂装），名字走 gift/all_equips 名表 +《武器皮肤总表v3》硬映射，产出 7 verified。方法固化在 `export_kaijia_phase2.py`，可对后续新奖池复用（先找 super_fashion 配置 key→lottery_id→panel 清单）。
3. **P2 人物类扩板块**【**主体完成 2026-09-01 晚，见二十章**】：✅ fashion_wardrobe 重写为 1093 件全量（整套/头饰/衣服，不再只收带后缀的）；✅ 新增 fashion_face 面饰/挂饰 180；✅ fashion_kaijia 重建为 9 条并补刑天面甲/飞影锋眸，**双源确认无独立「飞影铠甲」整套衣服本体**（飞影线=召唤器80185+锋眸面饰+浮澜头饰）。统一加载器 `08Lifeafter wiki/tools/lib_fashion.py`（值分类法，不信错位字段名）。**遗留小待办**：①时装/面饰描述需解 name(slot7)=整数文案ID 对应的 i18n 文案表（本表描述槽不可用）；②面饰描述需解 0x73 legacy 表行 name→desc 槽（池级邻接仅21%）。
4. **P3 治本（仍开放，可交接硬骨头）**：时装表 19 个 schema_ref（主270688=4923行）逐 schema 反查正配字段名池（CHS 反查法见 16.4）；已排除"解码器/切分/bitmap bug"，根因是字段名(程序标识)与行内实际语义载体分离、name/desc 存整数文案ID。
5. 长期硬骨头（勿在主线硬耗）：FPK 仅余 **013/020/021 三个 PVE 场景包加密体**（非主线、低价值）；gres 的 **RPGF/CPGF 分卷主链**；gpk 匿名条目的**全局自研 64 位 namehash**（字典/path_id 通道已还原 170 条，哈希本体未破）；**exe 脱壳**（仅侦察）；**3D 完整渲染**（mesh 顶点流已解析，缺索引/骨骼绑定/渲染器）。已破勿再当硬骨头：FPK 常规包 Zstd、THFB 索引桥接、KPGF、1DPW、**attrs 字段名绑定（可出 hurt/power）**；已证伪勿复活：**enc_jpg 伪装**（本不存在该加密格式）。

### E. 关键路径
- 解包器本体：`01拆包器本体\工具库\10_应用核心\toolkit_core\`；wiki：`08Lifeafter wiki\`（独立 git）。
- 配置 entry 解包产物与全部分析/验证脚本：`03拆包产物\config_work\`（当前 Documents workcopy：`script_py314_docs_56def41376ed`；Hermes 十八/十九用 `script_py314_docs_780363b86008`，**两个快照 SHA 不同，引用结论时注明用的是哪个快照**）。
- 最新道具名表：common_item **entry 17922（35948 行全带名）**，旧名表已过期勿用。
- 源只读：`E:\mrzh`（体验服）、`E:\lifeafter`（正式服，仅格式对照）。

### F. 章节编号说明（多 agent 追加导致重号，按此读）
- 有两个「十四」：第 479 行=体验服更新后武器皮肤比较；第 548 行=材质→纹理链攻坚（后者可称 14B）。
- 有两个「十五」：第 516 行=追加模板；第 618 行=Wiki 数据层补全（后者可称 15B）。
- 时间线最新为 十六→十七→十八→十九；**冲突时章节号靠后/日期靠新者为准**。

---

## 〇、写入规范（以后必须遵守）

每条新增结论必须先写清以下元数据：

```text
日期：YYYY-MM-DD
作者：Hermes
模型：gpt-5.6-terra（openai-codex）
范围：源包 / 服务器分支 / 表或资源路径
证据等级：已验证 / 待复证 / 作废
来源：原始文件、entry、同包 base+CHS、关键 offset 或用户实机锚点
```

### 证据与措辞

| 标记 | 含义 | 可以怎么说 |
|---|---|---|
| **已验证** | 同包原始字节、结构化行关系、实机锚点或实际回归共同支持 | “已确认”“可复跑” |
| **待复证** | 结构可读，但字段语义、业务 join、服务器启用状态或名称回填缺一环 | “候选”“待校准” |
| **作废** | 被更强的同包证据、用户实机锚点或解析错误推翻 | “不得再引用” |

**硬规则**：

1. 原始客户端文件只读；所有新产物写入 `03拆包产物`。
2. base 与 CHS 必须同包配对；跨包字段名串位时，宁可不命名也不能硬绑。
3. 服务器分支是业务结论硬边界。经典服、简单生存服、yk/kjxq 等只能作格式对照，不能混奖池、奖励、概率或活动启用状态。
4. `0x0b`、`0x27`、`0x36` 等结构关系先记录原始偏移和字节范围；无字段级证据不把“相邻”“同名”“值相似”升级为业务关系。
5. 任何活动的“当前期”必须同时核对活动配置、服务器分支、过期/版本条件与用户实机事实；不能从旧行、root 同编号、截图倒计时或其他活动时间硬套。
6. CSV 必须 `utf-8-sig`；旧错误 CSV 保留审计但明确作废，禁止静默覆盖。

---

## 一、接手先看：当前可信能力与边界

### 1.1 已具备的通用能力

| 能力 | 状态 | 关键边界 |
|---|---|---|
| NPK/FPK/GPK/WPK/IDX 等外层提取、AES/压缩链 | 已验证 | 容器切出不等于业务资源已命名或已可视化 |
| BinDict `D6/C6/96/0x36/0x27` 结构解码 | 已验证（具体表可能有变体） | 每表先验证 framing、schema、index 与同包 CHS；不把未支持尾变体硬解 |
| 活动配置表定位与热更 key diff | 已验证 | 必须先锁定 Documents/根包版本和目标服务器分支 |
| 活动奖池数据行、reward jump、物品/礼盒/时装三级回填 | 可核验，需活动锚点校准 | 不把未校准行尾数字、池号、slot 或旧 CSV 当真实掉落关系 |
| 限定核芯研制主线/返场记录区分 | 已验证 | 可核验当前包与历史；不能预测下一期返场 |
| 宸世臻藏商店 `optional_hd_exchange_shop_data` 结构 | 部分已验证，业务列仍待校准 | 1863 条 0x86 详情不是已完成兑换表；禁止用时间或相邻组硬推列语义 |
| 资源逻辑路径→实体桥与纹理处理 | 部分已验证 | 匿名 GPK 条目的最终文件名/精确贴图归属仍有缺口 |

### 1.2 当前测试事实

- 当前 Hermes 环境没有 `pytest`；相关测试以零参数测试函数直接执行。
- 2026-08-31 对 `0x36 / 0x86 / legacy pool / index / reward_pool_export` 五组相关测试实跑：**20 项通过**。
- 这只证明已覆盖的结构/回归样本通过，**不等于**“全项目测试全绿”“所有兑换表语义正确”或“所有奖池业务 join 已完成”。

---

## 二、源包、目录与工具入口

### 2.1 源包基线

| 源 | 路径 | 使用规则 |
|---|---|---|
| 体验服热更主源 | `E:\mrzh\Documents\script.py314.lc.npk` | 当前活动/商店/热更结论优先来源；重新分析前先核 SHA |
| 体验服根包 | `E:\mrzh\script.py314.lc.npk` | 可作全量/历史格式对照；不得覆盖 Documents 当前业务结论 |
| 正式服 | `E:\lifeafter` | 只可用于格式、字段存在性或引擎行为对照 |

已登记 Documents 主包 SHA-256：

```text
56def41376ed2e71f1901756cde1984a53e6a6b863767e982ffd1eac601bb224
```

### 2.2 目录约定

```text
E:\la拆包项目\
├─ 01拆包器本体\工具库\          # 可复用代码；新通用能力必须入库并补回归
├─ 02文档索引\                    # 专题索引与方法文档
├─ 03拆包产物\                    # 唯一活跃产物根
├─ 04临时存放\                    # 一次性探针、备份、验证中间物
├─ 05（人写）纲要.docx
└─ 06（agent写）拆包器进展与交接日志.md  # 本文件
```

核心库：

```text
01拆包器本体\工具库\10_应用核心\toolkit_core\
├─ bindict_table.py       # 表 framing / index / D6/C6/96/0x36/0x86
├─ bindict_rows.py        # ULEB、标量解码
├─ reward_pool_export.py  # 奖池导出门槛
├─ resource_resolver.py   # 资源索引与物理桥能力
├─ weapon_skin_table.py   # 武器皮肤表
└─ source_lock.py         # 源 SHA 锁定
```

---

## 三、活动配置表：已验证工作流

### 3.1 能核验什么

活动配置的标准链是：

```text
Documents 与根包同名活动表 key diff
→ Documents-only / 目标 key
→ lottery_id、left/right item、fortune_bag、rule、mail、UI 字段
→ 服务器分支与用户实机活动状态
```

适用表包括 `super_fashion_lottery_conf_data` 等活动配置表。

### 3.2 已验证的边界

- `panel_show_item_ids` 只是**页面展示清单**，不能替代真实掉落或概率表。
- `fortune_bag_dct` 只证明后级引用，不能自动证明福袋/珍匣内的完整奖励。
- 活动 key、lottery_id 或文字命中在 root/其他服务器出现，不证明 Documents 当前目标服启用。
- “活动已上线/未上线”必须同时经过：热更 key diff、服务器分支、历史更新排除与用户实机状态核验。

### 3.3 当前可复跑的铠甲活动锚点

- 帝皇铠甲与刑天飞影必须按经典服/简单生存服分开处理。
- `super_fashion_lottery_conf_data` 可作为活动→lottery 的入口；礼盒、时装、配方、核芯需要继续用同包结构化表回填。
- 任何后续奖池交付都必须保留：`源包 SHA / entry / base+CHS 身份 / 行起点 / reward jump / item 回填来源 / 服务器分支 / 当前期筛选依据`。

---

## 四、活动奖池：当前可核验能力与停止条件

### 4.1 已验证的可复跑链

```text
活动配置
→ lottery_id / 服务器分支 / 当前期锚点
→ reward_pool_data_base（Documents entry 021284）
→ 正确同包 CHS 池 010171（12,345 槽）
→ 命名 reward 行
→ reward 0x0b jump
→ 0x27 [item_id, quantity]
→ gift / recipe / fashion / common_item 同包正源回填
```

**配池铁律**：`021284` 的正确 CHS 池是 `010171`（`010447/023616` 内容一致）；不得拿 `010502` 或旧 `23286` 串位配池。`note` 与 reward leaf 的名称明显互相矛盾时，先判为配池错误，不继续做主题解释。

### 4.2 奖池导出前必须过的门槛

1. 活动配置能明确给出目标 `lottery_id` 与服务器分支；
2. reward-pool 行到 pool/slot 的字段语义，必须由**已上线、用户可核验的同活动奖池**校准；
3. reward jump 必须实际解到 `[item_id, quantity]`；
4. 名称只允许用同包 `common_item / gift / recipe / fashion / all_equips` 正源回填；
5. 当前期筛选要有明确 expiration、broadcast、活动图标或用户实机锚点支撑；
6. 概率字段未完成语义/总和核验时，仅保留原始值，不输出“最终概率”。

### 4.3 明确禁止

- 行尾 `[39xxxx, slot]`、连续 slot、裸 ULEB 命中或同主题文案，**都不能单独**作为“pool→reward 行”的证据。
- 已被作废的 `391782/391783` 旧复证 CSV，不得再用作真实掉落、概率、数量、slot 或获取方式结论。
- “某个表能被结构解码”不等于任意活动奖池都已业务闭环。

### 4.4 当前状态

- 帝皇铠甲是后续校准真实 pool→reward join 的优先业务真值锚点；当前待办见第八章。
- 刑天飞影、其他活动或新版本包，在没有重新校准前均不得套用旧表的 pool/slot推断。

---

## 五、限定核芯研制：已验证表分工

### 5.1 三张表的职责

| 表 | 能确认什么 | 不能确认什么 |
|---|---|---|
| `nucleus_hd_conf_data` | 主线限定核芯研制期序、展示核芯 | 未来第九期或运营尚未下发内容 |
| `limit_nucleus_lottery_conf_data` | 当前/历史返场轮换快照 | 下一次返场的预告与时间 |
| `push_notice_data` | 已发生的返场公告记录 | 未发生返场的预测 |

### 5.2 当前已核验结论

- 主线限定核芯研制共 **8 期**；当前客户端主线最后一项是 `660082 深蚀追猎`。
- `660044 电掣双刀` 属返场，不是第九期主线新品。
- 当前包与推送记录都没有“下期返场核芯”的可验证预告。
- 正确输出：**“客户端未预置下一期；等待运营热更，再做同表 key diff。”**

### 5.3 禁止事项

- 不用返场表的当前行推断下一次返场。
- 不把正式服、其他服务器或旧公告倒灌到简单生存服当前期。

---

## 六、宸世／宸晶臻石／臻藏商店：当前真实状态

> **术语纠正**：现阶段已定位的是“宸世臻藏商店/宸晶臻石兑换页”，不是已经完成核验的“宸世奖池”。帝皇战翼转入的具体宸世活动池，尚未形成独立、可交付的奖池链。

### 6.1 已验证的结构事实

源：Documents `optional_hd_exchange_shop_data`，entry `02949`。

```text
0x36 mapping row ×2
├─ map 0：1063 pair
├─ map 1：800 pair
└─ 合计：1863 pair

pair = (key, jump → 0x86 detail)
0x86 detail：schema@70，存在多种 bitmap/字段模板
```

- mapping 的 `key` 在两张 `0x36` 表中会重复，绝不能用 `dict[key]` 聚合；记录唯一身份必须至少包含：

```text
mapping_row + pair_index + key + detail_offset
```

- 用户实机锚点（仅作为业务真值，不反推时间字段）：
  - 重构转印器：宸晶臻石×2，月限购1；
  - 帝皇战翼交易盒：宸晶臻石×3，限购3；
  - 霓虹恶魔：稀世之证×450，限购1/1；
  - 幻钻晶梦时装、幻紫晶芒时装、红莲业火典藏、永灿之擎、凝渊之擎：宸晶臻石×3，限购1/1；
  - 幻影狩蝎：宸晶臻石×1，限购1/1。

### 6.2 当前不能声称的事

1. **不能声称“1863 行完整兑换表已定版”。** 原 CSV 的商品、价格、限购列被用户实机指出串列，保留审计但不得交付。
2. **不能把截图“剩余 X 天”填入商品时间列。** 这是页面/活动展示，不是每条配置行的已验证时间语义。
3. **不能按最近 `0x27` 组归属 `0x0b` 引用。** `0x0b` 有的落在组头、组内、其他局部结构或非组范围；没有精确组头或字段级字节证据时必须拒绝。
4. **不能用 root 同编号、正式服字段名、相邻 CHS 文本或单一 slot 推广 Documents 的业务列。**
5. 幻影狩蝎目前存在 `1110013` 与 `1110171` 候选冲突；未有同包允许来源的名称→ID正源绑定前，不得写入正式表。

### 6.3 继续前的正确路线

```text
用户实机锚点
→ 同包 item/gift/fashion/bag 行级名称→ID
→ mapping_row + pair_index + detail_offset
→ 仅精确/字段级验证的 0x27 组
→ 每种 bitmap 模板至少一个独立锚点
→ 商品 / 货币+数量 / 页面限购 三列
→ 时间字段保持空或“未验证”
```

当前相关待办：`exchange-rebuild`。旧 `臻藏商店完整兑换表_2026-08-31.csv` 是失败工作产物，不得覆盖、不得作为交付入口。

---

## 七、其他长期能力与项目状态

### 7.1 时装、武器皮肤与资源桥

- 武器皮肤名字正源：`common_item_data` 的 `item_id == skin_id`；未上线预告可用特效表名称补充，但必须分级。
- `skin_XXXX` 前缀可确认武器类型；`level` 可确认品级，详情见既有 `weapon-skin-table-builder` 工作流。
- 未上线判断优先同名表 key diff，再经历史更新表排除旧内容；“包版本新增”不等于“未上线”。
- GPK 匿名条目、尺寸筛选海报、同包视觉相似等都不是资源归属证据。海报/材质最终物理绑定仍需要路径桥或内容级验证。

### 7.2 已作废的资源结论不得复活

- “尺寸/形状可以定位时装海报”已作废；
- “enc_jpg 伪装 JPEG 是待解格式”已证伪；
- FPK 013/020/021 属 OpenWorld/PVE 场景内容，不应重新拉回人物时装/武器主线；
- 任何错 CHS 池得到的漂亮中文字段，均是高风险串位候选，不能复用。

---

## 八、当前待办（按恢复顺序）

| 优先级 | 待办 | 恢复条件 / 禁止项 |
|---|---|---|
| P0 | `exchange-rebuild`：臻藏商店商品/价格/限购三列重建 | 先审计并修正“近邻 0x27”关联实现；不碰时间、不覆盖旧 CSV |
| P1 | `real-pool`：用已上线帝皇铠甲作为真值，重验活动→真实 pool→reward join | 必须按服务器分支与当前期重建证据链，不能沿用旧 391782/391783 CSV |
| P2 | `rebuild`：铠甲再临奖池交付 | 只有 P1 的 join 通过锚点校准后才允许导表 |
| P3 | 宸世活动池（帝皇战翼转入的具体活动） | 先定位独立活动配置与用户实机锚点；不得把臻藏商店当奖池 |

---

## 九、正式作废与冲突索引

### 9.1 奖池旧导表作废

以下旧产物/说法均不得作为真实奖池证据：

```text
391782 / 391783 的旧“完整25槽位 / 后级6槽位复证版”CSV
基于未验证行尾 [39xxxx, slot] 的 pool→reward 行归属
以连续 slot 或 reward_pool_no_item_no_list 列表证明真实掉落内容
```

原因：辅助表/行尾容器只能支持编号或候选关系，未单独完成业务字段语义与活动调用方校准。

### 9.2 臻藏商店旧导表作废

```text
臻藏商店完整兑换表_2026-08-31.csv
“slot 4 全局等于 cost、slot 3 全局等于 limit”
“94 项宸晶臻石定价”“兑换表已定版”等表述
用页面倒计时为兑换行填写时间字段
```

原因：Documents 0x86 详情存在多模板，重复 mapping key、跳转层级、组归属与语义槽位均不能全局硬套；用户实机已否定旧列结果。

### 9.3 处理规则

- 作废文件只保留审计，不覆盖、不删除、不在新结论中引用；
- 新结果必须另起文件并标注 `证据等级`、源 SHA 与生成日期；
- 一旦新包 SHA 改变，旧 offset 和当前期业务结论自动降级为待复证。

---

## 十、原稿备份与本次重整记录

### 10.1 原稿完整备份（未删除）

```text
备份文件：E:\la拆包项目\04临时存放\日志备份\06（agent写）拆包器进展与交接日志_重整前_2026-08-31.md
原稿字节数：94,547
原稿 SHA-256：0432166b001a40827e7015140ddc4e71801465e04dd6b254fc7e26823f30a082
校验清单：E:\la拆包项目\04临时存放\日志备份\06日志重整前_校验清单_2026-08-31.json
```

### 10.2 本次重整说明

```text
日期：2026-08-31
作者：Hermes
模型：gpt-5.6-terra（openai-codex）
操作：重写主日志的信息架构；保留重整前完整原稿与 SHA 校验清单。
影响：主日志从按时间堆叠改为“可信能力 / 已验证流程 / 待办 / 作废索引”。
未做：未删除原稿、未移动游戏原始包、未覆盖任何 CSV。
```

---

## 十一、核芯图鉴板块落地（2026-08-31）

```text
日期：2026-08-31
作者：Hermes
模型：gpt-5.6-terra（openai-codex）
范围：根包 nucleus_hd_conf_data(48844+CHS 34914)；Documents limit_nucleus_lottery_conf_data(24352)；common_item_data 正源
证据等级：主线/返场=业务链已核验；全表77条=结构已解析
```

**新增结论**

1. 主线限定核芯研制 8 期明细（根包 nucleus_hd_conf_data，conf_id 1-8，CHS sub_title 正源）：
   660074 决斗时刻 → 660076 余烬流火 → 660077 穿心极雷 → 660079 蓄势寒锋 → 660080 磁聚轰雷 → 660078 凝华效应 → 660081 淬焰燃锋 → **660082 深蚀追猎（第 8 期）**，与既有结论吻合。
2. Documents limit_nucleus_lottery_conf_data entry24352 = 71 行返场轮换记录，slot_1 为返场核芯道具 ID（24 个不同核芯）；**660044 电掣双刀返场 14 次最多**，660082 深蚀追猎 1 次。
3. 660xxx 名字正源：Documents common_item_data 23 条；**660082 深蚀追猎在 Documents common_item 无条目**，名字取自根包 CHS sub_title（记待复证，下个热更包复验）。
4. slot_3（1726×5/1742×65/1872×1）、slot_2(1725) 语义未定，只记结构，不编业务语义。

**产物**
- `08Lifeafter wiki\data\boards\nucleus.json`（108 条：主线8+返场24+全表76，带 provenance）
- `08Lifeafter wiki\nucleus.html`（核芯图鉴页）+ wiki.html 分类树导航重排
- 解析探针：`03拆包产物\config_work\decode_nucleus_tables.py`、`gen_nucleus_board.py`
- 回归：ad-hoc 验证通过（builder v0.2 / 数据完整性 / 页面引用），非套件全绿

**不能推出**
- 不能预测下一次返场（24352 只含历史/当前配置，无时间字段语义）
- 全表 76 条的机制描述为既有 CSV 产物（structure 级），未逐条与 common_item desc 复验
- slot_3 1726/1742/1872 不代表商店/货币关系

---

## 十二、08Lifeafter wiki 项目交接（2026-08-31，交给豆包接手）

```text
日期：2026-08-31
作者：Hermes
模型：gpt-5.6-terra（openai-codex）
接手方：豆包（后续由豆包继续扩展；每条新日志须注明自己的作者与模型）
```

### 12.1 项目位置与结构

```text
E:\la拆包项目\08Lifeafter wiki\
├── wiki.html            # Wiki 总入口导航页（分类树：图鉴类/奖池类）
├── index.html           # 武器皮肤库（豆包原版 128 条，未改动）
├── new_textures.html    # 未上线贴图候选 324 张（豆包原版，未改动）
├── nucleus.html         # 核芯图鉴（Hermes 新增：主线研制/返场/全表）
├── data\
│   ├── boards\*.json    # 板块数据（带 provenance，唯一数据源）
│   ├── boards\*.js      # builder 产物（页面用 <script src> 加载，file:// 不能 fetch）
│   └── manifest.js      # builder 产物：板块清单
├── docs\SCHEMA.md       # 数据规范（必读）
├── docs\PIPELINE.md     # 流水线（必读）
└── tools\build_wiki.py  # builder v0.2：JSON 校验 → manifest.js + 板块 js
```

### 12.2 已上线板块

| 板块 | 数据 | 证据 | 页面 |
|---|---|---|---|
| 武器皮肤 | 128 条（豆包原版） | 拆包产物 | index.html |
| 未上线贴图候选 | 324 张（3 已标注） | 候选待复证 | new_textures.html |
| 核芯图鉴 | 108 条：主线 8 期 + 返场 24 + 全表 76 | 32 已核验 + 76 结构 | nucleus.html |

### 12.3 核芯图鉴关键结论（不可推翻，除非新包证据）

- 主线 8 期：660074 决斗时刻 → 660076 余烬流火 → 660077 穿心极雷 → 660079 蓄势寒锋 → 660080 磁聚轰雷 → 660078 凝华效应 → 660081 淬焰燃锋 → **660082 深蚀追猎（第 8 期）**
- 返场 71 行（Documents limit_nucleus_lottery_conf_data entry24352）：电掣双刀×14 最多
- 660082 名字来自根包 CHS（Documents common_item 无此条），下个热更包复验
- 下一期返场**不可预测**（无时间字段语义）

### 12.4 接手必守规则

1. **数据只写 `data/boards/*.json`**，跑 `python tools/build_wiki.py` 生成 js/manifest，禁止手改 js/manifest
2. **每条 item 必须带 evidence**：`structure`（结构已解析）/ `verified`（业务链已核验）/ `candidate`（候选待验证）；`source` 写清来源
3. **时间字段一律不填**（"时间 就别硬套了"）；截图倒计时、候选时间戳、外层活动时间都不许进兑换/活动记录
4. **Documents/根包/正式服严格隔离**：Documents（体验服热更主源）= 当前业务结论；根包 = 格式对照；正式服只对照。跨包字段名串位时宁可不命名
5. **旧 CSV 不得覆盖**：`03拆包产物\config_work\臻藏商店完整兑换表_2026-08-31.csv` 是失败产物，只可审计
6. **新增板块先写本文档**（作者/模型/证据等级/来源/不能推出），再入数据
7. 每次改动 `git commit`（仓库已 init，用户名 Hermes）

### 12.5 下一步待办（按优先级）

| 优先级 | 事项 | 依赖 |
|---|---|---|
| P0 | 武器皮肤 128 条补 provenance 字段（转成 boards JSON 格式） | 无 |
| P1 | 核芯全表 76 条机制描述与 common_item desc 逐条复验（升 verified） | 无 |
| P2 | 人物类图鉴（头饰/套装/背包/挂件/面饰/发饰/投影）数据源解析 | 新表解析 |
| P3 | 武器类型&涂装、载具图鉴 | 新表解析 |
| P4 | 奖池类三块（限时主题/常驻宸世/限时战力保底） | 依赖拆包待办：real-pool、exchange-rebuild 恢复 |
| P5 | 发布：GitHub Pages / 本地静态服务 + 版权边界确认 | P0-P4 |

### 12.6 相关文件索引

```text
解析探针：03拆包产物\config_work\decode_nucleus_tables.py、gen_nucleus_board.py
核芯全表来源：03拆包产物\核芯定位表_v2完整.csv（76 条）
名字正源：03拆包产物\common_item_data_rows.json（Documents 34,949 条）
入口索引：03拆包产物\精拆\annotated_index.json（25,373）、精拆新版\annotated_index.json（105,777）
```

---

## 十三、体验服更新前快照（2026-08-31 18:21–18:31 +08:00）

```text
执行代理：Hermes
模型：gpt-5.6-terra（openai-codex）
源目录（只读）：E:\mrzh
快照目录：E:\la拆包项目\03拆包产物\source_snapshots\pre_update_20260831_182129
```

### 已验证内容

1. `source_lock.json` 冻结 817 个原始容器（.fpk/.gpk/.gres/.idx/.npk/.thh/.thx/.wpk）的 path/size/mtime/SHA-256；SHA=`e945d11566e6dedcba1f447a55b88d83a0272764e270fe7dd22a1d3033c7257d`。
2. 相对 `baseline_20260829`：新增 52、内容变更 9、内容不变 756、纯 mtime 变化 8、删除 0。新增/变更原件合计 39,617,704 bytes。
3. 已做业务优先原件副本 `raw_priority\`：2,300 文件、10,199,858,223 bytes；覆盖 Documents\res 全量、Documents 根下脚本包、根下 NPK/GPK、全部基线新增/内容变化容器（含 `_preload_temp_`）。
4. 独立 verifier 实测：2,300 个源 SHA = 副本 SHA，copy manifest 0 failed；复制后二次检查 817 个容器 size/mtime 漂移 0。
5. `RUN_HASHES.sha256` 已写为 LF-only，实际 `sha256sum -c` 8/8 OK；其自身 SHA=`b030f02eb9fcd46e2b9c84b4c50e9ca9bdff02f783ad264ab5d0a73cd6ec1788`。

### 必须保留的边界

- **不是全目录物理镜像**：`E:\mrzh` 当时 286,742,485,938 bytes / 10,973 文件，而 E: 可用仅 84,168,032,256 bytes。根 `res\`（约 197.94GB）的既有静态资源未复制原件，只以完整容器 SHA 状态冻结。
- 因此可可靠用于：更新后内容差分、当前 Documents 配置/热更资源恢复、已变包证据复验；不可声称能独立恢复整个 286GB 客户端。
- 后续更新完成后必须另建 `post_update_*` 快照，与本次 `source_lock.json` 用 `compare_snapshots` 比较；不得仅依 mtime 认定新内容。

### 接手入口

```text
README.md              # 人读交接和范围边界
verify_snapshot.py     # 只读源/副本 SHA 复验，exit 0 才可复用
priority_source_lock.json / raw_priority_manifest.json
package_delta.json / CURRENT_STATE.json
```

---

## 十四、体验服更新后武器皮肤优先比较（2026-08-31）

```text
执行代理：Hermes
模型：gpt-5.6-terra（openai-codex）
更新前 Documents script SHA：56def41376ed2e71f1901756cde1984a53e6a6b863767e982ffd1eac601bb224
更新后 Documents script SHA：780363b86008999cf7ee5728e38033f4c7cfd8439977d098870d1aa7ffe3ba4d
主报告：E:\la拆包项目\03拆包产物\source_snapshots\post_update_recheck_20260831_184820\武器皮肤更新对比_2026-08-31.md
```

### 已验证结论（只限 Documents 主分支）

1. 更新后脚本包以其冻结副本完成 verified extraction：25,365 条，decode_error=0，invalid_bounds=0；更新前为 25,373 条。新版 entry 序号整体偏移，后续必须用 `file_id` 对齐，禁止沿用旧 entry 号。
2. 已知 `weapon_skin*` 主数据表共 12 张（主表、特效、行为资源、战斗表现、挂件、冷兵器动画、核芯联动、查询音效及分支 kind/pendant 表）按 `file_id → payload SHA` 核验：**12/12 完全一致**。
3. 名称/特效/行为/表现/核芯联动所涉 5 组 base+CHS 也全部相同：`weapon_skin_data`、`sfx_function`、`behavior_res`、`effect_show`、`replace_nucleus_conf`。
4. 全部脚本包变化条目为 349（同 ID payload 变 331、仅旧 13、仅新 5）；但其中 `skin_XXXX_NNN` 字面路径集合 8→8，新增=0、删除=0、条目内集合变化=0。
5. 因此本次 **没有 Documents 主分支新增/删除/改写武器皮肤配置的证据**；禁止新增 Wiki 皮肤记录、禁止改 `weapon_skin_full.csv`、禁止以 UI/着色器/oversea 壳的 `weapon_skin` 词命中宣称新皮肤。

### 资源层最终审计与边界

1. 资源在首次复制时曾漂移；最终以 `post_update_resource_recheck_20260831_190236` → `post_update_resource_stablecheck_20260831_190612` 两份完整锁复核，817/817 内容一致、0 mtime-only，随后相对 pre 的 10 个变化原件（1,453,421,234 B）全部复制且 SHA 复核通过。
2. 实体 hash delta：`character.idx` 0 新增/0 删除；`effect.idx` 3 新增；`ui.idx` 52 新增；共同 hash 的 descriptor 变动均为 0。
3. 55 条新增 hash 均从最终冻结分卷实际解出为 DDS，`1DPW → 解密/解压 → 最终 DDS MD5 = IDX hash` 的链 55/55 通过，0 decode error、0 hash mismatch。
4. 人工审计联系表显示新增 UI 为调色板/画笔、挂件小饰品、头像发型、框体、晶体/闪光/选择器等；effect 为笔触、环形刻度、雷电纹理。它们全是 `candidate`，**0 条**可回连主分支 `skin_id`，不得写成新武器皮肤/特效/上线内容，亦不得导入 Wiki。
5. 仅 mtime/WPK 变化永远不算新皮肤；下一次必须仍由 `主分支表字段 or 已验证路径桥 → skin_id → 资源实体` 完成闭环。

### 证据产物

```text
config_work\script_py314_docs_780363b86008\manifest.json
config_work\script_py314_docs_780363b86008\weapon_skin_target_fileid_map.json
config_work\script_py314_docs_780363b86008\weapon_skin_table_payload_audit.json
config_work\script_py314_docs_780363b86008\weapon_skin_literal_path_delta.json
```

---

## 十五、下一次追加模板

```markdown
### YYYY-MM-DD 主题

- 日期：YYYY-MM-DD
- 作者：Hermes
- 模型：gpt-5.6-terra（openai-codex）
- 范围：服务器分支；源包 SHA；表/entry/逻辑路径
- 证据等级：已验证 / 待复证 / 作废

**原始事实**
- entry / row / offset / 字节范围：
- 同包 base+CHS：
- 用户实机锚点（如有）：

**可得结论**
- 

**不能推出**
- 

**产物与回归**
- 文件：
- 校验：

**下一步 / 停止条件**
- 
```

---

## 十四B、材质→纹理链攻坚（2026-08-31，豆包补登；原编号与第479行「十四」重号）

```text
日期：2026-08-31
作者：豆包（Doubao）
模型：豆包
范围：体验服 E:\mrzh\res；weapon.gpk / textures.gpk / 003.fpk；递归全索引 216 包
证据等级：容器/解码/判据方法=已验证；324 张“独有”清单=候选待复证（分级见下）
来源：同包原始字节、entry、全索引 c1c2 桥接实测；重整时本节曾被精简，原稿见
      04临时存放\日志备份\06（agent写）...重整前_2026-08-31.md
```

### 14.1 原始事实（均已验证，可复跑）

1. **材质是 .mtg，不是 cgmat（修正旧稿）**：与主 gim 同名的 `.mtg` 为 c159 序列化材质。
   样例 `weapon\skin\skin_1001_001\skin_1001_001.mtg = 003.fpk#7517(1033B)`，解出
   shader=`shader\pbr_weapon.fx::TShader`，并引用 `<dir>\textures\` 下 4 张 PBR 贴图：
   **a=albedo 主色 / n=normal 法线 / m=metallic 金属度 / s_m=smoothness 光滑度**，
   命名 `<stem><3位编号><通道>.tga`。→ 配置→gim→mesh→mtg→四通道逻辑路径 100% 闭合。
2. **textures.gpk = KPGF 分卷**：564 条目，每条=36B 明文头（[16]clen/[20]olen/[24]c1/[28]c2/[32]flag）
   + off+36 起的**多帧 zstd**，须 `ZstdDecompressor.stream_reader(read_across_frames=True)` 跨帧读全。
   解出 493 张 BC7_UNORM（DXGI 98），条目0=泥土 tiling → 证明它是**通用材质库、非皮肤专属**；皮肤贴图在 weapon.gpk。
3. **BCn 解码管线（已验证）**：texture2ddecoder；DX10 数据从偏移 148 起、dxgiFormat@128（BC7=98/BC5=83），
   普通 DXT 从 128 起；BC7/BC3 每 4×4 块 16B、BC1 8B；`frombytes("RGBA",(w,h),raw,"raw","BGRA")` 颜色正确。
4. **递归全索引（已验证）**：`build_index(recursive=True)` 扫 res 下全部 fpk/npk（含 character/ui/model/
   building/scene/scene_bw 子目录分类 npk）= **216 包、3,007,422 条、唯一 c1c2 2,632,212、约 7.3s、0 失败**。
5. **匿名纹理墙 6 路证伪（已验证，勿重试）**：皮肤 .tga 逻辑路径在递归全索引 0 命中，源 tga 转 BCn 后进匿名
   weapon.gpk 无 fid。逐路证伪：扩展名/目录变体、gpk 内 fid 字节、wpk idx 16B（实为内容 MD5）、
   local_finfo*（磁盘 pickle 清单）、textures.gpk 头字段、扩展到 216 包——全部 0。缺的是「fid→路径全局名表」。

### 14.2 版本独有判据（方法已验证；结果为候选）

- **方法（已验证）**：匿名 gpk 条目用 c1/c2 桥全量索引，桥不到 fid 的记为“本索引未覆盖条目”。
  weapon.gpk 实测：dds 4948→**324**（6.5%）、mesh 11037→254（2.3%）、c159 35275→658（1.9%）。
- **证据边界（对齐本日志三档）**：“桥不到”只证明它不在当前 216 包带名索引内，是**高浓缩候选**，
  **不等于已确认“未上线”**——仍可能是正式服/按需包/已删资源。324 张中仅 3 张经人工看图标注，其余 321 张为候选待复证。
- 已人工看图标注（候选，名称为形态推断、非配置正源）：
  `#4009` 黑金华丽长剑（铠甲联动剑形态，且桥不到索引）、`#49505` 金黑蓝能重武器、`#00731` 太极圆盘机械；
  另 `#00179/#03163/#19771/#20110` 为金色步枪但**桥得到索引**（非独有，属已有内容副本）。
- 要把某张匿名 DDS **精确绑定**为“某皮肤的 a/n/m 通道”，仍需全局 fid→路径名表（exe 逆向或外部名表，硬骨头另线在攻）。

### 14.3 颜色特征筛选器（工具已验证；命中为候选）

- `toolkit_core/texture_extractor.py`：BCn 主 mip 解码 → RGB/HSV 规则打分（默认 gold 金色，可扩银/紫/红）
  → 多进程（`smart_workers`=逻辑核×0.8、留 2 核、getloadavg 高负载自动减半；32 核机=25 进程，4919 张约 7s）
  → 候选 PNG + 分页联系表。py_compile 通过，端到端自测复现 4948→324。
- 命中图只是“颜色形态候选”，需人工/多模态按形态确认，不得直接当某 IP 成品。

### 14.4 产物与回归

- 引擎：`10_应用核心\toolkit_core\resource_resolver.py` 新增/升级 parse_mtg、iter_kpgf_entries、
  decode_bcn_dds、find_unique_in_gpk、递归 build_index；新增 `texture_extractor.py`。均 py_compile + import + 端到端自测通过。
- 文档：`02文档索引\01_资源盘点与差分\08_资源体系与物理桥定位wiki.md` 已同步（材质链/KPGF/独有判据/6 路证伪/后缀表）。
- Web：候选页 `new_textures.html`+`new_textures_data.js`（324 张，搜索/尺寸/只看已识别/灯箱浏览器实测正常）；
  Hermes 已将其复制进正式项目 `08Lifeafter wiki`（与本页一致），后续改动走该项目 boards/builder 规范。

### 14.5 不能推出

- 不能把“桥不到索引”直接发布为“未上线”；324 张仅候选，需配置正源或外部名表复核。
- 不能凭金色占比/UV 形态断言具体皮肤名或 IP（#4009 的“极光剑/战神烈火剑”仅形态推测）。
- textures.gpk 是通用 tiling 库，不得当皮肤贴图来源。

### 14.6 下一步 / 停止条件

- 按 08Lifeafter wiki 规范，把 324 候选以 evidence=`candidate` 入 boards，3 张已标注的也不升 verified（缺配置正源）。
- 扩展颜色规则覆盖非金色联动；用同一独有判据扫 character_* 找新时装候选（同样标 candidate）。
- 停止条件：在拿到 fid→路径全局名表前，不输出“某匿名 DDS=某确定皮肤通道”的硬绑定结论。

---

## 十五B、Wiki 数据层补全（2026-08-31，豆包；原编号与第516行「十五」重号）

```text
日期：2026-08-31  作者：豆包  范围：08Lifeafter wiki；证据等级：结构=structure，候选=candidate
```

- 新增导出器（可复跑，带 provenance，符合 SCHEMA/PIPELINE）：
  - `tools/export_weapon_skins.py`：skin_library.json → `data/boards/weapon_skins.json`，**128 条 = 97 structure（物理定位可复跑）+ 31 candidate（未在带名 fpk 命中）**；皮肤名来自配置表、未逐条 common_item 正源复验，故不出现 verified。
  - `tools/export_new_textures.py`：new_textures_data.js → `data/boards/new_textures.json`，**324 条全部 candidate**（3 张带 shape_hint 形态推测，明确非命名正源）。
- 新增**通用板块渲染页 `board.html?b=<board>`**：读 `data/boards/<b>.js`，证据三色/搜索/证据筛选/字段自适应；后续人物、载具、奖池板块导出 JSON 后免写页面。
- `build_wiki.py` 通过：**3 板块共 560 条**（核芯 108 / 武器皮肤 128 / 贴图候选 324）；wiki.html 武器类补“贴图候选”入口，板块状态表每行可点击（有专用页优先，否则走 board.html）。
- 原 `weapon_skins.sample.json` 骨架被 128 条正式版替代，已移出 boards、归档 `04临时存放\wiki归档`。
- git：本仓库提交 `b1ffd35`（local 身份 Hermes）。
- **仍缺（按 txt 规划，需新表解析，暂留“建设中”不造假）**：人物类 7 子类、武器类型&涂装、载具；奖池三块依赖 real-pool / exchange-rebuild 恢复。

---

## 十六、奖池入 Wiki + 人物类数据源校准（2026-08-31，豆包）

```text
日期：2026-08-31  作者：豆包  范围：08Lifeafter wiki 奖池板块；Documents py314 common_item 数据源校准
```

### 16.1 奖池类补两板块（已提交 wiki git）

- `tools/export_lottery.py` 把既有 CSV 转两个 board，`build_wiki.py` 后 **5 板块共 697 条**：
  - `lottery_dihuang`：帝皇铠甲奖池 **54 条 verified**（已上线、分经典/生存服珍匣、档位/概率/发放物 ID 齐）。
  - `lottery_kaijiazailin`：【2026-09-01 二期已实装，旧 83 条未上线版作废】现 39 条 = panel/左右大奖 7 verified + reward 逐格 30 structure + 2 candidate，详见顶部 B 表；方法=super_fashion key232 的 panel_show_item_ids 配置锚点。
- 概率一律保留**配置原始值**，notes 声明未做按池归一化、跨池概率不可相加；`config_exp` 是配置内 expiration 原值（非截图倒计时）。
- **臻藏商店旧兑换表（已被用户实机否定）不导入**；转盘/满减/芯片保底无数据保持“建设中”。

### 16.2 common_item 最新名表校准（关键基础，可复用）

- 旧成品 `common_item_data_rows.json`(34949) 与 `..._root_py314_rows.json`(35544) 都是**旧根包**，新 ID（139292 刑天、1110183 战神烈火剑）全 MISS，弃用为旧源。
- **路径双 Murmur(seed 7777…/6666…) 对 cdata 表仍 0 命中**（已知搁置的文件名还原难题，不在此硬攻）。改用新通道「**chs 内容反查 base**」：用配对 chs 池(=entry **2121**，55085 字符串)试解每个大 entry，谁解出多个目标中文名谁是 base → 定位 **common_item base = entry 17922，35948 行**。脚本 `config_work/find_base_by_chs.py`（可复用于任意 base/chs 配对定位）。
- 导出成品 `config_work/common_item_data_py314_latest_rows.json`（35948 行全有 name，源 SHA 56def413，脚本 `export_latest_common_item.py`）。验证：极光剑=item167265、帝皇裁决=item220050，name 正确。

### 16.3 字段对齐质量结论（人物类路线依据）

- 逐行对比正确行/异常行：**`name` 字段基本可靠**（7209 典藏时装赤焰风华头像、9501 萌兔神探头饰箱、167265、220050 的 name 全对）；真正串位的是 **desc / source / from_map / icon 这几个 CHS 字符串字段互相错位**（如 7209 的 desc 串成新年鼓点、icon 串成贴屋顶说明）。
- 即：**做图鉴可信任 name；desc 长文在修好 CHS 槽位对齐前不可直接展示**。早期“32% 错位”是按名字长度过严统计，实际 name 可用率高得多。
- **刑天铠甲(139292)/飞影铠甲(139293)/帝皇铠甲 不在 common_item**——它们是穿戴外观（时装），名字在时装/外观表自有 chs，不靠道具表；super_fashion 表(220 行)是**抽奖面板混搭表**（核芯/家具/材料/皮肤混在一起，shop_display 仅 8/220），**不是套装正源**。

### 16.4 人物类下一步（路线 + 卡点）

1. 用最新名表 name 按 ID 段 + 关键词聚合人物类**道具层**（头饰/面饰/时装自选箱/套装礼盒），可先出 structure 版人物板块。
2. **穿戴外观正源表（fashion/appear/cloth 类）仍需定位**：同样走「chs 内容反查 base」，目标词换成时装部件名。
3. **硬卡点（可交接）**：`decode_table_rows` 对部分 schema 的多个 CHS 字段（desc/source/from_map/icon）存在槽位串位，name 不受影响；需对比同 schema 行的 bitmap 启用位与值流，修 CHS 槽位对齐，desc 才能可信。

### 16.5 时装/穿戴外观正源表定位（entry 级已锁定，字段池待配对）

- 用「CHS 关键词密度扫描」(`find_fashion_chs.py`) 在 25373 个 entry 里定位穿戴相关 CHS 池：
  - **entry 20739 = 时装部件中文池**（19480 条，含「塞壬之歌典藏-头饰/电音小子-头饰」等头饰 2822、衣服 3326）；近似副本 9608/10409/24953/15022。
  - **entry 10765/9122 = 面饰专池**（面饰 74，「樱花主题限定面饰」等）。
- 用「CHS 内容反查 base」(`find_fashion_base.py`) 以 20739 为池反查，**时装外观 base = entry 22470：19264 行、unbound=0、与中文池近 1:1**；字段含 name/part/part_type/model_id/icons/appear_ids/fashion_preview/cloth/brand_id，是穿戴外观正源。21284(23281 行,0 unbound) 是相关副表。
- **字段名池假设已被证伪并修正（重要，勿走回头路）**：最初以为 22470 缺独立字段名池；用 `find_fashion_fieldpool.py` 扫描证实 **20739 本身就含全部特异英文 key（model_id/appear_ids/part_type/fashion_preview/v2_socket_names），它就是 22470 正配池**。
- **真正卡点（可交接，硬骨头）= 宽 schema 解码器字段对齐 bug**：用正配池 20739 解 22470，行边界 0 unbound、字段名也解得出，但**值与字段名系统性错位**——name 解成数字 90091338、charm_value 解成「刑天召唤器-7天」、并把数据值 `b_f_3605_1/b_m_3613_2` 误当字段名。根因在 `toolkit_core/bindict_table.py::decode_table_rows`：对这种 **50+ 字段、含大量 0x0b jump 与嵌套 0x27 组的宽 schema**，schema 字段数 n / bits / bitmap 启用位或值流推进有偏移，把值流误当 schema slot 取名。common_item(17922) 字段少、name 靠前所以 name 大多正确，宽表错位被放大。**下一步：拿 22470 单行做字节级 walkthrough，对照 schema 定义逐字段核对 bitmap 位与值类型，修宽 schema 对齐（改前必须回归核芯/武器/common_item 已验证表，防止破坏）**；修好后按 part_type 拆 7 子类出人物板块。**首要怀疑点：`bindict_table.py` 第 337 行 `enabled = [... if i >= bits or bitmap位]`——当 schema 字段数 n > bits 时把超出 bitmap 的字段无条件当启用，宽表（50+ 字段）会因此多读值、整条值流后移错位；先验证 22470 各 schema 的 n 与 bits 关系。**
- 附带：22470 行内已能看到「不湮之花幻典-头饰」「刑天召唤器-7天」等中文值，证明新联动内容确实在该表，解码器对齐修好后即可完整提取刑天/飞影时装部件。
- 可复用脚本（均在 `03拆包产物/config_work/`，只读）：find_base_by_chs.py（通用 chs→base 配对）、find_fashion_chs.py（关键词密度找 chs 池）、find_fashion_base.py、find_fashion_fieldpool.py（证伪/确认字段名池）、export_latest_common_item.py。

## 十七、A 路线攻坚：宽 schema「解码器 bug」假设再被证伪 → 内容驱动绕过，人物首板块落地（2026-08-31）

对 22470 单行做字节级 walkthrough（`walk_fashion_row.py / walk_fashion_full.py / walk_chs_slot.py`），**逐条推翻 16.5 的「解码器字段对齐 bug」假设，勿再改核心解码器**：
1. schema 解析完全正常：单行 n=131 字段、bits=111，type 字节全在已知集合、字段名全是合法标识符，值流走完全程 **0 异常 0 越界**。
2. `i>=bits 即启用`是 `bindict_rows.py` 注释里参考实现确认的**设计**，不是 bug。
3. **CHS(0x05) 槽位 100% 精确、无串位**：逐字段比对「读到的 slot」与「目标串在池中的真实 slot」全部相等（part=5977、charm_value=13010…）。之前看到的「charm_value=刑天召唤器-7天」不是解错，是该字段名语义边缘 + 多 schema 字段名错位叠加的表象。
4. **真正根因 = 22470 含 8 个不同 schema_ref**（270688/274543/536016/23250…），单一字段名池 20739 只对部分 schema 的 slot→字段名排布正确，主 schema 270688 有 95% 行字段名错位；值本身没错，是「值挂错字段名」。硬修需要给每个 schema 配字段名池，成本高。

**采用的务实方案 = 内容驱动提取（绕开字段名）**：既然 CHS 值解码精确，就不依赖字段名——遍历每行所有 CHS 串，用正则识别部件名（`XX-头饰/衣服/…`）、短中文外观名、`-N天` 期限档，从 uleb 大数认 model_id。脚本 `03拆包产物/config_work/extract_fashion_content.py`、wiki 导出器 `08Lifeafter wiki/tools/export_fashion_kaijia.py`（可复跑）。

**产出：人物类首个板块 `fashion_kaijia`（铠甲勇士联动外观 26 条，structure）**，已 build + git 提交，wiki 达 **6 板块 723 条**：
- 刑天铠甲（永久本体 model 32710/90032710 + 1/14 天档）、帝皇铠甲（1/5/7/14/30 天档）；
- 刑天召唤器（永久 + 1/3/5/7/14/30 天全档）、飞影召唤器（2 个永久）；
- 帝皇战翼（背饰/滑翔翼，1/3/5/7/14/30 天档）、铠甲飞兔（头饰/挂件）；
- model_id 规律自洽：900 前缀=高模变体（31070↔90031070）。
- **明确遗留**：本表**无独立「飞影铠甲」本体名**（飞影仅召唤器+「疾如风…破风」主题描述），飞影铠甲本体需查面饰池 10765/其他表或确认本期是否实装；通用全量时装部件（内容驱动已得 衣服 2015 / 头饰 384 行、去重外观名 1114）尚未出 board，是人物类下一步。
- 三段联动外观描述主题：刑天「后人发先人至百战百胜」、帝皇「五行化龙天赐之铠」、飞影「疾如风徐如林掠如火难知如阴破风」、战翼「光盾展翼化作风羽」。

### 17.1 暂停状态与对接要点（2026-08-31，用户指示 wiki 先停）

**wiki 当前版本（commit 5b31db9，6 板块 723 条）有一个已知缺陷，接手先修：**
- `fashion_kaijia` 26 条里 **name / base / kind / duration_days / model_id 可靠**（内容驱动、CHS 槽位 100% 精确，期限档与 model 规律自洽）；
- **但每条 item 的 `desc` 字段全部错配**——挂的是「天枢龙将主题限定背包 / 星宿万象 / 潜龙在渊 / 云间龙吟」等无关老时装描述。根因：22470 有 8 个 schema_ref、字段名错位，导出器里「取行内第一个含标点的 CHS 当 desc」在错位行里抓到的是别的字段串，**不可逐行硬绑**。用户已当场指出。
- **正确修法（二选一，推荐①）**：
  ① 直接删掉每个 item 的 desc/desc_theme，改为在 `meta` 里用一个 `liaison_descs` 数组统一列 6 段**自带「明日之后×铠甲勇士」联动限定外观标记、可 100% 确认归属**的全局描述（这些在独立行、不绑定到具体期限款）：刑天「后人发、先人至，于末世百战百胜」、帝皇「五行化龙，天赐之铠，照亮末世黎明」、飞影「疾如风，徐如林，掠如火，难知如阴，破风于末世」、战翼「光盾展翼化作风羽，于末世乘风滑翔突围求生」、伙伴「铠甲身后的守望，本身就是力量」、日常装「不穿铠甲的日子，勇士依然/依旧是勇士」。
  ② 攻克「每个 schema_ref 配独立字段名池」，实现 desc 字段精确绑定（成本高，属宽 schema 字段名还原，非解码器问题——解码器本身已用 walkthrough 证明无 bug，勿再改 bindict_table 核心）。
- 导出器 `08Lifeafter wiki/tools/export_fashion_kaijia.py` 已回退到 commit 版（无半成品），改完重跑 `python tools/build_wiki.py` 再提交。

**人物类下一步（wiki 恢复后的队列，按优先级）：**
1. 修 fashion_kaijia 的 desc（如上，5 分钟）。
2. 通用全量时装部件出 board：内容驱动已得 **衣服 2015 行 / 头饰 384 行 / 去重外观名 1114**（`03拆包产物/config_work/extract_fashion_content.py` 产物 `fashion_部件_内容驱动.json`），按部件后缀分类、聚合同款多 ID（男女/高低模/期限），证据标 structure。
3. 面饰专池 entry **10765/9122** 单独出面饰板块；并在此池/21284 副表核查**独立「飞影铠甲」本体是否存在**（22470 内只有飞影召唤器、无飞影铠甲本体名，未排除在其他表）。
4. 若要彻底解决多 schema 字段名错位：按 schema_ref(270688/274543/536016/23250/22758/16129/34951/15257) 分组，分别反查各自正配字段名池（方法见 16.4 find_base_by_chs 的 CHS 反查），不要再怀疑值解码器。

**可复用资产位置**：内容驱动/字节级验证脚本全在 `03拆包产物/config_work/`（walk_* 是证伪过程、extract_fashion_* 是可用提取、grep_kaijia 是关键词全表扫）；最新道具名表 `common_item` entry17922（35948 行）导出成品同目录。

---

## 十八、Documents 奖池真值校准恢复点（2026-08-31，Hermes）

```text
范围：当前 Documents workcopy（script_py314_docs_780363b86008）
原始源：E:\mrzh\Documents\script.py314.lc.npk（只读）
源 SHA-256：780363b86008999cf7ee5728e38033f4c7cfd8439977d098870d1aa7ffe3ba4d
边界：不读取、不引用 root / KJ1 / yk / KJXQ 的业务配置；不重写失败的臻藏 CSV。
```

### 18.1 已通过的真值锚点：帝皇铠甲 `lottery_id=391762`

新增可复跑验证器：

```text
03拆包产物\config_work\script_py314_docs_780363b86008\verify_emperor_reward_pool_calibration.py
```

产物（已回读）：

```text
...\帝皇铠甲奖池_真值校准_2026-08-31.json
```

实跑结果：**6/6 PASS，exit 0**。验证器每次先重算原始 NPK SHA，再按稳定 `file_id` 定位表；**不依赖会随热更漂移的 entry 编号**。

闭环证据：

```text
super_fashion_lottery_conf_data
  key=230, lottery_id=391762
  left_item_desc=皮肤-极光剑
  right_item_desc=时装-帝皇铠甲
        ↓
reward_pool_data（12,345-slot main CHS pool）
  (391762, slot=11) → reward jump → 139265 ×1，note=帝皇裁决交易盒
  (391762, slot=12) → reward jump → 139266 ×1，note=帝皇瑞昭交易盒
  (391762, slot=10) → reward jump → 131216 ×1，note=银翼号背包礼盒
        ↓
gift_data（同一 Documents 快照）
  139265=帝皇裁决交易盒，说明：打开获武器皮肤「帝皇裁决」×1
  139266=帝皇瑞昭交易盒，说明：打开获宠物帽/宠物服「帝皇瑞昭」
  131216=银翼号背包礼盒
```

稳定 file_id（更新后 entry 仅作当前定位参考）：

```text
reward base D558884A36C972C5 → 021277
reward CHS  6731BD068F33B9BE → 010164（12345 slots）
super base  7E5A5A83B1F07D31 → 012526
super CHS   512C733C3B263D37 → 007907
gift base   C5998AD60B305608 → 019671
gift CHS    938D86FE498D1B1A → 014669
```

### 18.2 结论与后续边界

1. 对 **本次帝皇 391762 真值锚点**，`pool → reward jump → gift item` 的 join 已达到 `verified`：源锁、活动配置、奖励叶子、独立 item 定义、`note == item.name` 五层同时成立。
2. `reward_pool_data_chs.py` 的旧 12,295-slot KJ1 池不能再作为 Documents main 的配池；同一文本出现并不代表可跨服配对。
3. 历史 `common_item` 导出只适用于其已校准字段；本轮礼盒奖励的正源改用 `gift_data`，不再从无关 inline group 外推物品名。
4. **待办恢复顺序**：先用本验证器确立的 join 重建“铠甲再临”交付；只有每条能回到同服配置和 item/gift 定义时才标 `verified`。无法闭环的行保留 `structure/candidate`。随后才恢复臻藏商店；失败 CSV `臻藏商店完整兑换表_2026-08-31.csv` 继续封存，禁止覆盖。

---

## 十九、臻藏商店兑换表重建阻塞审计（2026-08-31，Hermes）

### 19.1 已完成的结构与锚点复核

```text
输入范围：当前 Documents main workcopy（entry 002949）
源 NPK SHA-256：780363b86008999cf7ee5728e38033f4c7cfd8439977d098870d1aa7ffe3ba4d
entry2949 SHA-256：f2573710d7def28335fe96351bd48668cd1c729ea94ff2a8847315252d032880
x{ frame：file 0x107；body 80,809 bytes
```

新建可复跑阻塞审计器：

```text
03拆包产物\config_work\script_py314_docs_780363b86008\audit_optional_hd_exchange_rebuild_blocker.py
```

实跑 exit 0，审计产物：

```text
...\臻藏商店_重建阻塞审计_2026-08-31.json
SHA-256：272acc4e8ec8c9cc124ed317caaf7cd22e3ead7d40bfdf5921a067d67cc5b67a
```

结构事实：`0x36 mapping → bounded 0x86 detail → framed 0x27 group` 已安全解出，包含 **1,863** 条完整记录、**1,368** 个唯一 detail；数值 key 跨两个 mapping 重复 **796** 个，detail alias **495** 个。因此完整身份只能是：

```text
mapping_row + pair_index + key + detail_start
```

用户实机锚点只验证“同一 detail 共现”，未能选择唯一 detail：

```text
139267 帝皇战翼交易盒：同 detail 含 [139267,1] 与 [153036,3] 的唯一 detail 有 17 个
156182 重构转印器：同 detail 含 [156182,1] 与 [153036,2] 的唯一 detail 有 65 个
```

### 19.2 不能跨越的结论边界

1. `[153036,n]` 的模式与两个用户锚点中的宸晶臻石数量一致，但**当前静态证据无法将它提升为全表已验证的“价格字段”**：商品 alias 不唯一，且未找到 runtime 当前店铺选择器。
2. “月限购/总限购”字段更不能凭 `[3,1]`、`[2]` 或某个 scalar 反推。两条锚点的已知限购无法唯一落到同一个 schema 位置；没有 consumer/call-site 字段名，任何标签都是编造。
3. `optional_hd_exchange_shop_goto_data` 只有跳转结构；当前 Documents 的静态审计未找到可验证的 local current-shop selector。KJ1/yk/oversea quick-buy 数据受服务器边界限制，禁止拿来补洞。
4. 因此本轮结果是 `BLOCKED_NO_TRUTHFUL_EXCHANGE_CSV`：**不生成、不覆盖、不发布**臻藏兑换 CSV。旧失败 CSV 已核验仍封存，SHA-256：
   `1c0875ebc72141592c74b1f5407bb86293badd1d18c1103ca2b317fbe1b6a3d6`。

### 19.3 恢复条件

恢复兑换表前必须至少补齐一条：

- 实机完整店铺截图/录屏（覆盖所有商品、价格、限购），用多条锚点同时锁定 runtime detail 集；或
- 客户端/服务器捕获到的当前店铺 payload（需脱敏）；或
- 消费端 call-site，能明确给 entry2949 字段赋予“商品/价格/限购类型/限购数”语义。

在此之前，交付只能是上述结构审计，不能伪装成“当前臻藏商店兑换表”。

---

## 二十、臻藏商店实机核验兑换表（2026-09-01，Hermes）

### 20.1 范围与源锁

本章只处理用户实机提供的 **臻藏商店**；货币固定为 **宸世臻石**。稀世商店/稀世之证、KJ1、yk、oversea 均未进入此表。

```text
Documents 源：E:\mrzh\Documents\script.py314.lc.npk（只读）
源 SHA-256：780363b86008999cf7ee5728e38033f4c7cfd8439977d098870d1aa7ffe3ba4d
实机图：4 张；每张 SHA-256 均由构建器重验
```

用户完成名称校正后的 20 个去重可见条目已按截图逐行登记，包含：商品名、限购原文、宸世臻石价格、特惠、截图可见倒计时/已拥有状态、截图文件名和 SHA。

### 20.2 新交付（可复跑）

```text
构建器：
03拆包产物\config_work\script_py314_docs_780363b86008\build_zhenzang_shop_ui_verified_20260901.py

CSV：
...\臻藏商店_实机核验兑换表_2026-09-01.csv
SHA-256：7a663c96abac71e128da27d2dbdcb785c9ef59a2e3ab614bc96b9b433081c393

JSON：
...\臻藏商店_实机核验兑换表_2026-09-01.json
SHA-256：3f5fe79869f87e18e0d8d7bd6558885336b2ebd0fdab1fdb765aebcd42e405b8
```

实跑结果：`UI_VERIFIED__DOCUMENTS_SELECTOR_UNRESOLVED`，**20 条**，exit 0。

已核验的截图事实：

```text
特惠：风火轮（46 宸世臻石）、浑天穹焰（35 宸世臻石）
已拥有：光影咏叹调（限购 0/1，1 宸世臻石）
名称用户校正：银蛇迅影芯片、风火轮、幻影狩蝎、浑天穹焰、赤砂炙火
```

### 20.3 证据等级与剩余边界

1. CSV/JSON 每行的商品名、限购原文、价格和截图可见状态为 `verified`，正源是用户实机图；这已经是可以使用的**当前臻藏商店兑换表**。
2. 每行保留 `documents_entry=002949`，但该列只表明同一 Documents 主分支的结构审计上下文，**不表示已绑定到具体 mapping key/detail/字段号**。
3. `entry2949` 的 `0x36 → 0x86 → 0x27` 结构仍为 `structure`。当前静态包未证明 active selector：匿名 CHS entry `015221` 虽有 `optional_hd_exchange_keys` 字符串，但以已验证 `.nxs` 路径算法计算的 `quick_buy_data.nxs` file_id `341E28EC5A1E76CD` 不在当前 Documents manifest，故不得把该池或任何数值 key 强认作当前商店选择器。
4. `精拆` 总索引的 entry 数字会与当前 workcopy 因提取源差异产生偏移；后续一律先按 `file_id → 当前 manifest.output_file` 定位，禁止把旧 index 直接套到 workcopy。
5. 历史失败文件继续封存，且本轮重验 SHA 未变：
   `臻藏商店完整兑换表_2026-08-31.csv` = `1c0875ebc72141592c74b1f5407bb86293badd1d18c1103ca2b317fbe1b6a3d6`。

---

## 二十一、稀世商店实机核验兑换表（2026-09-01，Hermes）

### 21.1 范围锁

用户提供两张独立实机图，明确属于 **稀世商店**，货币固定为 **稀世之证**。本表与第二十章臻藏商店/宸世臻石硬隔离：不复用 `entry2949`，不反向套用臻藏候选 key/detail/字段。

```text
图1：2d188b785e47337aaa900bdd4c00364c.png
SHA-256：a572afd0c356801fc4fb4c3483e8b62813da73248766360e1afda1d4f7d511d3

图2：27f521fc274beeb328f4db518e11e305.png
SHA-256：4b57d57e96586abba23480aa47d5b6f16fe4b0b670dc6fcba6247783c86780bf
```

### 21.2 新交付（可复跑）

```text
构建器：
03拆包产物\config_work\script_py314_docs_780363b86008\build_xishi_shop_ui_verified_20260901.py

CSV：
...\稀世商店_实机核验兑换表_2026-09-01.csv
SHA-256：ffb42bc0db9d585c266f4f67c27e1853468d2519b3dfaaf0858fade192d5cdc3

JSON：
...\稀世商店_实机核验兑换表_2026-09-01.json
SHA-256：c78748453434b9799a2502de045b12b455d1f11f57078e477e9160c4bf6c24a2
```

实跑：`UI_VERIFIED__STATIC_MAPPING_NOT_ASSESSED`，**10 条**，exit 0。

用户校正并已写入的名称：

```text
1型记忆材料（首字符为阿拉伯数字 1）
飞行载具改装模块
异变核芯·贯通战术
异变核芯·余烬流火
```

### 21.3 证据边界

1. 10 行商品名、数量、限购原文、稀世之证价格、特惠/划线原价、截图可见倒计时均为用户实机图 `verified`。
2. 本轮没有审计稀世商店的静态 selector/detail，状态是 `not_assessed__no_cross_shop_join`；这不是字段缺失，更不是允许把臻藏商店结构硬套过来。
3. 回读验收：表内商店集合仅 `{稀世商店}`，货币集合仅 `{稀世之证}`；`臻藏商店`、`宸世臻石`、`entry2949` 三个跨店词在所有记录中均为 `false`。

---

## 二十二、商店静态候选总表与 Wiki 接入（2026-09-01，Hermes）

### 22.1 目标与范围

用户要求保留当前 Documents 可静态解读的**全量商店结构表**，即使无法证明当期货架。该交付严格命名为“商店静态候选总表”，不得简称/发布为“当期兑换表”。

```text
只读源：E:\mrzh\Documents\script.py314.lc.npk
源 SHA-256：780363b86008999cf7ee5728e38033f4c7cfd8439977d098870d1aa7ffe3ba4d

同包 base：common_exchange_shop_data.nxs
file_id：4FCC4065681956B9
当前 workcopy entry：007760

同包 CHS：common_exchange_shop_data_chs.nxs
file_id：4EA3597CF2D785A7
当前 workcopy entry：007653
```

与第二十章臻藏截图表、第二十一章稀世截图表严格分层：本章不把任何静态格子写成臻藏/稀世当前商品，也不复用 `entry2949` 作为该表的业务归属。

### 22.2 已解结构与全量计数

实跑 dry-run（`export_exchange_static_candidates.py --dry-run --generated 2026-09-01`）exit 0：

```text
0x36 shop map 行：70
map identity（shop_key + pair_index + slot_key + detail_offset）：1,757 条
0x86 detail 字段解码成功：1,738 条
保留结构、detail bitmap 越界未解：19 条
```

`common_exchange_shop_data` 的 detail schema 可读出 `cost`、`item`、`show_item_id`、`limit`、`limit_per_purchase`、`month_limit`、`week_limit`、`category_ids`、`condition_ids` 等字段名及原始 typed-jump/scalar 值。交付只保留这些**原始字段引用**，不擅自把其数值升级为当前货币、价格、发放商品或限购结论。

为防止丢失/误命名：

1. 1,757 个 mapping identity 全部保留；19 个 detail 不因位图未解而删除。
2. 未建立直接同包 item-name 回填的行显示为 `静态格子 #shop_key/slot_key`，这是结构身份标签，不是假商品名。
3. `start/end/time` 类字段全部从交付中剔除；没有已验证语义时不发布活动期、倒计时或有效期。
4. 每行固定 `evidence=structure` 与 `current_stock_state=未绑定当前货架`。

### 22.3 不能跨越的当前货架边界

当前 Documents 静态包仍缺 runtime selector、consumer call-site 或当前 payload。用户实机稀世价格指纹 `1,1,1,1,2,10,30,30,50,450` 无法在 `common_exchange_shop_data` 的某一个静态 shop group 中形成完整、唯一的当前货架闭环。

因此：

```text
商店静态候选总表 = 可搜索的结构全集
不等于 = 当期臻藏/稀世商店
不等于 = 当前可兑换商品、货币、价格、限购或活动时间
```

### 22.4 交付与 Wiki 导入

构建器（Wiki 工具层）：

```text
E:\la拆包项目\08Lifeafter wiki\tools\export_exchange_static_candidates.py
```

回归测试：

```text
E:\la拆包项目\08Lifeafter wiki\tools\test_export_exchange_static_candidates.py
```

测试先行记录：初始导出器缺失时测试红灯；实现后内存构建测试通过，覆盖 1,757/1,738/19 与“非当前货架”标签。Wiki 首页入口测试也已通过。

待生成的版本化交付：

```text
03拆包产物\config_work\script_py314_docs_780363b86008\商店静态候选总表_2026-09-01.csv
03拆包产物\config_work\script_py314_docs_780363b86008\商店静态候选总表_2026-09-01.json
08Lifeafter wiki\data\boards\shop_static_candidates.json
08Lifeafter wiki\data\boards\shop_static_candidates.js（builder 生成）
```

Wiki 首页保留“当期兑换表”建设中提示，并另加“商店静态候选总表（1,757 结构）”入口；这能防止用户把静态全集误读为当前货架。

### 22.5 实际生成、校验与交付哈希

实跑导出器（非 dry-run）exit 0：

```text
CSV：商店静态候选总表_2026-09-01.csv
SHA-256：9c890089523204975e645a9a21c6a8135d0fc75fed528b29e69f3f8ed71d1df5

JSON：商店静态候选总表_2026-09-01.json
SHA-256：af06fcb5dfbae1bd0ed12a27cfeae1c7ccb592a185a4d80781d0cd1aa1ec1b4c

Wiki board JSON：data/boards/shop_static_candidates.json
SHA-256：af06fcb5dfbae1bd0ed12a27cfeae1c7ccb592a185a4d80781d0cd1aa1ec1b4c
```

`python tools/build_wiki.py` exit 0：8 个板块、2,937 条总记录；新板块为 `奖池类-常驻宸世 / 商店静态候选总表（非当期货架） / 1,757 条 structure`。

最终校验：

```text
回归测试：2/2 PASS
CSV 行数 / JSON items / Wiki board items：1757 / 1757 / 1757
manifest 新板块条目：1757（structure=1757）
CSV/JSON 与 Wiki board：数据字节一致
所有 item：current_stock_state=未绑定当前货架
CSV 列头：无 start/end/time 字段
```

浏览器 CDP 自动化在本机因 Windows localhost socket 权限拒绝（WinError 10013）未能加载 `file://` 页面，故**未记录为已完成视觉点击验收**；数据 JSON、JS 包装、manifest 登记、首页链接和构建器均已静态核验。Wiki 工作区保持未提交状态，未执行 git commit/push。

---

## 二十三、2026-09-01 `Documents/gres/0058.gpk` 新增尾包拆解（当前体验服）

### 23.1 源锁与增量边界

```text
当前源：E:\mrzh\Documents\gres\0058.gpk
当前 SHA-256：3fc273495f62bcd7830e2b9b7c5e2a94201a1c95ac9c90ca1e8dbaa175d8d8de
当前大小：1,158,751,514 B

紧邻旧稳定基线：post_update_resource_recheck_20260831_190236\raw_changed_vs_pre_final\Documents\gres\0058.gpk
旧 SHA-256：de92d2cb640e9ff7587a632ea507bf7dfa6501998fac92efdc1b97954b839f99
旧大小：1,146,791,214 B
新增：11,960,300 B
```

旧包范围内仅文件头 16B、距旧 EOF 457KB 处 16B 与旧 EOF 尾部 2B 不同；其余旧字节相同，随后追加新尾载荷。外层计数字段由 52→53，但未恢复字段语义，**不得称为“第 53 个段”或活动数量**。

### 23.2 实际解压与验收

直接扫描新增尾载荷的 Zstd frame；全部候选均独立完成实际 Zstd 解压：

```text
Zstd entities：763
成功：763
失败：0
解压类型：14 个 DDS、749 个二进制/资源描述实体
```

14 个 DDS 全部通过 Pillow 实际解析，均已转 PNG 并回读验证；3 个裸 `DDS ` 字节命中因异常尺寸/位深被验为压缩数据内偶然串，未计入贴图。

交付目录：

```text
E:\la拆包项目\03拆包产物\gpk_0058_delta_unpack_20260901\
├─ decoded\                                # 763 个解压原件
├─ dds_png\                                # 14 张 DDS 的 PNG 预览
├─ 00_gpk_0058_delta_dds_contact_sheet.png # DDS 联系表
├─ manifest.json                            # 每条偏移、大小、MD5、输出路径
└─ README_拆解结论.md                       # 人可读源锁、结论及边界
```

### 23.3 已验证的业务关联（STRONG）

解压实体中直接存在：

```text
kaijiayongshi_box.png
kaijiayongshi_fudai.png
kaijiayongshi_bg.png
zhutihuodong_v5/zhutihuodong/kaijiayongshi/02/choujiang/btn_liangjiyl_icon_down.png
```

同时存在 3 份 `spine 3.8.99` 动画 JSON，以及奖励预览/活动面板节点（如 `pnl_jiangli_spine`、`img_jiangliyulan_down`）。因此当前 GPK 新增尾包与**铠甲勇士二期的抽奖、礼包、背景、动画展示资源**有路径级直接关联。

边界：资源已入客户端包仅证明资源物理存在；没有 runtime selector/服务端开关/当前 UI 实机回链时，不能单独证明该活动当前已启用、奖池已切换或奖励必定可领取。

---

## 二十四、铠甲再临奖池 / 子奖池 / 配置概率审计流水线（2026-09-01 固化）

> 目的：以后查活动奖池时，不能只给面板展示，也不能再把未校准的尾组数值当作“真实池 → 槽位 → 奖励”。本章记录的是**可复跑的分层链路和停止条件**；旧文件保留供审计，但不因其文件名含“真实奖池”就自动恢复有效性。

### 24.1 必须分开的四层对象

```text
A. 活动 UI / 主题入口
   super_fashion_lottery_conf_data key=232
   → lottery_id=391782
   → fortune_bag_dct={4:391783}
   → left_item_id=139292（刑天铠甲） / right_item_id=139293（飞影铠甲）
   → panel_show_item_ids（仅页面展示清单）

B. 期次奖励行
   reward_pool_data_base 的已命名 D6/C6/96 行
   → expiration_time + broadcast_content（“铠甲再临”）过滤当前期
   → note/name、prob_note、ensure_count、reward jump

C. 秘宝/主池/福袋层
   既有前 Wiki 专项报告中：
   - pool=390704：长期“秘宝层”候选（exp=2298-11-08）
   - pool=391536：当前期候选行（exp=2027-01-31，broadcast 含“铠甲再临”）
   - pool=391536 slot=2：name=飞影刑天、note=飞刑福袋奖励，
     prob_note=0.03706、ensure=[30,30]、reward→391772

D. 发放物 / 实物内容
   reward 命名字段的 0x0b jump
   → 结构化 0x27 [item_id, quantity]
   → 同快照 item / gift / fashion / equip 正源回填名称
```

**硬边界：** A 已直接证明 `391782 → 391783` 的后级引用；C 中 390704、391536、391772 是按期次字段和已命名 reward 行恢复的奖励层事实。除非另有已命名 selector、consumer 或校准后的字段证明，**不得因为主题文字相同、ID 邻近，或未命名尾组出现 `[pool_id, number]`，就写成 `391782 → 391536` 或 `391783 → 390704` 的直接映射。**

### 24.2 配置概率与保底：正确读取方式

截图式概率报告来自前 Wiki 阶段对奖励行的直接字段整理，不是 Wiki board 生成：

```text
prob_note 原始值 × 100 = 报告中的“配置概率(%)”

例：
0.00188253012048 → 0.188%（刑天/飞影铠甲行）
0.00564759036145 → 0.565%（疾影枪、火刑电光炮、战神烈火剑行）
0.03706 → 3.71%（391536 slot=2 的飞刑福袋奖励入口）
```

- `ensure_count / ensure_weight / initial_threshold / cooling` 等字段必须原样保存；如已按结构化组验证 `ensure=[30,30]`，可表述为“配置写入 30 抽保底”。
- `prob_note` 是客户端**配置概率字段**，报告中必须写“配置概率”，不能擅自升级为包含保底递进、服务器热修、限时加成后的最终实机综合概率。
- 只有 `reward` 的命名字段经过完整 jump 链抵达 `0x27 [item_id,quantity]`，才可写“命中发放 X×N”；礼盒必须继续追其 `items`，不能停在礼盒名。

### 24.3 标准复跑顺序（以后所有活动都照此执行）

1. **锁源与服务器。** 重算当前 `Documents/script.py314.lc.npk` SHA-256；明确目标服。不得复用旧包 entry offset、旧 CHS 或另一服务器的 reward 行。
2. **先取活动入口。** 读取 `super_fashion_lottery_conf_data` 同包 base+CHS，记录 key、`lottery_id`、`fortune_bag_dct`、左右主奖、`panel_show_item_ids`、`rule_id`、`ui_group_id`、`video_path`。面板 ID 永远标“展示”，不是掉落表。
3. **再取奖励行。** 使用同快照 `reward_pool_data_base` 与经 source/CHS 自洽校验的对应字符串池，解出行的 `expiration_time`、`broadcast_content`、`note/name`、`prob_note`、保底字段和 `reward` jump。
4. **用期次字段筛选。** 以活动 broadcast 原文、有效 expiration 时间和命名 note 三者交叉选择当前期；长期秘宝层、当前期主池、福袋入口分别输出，禁止混成一张“本期全池”。
5. **建立子池映射前先校准语义。** `pool_id → slot → reward_row` 必须有已命名字段、consumer 或至少三条已知奖励的正反校准；未命名 `0x27 [39xxxx, slot]`、`reward_pool_no_item_no_list` 的 slot list、裸 ULEB 原始命中只能做定位候选。
6. **回填实物与概率。** 每行输出 `pool / layer / slot / expiration / broadcast / note / reward_item_id / quantity / prob_note_raw / 配置概率% / ensure_raw / 名称来源 / 证据等级`；无法回填名称写“未回填（ID）”，不从相邻 CHS 文本猜名。
7. **单独验证当前启用。** 客户端静态行、当前期日期字段、服务端 selector/实机 UI 是三件事。没有后两者时，只能写“当前包已配置 / 期次候选”，不得说“已经开放”。
8. **热更后重新跑。** 先比较活动表和 reward 表的 payload/key diff；只有当前 SHA 相同才允许复用本次结果。概率变化按 `prob_note_raw`、保底字段、`expiration/broadcast` 和 reward jump 的标准化结构比较，不能比较 table-local jump 偏移。

### 24.4 已作废的错误链（永久保留为反例）

```text
任意 reward_pool 行尾 0x27 出现 [391782 或 391783, 数字]
→ 把数字直接命名为 slot
→ 把该行 reward jump 当作铠甲再临该 slot 奖励
```

该链只验证了字节形状，未验证尾组字段语义，曾导出“391782 25 槽 / 391783 6 槽”并混入历史家具、旧时装和常规道具。相关旧 CSV、JSON 和 provenance 仍保留，但**不得用作活动内容、概率、槽位归属或获得方式的证据**；详细作废记录见：

```text
E:\la拆包项目\03拆包产物\铠甲再临_391782_391783_复证版_作废说明_2026-08-30.md
```

### 24.5 前 Wiki 概率报告的正确定位

`秘宝层 390704 / 飞刑福袋入口 391536 slot=2 / 发放 391772` 的报告是前 Wiki 阶段的**奖励行字段汇总**，其 0.188%、0.565%、3.71%来自原始 `prob_note`，并已保留 `exp / broadcast / ensure / reward` 上下文。以后引用时必须称为：

```text
“铠甲再临相关奖励行的配置概率报告（需随当前包和 runtime selector 复核）”
```

不能反向改写为“由 Wiki 生成”，也不能把它与已作废的 `391782/391783` 未校准尾组 join 混为同一证据链。

---

## 二十五、时装外观表字段错位根因终判 + 人物文字层全量落地（2026-09-01 晚，Doubao）

> 范围：BA8A239A 快照时装外观表（base fid E1645717C83FC968=BA entry022570 / CHS fid D016140651FEAB34=entry020834）+ 面饰专池（fid 6CD197C9670A961C=BA010816 / 5D094B94133851D2=BA009169，0x73 legacy 自带池）。证据等级：structure（值解码精确，字段语义按值分类法落地；未做实机闭环不升 verified）。只读源。

### 25.1 字段错位根因（终判，排除解码器 bug）
- 主表 19264 行 / 0 未解 / 19 个 schema_ref，主 schema=270688（4923 行）。字段记录格式 = slot(ULEB)+type(u8)，三种切分对比确认 A 正确；bitmap 判定无误；**解码器、切分、bitmap 均无 bug（勿再改 bindict_table 核心）**。
- slot0–89 字段名池完整：slot6=model_id、7=name、10=desc、12=part、13=part_type、14=charm_value、83/85=man_desc/man_name、86/87=female_desc/female_name。
- 数据驱动逐 slot 统计（slot_semantics，脚本已归档）证明：**同一 slot 在不同行混装 part部件名/desc描述句/path路径/color短标签**（如 slot12 在 521 行装部件名、5382 行装模型路径、2186 行装描述句）。根因=字段名(程序标识)与该行实际语义载体分离：
  - **时装显示名在 charm_value 槽**，格式 `名`（本体/永久）或 `名-N天`（N=1/3/5/7/14/30 时限变体）；
  - **part 槽装的是模型/图标路径**（character/…、ui/item_icon/…），不是部件名；
  - name(slot7)/desc(slot10) 存的是**整数文案/字符串 ID**（如 name=503156、desc=480），真正中文在其它内联 CHS 槽；
  - 描述句槽（socket_names_male/flowing_light_group_id/level 等）逐行跨记录错位，样例行里混入"潜龙在渊""天枢龙将背包""这个男人叫小帅"等**无关老时装描述**；意境描述句不含自身时装名，**强相关锚定命中 0%**。
- 结论：本表**无法按字段名可靠取描述**，只能可靠取 显示名/部件/时限/model_id/路径；描述必须另解 name 文案 ID→i18n 文案表（开放待办）。

### 25.2 值分类法统一加载器（可复用）
- 新增 `08Lifeafter wiki/tools/lib_fashion.py`：不信错位字段名，遍历每行全部 type=0x05 CHS 串，按**值本身特征**分 name/path/desc/code，显示名正则支持 `-部件` 与 `-N天` 后缀并解析 base/part_type/duration；model_id 用 slot6 稳定锚点；描述只保留含自身 base 名的强相关句（本表实际 0 命中→留空，杜绝串位）。
- 本体 model 选择规则：永久行(duration=None) model 优先，否则取非时限 model 最大值；900xxxxxxx 为时限版 model。硬验证：刑天铠甲本体=32710、帝皇铠甲=31643、帝皇战翼=30950、刑天召唤器=32709（与既有记录一致）。
- 质检：1094 base 名仅 1 噪声(NPC，已滤)，名字质量高。

### 25.3 人物三板块落地（build 后 9 板块 3663 条，浏览器逐页验证渲染正确、不串位）
| 板块 | 条数 | 导出器 | 说明 |
|---|---|---|---|
| fashion_wardrobe 全量时装衣柜 | 1093 | export_fashion_wardrobe.py（重写，旧457→1093，直接解 BA 表、不再用旧内容驱动 json） | 整套751/头饰66/头饰·衣服200/衣服75/套装1；desc 一律留空并标 desc_note |
| fashion_face 面饰/挂饰 | 180 | export_fashion_face.py（新增，解 0x73 legacy 池） | 名+时限可靠；描述待 legacy 表行解码 |
| fashion_kaijia 铠甲联动外观 | 9 | export_fashion_kaijia.py（重建） | 刑天/帝皇铠甲本体、帝皇战翼、刑天/飞影召唤器、铠甲飞兔、飞影浮澜头饰 + 面饰刑天面甲/飞影锋眸 |

### 25.4 铠甲联动人物线确定结论
- **不存在独立「飞影铠甲」整套衣服本体**：主外观表与面饰专池双源交叉，飞影线只有 飞影召唤器(80185)、飞影锋眸(面饰)、飞影浮澜(头饰)；刑天线=刑天铠甲本体(32710)+刑天召唤器(32709)+刑天面甲；帝皇线=帝皇铠甲本体(31643)+帝皇战翼(30950)。
- 铠甲面饰描述可靠样本：刑天面甲="承刑天不屈战意，绝境之中并肩坚守求生防线。「明日之后×铠甲勇士」联动限定外观"。

### 25.5 开放待办（可交接）
1. **name/desc 整数文案ID → i18n 文案表**：定位 name(slot7)=503156 这类 ID 指向的字符串/i18n 表（common_item_data 在 BA 仅 815B loader，真大表未定位），打通后可补全时装/面饰可靠描述。
2. **面饰 0x73 legacy 表行解码**：解 name 槽→desc 槽的行级配对（池内邻接配对仅 21%，不可用），补全 180 面饰描述。
3. P3 治本：19 个 schema_ref 逐 schema 正配字段名池（仍开放）。
4. 图鉴文字队列剩余：武器图鉴（hurt/power 147 条已具备 weapon_attrs_table，接皮肤128/涂装有文字分层）、载具（从 all_equips 筛 vehicle_type，只用结构字段+可靠名表）、核芯108核对补全。

---

## 二十六、Lifeafter Wiki 本地只读 NPK 按需读取 MVP（2026-09-02）

> 范围：把 `08Lifeafter wiki` 从纯 `file://` 静态展示，扩展为 **静态图鉴 + 127.0.0.1 只读 Script NPK 单条检查**。目标不是全量拆包，也不是给任何活动下“已开启”结论。源文件全程只读。

### 26.1 当前源锁与服务边界

```text
登记 source_id：documents-py314-current
物理源：E:\mrzh\Documents\script.py314.lc.npk
服务器：体验服 Documents 当前快照
SHA-256：ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad
bytes：270,106,156
mtime_ns：1788266451099903500
服务：127.0.0.1:8765（只绑定本机）
```

- `data/live_sources.json` 记录唯一可读源及预期 SHA / bytes；服务启动时重算完整 SHA-256，并在后续读条目前检查源文件 size+mtime 是否漂移。
- 物理源与登记锁不匹配时，条目接口返回 `source_lock_mismatch`；源在进程运行期热更时返回 `source_changed`。不得为了让页面恢复工作而直接填入新 hash，必须先完成新快照审计。
- 无 `raw` / `download` / `extract-all` 路由；已实际验证 `/api/sources/<id>/raw` 返回 HTTP 404。

### 26.2 已实现的按需读取链

```text
live_reader.html
→ localhost API
→ NXPK 头 + 48B entry stride 索引表（仅内存）
→ 按 entry_index / file_id seek 单条 packed payload
→ flag 0 AES + 可选 zlib / flag 2 LZ4 / flag 12 Zstd
→ 内存摘要：payload SHA、magic、直接路径候选、有限 UTF-8 预览
```

- 实现文件：`08Lifeafter wiki/tools/live_npk_reader.py`、`tools/wiki_server.py`、`live_reader.html`；说明文档：`docs/LIVE_NPK_READER.md`。
- `live_npk_reader.py` 的一个实际修正：NPK 单条有效字段 unpack 为 32B，但**表记录步长必须是 48B**（后 16B 为保留区）。首版将 32B 误作 stride，真实源第 2 条即越界；回归测试已固定此点。
- 首页标题右侧入口为“本地工具 · 现场读取 NPK”，不是图鉴的新一级分类；零到四的业务导航结构保持不变。

### 26.3 实测与证据等级

- 2026-09-02 本地服务实测：`/`、`/live_reader.html`、`/api/health`、`/api/sources`、`/api/sources/documents-py314-current/entries?offset=0&limit=1` 和 entry 0 summary 均 HTTP 200；entry 0 解码为 207 B。
- 回归：`python -m unittest discover -s tests -p 'test_*.py' -v`，3/3 PASS（真实源索引+单条摘要、API、首页工具入口）。`wiki.html`、`board.html`、`live_reader.html` 的内联 JS 均已通过 `node --check`。
- API 返回 `evidence_level=package_entry_exists` 和固定 `interpretation_boundary=entry_exists_does_not_prove_runtime_activation`：这只证明当前锁定包内的条目存在且可静态解码，**不证明活动开启、奖池切换、奖励可领取、物品上线或 selector 生效**。

### 26.4 复跑入口

```bash
cd 'E:\la拆包项目\08Lifeafter wiki'
PYTHONDONTWRITEBYTECODE=1 python tools/wiki_server.py --host 127.0.0.1 --port 8765
# 浏览器： http://127.0.0.1:8765/
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -p 'test_*.py' -v
```

---

## 二十七、Lifeafter Wiki 定位链审计与安全重建第一切片（2026-09-02 17:08 +08:00）

> 目标：先把无法复跑的旧定位链从对外展示撤下，再只放行一份能从当前 BA8 源包重复生成的最小板块；不以“展示数量”换取错误业务结论。

### 27.1 审计结果与止血

- 完成对 11 个旧 board 的来源与行级 provenance 盘点：旧板共 0 条可机读 item provenance，覆盖时装、武器皮肤、属性、载具、贴图、奖池、核芯和静态商店。
- 旧 board 已全部保持 `quarantined`：`fashion_*`、`weapon_*`、`vehicle_catalog`、`new_textures`、`lottery_dihuang`、`lottery_kaijiazailin`、`nucleus`、`shop_static_candidates`。未知 board 默认拒绝。
- 创建 `03拆包产物\wiki_positioning_chain_audit_ba8a239a_20260902\定位链全量审计矩阵.md` 与机器可读 `board_provenance_inventory.json`；分别记录逐板断点与旧基线。
- `nucleus.html`、`weapon_skins.html`、`new_textures.html` 原内容逐字节归档到 `08Lifeafter wiki\data\quarantine_legacy_html\`，旧 URL 改跳转 `board.html?b=<id>` 的 policy 隔离页；不删除原文。

### 27.2 发布契约与单板重建

- 新增/完善：`tools/publication_policy.py`、`data/publication_policy.json`、`tools/build_wiki.py`、`tests/test_publication_gate.py`、`docs/SCHEMA.md`（v0.2）。已发布 item 强制保存 source lock、entry/FID/payload SHA、table、row key、field refs、同快照名称来源与 evidence level；需要业务结论的等级另需 business/user chain。
- 新增 `tools/rebuild_kaijia_panel_static.py`：只读锁定 `E:\mrzh\Documents\script.py314.lc.npk`，实际 SHA=`ba8a239a…bcc55ad`、bytes=`270106156`、mtime_ns=`1788266451099903500`；按 FID 现场解码 `super` base/CHS 与 `gift` base/CHS，复现 `super_fashion_lottery_conf_data key=232 → panel_show_item_ids`。
- 新 board：`data/boards/lottery_kaijia_panel_static.json`。10 个面板 ID；同包 gift 正源仅回填 139292 刑天铠甲、139293 飞影铠甲、134061 异变核芯-球状闪电（禁交易）、132694 异变核芯-酸焰激流（禁交易）；其余 6 个严格显示“未回填（ID …）”。
- 该 board 的证据为 `structure-only`，仅代表静态面板配置；明确不代表活动启用、完整奖池、掉落、概率、保底或奖励可领取。
- `post_remediation_publication_inventory.json` 实测：12 个 board 在磁盘，1 个 published、11 个 quarantined；最终 `manifest.js` 仅 1 个 board / 10 条记录。

### 27.3 验证

```text
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -p 'test_*.py' -v
→ 14/14 PASS

PYTHONDONTWRITEBYTECODE=1 python -m py_compile tools/publication_policy.py tools/build_wiki.py tools/rebuild_kaijia_panel_static.py
PYTHONDONTWRITEBYTECODE=1 python tools/rebuild_kaijia_panel_static.py --output data/boards/lottery_kaijia_panel_static.json
PYTHONDONTWRITEBYTECODE=1 python tools/build_wiki.py
→ manifest 1 board / 10 items；行级契约通过

Headless Chrome（localhost）
→ 首页只显示该重建静态 board；新 board 可打开；nucleus 直链隔离；旧 nucleus.html 重定向隔离页
```

### 27.4 未完成边界

- 其余 11 个旧 board 未恢复。下一个切片应从可保留为非当前结构档案的 `weapon_attrs` / `new_textures` / `shop_static_candidates` 开始，先补 row key 与同快照名称来源，再讨论业务分类。
- 所有奖池、商店、核芯的“当前期/在售/掉落/概率/保底”仍需当前 selector/consumer 或用户实机链；静态入包和面板字段不够。

### 27.5 第二切片：all_equips → schema6109 原始属性关系（2026-09-02 17:16 +08:00）

- 旧 `weapon_attrs.json` 已复核为不合格：它只是读取上游 `武器攻击力火力表.json` 后重新 hash 当前 NPK；二者没有 source/row 绑定，并按不可靠中文 `name` 去重为 147 条、计算 `hurt×power` 后写成“理论伤害”。该旧 board 继续 `quarantined`。
- 现场从 BA8 读取 `all_equips` base FID `A130A31532FAF63C`（entry 16135，payload SHA `8573…2e516`）与 CHS FID `94AB0B3FD057EF01`（entry 14847，payload SHA `b57a…5a73f`）；schema6109 实测 55 字段，field[23] 标签为 `hurt`、field[35] 标签为 `power`。
- 直接保留 raw relation 后得到 196 个唯一 `all_equips row key → attrs_offset`，但仅有 51 个共享 attrs 对象；这否定了“147 把独立武器数值”的旧表述。父行候选文本可出现说明句，故全部放弃名称使用。
- 新增 `tools/rebuild_weapon_attrs_schema_static.py`、`tests/test_rebuild_weapon_attrs_schema_static.py`、`data/boards/weapon_attrs_schema_static.json`。新板逐项保存 source lock、两个 entry/FID/payload SHA、row key、attrs offset、schema6109 field[23]/field[35] 原值；显示名统一 `未回填（all_equips key=…）`；不包含伤害、排序、装备归属或当前玩法数值。
- policy 仅新增该新 board 为 `published`；首页把它动态放在“三、战力类 → （1）武器本体与涂装”。最终实测：13 board on disk，2 published、11 quarantined、206 published items（铠甲面板 10 + 匿名属性关系 196）。
- 验证：全套 `unittest` 15/15 PASS；`py_compile`、两张重建 board 的行级契约、manifest 2 board/206 item 均通过；Headless Chrome 确认首页两张已发布卡、匿名属性页可开、旧 `weapon_attrs` 直链仍显示隔离页。

### 27.6 localhost 隔离数据资产门禁（2026-09-02）

- 异步只读审计指出：虽然 `board.html?b=` 已先过 policy，旧 `data/boards/<id>.js/.json` 仍可能被 `wiki_server.py` 作为普通静态文件返回；这会让隔离数据经 localhost 直链暴露。
- 在 `tests/test_wiki_server.py` 先加入真实 HTTP 红灯：已发布 `weapon_attrs_schema_static.js` 必须 200，隔离 `weapon_attrs.js/.json` 必须 404。修改前测试按预期失败，隔离 JS 返回 200。
- `wiki_server.py` 现对 `/data/boards/` 使用 `publication_policy.json` 明确白名单：仅精确匹配 `data/boards/<id>.js|json` 且该 `<id>` 为 `published` 时放行；隔离、未知、子路径与其他后缀统一 404。原始隔离 board 文件继续保留在磁盘，供审计和重建，不会由 localhost Wiki 服务公开。
- 验证：该门禁测试已绿，随后全套 `unittest` **16/16 PASS**、`py_compile tools/wiki_server.py` 通过；实测 published JS=200、quarantined JS/JSON=404。未启动持久 server，未改动游戏源包。

### 27.7 第三切片：兑换商店静态 mapping/detail 关系（2026-09-02）

- 旧 `shop_static_candidates.json` 继续 `quarantined`。审计确认旧导出器固定读取旧快照 `script_py314_docs_780363b86008/entries/007760.bin + 007653.bin`，但运行时又对当前 NPK 重算 SHA 写进 meta；并且把易变 NPK `entry_index` 当跨热更稳定定位。这会形成“旧 payload + 新 package SHA”的伪链。
- 同一旧 index 在 BA8 中已指向不同 FID（current 7760=`4F51D797F6ECD63F`、7653=`4E3D748650148ACB`），证实 index 不能复用。按 FID 反查才得到稳定当前位置：base `4FCC4065681956B9` → entry 7804、payload SHA `a35d…f084c`；CHS `4EA3597CF2D785A7` → entry 7697、payload SHA `1ce5…ddc7`。两条当前 payload 与旧快照版本本体 SHA 相同，但其 package lock 已严格切换为 BA8 `ba8a…55ad`。
- 新增 `tools/rebuild_exchange_static_structure.py` 与 `tests/test_rebuild_exchange_static_structure.py`。重建器从 `live_sources.json` 校验当前 source SHA/bytes，按 FID 现场 seek/解码 base+CHS；每条保存 source lock、base/CHS entry+FID+payload SHA、mapping row、pair index、shop_key、slot_key、detail offset、schema/原字段，以及中性名称“未回填（静态格子 key=…）”。
- 当前实测：70 个 mapping row、1757 个 mapping pair、1647 个 unique detail offset（alias 关系保留，未按 detail 去重）、1738 条 detail 可解、19 条只保留未解结构。没有 selector/consumer，故新板不写运行时货架、商品名称、货币、价格、限购或活动启用。
- 新 `exchange_static_structure` 作为 `published` 放入“**四、奖池 → （2）满减活动、神秘商店**”；旧 `shop_static_candidates` 仍隔离。最终为 14 board on disk，3 published、11 quarantined、1963 published items（兑换静态结构 1757 + 铠甲面板 10 + 匿名属性关系 196）。
- 验证：TDD 红灯（缺重建器、再缺 builder 基础 meta/source、再缺 policy/首页插槽）均逐步修绿；全套 `unittest` **17/17 PASS**、`py_compile` 通过、行级契约和 manifest 3 board/1963 item 通过。Headless Chrome 确认首页显示新板、该板可开、旧 shop 直链隔离；localhost 上新 board JS=200、旧 shop JS=404。服务已停止，游戏源包未改写。

### 27.8 第四切片：当前 BA8 同快照礼盒文字表与名称回填链（2026-09-02）

- 问题修复：共享 `decode_table_rows` 只返回友好值 `(scalar_type, text)`，没有保留 CHS 槽位；只留中文文字不能作为 Wiki 的可回放名称来源。为避免修改 `01拆包器本体` 的共用工具，在 `08Lifeafter wiki\tools\bindict_provenance.py` 新增 Wiki 私有只读 decoder，保留 `field_chs_slot → value_chs_slot → text`。先写 `tests/test_bindict_chs_slots.py` 红灯，再以 BA8 `gift_data key=130000` 实测复放 `name` 的字段槽与文本槽后转绿。
- 当前主源仍严格锁定 `E:\mrzh\Documents\script.py314.lc.npk`：SHA-256 `ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad`、270,106,156 bytes、mtime_ns `1788266451099903500`。文字表只读同包 `gift_data` base FID `C5998AD60B305608`（entry 19768，payload SHA `e3c6c61d…2f338a`）与 CHS FID `938D86FE498D1B1A`（entry 14746，payload SHA `e3d51970…51652ec`）。
- 新增 `tools/rebuild_gift_data_text_sources.py`、`tests/test_rebuild_gift_data_text_sources.py`、`data/boards/gift_data_text_sources.json`。实测 5,445 个索引 row：5,443 条完整解码、5,443 条有同包 `name`、5,409 条有同包 `desc`；key `132721`、`135958` 的未支持 inline-tail 变体以 `stats.unresolved_*` 公开保留，没有为了凑全而删除或猜解。
- 新 board `gift_data_text_sources` 以 `published` 放入“**一、道具总表 → （1）当前同快照礼盒文字表**”。每项保存 source lock、base/CHS entry+FID+payload SHA、row key、`gift_data.name/desc` 字段引用和文字槽位 provenance。它仅证明行级名称/说明文本；明确不表示礼盒可得、可购买、可开启、奖励内容、价格、货币、限购或活动启用。
- `lottery_kaijia_panel_static` 同步切到该 CHS provenance decoder：同包已回填的 4 个名称（刑天铠甲、飞影铠甲、两个异变核芯）现在直接保存 `gift_data.name` 的 field/value slot；无同包名称正源的其余 6 个 ID 仍为“未回填（ID …）”。
- schema/pipeline 追加“文本字段必须保留 field slot 与 value slot”的发布规则。验证：全套 `unittest` **19/19 PASS**、`py_compile` 通过；实际 localhost HTTP 复核 `LIVE_HTTP_TEXT_BOARD_GATE_OK boards=4 records=7406 gift_rows=5443 sample=130000 slots=replayable legacy_weapon_attrs=404`。policy/static asset gate 允许新 board JSON、隔离旧 `weapon_attrs` 仍 404；build 结果为 **15 board on disk / 4 published / 11 quarantined / manifest 7,406 records**（兑换 1,757 + 礼盒文字 5,443 + 铠甲面板 10 + 匿名属性关系 196）。临时服务已停止，游戏源包未写入。
- 后续同包配对反例已登记：旧 `lib_fashion.py` 的 entry-index 线索在当前 BA8 实际解析为候选 base `22570/FID E1645717C83FC968/payload b02dd41f…ab4e6` 与候选 CHS `20834/FID D016140651FEAB34/payload 66e798a1…4a58e`。两者虽可分别解码（base 19,264 row、CHS 19,482 slot），但行解码出现字段名被路径/文案值占位、`name` 字段没有 0x05 文本的串位信号；6 个未回填 panel ID 都不在 row key 集。该候选配对未通过字段语义校准，**不得用于时装文字表或任何名称回填**；未生成 board，也未修改当前“未回填”状态。
- `common_item_data` 当前包路径也已按稳定 FID 直验：base `1232F498D07A0EBB` 在 BA8 为 entry 1765、payload SHA `af4d91fe…25d51`，但仅 815B 且没有 `x{` 表体；CHS `16037E102973F615` 在 entry 2131、payload SHA `65493c05…07b68`，有 3,496,923B 文字载荷。当前 Documents 缺同包可解 base，故 **不得以单独 CHS 或根包/旧快照 common_item_data 给 1110181/1110182/1110183 等 ID 补名**。

### 27.9 第五切片：武器皮肤父项 → SFX 子项结构（2026-09-02）

- 用户纠正：`sfx_name`（命中/弹道/音效/技能标签）是**其 `skin_id` 对应武器皮肤的子项**，不得被平铺成与皮肤并列的图鉴条目。此前新建的 `weapon_skin_sfx_text_sources` 首版虽然逐条 row/CHS 链正确，却把 20 条 SFX 平铺为 20 项，属于信息架构错误；已在正式发布前重构，而非以改标题掩盖。
- 当前 BA8 现场按路径 FID 读取并锁定四项：`weapon_skin_data` base `765AB12F1D6EB0EA`（entry 11817，payload SHA `55289493…04598`）+ CHS `D35E3103168889D2`（entry 21177，payload SHA `ea7dc770…190ce`）；`weapon_skin_sfx_function_data` base `B693DB548E5412B6`（entry 18238，payload SHA `d6f0409e…0addc`）+ CHS `5C56D035B329BEBB`（entry 9096，payload SHA `dd181037…c549b`）。四项均同一 Documents BA8 source lock `ba8a…55ad`。
- `rebuild_weapon_skin_sfx_text_sources.py` 现要求每个 SFX 行的 `skin_id` 精确命中 `weapon_skin_data.key`，否则拒绝构建父组；输出为 **9 个皮肤父组 / 20 个可回放 SFX 子项**（SFX 表 321 解码行、27 unbound）。父项 provenance 保存四个 entry/FID/payload SHA、`weapon_skin_data.key == skin_id`、全部子行 key；子项保留独立 SFX row key、sfx_type、`sfx_name` field/value CHS slot。
- 父名规则收紧为：同一 skin_id 至少两条 SFX，去 `命中特效/弹道特效/音效/特效` 明确后缀后根名必须唯一，才可暂填父名。当前仅 `1110178=帝皇裁决`、`1110181=疾影枪`、`1110183=战神烈火剑` 符合；`1110182` 根名同时为“火刑电光炮/火刑裁决”而保持未回填；`1110009` 只有一条“加油少年音效”而属证据不足；其余多特效根名父组也全部未回填。任何 SFX 子项都不再作为皮肤父名或同级皮肤显示。
- `board.html` 增加父卡内 `SFX 子项`渲染区，搜索会进入嵌套子项；通用字段渲染不再把 `sfx_items`/`name_resolution` 对象串成文本。policy、SCHEMA、审计矩阵同步改为“皮肤父项→SFX 子项”语义。
- 最终生成 `weapon_skin_sfx_text_sources` 为 9 个 manifest item（内部含 20 children）；manifest 现为 **5 board / 7415 父级公开记录**。验证：TDD 先见 20 平铺和无子项 UI 两个 RED，重构后定向 2/2 PASS；全套 `unittest` **21/21 PASS**；实际 HTTP 验证 `LIVE_HTTP_PARENT_CHILD_SKIN_SFX_OK boards=5 records=7415 parents=9 children=20 named=3 ambiguous=1 insufficient=1 legacy_weapon_attrs=404`。临时 localhost server 已停止，原始游戏包未写入。
- 为寻找真正父级正式名，另对同一 `weapon_skin_data` 全表做字段审计：共 125 行；20 个 SFX 涉及的 9 个父行字段集合中**没有** `name` 或 `item_id`。仅含 `camera_conf_id`、`camera_conf_id_2`、`idle_anim`、`nucleus_replace_ids`、`v2_self_soft_bone_id`、`yk_accessory_model_line_id` 等配置 ID，它们语义分别是镜头/动画/核芯替换/骨骼或饰线，不可当作 `gift_data` 道具外键。因此当前 SFX 一致根名只是受严格限制的父项暂填，尚未获得独立的同快照正式名称正源；后续需定位可校准的名称表，不得将 parent model_path、跳表配置或上述 ID 硬连到礼盒表。

### 27.10 当前 BA8 武器皮肤全量图鉴（2026-09-02 22:56 +08:00）

- 用户要求先补齐全量图鉴；范围严格定义为 **BA8 当前 `weapon_skin_data` 的每一个 parent row 都必须出现**，而不是只显示有 SFX 名称的 9 个皮肤，也不是把根包 v5/v7 的历史名称迁入当前 display name。
- 当前 BA8 source lock 保持 `ba8a239a…bcc55ad`。从同包 `weapon_skin_data` base `765AB12F1D6EB0EA`（entry 11817，payload `55289493…04598`）+ CHS `D35E3103168889D2`（entry 21177，payload `ea7dc770…190ce`）重建得到 **125 父行**；同包 SFX base `B693DB548E5412B6`（entry 18238，payload `d6f0409e…0addc`）+ CHS `5C56D035B329BEBB`（entry 9096，payload `dd181037…c549b`）解出 **321 行**，每行 `skin_id` 都精确命中这 125 个父行，无孤儿。
- root 8-27 (`0f824b35…b03b7`) 只作为版本 key presence 对照：同 FID parent base 在 entry 49069（payload `f26f9318…9e917`），CHS 在 entry 87558（payload `fc7806c9…dd24f`），共 121 行。BA8 独有 4 个父 key：`1110181/1110182/1110183/11101811`；图鉴对它们标记“BA8 新增（相对 root 对照）”。**根包名字、v5/v7 CSV 与 root item 表均未写入当前 display name。**
- 新增 `tools/rebuild_weapon_skin_catalog_current.py`：输出 125 父项、全部 321 SFX 子项；75 个父项有 SFX、50 个无 SFX 也保留。每父项保留 model_path/level/weapon_type 的同包字段与 provenance；每子项保留 SFX row key、type、raw fields、可用 `sfx_name` CHS field/value slot。旧 `rebuild_weapon_skin_sfx_text_sources.py` 改为兼容委托入口，防止再运行旧命令把正式 board 覆盖回 9 项。
- 名称状态：当前仅 `1110178=帝皇裁决`、`1110181=疾影枪`、`1110183=战神烈火剑` 满足“两条以上当前同 ID SFX 去后缀后根名唯一”，标为 `temporary_sfx_consensus` 而非正式名正源；5 个为 `ambiguous_sfx_names`（含 1110182），1 个为 `insufficient_sfx_names`（1110009），其余 **116 个**为 `no_current_name_source`，统一显示“未回填（武器皮肤 ID …）”。
- 生成公开 board `data/boards/weapon_skin_sfx_text_sources.json`（1,423,902 B，SHA-256 `38e05ba2…e5ddc`）及 Excel 友好 CSV `data/exports/weapon_skin_catalog_current.csv`（125 行、45,337 B、SHA-256 `0abe03ac…dad05`）。manifest 现为 **5 board / 7531 公开父级记录**。
- 验证闭环：先以“125 parent / 321 child / 50 无 SFX 仍保留 / root 名称不得进入 display”写 RED（缺重建器失败），实现后新全量契约 PASS；兼容入口 + UI 匿名 SFX 子项回归 2/2 PASS；全套 `unittest` **22/22 PASS**；实际 HTTP 验收输出 `LIVE_HTTP_FULL_WEAPON_CATALOG_OK boards=5 records=7531 parents=125 sfx_children=321 sfx_parents=75 no_sfx_parents=50 temp_names=3 unfilled_no_current_source=116 csv_rows=125 legacy_weapon_attrs=404`。临时 localhost server 已停止，原始包未写。

### 27.11 武器皮肤 128 项分层全量图鉴 + SFX 命名回退修复（2026-09-03 03:17 +08:00）

- **本节取代 27.9/27.10 中“同 ID SFX 根名一致可暂填父名”的错误规则。**`1110178/1110181/1110183` 不再由 SFX 写入父项当前 `display_name`；同 ID 根名一致仅存 `sfx_consensus_unpromoted` 审计状态。此前 9 父组 / 20 SFX 的阶段性数字仅作历史记录，不能再视为当前图鉴口径。
- 用户提供 `武器皮肤总表_整理版_v3-2.csv`，已逐字节保存为 `08Lifeafter wiki/data/reference_inputs/weapon_skin_catalog_user_reference_v3_2.csv`（128 行，27,487 B，SHA-256 `827935d8…98456`）。它的名称、描述、联动 IP、战斗/待机动作、战斗表现字段写入每条 `reference_fields`，界面明确标为“历史整理参考（用户提供；非当前正式名正源）”；源 hash 不符即拒绝重建，绝不自动提升为当前正式名或可得性证据。
- 当前 BA8 `weapon_skin_data` 仍为 125 条父行，root 对照为 121 条，BA8 父表独有 `1110181/1110182/1110183/11101811`。新增复证 `weapon_skin_behavior_res_data` 真正 BA8 条目：base FID `9F445AE2AA87D880` / entry `15939` / decoded SHA `7e7d6215…c3a0e`；CHS FID `E59CCA1F31417C6A` / entry `22997` / decoded SHA `c5d7bb55…92bc`。旧 skill 所列 `15858/22893` 已复测为错位加载壳/漂移 entry，已更正 skill。
- 行为表中不属于 125 父表的仅 3 条，作为 `behavior_preview_only` 预告层而非正式父皮肤：`1110184` 有 skin_2003_033 两条刀光/命中路径，`1110186` 有 skin_2003_031 两条刀光/命中路径，`1110190` 有 skin_1006_013 五条开火/命中/弹道路径。每条均保留行为表 row key、field refs、CHS field/value slot、当前 source lock 与 decoded payload SHA。
- `tools/rebuild_weapon_skin_catalog_current.py` 现输出 **128 项**：125 `current_parent` + 3 `behavior_preview_only`；125 父项中 75 个有合计 321 条嵌套 SFX、50 个无 SFX 仍保留。统计同时锁定 `125 / 3 / 128 / 321 / 75 / 50 / 128 reference`。父项无同快照正式名称链时一律“未回填（武器皮肤 ID …）”；历史整理名作为可见参考字段，不混入当前名。
- `board.html` 现显示当前未回填名之下的历史整理参考块，并为 3 条预告展示“当前行为资源（仅路径配置）”；CSV 导出扩展为 128 行，含图鉴层级、当前名称状态与全部历史整理参考列。产物：`weapon_skin_sfx_text_sources.json` 1,540,249 B，SHA-256 `fb98e508…8896e`；`weapon_skin_catalog_current.csv` 65,885 B，SHA-256 `0b516298…f5e09`。
- 同轮修正 `lottery_kaijia_panel_static`：删除 `resolve_unanimous_sfx_name` 和武器 SFX 表读取，面板只允许同快照 `gift_data.name` 回填。`1110181/1110182/1110183` 均恢复“未回填（ID …）”，其 provenance 不再含 `weapon_skin_sfx_text_provenance`。新板 SHA-256 `a0063057…a81ff`。
- 验证：图鉴/兼容入口/铠甲/发布门禁定向全绿；最终 `unittest discover` **22/22 PASS**。实际 localhost HTTP 验收：`LIVE_HTTP_128_LAYERED_CATALOG_OK boards=5 records=7534 catalog=128 current_parents=125 behavior_previews=3 sfx_children=321 reference_rows=128 csv_rows=128 kaijia_sfx_names=0 legacy_weapon_attrs=404`。额外 ad-hoc 边界验证：`AD_HOC_128_CATALOG_BOUNDARIES_OK catalog=128 parents=125 previews=3 sfx=321 reference=128 kaijia_sfx_backfill=0`，临时 `hermes-verify-1ukvbtdm.py` 已删除。临时 localhost server 已停止，原始包只读未写。

### 27.12 DeepSeek V4F 接手断点（2026-09-03）

- 已建立快速接手卡：`E:\la拆包项目\08Lifeafter wiki\docs\HANDOFF_TO_DEEPSEEK_V4F_20260903.md`。它是本日志 27.11 的导航副本，不竞争正式结论；本日志和当前原始 BA8 包优先级最高。
- **接手第一优先级**：定位并校准 BA8 当前同快照的 `skin_id → formal display name` 行级结构化关系。只有其 base/CHS 同包、字段/值 CHS slot 可复放、行 key 或显式外键可直接解释地 join `skin_id`、并经语义抽样校验后，才可把对应 `current display_name` 从未回填提升为 verified。
- 不要重做当前图鉴，不要先扫 GPK/贴图，也不要先做 exchange。当前已完成 128 项结构（125 父项+3 行为资源预告）/321 SFX/128 行参考 CSV；下一模型应在此基础上补**名称正源**，不是重新分类 SFX 或复制 root 名字。
- 红线：root 8-27、v5/v7 CSV、BA8 占位 `common_item_data`、孤立 CHS、模型路径、目录名、SFX 名、行为资源路径和用户旧表均不能提升 current 正式名。`sfx_consensus_unpromoted` 只是一致性线索；SFX 永远是父项子项。三条 `behavior_preview_only`（1110184/86/90）不是正式父皮肤。
- 当前主源仍为 `E:\mrzh\Documents\script.py314.lc.npk`，SHA-256 `ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad`、270,106,156 B、严格只读。当前核心 FID：skin base/CHS `765AB12F1D6EB0EA`/`D35E3103168889D2`（entry 11817/21177）；SFX base/CHS `B693DB548E5412B6`/`5C56D035B329BEBB`（18238/9096）；behavior base/CHS `9F445AE2AA87D880`/`E59CCA1F31417C6A`（15939/22997）。旧 behavior 15858/22893 已证实不可靠。
- 已排除：BA8 `common_item_data` base FID `1232F498D07A0EBB` 为 815B 无 `x{` 占位；`lib_fashion.py` 旧 pair 字段/值串位；旧 behavior entry index 漂移。不要重复把这些候选写成名称源。
- 最小起跑命令与最终门槛见 handoff 卡：先 source lock + TDD RED，再重建、全套 unittest、HTTP、临时 ad-hoc verifier。最后一次基线为 `unittest 22/22 PASS`、HTTP 5 boards/7534 records、皮肤 128/125/3/321、铠甲 SFX 假名 0。
- 名称链完成后的第二优先级才是 `exchange_static_structure` 的同快照 item/gift 名称 join 与 selector/consumer；未获得 runtime 链前不得宣称当前货架、价格、货币、限购或活动。

### 27.13 武器皮肤正式名闭环：common_item_data_base 正源 + 时限变体子卡（2026-09-03 03:38 +08:00）

- **重大发现，取代 27.12 的"BA8 内可能无正式名源"断点**：Documents BA8 中 `common_item_data.py`（entry 1765，815B 加载壳）不是真正的道具表。真表是 **`common_item_data_base`（entry 18005，FID `B42760CCA41DBC25`，decoded SHA `79e25ffd…ab34e`，1,979,020B，x{ @263）+ `common_item_data_base_chs`（entry 23928，FID `EF3A8474A5E5F7A4`，decoded SHA `3be82c3b…89494b`，3,500,753B）**。35,948 行可解、1,986 unbound；字段含 `name`（field slot 4）/`desc`/`icon` 等，CHS value slot 可回放。旧 1765+2131（815B 壳+3.49MB CHS）仍不可用，两者不配对。这是 BA8 热更包的 base+inc+del 表族：inc=5292（2,624B）、del=16447（147B）只是小增量。
- 用户确认三项业务规则：① 1110182 当前名用道具表正式名"火刑裁决"，曾用名（SFX 系"火刑电光炮、火刑裁决"）保留在历史参考层并注明出处；② `xxx1` 时限变体是会员服独有的时限武器皮肤，不单列，作为主皮肤的子卡；③ 变体名用道具表原文（如"疾影枪（7天）"）。
- 图鉴新结构（代替 128 顶层平铺）：**顶层 114 = 111 主皮肤（weapon_skin_data 无时限后缀行）+ 3 行为预告**。14 个时限变体（`k%10==1` 且 `k//10` 为主皮肤：11100061/11101341/11101681/11100231/11100271/11100281/11100901/11101141/11101451/11101691/11101701/11101771/11101781/11101811）全部嵌套为 `variant_items` 子卡，绝不在顶层。111 主皮肤全部 `verified`（同快照 common_item_data_base name/desc，CHS 槽可回放），evidence_level 升为 current-snapshot-verified 并带 business_chain。11 个变体有道具行正式名（11101811=疾影枪（7天）、11100231=玉饮琼花（14天）、11101781=帝皇裁决（7天）等）；3 个无道具行（11100061/11101341/11101681）`official_name_status=no_item_row`，display="主名（时限版）"，名称状态 user_confirmed_time_limit_variant_no_official_item_row（用户实机确认会员时限版）。SFX 321 条仍全部为子项（sfx_on_variant_skins=0，即变体无独立 SFX）。1110184/1110186/1110190 确认无道具行，保持行为预告未回填。
- `lottery_kaijia_panel_static` 同步升级两级名称回填：优先 common_item_data_base（1110181=疾影枪、1110182=火刑裁决、1110183=战神烈火剑），其次 gift_data（139292/139293/134061/132694 刑天铠甲等 4 个——探测确认它们无 common_item 行），皆无（194190/633070140/633080140）仍"未回填（ID …）"。
- 产物（新哈希）：`weapon_skin_sfx_text_sources.json` SHA-256 `274e3245…5ad61f`；`weapon_skin_catalog_current.csv`（128 行扁平：111 主+14 变体+3 预告，含"所属主皮肤ID/当前官方描述"列）SHA-256 `91e321e9…9f79`；`lottery_kaijia_panel_static.json` SHA-256 `9756f24a…ddb20`。manifest 现为 **5 board / 7520 顶级公开记录**（皮肤图鉴 114 顶层）。board.html 支持"时限变体子项（会员时限版）"区块、官方描述、正式名状态；搜索 JSON 全量可检索。
- 验证：定向 RED（field_refs 缺 common 引用先红）→ GREEN；武器皮肤契约/兼容入口/铠甲/发布门禁定向全绿；全套 `unittest` **22/22 PASS**；实际 HTTP 验收 `LIVE_HTTP_OFFICIAL_NAME_CATALOG_OK boards=5 records=7520 top=114 main_official=111 variants=14 previews=3 csv=128 kaijia_item_names=3 kaijia_gift_names=4 legacy=404`。policy reason、SCHEMA、审计矩阵、skill（weapon-skin-table-builder 顶部新增正源 FID/entry 覆盖块）已同步；临时 localhost server 已停止，原始包只读未写。
- 遗留（下轮候选）：① 3 个无道具行变体的精确时限天数（等实机截图/会员面板锚点补"（N天）"）；② 官方 desc 已进数据层，参考层 desc 与官方 desc 的双显去重可优化；③ exchange_static_structure 的名称 join 现在可参考同一 common_item_data_base 正源（gift 兜底），待 selector/consumer 链后再公开名称。

### 27.14 客户端热更/全量资源架构模型（2026-09-03）

- **总体模型（网易系 PC 客户端双层架构）**：安装根目录 = 全量基线；`Documents` = 热更覆盖区。运行时 Documents 层优先，故 BA8（Documents 9-01）是"当前态"，root 8-27 是"上一版全量基线"。分层如下（均为实测）：
  - 根 `E:\mrzh\res.npk` 2,015,778,608B（2024-12-10）：老资源全量基线；根 `script.py314.lc.npk` 455,619,092B（8-27 19:19，105,777 条）：上一版全量脚本基线；根 `script.npk` 229MB（2024-12）：legacy 脚本。
  - `Documents\script.py314.lc.npk` 270,106,156B（9-01 20:40 = BA8，25,373 条）：当前热更脚本包（唯一事实主源）。
  - `Documents\script.py3.npk` 473,764,988B（7-23）与 `Documents\script.npk` 340,643,664B（6-24）：旧脚本体系历史层，只作定位线索。
  - `Documents\res\`（72 项）：资源级热更，`building*.wpk / building3-8.wpk / character*.wpk / building.idx / character.idx` 等分卷 + idx 增量，覆盖根 res.npk 对应资源。
  - `Documents\gres\`（35 个 `0000.gpk…0011.gpk` 等）：另一类 gpk 格式资源热更区。
  - `Documents\client_doc@1_11030158…11030216`：**空标记文件序列**，每应用一个补丁写一个编号点（1103xxxx 递增）。`cfs_version`=1（内容文件系统版本）；`fo_version`=`2025_09_release_260820_563fc6840.1787042154.1788253891`（release 标识 + git hash + 双时间戳，后者≈9-01 构建）。`downloaded_packages` 当前为空。
- **表级三件套合并机制（本轮核心新证据 + 一处认知修正）**：Documents 热更包内业务表按 `xxx.py 壳 + xxx_base + xxx_inc + xxx_del` 组织。实测 `common_item_data` 家族：壳 entry 1765（FID `1232F498D07A0EBB`，815B）内容可打印字符串直接含 `MergedTableData`、`common_item_data_base`、`common_item_data_inc`、`common_item_data_del` 与版本 hash `aaebe9f972c76ecd`——**815B 不是"占位"，是运行时合并加载器代码（壳），不是表体**；真表是 `_base` entry 18005（35,948 行完整快照，见 27.13）；`_inc` entry 5292 = x{ 表体 1,911B 约几十行增量（配 legacy `{` 文字池 entry 2592）；`_del` entry 16447 = 147B 删除 key 集（1~2 个 key，无明文数字 token，marshal 编码未解）。语义：**当前表 = base ∪ inc − del**，每表带版本 hash 供校验/灰度。
  - 同款家族普适：`fashion_data`、`all_equips_data` 均为 `壳 + _base(+_base_chs) + _inc(+_inc_chs) + _del + _chs + kj1/yk 分支变体`；热更包内 `_base` 一律是完整新快照（非 diff），因此 root 8-27 与 BA8 9-01 同名表直接 key diff 即可得热更内容（weapon_skin_data 121→125 = +4 即此法）。全包共 798 个唯一 cdata 模块 stem。
- **运行时合并模型（验证度分级）**：目录结构/壳内容/表族完整性 = 已验证；"启动校验 client_doc 补丁点序列 → Documents 新包优先于根目录同名包加载 → MergedTableData 按 file_id 找 base/inc/del 合成当前表；资源以根 res.npk 为底 + Documents/res wpk 增量按 idx 覆盖" = 静态证据支持但未做进程级动态验证的推断；`_inc` 的服务端灰度下发路径 = 未验证。
- **对拆包工作的意义**：① BA8 当前态 = base+inc+del 合并结果；当 `_inc` 明显变大时必须先解 inc/del 再谈当前表（当前 inc 仅几十行、del 1~2 key，读 `_base` 等价读当前表，前提成立）；② `common_item_data_base` 家族成为通用名称正源（gift/兑换/商店/奖池均可同表 join，exchange 下一轮升级用）；③ "热更新增"判据（同名表 key diff）继续有效，因双包均带完整 base。
- 残留疑点：`common_item_data_del` 中被删 key 的精确值（147B，marshal 编码未解）；`_inc` 是否在运行期被服务端追加（静态不可见）；`gres` 35 个 gpk 与 `res\*.wpk` 的资源归属边界未逐一验证。

### 27.15 SFX 全量化：0x07 行尾容器解码 + 126 行皮肤表 + 348 条 SFX（2026-09-03）

- **解码器升级（wiki 侧 `tools/bindict_provenance.py`）**：行尾除已知 `0x27`（纯 ULEB 组）与 `0x36`（映射）外，实测存在 **`0x07` 类型化容器**：`[07][uleb 元素数][(scalar_type u8)(typed value)×n]`，元素类型支持 01/04=uleb、03=bool、05=CHS（记录 value_chs_slot provenance）、0b=jump、11=zigzag、12=f32、22=f64；`0x27` 与 `0x07` 可在行尾交替。已在解码器增加支持，行边界校验不变（解不全仍 unbound，不猜）。用户指出"BT 解码器不行就优化新增"后实施，未改动只读工具库（01拆包器本体）。
- **SFX 全量 348 行**：`weapon_skin_sfx_function_data`（BA8 018238+009096）原只解出 321 行、27 条 96 变体行（schema 14、`07` 尾巴）被当 inline list variant 丢弃；升级后 **348 行全解、unbound=0**。75 个皮肤有 SFX 不变；行尾 07 容器含 utility 模型路径（utility_p_XXXX.gim）+ f64 参数（0.4/0.2 缩放类）+ effect 路径，作为 inline_groups 原始 framing 保留在子项数据中（不赋予业务语义）。
- **连带发现：weapon_skin_data 也漏 1 行**——同一 07 尾巴问题使 125→**126 行**（BA8 独有 `11101831`：战神烈火剑第二时限变体，model_path=skin_2003_030，sale_ts=1788364800≈9-02，道具表无行→"战神烈火剑（时限版）"，v3-2 参考表无行→reference_fields.source_kind=no_user_reference_row）。**root 8-27 用升级后解码器复核仍 121 行、unbound=0，基线可信**；BA8 独有 4→5（1110181/2/3/11101811/11101831）。分类现为 111 主 + **15 变体** + 3 预告；嵌套变体 15（11 有道具行正式名 + 4 无行：11100061/11101341/11101681/11101831）。
- 图鉴统计新基线：`111 main / 15 variants / 126 total / 3 previews / 348 SFX / 75 sfx skins / sfx named rows 22 / named skins 9`。CSV 扁平 129 行。manifest 仍 5 board / 7520 顶层记录。SFX 子项新增 `sfx_type_label`（3=命中特效/4=击败特效/6=弹道特效/7=音效 等中文标签），页面显示中文类型。
- 验证：定向 3/3 GREEN；全套 unittest **22/22 PASS**（gift 表 2 个 unresolved key 132721/135958 非 07 型不受影响）；正式重建 + HTTP 实测 `LIVE_HTTP_SFX_FULL_OK rows=126 variants=15 sfx=348 named=22 named_skins=9 csv_entities=129`。原始包只读未写。
- **命名现状（关键事实）**：`sfx_function_data` 整表只有 **22 行带 sfx_name 中文文本，覆盖 9 个皮肤**（1110009/1110151/1110152/1110154/1110168/1110178/1110181/1110182/1110183——即命名集中在"有专属特效名"的行，8-29 新增皮肤 1110181/2/3 全带名）。其余 326 行是纯配置行（表本身无名字），图鉴显示"未命名 SFX 配置"。若需为更多皮肤补特效名，正源候选是 `weapon_skin_effect_show_data`（战斗表现表，段=皮肤、段内含特效名文本）与 `weapon_skin_sound_data_for_query`（175+ 行、390 unbound 需另解）等；是否扩展为命名层待用户拍板。

### 27.16 装配链与 effect_show UI 短名层：定位链打通（2026-09-03 晚）

**背景**：用户提供 7 张实机截图（提前测试服）要求彻底打通"皮肤→战斗表现名"定位链。经历：es 行 key=skin 假说被用户实验 A/B 否决（帝皇裁决 UI≠es 178 行内容；极狐破坏者 UI≠es 121 行内容）→ 排除轮空/中间表/版本差（现场 SHA 复核：工作副本 8 个关键 entry 与 `E:\mrzh\Documents\script.py314.lc.npk` 解码 **全部 SAME**；fo_version/client_ver/local_finfo 均未变 → **用户端就是 BA8**）→ 最终在 weapon_skin_data 行内找到装配 jump 字段。

**装配链正解（图鉴 SFX 命名的事实基础）**：
- `weapon_skin_data` 行内字段：`hit_sfx_functions`(命中)/`trace_functions`(弹道)/`extension_defeat_functions`(击败)/`jump_word_functions`(跳字)/`sound_functions`(音效)/`aim_cross_functions`(准星)/`link_nucleus`(核芯联动)/`idle_anim`/`play_anim_moudle`/`switch_weapon`/`nucleus_replace_ids` 等 = **jump:NNNN** → blob 内装配块。
- 装配块（0x27 组流）引用 **sfx_function row key（1120xxx）候选池**（每块 42-67 行、跨皮肤混合=武器族候选池，UI 按类目各取一行）。**验证锚点**：skin 159 hit 块首行 1120245=冰晶溅射=用户 UI 一阶 ✓；skin 161 hit 块首行 1120247=沙漠流光=三阶 UI ✓；skin 1110012 hit 块首行 1120019=青龙噬火=腾云 UI ✓。
- sfx rows 同 key 的 item 1120xxx 名 = **装配名**（BA8 可回放 CHS，333/348 已入图鉴）。沙海 1/2 阶（159/160）=冰晶溅射组、3 阶（161）=沙漠流光组与用户实机形态分组**完全一致**（159/160 行同内容=共用配置，161 独立）。

**effect_show 表结构正解**（推翻此前多次错误假设）：
- base（BA8 003671/FID 260B9B322A9D72D2）：x{ body（count 238）→ blob（de=3836）→ tail = `76 01 0b` + u8 bucket 59 + 59×8B 节点（hash key→off，**off 全部指向 tail 内**=自索引层，parse_index 从节点读出的 1110xxx 假 key 系误读）→ 节点区后 292B **uleb 流 = (行 key, 行 offset)×59**（真实行表；行 key 语义≠skin_id，用户锚点证实错位且无统一偏移）。
- 行内容 = 类目块序列：`[类别词/图标词]* + 特效名 + 字段词`（类目：命中效果/攻击弹道/击败特效/伤害跳字/战斗音效/攻击准星/核芯联动/特殊交互/蓄力效果/切枪动画/收刀入鞘…）。es 池（019852，238 槽）= **特效短名总池**（含疾影贯心/焚罪裁决/沙漠流光等；item 池只有装配名长名，青龙噬火两池分布不对称）。
- 56def(旧) 与 BA8 的 es 表字节级相同（8-29→9-01 未变）。

**UI 短名层实现（27.16 交付）**：图鉴主卡新增 `ui_combat_short_names`（类目=名 列表）+ `ui_short_name_es_key` + `ui_short_name_match`（`user_anchor_20260903`=7 条用户实机锚点 / `content_match`=装配名集∩es 行名集最大唯一 / `none`）。配对 30/114 顶层（7 锚点+23 内容匹配）。CSV 新增两列（UI战斗表现短名（es行）/UI短名匹配方式）。测试更新断言锚点类目（疾影枪命中=疾影贯心等）。全套 22/22 PASS；HTTP 实测一致。
- **已知局限（诚实标注）**：① es 行含混合内容（如行 1110184 含金乌驭光/赤焰灼痕 等非火刑名——锚点行只取命中/弹道类目可信，其余类目可能属他皮肤）；② es 行 key↔skin 映射机制仍未静态解明（新老皮肤错位方向相反），短名层靠锚点+内容匹配而非行级正式绑定；③ 腾云经内容匹配挂到 es 1110090（命中=碧火焚身≠用户 UI 青龙噬火）——青龙噬火不在 es 池，UI 该皮肤走 item 装配名，内容匹配行仅供参考。
- **下一步候选**：es 行 key 机制深挖需更多实机锚点（每皮肤 UI 面板截图/报命中名即可登记）；或先以当前 30 皮肤短名层验收。

### 27.17 effect_show 通用定位链：0x76 hash 索引同源实锤（2026-09-03 深夜）

- **实锤**：`weapon_skin_data` 与 `effect_show` 两表 0x76 尾部索引节点 key **完全同源**（同一 hash(skin_id)；抽查极狐破坏者 121 两表节点 hash 均=3016979616，共 126 vs 59 节点、交集 56）。→ **skin→es 行的通用索引层成立**：skin_id 经 hash 在 es 索引定位节点，节点 off 精确指向尾部流内行 key 起点（59/59 命中），流 (行key, 行off) 对给出 es 行。
- 重建器新增 `decode_es_registry()`（payload→hash2skin→注册行流 key），主卡注入 `es_registry_row_key`（50 皮肤有 es 注册行）；配对优先级改为 user_anchor > hash_registry_ui（注册行内容∩装配名≥2）> content_match(≥2) > hash_registry_row（低置信兜底）。
- **关键认知**：es 注册行是皮肤登记时的行；改名/升格皮肤（沙海类：注册行=玉泽流华旧组）UI 显示行在相邻行——注册行≠UI 行，故注册行只作归属审计+候选层，UI 显示名仍以锚点（9 条，面板逐类目全对，含极狐破坏者 6 类）/content 为准。es 池文本对部分皮肤（疾影贯心/焚罪裁决/不屈防御/极光开阖）是 BA8 内唯一名源（item/sfx/behavior 池均无）→ es 不是纯内部表。
- 已排除的映射源：`weapon_skin_sound_data_for_query`（=音效路径查询表，无名字）、`skin_2_sfx_function_map`/detail、`weapon_kind_to_skin_item_data`（非标准行式，未含名文本）。
- 验证：9 锚点面板逐类目精确（极狐破坏者=极狐之印/狐光锁定/游戏跳数/九尾光轨/骑士音爆/狐眸追击）；全套 22/22 PASS；registry 覆盖 50 皮肤。极光盾（1110197）无 es hash 节点（es 未索引）但 es 行含其 UI 内容（不屈防御/护臂开合=极光开阖，护臂专属类目词已入解析集）。

### 27.18 纯链判卷/解码自查/kind 注册清单表（2026-09-03 深夜续）

- **纯定位链判卷 1/9**：导出纯链版特效表（`03拆包产物\武器皮肤_战斗表现特效表_纯定位链版_20260903.csv`，无锚点干扰，仅 hash 注册行）→ 用 9 个用户实机锚点判卷仅极狐破坏者命中。注册行≠UI 行实锤：沙海 1 阶注册行=玉泽流华组（旧配置），UI=冰晶溅射组（当前）；云上铃注册行=贴芯印记组（差 2 行）；8/9 差在"多代配置行并存 + 运行时取当前行（客户端/服务端逻辑，静态不可推）"。
- **解码器自查（无 bug）**：① es 池 238 槽完整（行内无 238+ 越界文本引用，1286=0x86 子块标记非池引用）；② item 回放正确（1120248 name='占位' 属实）；③ **冰沙击灭/霜晶掠影/寒晶碎魄/碎玉沉鸣/弦月凝光 在 item 全表无任何行引用**（文本仅在 es 池）→ UI 名确引用 es 体系文本；④ 鎏金锐魄用户实机=无特效 → 图鉴空列=真实（老皮肤本无战斗表现），非缺数据。
- **新表发现：`weapon_kind_to_skin_item_data`（007005，1205B）= kind→皮肤注册清单**：10 个 27 组，组内皮肤 ID 列表，**覆盖全部 111 主皮肤**（如冷兵器组 28、金乌 142/143/144 组 8、沙海 159/160/161+腾云+云上铃 组 15）。这是全皮肤注册序候选表——es 行序/装配块选行规则的下一步对照源（未验证与 es 行关系）。
- 表名全量扫描落盘：`03拆包产物\BA8_表名清单_20260903.json`（5016 表名，含 weapon_kind_to_nucleus_ids/entry_ids 容器碎片线索 014020/015752=oversea 容器）。
- 工具链状态：canonical 22/22 PASS；9 锚点面板逐类目精确；registry 覆盖 50 皮肤（es_registry_row_key）；表 v2（锚点版）与纯链版已分列，供对照。

### 27.19 kind 清单排除 + 静态定位极限定性（2026-09-03 深夜结）

- **weapon_kind_to_skin_item_data（007005）验证排除**：10 组 111 皮肤全覆盖，但 es 行物理序/出现序与 kind 序两种对照均 False（es 序≈皮肤 ID 降序+热更前插；kind 序=kind 枚举分组序）→ 该表=武器类型页 UI 列表，非 es 注册序源。
- **静态侧排查全景收官**（全部无果）：sfx 装配行（4 例对，击败/音效等无名）、es hash 注册行（只对无改名史皮肤）、行序秩关系、sound_for_query（音效路径）、kind 清单、es 行 key hash（同源≠skin 直连）、表名全扫 5016。
- **最终定性**：es 行=按热更追加的档案行（皮肤登记时配置快照）；改名/升格后 UI 显示行=运行时选择（客户端逻辑/服务端下发），静态包内不可推。静态定位上限=登记行（极狐类无改名史皮肤）；UI 当前名=用户实机锚点唯一可靠源。
- 图鉴状态（终态）：9 锚点面板逐类目精确 + content 22 + 注册行 50（审计）+ sfx 回退；鎏金类无特效=空列（用户实机确认）；长字描述行=待锚皮肤（帝皇裁决等），随截图固化递减。

### 27.20 mrzh 全量扫 + script.npk(2024-12) 加密包结论（2026-09-03 收）

- **mrzh 全目录盘点**：脚本/表类包仅 3 个（BA8A 9-01 已全解 / root 8-27 已解=es 同 / script.npk 2024-12 老包）；其余=资源包（gres/ui/character 数百 GB）+客户端程序+configs（纯设置）+补丁缓存（已清空，multi_cloud 空 lock）；Documents/configs=聊天/画质等无表；client_doc@1_* 补丁点=0 字节 mail_content。
- **script.npk（229MB）结构判定：全加密容器**——无魔数、头 64B=双 hash（fe0e…+2f72…）、3422 个 x{ 命中=加密流随机字节巧合、3530 个 tI 路径全乱码（len 字段乱值）、无明文表名；无解密密钥无法解。其潜在价值仅"改名轨迹证明"（如沙海 1 阶 2024 年 es 行=玉泽流华 or 冰晶溅射），不影响现行结论。
- **静态侧最终状态**（27.19 定论不变）：es 行=热更档案行；UI 显示行=运行时选择（客户端/服务端），静态不可推；锚点=唯一可靠源。图鉴 9 锚点逐类目精确+content 22+注册行 50 审计+鎏金类无特效空列（实机确认）。

### 27.21 图鉴序键定位 + 排序控件 + 锚点扩至 11 + 类目级覆盖（2026-09-03）

- **游戏图鉴默认序键= sale_ts 降序 + 同日组内 skin_id 降序**（用户正式服图鉴截图验证 9/9：197极光盾/178帝皇/177极光剑/167粉息/180西瓜脆脆冰/176晶棘/175水晶玫瑰/179往哪看呢/172缄默；排除 sale≥2026-09-03 的 181/182/183=正式服未上线二期）。sale_ts/priority/charm/kind 清单均验证：仅 sale_ts+id 组合命中。sale_ts 已注入主卡+变体卡；board.html 新增排序切换（图鉴序列默认/皮肤ID升序）+卡片"上架月-日"徽标。多形态皮肤（173/174 等）游戏图鉴合并 1 格，本图鉴保留全形态（每形态战斗表现不同）。
- **锚点扩至 11 皮肤**：+战神烈火剑 183（命中=战神断岳/挥砍=烈火长虹，es 行 1110126，截图 2026-09-03）+帝皇裁决 178（命中=天罚坠光/弹道=圣裁破军，es 行 1110179）。四字短名均在 es 池（静态包内有），但 1110179 为**混合档案行**（弹道块含极光剑的极光贯日）→ 新增 **UI_ANCHOR_CAT_OVERRIDES 类目级覆盖**机制（es 行锚定 + 类目显示名覆盖，逐类目精确）。
- **近战类目归一下沉到数据层**：es 行类目词"攻击弹道"在近战（冷兵器/护臂）统一转"挥砍特效"（战神烈火剑/阿赖耶识不再重复/错位行）。
- 图鉴当前：11 锚点面板逐类目精确（user_anchor_20260903）、content_match 22、注册行审计 50（es_registry_row_key）、鎏金类无特效空列（用户实机确认）；canonical 22/22 全绿；排序=游戏图鉴序（sale_ts 键，正式服截图验证）。

### 27.22 行为资源并入主卡 + shadcn 视觉重构（2026-09-03 收尾）

- **行为资源并入**：weapon_skin_behavior_res_data（79 行，key=主皮肤）此前仅 preview 3 行接入；现 make_main_item 接 behavior_by_skin → **78 条目带行为资源**（开火 fire_sfx_path/命中 hit_sfx_path/弹道 trajectory_sfx_path 等资源路径 + skin_replace_anims 替换动作 id，含 text provenance）。行为行字段全部 .sfx 路径（实证：疾影枪 7 条资源齐）。
- **shadcn 风格视觉重构**：内联 <style> 外置为 `board_shadcn.css`（zinc 中性色板+单一紫 accent、卡片圆角 14px 细边框轻阴影、标签 pill 化去彩边、战斗面板无条纹 hover 细线、节标题 accent 竖条、focus ring、5→4→3→2→1 响应式栅格）。全部 class 名与 JS 不变。
- 服务端线索排除：grecord=录像工具（log 空）、Documents/db=着色器缓存——客户端不落服务端配置数据。
- 状态：11 锚点面板逐类目精确 + content 22 + 行为资源 78 + 图鉴序排序（sale_ts 键）+ 筛选（品级/武器类型/联动IP）+ 排序切换（图鉴序列/皮肤ID）；canonical 22/22；视觉用户验收通过（"先这样吧，还可以"）。

### 27.23 正式服新包验证：两包同表（2026-09-03 晚）

- 正式服客户端（E:\LifeAfter\Documents\script.py314.lc.npk，9-03 20:36，366MB，45687 entries，SHA 79c0d06f…）用拆包器 FID 直查：**weapon_skin_data/es/sfx_function/common_item/behavior 五表 FID 与 BA8 完全相同**（内容指纹一致）→ 正式服二期上线数据=BA8（测试服 9-01）同表，无版本差。
- 推论：① 11 锚点/78 行为资源/图鉴序对正式服同样成立（可靠性确认）；② 沙海类"注册行≠UI"差异在两包同存=客户端运行时取行逻辑（非表差异）最终确认；③ 无新 es 行可挖，锚点体系闭环。
- 拆包器适配：LiveNpkReader 可读正式服包索引（45687）；npk_reader.scan_package 对新包路径解析不全（222/0）——FID 直查是可靠路径。

### 27.24 wiki 板块归位 + 全量业务链搭建启动（2026-09-03 深夜）

- **武器皮肤图鉴归位二、时装类 / （7）武器皮肤**：tools category 修改+wiki.html 注入位（data-wiki-category）+manifest 114 条（commit 6b3823c）。图鉴卡更新：正式名→特效名→UI短名→行为资源定位链已建立（11 实机锚点精确）。
- **修正映射（用户纠正：核芯图鉴≠限定核芯研制）**：nucleus（核芯图鉴 108=装备战力系统）归 **三、战力类 /（2）异变核芯**；限定核芯研制=四、奖池（3）活动卡（待建）。已发布 5 板全就位；未发布板（nucleus/fashion_*/weapon_attrs/vehicle/lottery_*/new_textures/shop_static）归属已记录，搭建完成发布时按映射归位，不乱移。
- **全量搭建路线（todo 已立）**：①道具总表层全道具总表（item_id 键）→②时装类（头饰/套装/发饰/面饰/投影/荧光棒行级复证）→③战力类（核芯同快照链/芯片/无人机）→④奖池（selector/consumer 闭环）→⑤exchange（搁置）。
- 正式服 9-03 新包两包同表验证入档（27.23）；canonical 22/22 全绿。

### 27.25 全量搭建①道具总表发布：common_item 35986 行全量文字表（2026-09-03 深夜续）

- **新发布板块 common_item_text_sources（一、道具总表 /（2）全道具总表）**：BA8 common_item_data_base（entry 18005/FID B42760CCA41DBC25，897696B，flag 0）+ CHS（entry 23928/EF3A8474A5E5F7A4）FID 直查解码，35986 行全量（decode_table_rows_with_chs_slots）。
- **行级结论**：35986 行 **name 100%**（0 缺失）、desc 35163（97.7%）、icon 路径文本 35754（99.4%，ui/item_icon/icon_*）；**行 key 与 id 字段 100% 一致（0 差异）→ item_id 键无歧义**；name/desc/icon 均为 0x05+CHS field/value 槽可回放（name 槽位 179~55139 范围）。低段 key 行（7000 资源/7002 冷兵器等分类名行）按原文字呈现不附加业务归类。
- **1948 行 unbound（schema 40206 inline list variant，含 7001/7005/900xxx/1224xxx 等散布 key）完整保留于 stats.unresolved_keys，不静默丢弃不猜名**。与 gift 板（5443+2）互为补充：同 key 不同表可能异义（130000 在 gift=建筑补给箱、在 common_item=道具1+icon_120062 错位图标 → 文字表如实呈现，不解释业务）。
- **UI 配套**：board.html 新增**大表检索模式**（items≥15000 触发）：预构建轻量 _hay 索引（id/item_id/name/desc/icon 小写拼接），无关键字只展示前 200 条提示检索、命中>800 提示精确化；紧凑卡渲染（名称+item_id+描述+图标路径）。既有 5 板（最大 5443）路径零改动。wiki.html（2）卡注入 data-wiki-category。
- 验证：定向测试（重导全表断言 35986/1948/35163/35754、7000 资源 desc/icon、1110001 鎏金锐魄正式名、row key==id 0 差异）；build_wiki 6 板 43506 条；node 加载 65MB js 全量解析 + 抽样命中（鎏金锐魄/沙海月鸣）；全套 unittest **23/23 OK**（publication_gate 期望列表更新为 6 板）；HTTP 8765 验收通过。commit ffefed5。
- 本板意义：**全道具 item_id→正式名/desc/icon 同快照正源已闭环**，后续时装/战力/奖池/兑换板块的行级命名 join 全部可用此表（不再依赖旧名表/启发式）。

### 27.26 全量搭建②时装类行级槽位复证：时装衣柜发布（2026-09-03 深夜续）

- **新发布板块 fashion_wardrobe_slots（二、时装类 /（1）头饰与衣服套装）1280 条**：BA8 时装外观表（entry 22570/FID E1645717C83FC968 + CHS 20834/D016140651FEAB34，19264 行）用 decode_table_rows_with_chs_slots 行级解码 + 值分类法挑显示名（25.1 终判：19 schema_ref 字段名跨行错位不可信，charm_value 等槽位混装，只能按值特征分类）。7483 行命中显示名形态（名/名-部件/名-N天），聚合 (base,part) 成 1280 条：整套737/衣服275/头饰267/套装1。
- **行级契约补全（旧 fashion_wardrobe 1093 被隔离的缺口）**：每条=代表行（永久行优先，否则 value_slot 最小变体行）row key + 该行显示名文本的 field/value CHS 槽位（**text_provenance.name.text==name 100% 一致，0 差异**）；聚合组内全部变体行保留于 variants[]（row_key/text/槽位/duration/schema）+ all_row_keys + duration_days/has_permanent/schema_refs。NPC 噪声滤除（25.2 质检）。part 由显示名后缀解析并显式注明"part 槽为模型路径不可用，不猜"。
- **诚实边界**：帝皇铠甲/帝皇战翼在本表仅时限后缀行（has_permanent=false，variant 列出 1/3/5/7/14/30 天全部行），本体 model 归属属 25.4 双源结论范围、本板不越界宣称；描述槽跨行错位（25.1）留空标 desc_note，待 i18n 桥接。铠甲联动锚点 5/5 命中（刑天铠甲/刑天召唤器/帝皇战翼/帝皇铠甲/飞影召唤器）。
- UI：wiki.html 时装类（1）（2）卡合并为"（1）头饰 /（2）套装＆衣服"注入位（data-wiki-category），（3）发饰～（6）荧光棒维持待采集；board.html FIXED 增 variants/all_row_keys/schema_refs 防 kv 刷屏。
- 验证：定向测试（槽文本≡name、variants 槽位齐全、锚点 5/5、NPC 0、契约错误 0）；build_wiki **7 板块 44786 条**；全套 unittest **24/24 OK**（gate 期望列表更新）；HTTP 8765 board 页 200；node 加载 js 全量解析 OK。commit 待查。
- 意义：**时装文字层行级定位链闭环**（旧 1093 因无 row key/槽位被隔离，本轮补全正式发布）；②剩余：（3）发饰（5）投影（6）荧光棒待定位专表或部位字段、（4）面饰待 legacy 0x73 行解码（25.5 待办②）、描述待 i18n（25.5 待办①，未定位文案表）。

### 27.27 时装"全量"措辞纠正：内嵌名层 vs 文案 ID 层（2026-09-03，用户质疑驱动）

- **用户质疑"时装总表绝对不全"→ 证实成立**。量化：时装外观表（entry 22570）19260 行中仅 ~7539 行（39%）内嵌中文裸名（1280 条目聚合源）；**11721 行（61%）name 槽=整数文案 ID**（0x01，如 98076/98032/91220274，schema 433/6467/6845 等全有），正式名在 i18n 文案表（25.5 待办①，common_item_data BA 仅 815B loader 未定位）。
- 内嵌名层也不纯：部分名字藏在描述句前缀（"福虎贺岁典藏-头饰(永久款)。#r炮竹声里辞旧岁…"整串在 charm_value 槽）；扩展格式（（N天）/（永久款）/半角括号/空格）全表仅 +45 唯一文本（B站/CC新年限定等），base 数不变（1084）→ 缺口大头=文案 ID 层，非格式。
- **处置**：fashion_wardrobe_slots 板名降级为"时装外观表（内嵌中文名层）"，wiki.html 卡位标注"内嵌名层（非全量）"，policy reason 写明 61% 边界；**文案表桥接前不宣称全量**。测试期望不变（结构断言），build 7 板 44786 条不变。
- 下步（治本，仍开放）：定位 name 整数文案 ID→中文 的 i18n 文案表（可能是独立 entry 的 key→text 字典），打通后时装/面饰/武器 desc 与 61% 缺名行一次补齐。

### 27.28 时装名解析器补入解码器工具库（用户质疑+明确指示：解码器缺功能则补）

- **用户质疑时装总表不全 → 根因分三层**：①名字真实形态远超早期假设（#c 颜色码包裹、名。#r描述 富文本、-N天 时限、[（(]永久款/N天[)）] 款型、名 空格 色系尾、双括号脏数据），原 NAME_RE 整串锚定大量漏判；②~46% 行（8814/19260）经富文本解析可命名，行级唯一 (base,part) 条目 **1497**、base **1182**（旧 1280 为漏判后数字）；③剩余 54% 行待定性（配置行 vs 真缺名行 vs int 文案 ID 行）。
- **解码器（05_BinDict解码器/fashion_display_name_parser.py v2，已补入工具库）**：strip_rich（剥 #c..#n/#r、句号截断取名字段）→ parse_display（部件 PARTS 白名单/时限/款型/空格色尾/双括号容错，拒词=硬信号+desc 模板开头+纯色名）→ best_name_in_row（行级多文本取最优：部件>时限>空格）。20+ 实证形态样例全过（福虎贺岁典藏-头饰(永久款)。#r…、B站新年限定 - 衣服（30天）、假面骑士 空我-14天、三载之伴-衣服((30天)、#cffc8a4天枢龙将#n系列科技装置 等）。
- 数字快照：named rows 8814 (45.8%) / entries 1497 / base 1182；part kind 4635 / plain 4134 / spaced 40。
- **待办**：①剩余 54% 行定性（含 schema 6467/6845 模型行、荧光棒 desc 行、int name 行），对照实机衣柜总数；②时装板用新解析器重建（1497 条目层）；③wiki tools/lib_fashion 是否引此工具库模块（去重避免双实现）。

### 27.29 时装表内挖尽确认 + 工具库富文本解析器全量重建（2026-09-04 凌晨）

- **解码器补功能（用户指示）**：新增 `01拆包器本体/工具库/05_BinDict解码器/fashion_display_name_parser.py` v2——strip_rich（#c..#n/#r 剥离+句号/#r 截断取名字段）→ parse_display（部件 PARTS 白名单/-N天/（永久款|N天|时限|日款）括号款型/空格色系尾/双括号脏数据容错/`・`字符）→ best_name_in_row。20+ 实证形态样例（福虎贺岁典藏-头饰(永久款)。#r…、B站新年限定 - 衣服（30天）、假面骑士 空我-14天、三载之伴-衣服((30天)、#cffc8a4天枢龙将#n系列科技装置、战斗服・EVA初号机版-14天 等）42/42 断言全过。
- **定性结论（回答"能否全量"）**：时装外观表 19260 行 → **9619 含名行（49.9%）按 (base,part,flavor) 聚合 1489 条目（整套795/衣服374/头饰315/套装5）**；未命名 9641 行分类：A 无中文纯配置 3095（模型/路径行）/ B 仅 desc 句 655 / C 有中文候选被拒 5978——**C 类复查 0 新名可挖**（"潜龙在渊/魔术障眼法/花神佑世人"等均为跨行复用 desc 句，非名字）。**表内文字层已挖尽**；int name（98076 等）行名字在外部文案表（fashion_id_2_season_id 等 BA 仅 176B 壳，真表=xxx_base 全快照未定位），不属于本表 CHS 内。
- **wiki 侧**：rebuild_fashion_wardrobe_slots.py 弃用本地正则，import 工具库解析器（sys.path 加 05_BinDict解码器）；聚合键含 flavor（两小无猜 晨光翠茑 独立条目）；text_provenance.name 增 raw_slot_text（槽内原文审计）+rule；meta notes 改"表内已挖尽"。板 1280→**1489 条**，policy/wiki.html 文案同步。验证：24/24 unittest（期望更新 1489/9619/parts）；build 7 板 44995 条；锚点刑天/帝皇/战翼/召唤器/飞影 5/5；text≡name 0 差异；NPC 0；EVA・ 捕获。commit 059c9c1。
- **如实边界**：1489 = 时装表 CHS 内嵌文字层全部；游戏内"全量时装"若含外部文案 ID 行（int name）需 i18n 文案表定位（壳表 fashion_id_2_season_id→真表 xxx_base 未定位，开放）；desc 仍未接（描述槽跨行错位，25.1）。

### 27.30 时装 i18n 攻坚终判：无外部文案表，"int name"系错位字段（2026-09-04）

- **攻坚目标**：定位 25.5 待办①"name 整数文案 ID→i18n 文案表"，期望补时装 61% 缺名行。**结论：该待办前提不成立，正式作废**。
- **证据链（BA8 全表侦查）**：
  1. int name 值域分布 = 全行 19260 都带 0x01 name（值 90001~91222291 横跨 common_item 全域）；逐行 int 值**每行唯一**（19257 组≈行数）→ 是行级 ID 不是分组键。
  2. int 与 common_item 家具 ID 大量重合（95% 命中）但**语义 100% 不一致**（6154/6154：int=98076→common_item"积分纸箱2"vs 行内真名"福虎贺岁典藏-头饰(永久款)"）→ 纯 ID 区间重叠巧合，字段名 name 系错位（25.1 早已记录本表字段名不可信，此为其又一例证）。
  3. 9641 无内嵌名行定性：5787 共享 model 于已命名行（同外观模型/图标变体配置，无需名字）；3854 不共享者文本全为 desc 句/模型码/路径（"潜龙在渊"句横跨 2079 行为龙年主题通用 desc，非缺名线索）→ **表内确实无更多名字可挖**（与 27.29"0 新名"互证）。
  4. fashion_id_2_season_id / store_v2_fashion_type_ / fashion_data 在 BA 均仅 176B py 壳（壳模式≠common_item 的 815B loader 模式，真表不在 BA 快照内）；FashionCharmMagazineC/FashionCollectC/FashionC/FashionColorPlat 均为 Python 组件代码非数据表。
- **结论**：时装外观表（entry 22570）**全部名字都在表内 CHS**，无外部 i18n 层；已发布的 1489 条目（整套795/衣服374/头饰315/套装5）= 本表文字层全量。游戏内可见的"更多时装条目"若存在，来自①染色方案（change_color 系统，未定位专表）②其他外观类别（发饰/面饰/投影/荧光棒，wiki 卡位待采集）③其他模块表——均不在本表职责范围。
- 下步建议：1489 已发布可用；若用户以游戏衣柜数为准质疑覆盖，需实机对照截图或定位染色方案表（新侦查线），不再重复"找文案表"。

### 27.31 时装全量名册卡点终判 + 卡点登记（2026-09-04，用户指示挂卡点）

- **卡点终判（挂 BLOCKED）**：①时装 name/desc 列=int 文案 ID（主 schema 270688 列级 100% 稳定 0x01）；文案表 BA 仅 176B 壳（fashion_id_2_season_id 等全壳）、**正式服 45687-entry 新包不存在壳 FID**→服务端专属客户端不可得，列直读路线物理关闭。②武器皮肤 UI 特效名匹配=27.19 定论（静态上限已到，锚点唯一源）。两条已登记 C 区 BLOCKED。
- **本轮侦查副产品（均有 probe 实证）**：CHS 池=字段名区(前~350 ASCII，含 b_f_3605_1 型 socket 字段名)+值区混排；schema 270688（主，76 字段）字段名全 ASCII 正常、name/desc/part/charm_value 槽位定义正确→**字段名解析无误**；schema 433（131 字段）4/131 字段名 slot 越界引用值区文本（描述句当字段名）→次要 schema 的 0x05 列值仍有错位风险（16.4 宽 schema 议题内，非本轮主线）。int 与 common_item 95% 命中=ID 区间基数巧合（common_item 覆盖 97.7% 空间），非引用。
- **遗留（未跑完，登记在案）**：解析器 v3 desc 防护（_SENTENCE_WORDS 长短语表+句首模式+纯名长度/物品词尾三层）词表已加，**全表重建/测试/发布未执行**；当前发布版 1489 条仍含 ~58 条 desc 句子混名（用户抓出的"也许可以抵挡…侵害"类），需重跑 rebuild 清理后再提交。fashion_wardrobe_slots 发布语义=时装表内嵌名层，1489 条为客户端可达上限。

### 27.32 ②b 面饰侦查：0x73 结构定性 + base 未定位（2026-09-04 续）

- **表身份**：面饰旧板数据源 10816/9169 = `player_module_appear_data_chs.py` / `_for_export_chs.py`（0x73 尾 string_pool 标识实证）——**纯 CHS 池文件，无行区**（表头 38B + { 池 + 110B 模块尾）。
- **池结构**：2031 条（10816）+1083 条（9169）；池前 1-14 条=字段名（desc/hide_in_bag/icon/level/model_paths/model_socket/name/part/fashion_preview/female_icon/model_change_color_id/model_id/part_type/sort_key）；值区=面饰/挂饰 desc（`#f(5)名#n。可配戴在面部的面饰…` 富文本前缀名 125 个）+ **字典序裸名大块**（1128 个，一勺甜/一口甜心/刑天面甲/创世纪-冰霜/人鱼公主-白…，实为面饰名册主体）+ desc/名字交错小段（[37]desc+[38]不在线挂饰）。
- **卡点确认**：行级链（row→name/desc/icon/model/时限）需 base 行表 `player_module_appear_data`（无 _chs）；**BA8 清单仅收录两个 _chs entry，base 未定位**（乱码 key=池 ends 表无表名价值）。池内名字字典序排列暗示 base 行序可能同序（待验证）。
- **待续**：①全包扫 flag=2 pyc 找引用 player_module_appear_data 的加载代码（定位 base entry/FID）；②或验证"0x73 无独立 base、py 按 14 字段名硬编码序读池"假设；③面饰名册可与时装表 part=面饰 行对照（22570 无 -面饰 后缀行，面饰确在专表）。此线=②b 主体，暂挂（用户指示先做别的定位链）。

### 27.33 ③战力类侦查：BA8 无核芯/芯片/无人机主表体（2026-09-04）

- **nucleus 家族 BA8 定位结果**：全工作副本 25485 entry 尾标+字段名指纹扫描。nucleus_hd_conf_data（旧板主线研制正源）= 9 个 entry 全为 300B~1.8KB py stub（oversea 各服变体），**无表体**；nucleus_build_data kj1/kjxq CHS 池在（023314/005437，75KB，字段=attr_simple_desc/desc/icon_path/nucleus_attr_type/nucleus_base_buffs/nucleus_effect_name/rank_desc_ref/rank_to_desc/simple_desc/weapon_type）→ 池内容=**核芯效果文字**（【电震射击】#f(5)…#n 富文本 431 中文串），非核芯名册；候选 base 003932（519KB x{）解码失败（reserved≠0，非标准容器或错配）。
- **chip/drone**：choose_chip_conf_data/special_chip_lottery_hd_rule/drone_conf_data/drone_power_conf_data/drone_talent_* 等全为 ov於ersea stub（300B 级），**无表体**。
- **结论**：③战力类（核芯名册/芯片/无人机）的当期数据表体不在 BA8 Documents 热更包（同时装文案表模式：服务端下发/根包）。旧板 nucleus 108 条（8-31 根包 56def 快照）与 wiki 卡位（2）"待当前期复证"维持；**不得以旧快照冒充当期发布**。唯一当期文字资产=nucleus_build_data 效果文字池（可作核芯效果图鉴文字层素材，需行表配对才有条目语义，003932 配对未成）。
- ④奖池 selector/consumer 闭环不受影响（super_fashion 配置链已在 BA8 验证过：lottery_kaijia_panel_static 10 条已发布）。

### 27.34 ④奖池 selector/consumer 闭环尝试：BA8 静态侧零命中，闭环不可达（2026-09-04）

- **侦查**：BA8 工作副本 25485 entry 全量 grep 运行时选择器标识符——`current_shop/shop_selector/active_shop/exchange_shop_open/server_shop/lottery_selector/current_lottery/active_lottery/hd_selector` **全部 0 命中**（pyc 字符串区可被二进制 grep 命中，空=标识符不存在）。
- **结论**：④selector/consumer 闭环在 BA8 静态侧**不可达成**（与 C 区 BLOCKED 臻藏恢复三条件 19.3 一致；19.x 8-31 快照与 27.34 9-01 快照双证）。奖池静态可交付已达上限：lottery_kaijia_panel_static 10 条（铠甲再临面板，verified 锚点 key232）+ exchange_static_structure 1757 条（mapping/detail 静态）+ 帝皇铠甲 391762 五层闭环（C 区硬锚点）。卡位"待 selector 闭环/待 consumer"维持，禁止由面板推概率/当前启用。
- **路线全览（诚实状态）**：①道具总表 ✅ 发布（35986）；②时装 1489 发布（内嵌名层，**desc 混名清理未落地=27.31 遗留**）；②b 面饰卡点（base 未定位）；③战力类卡点（BA8 无表体）；④selector/consumer 静态不可达。**可落地的唯一遗留=时装 desc 句子防护全表重建**（下一步执行）。

### 27.35 时装 v3 desc 句子防护落地发布（2026-09-04，用户抓出"侵害句是描述"后修复）

- **修复**：fashion_display_name_parser v3 desc 防护接入 parse_display（此前仅常量未接线）：无部件形态三重判定——①句子特征词（_SENTENCE_WORDS 70+：也许可以/请不要/抵挡/侵害/呜啊/垂光织梦主题限定背包类靠句尾截断…）；②惊叹/句号截断残头（_desc_tail：'呜啊！吓你一跳！'→残头"呜啊"拒）；③纯名超长（>12 字且非物品词尾）拒。带部件真名豁免（武士意志-衣服/光影意志-头饰留）。
- **效果**：1489→**1428 条**（整套734/衣服374/头饰315/套装5）；被删 75 条（差集人工复核）**全部为 desc**——用户点名"也许可以抵挡…侵害"、为方舟纪念衫、将背包外形更改为X（18）、垂光织梦/福兔/永恒花冕/赤月终焉/青渊溯白主题限定背包、小小的脑袋疑惑、进击的巨人/金木研/定真嗣/哥斯拉联动 desc 等；**零真名误杀**（EVA・联动、2024新年纪念背包、CC定制时装、两小无猜 系列全保留）。desc 特征词残留 0。
- 验证：解析器自检 30+ 样例全过（10 desc 反例拒 + 7 真名豁免留）；全套 unittest 24/24（期望 1428/8878/parts 更新）；build 7 板 44934 条。commit 98102a9。
- 边界记录：'明日之后x哥斯拉大战金刚联动双肩背包'（名+功能 desc 同槽、无部件标记）随截断规则删除——若实机该背包正式名如此需人工补（商店短名机制），已可接受。

### 27.36 ②b 面饰行级槽位复证发布：fashion_face_slots 180 条（2026-09-04，②b 关闭）

- **base 行表定位**（27.32 卡点解除）：扫 25485 entry 尾 py 模块名 → `player_module_appear_data` base=**entry 003546**（FID 24947DBB72A943E5，0x73 壳+x{ 容器，60863B）+ CHS 010816（FID 6CD197C9670A961C）。for_export 变体=008243+009169。
- **行级解码**：1131 行 / unbound 0 / 单 schema 42。**name 0x05 100%、desc 0x05 100%**（此表 name 直接中文，非时装表 int 文案 ID）——列级可信，field names reliable。part_type 全 'face'；part 码 1（眼镜/面具 13）/2（747）/20001（371）；valid_days=1/3/5/7/14/30。
- **聚合 180 条目** = 去 -N天 时限后缀唯一名——与旧池扫 180 **完全一致** → 旧 fashion_face 名册正确性获行级证实（不再隔离重建，直接新板发布）。
- **新板 fashion_face_slots**：category「二、时装类 /（4）面饰」，每条目 name/desc/icon + text_provenance 双槽（field/value CHS slot）+ provenance.field_refs 机读链 + all_row_keys/variants（时限档全行）/has_permanent/duration_days。desc=主题级富文本（#f(5) 系列标题+描述，同主题共享池文本）按槽原样回放。
- 验证：25/25 unittest（新契约测试 test_rebuild_fashion_face_slots.py 断言 180/1131/0/刑天面甲 7 行全档/铠甲 desc/双槽）；ad-hoc 18/18（rebuild 复跑、锚点刑天/人鱼公主-白/粉红派对眼镜、manifest 8 板 45114、wiki.html 注入位）；build 8 板 45114 条。commit 4d08bf9。
- **25.5 待办②正式关闭**（面饰描述需解 legacy 0x73 行→base 自带 desc 列，无需 legacy 解码）。

### 27.37 时装类新增「背包·挂饰」附件板：fashion_bag_slots 63 条（2026-09-04）

- **动因（用户指示）**：时装类 wiki 需独立背包/挂饰分类——此前背包外观（2024新年纪念背包/五周年纪念背包/EVA 挎包等）被并入时装板「整套」无法按类检索。
- **构成**：从已发布时装板（fashion_wardrobe_slots，BA8 fashion_data 22570 同快照）筛展示名含 背包/挂件/挂饰/腰饰/披风/背饰/挎包/伞 → **63 条（62 背包 + 1 挎包·EVA）**；剔除 v3 仍漏网的 5 条 desc 句（可爱的水母啵啵/草莓甜心背包、使用全新科技打造的喷气背包、有纪念意义的背包、科技会全新背包产品——raw 为完整 desc 句且无部件标记）。时装表内挂件/腰饰/披风/伞后缀行=0（留待专表）。
- **行级链继承**：text_provenance（name/desc 槽位回放）/provenance（source_lock+source_entries+field_refs）/variants 原样继承时装板，未跨表裁决；金色 #c 主题限定/纪念背包（天枢龙将/塞壬之歌等）按真名保留。
- wiki.html 新增（8）背包·挂饰 独立 grid 注入位；policy 登记 published；build 9 板 45177 条。
- 验证：26/26 unittest（新契约测试 test_rebuild_fashion_bag_slots.py：63/62+1/锚点/desc 残句 5 不在/行级链 100%）；ad-hoc 18/18（rebuild、锚点、desc 剔除、manifest 9 板、注入位）；verification_evidence 已注册。

### 27.38 背包·挂饰板并入翅膀（2026-09-04，用户口径：翅膀属于背包）

- 时装板（fashion_data 22570）内 5 条翅膀外观（希望之翼/帝皇战翼-14天/晶澈之翼/皎月之翼/自由之翼，裸名+纯时限形态）此前归「整套」未被附件筛选抓到。
- rebuild_fashion_bag_slots.py ACC_WORDS 加 翅膀/翼；命中翼词条目 accessory_type=翅膀（细分）、accessory_bucket=背包（背饰槽，用户确认翅膀属于背包分类）。
- 板 63→68 条（62背包+1挎包EVA+5翅膀）；行级链原样继承时装板。
- 验证：26/26 unittest（新断言 68/62/1/5+翅膀锚点 5+bucket=背包）；ad-hoc 22/22；build 9 板 45182 条。commit 待记（见 git log）。

### 27.39 时装表种类属性侦查终判：part_type jump 全量解析失败（2026-09-04，用户问"时装总表没有种类属性吗"）

- **问题**：时装表（fashion_data 22570）行级无可用种类列→背包/衣服/头饰只能靠名字文本后缀分类，名字无"包/袋"字的背包（家族名共享行）漏网。
- **侦查**：时装表字段名确有 part_type（疑似种类列，面饰表同名列=face 直接文本）与 schema 536016 的 cloth 列。但 part_type 值全部=jump:N（0x0b 引用，N=uleb blob 绝对偏移）——需解析 jump 目标才能得值。
- **jump 解析全量实验**（19408 个 part_type jump 目标逐一读目标字节+标量）：**15869（82%）目标处=任意数据字节（00/ff 等）无效偏移**；2725 撞 0x01 int（值 1/2/39/32/8/238…无整齐部位码序列=随机命中）；196 撞 0x05 文本、108 jump 链、362 bool。目标偏移≈行 key 邻近=jump 指向行记录区内部任意位置。
- **终判**：part_type 的 jump 是**坏引用/行内自引用**，目标无独立部位语义——**时装表结构上不存在可读种类列**（设计有、数据不可用）。25.1"字段名错位→文本解析路线"结论以全量数据复证（此前未解 jump，本次解了 19408 目标仍无部位词）。
- **影响**：时装行身份只能靠名字文本后缀（-衣服/-头饰）与命名语义判定；背包"名字不带包字"的行（套装家族共享名）静态不可辨=与 1489 时装文字层同边界。补齐仅实机锚点可用。无发布改动。

### 27.40 解码器 jump 波及审计 + part_type 真解（2026-09-04，用户怀疑拆包器 bug）

- **用户质疑两连**："肯定有种类属性，只是办法不对"/"压根没跳转，是拆包器有 bug" → 全量复查。
- **发现 1（probe 基准 bug 在我方）**：此前 probe 用 x{ 全长 body 索引 jump 目标（错 8+4×15346=61400B），误判"82% 无效偏移"；改用解码器同款 blob（去表头）后：**part_type 的 19260/19260（100%）jump 目标=合法 0x27 组**——jump 不是坏引用！
- **发现 2（0x27 组内容）**：part_type jump→0x27 组（kind=0x05，4 元素）——元素=外观展示配置（icon 路径/模型名/描述/部件名）；第三元素多为 **b_f_/b_m_（背包模型，如 b_f_3587_2 x1012、b_m_3295_1 x552）、h_h（1432）、suit_suit（60）、character/players*/bag_ 路径**——疑似与行部位相关（待行级对照确认）。
- **波及审计（用户问"有没有波及别的东西"）**：
  ① 行对齐验证：key=254698 手工重放（marker d6/schema 23250/bitmap_ref/字节序列）与解码器输出**完全一致**→ 解码器无行错位 bug；"字段错位"现象=时装表**多 schema 设计差异**（显示名在 socket_names_male 等槽、name=0x01 int ID），非解码错位。
  ② 已发布板（道具 35986/面饰 180/时装 1428/背包 79/礼盒 5443/皮肤 114/奖池）全部只依赖 0x05 文本槽回放——**jump 未解不影响任何已发布数据**（0x05 路径不经 jump）。
  ③ **结论层波及**：25.1/27.39 "part_type jump 不可信/无种类列"**需要修订**——jump 可解（0x27 组），时装表结构字段并非全不可用；种类属性可能在 0x27 组内（b_/h_/suit_ 模型族）。时装表行身份升级路径打开（下一轮：行名 vs 组模型族对照）。

### 27.41 时装表行级结构深挖（"重做"轮）：bag 模型族与部件判别的边界

- **0x27 组真解**：part_type jump 100%→0x27 组（kind=0x05 四元素）=家族共享外观配置（icon/模型/desc），组第三元素含 b_f_/b_m_（bag 模型族，b_f_3587_2 x1012/b_m_3295_1 x552）/h_h/suit_suit——**组=家族级非行级**。
- **行内 .gim 模型路径**：仅 769/19260 行有完整模型路径；2531 行 part 槽含 bag 标识——但**衣服行也带 bag 模型引用**（都市打工人-衣服 part=bag_f_3224_1.gim、圣诞温情-衣服(永久款) part=bag_m_3146_1.gim）。
- **判别分析**（374 衣服行 vs 77 背包行，15 个共同 schema 全字段对比）：无单一干净判别字段——**衣服时装自带配套背包模型**（角色=衣服+背包组合），独立背包外观（衣橱背包格）=纯 bag 模型时装。
- **候选家族**：138 个裸名家族含 bag 模型行（饿龙咆哮 12 行全 bag/太空舱喵/圣诞温情/巨蟹座…）；"XX-衣服/-头饰"后缀行已剔除但仍混入空格分隔漏网（斗鱼新年限定 - 衣服）。**时装家族文本（衣服件/背包件共享名）与独立背包名在名字层+模型层双重重叠→静态无法可靠区分的边界已到**。
- **卡点建议**：需用户 2-3 个实机样本（饿龙咆哮/圣诞温情/巨蟹座 在衣柜是"时装"格还是"背包"格）校准判别维度；否则维持 79 条文本层板+138 候选待锚。与 27.31 时装 int name/27.19 武器皮肤 UI 名同类：**静态表内无法裁决的，实机锚点唯一**。

### 27.42 背包行身份静态判别穷尽（续 27.41）

- **家族×组模型族构成**（2121 家族）：纯bag 族 513（例名却含 -头饰/-衣服 后缀：海街日记-头饰/恶魔玩偶-衣服-30天）；含非bag(h) 113、含非bag(suit) 38；无模型 1186（含深渊漫步/樱花纪念背包）。**名字文本与模型族交叉污染**——icon_bag_/b_ 前缀命名空间语义不明（疑似"时装上身预览图/配套背包引用"而非背包部件标识），衣服/头饰行同样命中。
- **行文本部件前缀**（cloth_/hat_/hair_/bag_/b_/h_ 短模型名）：15255/19260 行含；b 前缀独占 11255（配套背包引用无处不在），×背包类名仅 63——无法作为部位判别。
- **终裁（静态层穷尽）**：时装表"行身份"判别被三重污染（①每行都带配套背包模型引用 ②icon_bag_/b_ 命名空间语义无法对照 ③家族文本共享）；**行级背包全量的静态路径已穷尽**。背包板维持 79=名字语义文本层上限；138 候选家族（27.41）+513 纯bag 家族留待实机锚点裁决（用户当前无法查看样本，挂卡点 C 区候选）。
- 教训：27.40 jump 基准修正（blob vs xfull）说明 probe 基准错误可致假结论；解码器本身无错位 bug（27.40 行对齐验证）。


### 27.43 时装类大分类重排发布（2026-09-04，用户指示）

- **wiki.html 时装区重排四大分类格**：grid「（1）头饰、套装&衣服」←fashion_wardrobe_slots 1428（csub 注明=时装外观表文字层全量，含背包/荧光棒条目独立视图见（3）（4））；「（2）发饰、面饰」←fashion_face_slots 180（face 槽，细分口径见 C 区）；「（3）背包、挂件」←fashion_bag_slots 79（挂件/行级候选见 C 区）；「（4）投影、荧光棒」←新增 fashion_glow_slots 2 条（普通荧光棒/彩虹大神荧光棒，从时装板筛，行级链继承）+投影占位。（7）武器皮肤独立 group 保留。
- 4 板 category 常量更新（rebuild 脚本）→ 全量 rebuild → build 10 板 45195 条；policy json 同步 category。
- 26/26 unittest（gate 数组 10 值含 glow 2）。
- **C 区登记「时装类细分系列」BLOCKED 一条**（用户指示细分进卡点）：①发饰/面饰/挂件细分口径（face 槽 180 内眼镜/面具/帽子/头顶装饰/挂饰归属）；②挂件格（时装表 0+face 3 条，背包格 vs 挂件格边界）；③背包行级全量（27.41/27.42 三重污染穷尽，138+513 候选待实机）；④投影无同快照表；⑤荧光棒 2 全量已发。

### 27.44 投影定位链发布：fashion_projection_slots 36 条（2026-09-04，用户 3 张实机锚点图）

- **定位链（用户实机锚点驱动）**：用户发 3 张「时装搭配→投影」界面截图（回旋音阶/有龙则灵系/翅膀型悠游天地…27 名）→ 工作副本二进制反查 → 全命中 buff_data 相关（002918/007597/025378=buff CHS 池）→ 池文本形态「伴身投影-回旋音阶/伴身投影·时空裂隙」→ **投影=buff_data 伴身投影系**。
- **铁证**：行级 sfx_path 全部指向 `effect/fx|mesh/players/common/benshentouying/`（伴身投影资源目录）；buff_class=SfxBuff/IdleChangeFollowBuff/AddSocketModelBuff。
- **板**：buff_data base entry 006675 FID 445751514818606E + CHS 002918 FID 1E23D0CBDFC4BEA7；筛选=sfx_path 含 benshentouying 或 name 含投影，剔除 1219测试资源 → **36 条**（伴身投影·/- 30 + 投影·浑天穹焰 1 + 有龙则灵系 4 变体[sfx 同目录、name 无投影字样]）。
- **锚点核对**：27 名中 **24 精确命中**（有龙则灵本体+悬河注火/云阙天光/春风桃醉/青寰入梦 全在）；星河流淌/无尽之紫/星礼星愿 3 名 buff 池（chs/kj1/yk 同 15116 条）0 命中——疑似 OCR 错字，等用户核对实际字样后精确重查。
- wiki.html（4）投影、荧光棒 格升级（投影 36 · 荧光棒 2）；policy 登记；build 11 板 45231 条。
- 验证：27/27 unittest（新契约测试 test_rebuild_fashion_projection_slots.py）；ad-hoc 15/15（rebuild/锚点 24/sfx 判据/测试资源剔除/manifest/wiki/policy）。commit a648b48。
- 备注：buff_data 17866 行 name 列级干净（0x05 直读）——又一个可整表行级解码的表（buff 体系后续可扩展）。

### 27.45 投影板补道具层名册：39 条，锚点 27/27 全中（2026-09-04）

- **用户核对 3 名无 OCR 错字** → 重查：星河流淌/无尽之紫/星礼星愿 不在 buff 池，但在 **common_item 640000 系投影道具专段**（星河流淌=640001/无尽之紫=640020/星礼星愿=640032；icon 全=ui/item_icon/icon_fx_640xxx；desc="科技会研发的最新投影道具：…"）——用户界面名=道具层名册，buff 名册缺这 3 名（可能新投影 buff 未建/名不同）。
- **投影双层定位链定稿**：①common_item 640000 系投影道具名册（icon_fx_640xxx，含 有龙则灵+4 典藏主题变体 640035-640039/五行之力 640044[铠甲勇士联动]/浮游炮 640041[灵笼联动] 等）；②buff_data 伴身投影系特效执行层（sfx benshentouying 目录）。**用户实机锚点 3 图 27 名 → 100% 命中**。
- 板 36→**39 条**（3 条补自 common_item，标注 provenance.table=common_item + 行级槽位回放）；notes/wiki/policy/测试/gate 同步；build 11 板 45234 条；27/27 unittest + 13/13 ad-hoc（锚点 27 全核对、3 新条目来源/槽位）。commit c76677c。

### 27.46 荧光棒名册重建 v2：9 款全量（2026-09-04，用户指出"荧光棒不全"）

- **v1 缺陷确认**：fashion_glow_slots v1 从时装表筛 name 含荧光棒=仅 2 条（彩虹大神荧光棒/普通荧光棒）——漏了游戏内荧光棒格主体。
- **正源**：player_appear_data（base entry 007074 FID 484AB42BD31AE503 + CHS 006403 FID 4151CFD3191DCAD7；5261 行/238 unbound；字段名干净 part/name/model_name/gender）——name 含荧光棒 16 行（key 5xxxx/15xxxx=男女对，part=5 荧光棒部件）聚合 **9 款**：彩虹大神荧光棒/彩虹荧光棒/荧光棒·守护/救援/求索/漫步/腾飞/追随/闪耀；荧光棒·漫步/腾飞 仅女行（无 5xxxx 男行）。
- **desc 层**：池含赛季获取说明（"新款荧光棒，在辐射诡楼 XX 赛季成为 XX 骑士即可获得，在下赛季开始前回收"——青铜/白银/黄金/见习/资深/钻石/皇家 7 级骑士 × 先锋/征服/挑战/第15赛季 等）。
- **附带认知**：player_appear_data=角色外观部件表（part 1=发型[白色马尾等 1388 行]/2=脸型[鹅蛋脸等 22 行]/3=2092/4=1003/5=716[含荧光棒]/6/7），=发饰/捏脸体系潜在扩展源。
- 板重建：16 行聚合 9 条目（pair_key 男女关联）；wiki badge 荧光棒 9；policy reason 更新；manifest 11 板 45241 条；28/28 unittest（glow 契约测试重写）；18/18 ad-hoc。commit 待记。


### 27.47 时装类新增（5）本场最佳 击败播报板 13 条（2026-09-04，用户指示）

- **定位链**：common_item desc 特征（可在衣柜-社交-击败播报处更换）破案：
  ① **本场最佳动画道具**=common_item **1340003-1340009**（7 主题：斩破天光[赤月晶魄]/炽日耀斑/炽海天姿[殿堂造境]/金乌负日/沙海月鸣/水晶玫瑰/不湮之花[殿堂造境]——传世皮肤升阶三阶或殿堂时装造境奖励）；
  ② **击败播报**=common_item 154150 赤月荆棘/154775 炽海天澜/155147 神鸟凌天/155740 沙海月鸣/155955 水晶玫瑰（传世皮肤升格二阶）；
  ③ **街头赢家**（用户锚点：特训战场每赛季 1000 分限时奖励）=**gift_data 礼盒 135386「本场最佳:街头赢家（30天）」**（街头涂鸦风暴龙卷动画；common_item 1340010/11 空洞=曾占位）。
  **同主题链**：皮肤二阶→击败播报、三阶/造境→本场最佳动画。
- **UI 佐证**：020463=PanelFashionArrangementV2.py（时装搭配面板 含 设置为击败播报）；009414=配置表（全场最佳动画/赠送主题击败播报）——与投影/荧光棒同属衣柜-社交界面体系。
- **板**：fashion_bestplay_slots 13 条（8 动画+5 播报），source_board 标注 common_item/gift；wiki.html 时装类新增 grid（5）；manifest 12 板 45353；29/29 unittest + 22/22 ad-hoc。commit eccf2a6。


### 27.48 UI 排布整理（2026-09-04，用户：遗落收尾+整理 UI，现在很多）

- 顶部 alert → 统一发布纪律（所有板=当前包行级文字/配置来源，不表示当前可得/业务启用）。
- **零、新更新与预告专栏=游戏未上线资源预告**（用户纠正：不是网站进度预告）——用途说明卡+发布前对照历史更新汇总排除已上线。
- 已发布类目（道具 2+时装 1-5+武器皮肤）删除冗余 audit 占位卡 → 每 grid 单卡（JS 注入 published 卡）；边界说明并入顶部纪律区。
- 战力（1）武器本体与涂装/奖池（1）（2）已发布板（weapon_attrs 196/lottery_kaijia 10/exchange 1757）注入 grid 恢复（初版重排误删已修正）。
- 26/26 前端校验（注入位全匹配/无残留双卡/零区用途正确）。commit（UI 整理）。

### 27.49 道具总表（common_item 35986）全量解码核对：无误（2026-09-04，用户：重新核对检查一次）

- 重解 base entry 18005 FID B42760CCA41DBC25 + CHS 23928 FID EF3A8474A5E5F7A4：
  解码 SHA 与板 provenance 一致；行数 35986；行键集合与板全等；name 槽位 field/value 35986 全等；
  name 文本 35986 全等；desc/icon 槽位抽样 20 全等 → **发布板=当前包解码忠实回放，无解码问题**。
- stats 说明：indexed 37934 / decoded 35986 / unresolved 1948（行 ID 空洞/无 name 槽引用，记录在案非缺陷）。

### 27.50 核芯词条数值层：min/max jump 目标=0x27 kind 0x12 紧凑组（2026-09-04）

- nucleus_entry_data（87 词条）行对齐**手工逐字节验证正确**（key1: upgrade_desc=slot71/weight=50/buff_id=16601/desc=72/entry_id=1/type=1/max=min=jump:179 全对上）。
- min/max 的 jump:179 目标=blob[179] `0x27 kind=0x12` 组——**resolve 白名单（01/02/05/0B）缺 0x12**（用户怀疑工具缺口，二次命中）。
- 0x12 组例：`27 12 02 00 00 80 3e 00 00 80 3e`=疑似 float32 0.25×2（min=max=0.25 词条）；结构（高/低 nibble 语义/元素类型变长）待解。若解通=词条数值区间可得=核芯数值链第 2 块。


### 27.51 解码器 0x12/0x22 nibble 组支持补丁（2026-09-04，用户：先把2补了）

- 结构破译：0x27 组 kind 高半字节=元素类型（1=float32 4B、2=double 8B），低半字节=元素数；
  例 nucleus_entry min/max 组 `27 12 02`=2×float32、`27 22 02`=2×double（count 字节=低 nibble 冗余一致）。
- 补丁：toolkit_core/bindict_table.py `resolve_jump_group`+`_read_27_uleb_group`+`_resolve_27_group_reference`
  支持 kind 0x1N/0x2N（原白名单 01/02/05/0B 语义不变）；踩坑 3 个（fmt 拼接 '<f'*n 非法、值区起点 +2 应为 +3、
  width 判断用旧 fmt）——手工逐字节验证修复。
- 验证：nucleus_entry min/max jump 目标解出数值（[0.01,0.01]/[0.25,0.25]），uleb 组回归无损，wiki 全套 unittest 绿。
- 含义：核芯词条数值区间字段级可得（解码层已通）；bindict_provenance 主输出仍保持 'jump:N' 忠实回放，
  数值经 _resolve_27_group_reference 按需取用。


### 27.52 核芯特技配置表破案（nucleus_build_data kj1 base 016783 + chs 023314）

- 定位：nucleus_build_data 家族 kj1/kjxq 各有 6.3KB base（016783/020841）+75KB chs 池（023314/005437 519 条）——
  27.33「build_data 无 base」误判修正（当时只找 com\cdata 主路径，实际在 overseasuto_oversea_data_kj1）。
- 结构：75 行特技配置（key 1011=疾影火刃/1012=绝对零度…）：nucleus_effect_name（=异变核芯-X 的 X，与
  common_item 660000 名册同名关联）、desc=完整特技描述、simple_desc、attr_simple_desc（含 {0}=每星数值占位）、
  icon_path（技能图标 ui/other_icon/jinghejineng/）、nucleus_attr_type(1/2)、released_cbg、
  weapon_type（jump→组[50]=武器类型码，映射表待查）、rank_desc_ref/rank_to_desc/rank_to_simple_desc
  （jump→星级文本：池[329] 实证=疾影火刃星级段「每冲刺40距离提升重斩伤害8%…上限60%…击倒」——
  rank 文本=05 引用池段形态，池 519 条=全部核芯星级效果文本库）。
- 用户锚点双证：穿心极雷=660077（common_item）+池内星级段（截图 *5 原文逐句命中【电能充盈】…25%）。
- 用户情报：经典服核芯最高 12 星（非 5）——rank 数值档位需按 12 档考虑（数值数组元素数 5/12 未定）。
- 卡点：0x96 行 schema bits=0（无 bitmap 全字段序）手工 trace 易错位（工具库解码正确）；rank 每星数值数组
  位置（rank_desc_ref 关联）未解；weapon_type 码 50→武器名映射表未定位。


### 27.52 核芯卡展示定版完成（2026-09-04，commits 06f3a8a→8c2e87e）

- **核芯卡=唯一一张**（nucleus_cards_classic 77 条：经典服 76 颗 12 星完整 + 简单生存服独有 1 淬焰燃锋），131 名册/87 词条板撤发布（json 存档）；13 板 45430
- 品级 100% 补全：正式服 npk common_item 主表（同 FID B42760CCA41DBC25/EF3A8474A5E5F7A4=两服同表实证）660000 段 desc 前缀；分布 特级30/高级32/中级11/低级4；rebuild 脚本 entry_bytes 支持按 FID 查询
- board.html 渲染：摘要卡（品级/武器类型=种类（码）同行/技能图标/核芯特技全文），星级段点卡头展开（默认 hidden），5/9/12 拆独立标题段；item_id 入副标题去正文重复
- 星级段三字一行坑：.i-more 是 .kv grid 子项只占首列 84px→ grid-column:1/-1 跨全宽（8c2e87e）
- 遗留：星级中间（1-4/6-8/10-11）属性成长数值源未定位（主表无数值矩阵、nucleus_base_buffs→buff id 6→buff 表待定位；截图锚点 40/44/48/52/52）；升星数值表=下一侦查目标
- 核芯数值链卡点更新：name/品级/武器类型/完整特技/5-9-12 星级段=全通；中间星纯数值=未通


### 27.53 核芯展示定版收尾 + 词条/升星搁置决策（2026-09-04）

- 核芯卡终态（commits 06f3a8a→0ed6524）：nucleus_cards_classic 77 条单卡（经典 76×12 星+简单独有淬焰燃锋）；摘要卡（品级/武器类型（码）同行/技能图标/核芯特技）；点卡头展开星级段（5/9/12 拆标题段）；排序默认新出在前（sort_660 正式编号降序，同名取首版 min id；疾影火刃 660000 最早→深蚀追猎 660082 最新）
- 品级链：正式服 npk common_item 主表（同 FID B42760CCA41DBC25/EF3A8474A5E5F7A4=两服同表实证）660000 段 desc 前缀；rebuild 脚本 entry_bytes 支持 FID
- **词条+中间星级数值=用户搁置（价值低+无源）**。机制澄清（用户实机信息）：通用词条 35 随机洗炼、数值随核芯星级（射速 1.2→3.0% 型）；专有词条 52 随机洗炼、品级固定数值不随星（特级 0.6-0.7 即特级）；核芯成长条（磁暴伤害 40→52%）核芯自带。成长模式=1-4 递增/5 停/6-8 增/9 停/10-11 增/12 停。数值源排查 8 轮全阴性（kj1/正式主表 blob f32/i32/u16/uleb/f64、buff 006675 key6 空洞、nucleus_conf 005289 非数值、005437/023314 池）=服务端下发/客户端代码公式推断
- 下一步：t4 奖池定位链（selector/consumer 静态可证性）


### 27.54（2026-09-04 夜）战力类三连发 + 芯片深扫定论

**发布链（commit 链）**：`5fe9cec`（战力四大分类定版（一）武器/（二）核芯/（三）芯片/（四）无人机，grid+两板 category+policy+gate 断言四处一致）→ `776bae7`（武器名称回填）→ `0ed6524`（排序控件可见性修复）→ `8c2e87e` 前序 → `9a181bb`（芯片名册板）→ `3a67244`（policy.js 版本化防缓存）。现 **14 板 45497，31/31 unittest，工作树干净**。

**1. 武器名称回填（776bae7）**：196 行中 164 行回填真名——153 name-slot 短名直读（夏尔魅影/95式/EM 系列/590M…）+10 desc-first 人工清单（AWP狙击步枪/UZI冲锋枪/KSG/G3/蝶影双枪/雷明顿/仿生菌焰/光盾无人机/生产台×2）+Mark.06 特例；32 行诗句/路径/限用句保持匿名（name_raw 原样可见）。**解码正确性实证**：行起点与数值字段（weapon_kind/bullet_id/attrs offset）互相印证；name/desc/model_path 槽同行为不同物品文本=**all_equips 宽表文本槽跨物品引用为游戏侧数据布局**（部分行 name 槽=宣传文案）。武器 desc/icon 槽不可信——板不展示。遗留：33 行匿名行的真名（用户游戏内认领 or 放弃——用户 2026-09-04 判定"武器没啥用"暂缓）。

**2. 核芯卡排序（ecac899→0ed6524）**：sort_660 正式编号（grade_660 同名取首版 min id）默认新出在前（深蚀追猎 660082→穿心极雷 660077 最新批 ✓）；排序控件独立于 meta.filters（cfg 分支原把 fOrder 一起藏了=控件不显示 bug 根因）；排列顺序=早到新/新到早可切。

**3. 芯片链（9a181bb）**：
- 名册=common_item 330xxx（进攻 42）/331xxx（防御 17）=59 道具；chip_type 配置池（003278 kjxq/022874 kj1，各 205 条=10 字段名+芯片名区）另有 8 防御芯片名在册（坚如磐石等=当前包无道具行=经典服/未上架）
- **chip_type 配置表族定位**：kjxq 主表=1352（78 行 schema125=80 列宽表：10 标准列+70 芯片关系列=升级合成/成长配置，max_chip_level=350xxx 成长曲线段，fragment_count=合成碎片需求）；kj1 版=533（86 行 key 1011+，名在 chip_icon 槽，effect_label=价值梯度 5000→365000）；714=19264 行大表（330 段 71 行撞车=芯片关联矩阵）
- **1352/533/714 的 0x76 index 变体**：bucket offset 落在 tail 区内（de 后）=parse_index 的直存/移位探测把第三类"基准相对型"误判为直存→行起点全错位→decode 值乱。**修复方向=parse_index 加第三候选（off 落 tail 内但 off-N 落行区）——未做（挂起）**
- **金紫蓝品级=无静态列**（三表数值=成长/价值梯度非 3 簇）；用户实机锚点：金=特级（从容不迫"特级防御"截图 9e20f478/9c3dfaef）、图鉴排序=金→紫→蓝分组、星级 1-8=强化等级独立于品级
- **芯片效果长文（"对300距离内目标造成伤害后获得11.5%暴击率"）=全包 0 命中**：002918（buff 短名池）/1990+4617（天赋 desc 池 3136 条=技能/探测芯片采集天赋/核芯共鸣效果）/13196+22221（战术装备减免档）都无战斗芯片效果模板——效果文本=客户端/服务端拼装（同核芯中间星级数值结论）。用户断言"不可能不在"但穷尽扫描（全 ED utf8 特征+全 0x73 池+x{ 表全文件）确认不在 script 数据包

**4. 深扫方法论沉淀**：ED 文件头分布 73=24241 主（0x73 壳）+其余小类；x{ 真头=263/271（表）vs 内容区假 x{（文件尾）=用头位置判表型；utf8 特征直搜文件（非池 parse）可覆盖 x{ 表内嵌文本。

**挂起队列（下轮候选）**：1352/533 0x76 index 修复（parse_index 第三候选）；all_equips 33 匿名行；无人机；t4 奖池。核芯中间星级/词条数值/芯片品级色/芯片效果文本=客户端展示层无静态源（日志 27.53 起维持）。

### 27.55 铠甲再临奖池共享池污染修正（2026-09-04）

- `super_fashion_lottery_conf_data.key=232` 的面板展示层仍为 10 格；活动卡保持 1 个顶层条目，不把面板格平铺成 10 个活动。
- 旧 `rebuild_kaijia_panel_static.py` 将 `391782` 的历史共享 reward rows 按 `pool_id + slot` 展开，导致星宿万象/鸾凤依偎等家具混入铠甲卡。修正为：`391782` 只保留 `activity_pool_refs` 的 `shared-reference-only` 逻辑入口，不展开其行；家具反证 ID（133123、131219、94877、94878、94876、94874、94881、94873）均不进入 390704。
- `390704` 当前保留 9 条数字 slot 的秘宝拆解：8→194190 火刑战驱、9→139292 刑天铠甲、10→139293 飞影铠甲、11→1110181 疾影枪、16→134061 球状闪电核芯、17→132694 酸焰激流核芯、20→1110182 火刑电光炮、21→1110183 战神烈火剑、22→633070140 刑天召唤器；`391783` 保留当前已定位的福袋 slot 5→135891。
- 面板第 9 格 `633080140` 名称按用户正式上线事实回填为“飞影召唤器”，并在 provenance 标记 `user_evidence.scope=name-only`；未把它伪造为 390704 的 slot，也未把蝶影左轮 reward_pool key=440974 的附属引用升级为铠甲奖励叶子。
- 页面新增逻辑活动池关系区；板块 JS 加 `?v=` 查询参数，解决 board.html 缓存旧 JSON/JS 的问题。验证：builder 输出 14 板/45488 条；全套 unittest 31/31 OK；Node 数据运行时断言通过；8765 HTTP 与桌面预览显示 2 个子奖池、飞影召唤器和 shared-reference-only 关系。

### 27.56 0x76 索引复核 + all_equips 匿名边界收束（2026-09-04）

- **1352/533/714 的“第三 offset”待办撤销**：以 BA8 entries `001352/003278`、`000533/022874`、`000714/003278` 实字节重放。`parse_index` 的 raw bucket node offset 虽落在 `tail`（1352：`de=4381`，如 5219），但它指向 tail 内 `(key,value_start)` 索引对，最终 `value_start` 全在 `blob[4:de]` 并命中行标记。结果为 1352=78 index/78 decoded/0 unbound，533=86/86/0，714=19264/19264/0；`off-de` 候选反而 ULEB 截断。故 0x96 文本错位仍是字段标签/值槽语义问题，**不是行起点或 parse_index 问题**；不改解码器。
- **all_equips 匿名当前实际为 27 条（不是旧口径 33）**：总 196 = name-slot 154 + desc-first-map 15 + unresolved 27。专项重放 10440、10441、10743：三条具 `id==row_key`、枪械模型/弹药/weapon_kind 结构，但 name/desc CHS 文本彼此跨物品错位；10440/10441 为转轮霰弹枪结构、10743 为双枪结构，均无同一行可用短名。
- 三条武器候选的 `common_item`/`gift_data` 无同 ID 正式行，图标路径也无同表正式物品记录；模型路径全包命中仅回到 all_equips 变体，无独立命名表。**禁止以 row_key/id 与 common_item 同号、被串入的 desc、模型路径、名称相似或跨变体文本回填名称**。它们连同其他 24 条路径/任务/外观/护盾行保持匿名，等待运行时/实机锚点或独立命名表。
- Wiki 板说明修正为 154/15/27，并加入“不与 common_item item_id 跨表同号回填”；回归断言固定三条武器匿名。rebuild + builder=14 板 45488 条；全套 unittest 31/31 OK；Node JS runtime 与 8765/桌面预览均验收通过。

### 27.57 铠甲再临正式服定向 trace checkpoint（2026-09-06，未发布/未闭合）

- **在线状态纠正**：铠甲勇士二期已在经典服正式服上线；此前“概率详情 UI 不展示”只能说明该 UI 不提供明细，**不能**推成活动未上线或无运行时活动。
- 正式服只读源为 `E:\LifeAfter\Documents\script.py314.lc.npk`，SHA `79c0d06f53db02ca4f8ebad97da2cfef22916f963e8cae3461b914d4a39bb85d`。新增但尚未提交的 `tools/extract_kaijia_formal_tables.py` 已从该源定向提取 8 张活动链相关表；`tools/trace_kaijia_formal_reward_chain.py` 生成 136 条 reward 记录 trace。二者是 provenance 辅助工具，**尚未接入 Wiki rebuild/policy**。
- 正式服 key=232 已复核：`lottery_id=391782`；`fortune_bag_dct` 是 0x36 单键映射 `{4:391783}`；面板展示仍为 10 个 item ID。正式服 trace 能复现部分候选 reward-pool 行、配置概率和 reward jump，但没有找到把在线本期唯一分派到 `390704/391536/391533` 的活动级 selector。
- 另复核 `random_item_reward_data_998` 与 `gift_data`：六个礼盒 field-level 链为战神烈火剑 `139300→998556`、疾影枪 `139301→998557`、刑天面甲 `139302→998558`、飞影锋眸 `139303→998559`、刑天召唤器 `139304→998560`、飞影召唤器 `139305→998561`。这只闭合礼盒配置/名称桥，**不证明奖池归属或概率**。
- 当前已发布 `lottery_kaijia_panel_static` 仍锁 BA8 源（`ba8a239a…`），为 1 张活动卡：可展开 `390704` 9 行（均带旧链概率）和 `391783` 1 行（概率未定位）；`391782` 只标 `shared-reference-only`，不展开以排除历史家具污染。其 `audit_status=passed` 仅代表该受限静态板 provenance 契约通过，**不等于“完整主池/子池/概率已闭合”**。
- 工作树现状：仅跟踪的改动是生成器子页标题源改为“ 四、奖池 / （一）抽奖、转盘、不放回抽奖”；两份正式服工具未跟踪。尚未因 27.57 重建、跑测试、更新生成 `.js`、发布或提交。
- **停损/下一门槛**：不再扩大扫描 Documents 缓存、混合媒体、公开前瞻或网络连接来替代 selector。后续任何 runtime/协议方向先向用户说明额度、预期字段和停损线；只有取得活动级 selector 或可逐项复核的概率来源，才允许将正式服 trace 接入铠甲板。

### 27.58 奖池类分类重排：宸世臻藏独立为（二）（2026-09-06，未提交）

- 用户确认当前 `exchange_static_structure` 的 `common_exchange_shop_data` 静态 mapping/detail 内容均属**宸世臻藏**，不应占用通用的“满减活动、神秘商店”栏。
- `tools/rebuild_exchange_static_structure.py` 与生成板同步改为 `四、奖池 / （二）宸世臻藏`；主页待采集项顺延为：（三）满减活动、神秘商店、（四）限定核芯研制、（五）限定芯片保底。新增（三）说明明确其需独立 selector/商店配置，不得以宸世臻藏 mapping 代替。
- 已执行 `rebuild_exchange_static_structure.py`（1757 条）→ `build_wiki.py`（14 板、45488 条）→ `unittest discover`（31/31 OK）。JSON、生成板 JS、manifest 与主页文本四处断言一致；旧主页标签“（二）满减活动、神秘商店”不存在。
- 本次未提交。工作树中另有铠甲标题源、正式服定向提取/trace 工具等既有未提交项，禁止混入本次分类提交。

### 27.59 子页标题与主页卡片同源（2026-09-06，未提交）

- 根因：主页卡面标题本来取 `category.split(' / ').pop()` 的分类尾段，但 `board.html` 用内部 `meta.name` 做 `<h1>` 与浏览器 tab 标题，故出现“铠甲再临 · 静态面板配置”等生成器名。
- `board.html` 新增 `boardCardTitle(meta)`：优先取分类尾段，只有 category 为空才回退内部名；所有已发布板的 `<h1>` 和 `document.title` 都改用此函数，移除 h1 后附加的完整分类 badge。因此子页主标题与主页卡片严格同字。
- 新增 `test_board_page_primary_title_matches_homepage_card_category_tail`：Node 执行实际前端函数，覆盖铠甲、含斜杠分类（背包/挂件）及空分类回退，并断言渲染点不再引用 `m.name`。先 RED（缺函数）后 GREEN。
- 验收：Node 从实际 `board.html` 提取函数并遍历 manifest 14 个 published board，14/14 标题均等于主页卡名；全套 unittest 32/32 OK。8765 在最后 GUI 预览时拒绝连接，按“不得重启”约束未改服务，故视觉预览未作为验收依据。
- 铠甲生成器此前仅为此 UI 问题写入的 `meta.name=完整分类` 临时改动已撤回；不再单板硬编码标题，内部名保留为 provenance 描述，页面统一由 category 驱动。

### 27.60 正式服+测试服双源并行规则（2026-09-06，规范已落/未做数据发布）

- **用户定案**：正式服（经典服）与测试服（简单生存服）均为默认读取源。正式服可能含测试服遗留老内容，测试服可能含预先内容；不得再把任一源作为唯一真源而跳过另一源。
- `data/live_sources.json` 的两份现有只读锁保持不变：`lifeafter-classic-current`（正式服 `79c0d06f…`）与 `documents-py314-current`（测试服 `ba8a239a…`）。新侦查先双读同目标并记录 `both` / `formal-only` / `test-only` / `conflict` presence diff；base、CHS、reward、名称字段仍必须同一快照闭合，**禁止跨服拼字段**。
- 测试服独有只是一种快照差异。只有 `test-only` 条目已对照 `E:\la拆包项目\明日之后完整历史更新汇总_2018-2026.md` 排除历史已上线，且有测试服行级/资源 provenance，才允许进入 **零、新更新与预告专栏**；页面必须标“测试服独有预告”及源锁。未过历史排除=隔离候选；`formal-only` 也不推断版本状态。
- `docs/SCHEMA.md` 已新增 3.1 双源规则；主页零区说明改为该准入条件；`lifeafter-wiki-boards` skill 已同步。项目计划阶段 A 改为“先做双源 presence diff 与发布语义”。
- 本 checkpoint 未重建 board、未扫描 NPK、未发布/提交任何测试服独有内容。单源历史板不自动失效，但下次重建前必须补双源 diff。已委派 Luna 仅做现有生成器/发布板单源默认盘点，结果待主模型复核后再排改造优先级。

### 27.61 双源 presence pilot：common_item（2026-09-06，未发布审计）

- Luna 只读盘点经主模型复核：14 个 published board 中，当前双源锁仅 `nucleus_cards_classic`（正式服+测试服业务合并特例）；`weapon_skin_sfx_text_sources` 的第二锁为历史 root 对照，非正式服当前源；其余板仍为 BA8 单源或继承单源。盘点不代表业务上线/未上线判断。
- 先实现纯 `tools/source_presence.py`：按同逻辑键比较两源记录，`both`=name/desc/icon 指纹一致；仅一源存在= `formal-only` / `test-only`；同键展示字段不同= `conflict`，**保留两边记录、不做字段借用或合并**。
- `rebuild_common_item_text_sources.py` 已参数化 `source_id`（默认仍为 `documents-py314-current`，现有公开 BA8 板不换源）；可显式 FID 读取正式服或测试服并在 provenance 写实际 source_id。新增 `tools/audit_common_item_dual_source.py` 只输出 `data/audits/common_item_dual_source_presence.json`，`publication_status=unpublished-audit`，不进入 policy/manifest。
- 定向实读仅 common_item 的两组 FID：两服 SHA/bytes 均匹配 registry；测试服 entries `18005/23928`、正式服 `32172/42758`（**FID 相同、entry 号漂移**）。结果：已解码 35986 个 item_id 全部 `both=35986`，`formal-only=0`、`test-only=0`、`conflict=0`，差异明细 0。该结论只限这张表；没有测试服独有候选，因此零区不新增卡。
- 验证：source_presence 2/2、audit contract 2/2、common_item 现有回归+新增 source 选择 2/2 均绿；正式服/测试服 source_locks 已写入未发布 audit sidecar。未 rebuild 公共 board、未 build manifest、未发布/提交。
- 下一优先级：按同一低风险模式先检查 `gift_data` 的两服 FID/源锁可读性（其为独立直读板且供最佳动画等派生板使用）；确认后再决定是否做第二份 presence audit，仍不跨源合并。

### 27.62 优先级切换：双源改造后置，先优化铠甲再临奖池定位链（2026-09-06）

- 用户决定：双源规则与 common_item pilot 保留，但**停止继续 gift/其他板的双源改造**；双源 rollout 回到 pending。此前仅完成 gift_data 两服 FID/锁的读取前置检查（正式 `35329/26317`、测试 `19768/14746`），未解码行、未改 gift 生成器、未生成 gift audit。
- 当前主线恢复为铠甲：只利用已有正式服 `79c0d06f…` 8 表 targeted workcopy 与 `kaijia_formal_reward_trace.json`，优化“key=232 活动配置 → 逻辑入口 → reward_pool 原始行 → reward jump → 最终 [item,quantity] → 配置概率”的逐段 provenance；不再扩扫缓存、媒体、网络或 UI 通道。
- 硬边界不变：`391782` 共享逻辑池不展开；`pool_id + slot` 不可单独认领；`panel_show_item_ids` 仅展示层；`prob_note` 仅配置概率，非服务端完整 odds；没有活动级 selector 时不宣称完整主/子池闭合、不发布完整奖池。

### 27.63 铠甲分期与二期服务器分支锚点（2026-09-06，用户校准）

- 用户校准：`super_fashion_lottery_conf_data.key=230` 的帝皇铠甲是**一期抽奖**；`key=232` 的刑天/飞影是**二期抽奖**。两期必须拆开，禁止把“铠甲”关键词命中的一期 row / pool 混入二期。
- 用户给出二期分支锚点：**经典服独有奖励=菌焰喷火器；简单生存服没有**。此锚点只用于反查二期的服务器 selector 与行级链，不能在未找到原始 selector 前直接将奖励写入经典服完整池或将其从简单服池宣称排除。
- 已验证当前注册两包的 8 张铠甲目标表（common_lottery、super_fashion、fashion_sale、reward_pool 各 base+CHS）在解码后 SHA 上逐张完全相同；entry index 不同。因此“包版本差异”不是该二期服务器奖励差异的证据，后续只在二期相关上游配置/行字段定向找 server selector，禁止由两包路径猜分支。

### 27.64 二期 reward_pool 原始行收束与 selector 停点（2026-09-06）

- 以 `reward_pool.broadcast_content` 字面包含“在铠甲再临活动中获得”作为严格筛子（不是按 ID、slot、名称邻近），正式目标表得到 **22 条**二期原始行；其 inline `[pool_id,slot]` 落在：`390465`、`390704`、`390714`、`390733`、`391533`、`391536`、`391782`。每条均已具备 row key、组 raw bytes/offset、reward jump、最终 `[item_id,quantity]`、`prob_note` 与有效期；此时仅为二期活动行集合，未把全部池断言为同一服务器。
- 用户“经典服独有菌焰喷火器”锚点在该集合精确命中：`391782 slot 0` note=`涂装:菌焰喷火器典藏` → leaf `[104999,1]`、`prob_note=0.00163`；`391782 slot 1` note=`涂装:菌焰喷火器雨战版` → leaf `[104997,1]`、`prob_note=0.00253`；两者均带二期广播、有效期 `1801353599`。这是 **391782 的经典服锚点证据**，但“简单生存服没有”不能倒推其他池必属简单服。
- 对 common_lottery / fashion_sale / super_fashion / reward_pool 四表做字段名盘点：均无 `server/branch/classic/simple/channel/platform/zone/region` 命名字段；按二期候选 pool ID 解已成功的 0x27 jump 组也无上游命中（大量非 0x27/非列表 jump 仅记为未解析，不作为“无 selector”证明）。已有 BA8 完整工作副本 manifest 仅含 25485 个无模块名条目，按表名关键词无法列出候选。
- **停点**：当前 8 表可证明二期行/叶子/配置概率，但尚不能为 7 池完整贴服务器分支。未开展全工作副本字段/模块定位、未扫 NPK、未读缓存/网络/UI。若扩展，目标仅为找到含 pool→server selector 的上游配置表；需先明确一次范围/停损线。

### 27.65 二期简单生存服验收锚点与概率门禁（2026-09-06，用户提供）

- 用户提供**简单生存服·体验服、铠甲再临二期**验收锚点：勇士珍匣秘宝奖励 10 项、稀有奖励 14 项、普通奖励 6 项；完整原文已固化在 `tests/fixtures/kaijia_simple_survival_anchor.json`，仅作验收合同，**不得反向回填 pool/slot/selector/概率**。
- 新门禁：定位链只有在三池成员与锚点完全一致、且每个实际奖励都有原始 `reward_pool.prob_note` 配置概率时才可称“简单生存服二期奖池闭合”；任何名称、池归属或概率缺失都保持未闭合。特别保留 `火刑裁决`、`飞影召唤器`、`面饰：刑天面甲`、`面饰：飞影锋眸` 作为防近似名误替换锚点。
- 验收 fixture 不是数据源，不改变当前已发布 BA8 静态卡，也不解除 391782/其他池的服务器 selector 卡点。

### 27.66 展示名与原始内部标记并列规则（2026-09-06，用户校准）

- 用户校准：`刑天口罩`、`火刑电光炮`等可能是内部原始标记，**允许保留**；不得为了锚点展示名而覆盖或删除原字段。
- 二期验收输出改为双标签：`display_name`（锚点/展示名）与 `source_internal_marker`（原始 note/name）并列。例如 `火刑裁决 / 火刑电光炮`、`面饰：刑天面甲 / 刑天口罩`。该桥接只解决名称呈现，不证明 pool、slot、服务器 selector 或概率；后四者仍须各自原始行链闭合。
- 已将两条用户许可桥写入 simple-survival fixture，并要求 `preserve_source_internal_markers=true`。

### 27.67 共享 reward item 续接候选不晋升（2026-09-06）

- 正式服 raw trace 的机械盘点曾给出唯一“可能续接”：`391536 slot 2` 最终 reward group=`[391772,1]`。主模型回放 `391772` 的全部 10 条记录后确认其同时含幸运礼盒、宸世臻藏、蝶影左轮、家具箱和二期菌焰等不同广播/有效期上下文。
- 结论：`391536 → 391772` 仅是 pool ID 被复用为 reward item 的候选，**不得晋升为二期简单生存服子池、不得用于补奖励或概率**。继续坚持活动广播/分支 selector/原始叶子三层分开。

### 27.68 391772→秘宝池静态全排查与分支通道发现（2026-09-06）

用户授权一次 BA8 已解包 25485 条目的精确定位（ULEB 精确编码、只读、不碰 NPK/缓存/网络/UI），排查 391772→390704 二次路由。全部临时探针已删除。

**扫描结果**：391772 与 390704 同现仅两处：
1. `021380 reward_pool_data_base` 主表（各自 pool/leaf 定义）；
2. `017006 reward_pool_no_item_no_list` key=391054 值区内，但两者相隔约 6000 字节、分属不同子块，且 391054 为幻钻晶梦/星河龙焰等跨活动复用池 → **不构成引用关系**。

**随后逐表排除（全部原始解码）**：
- kj1/kjxq reward_pool 覆盖行表（012386/023115，各 237 行 0 unbound）：391533/391536/391772/391782/391785/390704 六池零行；
- lottery_big_reward_conf（006173，1314 行）+ lottery_big_reward_index_data（002571）：8 个目标 ID 全零命中；
- common_item 35986 行：391772/391783/刑天面甲/飞影锋眸/两召唤器 leaf 全不在道具名册（不可用道具名给它起名）；
- 391772/390704 均非两张 big-reward 表的 key。

**分支通道关键发现（正面结果）**：BA8 `super_fashion_lottery_conf_data` 主表与 kj1/kjxq 变体在 **key=232（铠甲二期面板，10 项一致）** 上分化：
| 通道 | lottery_id | fortune_bag_dct |
|---|---|---|
| 主表（与经典服同 SHA，trace 已证） | 391782（池含菌焰典藏/雨战） | {4: 391783} |
| kj1 变体（012545） | 391785 | {726: 391786} |
| kjxq 变体（004258） | 391785 | {726: 391786} |
- 但 391785（24 行）/391786（6 行）主表池行**均无铠甲内容**（391785=虹神北斗/宸世臻藏等复用；391786=天国家具/纳米复用）→ 分支在活动配置行已分化，被引池的静态内容缺失，**实际发奖组合只能由运行时 selector 决定**。
- `391536` 主表 16 行二期 cohort（无菌焰、含珍匣触发 [391772,1]、prob 0.03706）仍是与「简单服锚点稀有+普通」最接近的静态池，但缺飞影锋眸/能量电池/酸焰核芯/1型记忆材料 4 项，且无活动配置行引用证据（kj1 row224 lottery=391535 的面板非铠甲，391535→391536 的 +1 映射纯属猜测，禁止使用）。
- `390704` 二期 cohort 9 项+prob 仍是秘宝内容最匹配；飞影召唤器 [633080140,1] 在 lottery_big_reward_conf row 20413 注册（但该表不含 390704/391772，不能证明其为 390704 slot）。

**结论（停损）**：静态侧「勇士珍匣→秘宝池」路由未闭合；BA8 已解包表内不存在 391772→390704 结构性引用。分支 selector 的静态形态 = super_fashion 活动配置行（主表 vs kj1/kjxq），但被引池内容静态缺失 → 该缺口属于运行时 selector 通道（todo kaijia-runtime-selector），不继续扩静态扫。验收 fixture 三池门禁保持未通过状态。

**补充（common_lottery 侧阴性）**：`common_lottery_conf_data` 主表（008644+000035，371 行 0 unbound）中 391782/391785/391535/391536/391533/391772/390704/391786/391781 全不在行 key；kj1/kjxq 覆盖表（000675/021903，各 2 行）只含 key 4/117 货币次数配置。→ `lottery_id` 无中间映射表，super_fashion 直接引用 reward_pool 池 ID；「活动行→池」引用链缺口维持。


### 27.69 双源对比收口 + 抽奖定位链方法论文档化（2026-09-06）

用户质疑「拆完整/拆对了吗」，主模型认账后补齐三类漏检，全部只读原始解码：

1. **正式服侧 kj1/kjxq 变体从未对比** → 查正式服（79c0d06f）manifest：super_fashion 家族只有主表+CHS（022498/014527），**无任何 auto_oversea 变体**；BA8 主表 012591 与正式服 022498 同 FID（7E5A5A83B1F07D31）同 SHA = 同一文件。
   **结论**：kj1/kjxq 变体 = BA8 测试服专属覆盖通道（把 key232 指向 391785/{726:391786}），主表（两服同）key232 → 391782/{4:391783}。之前「kj1=简单服通道」从假设升级为有正式服侧实证的结论。
2. **reward_pool 家族未探文件**（010551/023391/023705/010219/023723）→ 全部 0x73+`{` 无 `x{` = CHS 文本池；行表只有 021380 一份（两服同 SHA）→ reward_pool 行侧无分支，通道差异只在文本池层。
3. **fashion_sale_conf_data**（001388+001940，75 行 0 unbound）→ 目标池零引用。8 表 + 变体 + 相关表至此全覆盖。

**fortune 语义修正**：0x36 正确解析后，主表 {4:391783}=铃兰福袋系、kj1 {726:391786}=天国家具系，均无铠甲内容 → fortune_bag_dct=「福袋附加小奖池」，**不是秘宝/珍匣入口**（此前表述有歧义，以此为准）。

**收敛图景**：四张铠甲内容池（391782 有活动行引用=经典侧；391533/391536/390704 无任何活动行引用=孤儿）＋测试服覆盖指向的 391785/391786 静态为空 → 断点唯一且精确：**测试服当前发奖组合=纯运行时下发**。静态侧已到终态。

**产出**：新增 `docs/LOTTERY_CHAIN_LOCATOR.md`（v1）：分层模型 L0-L4、双源分支判定法（FID 同=同文件/变体存在性对比/结构先验）、表族档案（super_fashion/reward_pool/common_lottery/fashion_sale/big_reward/no_item_no_list/common_item 各文件角色）、铠甲二期已闭合/未闭合对照、验收门禁、可复用工具链。后续任何抽奖定位按此文逐层走。

### 27.70 铠甲再临二期双分支板发布（2026-09-06，commit 6381039）

用户拍板方案 A（双分支+候选池行带概率）。rebuild_kaijia_panel_static.py 重写为双源/双分支：

- **经典服分支（item 232-classic）**：super 主表 key232（与正式服同 FID 7E5A5A83B1F07D31=同一文件）→ lottery 391782；pools 列出该池 exp 1801353599 本期实例 3 行（菌焰典藏 slot0 0.00163 / 菌焰雨战 slot1 0.00253 / 新币 slot3 0.14528，prob_note 原文保留）；面板 10 项 rewards 保留在本卡（两服同面板）。fortune {4:391783}=福袋小池（非秘宝）。
- **简单生存服分支（item 232-simple）**：kj1/kjxq 覆盖 key232（BA8 专属，正式服包无变体）→ lottery 391785/fortune{726:391786} 标 static-empty（发奖组合=运行时）；孤儿候选池 391536（16 行含珍匣触发 slot2 0.03706）与 390704（9 行）全部行带 prob_note 上板，池名强制含「候选/未闭合」，activity_pool_refs 记 candidate-only 与缺口（缺飞影锋眸/能量电池/酸焰核芯/1型记忆材料/飞影召唤器 slot+prob）。
- **展示名桥仅两条许可**：火刑电光炮→火刑裁决、刑天口罩→面饰：刑天面甲（board.html pools 渲染 display_name + 内部标记并列 + prob_note，概率 6 位去尾零）。
- 修 decode_table_rows 对 kj1 表漏 8 行（18/26）→ 统一 decode_table_rows_with_chs_slots；test_bindict_chs_slots 适配 load_registered_source(source_id) 签名。
- 验证：专项 4/4（含发布契约）、全套 42/42 OK、build_wiki 成功（板 2 条）、主页卡片渲染验收、node 加载板 js 断言。git 6381039（含 27.59-27.61 已验收遗留收口）。
- 边界（板上注明）：候选池≠简单服当前奖池；概率=reward_pool prob_note 配置概率；经典服完整三池锚点未提供→仅列被引池实例行。

### 27.71 面板未回填清零：reward_pool note 名称层（2026-09-06）

用户问"为什么还有未回填"→ 查实仅 2 项：194190（火刑战驱）/633070140（刑天变身器）。两者不在 common_item（道具层）也不在 gift_data，因 ID 属战驱/外观命名空间（同武器皮肤不在道具表）；旧版靠 config_work CSV 中间产物补名，双分支版改纯 NPK 直读后 CSV 层移除但未补等价层=回填链缺层（非全道具总表问题）。
修复：name_for 增加 reward_pool_data_base 二期池行 note 名称层（leaf item_id==面板 item_id 的结构匹配），链序 user > gift > common_item > reward note > 未回填；134061/132694 保留 gift「禁交易」名。面板 10 项未回填清零。测试补防回归断言（194190=火刑战驱、633070140=刑天变身器、633080140=飞影召唤器）。专项 4/4、全套 42/42 OK。

### 27.72 帝皇铠甲一期奖池定位链（侦察闭合，2026-09-06）

用户新任务（一/三）：基于铠甲二期方法论定位帝皇铠甲（一期）奖池。BA8 reward_pool 全表关键词侦察 + 聚焦提取：

**实例 cohort**：广播「在帝皇铠甲活动中获得」行统一 exp=1800143999（**2027-01-17 07:59:59 过期**，紧邻二期 1/31）——BA8 快照预装 2027-01 帝皇→二期连续档期（与历史汇总 2026.08.20 一期正式服轮不同轮次，不混称）。

**活动配置行（super_fashion 主表 vs kj1 覆盖再次分化）**：
| key | 主表 lottery | kj1 lottery | 备注 |
|---|---|---|---|
| 223 | 391513 | （kj1 无此行） | 主表独有 |
| 224 | 391514 | 391535 | 面板不同（主表含 131216 银翼号背包礼盒） |
| 230 | 391762（fortune jump:342） | 391767（fortune jump:11） | 面板相同 [467620,194180,1110151,660056] |

**帝皇池族 8 池 / exp=1800143999 全量 57 行**：391762（18 行完整池：帝皇裁决/瑞昭交易盒+蛛螯配方+核芯+能量电池/微晶/记忆材料/残页/纳米/自选箱=主池结构）、390699（18 行：帝皇广播 9 行=裁决/瑞昭交易盒+涂装苍风青翼/盾甲金牛/医疗无人机+无广播普通行）、391513（7 行含待取名 391763 0.02084=帝皇铠甲本体候选）、391514（6 行：帝皇铠甲/铠骑/极光剑/战翼 4 交易盒 0.14815/0.13333/0.20833/0.00911+双核芯）、391535（4 行：帝皇铠甲/极光剑交易盒 0.15686/0.18519）、390716/391760/660078（各 1 行）。帝皇铠甲本体=leaf 391763/391768（39xxxx 触发物，同珍匣模式）。

**未闭合**：面板→池档位精确对齐待收口（key224/230 面板与池内容部分重叠=复用池多活动共享行）；帝皇奖池无用户锚点（二期才有 10/14/6 名单）；无「帝皇盾/帝皇腰带」行命中（2026.08 一期内容清单里有，2027-01 轮未见=可能是另一期/另一渠道）；kj1 侧帝皇主池（391535 之外）覆盖关系待续。

### 27.73 帝皇铠甲一期双分支板发布（2026-09-06）

用户方案 A：帝皇按二期同构双分支板发布（无锚点验收、2027-01 档明确标注）。

新板 lottery_emperor_panel_static（15 板 / 45491 条），manifest 与二期同格并立：
- classic（emperor-classic）：主表 key223→391513(7 行)/key224→391514(6 行，帝皇铠甲/铠骑/极光剑/战翼 4 交易盒 0.14815/0.13333/0.20833/0.00911)/key230→391762(18 行完整池)；refs 注明 key230 fortune {335:391764}=宸世臻藏青龙池（非帝皇内容，语义 unresolved）；主表面板 [106427,105276,241867,131216] 与池部分重叠=档位未逐行对齐。
- simple（emperor-simple）：kj1 key224→391535(4 行)/key230→391767(3 行普通)；孤儿候选 390699(18)/390716(1)/391760(1)/660078(1)；key223 无 kj1 行=absent-in-kj1。
- 二期池零泄漏断言（391536/390704/391782/391533/391772/391783 隔离）；prob 全 prob_note 原文；每行 config_exp=2027-01-17。
- 验证：专项 3/3（含发布契约与二期隔离）、全套 45/45、build_wiki 15 板、主页双卡并立验收。commit 见 git log。

### 27.74 抽奖板块单卡多活动子卡定版（2026-09-06，commit 1c1f03f）

用户两次纠正：帝皇期不应在首页独立成卡；「抽奖、转盘、不放回抽奖」=一张卡（一个板），帝皇一期/再临二期=卡内活动子卡，**以后所有新抽奖池一律作为该板 items 追加（活动×双分支=每期 2 item）**，禁止另开新板新卡。

执行：
- lottery_kaijia_panel_static 板 items 2→4：emperor-classic（391513/391514/391762，7/6/18 行）+ emperor-simple（391535/391767+孤儿 390699/390716/391760/660078，4/3/18/1/1/1 行）+ 原二期 2 item；meta.name=「抽奖活动（帝皇一期 · 再临二期） · 双分支定位」。
- lottery_emperor_panel_static 板 retired（JSON 留档），独立脚本/测试/js 删除（内容已吸收进 kaijia 脚本的 emperor_section/emperor_classic/emperor_simple）。
- 测试：kaijia 专项 5/5（活动子卡顺序/帝皇行数与概率/隔离/契约），全套 43/43；manifest 14 板块 45491 条；主页验收=单卡。
- 架构规则已写入 lifeafter-wiki-boards skill（单卡多活动子卡+禁开新板新卡+已犯错误示例）。

### 27.75 宸世臻藏（exchange）名称回填（2026-09-06，commit d85fa75）

任务（二）首轮：1757 静态格子中 887 已回填（329 唯一名），回填链=detail.item jump 组首值 → common_item_data_base 名册名（同快照，with_chs_slots 解码；1948 schema40206 unbound 为已知保留不 raise）。
- 命中示例：shop1/slot130 → item 151784=1型记忆材料；9845=保密级配方资料。含币制格（乐居币/领章币/迎新币/次元币=item 字段指向币 id 的行也如实回填）。
- 未回填 870：851=detail.item 指向币制/内部码/外观类 id（不在道具名册，item_id 字段保留供查）+19=detail 解析失败。语义纪律：notes 不含「在售/定价/币种/上限」词（测试锁定），名称=静态名册标签。
- provenance：source_entries 扩为 4 FID（exchange base/chs + common_item base/chs），field_refs 带 common_item_data_base.key=N。
- 验证：exchange 专项 OK（named>800、样本 151784、未回填 name_source=No item-name join）、全套 43/43、build 14 板 45491 条。

### 27.76 预告专栏（零栏）双卡拆分（2026-09-06）

用户方案 A 全收。零栏从纯说明占位改为 data-wiki-group 注入两子卡（16 板块 / 45519 条）：
- （1）武器皮肤-仅行为资源未上线（skin_behavior_preview，3 条）：weapon_skin 板筛 version_status=「仅当前 BA8 行为资源」深拷贝（1110184/1110186/1110190，无父项/道具行/名称，official_name_status=no_item_row）。
- （2）新奖池活动（future_lottery_preview，25 实例）：reward_pool 扫 exp>2026-09-06 且广播活动名，聚类（活动名,exp）时间窗 2026-09~2027-12；排除已发布主题（帝皇/铠甲再临/宸世臻藏/无人机抽奖/战备工坊）与测试行；每实例=活动名/过期日/行数/池集/note 样本/首行 row_key（契约）。含历史返场与未来新档，板上明示「是否测试服独有新内容须对照历史汇总逐条判定」。
- wiki.html 零栏 grid 加 data-wiki-group 并更新说明卡（两子卡口径）。
- 验证：preview 专项 2/2（含发布契约）、全套 45/45、主页零栏双卡验收。

### 27.78 满减市场板（三）发布 + 外观锚点→活动载体定位链（2026-09-06）

用户以「灵笼满减补贴」活动锚点（白月魁交易盒/浮游炮/清镜识微/噬极）要求定位满减活动并沉淀可复用链。多轮侦察闭合：

- 活动目录（huodong_conf kj1 858 行）：满减两代——旧 ManJianHuoDong「满减市场」（2023-11~2024-06 三档，manjian_market_goods 101 行材料商品 kj1/kjxq 同）+ 新 DiscountMarketHD「满减补贴」（2025-04~2026-06 七档：南疆/流萤/青白/丹枫/鎏金/**灵笼 3402**/簪花）。
- 锚点名册链：白月魁交易盒=gift yk 增量 136388（desc 唯一直接引用「灵笼满减活动结束后可交易」）；浮游炮=common_item 640041（灵笼投影）+buff「伴身投影·浮游炮」；清镜识微=player_appear 492700+6 时限变体（白老板同款眼镜）；噬极=weapon_skin 1110156 喷火器皮肤（噬髓腐蚀/噬炎蔓溢）。
- **载体缺失结论（双重印证）**：DiscountMarketHD 商品定价表 BA8 模块名 0 命中；四锚点精确 ULEB 全条目同现 51 文件全为名册/公告/交易/行为存在性表 → 商品载体静态缺失=运行时。
- 交付：manjian_market_panel_static 板（10 期+4 锚点=14 items）挂奖池（三）满减市场；主页占位重排（四）神秘商店/（五）核芯/（六）芯片；docs/LOTTERY_CHAIN_LOCATOR.md 增 §8 外观锚点→活动载体定位链（名册反查→活动注册→同现扫→锚点直接引用→半闭合交付）。
- 验证：满减专项 2/2（含禁词/契约）、全套 47/47、17 板块 45533 条、主页验收。

### 27.79 锚点归属校正：灵笼满减补贴子卡（2026-09-06，commit f57d8d8）

用户校正：四锚点（白月魁交易盒/浮游炮/清镜识微/噬极）是**灵笼期内容**，原满减板把它们作为 4 个顶层 item 平铺=归属错误。

修正：满减市场板 items 14→10（仅活动期次子卡）；四锚点并入「灵笼满减补贴」期条目内（4 行「锚点：XXX」kv，含名册表/key/desc 摘要），其 provenance.source_entries 合并 6 个锚点表 FID（去重），field_refs 加 4 条锚点明细。测试断言锚点字段/合并 FID/无顶层 anchor item；gate 条数 10。全套 47/47。教训：锚点按主题归属活动期子卡，不按渠道板平铺。

### 27.80 神秘商店板（四）发布 + 返场锚点收齐（2026-09-06）

神秘商店=RandomDiscountHD（随机折扣店）。BA8 静态 3 期（2024-01/04/06）+UI 映射（016741 神秘商店↔RandomDiscountHD）+商城标签（new_store_tag）+推送活跃。
用户验收返场锚点 4 件并入：冰蕊银华（初始=黄金年代 453529/公告；名=冰锐银华同物）、桂月清辉/热血学院/月色咏叹调（初始=直售/礼盒/自选箱名册）。机制佐证：刷新币 common_item 153535-153538 desc（name 槽漂移已注）。
**返场/商品载体表定位结论**：RandomDiscount 商品表 BA8 模块 0 命中；活动行无商品引用字段；黑市表=资源交换非神秘商店；store 族无关 → 商品清单=运行时（同满减模式）。测试 2/2+全套 49/49+18 板块。commit 见 git log。

### 27.81 限定核芯研制（五）+限定芯片保底（六）半闭合结构板（2026-09-06）

- 核芯研制=NucleusLotteryHD 10 期（huodong）+nucleus_lottery_pool_data（kj1 003119+014033 355 行 0 unbound）：研制池→reward_pool_id 引用+is_guarantee+权重+显示组（极品/基础异变核芯）。
- 芯片保底=BeltChipSpecialLotteryHD 27 期+special_chip_lottery_hd_conf（30 行：金芯片保底 80/总保底 170-180/折扣 0.9）+rule（60 行：组保底 80/单奖 2）。
- 两板=期次目录+表族结构半闭合：当前期启用 conf/池=运行时（快照 2026-09 无后续排期）；不用历史期序预测当期。占位（五）（六）转正（audit 全清，奖池 6 格全为板）。
- 验证：专项 3/3、全套 52/52、manifest 20 板块 45572 条。commit 见 git log。

### 27.82 核芯/芯片板内容层增强（2026-09-06）

用户纠正：板不能只有卡没有内容。增强：
- 期次子卡 name 带日期窗口（如「限定核芯研制（2026-04-30~2026-05-14）」）+extra_param 期号+sub_title。
- 核芯板新增「研制池族内容」item（71 个研制池：配置行数/保底行/显示组/权重样本+外围奖励池行展开 note@slot(prob)）。
- 芯片板新增「期配置内容」item（30 期配置：ui_id/金芯片保底/总保底/折扣率/UP 芯片组 id/新芯片组/活动池组）+规则组展开（60 行 rule：池→组→保底→奖励组 id）。
- 边界保持：研制 UP 核芯本体与当前期启用=运行时（display group 面板语义）；芯片 id 数值名称 join 留待后续。
- 验证：专项 3/3、全套 52/52、manifest 20 板块 45574 条。

### 27.83 芯片板名称层 + 8 返厂结构确认（2026-09-06）

common_item 名册 join：UP/新芯片与 rule 保底物 id→名（330014=连环暴击/331013=从容不迫；240807=连环暴击自选箱…）。
结构确认：新格式期（ui_id=20，key13 起金保底 450/总 180）UP 芯片组=**8 款**（=用户口径"每期返厂 8 个"）；旧格式期（ui_id 8-19，金保底 80/总 170）UP=2 款（新芯片）。331018/331026 等 common_item 无名（名册外/槽位问题）保留原始 id。核芯研制"新+返厂"期次细分与芯片返厂 8 列表的完整面板映射=按用户指示静态先做到保底物+UP，返厂面板确认后补。

### 27.84 芯片板重构：每期子卡=当期全部芯片（2026-09-06）

用户口径：新芯片期约 1 个月、老核芯/芯片返厂期约 2 周；要求芯片子卡写全当期所有芯片。
huodong 期 sub_title 直标期型：全新特级芯片/强力特级芯片/**特级芯片返场**（extra_param=期序号）。
重构 chip 板（29→32 items）：
- 30 张「芯片期 N（uiX · 保底 Y）」子卡（conf 30 行每期一张）：当期芯片（UP 返厂组，新格式 ui20=8 款：雷霆一击/连环暴击/荆棘护盾/异变赋能/高能弹匣…；旧格式=2 款）+新芯片组+保底奖励（rule reward 保底物名：旧格式=「XX自选箱」240807 连环暴击自选箱等；新格式=241405 限定特级芯片自选箱）+金芯片保底数/总保底/折扣率/活动池。
- 「活动期次目录」：27 期时间+期号+全新/返场标注（conf 无时间字段，不强行对齐）。
- conf↔huodong 期映射未建（时间域不同），如实标注。
验证：专项 3/3、全套 52/52、manifest 20 板块 45577 条。

### 27.85 芯片期子卡带时间 + 去鬼卡 + 问号溯源（2026-09-06）

- conf key = huodong extra_param - 2 映射（rule 池号=key+2=extra_param 三点自洽：key1→池3→extra3 首期 2023-10-26；key13→池15；key30→池32）→ 30 张期子卡名称带活动时间窗（芯片期 13（2025-01-09~2025-02-12 · ui20 · 保底 180））；key28-30 无对应 extra=标未排期。
- 删除「表族结构」鬼卡（芯片板 32→31 items）；「期配置内容」早前已并子卡。
- 问号溯源：331018/331025/331026 在 common_item 与芯片图鉴均无行（331 段名册仅到 331017）→ 名册真实缺口（非回填链 bug）；NPK 名册链解析正确（330xxx/331001-017 全命中）。
- 验证：专项 3/3、全套 52/52、manifest 20 板块 45576 条。

### 27.86 芯片期错位修复 + 目录可读化（2026-09-06）

用户指正：期次标注错位 + 目录不可读（"没滚"）。
根因：chip huodong 期 extra 序号在 extra23 处被核芯期插号（非连续）；conf key=extra-2 前 20 期碰巧正确、第 21 期起整体错位 1（key21 误标"未排期"）。修复：conf key n ↔ 芯片期时间升序第 n 期（序号对齐）。验证点：期21=2025-11-27~12-11（extra24）、期27=2026-07-16~08-06（连环暴击返场）。
目录可读化：period-directory 由 27 行数组（fmtVal join 挤成一行）改为逐期 kv 行（每期：日期区间 | 活动名 · 全新/强力/返场标注 · 期号）。
验证：专项 3/3、全套 52/52、manifest 45576 条。

### 27.87 芯片期 key=extra 映射（用户校准）+ 用户补名 + 目录卡删除（2026-09-06）

用户校准错例：芯片期 30=2026-07-16~08-06 连环暴击返场（=extra30 期）→ conf key=extra_param 值（key1/2=BA8 未注册更早期，标"快照无期次"）。
期 30 当期 8 款（连环暴击/覆盖打击/好事成双/势如破竹/全副武装/坚如磐石/坚韧不拔/荆棘护盾）与 key30 UP 组全对 → 同时用户补两枚名册缺名：331026=坚如磐石、331018=坚韧不拔（USER_CHIP_NAMES 层）。
删「活动期次目录」子卡（时间/标注已入各期子卡）。芯片板=30 张期子卡。
**双服差异预告（用户校准）**：芯片返厂两服不同——30 期经典服=破盾强攻、简单生存服（BA8）无破盾强攻换连环暴击；BA8 conf=简单服配置。待双源对比（正式服 conf）。

### 27.88 芯片返厂双服差异标注（2026-09-06）

用户校准：芯片返厂两服不同（30 期：经典服=破盾强攻、简单服无破盾强攻→连环暴击）。
双源核查：正式服包（79c0d06f）manifest/尾部模块名 0 命中 special_chip/belt_chip/chip_lottery → special_chip conf/rule 为 BA8（简单生存服测试包）专属打包表；经典服同期名单=服务端运行时（不可静态读）。
板 notes 增加双服差异说明（本板=BA8 简单服配置；经典服同期不同且不可静态读）。核芯/芯片板结论保持。

### 27.89 核芯板鬼卡移除（2026-09-06）

用户指示：核芯板「表族结构（保底/权重语义）」「研制池族内容」两卡删除。
rebuild 清理：nucleus 板=10 期次子卡（日期/期号/sub_title）；共享生成器去除 structure/content 构建（含一次误植修复：nucleus 内容块曾错挂 chip 分支，已行级删除并编译验证）。
核芯本体（新 UP/返厂）仍=运行时（等待用户游戏内名单后继续）。
验证：专项 3/3、全套 52/52、manifest 45573 条。

### 27.90 核芯期名占位揭示 + 凝滞侵袭锚点（2026-09-06）

用户锚点「限定核芯研制 凝滞侵袭返场」：
- 凝滞侵袭=异变核芯-凝滞侵袭（660072，特级，狙击枪 5，nuc_1079）已入 77 核芯全集。
- 揭示：BA8 kj1 覆盖把核芯 9 期 sub_title 全置「电掣双刀返场」（重复占位，非真实期名）；真实期名（UP 核芯名+登场/返场，如凝滞侵袭登场/返场、凤凰幻彩典藏等）在 yk 运营文本池（001445），BA8 无 yk base 行级对齐不可达。
- 核芯期次卡：sub_title 保留并附 sub_title_note（注明 kj1 占位/真实期名在 yk 层），防误导。
- 每期 UP 核芯本体仍待（真实期名↔核芯名映射可推：期名=UP 核芯名，登场=新/返场=老；凝滞侵袭返场期=当期（2026-09，BA8 2026-05 截断未含））。
验证：专项 3/3、全套 52/52、manifest 45573。

### 27.91 核芯 UP 期名样本 + 用户校准补录（2026-09-06，commit e814f53）

用户校准：登场=新核芯首次出（约 1 个月期）；返场=老核芯回归（约 2 周）；**同名返场可多次**（电掣双刀返场不止一期）→ yk 文本期名不可逐期归属。
核芯板=10 期次 + 「UP 核芯期名样本」参考条目：期名模式（登场/返场）+yk 文本 10 样本+用户锚点核芯（凝滞侵袭返场 660072 当期/电掣双刀返场 660044/穿心极雷返场 660077）+全集指引（（二）核芯卡 77 条）。锚点核芯全集落位：电掣双刀=660044 特级冷兵器、穿心极雷=660077 特级霰弹、凝滞侵袭=660072 特级狙击。
验证：专项 3/3、全套 52/52、manifest 45574（核芯 11 条）。

### 27.92 核芯/芯片期全量修复：huodong 源换 ykxq 主表（2026-09-06）

用户连续纠正"期数不对/不止这几期/中途还有很多期"——根因：此前一直解 kj1 覆盖表（025079，858 行=后期子集），真实全量=ykxq 主表（024329，1382 行 0 unbound）。
- 核芯研制（NucleusLotteryHD）：**72 期**（2023-08-04 ~ 2026-09-16），sub_title=真实期名：凝滞侵袭返场（extra73=2026-09-03 当期，用户锚点命中）、电掣双刀返场 ×10、穿心极雷登场/返场多次、酸焰激流/极光狙击/决斗时刻等多轮——用户"返场不止几期/双刀多次"全部坐实。
- 芯片抽奖（BeltChip）：**30 期**（2023-05-25 起）=conf 30 行 1:1；key30=2026-07-16~08-05。
- 双服差异实证：huodong 期名（ykxq 主表两服共享）=「破盾强攻返场」（经典服）；BA8 special_chip conf（简单服覆盖）=UP 连环暴击 8 款——与用户校准完全一致。
- 移除全部 up_candidate/占位推测字段与 kj1 覆盖占位逻辑（用户多次要求无关内容清零）。
- 验证：专项 3/3、全套 52/52、manifest 20 板块 45635 条（核芯 72/芯片 30）。

### 27.93 定位链文档更新：通道层级铁律 + 核芯/芯片链（2026-09-06）

LOTTERY_CHAIN_LOCATOR.md 新增 §9（核芯研制/芯片保底定位链）：
- §9.1 通道层级铁律：活动类结论必须以 ykxq 主表（024329，1382 行 0 unbound）为准；kj1（025079，858 行）=后期覆盖子集（核芯 kj1 10 期 vs ykxq 72 期）；kj1 sub_title 覆盖 bug 实证（9 期复制电掣双刀返场占位）。行数对不上先怀疑通道。
- §9.2 核芯研制链：huodong ykxq 72 期（sub_title=UP 期名：登场=新核芯首出/返场=老核芯回归，同名多轮）→ 期名去缀=核芯名（凝滞侵袭=660072）→ 660000 段全集 77 卡/350000 词条；研制池族 nucleus_lottery_pool_data（355 行）为外围奖励层。
- §9.3 芯片保底链：BeltChip 30 期 1:1 conf 30 行；conf up_chips（新格式 8 款返厂/旧 2 款）+rule 保底物（240807 连环暴击自选箱/241405 限定特级芯片自选箱）；名册 330xxx+331001-017（67 卡），331018+ 名册缺口。
- §9.4 双服差异判据：活动期名看 huodong（两服共享，经典视角如破盾强攻返场）；当期内容/UP 名单看 conf（BA8 专属=简单服；经典服运行时）。
- §9.5 验证锚点：核芯凝滞侵袭返场 extra73 当期/双刀×10/穿心极雷；芯片 key30 8 款名单+2 用户补名。

### 27.94 Wiki 首页与子页轻量可用性优化（2026-09-06，未提交）

- 作者：Hermes；模型：gpt-6-astra（openai-codex）。范围仅前端、测试与本文；证据等级：代码运行回归已验证，非游戏业务结论。用户已确认“首页＋子页交互”范围，附件保留原样。
- 首页增加 manifest 级板块搜索（不加载各板大数据）、清空/空结果提示、零一二三四分类快捷跳转。保留原分类序号、单卡与活动子卡组织；改中性卡面、窄屏单列、键盘焦点；详细发布纪律和预告说明折叠，关键非当前可得边界常显。顶部来源说明改为各板实际记录为准，不再声称全站均为 BA8 单源。
- 修复隔离统计误算：按 publication_status 分开计数，当前实读为 published20 / quarantined11 / retired2 / unpublished2；不能用 policy总数−manifest数称“隔离”。
- 子页：搜索160ms防抖、中文组字时不刷新；核芯/奖池展开头加键盘Enter/Space、tabindex、aria-expanded与可见焦点；脚本缺失/数据对象格式不完整给明确加载失败提示，不当空表。未改变条目过滤范围、数据内容和概率/名称来源。
- TDD：新增 tests/test_frontend_usability.py，先见旧统计、缺键盘能力、快捷导航乱序RED，再GREEN。旧 publication_gate 的 for-in 语法字符串断言随显式排序循环更新，分类约束不变。最终 unittest discover：54/54 OK；另有测试HTTP读取中 ConnectionAbortedError/WinError10053警告，未改服务端；unsafe.json拒绝生成是预期负例。
- 桌面预览 read_preview 已确认20张已发布卡、状态统计、搜索与折叠说明可见；Node vm执行实际前端验证搜索/清空/空结果/导航序、键盘展开收起、防抖与缺文件/缺全局对象分支。自动浏览器9222受WinError10013阻断；8765当前拒绝连接，未重启。未宣称真实浏览器交互或像素级视觉验收完成。
- 未执行board重建/build manifest、未改data或原始客户端、未推送/提交。全套现有测试包含只读源验证与临时HTTP测试，不是新拆包侦查。简单静态检查已委派Luna，业务裁决不委派。

### 27.94 富文本染色渲染（2026-09-06，任务五）

board.html 新增 richText()：解析游戏富文本 #f(N)（色段，N=色号近似映射 5=高亮金，可校准）/ #cRRGGBB（hex 色段）/ #r（换行）/ #n（复位）/ {0}（变量保留显示）；esc 先行防注入。
接入：核芯特技 skill_desc（nucleus-desc）与全部含色标的 kv 文本行（isRichText 门限 8000 字符）。
验证：node vm 真实执行 richText——用户示例（酸蚀渗透技能文本）全断言通过（f5 金色/{}保留/#r 换行/#n 复位/esc 安全/hex 色）；纯文本无标记原样输出。核芯卡（(二)）视觉=核芯特技染色+换行段落。

### 27.95 战力类重排 + 服务器筛选（2026-09-06）

用户定稿战力类排列：（一）武器（二）护具[先搁置]（三）核芯（四）芯片（五）无人机[先搁置]。
- policy/board meta category：nucleus_cards_classic（二）→（三）核芯、chip_item_catalog（三）→（四）芯片（weapon_attrs_schema_static 已在（一）武器）。
- wiki.html：占位卡按 catSeq 与真卡混排（AUDIT 注入改 cards.sort）；战力占位=（二）护具（头盔/护甲/护盾，先搁置）+（五）无人机（先搁置）。
- 服务器筛选：核芯卡板 meta.filters=[{server_branch,服务器}] → 板内自动下拉（全部/经典服/简单生存服；76 经典+1 淬焰燃锋简单独有）。机制=board.html _custFilters 现成（meta.filters 配置），后续有服字段的战力板同法接入。
- 武器 3 板（weapon_skins/attrs/new_textures）保持隔离——实证复验：skin id join common_item 全命中但全错名（1110001=钴天蓝天花板=家装段），皮肤表 id≠道具表 key=隔离 reason 坐实；修复=独立战役（后续）。
- 测试 57/57（3 处过时断言随前端改动同步：css grid/input 规则、占位（四）→（二）/（五）、append 写法）。

### 27.96 武器旧 3 板删除（2026-09-06）

用户决策：直接删掉武器旧 3 板（以后重新搞）。
删除：weapon_skins/weapon_attrs/new_textures（board json + 根静态重定向页 + quarantine_legacy_html 归档 + tools/export_* 旧导出器 + policy 注册条目）；保留 weapon_attrs_schema_static（all_equips→schema6109 结构地基卡）。
隔离实证（入库前因）：皮肤表 id≠道具 key（1110001=钴天蓝天花板家装材料）等三条 reason 见 policy 历史。
测试：legacy 重定向断言去 weapon 2 项、quarantine 计数 11→8（frontend node 断言）；57/57 全绿。
policy 32 板注册（20 published / 8 quarantined / 2 retired / 2 unpublished）。架构图 docs/wiki_architecture.html 同步。
重做清单（待）：weapon 皮肤名册同键源、本体数值行名对齐（all_equips 错位）、贴图 DDS 路径桥接。

### 27.97 项目目录精简（2026-09-06）

清理（工作区 ~297M→~40M 外 git）：
- assets/textures/独有新武器候选 230M（324 张 DDS PNG，旧 new_textures 板素材）——用户确认删除（BA8 源可重提取）
- data/app（skin_data/new_textures_data.js）+data/source（skin_library.json/weapon_独有dds清单）+data/exports（weapon CSV）=旧武器管线孤儿（无活动引用，git 可恢复）
- 根散件 probe_py3.py/effect_show_row_level.json（git 内）
- "08lifeafter wiki构建.md" → docs/legacy/构建规划-20260831.md
保留说明：data/boards json+js 双格式=架构性（json=生成器真源/js=file:// 浏览器加载），未拆；.git 367M 历史体积另议。57/57 绿。

### 27.98 通道侦察器固化（2026-09-06）

tools/scan_table_family.py：新表族侦察第一步工具。扫 BA8 尾名 → 全通道变体清单（文件/x{ 长/归类/FID）→ 主表建议（ykxq 优先=27.92 铁律固化；kj1/kjxq 覆盖警告；CHS 配对提示）。--rows=按变体名自动配对同通道 CHS 解码验证行数。
实测：huodong_conf → ykxq 024329=1382 行 0 unbound（铁证）；vehicle_proto 家族发现 ykxq 变体 019849/015924（载具本体数据候选=挂起线索，恢复时 --rows 验证）。
skill：lifeafter-wiki-boards 通道铁律节追加 §13（工具用法+载具线索）。57/57 绿。

### 27.99 双源定位器 v3 + kj1/kjxq 判据修正（2026-09-06）

scan_table_family v3：双源整合（live_sources→正式 npk LiveNpkReader 45687 entry FID 索引→每文件自动标 双源共享/BA8专属+◆双源判定清单）；主族/子族分组折叠；海外壳收敛；CHS 三级回退配对（同变体段→同族试解取 unbound 最低+高 unbound 缺池警示）；--rows/--no-formal。

★判据修正（npk 直读实证，推翻旧结论）：
- kj1 通道=双源同 FID（huodong kj1 025079 FB80FED51B8B4638、ykxq 024329 F394516378015E27、yk 007577、super_fashion kj1 023542 均正式 npk 同 FID）
- kjxq=BA8/测试专属（huodong kjxq 001941 140E2B9B3F7597AE 正式无）
- 旧「kj1/kjxq 只存在于 BA8=测试服覆盖通道」判据作废（来自仅 8 表的残缺正式工作副本）；双源存在性判定必须 npk 直读
- special_chip conf/rule「仅 BA8 打包」同样作废=kj1 通道双源同文件；但「谁启用=服务器差异」（BA8 conf=简单服 UP 连环暴击 8 款用户实证；经典服=运行时破盾强攻）仍成立=存在性≠启用
- skill 双处修正+wiki-boards §13 同步；57/57 绿

### 27.100 定位器 --json/--fid + 解码探针 decode_probe（2026-09-06）

定位器补模式：--fid <FID> 反查（表名/族/manifest FID→文件）、--json 机器输出（hits class/family/fid/formal_present）。
新工具 decode_probe.py：单表第一眼——x{ 容器/头部 marker 分布/parse_index 行数估算/schema 数/标准解码 rows+unbound/前 N 行 dump/两条启发警示：
- 疑似 0x96 宽表（0x96 密集且 0x92 行 marker≈0）→ 字段名可能来自池值文本区（chip_type/nucleus_entry 同族，先验键域）
- 文本槽路径占比>30% → 文本字段跨行错位（all_equips 模式），数值字段才可信
实测：huodong 024329=1382/0（0x92 存在=无误报）；chip_type 1352=78/0 且字段名=芯片名（从容不迫/以攻为守/临危不惧…）+chip_name=icon_330082_s 路径文本=0x96 形态一眼可见。坑：parse_index=0 不代表表不可解（huodong parse_index 空但 decode 1382 全解）；头部字节计数只是启发。57/57 绿。

### 27.101 日志卡点总清理 + decode_probe 键域修正（2026-09-06）

用户指示"把日志里遇到的卡点统统解决优化掉"。盘点现行卡点处置：

【本轮解决/终判】
1. 0x96 宽表键域修正 → decode_probe 自动识别：**中文字段名=池值文本误升为键**（行列式/无名槽设计，chip_type 芯片名列组特征；正常 schema 字段名=英文）。判据演进：0x96 字节计数误报（普通表数据区含 0x96=常态）→ 0x92 行 marker 缺失也误排（1352 有 0x92×383）→ 最终=中文字段名检测（1352 触发/024329 零误报/007998 词条表字段干净不触发）。输出 field_keys_sample+对齐建议（effect_label 类英文字段为锚）。
2. 核芯词条↔核芯关联表卡点 → 终判：type2 词条名（分裂弹片/无尽攻势/背后突袭/快速装填）在核芯 chs 池（023314）0 命中=词条不拼入核芯 desc；nucleus_build_2_nucleus_conf（kj1 016573/kjxq 001406/ykxq 000932 壳族）=单行覆盖（key1088→350081/660081/5）非关联全表；nucleus_build_data 行字段无词条引用 → 词条表=静态孤儿/UI 参考层，核芯特技=desc 内嵌文本已闭环（77 卡用户验收过）→ 卡点归档。
3. 载具链 ykxq 线索排除：vehicle_proto 族 --rows 全验=019849 ykxq 1+1 行、015924（character）3 行、001504 impulse 0+1、021723 主表 51+24=全部物理/角色参数层，无 182xxx/194xxx 名册 → 本体名册表仍缺=载具链维持挂起（唯一解=用户给载具名锚点）。

【已终判归档（不再追）】核芯中间星级数值/词条数值=服务端（用户搁置）；芯片品级色/效果文本=客户端展示层；时装 int name=表内 CHS 全量（无 i18n 层）；背包行级=文本层 79 上限（候选待实机）；selector/consumer 闭环=静态不可达；kj1 判据=27.99 修正版。
【维持挂起（等用户锚点/新版本）】载具本体名册；武器皮肤重做（3 板已删）；面饰细分/挂件边界（用户无法看样本）；帝皇 2027-01 轮面板对齐。

57/57 绿。commit fea5fe8（decode_probe 键域）。

### 27.102 芯片图鉴 v2（2026-09-06，用户"图鉴不全量+没 id+换全量源"轮）

根因澄清（非解码 bug）：331018-27 在 common_item 真无行（35,986 全解=0 漏行；331 段 331017 后整段空）——chip_type 配置引用超前；道具行在更新包/未道具化。inc 增量表（5292）25 行也无芯片。
全量源定位：**chip_type chs 池 003278 中文短名=恰好 65 个=游戏图鉴全集**（用户 UI 65 实证）——旧板 59 道具+8 硬编码=67 条结构错（游戏图鉴无 2 条、8 防御非全在 UI）。
图鉴 v2：主源=池 65 名；id 三层=common_item 道具 56 + USER 锚 2（坚如磐石=331026、坚韧不拔=331018，conf up_chips 引用一致实证）+9 无 id（6 防御配置名 id 静态不可得+爆破专家/愈护屏障/掌控大师未知）；附注=创伤专家/寸长寸强/活力充沛/特攻专家/破盾强攻（道具行有/池无名=游戏图鉴不显示；破盾强攻=经典服独有=简单服池无=27.88 用户校准印证）。family 无道具=未定（不猜）。
技术：conf jump 基准教训复现（铁律：jump 相对去 8+4*count 表头 blob——初解 key30 组全空=基准错 128B；修正后 8 款全出）；1352 effect_label 仅 11 行可解（其余 icon 路径错位）不可作全序；003278 池序≠id 序。
测试：gate 67→65、policy items、全套 57/57。
待补：剩余 4 名（331020/21/25/27）与 9 无 id 中 6 个的名字桥=等用户 UI 或更新包；图鉴后续可加"芯片→期次出现"映射索引（奖池映射优化项）。

### 27.103 芯片锚定破译：331027=寒霜守护、331020=应急防御（2026-09-06）

用户提供经典服 27 期自选界面图（2026-02-12~03-05）。集合论破译：
- 经典服 27 期 8 款 vs 简单服 key27 8 款（conf）=破盾强攻↔连环暴击（27.88 已知替换）+共享 7 颗
- 共享 7 颗 id 一一对应（330035/330042/330040/331012/331014/331018 已知）→ 剩 331027=寒霜守护
- 连锁：期 29 二选一排除寒霜 → 331020=应急防御（紫=图鉴紫区一致）
- 品级交叉验证：寒霜守护金✓/应急防御紫✓（用户防御图鉴截图）
USER 锚层更新（rebuild 两脚本）；图鉴 65=58 有 id（56 道具+4 锚）+7 无 id；期卡 ? 清零。
剩 331021/331025=以攻为守/重整旗鼓（金2，待锚）；330018/330027=格斗大师等（金攻击 16 名单外无 conf）。
方法沉淀：跨服同期活动图=集合论对位（共享颗数=8-替换数；唯一未知=锚）；用户网图可用但要报服与期。
57/57 绿。

### 27.105 工具链优化轮（数据源/定位器/解码器三件套，2026-09-06）

承接 27.104 芯片期校准大战教训（conf 行序≠时间序证伪）——本轮把坑固化进工具与 skill：
1. **数据源层**：新增 tools/announce_calibrate.py=官方更新公告校准源抓取器（curl mrzh.163.com
   news/update 分页→提取「限定芯片自选/保底自选」段=精确起止时间+名单前2名指纹），全量 20 条
   落库 data/external_refs/announce_chip.json（2024-06-06~2025-06-18 每期双服），与板上
   CHIP_TIME_OVERRIDE 逐一吻合=权威外部交叉源（核芯/载具期同法复用）；官网列表保留 ~2 年
   （2024-06 起）、2025-07 后公告不再宣传芯片=锚库边界已注明。
2. **解码器 decode_probe.py 三项硬化**：①x{ 容器形态诊断（假 x{ 序列识别=后跟段偏移表如
   kj1 base 27423 老格式壳；返回 mode=ok/no_x/fake_only 区分，不再拿假容器硬解）；②幽灵行
   检测（key>=200000=测试段——chip huodong key200002=2023-07-13 与 2130 同窗=「期2/3重复」
   根因实证，ghost_row_warning 内置）；③同日重复行检测（日期级 //86400，ts 同日不同秒也可见）。
3. **定位器 scan_table_family.py**：xbody_info 同步硬化（假 x{/老格式壳识别，--rows 老格式表
   报「标老格式勿硬解」而非误导性解码失败）。
4. **skill lifeafter-bindict-decoding 同步**：芯片期时间映射铁律重写（27.104 行序对齐证伪→
   公告锚/用户锚/待校准三态+校准结果表）；芯片锚终态（331021=重整旗鼓/331025=以攻为守=自选箱
   名铁证，早期集合闭合对反教训）；自选箱=期↔名↔id 三合一锚方法论；幽灵行/假 x{ 三坑。
测试 57/57 绿；commit ca63e6b/d492bfd/announce 批次。

### 27.106 宸世臻藏链重建+勘误（2026-09-06，用户「宸世臻藏链全错」）

**勘误**：27.103 载具侦察把 common_exchange_shop_data（通用兑换=商队/集市）的载具格子（194114/
194140/182xxx 共 16-25 格）标为「宸世 exchange」=全错——exchange 板那些行源表=common_exchange_
shop_data≠宸世；宸世臻藏=独立 Optional* 活动体系。
**重建链（LOTTERY_CHAIN_LOCATOR.md §9.6）**：huodong 注册=OptionalLotteryHD「宸世臻藏」（key2538
2024-04-26 长驻框架）+OptionalExchangeHD「臻藏商店/稀世商店」（key2591/2592）+同族
MultiOptionalLotteryHD（2025-07 起 8 期主题时装自选：幻海旖旎/青春变奏曲×2/喵不可言×2/学院企划/
夏日香氛/战备工坊(WeaponDecompOptional 2026-09-03 当期)）；道具链=宸世之钥 153035→宸世宝箱→
宸晶臻石 153036（臻藏商店货币永久）+臻藏时装兑换券 155956；商店表=optional_hd_exchange_shop_data
主表 002962（81.5KB FID 1E888FAB015CA82D 双源共享）+yk 005580；宝箱奖励候选=ext_dynamic 007729
（未解）。载具修正：可升级飞行载具（灰翼游鹰等）随宸世返场=臻藏商店兑换/宝箱=宸世链来源；
common_exchange 同段=通用商店≠宸世。⚠002962 行级=0x76 特形索引（count=32 偏移全 0）=
parse_index 不支持=待工具扩展，商品行未闭不发布。
双服校准器新增 chenshi 链（optional_hd_exchange_shop_data/multi_optional_lottery/optional_version）。

### 27.107 002962 组流攻破 + 宸世卡用户定版（2026-09-06，接 27.106）

**002962 商品行解出（27.106 判「parse_index 不支持=未闭不发布」→ 本批绕行攻破）**：
行=0x76 特形（count=32 偏移全 0 前向索引）→ parse_index 不可用 → 改 **组流扫描法**：
从 0x0b jump 组流直接抽 (货币,价,限购) 三元组流——商品名走 exchange 名册（001345 官方兑换名册）
join 落名，价目组与名序对齐。解出 30 品 = 臻藏 12（宸晶臻石 1/2/5/15/30/50/99 石档）+ 稀世 18
（证档 1~450）；行级 source_entries 挂经典服核验静态 entry 2949（file_id 1E888FAB015CA82D）。
**双服差异实证（写进板）**：时空裂隙=经典臻藏 2 石 vs 体验稀世 50 证；浑天穹焰=经典 35 石特惠
vs 体验 5/1 石——两服货架价目不同，卡内分服标注。

**宸世卡结构定版（用户两轮纠正）**：
1. 「不要拆成一张张子卡…子卡是每期」→ 商品/货币不单列行；
2. 「让这些滚+加时间排序，默认近期到早期」→ 货币 8 行移除（common_item 名册一区已有），
   items=纯期次 28（2024-04-26~2026-08-20），当期内容（公告+双服商店 60 品清单=932 字 desc）
   并入 2026-08-20 期卡；stats.currencies 删、gate 36→28。
3. **board.html 通用时间排序（period_date 自动激活）**：fillFilterSelects 开头
   timeSort=!nucleusSort&&some(period_date) → 「近期到早期(默认)/早期到近期」，隐藏皮肤筛选模组；
   render() timeOrder 分支按 period_date localeCompare 降/升序；核芯 sort_660 板不受影响。
   headless Chrome 实测：控件可见+28 期卡降序（08-20→07-24→06-11→05-14）；node 单测双向互逆。
   以后任何期次板加 period_date 即免费得排序。
commits: f1d968f（002962 解出）/ 9245aa1（36 行定版）/ 26fe516（去货币+排序控件）。
测试 57/57 绿。

### 27.108 宸世商店链勘误（2026-09-06 用户「只有这一期/靠锚点才弄出来/格式全错/定位链弄好没」）

**27.107 的「002962 组流解出 30 品」宣告作废**（启发近邻配对无结构证据=用户核卡发现币种全错）：
1. **币种全错根因**：rebuild 构造写死「石」（稀世店品也标石）；quantity_raw 自带 × 又拼 ×=「××2」；
   核验 JSON currency_name「宸世臻石」=转录笔误（正式=宸晶臻石 153036）。
2. **静态链穷尽实证**：optional_hd_exchange_shop_data 全族=002962(main 81.5KB)+005580(yk)+007946(ykxq)
   两 76KB——yk/ykxq 解出内容与 002962 逐条相同（30 商品同 id 序）=三通道同内容冗余=客户端只有
   **当期单快照**（双服同 FID 同 SHA f2573710…）。历史 27 期商店=服务端期到时下发=客户端无任何
   静态快照=**历史期商店内容静态不可得**（与 27.103 芯片时间同性质：宁空不造假）。
   教训：scan_table_family 的「ykxq=全量主表」判语在该族=误导（通道同内容非多期），通道铁律必须
   以内容对比验证，不能只信变体存在性。
3. **当期两店重做**：撤体验服拆包清单（含 id33/id63309014040证 等死数据）；2026-08-20 期卡拆
   store_zhencang/store_xishi 独立字段（概要直显两行=用户「两店分开别混一期」定版），币种按店型
   固定映射（臻藏=宸晶臻石/稀世=稀世之证）+数量原样+限购全角括号+特惠/划线原价=用户实机核验
   2026-09-01 为唯一权威。board.html FIELD_CN+SUMMARY_SET 同步。
4. 002962 特形（0x76 前向索引+0x96 键域 155 处+1156 个 0x27 组）真解析器=仍开放（要名↔店↔价
   结构证据必须解 0x96 键域与组间跳转=下一步可攻，暂不发布）。
commit 819e1d4；57/57 绿。

### 27.109 宸世商店终局定版：实机快照=当期权威 + 常驻子卡 + 静态池拆解（2026-09-06 晚，用户 14+ 张截图轮）

用户连发 14+ 张实机截图（9-06 22:06~22:14）：臻藏商店（推荐/外观/无人机/载具/特惠区）+稀世商店
（推荐/装备/道具/无人机/载具/庄园）。**本轮用户核心纠正**：①「刑天召唤器压根不在宸世」=633090140
非刑天（锚 633070140）=我 633 段相邻瞎关联=撤；②铠甲系可在宸世返场（帝皇战翼交易盒 3 石=实锤）；
③贯通战术两档=30特惠(限1)+40原价(限10)=同品多行；④「商店分为常驻品和每期限时商品」+「常驻的单做
一个子卡」。
**结构最终定版（27.109）**：
- 002962 静态=「客户端候选池」（204 核心双组签名品+498 单次引用；44 有名：核芯 660xxx 全系/皮肤 1110xxx/
  时装 640xxx/57000xx 福虎龙吟系/升级芯片 152xxx/材料 151xxx/自选箱 240xxx 等）——服务端每期从池选品+
  下发新品（星月落羽/深渊之力/凝渊之擎/福虎贺岁典藏=静态无行=服务端下发）；静态价档 30=原价/特惠并存
  （贯通静态 30+40 两档=实机特惠划线互证）；实机↔静态 id 级闭环 12+（重构 156182/帝皇盒 139267/贯通
  660060/余烬 660076/浑天 640015/时空 640011/紫焰 1110021/霓虹 366126/守御灵 105494/青龙 182609 等）。
- 板终态：29 行=常驻卡(2099 置顶=两店无倒计时品=月/周限重置型 vs 限1/1一次性位分标)+28 期卡；
  2026-08-20 期卡=9-06 实机全量两店快照（臻藏 31=推荐4+特惠4+外观16+无人机1+载具6；稀世 22=推荐4+
  装备6+道具6+无人机2+载具3+庄园1=53 品=倒计时/特惠/限购全录）store_zhencang/store_xishi 字段。
- 9-01 核验 30 品=9-06 快照子集（银蛇迅影「升级芯片」UI 全名修正；一瞬光年 50 证特惠=用户确认 vision
  误读 100 已修）。
- 静态池拆解落盘：data/external_refs/chenshi_static_pool_002962.json（204 核心+160 无名待锚）。
commit 待记；57/57 绿；manifest 43905。

### 27.110 宸世板=拆包主体定版 + 160 无名品补缺穷尽审计（2026-09-06 深夜，用户「不要实机截图=拆包+定位链=锚点只是锚」）

**用户口径终版**：wiki 板块内容=拆包（002962/004463 静态）为主；实机截图=只作锚点（命名/验证）。
板重做（commit 9b8ac48）：28 期次行(004463)+002962 静态池 205 商品卡=233 行——10 user-verified
（锚点命名：重构转印器 156182/帝皇战翼交易盒 139267/贯通 660060/余烬 660076/浑天穹焰 640015/时空裂隙
640011/紫焰蛇矛 1110021/霓虹恶魔 366126/飞行载具改装模块 152182/银蛇迅影升级芯片 153523）+45 structure
（common_item 名册）+160 static/candidate（ID 占位）。实机快照文本撤下=external_refs 参考层。
**002962 行结构终解**：每商品行=[21011,行号][品id][品id,1][货币,价]；行内无 限购周期/时间字段
→ 常驻/限时=纯服务端维度=静态不可分（27.109 已证）→ 板上不断言常驻（27.109 的实机倒计时常驻卡
已撤=内容源=实机=不合口径）。
**160 无名品补缺穷尽审计（27.110）**：经典服 common_item=同 FID 共享（sha 实测 79e25f…/3be82c…）
=与 BA8 同名册=无补；gift_data=补 135048 福鼠迎春典藏 1 个；vehicle_catalog/collect 族 319 表
（卡牌收集/执照/任务类）/res_handbook（023520 手册=1344xxx 资源域、005886 映射=0x96 老格式=键域
非商品）全阴性；root 老包=规则禁止。**结论：160 品正式名=双服当前客户端静态名册不可得=服务端下发
/待更新包登记**；出路=①下次更新包②用户图鉴收集截图③服务端。审计落盘 chenshi_static_pool_002962.json。
测试 57/57 绿；manifest 44109。

### 27.111 池全量版 702 修正 + 板结构终版 29 行（2026-09-07 凌晨，用户「怎么又逐品子卡/塞回常驻或每期」）

两轮修正：
1. **板结构**：205 逐品卡被否（「塞回常驻或每期里面」）→ 29 行=28 期次卡+1「常驻商品池」卡
   （置顶 2099）：702 品全部以族分组文本入卡（20 族段 7317 字），锚点品 ▲ 标。
2. **池数据 bug**：双组签名收窄（204）把单次出现的真品全丢（核芯 660xxx=容器行内内容=
   单次出现=误判引用）→ 改出现≥1 次全收=702；common_item 名册 110+gift 补 88（含核芯
   「禁交易」款）=198 有名；504 无名占位 ID。int/str 键 bug 同修。
commits 951b4b4 等；57/57 绿；manifest 43905=20 板 29 行宸世。

### 27.112 神秘商店静态封顶 + 载具名册表 vehicle_ui_data 发现（2026-09-07）

**神秘商店（四/（四））推进=静态侧封顶**：discount 族 28 表全扫（配方改造折扣/月卡折扣/家园派对
折扣=全无关）+random_discount 名 0 命中复核——RandomDiscountHD 商品/折扣载体表=客户端静态确定
缺失（两轮扫描证据链）；板现状（4 期+系统定位+返场候选链+刷新币机制）=静态上限；下一步=神秘开店
实机截图（当期限时折扣货架=锚）。
**载具定位链=vehicle_ui_data（014186，双源共享，FID 8E1FB6707CA13451）=载具车库注册表**：
- 274 行=key 全在 194xxx 载具域（标准解码 3 行样本：194097/194106/194166）+245 D6 老格式行
  （50B 紧凑数值行=scale/acc/speed 浮点+变体引用=无直接文本）+标准文本行（desc=「羊羊摇摇车（14天）」）
- CHS 池 014204（105 条）=字段名 1-35（name/desc/brand_name/vehicle_equip_type/available_ts…）+
  内容 36+（车名/desc/获取文本/路径）；**车名全集在池**（已落盘 external_refs/vehicle_ui_pool_names.json
  23 候选：古典绅士(-热潮/-粉黛)、月舞风华(-夜星/-赤霞)、帝皇铠骑(3天)、烈焰归途(3天)、羊羊摇摇车
  (14天)、虹神北斗、春日颂樱、鎏金煌影、镭射流星、风火轮、拳击手、旷野骑士+铠甲勇士曜影奔袭/喜羊羊
  灰太狼/环太平洋联动 desc）
- 完整行级 id↔名↔model 配对=待老格式解析器（D6 行字段序+文本池 idx 判定=下轮专攻）；
  vehicle_catalog 71 待命名行=候选名池=已可用此车名词典

### 27.113 vehicle_ui_data 解析器攻坚-暂停点（2026-09-07）

结构解剖到深层：body 布局=0x27 头区(2696-2819)+D6 数值行区(2874 起 245 行×~50B=浮点参数
scale/acc/speed+变体引用)+76/86/C6 行区+尾部 id 对索引区(21900-22670=成对 193xxx/194xxx
三字节 uleb 对=每 ~7B=实体映射表)。D6 行=无独立文本（desc/名=池引用在标准行）；标准解码=3 行
（194097/194106/194166=desc 羊羊摇摇车（14天）=首个车辆 id↔名锚=已落盘
external_refs/vehicle_ui_id_anchors.json）；002962 池无此 3 id（摇摇车=活动车非商店返场=交集空）。
**暂停原因**：完整行级配对需 D6 字段序+文本池 idx+索引区三方联合解析=数小时级；当前已产出=车名
词典（vehicle_ui_pool_names.json 23 条=vehicle_catalog 候选名池）+3 id 锚。**更短路=用户车库/图鉴
实机截图**（车库=每车名+模型=id 锚=直接）或等更新包。

### 27.114 vehicle_ui_data 参数层=工具缺口登记（2026-09-07 凌晨，用户「继续攻」终局）

**名册层闭环**（27.113 续）：vehicle_ui_data 014186 尾索引（21900+，308 uleb=77 对）=车库全量
显示序；车库截图 47 辆（DS vision-exp=Agnes 挂后的视觉通道）1:1 锚定：193013=月舞风华/
193014=古典绅士/193015=金鳞浮光/193017=银虹贯日…193048=霓虹恶魔/193057=都市游侠/
194140=游园单车·樱草/194147=独行者（193 段用完续 194 段=车库 id 连续序）；002962 池 31 品
回填命名（commit 17ee9c7）。vision 通道=config 切 deepseek-v4-flash-vision-exp（Agnes 401 故障
期间可用=已验证读图）。
**参数层卡点=工具缺口（非数据缺失）**：274 行（D6 226 行变体+C6/76/86 文本行 48）行首=marker+
schema_ref（D6 行=83?/C6 行=841?=schema_at 均越界）+值流=uleb/double 混合（0x66×6+e6 3f=double
0.7 被 uleb 误读元凶）；parse_index(014186)=「index bucket count unreadable or offsets out of
range」=bindict parse_index 不支持该表索引格式（002962 同族 0x76 特形先例）→ 参数层（速度/耐久/
氮气加成等字段级）需 parse_index 扩展或专用索引解析=**工具缺口=登记**（bindict_table 核心禁改=
独立解析器=专项轮）；名册层已够 wiki 用（vehicle_catalog 71 待命名=47 已锚可回填）。


### 27.115 common_item 三件套 del 定位 + loader 壳字面审计落地（2026-09-07 深夜）

**背景**：wiki 数据源升级轮（schema v3、11 源锁定）后，BA8 `common_item` 热更表族的 `del` 组件一直是断点（旧结论「0 命中」）。

**del 定位（修正旧结论）**：`common_item_data_del.py` = entry 16447（FID `A44D99E0490CA9BF`，147B，SHA `fe1ef916…`）。此前扫描器 `scan_table_family.py` 跳过 <250B 文件=把 147B 的 del 漏掉（缺陷）；已移除尺寸过滤并新增真实 BA8 小模块回归测试。同包合并壳 entry 1765（FID `1232F498D07A0EBB`，815B，SHA `af4d91fe…`）marshal 常量表字面含 `MergedTableData`、`SplitTableData`、`common_item_data_base/inc/del`、版本 hash `aaebe9f972c76ecd`、输出路径 `com\cdata\common_item_data.py`；del 模块本体=构造名为 `data` 的 `set`。**字面证据≠运行时语义**：合并顺序/同 key 覆盖/删除 key 值/灰度分支仍未复放，状态维持 `components-located-loader-replay-pending`。

**decode_probe 缺陷修复**：无 x{ 容器且含 `.py` 逻辑路径的小文件此前被误报「0x73 纯 CHS 池/壳」；现归为 py 模块加载壳并恢复路径尾（1765/16447 均正确识别，新增回归测试）。

**新工具**：`tools/audit_common_item_split_shell.py`（+3 测试）=只读字面审计：SHA 锁 + 词条偏移 + ascii runs + 结论门禁，输出 `data/audit/common_item_split_shell_audit.json`；不 import/marshal/exec payload。registry `observed_components.del` 已同步 `located-static-loader-replay-pending` + 壳证据。

**验证**：全量 unittest **70/70 PASS**（65→70）；原始 NPK 未写；工作副本只读。


### 27.116 common_item 家族静态闭环：0x86 附属行解码 + 集合审计 + 大板重建（2026-09-07 深夜续）

**0x86 附属 detail 行支持（bindict_provenance.py，wiki 私有层）**：语法 `[86][uleb schema_ref][uleb bitmap_ref][bitmap @ref][值流]`（D6-style，schema 170）。**只接受精确闭合到行边界的 detail**；解析失败回退 `unsupported tail marker 0x86` 旧语义（0x86 字节也可能是 0x27 组内普通 uleb 元素值=wardrobe 表实测，若不回退会误伤整行）。落地效果：
- inc（5292+2592）：25 解/12 未解 → **35 解/2 未解**；保留 1224504（detail 溢出行边界 1B）、1345059（0x0c 扩展区，语法未校准）
- base common_item（18005）：**35980 → 36038 行**（+58 行 0x86 尾行转正，unresolved 1954→1896）
- 回归：fashion wardrobe/projection 等表 0 误伤（0x86 数据值→opaque 语义）

**家族静态集合审计（audit_common_item_family.py + data/audit/common_item_family_composition_audit.json）**：base 36038 key / inc 35 key / 重叠 27 / 仅 base 36011 / 仅 inc 8。**关键警示：重叠 27 中 23 组 name 不同**（key 1224479：base=1型倒三角墙 vs inc=3型倒三角墙）→ inc 行 key 疑似槽位而非 item_id，重叠≠同一物品被修改；4 组 name 相同（156182 重构转印器等）为真重叠候选。del（16447）删除键=自定义 marshal set 常量，`payload-shape-unresolved`，不应用任何删除。**仍不构成 loader 顺序/行身份结论**，状态保持 `components-located-loader-replay-pending`。

**strict-v2 契约补齐**：rebuild_common_item_text_sources.py 的 meta.provenance 升级（contract_version 2、dual source_locks primary+comparison、dual_source 块），item 级补 source_id + locator_chain（replayed-structural）。

**大板重建（用户授权范围）**：common_item_text_sources.json 94,222,413B / 36,038 items 覆盖写入；manifest 重建 **21 板块 / 44,004 条**（原 43,952）；publication gate 计数同步 35986→36038。

**验证**：全量 unittest **77/77 PASS**（73→77）；原始 NPK 未写；所有工作副本只读侧改动。


### 27.117 双客户端文件地图 + 统一 source registry + P1-8 索引（2026-09-07 深夜，用户 P0-P7 工作台路线图）

**P0 闭环（7/7）**：双端全文件盘点（test 11,344 / live 17,588 文件，inventory JSONL + 定向 SHA 1,417）；用途分类（路径身份/扩展名/魔数抽检，unknown 仅 4+3）；client 维度=verified（体验服.lnk/正式服.exe），**server_branch 一律 unresolved**（历史 mrzh↔简单生存服绑定作废）；统一 registry `data/source_registry.json` schema v1 **543 源**（test 385/live 158：script 11/npk 155/gpk 136/fpk 73/wpk 118/idx 27/fhpk 2/散装 21），sha_missing=0，与 live_sources.json 11 script 项交叉一致。路线图 `docs/WORKBENCH_ROADMAP.md`。

**P1-8 进度**：
- Stage 1 file_hash_pack.bin（FHPK v2）评估：官方文件级清单 test 1,580/live 1,526 条（SHA-1 校验过；x_data 全空=纯清单）；含 res.layers 分卷 npk 全集与根 script+overlay；**不含 Documents 热更/gres/wp/fpk**；磁盘=官方子集（多架构未全装）。覆盖能力=文件级名册，非包内索引。
- Stage 2 script 11 包 entry/FID 索引：11/11 SHA 校验（总 1,932,449 条目含 Stage 3a 全部 npk）；BA8 锚修正 25,373→**25,485**（manifest header.entry_count 实测，日志旧口径作废）。
- Stage 3a 全 npk 166/166（1,932,449 条目；flag 0=1,034,467/2=897,982；NXPK 格式统一含 4GB 大包）。
- Stage 3b：gpk 136/136（2,169,772 条目；flag 12=1,990,751 主流；magic 不 gate=gres 变体头；weapon.gpk 51,664 与先例一致=硬锚）；idx 27/27（61,277 记录；pkg 3-15+255 旁侧）；wpk 118 文件登记；fpk 73 包全帧解压索引进行中（live 壳 1 帧/包；test 包 DDS+OTHER 为主，已完成 16/64）。
- 修复记录：decode 相关见 27.116；registry 误排 documents-res wpk/idx（补 145 源）；GPK magic 反序（HPGF=FPGH 存储序）不 gate。


### 27.118 P1-8 完成：全格式条目索引 + 统一 file_index（2026-09-07 深夜续）

**执行修正**：会话中断后按实际落盘核对（未按旧汇报猜）：gpk 136/136 与 idx 27/27 早已完成保留；fpk 仅 32/73 且可能截断→删除残留，**14 worker 多进程全量重跑**（7950x3d，73 包 ≈16 分钟）完成 73/73、0 失败、1,856,043 帧（live 壳 1 帧/包，test 包帧数万级；OTHER 70.9%=原生二进制内容头未知，P7 深分）。

**merge_file_index 两处修复**：idx summary 用 idx_packages 键、fpk 用 frames_file 字段——首跑只并入 npk+gpk（302 源）；修复后 **402 源 / 6,019,541 条目** 全并入、对账吻合（npk 1,932,449 + gpk 2,169,772 + fpk 1,856,043 + idx 61,277）、failures 0。

**file_index 产物**：`data/file_index.json`（目录+统计+字段说明）+ `data/file_index_entries.jsonl`（6,019,541 行统一字段：kind/client_channel/package/entry_index/file_id|c1c2|hash16|frame_offset/offset/size/flag|storage/name_known=false）。npk file_id 跨包重复键 223,517（Documents↔root 同内容覆盖关系，正常）。回归 +3（test_file_index_contract），全量 **91/91 PASS**。


### 27.119 P1-9 完成：标识→出现位置 定位索引（2026-09-07 深夜续）

复用 P1-8 file_index_entries.jsonl（不重扫原包）构建 SQLite 定位库 `data/id_locator_index.db`（6,019,541 行，66s）：
- 标识：npk=file_id / gpk=c1c2 指纹 / idx=hash16；fpk 帧无内容级标识（未存 payload hash），按 (client, package, frame) 查询，identifier=NULL
- 覆盖：有标识行 4,163,498（npk 1,932,449+gpk 2,169,772+idx 61,277，对账吻合）；唯一标识 2,843,919
- 重复键 363,703（额外出现 1,683,282 次=Documents/root 覆盖、同内容跨包/去重）；冲突（同标识不同 decoded_size）120,449=script 多世代同 fid 大小演化类，只记录不解释
- 查询 CLI `tools/query_id_locator.py`（--fid/--c1c2/--hash16/--frames）；硬锚验证：FID B42760CCA41DBC25 → test Documents/script.py314 entry=18005（BA8 common_item base 精确命中）
- 回归 +4（test_id_locator），全量 **95/95 PASS**


### 27.120 P1-10 完成：table_index 全量表清单（2026-09-07 深夜续）

复用 BA8 工作副本（config_work/script_py314_docs_BA8A239A，25,485 已解码条目）+ P1-9 id_locator，不重扫原包。

**机制定论（实测锚）**：BA8 每条目内嵌 co_filename 字面 `com\cdata\<X>.py` + <module> 邻接=自身模块路径（18005/8644/16447/5292/1765 全命中）；x{ 合法容器=表数据体；MergedTableData/SplitTableData 字面=合并/拆分壳。npk_reader path_id（双 Murmur3）对 script 包 file_id 不成立（全 MISMATCH）→ 弃路径 hash 绑定，改字面提取。

**产物**：data/table_index_entries.jsonl（76,143 行：test BA8 25,485 + live fid 传播 50,658）+ table_index.json + table_families.json + tools/query_table.py。
- test 命名 22,616（88.7%）；配置表体（x{）5,296，命名 5,231，unknown 65；role（纯后缀）：plain 4,977/chs 235/base 14/inc 5（del/merged 无表体=代码壳）
- 表族 4,990（family=族后缀循环剥离）；多 role 族 239；家族示例=common_item_data{merge壳1765+chs2131+inc5292(body)+del16447壳+base18005(body)}
- live 5 包 fid 共享命名 50,658（全部 evidence=fid-shared；live BA8 sha 79c0…≠test，无工作副本，不重扫）
- 大表锚：building_object_data_base(entry 22570)/system_home_data_base(8332)/common_item_data_base(18005, 1.98MB)
- 修复：co_filename 窗口错用路径起点（144→22,616）；role 双后缀循环剥离（_base_chs 归族）
- 回归 +4（test_table_index），全量 **99/99 PASS**


### 27.121 P1-10 口径修正 + P1-11 表族关系固化（2026-09-08）

**P1-10 双端口径修正（stats_v2）**：family 级（覆盖范围内）test 17,486 / live 17,396 / 共有 17,396 / test 独有 90 / **live 独有 0=结构性**（live 命名 100% fid 传播自 test，非"live 无独有表"证据——live Documents/script 系 170,177 fid 位置中 119,519 不在 test BA8 fid 集=未覆盖 unknown）。live 行 table_body 继承源值（fid 传播时一并传），统计逻辑内嵌 build_table_index（不再依赖外部校准文件，防覆盖丢失）。

**P1-11 产物**：data/table_families_v2.json（schema lifeafter-table-family-relations-v1，17,486 族）+ tools/build_table_families.py。
- 槽位规则：后缀完整保留（_base_chs→base_chs 非截断）；主名无后缀归位 merge_shell→merged / table_body→main / 纯代码→code；双端同规则
- 完整 6 槽 {base,base_chs,inc,inc_chs,del,merged}；缺槽 missing 不补造；不推断合并顺序
- 数字：family_total 17,486（code_only 12,496 纯模块族 / main_only 4,975 单体表族 / structural 15 真族结构）；complete test 7/live 4；incomplete structural test 8/live 11
- common_item_data 全槽锚：base=18005(B42760CCA41DBC25 body)/base_chs=23928(EF3A8474A5E5F7A4)/inc=5292(363827281579481B body)/inc_chs=2592(1A81E67098A6E8D9)/del=16447(A44D99E0490CA9BF)/merged=1765(1232F498D07A0EBB)；live 端同 fid 多包多位置正确记录
- 完整族 7：all_equips_data/battle_mission_data/building_object_data/common_item_data/hd_ui_scheme_data/monster_attributes_data/reward_pool_data
- 回归 +3（test_table_families）+ 修 test_table_index stats_v2 契约，全量 **102/102 PASS**


### 27.122 P1-12 完成：行级定位索引（2026-09-08）

**术语定版（P1-11 汇报修正）**：structural_family=15 真族结构 / standalone_table=单体表（main_only 4,975）/ code_module=代码模块（code_only 12,496）——不再统称"表族"。

**产物**：data/row_index.jsonl（984,493 行）+ row_index_summary.json + tools/build_row_index.py（12 worker，3.8s）。
- 范围：test BA8 快照全部 5,231 命名表体（x{ 容器验证）；live 无独立解码证据不补行
- 行定位：std 0x76 索引尾 (key,start)+行头 marker/schema_ref（96/D6/C6/36）；KJ1 老格式 node off→ULEB 行偏移桶；key/offset/schema_ref 全定位，不解字段值
- 成功 4,462 表 / parse_failed 769（细分：unknown_head 各 0x04/0x61 等=非标准头容器 ~658（疑老格式/覆盖容器，P2 字段阶段验证）、bad_xbody_header 74、kj1_nodes_fail 37、row_stream_without_index 38、legacy_0x73_shell 18）
- 行字段：client/snapshot/table(com\cdata\X.py)/fid/entry/row_index/row_key/offset(文件内绝对)/schema_ref/marker
- 锚验证：common_item_data_base 18005=37,934 定位行（=36,038 值解码成功 + 1,896 解码层 unbound 的位置，全含 schema_ref 40206）；x{ 容器 cnt=55,141=CHS 池锚精确一致
- schema_ref 覆盖 983,321/984,493（99.9%）；无 schema_ref 1,172 全为 0x36 mapping 行（结构如此）；marker：0x96=710,443/0xd6=271,402/0x36=1,172/kj1=1,476
- 回归 +3（test_row_index），全量 **105/105 PASS**


### 27.123 P1-13 完成：数字 ID 出现位置索引（2026-09-08）

**产物**：data/id_occurrence_index.db（SQLite，6,855,054 条，37s）+ id_occurrence_summary.json + tools/query_id.py（--tables/--all）。
- 扫描 4,456 可解码表（4,462 定位成功中 6 表无 schema 跳过）；复用 P1-12 row_index 定位+解码器行语义（_schema_at pool=[] 安全占位=字段名不解只记 field_slot）
- 抽 ID 槽：整数型 ULEB/ULEB_ALT/ZIGZAG（std 槽位+0x27 组元素+0x36 mapping 键值）；BOOL/JUMP/CHS/浮点不抽（非数字 ID 语义）；值=0 不记（缺省/空）
- 修复：INSERT 列错位（marker 入 table_name）；SQLite 64 位溢出值过滤（dropped 818）；_scan_table 返回缺 table_name（改 tasks 引用）；query dict(zip(FIELDS, keys)) 错配
- 锚：ID 152239 → common_item_data_base(18005, row_key 152239 自引用) + new_talent kj1(11605)；ID 7000 → 124 次/34 表
- 统计：occurrences 6,855,054 / unique_ids 233,766 / 跨表 ID 126,708（54.2%）；无字段名=全部（by-design 只记 slot，P2 命名）
- 回归 +5（test_id_occurrence），全量 **110/110 PASS**


### 27.124 P2-1 完成：字段名绑定（2026-09-08）

术语修正：233,766=唯一整数值候选（非已确认业务 ID）。
**机制（验证锚）**：schema 定义=blob 内 schema_ref 偏移（uleb n+bits+n×(slot,type,name=池文本[slot])）；字段名池=家族 chs 型成员条目 parse_legacy_chs_pool，配对=池条数==表体 x{ 头期望 N——common_item 锚：023928 池 55,141=base 期望 55,141 精确命中，schema 328 字段名=bag_index/bobj_item_id/attrs…（池文本=可验证非猜）。

**产物**：data/field_names.json（(entry,schema_ref) 定义级，3.4s）+ field_names_summary.json + tools/build_field_names.py。
- 4,268 std 表全处理：绑定成功 4,105（96.2%）；池无法配对 163（单列 pool_unresolved_entry_list）
- 字段槽 95,806：已绑定 94,422（98.6%）；unresolved 1,384（slot 越池界占位）
- 多 schema_ref 表 65（分别绑定）；unsafe_count=0（BA8 快照无已实证错位表；值层错位检测=P2-2，0x96 宽表 suspect 待复核）
- 回归 +3（test_field_names），全量 **113/113 PASS**


### 27.125 P2-2 完成：字段语义可信度验证 + FIELD_RULES（2026-09-08）

**判据（统计级/结构级，无单条值语义猜测）**：
A. 名↔型一致（字段名尾模式 vs 槽类型字节，矛盾=unsafe）；B. 文本槽内容模式（name/desc 类=可读文本样占比≥0.8；icon/path 类=路径样≥0.8）；C. 历史实证（2026-09-01 日志用户确认）：all_equips_data 的 name/desc/icon **跨记录错位**→文本语义槽直接 unsafe，结构字段 verified。
**误报修正 3 轮**：_sfx/_model/_anim 尾误当文本（跳转/整数引用合理）→TEXT_TAILS 收窄；中文长句/含斜杠 desc 误判 pathlike→text_mode 中文优先；neutral 名文本槽不做模式强判；desc 英文短文本并入可读文本。

**产物**：data/FIELD_RULES.json（表级+槽级状态与证据）+ field_semantics_summary.json + tools/verify_field_semantics.py（13s）。
- 字段（槽）95,810：verified 81,339（84.9%）/ unsafe 1,673 / unresolved 10,707（无样本/池缺/越界）/ likely 2,091（少样本/时装 suspect）
- 表 4,268：verified 2,695 / unsafe 804 / likely 544 / unresolved 225（表状态=最差槽）
- 锚：all_equips 16135 name/desc/icon=unsafe（hist 证据）；common_item 18005 bobj_item_id/bag_index/name/desc/icon=verified
- 多 schema_ref 65 表与 0x96 宽表在逐槽统计内覆盖（各自 schema 分别判定）
- 回归 +4（test_field_semantics），全量 **117/117 PASS**


### 27.126 P2 口径修正 + P3 可靠数据源完成（2026-09-08）

**P2 口径修正（95,806 vs 95,810 差 4）**：4 个 error schema（1861/2559/4861/9667）定义解析失败=P2-2 用默认值 1 虚计；P2-1 跳过不计。修正=error schema 槽数未知一律不计（两 summary 统一 95,806）。随后发现**KJ1 6 表（1861/2559/3862/4861/9667/18341）被误当 std 表做字段绑定**（KJ1 行型 uleb 被当 schema_ref，86 个假 schema 含 4 error）——build_field_names 聚合排除 marker=kj1 行 → 4,268→4,262 表、95,806→95,720 槽。P2-2 同步重跑口径一致。

**P3 产物**：data/RELIABLE_SOURCES.json（schema v2，4,258 源）+ SOURCE_RULES.json + docs/SOURCE_RULES.md + tools/build_reliable_sources.py。
- 源=命名表主数据体（去 chs/inc/del/merged 附属）；oversea 变体归 canonical+标注 variant
- **源状态=类别关键槽聚合**（名称正源→name 槽；业务源→name+icon；desc/title 参考）；no-samples unresolved 中性化（不压实证 verified）；KJ1 格式表不在 FIELD_RULES=如实 unresolved
- 状态：verified 3,310 / likely 416 / unsafe 34 / unresolved 498（numeric_only 2,553 标注模式）
- 分类（表名模式规则，非业务证明）：物品/装备 443（301v）、奖池 205（172v）、活动 363（231v）、商店/兑换 167（116v）、时装 89（63v）、武器 71（50v）、载具 62（49v）、名称正源 60（51v：common_item_data_base 18005=verified=can name 槽/cannot desc 槽）、其他 2,798
- 锚：18005 名称正源 verified（name/icon 实证 36k 行）；16135 all_equips unsafe（name/desc/icon 禁业务真值）；13068 fashion likely（样本少）；8644 KJ1 奖池 unresolved（格式不适用不硬猜）
- 回归：+4 reliable_sources + 修正 field_names/field_semantics 测试计数，全量 **122/122 PASS**


### 27.127 Wiki v0.1 武器皮肤静态候选展示修复（2026-09-10）

**边界**：只修 Wiki 展示，不重启 P4-C 身份研究。新增 `weapon_skin_static_candidates_v01`，保留原 `weapon_skin_structure_v01` 3 条结构声明。

- 展示记录 **129**：`weapon_skin_data` 静态记录 126（旧板 111 顶层 + 15 嵌套记录展平，不沿用其父子身份推断）+ `weapon_skin_behavior_res_data` behavior-only 3。
- 子证据：SFX 静态子项 348；行为资源按原记录保留；候选名称/UI 短名仅以 candidate 标签显示。
- 每条强制 `identity_status=unresolved`、`publication_tier=static config`、`official_identity=null`、`verified_weapon_skin_id=null`。
- **旧整数 join 重启数=0**：不使用 `weapon_skin_data.row_key == common_item.row_key`，不做任意同整数跨表 join，不使用 `%10==1` 归父，不把 SFX/UI 短名当正式皮肤名，不使用 all_equips name/desc/icon。
- 页面专用折叠卡已实渲染：候选名、静态字段、行为资源、UI 短名、SFX 子项、回放来源分区可见；Chrome DOM 显示 129/129 + 348 SFX。
- Wiki 最终 **10 板块 / 61,828 条**；全套 unittest **228/228 PASS**；`tools/build_wiki.py` PASS。

主要产物：
`08Lifeafter wiki/data/boards/weapon_skin_static_candidates_v01.json(.js)`、`tools/rebuild_weapon_skin_static_candidates_board.py`、`tests/test_rebuild_weapon_skin_static_candidates_board.py`。


### 27.128 体验服更新前快照（2026-09-10 21:48 +08:00）

- 源（只读）：`E:\mrzh`
- 快照：`E:\la拆包项目\03拆包产物\source_snapshots\pre_update_20260910_214818`
- 结果：**PASS**；创建后又独立执行 `python create_and_verify_snapshot.py --verify`，源/副本 SHA 错误 0、容器 stat 漂移 0；`sha256sum -c RUN_HASHES.sha256` **8/8 OK**。
- 全容器状态锁：**817 文件 / 275,464,160,584 bytes**；`source_lock.json` SHA-256 `7a351075c9ae1a4637a2629cdac595ea14be46be97d6a1ec5d3c094432e06582`。
- 高优先级原件副本：**2,264 文件 / 11,370,225,676 bytes**；含 Documents/res 全量、Documents 根脚本包、客户端根 NPK/GPK、相对上一稳定锁新增/变更容器；复制失败 0。
- 配置硬锚：`raw_priority/Documents/script.py314.lc.npk` SHA-256 `ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad`（BA8A）。
- 相对 `post_update_resource_stablecheck_20260831_190612`：容器 added 0 / content changed 13 / deleted 0 / mtime-only 7；该差分只是 8/31→9/10 基线信息，不是待到来的更新结果。
- 更新后必须新建 `post_update_*`，以本次 `source_lock.json` 按 path + SHA 比较；不得只看 mtime。该快照不是整个 275GB 客户端物理镜像，但完整冻结了全部容器哈希并实体保存高优先级原件。

## 2026-09-11 05:43 legacy 文档流读取器（0x73 容器）— 已修通并自校验

**问题**：`huodong_conf_data`（活动排期）、`fashion_charm_period_data` 等表不是标准的 `x{` 容器，
`body_from_payload()` 报 no x{ body / base reserved != 0，排期读不出来（此前因此误判“9/17 没大抽奖”）。

**结构实证（entry 18027 逐字节）**：流 = 顺序 (tag, value)，无定长头
- `0x3e + u32` 行引用/行键（活动表键 1000~6000）
- `0x28 / 0xd3 / 0x66 / 0x67 + u32 len + utf8` 字符串
- **`0x30 + f64(8B)` = 时间戳**（实证 @472479 → 2026-09-17 08:00）<- 关键
- `0x30 + u32` 其它数值；裸 f64 时间戳；其它字节前进 1
- 坑：只有落在行键窗口内的 `0x3e` 才可按 5 字节消费，否则冲掉 f64 对齐（时间会全部解不出）

**工具**：`analysis/tools/read_legacy_doc_stream.py`
- 配对 = ref 切行 + 「只有时间无文案」的记录回填最近的「有文案无时间」记录
- 输出带 `window_source`（own / neighbor-backfill）——回填窗不可当定论
- `--selftest` 内置 8 项已知事实（用户核对过的日期），**当前 8/8 PASS；不过不许用**

**产出**：`analysis/script_delta/activity_timeline_huodong.json`（2358 条记录）

**本轮排期结论**：铠甲再临·双勇士登场 = `ArmorHeroLotteryHDUIV2`（超级时装抽奖 期232：刑天铠甲 139292 / 飞影铠甲 139293），
行内无时间字段（回填窗不可信）→ 待 UI 锚点；铠甲勇士联动收尾 2026-09-19 23:59；
蛛螯步枪返场止于 09-17 07:59；落叶世界 09-17；云兔衔光 09-24→10-08；信号猎手·机载辅助单元（VehicleLotteryHDUIV2）11-05→11-06。

**仍未解**：`reward_pool_data`（815B，无文档流区）、`lottery_big_reward_camera_conf`（解码报错）、
`super_fashion_lottery_gacha_data`（未随包）→ 抽奖概率/权重仍缺。

## 2026-09-11 05:47 奖池本体与自动时间轴（啃完 camera_conf 的结论）

**camera_conf 更正**：`lottery_big_reward_camera_conf`（+chs）**PRE/POST 都不在包内** → 不是"解码报错"，是未随包。
`super_fashion_lottery_gacha_data` 同样未随包。**所以抽奖概率不在这些表里**。

**奖池本体（已找到并解出）**：
- `com/cdata/reward_pool_data.py`（815B）= **split-table 合并脚本**（base ∪ inc − del），不是数据本体。
- 数据在无名条目：**entry 11068 / 11371 / 25573**（657KB，CHS 池，字段名 `reward / initial_weights / prob_note / probability_level / initial_threshold / cooling / reward_rank / accumulative_weight / ensure_count / expiration_time / note / p_group_id / broadcast_content`）+ **entry 23049**（1.1MB，表体，23,452 行）。
- 行结构：`note`=池名/物品名，`prob_note`=**展示概率文本**，`initial_weights`/`accumulative_weight`=权重，`initial_threshold`=保底阈值，`reward`组=`[[池id, 池内序号],[物品id, 数量]]`。
- 注意：同池 `prob_note` 相加 **>1**（实测 1.31/1.62/1.66）→ 它是**分档展示概率**，不能当绝对概率直接相加；真实抽取还要看权重+保底。
- 无人机机舱奖池三期已解出并落盘：`analysis/audit/无人机机舱奖池_明细.md`（391593 溶蚀机枪 31 条 / 391721 典藏涂装·碧辉 27 条 / 391807 信号猎手 32 条，含概率/保底阈值/权重）。
- 另注：池内出现 3 条 `待取名`（策划占位未命名）。

**自动时间轴（已交付）**：`analysis/tools/build_activity_timeline.py`
- `--workcopy <dir> --path-table <..paths.json> --match huodong_conf_data --out <dir> [--diff-against <旧产出目录>]`
- 逐链输出 `activity_timeline_<链>.json` + 合并 `activity_timeline.md` + `activity_timeline_diff.md`（新增/消失/窗口变更）
- 自校验默认 `warn`（不通过也产出并标注），`--selftest strict` 可切成硬闸
- 本次实跑：POST 2358 条记录（436 有窗口，自校验 8/8 PASS）、PRE 2341 条；差分=新增 9 / 窗口变更 3（落叶世界 9/17、信号猎手 11/5-11/6、云兔衔光 9/24-10/8、璀璨铁花 …）

## 2026-09-11 05:53 更正：活动名 ≠ 物品（极寒冰爆误认）

**错误**：把活动名「新霰弹枪冰核芯」当成「异变核芯-极寒冰爆(660024/660113)」。
**实情**（全物品表核对）：
- 全表 213 个核芯类物品里，"描述含冰且含霰弹"的**只有极寒冰爆 660024 / 660113**（同技能同描述，6601xx 是同批"新块"重复号）——**极寒冰爆确实是老核芯**。
- 活动名「新霰弹枪冰核芯」只出现在 huodong_conf **行 3592**（单独一行，无 ui_class、无奖励/物品引用）与活动名池 23640 → **本包内无从认领**。
- 另一条线索：核芯活动行 **3692** 引用 4 个核芯 id（660024 极寒冰爆 / 660044 电掣双刀 / 660000 不在物品表 / 660035 酸蚀回响）——与 3592 不是同一行。

**规则（加入读取纪律）**：
1. `huodong_conf` 的 `name` 字段是**宣传名**，不得据此认领物品/机制；必须找到该行对物品 id 的引用或对应 conf 才算。
2. 活动名行（只有 name、无 ui_class/无引用）→ 一律标"**无法认领**"。
3. 老技能"新号重复"很常见（6600xx → 6601xx 同描述）→ 报"新核芯"前先看 id 块与描述是否**首次出现**。

## 2026-09-11 05:56 奖池机制：条目行可被多池共用（391560=宸世臻藏池）

**确认（用户 UI 锚点 + 静态交叉）**：`391560` = **宸世臻藏池**。静态支持：
- 成员构成 = 赤月终焉臻藏盒(槽0) / 丛林斥候臻藏礼盒(槽1) / 宸晶臻石(槽2) / 配方残页*50(槽3)——"臻藏盒 + 宸晶臻石"正是宸世臻藏系道具；
- 同一张池表(CHS entry 11068)里就有该活动文案：`恭喜{0}鸿运当头，在宸世臻藏活动中获得{1:format_item_name}`、档位名 `宸世臻藏紫色奖励 / 宸世臻藏金色奖励`。

**机制（新发现，重要）**：`reward_pool_data_base` 的**同一条目行可挂多个池槽位**，组形如 `[[池A, 槽i], [池B, 槽j]]`：
- 行693298 赤月终焉臻藏盒 → `[[391560, 0], [391807, 28]]`
- 行84168  宸晶臻石     → `[[391560, 2], [391807, 26]]`
→ `391807`(信号猎手池, 32 条) **直接复用** `391560`(宸世臻藏池) 的条目行。
所以"某道具在哪个池"**不是二选一**：原生池是宸世臻藏池，信号猎手池是复用位。

**推论纪律**：看到道具同时属于多池时，先看槽位序号与池成员规模判断原生/复用；不要只报一个池。

## 2026-09-11 06:07 国庆档主题线：非遗铁花 × 火树银花（+ 严重坑：923 礼包表名称↔内容错位）

**A. 非遗联动线（"明日之后×非遗传承人"）**
- 活动：`huodong_conf` 3591「璀璨铁花活动」，UI 类 `IronFlowerShowHD`（真实装）；玩法＝每日 3:00–19:20 捐献炉料 → 19:20–19:30 结算 → 19:30–22:00 达标营地铁花表演；表演期用动作「转铁花」共演；任务送动作/玩具「打铁花」
- 文案原文（desc_info_data_chs 直读）："每日捐献可为当日铁花表演积累进度…未加入营地的幸存者为快乐101捐献…铁花共演时段…"
- 道具：`1221430 铁花云廊`（非遗联动限定家具，火除邪祟百家安宁）+ `91221430` 独享版；`157377 动作：转铁花`、`157378 动作：打铁花`

**B. 火树银花线**
- 时装 `450053 火树银花`（"于限时活动中获得"）；fashion_data 号段 `6372501xx`（衣服 3/5/7/14/30 天版，level4，魅力350，模型 3725，品牌3）；desc＝"将人间岁时的炽热欢腾，尽数点亮。「明日之后×非遗传承人」联动限定外观" → 与铁花同一条非遗线
- 染色：`570611–570614`（浅紫/墨蓝/浅褐/浅绿,3级）+ `570615 金丝葵`/`570616 粉黛子`（4级）+ 自选箱 `241962`/`241963`
- 头像：`241889 头像自选箱` 含「火树银花」；期刊 `1300026 闪耀风尚-火树银花`（第26期，重山厂牌）；图鉴图 `shizhuang_icon/shoucang/img_tujian_3725_001.png`
- 投影：`97329/97330 梅花树灯·赤/金`（"火树银花不夜天"）+ 独享版 `90097329/90097330`
- 礼包：923 表 `923488 火树银花时装`

**C. 满减线**：`银花满减补贴`＝"满减补贴"系列（流萤/丹枫/鎏金/清铃/簪花/灵笼/青白/银花…），实现 `ManJianHuoDong`/`DiscountMarketHD` + `discount_market_{conf,reduction,goods,recommend}_data`（本次在包）；规则原文＝商城消费达额减免（满500减60…满14000减7500 封顶14000；另一套满8000减4000封顶8000）＋商城满减券＋联盟二度补贴＋购物车打包结算。该行**无 own 窗口**（服务端）

**D. ⚠️ 坑（本轮实测，记录纪律）**：`random_item_reward_data_923` 的**名称与内容组不对齐**：
- 923488「火树银花时装」→ 内容 [637320110,637320130]，但 6373201xx＝**云兔衔光**号段
- 923489「赤月终焉臻藏盒」→ [637250110,637250130]，6372501xx＝**火树银花**号段
- 923490「福鼠迎春臻藏盒」→ [460620,461620]＝**赤月终焉典藏**头饰/衣服
→ 结论：**该表不得用"名称↔内容"直接认领**；只能按号段确认"给一套时装头饰+衣服"。此前"赤月终焉臻藏盒＝火树银花/赤月时装"等具体归属全部降级为 unresolved。

## 2026-09-11 06:16 池钉名 + 923 表一行错位（已校正，含撤回撤回）

### A. 同族池钉名（reward_pool_data_base）
| 池 | 判定 | 证据 |
|---|---|---|
| **391560** | 宸世臻藏池 | 4 条：赤月终焉臻藏盒0/丛林斥候臻藏礼盒1/宸晶臻石2/配方残页*50·3 |
| **391593** | 溶蚀机枪（无人机）抽奖池 | 配方残页30 25.79%、纳米自选礼包 19.343%、涂装：苍风 0.169%(阈值171)、游鲤戏浪、帆船挂件礼包 |
| **391721** | 保卫者线涂装池（"典藏涂装：碧辉"期） | 保卫者/雨战/联动/典藏、启航训练服/研究服、涂装:仿生火箭筒典藏版 0.089%(157)、魔王金币、飞天扫帚召唤毯 |
| **391807** | 信号猎手池 | 32 条；技能点 25.734%、配方残页30 32.066%、新币*5000 17.39%、涂装：黄袍 0.12%(575)、涂装：夜骐 0.12%(788)、赤月终焉臻藏盒 2.799%(阈值1) |
| **391808** | 讯猎（信号猎手）物资箱池 | 讯猎币×4、纳米塑材自选箱 23.391%、异变核芯-燎原炽焰 24.943%、福鼠迎春臻藏盒 2.799%、典藏涂装：苍穹 0.122%(216) |
| **391810** | 宸世臻藏·主抽奖池 | 稀世之证 43.748%、配方:仿生瞬豹霰弹枪 7.494%(3)、赤月终焉臻藏盒 2.77%(阈值1) |
| **391811** | 宸世臻藏·家具向池 | 海底水晶石SSR、水晶独角马雕像、海风户外烤炉SR、海螺投影仪SR、金条*10000、福鼠迎春臻藏盒 2.77% |
| **391812** | 宸世臻藏·涂装向池 | 雷托典藏（限购1）0.079%(187)、菌焰雪地涂装自选、宸晶臻石 3.008%、纳米塑材2 |
| 391813 | **不存在**（0 条） | 早前列它属误列 |

池行字段（实测全字段）：`note / prob_note / initial_weights / accumulative_weight / initial_threshold / reward_rank / probability_level / p_group_id / broadcast_content / ensure_count / expiration_time / custom_item_level / reward(jump)`
→ 红利：**同一行可同时挂多个池槽**（`[[391560,0],[391807,28]]`=别名行），且 `broadcast_content` 直接点名活动（赤月盒那几条＝「在**宸世臻藏**活动中获得」）→ 这就是把"信号猎手池里的赤月盒"钉到宸世臻藏活动上的硬证据。
**注意**：`reward` 字段的 jump 解析在同一 index 上给出不同组（行203/693298 都是 jump:210 但组不同）→ **该字段解析不可单独采信**，须表内交叉。

### B. 923 礼包表：名称↔内容存在**一行错位**（读取器侧），校正后 5 组 4 组严丝合缝
把 923484~923490 拉直对照（内容 id 落到 fashion_data 号段）：
| 行 | 我最初打印的名称 | 打印出的内容 | 校正后真实归属 |
|---|---|---|---|
| 923484 | 飞影印象web礼包 | [636940110,636940130]=飞影浮澜 | ✔ 飞影浮澜（web 礼包给飞影浮澜） |
| 923485 | 刑天铠甲 | [636920130]=**刑天铠甲** | ✔ 下一行名=刑天铠甲 |
| 923486 | 飞影铠甲 | [636930130]=**飞影铠甲** | ✔ |
| 923487 | 月下兔 | [637320110,637320130]=云兔衔光 | ⚠ 题材对得上但名不同（礼包名 vs 时装名） |
| 923488 | 火树银花时装 | [637250110,637250130]=**火树银花** | ✔ |
| 923489 | 赤月终焉臻藏盒 | [460620,461620]=**赤月终焉典藏** | ✔ 盒名与时装名同题 |

**结论（校正后）**：
- **赤月终焉臻藏盒 = 赤月终焉典藏 头饰+衣服**（460620 hat 魅力400 lv5 ／ 461620 cloth 魅力1100 lv5，desc「至终焉以新生，冠荣光于破晓」）
- **火树银花时装礼包 = 火树银花 头饰+衣服**
- 校正规则：**该表 `name[i] ↔ contents[i+1]`**（本表内验证），凡引用 923 表内容必须做此偏移；此前"该表名称↔内容矛盾、归属降级 unresolved"的判断**作废**，本会话早前"赤月盒=赤月终焉典藏时装"的原始结论**恢复成立**。

**纪律**：legacy 家族表（923 礼包 / reward_pool 条目）在**名称与 jump 组**上均可能整行错位 → 任何"名称↔内容"认领必须先在**连续行**上做号段自证。

## 2026-09-11 06:20 【工具修复】0x27 组：byte-range 扫描 → jump 指针链（含自证）

**问题**：旧的 `decode_table_rows` 只用"行字节区间内的 0x27 组"当该行的组。对 `random_item_reward_data_923`（礼包/盒子表）会**整体错一行** → 名称↔内容错配（我曾据此误判"该表名称内容矛盾"，实际是读取器问题）。

**正解（已实装进 `toolkit_core/bindict_table.py`）**：
- `read_27_group(blob,pos)` → (kind, elements)
- `resolve_27_chain(blob,target)` → 沿指针链：kind **0x0b = 指针组**（元素是别的组的偏移）→ 递归；kind **0x01 = 叶子组**（元素交替 id/数量）；带 cycle/深度/越界保护，出错返 `error` 而非猜测
- `resolve_row_jumps(blob,rows)` → 给每行挂 `resolved`（按字段名），并加 `inline_groups_note` 说明该表该用哪种
- `decode_table_rows(..., resolve_jumps=False)` → **默认关闭，零回归**（已验证池表 23,452 行不变）
- **`selftest_jump_chains(body,pool)`** → 内置 8 条已知事实断言（923 表），**必须跑过才允许引用该表名称↔内容**

**实测**：923 表自证 **8/8 PASS**（帝皇铠甲交易盒→636910130、极光剑→1110177、极光盾→1110197、刑天铠甲→636920130、飞影铠甲→636930130、火树银花时装→637250110、赤月终焉臻藏盒→460620、福鼠迎春臻藏盒→166998）；其中 17 行（923470~923490）逐行自洽。

**逐表口径（写死，别混）**：
| 表 | 组在哪 | 用法 |
|---|---|---|
| `random_item_reward_data_*` | **jump 指针链** | 必须 `resolve_jumps=True`，区间扫描会拿邻行（错一行） |
| `reward_pool_data_base` | **区间扫描** | 成员=[池id,槽位] 用 `inline_groups`（已与游戏 UI 互相验证）；`reward` 字段的指针链 = 实际奖励物（如赤月盒→139314） |
| `vehicle_lottery_base_conf_data` | jump 指针链 | 叶子元素是**物品 id 列表**（非 id/数量对） |

## 池钉名（`name` 字段直读 + `name`=奖励档位名）

- 池表 `name` 字段 = **奖励档位/池名**（不是道具名）：实测 `宸世臻藏紫色奖励` / `宸世臻藏金色奖励` / `宸世臻藏金色奖励X9` / `宸世臻藏蓝色奖励` / `宸世臻藏金色奖励（国服` / `（海外` / `中秋兔子不放回7` / `水晶家具宝箱` / `圣诞小镇` / `重拳出击` 等
- **391812 = 宸世臻藏金色奖励**（行114387 name 直读）；391560 = 宸世臻藏；391811 = 水晶家具宝箱；391798 = 中秋兔子不放回7
- 391808 = 讯猎物资箱池（成员含 讯猎币×4 + 福鼠迎春臻藏盒）；391807 = 信号猎手池（conf3 `reward_pool_id` 直证）

## 任务② 信号猎手/讯猎线（解开）

`vehicle_lottery_base_conf_data` 三行（字段全解）：
| conf | drone_module_name | reward_pool | 货币 | mail | 备注 |
|---|---|---|---|---|---|
| 1 | 溶蚀机枪-进阶6 | 391593 | **155736 飞行令牌** | 3206 | 展示图 icon_1360005_b；中间物 128481 溶蚀机枪进阶芯片 |
| 2 | 典藏涂装：碧辉 | 391721 | **155951 晶蝶币** | 3240 | middle_item **180623 典藏涂装：碧辉**；图 icon_180612_b |
| 3 | 信号猎手-进阶6 | 391807 | **156236 讯猎币** | 3352 | middle_item **1360012 信号猎手**；图 icon_1360012_b |

- 兑换商店：`exchange_shop_conf_id` 1/3/5（表在包，**CHS 未随包** → 货架明细本轮给不出名字，等热更或 UI）
- 讯猎币机制（道具文案直读）：幸存者在活动中获得的部分道具可在【暂存箱】中分解为讯猎币；讯猎币在兑换商店换道具；活动结束自动回收为新币 → 对应 conf3 的 `decomposition_item_ids`（`storage_decomposition_item_ids` = 1型/2型记忆材料 + 纳米塑材自选箱）
- 展示条 34 条：信号猎手-进阶2/4/6（1360007/1360010/1360012，视频 xinjq3~6）、涂装：绯影（180622，hdwrj2）、典藏涂装：碧辉（180623，hdwrj1）、溶蚀机枪（wrjjqanye1-3 / wrjjqjiguang1-3）、技能特效 id 3086–3107


## 2026-09-11 · 08Lifeafter wiki 修完轮（体验服 2026-09-10 热更后）

**目标**：把 wiki 修到与新包一致 + 上线"预告专栏"（零栏两卡）。

**已完成**
1. 源锁对齐：`data/live_sources.json` 的 `documents-py314-current` → `328b8446…dc59f`（188,064,088 B）；`audit_live_sources --include-disabled` 全 verified；工具/测试/文档 31 处 SHA 常量统一；`source_registry.json` test 端 script 条目重锁。
2. 预告专栏上线：`skin_behavior_preview`（**2 条：1110185 / 1110186**）+ `future_lottery_preview`（**26 条**，窗口 2026-09-12~2027-10-23），policy retired→published，manifest 12 板，**无头 Chrome 实测主页已渲染两张卡**。
   - 新工具 `tools/preview_board_contract.py`：冻结产物 **契约 v3**（contract_version/primary 锁/source_scope/state_summary/逐条 locator_chain+upstream），支持显式 `source_lock`（用于如实登记冻结副本）。
   - 新工具 `tools/stamp_board_contract.py`：为已发布板**补** v3 机读定位链，只增字段、不改数据声明（chip / gift / nucleus_cards_classic 靠它过门禁）。
3. 武器皮肤链适配新包：**113 主 / 18 时限变体 / 131 总 / 2 行为预览（1110185、1110186）/ 352 SFX**；候选板 129→**133**。
   - 事实更新：**1110184 = 星火永传**、**1110190 = 佳期如梦**（均已成为 current_parent，不再"仅行为资源"）。
4. 重跑并落地：wiki_v01 全套（**硬门 28/28**，P4-D 23567/474/0 不变）、common_item 36267、gift 5477、fashion face 1145/wardrobe 19278(catalog 1356)/projection 40/bestplay 13/bag 69、nucleus item 130/entry 87/cards 77、芯片保底 **31 期**、核芯池 **73 期**、满减 11 期、mystery、kaijia、chip_item_catalog、lottery_pool_resolved 重锁。

**新纪律（本轮踩坑总结）**
- **FID 是内容派生的，热更即变**：`all_equips` 的 base `A130A31532FAF63C` 与 CHS `94AB0B3FD057EF01` 在 2026-09-10 包中**双双消失**。工具写死 FID 当长期真值 = 下次热更必炸。→ `rebuild_weapon_attrs_schema_static.py` 因此**未解**（待改为"扫包 + schema6109 结构验证自定位"）。
- **workcopy 来源必须如实标注**：`rebuild_chip_catalog.py` / `rebuild_nucleus_cards_classic.py` 读的是冻结工作副本 `config_work/script_py314_docs_BA8A239A`，不得盖当前包 sha；chip 板锁 = `frozen-workcopy-ba8a239a`。
- **P4-D3 冻结数据集标注其冻结快照**：`build_lottery_pool_resolved_v01.py` 的 `EXPECTED_SOURCE_SHA256` 保持 ba8a（用户冻结指令），不随热更改写。
- 计数类断言一律改**结构不变量**（如 `main+variant==total`、records 唯一），不写死具体条数。

**未完成（1 项）**
- `weapon_attrs_schema_static`：新包 all_equips base/CHS FID 变更，工具拒绝重建；已扫出 75 条含 `all_equips` 标记的大 payload 候选（12 条文本型 + 6 条二进制型），结构配对未命中。需要自定位解析器（扫包 → schema6109 结构验证 → 缓存）后再跑。

### attrs（武器属性板）FID 定位：静态链已穷尽 → 未命中

2026-09-10 包中 `all_equips` base/CHS 的旧 FID（`A130A31532FAF63C` / `94AB0B3FD057EF01`）均不存在。已按纪律穷尽静态链：

1. 旧板 provenance 记录：base entry 16135 / chs entry 14847，`decoded_sha256` 为 `8573bbe8…` / `b57a2f3e…`；
2. 冻结工作副本 `config_work/script_py314_docs_BA8A239A/entries/016135.bin`、`014847.bin` 两份旧 payload **sha 与记录完全吻合**（确认取到真身，非误配）；
3. 内容指纹扫描：CHS 用 all_equips 独有中文串（2560 个差集串）；base 用旧 base 独有 ascii 片段 + 头 16B；
   → 新包 CHS 候选收敛到 6 个 ~3.5MB 文本档（旧 1.28MB），但**与 common_item CHS 共享道具文案，差集分不开**；
4. `x{` BinDict 容器过滤：旧 base 的 `x{` 在**偏移 277**（非开头）→ 0.9–5MB 且含 `x{` 的候选 20 个；
5. **结构判定**：20 base × 6 CHS = **120 组**交给工具自身 schema6109 解析验证 → **0 命中**。

结论：该表的定位不能靠 FID/内容指纹恢复，需要**结构自定位解析器**（扫包 → 用 schema6109 行布局验证 → 缓存），或一个**实机 UI 锚点**（游戏内武器属性面板截图/表名）。
在此之前该板保持锁定在 BA8A 冻结快照（板内 provenance 已如实记为 `documents-py314-current@ba8a239a`），**不冒充新包**，测试 `test_rebuild_weapon_attrs_schema_static` 保持红并作为待办标识。

### attrs 自定位解析器（结构反查）—— 已实现，0 命中（2026-09-11）

工具：`08Lifeafter wiki/tools/locate_all_equips_pair.py`
方法：扫包 → `xbody()` 取容器 → 分 base-like（`base_blob()` 行数≥500）/ chs-like（`strings()` 串数≥2000）
→ 逐对跑 codec 的 schema6109 校验（field_count==55 且 field[23]=='hurt'、field[35]=='power'）+ 关系条数下界。

实测候选画像（体验服 328b8446 包）：
- base-like **25** 个（最多 15,972 行 / 796KB；另有 13,486、13,244…）
- chs-like **71** 个（最多 35,133 串；文本型 ~1.1–1.3MB / 3.5MB）
- **配对校验通过 = 0**

推论：新包里 all_equips 的表示形态与旧 codec 的假设不再匹配（不只是 FID 变了），
`x{` 容器 + 行表/文本池这一套结构在这两张表上已不成立。
→ 该板继续锁 BA8A 冻结快照（板内 provenance 已如实标注），测试保持 expectedFailure。
→ 下一步只剩"实机 UI 锚点"（游戏内武器属性/装备属性面板的字段或截图）或更深的表格式逆向；
   不建议再扩大盲目配对（已试 25×71 = 1,775 组）。

## 2026-09-11 · 08Lifeafter wiki 中文化 + 时限变体附属化（玩家图鉴页）

- **时限变体展示定版（前端）**：永久皮肤=唯一主卡；18 个时限变体=主卡内 details.vv 紧凑列表，
  每行只显示差异（7天版/14天版/30天版/时限版 + ID timed_id，品级/类型/上架时间/名称仅当与主项不同）；
  不再生成完整子卡（旧 .variant-child 卡片式 UI 删除）。顶层统计/排序只吃主卡；统计文案「时限变体 N（并入主卡，不单独计款）」。
  搜索变体 ID/名 → 命中主卡：_hay 含变体 id+display_name，命中时主卡加 open 类 + 详情展开 + .vv-hit 高亮。
  P4 候选板保留逐记录结构（未动）。//10 关系与底层数据未改。
- **可见性坑（截图复核抓住）**：详情可见性由 `.skin-card.open .skin-detail{display:block}` 决定，只摘 hidden 属性用户仍看不到 →
  现同时给 open 类与 aria-expanded=true；护栏 tests/test_timed_variant_ui.py。
- **中文化（只改显示层）**：FIELD_CN（全部已发布字段中文名）/VALUE_CN/STATE_CN/TERM_CN+zhText()/TITLE_CN+zhTitle()；
  工程字段（FID/payload/schema/provenance/identity_*）统一折叠进「技术详情 / 数据来源 / 审计信息」，原始字段名只留悬停。
  未动 P4/identity/join/ITEM_MASTER/LOTTERY_POOL_RESOLVED/排序逻辑。
- **验收**：analysis/tools/check_zh_surface.py 六页可见区裸英文 0/6；check_timed_variant_ui.py 全部通过
  （115 主卡 / 18 变体块 / 18 紧凑行 / 搜索 11101771 → 主卡极光剑展开高亮 / 候选板 133 条保留）。
  全量测试 244 OK（expected failures=1）。提交 86c9653 → 953080f。
- **教训**：①改内联 JS 必须 node --check（一处括号错=整页空白，DOM 检查会把模板串当渲染结果误判）；
  ②统计 DOM 前必须剥 script/style（否则模板串虚增计数）；③前端改完必须截图+视觉复核。
- **挂起（用户明令暂停）**：时限变体识别门槛两步化——先 is_timed_skin_id(item_id)（区间判定）再 get_perm_skin_id = //10；
  parent_set 只做一致性审计（parent 在=resolved / 不在=missing），不得由 k//10 in parent_set 反推 timed 身份。
  待用户解禁后再改 rebuild 逻辑+回归测试+技能文档+board notes。

## 2026-09-11 · 武器皮肤名称展示改三级（name_status）+ 前后名称对比

- **前后对比（用户要求先查）**：旧 `data/boards/weapon_skins.json`（git `7f30344`，已删板）= 128 条**全部有名**
  （97 structure + 31 candidate）。现在：图鉴板 113 主卡 verified 名 + 候选板 121 条候选名（历史参考表）
  + 旧 128 条中仅剩 10 条只在候选板；**“有旧名称但现在被清空”= 0 条**（旧板里 5 条本就写“(未命名)”，
  其中 3 个是时限变体，现已以「主名（N天/时限版）」展示）。
- **真问题**：候选板 133 条的 `name` 全是占位「武器皮肤静态记录 · ID」✗，而 121 条 `candidate_name` 挂在数据里
  没被当主标题展示 → 用户看到“很多记录没名字”。
- **定版规则（前端+生成器）**：`name_status` 三级（verified / candidate / unresolved）与 `identity_status` 独立；
  candidate 继续显示 + 页面「名称待确认」徽章且不升级；unresolved 显示「未命名皮肤 · ID <skin_id>」；
  `name_display`/`name_status_note` 落库；meta `name_status_summary` + manifest 透传 + 页面 pills/统计行。
  图鉴板：主卡 113 verified、变体 13 verified/5 candidate、行为预告 2 unresolved。
  候选板：121 candidate / 12 unresolved，identity 全部保持 unresolved。
- **未越界**：整数碰撞 verified 链未恢复（`legacy_integer_join_reenabled=0`）、SFX 未当皮肤名、all_equips 仍禁用；
  未重开 P4-C 身份研究。
- **验收**：`tests/test_name_status_tiers.py`（9 项）+ 修正 4 处旧断言 → 全量 **254 项 OK**；
  `analysis/tools/check_name_status_ui.py` 浏览器 15 项全过（候选名 121 张、未命名 12 张、徽章/统计）；
  `check_zh_surface.py` 六页可见区裸英文仍 **0/6**。提交 `17bbf10`。
- **测试坑**：候选名与同记录 SFX 文本可能同名（UI 把皮肤名显示在特效行）→ 名称来源判定看来源字段，别用字符串相等。

## 2026-09-11 · 武器皮肤板统一整改（名称/变体/筛选/排序/中文化）

- **名称三级**（与 identity 独立，不因 unresolved 清空）：图鉴板 verified 126（113 主卡 + 13 变体）/ candidate 5
  （主名+时限后缀推导，页面「名称待确认」）/ unresolved 2（预告层→「未命名皮肤 · ID」）；
  候选板 0/121/12，identity 全保持 unresolved。`name_display`/`name_status_note` 落库，meta 带 name_status_summary。
- **时限变体**：主卡内 `<details class="vv">` 紧凑列表（只显示差异：N天版/时限版 + 时长 ID + 真实不同字段），
  不生成子卡；顶层统计/排序只吃主皮肤；搜索变体 ID → 定位主卡 + 展开高亮。
- **时限门禁改两步法**（用户口径）：`is_timed_skin_id(k)` 区间判定（`TIMED_SKIN_ID_MIN/MAX = 11_100_000~11_199_999`
  常量 + 命名函数）→ `permanent_skin_id = k // 10`；`parent_set` 只做一致性审计
  （新增 `variant_relation_target_state = resolved|missing`）。**已删 `k>9 and (k//10) in parent_set` 反推**；
  无 `%10`/末位门槛。重跑结果不变：113 主 / 18 变体 / 2 预告。
  注：会话与仓库里都找不到你手头那份 `is_timed_skin_id`  оригинала 区间常量，我按「区间判定 + 快照自证」实现，
  若你的常量边界不同，改 `TIMED_SKIN_ID_MIN/MAX` 一处即可（会由 test_weapon_skin_board_filters_sort 自证）。
- **筛选重设计**：武器种类 / 品级 / 联动IP / 上架状态 / 名称状态 五路独立、真实枚举、可组合（实测霰弹枪+典藏级=3）。
- **排序只留三组**：皮肤ID ↑↓ / 上架时间 ↑↓；**无可靠图鉴顺序字段**（`priority` 16 去重≠顺序、`obtain_limit` 恒 1）
  → 默认「皮肤 ID ↓」+ 页面写明依据，不伪造图鉴顺序。筛选与排序互不重置。
- **验收**：`analysis/tools/check_weapon_skin_board_ui.py`（同源 iframe 探针驱动真实 UI，22 项全过）、
  `check_name_status_ui.py` 15 项、`check_timed_variant_ui.py` 17 项、`check_zh_surface.py` 六页 0/6；
  新增 `tests/test_weapon_skin_board_filters_sort.py`（17 项，Node VM 驱动真实 render）→ 全量 **271 项 OK**。
  提交 `c29ff48`。

## 2026-09-11 · 只读核验 is_timed_skin_id 真实函数体（结论：区间常量 = 11_100_000 / 11_199_999）

- **扫描范围**：`analysis/tools/find_timed_skin_runtime.py` 对两个包（documents-py314-current + root-baseline）
  **共 133,245 条 entry 全部解包扫描** + npk 原始字节扫，不做抽样、不靠样本反推。
- **定义处**：`com\utils\EquipSkinHelpers.py` 模块级函数 `is_timed_skin_id`
  —— 当前包 FID `A108220338E1AE9B` / entry#17364（declared 36,744，flag=2）；root 基线同 FID / entry#66807（跨版本稳定）。
- **消费方**：`com\components\avatar\EquipSkinComp.py`（FID `822E3046861AA53C` / entry#14032）
  含 `is_timed_skin_id` / `get_perm_skin_id` / `get_timed_skin_duration`；另有 `9CF387E2D156513B`（WEAPON_SKIN_DATA + 调用）与 `9A73B523DB1D64FC`。
- **字面量**（函数 code object 常量区，函数名前 ±200B 只有两个 int32，下界→上界紧邻）：
  `0x3E 60 5F A9 00` = **11,100,000**；`0x3E FF E5 AA 00` = **11,199,999**
  （0x3E = 该客户端自定义序列化的 int32 常量标记，不是 CPython marshal 的 'i'）。
- **运算符**：**不可直读**（真字节码 + 自定义序列化，本地无 py314 解释器/该 VM opcode 表）。
  `<=…<=` 与 `<=…<` 对本域等价（时限 id = 永久 id*10+n，永久 id ≤ 1,110,200 → 最大 11,102,009，取不到上界值）。
- **额外条件**：**无**（函数内仅此两个字面量，无取模、无第三个比较常量）。
- **升级**：常量对与实现完全一致 → 写进工具 `TIMED_SKIN_ID_EVIDENCE`（模块/FID/entry/字面量/扫描范围）+ 板 notes，
  加断言 `test_timed_interval_bounds_match_runtime_evidence` 锁住；全量 **272 项 OK**。提交 `20afc4e`。
  `timed_id // 10 → permanent_skin_id` 的已验证关系未受影响。
- 证据产物：`analysis/audit/timed_skin_runtime_probe.json` + `analysis/audit/timed_skin_hits/*.bin`（只读留存 352K）。

## 2026-09-12 · published_hidden 服务端门禁收口 + 旧验收脚本同步（commit `ac18cdc`）

**背景**：首页信息架构收口后，两个旧武器皮肤入口改为 `published_hidden`（首页不列、直链可开）。
本地服务打开隐藏板出现 404。

**根因（两层，缺一不可）**：
1. 服务端 `data/boards/<board>.{json,js}` 资产门禁原先只认 `published`（`is_public_board`）→ hidden 被拒；
2. 上一轮 kill 后**服务进程未重启**（`netstat` 无 8765 监听）——现象与门禁问题相同，极易误判。

**收口口径（同一套 helper）**：
- `is_public_board()` = 首页可见（仅 `published`）：`build_wiki` manifest 过滤 / `public_board_ids`
- `is_openable_board()` = 直链可开（`published` | `published_hidden`）：`wiki_server` 资产门禁、`board.html` 客户端门禁
- `retired` / `quarantined` / 未登记 → 两者皆 False（照旧阻止普通访问）

**实测（真实 HTTP + 服务重启）**：
- `weapon_skin_sfx_text_sources` / `weapon_skin_static_candidates_v01` / `weapon_skin_structure_v01`：
  `board.html?b=` / `.js` / `.json` 全 **200**
- retired（`common_item_text_sources` 等）与不存在板 `.js` → **404**；`data/live_sources.json` → 404
- 首页：时装类武器皮肤入口 **1**、战力类 **0**、隐藏板未回首页；manifest **11 板**
- 3 个旧验收脚本（武器皮肤/时限变体/名称状态）**0 未通过**；中文化 0/6；publication gate + frontend usability 18 OK
- 全量 **297 项 OK**（expected failures=1）

**经验（已写进技能 lifeafter-wiki-boards）**：
- 改 policy 状态要搜完 `rewrite_publication_policy()` 内**全部** `boards.update`（后面一处会把状态改回去）
- 控件从"一个大排序菜单"拆成"排列依据+方向"后，探针设完方向必须**再触发一次 render**（方向按钮不派发事件）
- 排障先分清"服务没起来"与"门禁拒绝"：curl 404 + 无监听 = 进程问题

## 2026-09-12 · P4-C 武器皮肤 identity/name 主链只读调查（进行中，commit `ae6956f`）

**已完成扫描**：`analysis/tools/find_weapon_skin_chain.py`（10 个 needle，两个包）
- Documents 当前包 27,468 条 entry 全扫 → 命中 198 条；root 全量包 105,777 条 → 命中 327 条
- 产物：`analysis/audit/weapon_skin_chain_probe.json` + `weapon_skin_chain_hits/*.bin`

**Q1（runtime data 的 key 是否＝原始行 key）→ 有 producer+consumer 双证，答案是"是"**
- producer：`com\cdata\weapon_skin_data.py` 走标准 cdata 装载链（`TableImportHelper.fix_translate_data` +
  `bindict` + `data` + `set_adaptive_cache_strategy`），数据来自同名 BinDict
- 原始表：125 行，`key` = 1110001…11101811（与板内 skin_id 同空间）；行字段含
  `weapon_type / model_path / sale_ts / level / skin_replace_anims / fire_sfx_path …`
- consumer：`EquipSkinHelpers.get_weapon_type_name_by_skin_item_id` 邻域为
  `skin_item_id | raw_data | weapon_kind | WEAPON_SKIN_DATA | data | get | NUCLEUS_WEAPON_TYPE_DATA | weapon_type`
  ⇒ `raw_data = WEAPON_SKIN_DATA.data.get(skin_item_id)`，随后读该记录的 `weapon_type`（**只有本表提供该字段**）
  ⇒ key 空间 = 原始行 key 空间（字段级链接，不是整数巧合）

**Q3（skin→item/name 显式链）→ 已定位候选消费方，待函数体级确认**
- `EquipSkinComp`（FID `822E3046861AA53C`）：`find_skin_by_item_id` / `get_skin_id_by_item_id` /
  `get_equip_skin_item_ids` / `check_equip_weapon_kind`（item↔skin 双向转换的存在本身＝显式映射消费方）
- `EquipSkinHelpers`（`A108220338E1AE9B`）：`get_item_data` / `get_item_num` / `skin_item_id`
- 道具名通道范式已证存在：`BagCompBase`（FID `0D86C2AE10376C4E`）里
  `COMMON_ITEM_DATA | data | get | item_id | item_info`
- 映射表主体已定位：**`com\cdata\weapon_kind_to_skin_item_data.py`（entry#7590，FID `478A79D619123CBC`，960B）**；
  其余 23 条命中全是 `com\cdata\oversea\weapon_kind_to_skin_item_data_auto_oversea_data_<通道>.py`
  （kj1/kjxq/ykxq/xq/yk/na/eu/sea/kr/jp/hmt/kjhmt/kjjp/kjna）→ **禁止跨通道混用**
- 下一步：解 `weapon_kind_to_skin_item_data` 的数据条目（kind→skin_item 映射），
  再对 115 主皮肤反向验证"skin_item_id 是否落在 common_item_data 的 key 上"；
  若成立 ⇒ 现 113 个 verified 名不是"整数碰撞"，而是客户端同款 `COMMON_ITEM_DATA.data.get(id)` 查找路径。


---

## P4-C 武器皮肤 identity / name 主链 —— 名称链闭合（2026-09-12，USER 授权升级）

**结论**：客户端 UI 名称消费链成立 ⇒ 113 个主皮肤 `name_status=verified`，证据类型 **`verified_runtime_ui_lookup`**。

### 可复放链
```
skin_item_id
→ PanelWeaponSkinCollection.update_right_info(self, skin_item_id, ...)  [ui\PanelWeaponSkinCollection.py, root FID BC1BEF691C819C9C]
→ Helpers.get_item_data(skin_item_id)                                   [com\utils\Helpers.py entry#22533 FID D0DE63643D7F43B7]
→ DataHelpers.get_item_data → get_item_type → get_item_data_module_name  [com\utils\DataHelpers.py entry#20487 FID BE842BC2295D957F]
→ import com.cdata.<module> → <MODULE>.data.get(item_id)
→ common_item_data (COMMON_ITEM_DATA.data.get(skin_item_id))
→ item_data.name / item_data.desc
→ txt_stickers_name01 / txt_stickers_desc01（set_string / set_rich_str）
```

### 支撑点
- `update_right_info` 形参即 `skin_item_id`（varnames 段 `self ｜ skin_item_id ｜ unlocked ｜ item_data ｜ item_level ｜ prefix`）
- `DataHelpers.get_item_data` 定义体按 item_type 在 `all_equips_data / common_item_data / belt_chip_data` 间分派后 `data.get(item_id)`
- 跨表成员实测（`data/row_index.jsonl`）：1110001/1110002/1110146/1110177 在 `weapon_skin_data` + **`common_item_data_base`**，**不在 `all_equips_data`**
- 面板整体以 item id 认皮肤：`SkinItem.set_data` 字段集 + `equip_skin_comp.try_view_equip_skin_by_item_id`
- 不是"两表整数相等 join"，而是客户端自身 item lookup + UI consumer 链

### opcode-level 残差（随产物发布，不阻塞名称语义，不再追）
- `operand-level call binding = unresolved`（无 VM opcode 表）
- `numeric item_type constant = unresolved`（VM 常量级不可读）

### 绑定状态（严格区分）
| 绑定 | 状态 |
|---|---|
| runtime_row_binding | **verified** |
| name_binding | **verified_runtime_ui_lookup** |
| business_identity | **unresolved**（待单独审 owned / unlock / sale / 商城兑换 / equip-view 是否同键） |

### 隔离
`1110185` / `1110186` 保持 unresolved：无 weapon_skin 主数据行、无 common item 行、无名称源；未从行为资源/SFX/模型路径/oversea/all_equips 补名。

### 产物 WEAPON_SKIN_RESOLVED_v0.1
- `data/WEAPON_SKIN_RESOLVED_v0.1.jsonl` sha256 `4ec89b8d5917870b7777d4abe41dd09350e5dfa3f10691499510ec34c62eb9e4`
- `data/WEAPON_SKIN_RESOLVED_v0.1_RULES.json` sha256 `fe85f008d3d1999d0bcb7f9289fb8cc326a4e78012dc66d7cbc8aeec84102ab0`
- audit `data/audit/weapon_skin_resolved_v01_audit.json`
- 计数：主记录 115 / 名称 verified 113 / unresolved 2；timed 变体 18（名 verified 13 / candidate 5）
- 生成器 `tools/rebuild_weapon_skin_resolved_v01.py`（只读图鉴板，只写 data/，不改页面）


---

## P4-C business identity 独立审计（2026-09-12，只读，未升级）

**目标**：判断 `skin_item_id` 是否可作为客户端武器皮肤业务主键。**结论：证据到 API/形参级，未达 VM 操作数级 ⇒ 本轮保持 `business_identity = unresolved`。**

### 核心路径证据（payload 窗口级，非符号共现式结论）

| 路径 | API/位置 | 窗口证据 | 判定 |
|---|---|---|---|
| raw/runtime lookup | `EquipSkinComp.check_equip_weapon_kind` | `WEAPON_SKIN_DATA.data.get(skin_item_id)` → `skin_data` → `get_skin_weapon_type` → 与 `equip_data`(weapon_kind) 比较 | PASS |
| owned | `EquipSkinComp.get_all_unlocked_skin_item_ids` | 与 `get_all_unlocked_decal_item_ids` / `get_all_unlocked_pendant_item_ids` 同族，命名与变量均为 `*_item_ids` | PASS(API级) |
| unlock | `EquipSkinHelpers.check_player_has_skin_item` | 同窗口 `player｜equip_skin_comp｜skins｜item_id｜skin_id｜skin｜skin_item_id`；玩家 skin 记录同时带 `item_id` 与 `skin_id` | PASS(API级) |
| equip | `EquipSkinComp.get_equip_skin_item_ids` | 局部变量 `skin_item_ids｜equip｜skin_item_id｜skin_data`；遍历 `WEAPON_SKIN_DATA` + `is_timed_skin_id`，按当前装备武器 kind 过滤 | PASS |
| equip(装配) | `EquipSkinComp.get_equipped_id_by_skin_id` / `check_can_equip_skin` | 与 `check_equip_weapon_kind` 同族；`equipped_id｜skin_setting｜item_id` | PASS(API级) |
| view/试穿 | root `PanelWeaponSkinCollection.SkinItem.set_data` | 字段集 `item_id｜is_unlocked｜is_new_unlocked｜is_new_sale｜name｜icon_large｜level`；`equip_skin_comp｜server｜try_view_equip_skin_by_item_id`；`selected_skin_item` | PASS |
| view/preview | `ui\weapon_skin\WeaponSkinPreviewV2` | `curr_select_skin.item_id`；`WEAPON_SKIN_DATA.data.get(skin_item_id)`；`_is_shield_skin(skin_item_id)` | PASS |
| sale | 仅见记录字段 `is_new_sale`（上架标记） | 无独立出售/上架配置 consumer | **absent（不猜）** |
| shop/exchange/acquisition | 本轮未追（按 USER 要求不扩范围） | — | **absent** |

### 身份空间混淆风险（已定位，可控）
- `skin_id` 与 `skin_item_id` **确为两个空间**：存在双向显式转换函数 `EquipSkinComp.get_skin_item_id(skin_id)`（varnames `self｜skin_id`）与 `EquipSkinComp.get_skin_id_by_item_id(item_id)`、`get_equipped_id_by_skin_id`、`find_skin_by_item_id`
- 另有独立空间：`sample_weapon_id`（`EquipSkinHelpers.get_sample_weapon_id_by_skin_id`）、`sfx_item_id`、背包普通武器 `equip_data.item_id`
- 风险点：这些 id 在**同一函数窗口内共现**，仅凭命名/共现不足以定 key；必须靠转换函数边界隔离

### 残差（与名称链同源，同一 VM 限制）
- `operand-level call binding = unresolved`（无 VM opcode 表）
- 新增：`business key 单一性未做 opcode 级证明`（多条 API 命名一致 ≠ 操作数级同一 key）

### 产物
`WEAPON_SKIN_RESOLVED_v0.1` **未改动**：business_identity 保持 unresolved。


---

## P4-C business identity 升级：单函数闭环取证（2026-09-12）

**USER 选 B（先补单函数闭环）→ 闭环已拿到，113 条升级 `verified_runtime_business_key`。**

### 单函数闭环（形参/局部 → 同一值流，同函数内 producer→consumer 连续）

| 业务路径 | 模块 / FID / entry | 函数 | 同一值流 |
|---|---|---|---|
| owned | `com\components\avatar\EquipSkinComp.py` / 9CF387E2D156513B / #16905 | `get_all_unlocked_skin_item_ids(self)` | `self.skins`（每项 `skin.item_id` + `expire_ts`）→ `add` → 结果集 `all_unlocked_skin_item_ids`（元素即 skin_item_id） |
| equip | 同上 | `get_equip_skin_item_ids(self, equip_id)` | 遍历 `WEAPON_SKIN_DATA.data` 键 `skin_item_id` + `is_timed_skin_id` + `get_skin_weapon_type(skin_data)` 过滤当前装备武器 kind → `append(skin_item_id)` → `skin_item_ids` |
| equip-check | 同上 | `check_equip_weapon_kind(self, equip)` | 同函数 `WEAPON_SKIN_DATA.data.get(skin_item_id)` → `skin_data` → `get_skin_weapon_type` → 与 `equip_data` 的 weapon_kind 比较 |
| view | `ui\weapon_skin\WeaponSkinPreviewV2.py` / 16422DF732CFCD6C | `update_use_primary_weapon_model_setting(self, ..., skin_item_id, ...)` | 同函数 `WEAPON_SKIN_DATA.data.get(skin_item_id)` + `_is_shield_skin(skin_item_id)` + `equip_skin_comp.check_can_show_weapon_setting`（入口 `curr_select_skin.item_id`） |
| view-api | `ui\PanelWeaponSkinCollection.py` / BC1BEF691C819C9C | `SkinItem.set_data` | 记录字段 `item_id｜is_unlocked｜is_new_unlocked｜is_new_sale` → `equip_skin_comp/server.try_view_equip_skin_by_item_id`（`selected_skin_item`） |
| unlock/has | `com\utils\EquipSkinHelpers.py` / A108220338E1AE9B | `check_player_has_skin_item` | `player.equip_skin_comp.skins`（每项带 `item_id` 与 `skin_id`）→ has 判定（同窗口 `skin_item_id`） |

### id 空间隔离（强制）
- `skin_id != skin_item_id`；显式转换函数：`get_skin_item_id(skin_id)` ⇄ `get_skin_id_by_item_id(item_id)` / `get_equipped_id_by_skin_id` / `find_skin_by_item_id`
- 排除他域：`sfx_item_id`、`sample_weapon_id`（`get_sample_weapon_id_by_skin_id`）、背包普通武器 `equip_data.item_id`

### 修正（USER 指出表述过宽）
- `1110185 / 1110186`：无 `weapon_skin_data` 主数据行 ⇒ `runtime_row_binding` 由 `verified` 改为 **`no_main_row`**；`business_identity` 保持 **unresolved**；name 保持 unresolved
- 写入 RULES：**只有** `skin_item_id → WEAPON_SKIN_DATA.data.get(skin_item_id) → weapon_skin_data main row` 成立才可标 `runtime_row_binding = verified`
- 判定依据：图鉴板 `catalog_layer == behavior_preview_only`（等价 `official_name_status == no_item_row` / `evidence_level == structure-only`）

### 升级后状态
| 绑定 | 结果 |
|---|---|
| runtime_row_binding | verified 113 / no_main_row 2 |
| name_binding | verified_runtime_ui_lookup（113） |
| business_identity | **verified_runtime_business_key 113** / unresolved 2 |
| sale / shop / exchange | **absent**（获取来源未闭环 ≠ 核心业务主键未闭环） |
| opcode 残差 | `operand-level call binding`、`numeric_item_type_constant`（保留发布） |

产物 hash（本轮重生成）：
- `data/WEAPON_SKIN_RESOLVED_v0.1.jsonl` = 4ec89b8d5917870b7777d4abe41dd09350e5dfa3f10691499510ec34c62eb9e4
- `data/WEAPON_SKIN_RESOLVED_v0.1_RULES.json` = fe85f008d3d1999d0bcb7f9289fb8cc326a4e78012dc66d7cbc8aeec84102ab0


---

## P4-B 时装 identity 主链 —— runtime key 取证（2026-09-12，只读，未升级）

**口径**：复用 P4-3 套件（`business_ids_allowed=0` / `entity_names_allowed=0` / 5 项负对照）保持不变；Documents / root / oversea 通道严格隔离。

### producer
- `com\cdata\fashion_data.py`（entry #728 / FID 06EDEAAE3B08B985）标准 cdata 装载：`bindict + TableImportHelper.fix_translate_data + data + set_adaptive_cache_strategy/STRATEGY_MISS_RATE`
- 数据本体已在项目 `data/row_index.jsonl`：`com\cdata\fashion_data.py` = 10,710 行

### consumer：`FASHION_DATA.data.get(runtime key)`（函数级窗口 + varnames）
| 模块 · entry(root) | 函数 | 同函数证据 |
|---|---|---|
| `ui\store_v2\FashionPage.py` · #13828 | `FashionPage.get_fashion_data(self, fashion_id)` | varnames `self｜fashion_id` + locals `item_type｜fashion_data｜appear_id｜appear_part｜app_id`；同函数 `FASHION_MODULE_DATA.data.get`、`DataHelpers.get_fashion_data`、`APPEAR_DATA`、`try_wear_fashion` |
| `ui\PanelFashionPreview.py` · #17357 | `PanelFashionPreview.init_role` | `A2F_DATA.data.get` + `FASHION_DATA.get_active_items_str` + locals `fashion_id｜part_items｜fashion_data｜style` |
| `ui\PanelSakuraChangeFashionPop.py` · #16068 | 面板类 | locals `fashion_id｜fashion_data｜appear_id｜item_id`；同模块 `has_fashion_by_fashion_id`、`try_puton_fashion_module`、`server.puton_fashion` |
| `ui\PanelPlayerShowItemInfo.py` · #20674 | `show_fashion_tasting` | locals `fashion_ids｜fashion_id｜fashion_data｜express_data`（试穿） |
| `com\utils\HuodongHelpers.py` · #1239 | `get_fashion_video_path` | `FASHION_DATA.data.get(...) → fashion_data → video_conf`（读取该记录专属字段） |
| `ui\PanelAppearZxGallery.py` · #10967 | `init_bg_id` | `FASHION_DATA.data｜fashion_id｜get｜FASHION_BG_DATA` + local `fashion_data` |

串表顺序统计（root+documents 全命中）：`data + get + self + fashion_id + fashion_data` = **8×**（最强形态）；`data + get + fashion_id + ...` = 6×。

### 显式转换函数（key 空间隔离，单独记录）
- **`com.cdata.appear_id_2_fashion_id`**（全局 `APPEAR_ID_2_FASHION_ID`，别名 `A2F_DATA`）：`data.get(self.appear_id) → fashion_id` ⇒ **appear_id → fashion_id** 唯一正规通道
- `get_fashion_id_from_newfashion`（`com\utils\gm\GmCmd_mzw.py`）⇒ `new_fashion_id → fashion_id`
- `get_other_appear_by_appear_id_in_suit`（AppearHelpers）⇒ suit 内 appear 关系
- `FashionPage.get_fashion_data` 自身承载 `fashion_id ↔ appear_id/appear_part` 关系
- 禁用（沿用现有 RULES）：`appear_ids / gift_id / model_id / item_id / id_female / id_male / new_fashion_id_str` 不得作身份键

### 业务路径（同函数级）
| 路径 | 判定 | 证据 |
|---|---|---|
| owned / has | **PASS** | `fashion_comp.has_fashion_by_fashion_id_permanent`：`com.huodong_mission.CollectFashions6`（同函数含 `FASHION_DATA.data`）、`FashionCollectionBrand.update_detail_content.<locals>.<genexpr>`（`fid → has_fashion_by_fashion_id_permanent(fid)`）、`FashionItemUI.set_item_red` |
| equip / wear | **PASS** | `FashionPage.get_fashion_data(self, fashion_id)` 同函数 `try_wear_fashion`；`PanelSakuraChangeFashionPop` 同模块 `has_fashion_by_fashion_id` + `server.puton_fashion`；`SecretFashionPage.try_wear_fashion`；`TryWearFashionCount` |
| preview / 试穿 | **PASS** | `PanelFashionPreview.init_role`（`fashion_id → fashion_data → style`）；`PanelPlayerShowItemInfo.show_fashion_tasting` |

### 未解（本轮最小缺口）
1. `fashion_id` 是否 == 表 schema 的 `row_key`（需 loader 的索引规则；现有 RULES 把两者并列为候选字段，尚未定）
2. **物理 payload 归属仍 unresolved**：consumer 证据多来自 root；数据行由项目从 Documents 包读出；尚未证明 runtime 最终加载的正是 Documents 那份（含 base/export/oversea 变体）
3. 名称链（`name/show_name`）本轮未碰，继续不放行

### 产物
**未生成** `FASHION_RESOLVED_v0.1`；`business_ids_allowed` / `entity_names_allowed` 保持 0。新增只读扫描器 `analysis/tools/find_fashion_chain.py`（commit 1303b69）。


---

## P4-B 缺口 1：loader 索引规则 + `row_key ↔ fashion_id` 审计（2026-09-12，只读，结论：**不能升级**）

### 1. BinDict key 生成规则（客户端侧实证）
- cdata stub 统一样板（全包逐条确认）：`bindict | data | set_adaptive_cache_strategy | STRATEGY_MISS_RATE | [region_delete_keys] | com.lang.TableImportHelper | fix_translate_data | <table>.py | <module>`
- 实现模块 **`com\lang\TableImportHelper.py`（root entry #69993 / FID A8D468AB34D86D47，9,226B；另有 #5007 语言池）**：`bindict → set_string_pool(string_pool) → do_fix_translate_data / fix_replace_data / update_file_version_infos`
- ⇒ helper **只注入字符串池并做替换修补，不重建键** ⇒ `FASHION_DATA.data` 的键 = 表容器**结构键**（= 我们 `parse_index` 读的 0x76 索引尾键 = 项目 `row_key`）
- 残差：`bindict` 为引擎原生符号（不在 Python payload 内）⇒ **格式级契约已证，opcode/原生级未证**

### 2. `row_key ↔ fashion_id` 审计（项目自身候选表 + 已冻结 slot 规则）
对 `candidate_field=fashion_id`（**slot 52 / scalar_type 0x01 / p2_field_state=verified**）的全部记录逐条比对：

| table | schema | 行数 | row_key==fashion_id | 不等 | 缺值 | 重复 row_key | 重复 fashion_id |
|---|---|---|---|---|---|---|---|
| fashion_data_for_export_base.py | 13182 | 1111 | **0** | 1111 | 0 | 0 | 319 |
| fashion_data_for_export.py | 13197 | 1111 | **0** | 1111 | 0 | 0 | 319 |
| fashion_data_for_export_base.py | 12309 | 67 | **0** | 67 | 0 | 0 | 11 |
| fashion_data_for_export.py | 12324 | 67 | **0** | 67 | 0 | 0 | 11 |
| **合计** | | **2356** | **0** | **2356** | 0 | 0 | 330 |

样例：`(fashion_data_for_export_base, 13182, row_key, slot52值)` = [["fashion_data_for_export_base.py", 12309, 166559, 500], ["fashion_data_for_export_base.py", 12309, 166572, 544], ["fashion_data_for_export_base.py", 12309, 166599, 630], ["fashion_data_for_export_base.py", 12309, 166682, 651]]

⇒ **`row_key` 与 `fashion_id` 是不同 namespace（0/2356 相等；fashion_id 有重复而 row_key 无重复）**，禁止合并。
另有：RULES 冻结 `row_key_is_p2_field=false`（row_key 是 structural-row-key，不是 P2 字段）。

### 3. 结论（不升级）
| 项 | 状态 |
|---|---|
| `runtime key = fashion_id` | verified（既有） |
| `fashion_id → FASHION_DATA logical record` | verified（既有） |
| `fashion_id → raw row_key` | **unresolved（本次审计否定"相等"假设）** |
| `runtime row binding` | **不升级** |
| business identity | **不升级** |
| physical payload 归属 | unresolved |
| name / show_name | 不放行 |

### 4. 由此产生的新最小缺口（比原假设更具体）
1. **`.data` 的索引规范**：`bindict(...)` 的常量参数是否含"按指定 id 字段建索引"的配置（键是否一定等于结构 row_key）——需 stub 常量/引擎符号层证据
2. **runtime 时装表与 export 变体关系**：本次 slot-52 规则只覆盖 `fashion_data_for_export*`；运行时 `com\cdata\fashion_data.py`（BA8 快照 entry 022570 / FID E1645717C83FC968）+ CHS（entry 020834 / D016140651FEAB34）自身尚无同等级的 `fashion_id` 字段规则 ⇒ 它到底以什么为键仍未定
3. 候选表绑定的快照为 `ba8a239a…`（旧），当前快照 `328b8446…`；数字随快照变，规则结构不变 ⇒ 复用需重跑
4. 名称链（后置，未碰）

**本轮零升级**：未写 `FASHION_RESOLVED_v0.1`，未改 `FASHION_IDENTITY_*` 套件，未动 Wiki。


---

## P4-B 缺口 1 续：runtime `fashion_id` 的来源（2026-09-12，只读，选 A）

### 决定性发现：runtime `fashion_id` 来自 A2F 转换，不是 slot52
三处独立模块窗口一致（root 包）：

1. `ui\store_v2\FashionPage.py` · `FashionPage.update_avail_bg_ids`
   `part | bg_ids | APPEAR_DATA.data.get | **A2F_DATA** | **DataHelpers.get_fashion_data** | append | avail_bg_ids | ... | appear_ids | is_takeoff | has_body | appear_id | **fashion_id** | fashion_data | bg_id`
2. `com\utils\AppearHelpers.py` · `get_appears_from_player_team`
   `get_appears_from_player_team | appear_ids | **APPEAR_ID_2_FASHION_ID** | get | **DataHelpers.get_fashion_data** | appear_id | item_id | fashion_data`
3. `com\components\avatar\UgcProjectorBuildingObjectAppearComp.py` · `get_other_gender_appear`
   `appear_ids | APPEAR_ID_2_FASHION_ID | data | get | DataHelpers.get_fashion_data | self | appear_id | item_id | fashion_data`

⇒ **`appear_id` → `APPEAR_ID_2_FASHION_ID.data.get(appear_id)` → value → `DataHelpers.get_fashion_data(value)` → fashion record** ✓
⇒ 同一族还有：`FashionHDUI.show`（`DataHelpers.get_fashion_data` + locals `fashion_id｜fashion_data｜appear_id`）、`SuperFashionLotteryV11HDUI.get_cinema_fashion_data`（`FASHION_STORE_DATA.data.get`）、`FashionPage.update_shopping_cart`（`cur_appears｜fashion_comp.has_permanent_fashion｜Helpers.get_item_type｜RACE_CTRL_DATA｜FASHION_DATA`）、`CommonModelShowUI.get_fashion_data`（包装层）

### 由此解释 0/2356
- export 表 slot52 `fashion_id` **≠** 结构 `row_key`（0/2356 相等，且 slot52 有重复、row_key 唯一）⇒ 两套 namespace
- runtime 侧那个名叫 `fashion_id` 的值来自 **A2F value**（第三套空间）⇒ 之前"`row_key == fashion_id` 稳定成立"的前提本身就是选错了对照对象 ⇒ **0/2356 现象已被结构性解释**（不是"证据不足"，而是"对象错位"）

### 未完成（本轮最小缺口）
- **A2F 表本体未提取**：Documents 只有 1 条 stub（#10243 / 5FA629EFB3B8CB74）；root 有 105 条引用，但 3 个最大条目用常规帧路径解码失败（`base reserved != 0`），疑为 **BigTableSplit 分片**形态（旁证：`DataHelpers` 引用 `BigTableSplitConsts/BigTableSplitType/get_big_table_split_module/get_big_table_split_data`）
- 因此 A2F **value 集合**未得 ⇒ 无法做 A2F value ↔ FASHION_DATA row_key / ↔ slot52 的集合对照
- 项目既有 RULES/索引里**没有** A2F 条目（FIELD_RULES/SOURCE_RULES/RELIABLE_SOURCES 均 0 命中）⇒ 需新做

### 口径（按 USER 要求三分）
- `runtime_fashion_key`（代码里常叫 `fashion_id`）= A2F value 空间（来源已证，值域待取）
- `export_fashion_id_slot52` = 独立 namespace（已证 ≠ row_key）
- `row_key` = 结构索引 namespace
三者不得因同名而合并。

### 状态
`runtime row binding` **仍未升级**；`business identity` 不升级；未生成 FASHION_RESOLVED；未碰 Wiki / oversea / 名称链。


---

## P4-B 缺口 1 续 2：A2F 提取尝试（2026-09-12，只读；未提取成功，已定位卡点）

### 1. BigTableSplit 装配规则（已还原，来自 DataHelpers 函数窗口）
```
SPLIT_INFO.data.get(key) → split_info → {split_type, shard_no}
→ get_module_name(...) → "com.cdata.%s" → BasicHelpers.import_module(module)
→ get_big_table_split_module(...) / get_big_table_split_data(...) → module.data.get(key)
```
分片注册表：**`com\consts\BigTableSplitConsts.py`（root entry #20459 / FID 30E5E6D6090D9980 / 1056B）**，模板串 `monster_data_%s / distortion_infect_monster_data_%s / random_item_reward_data_%s / mission_step_data_%s / skill_stage_data_%s / building_object_data_%s / monster_attributes_data_%s`，常量 `MONSTER_DATA / DISTORTION_INFECT_MONSTER_DATA / RANDOM_TIEM_REWARD_DATA / MISSION_STEP_DATA / SKILL_STAGE_DATA / BUILDING_OBJECT_DATA / MONSTER_ATTRIBUTES_DATA / SPLIT_INFO`。

⇒ **只有 7 张分片表，`appear_id_2_fashion_id` 不在其中** ⇒ **A2F 不是分片表**（此前"疑为分片"判断作废）。那 3 个大条目（389KB/331KB/293KB）实为 UI/代码模块（各自只含 `com\utils\UIHelpers.py` / `ui\PanelTeamFullScreen.py` / `character\AppearController.py`）。

### 2. A2F 真实资产位置（当前 Documents 包，按内容实测）
- 模块 stub：`com\cdata\appear_id_2_fashion_id.py` → **entry #10243 / FID 5FA629EFB3B8CB74 / 55,536B**（样板结尾 `bindict | data | set_adaptive_cache_strategy | TableImportHelper.fix_translate_data | com\cdata\appear_id_2_fashion_id.py | <module>`）
- CHS 兄弟（项目路径表所载）：`com\cdata\appear_id_2_fashion_id_chs.py` → FID 4EC2AC33F40CCBDB
- 通道变体隔离：`oversea/appear_id_2_fashion_id_auto_oversea_data_{xq,eu,kjxq}.py`

### 3. 新发现：项目已有 Documents `tI` 逻辑路径表（表名 → FID 的通用解析器）
`03拆包产物/config_work/path_tables/script_documents_c230d49114f0_ti_paths.json`（**600,671 条路径**，schema `lifeafter-nxpk-ti-path-table-v1`）。
⚠️ 该表绑定**旧快照** `c230d49114f0`，与当前包条目索引/FID 不完全对应（实测按 FID 取条目时 KeyError vs 内容扫描命中，两套口径不一致）。

### 4. 卡点（本轮最小缺口）
A2F **value 集合未取到**。原因不是规则不明，而是**当前 npk 原始条目的载荷取帧实现不对**：
- 我自写的取帧（`x{` + 4 字节长度）在**当前 npk 条目**上全部失败（`base reserved != 0` / body 越界），在抽出的 `entries/*.bin`（BA8A）上同样失败
- 项目工具能跑通 ⇒ 必须**复用工具库的确切实现**（`toolkit_core.npk_extract.NpkReader` / `bindict_provenance` 的载荷包装），而不是自建取帧
- 结论：缺的是 **当前包的载荷解码路径（工具库取帧/解包实现）**，不是 A2F 语义

### 5. 状态（未升级）
`runtime fashion_key → raw FASHION_DATA row` 仍 **unresolved**；`business identity` 不升级；`physical_payload_binding` 独立仍 unresolved；未生成 FASHION_RESOLVED；未碰 Wiki / oversea / 名称链 / slot52。

### 6. 下一轮精确动作（不扩大范围）
用项目既有解码入口（照抄 `tools/lib_fashion.py` + `rebuild_fashion_wardrobe_slots.py` 的 `_read_by_fid` + 其 `_xbody` + `parse_legacy_chs_pool` + `decode_table_rows_with_chs_slots` 组合，在**同一快照**内配对 base/CHS）解出 A2F；若该组合在当前快照仍失败，则先重建当前包的 `tI` 路径表并按新 FID 取表。


---

## P4-B A2F 提取（第 3 轮）：用项目工装链同快照尝试（2026-09-12，只读；**未解出，失败层已定**）

### 唯一 snapshot（本轮口径）
`documents-py314-current`（`data/live_sources.json` 注册表；包 `E:\mrzh\Documents\script.py314.lc.npk`，27,468 条目）。**不再混用** BA8A 工作副本 / 旧 tI 路径表（仅作结构参考）。

### decoder 自检：PASS ✓
用工装原实现（import `rebuild_fashion_wardrobe_slots._read_by_fid` / `._xbody` + `parse_legacy_chs_pool` + `decode_table_rows_with_chs_slots`）：
- `fashion_data` base FID `E1645717C83FC968` → entry **24340**；CHS FID `D016140651FEAB34` → entry **22449**；CHS 池 19,675
- **解码 19,276 行**（未绑定 2 行）⇒ 取帧/解码链路本身没问题；此前失败全部源于我自写 `x{`+4B 取帧与 `parse_index` 用法错误 ✓ 已纠正

### A2F 定位（同快照，按内容实测）
- 模块：`com\cdata\appear_id_2_fashion_id.py` → entry **#10243 / FID 5FA629EFB3B8CB74**（declared 55,536B / decoded 65,698B）
- **CHS：当前快照不存在**（旧路径表载 `4EC2AC33F40CCBDB`，已失配）
- 通道变体隔离：`oversea/appear_id_2_fashion_id_auto_oversea_data_{xq,eu,kjxq}.py`
- 该条目 **3 个 `x{` 帧**均非 BinDict 表体：
  - @263 len=64,983 → 尾部 `760101d6`（非 0x76 索引）
  - @17136 len=54,368 → `base reserved != 0`
  - @21367 len=10,075,803（可得 44,325B）→ `base reserved != 0`
  ⇒ #10243 是**模块包**（代码 + 字符串池），不是数据表

### 全包结构搜索（同快照，定向）
13,246 条候选（300B–60KB）→ 6,098 条有帧 → 252 条"纯整数" → **5 条可解**（#22118 / #17932 / #27428 / #27221 / #6226，均为小整数配置表，值 76/80/52/352 之类）；**没有任何一条的值落在同快照 FASHION row_key 空间（19,276 keys）**。

### 失败层判定（按 USER 五层）
| 层 | 结果 |
|---|---|
| 1 path → FID | **OK**（内容实测；但只解析到"模块"，旧路径表里 A2F 也无独立数据条目） |
| 2 FID → entry | **OK** |
| 3 **payload framing** | **FAIL ← 卡在这里**（模块条目无可解 BinDict 体；快照内也无独立数据条目） |
| 4 base/CHS snapshot 配对 | 部分：当前快照 **无 `_chs`** |
| 5 decoder 不支持该表格式 | 待定（需先拿到真正的表体） |

### 下一轮线索（不扩大范围）
1. A2F 数据可能在 **root 包** 有独立可解条目（须显式把目标快照声明为 root，并单列 physical_payload_binding）
2. `DataHelpers` 引用 `is_x9_replace_table` / `enable_theme_replace_table` ⇒ 存在 **x9/主题替换表** 机制，A2F 可能走替换分支
3. 亦可能 A2F 由服务端下发 / 只在特定分支表出现

### 状态
`runtime fashion_key → raw FASHION_DATA row` 仍 **unresolved**；business identity 不升级；physical payload unresolved；未生成 FASHION_RESOLVED；未碰名称链/Wiki/oversea/slot52。


---

## P4-B A2F 提取（第 4 轮）：root 快照定向（2026-09-12，只读；known A2F module payload is not a decodable table body; independent data body not located → 转 x9/theme replace）

### 1. 唯一 root snapshot
- source_id **`mrzh-root-py314-full`** / path `E:\mrzh\script.py314.lc.npk` / server_branch 简单生存服 / **entry 总数 105,777**
- decoder：项目工装链原实现（`rebuild_fashion_wardrobe_slots._read_by_fid` + `._xbody` + `parse_legacy_chs_pool` + `decode_table_rows_with_chs_slots`）
- path/FID 注册来源：`data/live_sources.json`；**root 无 tI 路径表**（`config_work/path_tables/` 只有 documents 的一张）
- **与 Documents 完全隔离**：本轮未把 root 结果对 Documents 的 19,276 row_key

### 2. root decoder 自检：**FAIL（不适用）**
用 Documents 的 fashion FID（`E1645717C83FC968`）在 root 取条目 → `expected one entry for FID …, got 0`
⇒ **FID 不可跨包复用**（同包 A2F FID 巧合相同 ≠ 通用规则）；root 侧 known-table 自检需先解析 root 自己的 FID，本轮未通过。

### 3. root A2F 实际位置（区分 stub / data / CHS）
| 资产 | 位置 | 判定 |
|---|---|---|
| module | entry **#39738** / FID `5FA629EFB3B8CB74`（declared 55,168B / decoded 65,255B） | 含 3 个 `x{` 帧（@263 len 64,540；@17032 len 53,982；@21255 len 10,003,355）——**全部非 BinDict 表体** ⇒ 是模块包，不是数据体 |
| CHS | entry **#32818** / FID `4EC2AC33F40CCBDB`（154B） | 内容仅 `string_pool` + `com\cdata\appear_id_2_fashion_id_chs.py` + `<module>` ⇒ **A2F 无文本**（纯 id 映射的旁证） |
| 其他引用 | 103 条 | UI/组件消费方 |

### 4. 是否解出：**否**（known A2F module payload is not a decodable table body; independent data body not located）。行数/unique/对照 全部未做（依赖解出）。

### 5. 转 x9 / theme replace 调查（按 USER 第 6/7 步：root 仅"已知 A2F module payload 不是可解表体"，**未**排除全包存在独立数据体）
三个线索模块（root）：
- **#9958**（6,960B）特性开关表：含 `enable_theme_replace_data` / `enable_theme_replace_table`（与大量 `enable_theme_*` 并列）
- **#34937**（DataHelpers 小模块）：`is_x9_replace_table` 与 `get_big_table_split_*`、`get_module_name` 同族
- **#41636**（11,430B，`com\utils\SpecialNancyHelpers.py`）：`com.cdata.%s` + `Helpers.is_x9_replace_table` + `_X9_OLD_SCENE_CONF_MAP` + `import_module` ⇒ **替换表加载范式**（按老配置映射换表）

### 6. 正式工程结论（写入长期口径）
**找到 cdata module stub ≠ 找到表数据体。** 表定位必须经过实际 decoder 验证（能解出行的才算数据体），不得仅凭"逻辑路径 / FID / 字符串命中"认定数据体。本轮 Documents 与 root 两次踩坑均由此而来。

### 7. 状态（未升级）
`runtime fashion_key → raw FASHION_DATA row` = **unresolved**；`business_identity` 不升级；`Documents physical binding` = unresolved；`root physical binding` = 未通过自检；未生成 FASHION_RESOLVED；未碰名称链 / Wiki / oversea / slot52。


---

## P4-B 口径修正（2026-09-12，USER 指令）

### 修正 1：root ≠ 简单生存服（source metadata）
`E:\mrzh` + `script.py314.lc.npk` 只能证明 **client_channel = test**；`root` 只是包位置/包层级。在拿到独立 selector / config / loader / runtime consumer 证据前，不得把 root 包绑定到服务器分支。本轮正式口径：
```
source_id       = mrzh-root-py314-full
client_channel  = test
package_scope   = root
server_branch   = unresolved
```
注：`data/live_sources.json` 是**被判分/审计锁定的注册表**，本轮**未修改**（改它会破坏 input lock）；修正后的口径以本日志 + `analysis/audit/root_source_metadata_v1.json` 为准。

### 修正 2：不得写"root 已排除 A2F 独立数据体"
当前 root decoder 自检**未完成**（Documents 的 fashion FID 在 root 不存在；root 自己的 known-table FID 未解析；root 无完整 tI/path→FID 注册表）。因此正式可证的只有：
- root 已知 `appear_id_2_fashion_id.py` module entry **不是** BinDict 表体
- root `_chs` entry 只是模块/string_pool，**不是**映射数据
- 当前**未定位到**独立 A2F data body

正式措辞统一为：`known A2F module payload is not a decodable table body; independent data body not located`。


---

## P4-B A2F 第 5 轮：x9 / theme replace 机制调查（2026-09-12，只读）

### 机制（root 快照，≤120KB 条目定向扫描；12 条命中）
| 模块 | 命中符号 | 角色 |
|---|---|---|
| `com\cdata\theme_switch_conf.py`（#9958） | `enable_theme_replace_table` / `enable_theme_replace_data` | theme 开关名表 |
| `com\switch.py`（#10808） | 同上 | 开关实现 |
| **`com\lang\TableImportHelper.py`（#69993）** | `enable_theme_replace_data` | **导入期 theme 替换点** |
| `com\lang\Translator.py`（#82246） | `enable_theme_replace_data` | 翻译侧 |
| `com\utils\ServerOverseaDataHelpers.py`（#35417） | `enable_theme_replace_data` | 服务/oversea 侧 |
| `com\utils\DataHelpers.py`（#78966 / #34937） | `is_x9_replace_table` + `enable_theme_replace_table` + `switch.use_theme_new_table` | **两套机制共用入口** |
| `com\schedule\ScheduleHelpers.py`（#7504） | `is_x9_replace_table` | **x9 装配实例** |
| `com\utils\SpecialNancyHelpers.py`（#41295/#41636） | `is_x9_replace_table` + `_X9_OLD_SCENE_CONF_MAP` | x9 map + `com.cdata.%s` + import_module |

**x9 replace 装配规则（实例证据）**：逻辑表存在 `<name>_x9_old_table` 变体模块（如 `com.cdata.player_new_schedules_data_x9_old_table`）；消费方 `ScheduleHelpers.get_schedule_simple_data` 内同时出现 `PLAYER_NEW_SCHEDULES_DATA | data | Helpers.is_x9_replace_table | import_data | copy | get | r_data | old_data` ⇒ 判定命中后 **import_data + copy** 把 old 变体数据合并/替换进当前表。
**theme replace 装配规则**：由开关 `enable_theme_replace_table` / `enable_theme_replace_data`（+ `switch.use_theme_new_table`）控制，替换点在 **`TableImportHelper` 导入期**，并有 `Translator` / `ServerOverseaDataHelpers` 两处配套。
⇒ **两套独立机制**（x9 = 表名变体替换；theme = 开关门控的导入期替换）。
> 未取得：`Helpers.is_x9_replace_table` 的**定义体**（定义模块 >120KB 被本轮过滤条件排除，未隔离）。

### A2F 是否命中（结论：两套都不命中）
- A2F 相关条目中 **x9/theme 关键词命中 = 0**
- 全包搜索 A2F 专属替换变体（`appear_id_2_fashion_id_x9*` / `fashion_id_x9_old` / `appear_id_2_fashion_id_theme`）= **0 命中**
⇒ 按 USER 第 4 目标，**立即停止该方向**。

### A2F 正式记录（四态）
```
standalone data body : not located
BigTableSplit        : rejected
x9 replace           : rejected
theme replace        : rejected
```
下一步可选方向（不下结论）：动态生成 / 服务端下发 / 其他 loader patch；以及"A2F 表体定位能力"缺口（root 无 tI 路径表、多帧/嵌套容器识别）。


---

## P4-B A2F 第 6 轮：root 侧 path→FID→data-body 定位能力（2026-09-12，只读；未闭环，但性质已定）

### 两个决定性实证
**① 数据表体 payload 不带逻辑路径**
- Documents 已知数据体 `fashion_data` base（entry **24340** / FID `E1645717C83FC968`，已解出 19,276 行）→ 其 payload **不含** `com\cdata\fashion_data.py` 字符串（含 `_chs` 亦否）
⇒ 「数据体自带表名」假设 **FALSE**：数据条目是**无名的**，不能靠名字定位。

**② FID 的稳定性分层**
| 类型 | 跨包行为 | 证据 |
|---|---|---|
| **模块**（有逻辑路径的文件） | **跨包一致** ✓ | `com\cdata\fashion_data.py` 模块 FID **`06EDEAAE3B08B985`** 在 Documents(#728) 与 root(#2805) 相同；`appear_id_2_fashion_id.py` 亦同（`5FA629EFB3B8CB74`） |
| **数据体** | **跨包不一致** ✗ | Documents 的 fashion 数据体 FID `E1645717C83FC968` 在 root **不存在**（`got 0`） |
⇒ 仅凭「逻辑路径 → FID」**无法**定位 root 的数据体：路径能定位的是模块，数据体无名且 FID 随包变化。

### root 定向扫描 + decoder 探针（同一 root snapshot）
| 目标路径 | 命中条目 | 探针结果 |
|---|---|---|
| `com\cdata\fashion_data.py` | **1 条**：#2805 `06EDEAAE3B08B985` 329,168B | 可解=**False**（模块包） |
| `com\cdata\fashion_data_chs.py` | 1 条：#86245 `D016140651FEAB34` 139,504B | False（模块包） |
| `com\cdata\appear_id_2_fashion_id.py` | 1 条：#39738 `5FA629EFB3B8CB74` 55,168B（3 帧） | False |
| `com\cdata\appear_id_2_fashion_id_chs.py` | 1 条：#32818 `4EC2AC33F40CCBDB` 144B（0 帧） | False |

⇒ **root known-table 自检未闭环**（无法先定位 root 的 fashion 数据体做已知行数验证）。

### module vs data body 的判据（本轮确立，可复用）
- 模块/包装：帧存在但 decoder 失败（`base reserved != 0` / `not a supported 0x76 index tail` / 无帧）
- 数据体：**至少一个帧能被 `decode_table_rows_with_chs_slots` 解出 ≥1 行**
- 探针必须逐帧枚举（offset / declared length / 可解行数），不能只看第一个帧

### 失败层定位（USER 五层）
| 层 | 结果 |
|---|---|
| path → FID | **对"数据体"不成立（数据体无名）← 卡在这里**；对"模块"成立且跨包一致 ✓ |
| FID → entry | OK ✓ |
| entry → data body | 无法定位 ✗（root 无 tI 路径表；数据体无名） |
| frame | 已由 decoder 探针覆盖 ✓ |
| decoder | 工装链已验证可用 ✓（Documents 19,276 行） |

### 下一步（唯一顺位，未执行）
用项目既有 `toolkit_core.npk_paths.build_ti_path_table` 为 **root 包**重建 `tI` 路径表（Documents 已有同类产物 `script_documents_c230d49114f0_ti_paths.json`，600,671 条），再按 root 自己的 path→FID 重试 A2F。

### 状态
未具备进入"动态生成 / 服务端下发"调查的资格（USER 第 7 条前置条件未满足）；`runtime row binding` / `business identity` 均不升级；未碰名称链 / Wiki / oversea / slot52 / BigTableSplit / x9 / theme。


---

## P4-B A2F 第 7 轮：tI path table 能否定位无名 data body（2026-09-12，只读；**结论：不能**）

### 先证明机制（避免无意义地重建 60 万条）
读 `toolkit_core/npk_paths.py` 全文：`_declared_python_paths(payload)` 只在 **payload 内部**找 `tI` + 长度前缀 + 以 `.py` 结尾的路径串；`build_ti_path_table` 对每个 entry 解包后收集这些声明，输出 `{entry_index, file_id, path, ti_marker}`。
⇒ **tI 表 = "payload 里声明过 .py 路径的条目"集合（=模块/代码包）；无名数据体没有声明 ⇒ 结构上进不了这张表。**

### 再用既有 Documents tI 表实证（`script_documents_c230d49114f0_ti_paths.json`）
| FID | 身份 | tI 记录 |
|---|---|---|
| `E1645717C83FC968` | **fashion_data 数据体（entry 24340，已解出 19,276 行）** | **0 条 — 未记录** |
| `D016140651FEAB34` | fashion_data CHS | 1 条 `com\cdata\fashion_data_chs.py` |
| `06EDEAAE3B08B985` | fashion_data 模块 | 1 条 `com\cdata\fashion_data.py` |
| `5FA629EFB3B8CB74` | A2F 模块 | 1 条 `com\cdata\appear_id_2_fashion_id.py` |
| `4EC2AC33F40CCBDB` | A2F CHS 模块 | 1 条 `com\cdata\appear_id_2_fashion_id_chs.py` |

表规模：`path_records 600,671` / 不同 file_id 87,568 / `entry_count 87,597` / schema `lifeafter-nxpk-ti-path-table-v1` / source `E:\mrzh\Documents\script.npk`。

**结论**：`tI path table 不能解决 data-body 定位`（module/CHS 能定位 ✓，无名数据体不能 ✗）。**因此本轮未重建 root tI 表**（机制已证无用；等 USER 需要时再建）。

### 性质判定（USER 第 6 条 A/B 二选一）
属于 **A：tI 根本不描述 data-body companion** ⇒
- 正式结论：`root path table 不足以解决无名数据体定位`
- **新最小缺口 = module → companion data-body 的关联机制**

### 具体线索（下一步候选，未执行）
`com\lang\TableImportHelper.py`（root #69993）窗口内出现 `data_file_id | file_id | ori_filename` 与 `com.tdata.%s.data_translator_data_file_id` ⇒ 存在**由模块名派生 data file id** 的规则（疑似 hash/命名映射，而非目录列举）。项目 config_work 里已有 `probe_idx_hash.py` / `probe_crc_hash.py` / `probe_1dpw_hash.py` 等探针可复用。
**按 USER 要求：不因此下"服务端下发"结论**；先查关联机制（hash/file-id 派生）与动态生成/loader patch。

### 状态
`runtime row binding` / `business identity` 均不升级；未生成 FASHION_RESOLVED；未改 decoder / RULES；未碰名称链 / Wiki / oversea / slot52 / BigTableSplit / x9 / theme。


---

## P4-B A2F 第 8 轮：module → data-body 关联机制（2026-09-12，只读；机制=查表，非哈希）

### 1. `data_file_id` 的定义位置
`com\lang\TableImportHelper.py`（root #69993 / FID `A8D468AB34D86D47`，9,226B）→ **`fix_replace_data`** 窗口：
```
enable_theme_replace_data | **com.tdata.%s.data_translator_data_file_id** | com.cdata.oversea.A | _%s |
update_file_version_infos | com.switch | switch | getattr | ThemeHelpers.get_theme_language | get_theme_tr_suffix |
__import__ | sys | modules | data | startswith | _import_string_pool | hasattr | bindict | set_string_pool | string_pool |
__file__ | file_name | lang | suffix | **table_name | data_file_id | file_id | ori_filename | module_name | module | succ**
```
⇒ 客户端**不是**用哈希算 data file id，而是：`table_name` → 组装 `com.tdata.<scope>.data_translator_data_file_id` → 取其映射值作为 `data_file_id`（并与 `file_id` / `ori_filename` / `update_file_version_infos` 配套）。

### 2. 判定类型：**B/C 混合（查表映射）**
- **纯哈希派生：已排除** ✓ —— 8 个名称变体 × 9 种哈希（md5/sha1/sha256/crc32 × lo8/hi8 + 2 个 FNV 种子）= **72 组，对 6 个已知 FID（3 数据体 + 3 模块）0 命中**
- 映射来源族：**`com.tdata.<scope>.data_translator_data_file_id`**（另有 `data_translator_data` / `data_control_data` / `code_translator_data`）

### 3. 规范化规则
`module_name` / `table_name` → `com.tdata.%s`；带语言/主题后缀（`get_theme_language` / `get_theme_tr_suffix`：`_chs/_cht/_eng/_jpn/_kj1…`）与 oversea 分支（`com.cdata.oversea.A…` + `_%s`）。

### 4. 多表验证结果
- `com.tdata.*` 树：root **23 条** / documents **12 条**；scope 含 `yk` / `kj1` / `en` / `jp`
- 模块 FID **跨包一致**（`com\tdata\yk\data_translator_data_file_id.py` = `280094F3F29DA038`；`com\tdata\kj1\...` = `3147BA121D83FE68`）✓ 再次印证"模块 FID 路径派生、跨包稳定"
- **但已知数据体 FID（`E1645717C83FC968` fashion / `B42760CCA41DBC25` common_item / `EF3A8474A5E5F7A4` common_item CHS）在这些模块里 0 命中**（raw 与 int64-LE 两种形式均试）
⇒ 这些 translator 模块自身也是**代码 stub**，其**映射数据**同样落在无名 data body 里 ⇒ **递归回同一问题**

### 5. 结论（USER 第 7 条）
- `data_file_id` **存在**，位置/机制已定（TableImportHelper.fix_replace_data + com.tdata.* 族），**类型=查表映射**
- 已排除候选：纯哈希派生 ✓、BigTableSplit ✓、x9 ✓、theme ✓、tI path table ✓
- **仍缺**：① `data_translator_data_file_id` 模块自身的映射数据如何载入（同样无名）② `update_file_version_infos` 对应的 **file-version registry** 来源（疑似"表名→file_id"唯一权威表，未定位其数据体）
- 按 USER 要求：**不猜服务端下发**；动态生成 / loader patch / 服务端注入仍属未排除项

### 状态
`runtime row binding` / `business identity` 均不升级；未生成 FASHION_RESOLVED；未改 decoder / RULES；未碰名称链 / Wiki / oversea / slot52。


---

## P4-B A2F 第 9 轮：file-version registry 来源（2026-09-12，只读；**递归终点：native 层**）

### 1. `update_file_version_infos` 定义位置
全包（root，≤300KB 条目）**仅 1 处引用**：`com\lang\TableImportHelper.py`（#69993 / FID `A8D468AB34D86D47`）——作为**导入符号**被 `fix_replace_data` 调用（窗口：`update_file_version_infos. | fix_replace_data | … | table_name | data_file_id | file_id | ori_filename | module_name`）。
⇒ **定义不在 Python payload 内** ⇒ 属 **native / 引擎层符号**（与 `bindict` 同类，均无 `.py` 定义体可读）。

### 2. 值流（Python 侧可见的边界）
```
com.tdata.<scope>.data_translator_data_file_id（查表映射，stub）
        ↘
fix_replace_data(… table_name, data_file_id, file_id, ori_filename, module_name …)
        ↘ 调用 native 符号
update_file_version_infos   ← 定义不可读（native），registry 由引擎维护
```

### 3. registry 类别判定
- **不是** Python module 可读的映射；但**存在实际的包元数据资产**：`E:\mrzh\Documents\res\*.idx`（building.idx 64KB / character.idx / effect.idx / scene.idx / ui.idx / scene_bw.idx / …），热更副本亦在 `03拆包产物\source_snapshots\...\raw_changed\Documents\res\*.idx`。⚠️ 这些 idx 按名是 **资源（美术）索引**，是否也承载 cdata 的 file-version/table→data_file_id 映射**未证**；且本项目已有 idx 解析资产（`analyze_idx_delta.py` 等）可复用。
- **不是**普通 Python/cdata module（全包无定义体）
- **是** **native + package metadata**（引擎从包自身的 index/metadata 读取并维护）⇒ **Python 静态层不可达**

### 4. 是否含 table→data_file_id
无法从 Python 侧读取 ⇒ **不能**据此定位无名 data body。

### 5. 多表交叉验证
不适用（registry 不可读）。

### 6. 本轮定性结论：**静态 Python 层的定位能力已穷尽**
已逐一排除：tI path table ✗、纯哈希派生（72 组）✗、`com.tdata.*` 查表（其映射数据本身无名）✗、BigTableSplit ✗、x9 ✗、theme ✗。
剩下的唯一通道是 **native/引擎层**（`update_file_version_infos` / `bindict` / package index）⇒ **"逻辑表 → 无名 data body"的通用定位能力在纯静态 Python 层无法建立**。

### 7. 后续可选方向（按 USER 要求，不猜服务端）
① 运行时/动态（进程内 hook、内存或日志读取）② 其他 loader patch ③ 服务端注入/下发。
**在 ① ② 排除前不下"服务端下发"结论。**

### 8. 状态
`runtime row binding` / `business identity` 均不升级；未生成 FASHION_RESOLVED；未改 decoder / RULES；未碰名称链 / Wiki / oversea / slot52 / tI / BigTableSplit / x9 / theme。


---

## P4-B A2F 第 10 轮：`Documents\res\*.idx` 是否参与 cdata / data_file_id 映射（2026-09-12，只读；**判定：不参与，IDX 方向收口**）

### 复用资产（未新写解码器）
- 项目既有：`01拆包器本体\工具库\03_WPK_1DPW\wpk_1dpw_decryptor.py`（`parse_idx` / `decrypt_payload`）
- 项目既有语义（`analyze_idx_delta.py` 文档串）：
  > "The 16-byte IDX key is treated only as the final decoded entity MD5, not a name."
  > "IDX 16-byte hash is final decoded entity MD5. Offset/pkg changes of a common hash are placement changes, not new content."

### 样本实测（3 个：building / character / scene）
| 文件 | 大小 | magic | 锚点命中 |
|---|---|---|---|
| `Documents\res\building.idx` | 65,448B | `SKPW` | **0** |
| `Documents\res\character.idx` | 177,912B | `SKPW` | **0** |
| `Documents\res\scene.idx` | 16,884B | `SKPW` | **0** |

锚点搜索（raw bytes）：`fashion_data` / `appear_id_2_fashion_id` / `common_item_data` 字符串 → **全无**；已知数据体 FID（`E1645717C83FC968` / `B42760CCA41DBC25` / `EF3A8474A5E5F7A4`）以 8 字节 LE 形式 → **全无**。

### 判定（USER 第 3 条）
结构 = `资源实体 MD5 → 位置(pkg/offset/header_size/payload_size)`，**无 name 字段、无 table_name、无 data_file_id**；锚点零命中 ⇒
**`Documents\res\*.idx` = 美术/资源索引，与 cdata `data_file_id` 定位无证据关联** ⇒ **立即停止 IDX 方向**。

### 静态客户端侧状态正式整理（收口）
| 路线 | 结论 |
|---|---|
| tI path table | 只记录 payload 内声明的 `.py` 路径；**不描述无名 data body** |
| 纯哈希派生 | **rejected**（72 组，6 个已知 FID 0 命中） |
| BigTableSplit | **rejected**（注册表 7 张，不含 A2F） |
| x9 replace | **rejected**（无关键词/无变体） |
| theme replace | **rejected**（同上） |
| `com.tdata.*` 查表 | **递归**（其映射数据本身是无名 data body） |
| file-version registry | **native**（`update_file_version_infos` 无 Python 定义体） |
| `Documents\res\*.idx` | **rejected**（本轮无证据） |

⇒ **静态 Python 层定位能力穷尽，"逻辑表 → 无名 data body" 无法在静态层建立。**

### 下一阶段（按 USER 第 5 条，未执行）
1. runtime instrumentation / hook
2. loader/native 调用观察
3. 内存中读取 `data_translator_data_file_id`
4. 最后才讨论是否存在服务端注入


---

## P4-B Runtime Observation v0.1（2026-09-12，**只读**；未取得 runtime 值，边界已定位）

### 0. 安全/合规边界（先声明）
往**在线游戏进程**注入 / 附加调试器 = 触碰反作弊面，且存在**封号风险**，同时违反本轮"不绕过任何保护机制"。⇒ **未对游戏进程做任何注入/附加/内存读写**；只做**磁盘只读巡检**（客户端自己写出的运行产物）。

### 1. 进程状态（只读）
`tasklist`：仅 `mrzh_launcher.exe` 在跑，`mingrizhihou.exe` **未运行**（未启动游戏）。

### 2. 运行时产物巡检（`E:\mrzh\Documents` 等）
| 产物 | 内容 | 判定 |
|---|---|---|
| `bindict_mmap_enabled` | `0` | **cdata bindict 不走 mmap** ⇒ 表数据在进程内存，**磁盘无副本** |
| `cfs_version` / `cfs_version_inited` | `1` / `1` | CFS 层标记 |
| `cfs_prewarm_pos` | `12208` | 预取位置 |
| `configs/*` | 大量 per-account/UI 配置（`chatconfig_<rand>` 等） | 非表注册表 ✗ |
| `db/` | 仅 `shader_compile.db` | 无关 ✗ |
| `client_doc@1_11030xxx` | **空目录**（0 字节） | 无关 ✗ |
| `LocalLow/*/Player.log` | 无 LifeAfter 相关（只有其他游戏） | 无引擎日志 ✗ |

⇒ **磁盘上没有 `table_name → data_file_id` 的任何运行时副本**。

### 3. 结论
- `fix_replace_data` 运行时调用：**未观察**（未运行、未注入）✗
- runtime `data_file_id` / tdata scope：**未取得** ✗
- A2F：未定位 entry、未解出 ✗
- `runtime row binding` / `business identity`：**不升级** ✓

### 4. Python 层失败的具体边界（USER 第 6 条）
必须在**进程内**才能观察的点：
1. `com.tdata.<scope>.data_translator_data_file_id` 的 `.data` 由 **native `bindict`** 填充，且 `bindict_mmap_enabled=0` ⇒ 数据只在**进程内存**，Python 侧无中间产物
2. `update_file_version_infos` **无 Python 定义体**（native）
⇒ **边界 = Python ↔ native 之间**；Python 侧可读窗口内不存在该映射。

### 5. 后续可选（需 USER 决策，均不违反本轮原则）
- (a) 静态但**新角度**：A2F 那 3 个帧可能**根本不是 Python BinDict 容器**（我们只用 Python 表解码器探过）⇒ 可研究 **native 表容器格式**（不是重开已排除项）
- (b) 若存在**可自由调试的客户端副本/体验服且已获准**，再做进程内观察
- (c) 客户端自带的**调试/日志开关**（若有）
- **不做**：对在线游戏进程注入/附加 ✓（封号与合规风险）


---

## P4-B A2F 第 11 轮：module payload 格式分类（2026-09-12，只读；**"内嵌 native data body" 假设 rejected**）

### 口径修正（USER）
`x{` 命中 ≠ 已证明的 frame boundary；此前 @263 / @17136 / @21367 只能称 **`x{ marker candidates`**，不得称"3 个帧"。

### 三类 module payload 结构对照（root 快照，命令式只读）
| 项目 | A2F module `5FA629EFB3B8CB74` | fashion_data module `06EDEAAE3B08B985` | tdata stub `280094F3F29DA038` |
|---|---|---|---|
| decoded | **65,255B** | **827,003B** | 49,226B |
| 前 16B | `73 00000000 00000000 00000000 00050000` | **同** | `73 …00180000` |
| `x{` 命中 | 3 处：@263 len=64,540 **in-bounds** ✓；@17,032 len=49,003 **越界** ✗；@21,255 len=15,541,148 **越界** ✗ | 1 处：@263 len=826,296 **in-bounds** ✓ | **0 处** |
| `<module>` | 1 次 | 1 次 | 1 次 |
| 限定名条目数 | **1**（`com.lang.TableImportHelper`） | **1** | 80（列 oversea 表模块的翻译注册代码） |
| `bindict` / `TableImportHelper` / `fix_translate_data` | 均在**尾部**（@64,873 / @64,946 / @64,995；距末尾 ~382B） | 同（@826,629 / @826,702 / @826,751） | 无 |

⇒ **A2F module 与普通 cdata loader stub 结构完全一致**（同头部、同"@263 单一容器帧"、同尾部 loader 代码、同 `<module>`）⇒ **没有特殊 native container**。

### 10MB 假长度的成因（已解释）
`x{` 是 **2 字节** 标记；在 ~65KB payload 内期望偶遇 1–2 次。只有真正的容器帧其"后 4B"才是长度：
- @263：后续 4B = `1c fc 00 00` → 64,540 ✓ 且 in-bounds ⇒ **真帧**
- @17,032：后续 4B = `6b bf 00 00` → 49,003 ⇒ 17,032+6+49,003 = 66,041 **> 65,255 越界** ⇒ **偶遇**（落在序列化数据里，非长度字段）
- @21,255：后续 4B = `9c 23 ed 00` → 15,541,148 ⇒ 明显越界 ⇒ **偶遇**（Documents 同位置读到 10,075,803，同样偶遇）
⇒ 之前的"3 帧"判断 **确认错误**，已按 USER 口径改称 `marker candidates`。

### Payload coverage（cmd 口径）
`263B 头部 + 64,540B 容器帧 + ~446B 尾部 loader stub ≈ 65,255B` ⇒ **≈100% 可被"标准 module 容器 + loader stub"解释** ⇒
**`module contains hidden native data body` = REJECTED** ✓

### 结论（USER 第 8 条）
**静态 module 内嵌路线正式关闭** ✓。A2F 是普通 Python module/loader stub；它的 data body 若存在，只能是**另一个无名条目**，其 FID 由 native `update_file_version_infos` 决定（上一轮已证 Python 层不可达）。

### 下一最小缺口（USER 第 9 条）
在**不注入进程**的前提下取得"客户端启动时到底读了哪个文件作为 A2F 数据"：
- 候选方案：**系统级只读文件访问日志**（如 Sysinternals ProcMon 的文件 I/O 记录），观察 `mingrizhihou.exe` 启动时对 `Documents/*.npk` 的读取序列，定位被读作 A2F 数据的 entry/offset
- 该方案不注入、不改游戏、不碰反作弊 ✓（仅记录 OS 层的文件访问事件）；实施前需 USER 同意安装/运行该监控工具
- 仍不采用：进程内 hook / 内存读写 / 网络分析

### 状态
`runtime row binding` / `business identity` 均不升级；未生成 FASHION_RESOLVED；未改 decoder / RULES；未碰名称链 / Wiki / tI / 哈希 / x9 / theme / IDX。


---

# P4-B Fashion Identity 收口（2026-09-12，连续执行 A→J，只读；**硬阻断收口**）

## 阶段 A：A2F module payload 再审视 → **内嵌 native data body = REJECTED**
- A2F module 与普通 cdata loader stub **结构完全一致**（同头部 `73 00…`、同"@263 单一容器帧"、同尾部 `bindict`/`TableImportHelper.fix_translate_data`、同 `<module>`）⇒ 无特殊 native container
- `x{` 仅为 **2 字节 marker**；@263 的后续 4B=64,540（in-bounds ✓ 真帧）；@17,032（49,003）与 @21,255（15,541,148）**均越界** ⇒ 偶遇，非 frame；"3 帧"判断确认错误
- Payload coverage ≈100%（263B 头 + 64,540B 帧 + ~446B 尾部 stub）
- **A2: 格式对照**（fashion_data module / fashion_data 数据体 / common_item / tdata stub）⇒ 数据体与模块共用同一容器布局，差异只在内容
- **A 结论**：A2F 无内嵌数据体；数据若存在必为**另一个无名条目**

## 阶段 C：companion 规则 & 结构扫描 → **未发现规则**
- npk 条目 48B 记录：`file_id / offset / packed / declared / c1 / c2 / flag / 尾部16B`
  - `c1 == c2`（如 `0xd23a0f90`）⇒ 校验值；**尾部 16B 全零** ⇒ 无 companion 指针/无 name hash
- 已知对（module `06EDEAAE3B8B985` ↔ 数据体 `E1645717C83FC968`）之间**无 entry 邻接关系**（#728 vs #24340）
- **结构扫描（Documents，3KB–400KB）**：4,199 条 → 211 张可解表；**没有任何一张的值以 fashion row_key 为主**（最高比例仅 15.7%）⇒ Documents 内**不存在可解的 A2F 表体**
- fashion 行字段名不可信，且**未找到可用 appear 字段** ⇒ "A2F 由 fashion 行派生"假设**不成立**
- tI 放宽过滤（收非 `.py` 声明）重扫已知条目 ⇒ **0 条声明**（项目 tI 表来自另一包/另一套 unpacker）⇒ 该方向无线索

## 阶段 B：native bindict 静态接口 → **静态不可达**
- 扫 `E:\mrzh\bin\**\*.dll|exe`（825 个原生模块）搜 `bindict / data_translator_data_file_id / data_file_id / 1DPW / com.cdata.%s / file_version_info`
- 命中**全为误报**（`fontdata`/`updateclientdata`/Chromium `file_version_info_win.cc`）⇒ **客户端原生引擎不在可访问 bin 树**（CEF/Qt/SDK 而已；主 exe 疑 UPX 打包，项目里亦只有 `disasm_upx_stub.py`）
- ⇒ `bindict` / `update_file_version_infos` 的包读取契约**无法在允许范围内静态取得**

## 阶段 D：客户端自带 debug/log 开关 → **未发现**
- `Documents/client.ini`（仅 Ext/UseFix/DefaultPreload）、`vendor.ini`、`launcher_conf`（二进制）、`cloud.json`（下载器配置，含 `enable_namehash_check: true`）
- `configs/*` 全为账号/UI 配置；grep `debug|verbose|log_level|trace` **0 命中** ⇒ **无表加载日志开关**
- 新发现但未追（residual 候选）：`fo_version` / `patch_ab_test_version` / `s_patch2` / `patchlock`

## 阶段 E–H：因 A2F 未取得
| 项 | 状态 |
|---|---|
| `appear_id → runtime_fashion_key` 映射数据 | **未取得**（表体不可定位） |
| A2F value ↔ FASHION row_key 统计 | 未做（无数据） |
| runtime row binding | **unresolved**（不升级） |
| business identity（owned/wear/preview） | **consumer 语义一致已证**（同一 `fashion_id` 流经 has/wear/preview ✓），但**其 raw-row 绑定未证** ⇒ **unresolved**（不升级） |
| name binding | unresolved（阶段 H 前置未满足，未做） |

## 阶段 I：产物
**未生成** `FASHION_RESOLVED_v0.1`（硬门未满足：runtime row binding 未 verified）✓

## 阶段 J：正式收口（USER 授权口径）
```
P4-B runtime key semantic  = verified        （appear_id → A2F.data.get → runtime_fashion_key → FASHION_DATA.data.get 的消费者语义链已证）
P4-B raw-row physical binding = unresolved    （无名 data body 静态不可定位；native 层不可达）
```
**建议**：v0.1 允许 fashion business identity **保持 unresolved**，不再阻塞项目（RULES 显式标注 unresolved 与三层 namespace 隔离）。

### 最终 residual 清单
1. `无名 data body 定位`：需要 native/运行时观察（禁止注入 ⇒ 当前不可得）
2. `com.tdata.* 映射数据`：同上（递归）
3. `physical_payload_binding`（Documents/root 谁进 runtime）：unresolved
4. `export slot52 ≠ runtime key ≠ row_key`：三 namespace 隔离（已冻结）
5. `sale / shop / acquisition`：absent
6. `name / show_name`：未评估（前置未满足）
7. 候选元数据未追：`fo_version` / `patch_ab_test_version` / `s_patch2` / `patchlock`


---

# P4-A2 Item Identity Backfill（2026-09-12，连续执行 A→J，非破坏性新增产物）

## 阶段 A：候选分组（27753 → 7 个 schema family）
全部候选来自 **同一张表**：`com\cdata\common_item_data_base.py`（FID `B42760CCA41DBC25` / entry 18005 / snapshot `ba8a239a…55ad`），id slot = 1：

| schema | 候选 | row_key==id | 名称链(slot4) | 运行时 dispatch 归属 | 结论档位 |
|---|---|---|---|---|---|
| 92 | 992 | 100% | verified | common_item | verified |
| 328 | 19146 | 100% | verified | common_item | verified |
| 689 | 1350 | 100% | verified | common_item | verified |
| 893 | 1610 | 100% | verified | common_item | verified |
| 49912 | 1866 | 100% | verified | common_item | verified 1812 / unresolved 54（chip 遮蔽） |
| 118640 | 634 | 100% | verified | common_item | verified 630 / unresolved 4（nucleus 遮蔽） |
| 245151 | 2155 | 100% | verified | common_item | verified |

## 阶段 B/C：找到 runtime consumer（**本轮关键突破**）
旧 P4-A2 审计卡点是"缺独立正锚"（anchor-only 政策下 0/7 通过），日志明确拒绝 common_item 派生作为循环证据 ✓。本轮改用 **runtime consumer** 证据（独立于表内容）：

```
item_id → Helpers.get_item_data(item_id)  (BagCompBase)
        → DataHelpers.get_item_data        (entry #20487)
        → get_item_type(item_id) → com.cdata.common_item_data
        → COMMON_ITEM_DATA.data.get(item_id) → item_info
        → 业务：bag/count/stack（max_stack_count / capacity）、get_item_num、
                is_blood_moon_inner/outer_item(self.item_id)
```
- consumer 模块：`com\components\avatar\BagCompBase.py`（FID `0D86C2AE10376C4E` / entry 1410 / 153,013B）
  - `BagItems.get_avail_space` / `get_avail_space_for_common_item`：`Helpers.get_item_data(item_id) → item_data → max_stack_count/capacity`
  - `BagCompBase.get_item_num(item_id)`；`is_blood_moon_*_item`：`COMMON_ITEM_DATA.data.get(self.item_id)`
- dispatch 体（#20487）确认候选模块表含 `com.cdata.common_item_data` ✓
- 交叉一致：旧审计的 9 个弱锚（如 150005 新币）在新口径下自然升级且名称一致 ✓

## 阶段 E：负控（保留并生效）
- **只因为 row_key==id / integer collision / 表名像 item / 有 name/icon** → 仍禁止 ✓
- **dispatch namespace 遮蔽**：id 同时存在于其它 dispatch 表 ⇒ 不可判归属 ⇒ **不升级**
  - belt_chip 54 个（schema 49912）+ nucleus 4 个（schema 118640）= **58 个 unresolved** ✓
  - all_equips 196 个 id 与候选交集 = 0 ✓
- **unsafe name slot**：slot 6（desc）全部 `chain_state=unsafe` / `entity_name_allowed=False` ⇒ 不充当 name ✓

## 阶段 G/H：name 绑定与合并
- name 源：同记录 `NAME_CHAIN_CANDIDATES` slot 4 / `name` / `primary` / `chain_state=verified` / `entity_name_allowed=True` ⇒ **27,695 / 27,695 全部 verified** ✓
- 产物：`data/ITEM_MASTER_v02.jsonl` = **1,189 + 27,695 = 28,884** 行（唯一 id 28,884 / size 58.5MB / sha `36042639…74a4c8`）
- 零冲突（collisions_with_base = 0）；v0.1 行**原样保留**（provenance/hide_in_bag 三态结构不变）✓
- 旧 artifact `business_id_allowed=false` **不追改**（v0.2 以新证据类型升级，RULES 显式记录）✓
- RULES：`data/ITEM_MASTER_v02_RULES.json`；审计：`analysis/audit/item_master_v02_audit.json`（含 58 条排除明细）✓
- 构建器：`tools/rebuild_item_master_v02.py`（可重跑）；测试：`tests/test_item_master_v02.py` ✓

## 阶段 I：P4-D reward 只读覆盖（不建 join）
- `lottery_pool_resolved_v01` 2,3567 条 record 的 `static_reward_raw[0]`
  - v0.1（1,189）命中 **0** → v0.2（28,884）命中 **10,683 / 23,567 = 45.33%** ✓
  - 未命中 12,884 条 / 唯一 2,164 个 id（落在 ITEM_MASTER 之外的 namespace，如 10829/20052/35112）✓
  - `item_master_id` 仍为 null，**未建立 reward→item 正式 join** ✓

## 残留
1. 58 个 dispatch 遮蔽 id：需 namespace 优先级证据（opcode 级）才能定档 ✓
2. dispatch 顺序 / numeric constant 不可读 ⇒ 残差保留 ✓
3. 未命中 reward id 的归属表未定（属其它 identity 族，本轮不追）✓


---

# P4-A3 Item Namespace Expansion（2026-09-12，A→G 连续执行，产物非破坏性新增）

## 阶段 A：runtime item dispatch 共 **17 个 namespace**（来自 `DataHelpers.get_item_data` / `get_item_type` 实体，非表名猜）
common_item_data / bullets_data / edible_item_data / recipe / gift_data / fashion_data / advanced_recipe_material_data / advanced_recipe_data / player_module_appear_data / chat_bubble_data / spray_paint_data / all_equips_data / belt_chip_data / reward_pool_data / plants_seed_data / trade_items / space_data（+ race_ctrl_data）
另一组 entity namespace（player/building/resource/loot/monster/common_entity/blast/npc/box）非 item，不混入。

## 阶段 B：2,164 个 reward 未命中 id 分类
| 分类 | 数量 | 依据 |
|---|---|---|
| common_item | 562 | common_item_data_base 全量表（解出 36,038 行）row key 命中 |
| gift_data | 748 | gift_data 表行（gift_data_base entry 21287 / FID C5998AD60B305608）+ dispatch namespace |
| fashion | 47 | 时装行集 |
| reward pool_key（**非 item**） | 37 | 同池 pool_key |
| **unresolved** | 770 | 无 namespace 归属证据（5/6 位为主） |

## 阶段 C：58 条 shadow 收口（含 v0.2 自我纠错）
- **54 chip** → `belt_chip` namespace ✓：consumer 证据 = `ArtifactHelpers.get_match_conf_raw_data: BELT_CHIP_DATA.data.get(chip_id) → Helpers.get_item_name`；`DroneHelpers`（`_FUNC_TYPE_CHIP_ITEM_ID_CACHE` / `get_chip_item_id_by_func_type`）；`GmCmd_lcw.show_drone_slot`（chip_slots/alpha_chip_item_id）✓
  - 残差：belt_chip_data 原始 row key 集未直接解出；common_item ∩ belt_chip 双列 id 的 dispatch 优先级 = opcode-level unresolved
- **4 nucleus（660038-660041）→ 回填 common_item** ✓ —— **v0.2 的排除依据（nucleus 板）实为 common_item 660000 段派生板，属误排除，本轮纠正** ✓

## 阶段 E：ITEM_MASTER v0.3（统一业务物品索引）
- 行数 **30,252**（common_item 29,450 = 28,884+566 / belt_chip 54 / gift_data 748）
- `(item_namespace, item_id)` 唯一 = 30,252 ✓；**全局 id 唯一性已审计、未预设**：仅 1 个双列 id（330033 = common_item ∩ belt_chip，名同"以静制动"）✓
- 字段：item_id / item_namespace / runtime_module / raw_table / raw_row_key / row_key_equals_id / business_identity / identity_state / identity_evidence / name / name_status / provenance / snapshot / residuals ✓
- name_status 全 verified ✓（新增 common_item 行 name 槽全为 4 ✓）
- sha256 `cbf54c0820071c0e6c7af81fc52ce281f0b73d216b7380c1e66af7ca689796e9`；RULES `data/ITEM_MASTER_v03_RULES.json`；audit `analysis/audit/item_master_v03_audit.json`；构建器 `tools/rebuild_item_master_v03.py`；测试 `tests/test_item_master_v03.py`（7 项 OK）

## 阶段 F：P4-D 只读覆盖（v0.3）
- 记录 23,567 / 唯一 reward 整数 4,383
- **v0.2 命中 10,683（45.33%）→ v0.3 命中 19,365（82.17%）** ✓
- 未命中 4,202 条 / 854 唯一 id = 37（非 item pooling）+ 47（fashion）+ 770（unresolved）✓
- `item_master_id` 仍为 null，**未建立 reward→item 正式 join** ✓

## 阶段 G：停止条件达成
2,164 + 58 全部定档，无"待看"；剩余 unresolved 770（namespace 未证）+ 非 item 37 已显式归档 ✓


---

# FINAL IDENTITY PASS（2026-09-12）P4-A3 residual cleanup + P4-D reward→target

## 0. 口径审计：raw presence vs runtime business namespace
- 建立 `table_index_entries.jsonl`（76,143 条，entry↔table_name↔role↔`table_body`）作为表定位基础设施；据此拿到各 namespace 的候选 entry（all_equips 1510 / reward_pool 21380 / bullets 24763 / edible 15523 / recipe 20952 / fashion 670 / player_module_appear 3546 / trade_items 22239 / space_data 16940 / common_item 18005）
- **多数 namespace 数据体无法通用解码**（非 `x{` 帧 / index tail 不支持 / CHS 池缺失）⇒ 其 row key 集本轮**未取得**，这是 770 保持 unresolved 的直接原因
- 54 chip 复核：**raw_presence.common_item_data_base = true（54/54）** 且 runtime dispatch destination = **belt_chip**（消费者链：`ArtifactHelpers.get_match_conf_raw_data: BELT_CHIP_DATA.data.get(chip_id) → Helpers.get_item_name`；`DroneHelpers` chip_item_id 缓存；`GmCmd_lcw.show_drone_slot` chip_slots）⇒ **业务 namespace 归 belt_chip，不因 common_item 有 catalog 行而回改** ✓
- **330033 解释**：它是 54 个 chip 中唯一同时落入"reward 未命中 → common_item 分类"的 id，因此被两条 add 路径各写一次 ⇒ 属**实现重复**而非业务双身份 ⇒ **修正为 belt_chip 单条** ✓（v0.3.1：global_id_duplicates = 0）
- `raw_presence` 字段正式加入模型（记录同名整数在其它 raw/catalog 表的出现，禁止据此改写 namespace）✓

## 1. 770 定档
- 表族划分：common_item 562 / gift_data 748 / fashion 47 / reward pool_key（**非 item**）37 已在前轮升级或归类
- 剩余 **770 全部 = `unresolved_no_namespace_evidence`** ✓（侧车 `analysis/audit/p4a3_residual770.json` 逐 id 记录原因：不在任何已解 namespace 的 row key 集内 + 无 runtime membership 证据）—— **明确原因，不是"以后再看"** ✓

## 2-4. 产物
- `data/ITEM_MASTER_v03_1.jsonl` **30,251 行**（common_item 29,449 / belt_chip 54 / gift_data 748），sha `da46ff37…3ac48d7`；RULES + audit + 5 项测试 OK；旧 v0.1/v02/v03 未覆盖 ✓

## 5-12. P4-D reward→target（分层完成）
- runtime 判据证据：`com\components\avatar\RewardPoolComp.py`（entry 17084 / FID `9E87D78784DC59B6`）
  - `get_reward` / `get_reward_by_random`：`reward | replace_child_reward_by_random | reward_dct` ⇒ **child pool 递归**
  - `try_init_pool_weight`：`G_POOL_NO_ITEM_NO_TUPLE | REWARD_POOL_DATA.data.get | init_weight | isinstance(tuple|int)` ⇒ **tuple(pool_no,item_no) = 子池 / 标量 = item**
  - `init_probability_level_lottery_cnt` / `is_expire` / `get_lottery_cnt_by_probability_level`
- replacement/overlay 证据：`com\huodong\controller\OptionalVersionMgrController.py`（entry 2430 / FID `173C6E66B9DBBD59`）：`on_replace_child_reward` / `child_pool_id_2_item_no` / `on_pool_data_inited` + `optional_pool_replace_data` / `optional_version_data` ⇒ **static ≠ runtime final** ✓
- 新产物 `data/LOTTERY_REWARD_TARGETS_v0.1.jsonl`（23,567 条，sha `f2426d96…2a4f2a`）：item **19,365** / unresolved **4,092** / item_fashion_candidate **67** / child_pool **43**；item namespace 分布 common_item 17,406 / gift_data 1,958 / fashion(P4-B 边界) 67 / belt_chip 1
- **不写 `item_master_id`、不建正式 join、不声称 runtime_final=verified**（全部 = `unresolved_replacement_overlay`）✓
- 分层：池结构（LOTTERY_POOL_RESOLVED_v0.1 不动）+ target resolution（新层）✓
- 47 fashion 未硬并 ITEM_MASTER，P4-B 证据边界保持 ✓

## 最终状态
- P4-A CLOSED ｜ P4-B 语义 verified / 物理绑定 unresolved ｜ P4-C CLOSED ｜ P4-D **分层 CLOSED**（pool structure + static target 分类已交付；runtime final 保留 unresolved）
- 测试：全量 **345 项 OK（expected failures=1）** ✓
- 本阶段零注入、零反作弊操作、零旧产物修改 ✓


## 2026-09-21 13:2x · 武器皮肤图鉴刷新到 09-21 热更快照（commit 85e3fff）

**背景**：客户端 12:02 热更（Documents/script.py314.lc.npk 188,306,920→190,243,900 B），
0058.gpk 也写了 1.66 GB。按「热更后连锁反应」流程刷新图鉴。

**做了什么**：
1. 源锁更新：`data/live_sources.json` 的 `documents-py314-current` → sha `d9acae75…`、
   190,243,900 B、mtime 1789963360533020400；`audit_live_sources --include-disabled` 复核 verified。
   （只改这一条源；经典服与 legacy 锁未动。`data/source_registry.json` 无此源、未参与。）
2. 重建：`tools/rebuild_weapon_skin_catalog_current.py` → 115/113 主/18 变体/2 预览/sfx 352。
3. 盖章：`tools/provenance_standard.py --apply` —— 注意该工具跑**全 published 板**时会因别的板
   缺 `provenance.source_id` 报 `cannot identify a board primary source` 而中断；
   本次用「临时 boards 目录只放目标板」的办法只盖图鉴板（未动其它板）。
4. 构建：`tools/build_wiki.py` EXIT=0。

**事实变化（图鉴可见）**：
- 1110184 星火永传 / 1110190 佳期如梦：预告 → **已上架**（上架时间 2026-09-16）。
- 5 个时限变体补到官方正式名（`common_item_data_base` 新快照有行）：name_status candidate→verified，
  名称核验 126→131、待确认 0；例 11100041 萌豚霰击（14天）、11100061 傲隼睨视（14天）、
  11101831 战神烈火剑（7天）。
- 1110185/1110186 仍为「仅行为资源」→ 图鉴显示「未命名皮肤 · ID」（按规则，不补名）。

**代码/测试改动**：
- `tools/bindict_provenance.py`：未知形态尾部容器不再 `KeyError: 'container'` 中断——
  安全访问 + 原样保留进新字段 `untyped_containers` 供审计（**没有这个修，当前新包解不开**）。
- `tests/test_rebuild_weapon_skin_catalog_current.py`：`CURRENT_SHA` 由写死改为**从
  `data/live_sources.json` 动态读**（skill 铁律：写死会在热更后成为假红）；`EXPECTED_STATS`
  与名称断言按新快照事实同步，并在断言处写明「为什么变」。

**坑（本轮踩到并已修正）**：
- 给板补 `source_id` 时用了 `json.dump(indent=1)` → 把 7 个无关板（含 200 万行的
  fashion/lottery）整体重排，差点造成 780 万行 diff；已全部 `git checkout` 回退，
  只保留图鉴板 + 源锁 + CSV 的真实改动。**下次改板内单字段一律用文本级 replace。**
- 全量 `discover` 在 HTTP 测试处挂起：测试自起的 `wiki_server.py` 想绑 **8765**，
  与常驻保活服务端口冲突（环境问题，非本改动）。已收掉挂起测试进程，服务未动。

**验收**：图鉴专项 2 项 OK / 发布门禁 11 项 OK / 前端 7 项 OK；
无头 Chrome 实渲染：「星火永传 紫皮 冷兵器 已上架 已核验」「佳期如梦 紫皮 霰弹枪 已上架 已核验」。

### 同日追加 · 解码器根因追查（commit c88caa0）

上一条提交里的 `bindict_provenance.py` 修复只做到「不崩 + 留证」，根因当轮未挖。本轮补上：

**根因**：tail 解码的「top-level `0x1N`/`0x2N` 浮点数组」分支 append 的是
`{"type": …, "values": …}` —— **漏了 `container` 键**；下游按 `container` 分派时 `KeyError`，
整表解码中断（`_decode_0x96` 的无 schema 回退分支同病，一并修）。

**实测（09-21 快照 · common_item_data 38231 行）**：
```
修前: {'type,values': 6 ✗缺键} + 386 opaque ✓ + 67 0x86 ✓ + 38 标量 ✓
修后: {'container,type,values': 6 ✓} + 其余不变 ⇒ 不再有任何缺键容器
```
`weapon_skin_data`（131 行）只有 1 个 `opaque`（`unsupported tail marker 0x00`）——那是**真未解**，
按纪律原样留证，不硬解。

**产物影响**：图鉴板 **零变化**（本次重建后与上一条提交仅差 `generated` 时间戳）——
说明此修复只影响解码器内部标注，不动业务数据。

**新增**：`tools/probe_untyped_containers.py`（热更后一键看容器形态分布）+
证据 `data/audit/untyped_containers_probe_20260921.json`。
