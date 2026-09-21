================================================================================
                    明日之后资源拆包工具包 使用说明（v5.0）
================================================================================

【目录结构】
  工具库/               全部功能模块（01_核心解包器~10_应用核心 + _archive + GUI样式表）
  文档索引/             资源包索引 + 资源更新时间表（拆包成果必须写入此处）
  3D预览器/             3D模型预览器（HTML+Three.js，支持OBJ/glTF/FBX）
  run_all.py            统一入口（索引 / 查询 / 提取 / 自检 + 旧兼容命令）
  明日之后拆包器.exe     可视化拆包器（双击运行）
  output/               所有运行产物（含 physical_bridge_v002 物理桥审计）
  readme.txt            本文件

【工具库/ 内结构】
  01_核心解包器/        全格式解包器 + NPK解包器 + 资源定位器 + GUI源码 + 公共库（5个脚本）
  02_FPK工具/           FPK 64包概览 + 单包全量帧扫描（1个脚本）
  03_WPK_1DPW/          1DPW解密器 + 全链验证器（2个脚本）
  05_BinDict解码器/     武器attrs/转印消耗/attribute_data等（8个脚本 + bindict_lib/9个核心依赖）
  06_文件名还原/        三合一脚本（dict/bindict/verify）
  07_纹理转换/          KTX转PNG（ASTC 8x8）（1个脚本 + astcenc-avx2.exe）
  08_GUI界面/           可视化拆包器exe + 样式表（2个文件）
  09_THFB工具/          THFB 三合一脚本（extract/merge/verify-weapon）
  _archive/             归档的旧脚本（10个）
  output/                输出目录（运行时自动创建）
  run_all.py            统一入口（index / find / extract / verify + 旧兼容命令）
  使用说明.txt           本文件

【v5.0：统一文件索引（当前建议入口）】
  python run_all.py index build
      只读 E:\mrzh 的 GPK/FPK/NPK，生成 03拆包产物\indexes\lifeafter_files.sqlite3。
      构建使用临时库，完整自检后才原子替换正式库。

  python run_all.py index status
      检查 SQLite 完整性、313 个源容器清单以及 fpk_fid_index.json 是否变化。

  python run_all.py find "common\env_map\qiangpi.cube"
      返回全部物理候选，不再静默取第一个。

  python run_all.py extract "逻辑路径" "输出文件" --container "res.npk" --row 14213
      按明确候选定点提取；多命中未指定候选时 fail-closed。

  python run_all.py verify
      用三条已知 cube 路径做路径键→索引行端到端自检。

  2026-09-21 实盘结果：8160775 行（GPK 4579792 / FPK 2012297 / NPK 1568686），
  313 个容器、0 解析失败、SQLite quick_check=ok。

  注意：旧 resource_resolver.py 的 GPK c1/c2 桥接已作废。GPK 32B 条目必须读满
  8×u32，u6/u7 为直接路径 fid；多块 GPK 还必须使用逐块载荷偏移。
  当前图形 EXE 已内置 v5「文件索引」页，可查询全部候选并提取选中行；
  索引构建与批量自动化仍以 run_all.py 为权威入口。

【工具包内容】
  明日之后拆包器.exe        可视化拆包器（PySide6 界面，双击运行，在08_GUI界面/）
  run_all.py                统一入口（overview / restore / bindict-check）

  ※ 权威声明（2026-08-29 起）：本目录为唯一维护源。
    历史成果目录（E:\mrzh_audit\run_002 / run_003 / run_004）仅作只读归档，
    若本包与归档脚本存在同名/同功能版本，以本包为准；修改请只改本包。
  lifeafter_unpacker_full.py  全格式解包器（gpk/fpk/npk/nxs/wpk 等，在01_核心解包器/）
  resource_locator.py       资源定位器（武器皮肤/人物时装四层搜索，在01_核心解包器/）
  main_qt.py                拆包器 UI 源代码（PySide6，在01_核心解包器/）
  shadcn.qss                UI 样式表（shadcn 风格，在08_GUI界面/）
  astcenc-avx2.exe          ASTC 纹理解码工具（ktx_to_png.py 依赖）
  npk_reader.py             NPK 公共读取库（AES解密+条目解析+path_id计算，在01_核心解包器/）

  === 核心解包脚本 ===
  lifeafter_unpacker_full.py  全格式解包器（gpk/fpk/npk/nxs/wpk 聚合，含 gpk 的 AES+条目表+lz4/zstd）
  pc_npk_extractor.py       PC .npk 解包器（NXPK+AES+Murmur3双哈希精确定位）
  wpk_1dpw_decryptor.py    .wpk 1DPW 解密器（AC/PC/XC派生AES+Zstd→DDS）
  wpk_1dpw_verifier.py     1DPW 全链验证器（含5项负对照）
  ktx_to_png.py             .ktx 纹理转 PNG（ASTC 8x8）
  apk_script_decryptor.py   APK script.bin 解密器（AES+zlib）
  apk_npk_unpacker.py       APK .npk 解包器
  probe_gpk_images.py       GPK 伪装图片扫描器（扫描1DPW/异常头图片）

  === FPK 解包器（已破解：32B头+Zstd帧流）===
  fpk_scanner.py              .fpk 64包概览扫描器（分类：DDS/时装/MP4/FSB5/网格）
  fpk_001_full_scan.py       001.fpk 全量帧扫描器（manifest/DDS/spine/网格分类）

  === BinDict 配置解码器（已完全破解）===
  bindict_attrs_decoder.py       武器 attrs 解码器（hurt=攻击力, power=火力）
  bindict_kj1_transfer_decoder.py  转印消耗表 KJ1 解码器（11配方×6配置）
  bindict_attribute_data_extractor.py  attribute_data 表提取器（4个变体）
  bindict_attribute_data_decoder.py    attribute_data 行解码器（1404池,48字段）
  bindict_attribute_helper_extractor.py  AttributeHelper.nxs 提取器
  bindict_schema_scanner.py       全包 attrs schema 静态扫描器（25335条目）
  bindict_item_id_lookup.py       item id 互证查找器
  bindict_kj1_raw_decoder.py      KJ1 原始解码器
  bindict_lib/                     BinDict 依赖库（9个核心解码/验证脚本，勿删；旧探索脚本在_archive/05_bindict_exploration/）

  === 文件名还原器（三合一，已突破：170条资源路径）===
  filename_restore.py      统一入口：dict（路径字典匹配）/ bindict（配置表提取170条）/ verify（解包验证）

  === THFB 工具（三合一）===
  thfb_toolkit.py          统一入口：extract（27.3万条hash）/ merge（IDX映射）/ verify-weapon（SKPW 1DPW复验）

  === 其他 ===
  output/_archive/            归档目录（旧实验脚本/测试脚本）
  使用说明.txt                本文件



================================================================================
一、新版图形化 EXE（2026-08-29 已构建并验收）
================================================================================

【请运行】
  明日之后拆包器_新.exe（工具包第一层，45.58 MB）

【已实测】
  - EXE 可启动；冻结模式 smoke 通过。
  - 默认输出固定为 EXE 同级 output\，不会写入 PyInstaller _MEI 临时目录。
  - 游戏目录 E:\mrzh / E:\lifeafter 只读；输出目录若落在游戏源目录内会被拒绝。
  - 大 FPK/GPK 同盘顺序执行；小索引低并发；CPU 当前上限约 80%。
  - 暂停/取消在当前资源包完成后的安全边界生效，避免半截写入。
  - 皮肤页只展示已验证配置链；path→物理条目现由 v5 统一索引提供，EXE 旧皮肤页尚未接入。

【新旧关系】
  明日之后拆包器.exe      旧版，保留未覆盖。
  明日之后拆包器_新.exe    新版，当前建议使用。
  工具库_应用核心\       新 GUI 源码、任务层、调度器、6 条回归测试和构建环境。

================================================================================
一、明日之后拆包器.exe（可视化界面）
================================================================================

【运行方式】
  双击 明日之后拆包器.exe 即可运行，无需安装 Python。

【功能说明】
  1. 路径设置
     - 游戏目录：选择游戏根目录（如 E:\mrzh），程序自动识别 res 子目录
     - 输出目录：解包后的文件存放位置

  2. 拆包模式（三选一）
     - 全量拆包：解包资源目录下所有支持的文件
     - 近30天内更新：只解包最近30天内修改过的文件（适合找新内容）
     - 定向搜索：按关键词搜索文件内容，只输出命中的文件

  3. 文件类型（可多选）
     GPK / FPK / NPK / NXS / WPK / 全部

  4. 搜索关键词（仅定向搜索模式显示）
     输入空格分隔的关键词，如：战神烈火剑 极光剑 帝皇裁决 AUG

  5. 预览标签页
     - 加载解包后的目录，浏览文件
     - 支持 PNG/JPG/BMP 图片预览
     - 支持 DDS 纹理自动转 PNG 预览
     - 支持 TXT/JSON/XML 文本预览
     - 其他格式显示十六进制预览

【注意事项】
  - exe 首次启动较慢（解压运行库），后续正常
  - 全量拆包耗时较长，建议先用"定向搜索"或"近30天内更新"
  - 解包大文件时电脑可能卡顿，属正常现象


================================================================================
二、resource_locator.py（资源定位器）
================================================================================

【功能】
  封装武器皮肤和人物时装的完整定位流程，四层递进搜索：
    1. 文件名/目录名关键词扫描 → 快速定位候选目录
    2. 多编码内容字符串搜索（UTF-8/GBK/UTF-16LE/BE）→ 挖明文文本
    3. 关键词链式扩展 → 从已知词扩展同系列新词
    4. 与正式服对比 → 筛选体验服独有（未上线）内容

【环境依赖】
  Python 3.8+，无需额外第三方库（仅用标准库）

【命令行用法】
  # 只搜武器皮肤
  python resource_locator.py <体验服解包目录> <正式服解包目录> weapon

  # 只搜人物时装
  python resource_locator.py <体验服解包目录> <正式服解包目录> fashion

  # 全部（武器+时装）
  python resource_locator.py <体验服解包目录> <正式服解包目录> all

  # 不对比正式服
  python resource_locator.py <体验服解包目录> weapon

【示例】
  python resource_locator.py E:\mrzh\gpk_unpacked E:\lifeafter_unpacked weapon

【Python 调用用法】
  from resource_locator import ResourceLocator

  locator = ResourceLocator(
      unpack_dir=r"E:\mrzh\gpk_unpacked",    # 体验服解包目录
      official_dir=r"E:\lifeafter_unpacked",   # 正式服解包目录（可选）
      workers=8                                  # 多进程数（默认 CPU 一半）
  )

  # 武器皮肤完整定位
  weapons = locator.locate_weapon_skins()

  # 人物时装完整定位
  fashions = locator.locate_fashion()

【输出结果】
  结果自动保存到 解包目录同级\_定位结果\ 文件夹：
    武器皮肤_文件名命中.txt       候选文件路径列表
    武器皮肤_内容命中.json        明文搜索结果（含路径、命中词、编码、上下文）
    武器皮肤_链式扩展.json        每轮发现的新词
    武器皮肤_体验服独有.txt       正式服没有的新文件
    武器皮肤_定位结果_汇总.json   全部结果汇总
  （人物时装同理，文件名以"人物时装_"开头）

【自定义关键词】
  打开 resource_locator.py，修改顶部常量：
    WEAPON_FILENAME_KEYWORDS   武器皮肤文件名关键词
    WEAPON_CONTENT_KEYWORDS    武器皮肤内容关键词
    FASHION_FILENAME_KEYWORDS  人物时装文件名关键词
    FASHION_CONTENT_KEYWORDS   人物时装内容关键词
    ARMOR_KEYWORDS              铠甲勇士联动专属关键词


================================================================================
三、lifeafter_unpacker_full.py（全格式解包器）
================================================================================

【功能】
  核心解包脚本，支持以下格式：
    .gpk   AES-ECB 加密 + 32字节条目表 + lz4/zstd 压缩
    .fpk   32字节文件头 + Zstd帧流（连续Zstd帧，magic 28 B5 2F FD）
    .npk   NXPK 魔数 + AES-ECB 头/表 + 48字节条目 + Murmur3 双哈希
    .nxs   BinDict 配置表（完整codec：x{容器+0x76索引/0x96行式+D6/C6 schema）
    .wpk   1DPW 外壳 + AC/PC/XC 派生 AES-ECB + Zstd → DDS

【环境依赖】
  Python 3.8+
  pip install pycryptodome zstandard lz4 pillow fsb5 cryptography

【核心算法】
  AES 密钥材料： [REDACTED]
    算法说明：AES-ECB；具体材料不写入说明文档

  gpk 条目表结构（解密后 pt@20 = 条目数，每条 32 字节）：
    uint32 offset       数据偏移
    uint32 comp_size    压缩后大小
    uint32 decomp_size  解压后大小
    uint32 crc1
    uint32 crc2
    uint32 flag         0=原始, 2=lz4, 12=zstd
    uint32 res1         保留
    uint32 res2         保留
    数据从 offset+36 开始

  FPK 结构（32B头 + Zstd帧流）：
    帧流 = 连续独立 Zstd 帧（magic 28 B5 2F FD），帧间 1-3 字节 0x00 间隔
    帧内容：清单文本 / DDS 纹理 / spine JSON 骨骼 / 模型网格 / MP4 / FSB5
    帧循环正确姿势：decompressobj + obj.eof + obj.unused_data + find magic

  1DPW 解密链：
    1DPW外壳 → AC/PC/XC前缀派生AES-ECB → 尾部XOR(0x5a反序) → ENON/DTSZ → Zstd → DDS

  BinDict 完整 codec：
    容器：x{ + u32 body_len + body
    body = [u32 count][u32 res][ends表/占位][blob]
    行式：0x96 32 + 6×ULEB头 + 0..n×(27 kind count 元素...)
    行值：[d6或c6][uleb schema_ref][uleb bitmap_ref][标量值流]
    标量类型：01=uleb 03=bool 05=CHS字符串引用 11=0x0B引用
              17=zigzag 18=f32 22=f64

  武器 attrs schema（55字段，schema_ref=6109）：
    field2  = armor（护甲）
    field23 = hurt（攻击力）  ← AUG=148, SCAR=161
    field35 = power（火力）   ← AUG=2.0, SCAR=2.0
    field42 = shield_recovery（护盾恢复）
    field48 = thump（震动）
    实际伤害 = 攻击力 × 火力

  文件名 path_id（双 Murmur3 x86_32）：
    high = murmur3_x86_32(path, 0x77777777)
    low  = murmur3_x86_32(path, 0x66666666)
    file_id = (high << 32) | low
    路径用反斜杠（如 com\cdata\attribute_data.nxs），UTF-8编码

【快速调用示例】
  from lifeafter_unpacker_full import extract_gpk, extract_fpk_full

  # 解包单个 gpk
  extract_gpk(r"E:\mrzh\res\001.gpk", r"E:\output\001")

  # 批量解包所有 gpk
  import glob, os
  for f in glob.glob(r"E:\mrzh\res\*.gpk"):
      name = os.path.splitext(os.path.basename(f))[0]
      extract_gpk(f, os.path.join(r"E:\output", name))


================================================================================
四、FPK 解包器（64包分类总览）
================================================================================

【fpk_scanner.py — 64包概览扫描】
  功能：扫描所有 .fpk 包，分类（DDS纹理流/活动时装/MP4/FSB5/模型网格/加密网格）
  用法：python fpk_scanner.py
  输出：output/fpk_overview/fpk_overview_001.json

【fpk_001_full_scan.py — 单包全量帧扫描】
  功能：解包单个 fpk 的所有帧，分类（manifest/DDS/spine/网格/other）
  用法：修改脚本顶部 SRC 变量为目标 fpk 路径，然后 python fpk_001_full_scan.py
  输出：output/fpk_001_full/（含所有帧的分类清单和提取的DDS/manifest/spine）

【64包分类】
  DDS 纹理流：58个（003-064多数），图集/贴图（2048²为主）
  活动时装包：001，"沙漠珍珠"：男女图集 2048² + spine 骨骼 + 附件
  MP4 视频：002，isom/BMFF容器
  FSB5 音频：010，FMOD Sample Bank
  模型网格：022/023/027/048/054/055/058/064，NeoX顶点流格式
  半加密网格：013/020/021，明文float头(44/56B) + 加密数据体（未破，收益递减先搁置）

【001.fpk 完整案例】
  总帧数：40,454
  类型统计：manifest×2、DDS×11,146、spine JSON×2、other×29,304
  other帧分类：34 80 c8 bb系×7606、c1 59 41 0d系×3700、cc aa 55 66×390、
              52 47 49 53="RGIS"×203、2.1.0.0网格仅5帧


================================================================================
五、BinDict 配置解码器（武器属性/转印消耗/属性表）
================================================================================

【概述】
  BinDict 是网易自研的 Python 序列化格式，用于存储游戏配置表。
  完整 codec 已攻破：x{容器 + 0x76索引/0x96行式 + D6/C6 schema + bitmap + 标量值流。

【核心脚本】

  1. bindict_attrs_decoder.py — 武器 attrs 解码器
     功能：解码 all_equips 表中武器的 attrs 对象，输出 hurt(攻击力)/power(火力)等属性
     用法：python bindict_attrs_decoder.py
     关键结论：AUG 攻击力=148, 火力=2.0；SCAR 攻击力=161, 火力=2.0

  2. bindict_kj1_transfer_decoder.py — 转印消耗表 KJ1 解码器
     功能：解码 advanced_recipe_consume_conf_auto_oversea_data_kj1 表
     用法：python bindict_kj1_transfer_decoder.py
     输出：11个转印配方 × 6个共享配置的完整消耗数值

  3. bindict_attribute_data_extractor.py — attribute_data 表提取器
     功能：从 PC script.npk / script.py3.npk 中提取 attribute_data 表（4个变体）
     用法：python bindict_attribute_data_extractor.py
     依赖：npk_reader.py（公共NPK读取库）

  4. bindict_attribute_data_decoder.py — attribute_data 行解码器
     功能：解码 attribute_data 表的行数据（1404池，48字段schema）
     用法：python bindict_attribute_data_decoder.py

  5. bindict_schema_scanner.py — 全包 attrs schema 静态扫描器
     功能：扫描 PC script.py314.lc.npk 全部25335条目，找 attrs schema 定义
     用法：python bindict_schema_scanner.py

  6. wpk_1dpw_verifier.py — 1DPW 全链验证器
     功能：验证 ui.idx/ui3.wpk/ui4.wpk 的 1DPW 解密全链，含5项负对照
     用法：python wpk_1dpw_verifier.py
     关键：1DPW → AC派生AES → DTSZ → Zstd → DDS

【注意事项】
  - BinDict 脚本硬编码了游戏路径 E:/mrzh，如需修改请编辑脚本顶部的路径常量
  - 输出目录默认为脚本目录下的 output/ 子目录
  - bindict_lib/ 是依赖库，不要删除


================================================================================
六、文件名还原器（已突破：170条资源路径）
================================================================================

【核心发现】
  NPK 资源条目逻辑路径 = 相对路径 + 反斜杠，无 `ui/` 前缀
  例：配置表原文 `ui/damoshi_icon/.../daxiao.png`
      → NPK 路径 `damoshi_icon\...\daxiao.png`

【算法】
  file_id = murmur3_x86_32(path, 0x77777777) << 32 | murmur3_x86_32(path, 0x66666666)
  路径用反斜杠，UTF-8编码

【filename_restorer.py — 基础路径字典匹配】
  功能：用路径字典与 NPK 条目表匹配，还原文件名
  验证：11个已知脚本路径全匹配（AttributeHelper、Equip、GmCmdParser等）
  用法：
    python filename_restorer.py <npk文件> <拆包器目录> <输出目录>
  输出：
    filename_restore_<npk名>.json  匹配结果
    unmatched_ids_<npk名>.txt       未匹配的 file_id 列表
    path_dictionary.txt              路径字典（可手动扩充）

【filename_restore_from_bindict_001.py — 从BinDict提取资源路径】
  功能：从 BinDict 配置表 CHS 池提取资源路径字符串 → 生成正反斜杠+去前缀变体
        → 计算 path_id → 与4个NPK包（script.py3/script.py314/res/ui）匹配
  成果：360条原始路径 → 1313条变体 → 170条命中（ui.npk，57,353条）
  命中组：damoshi_icon(打魔石图标)、jijianbiaoqing_icon(击剑表情图标)、
          ganranzhe_touxiang_icon(感染者头像图标)、main_v4_icon(主界面技能图标)、
          item_icon(物品图标)、font_icon(字体图标)
  用法：
    python filename_restore_from_bindict_001.py
  依赖：C盘历史配置表副本（如不存在需先从NPK解包配置表）
  输出：
    resource_paths_extracted.json  提取的原始路径+变体
    resource_path_matches.json      匹配结果（170条）

【filename_restore_verify_001.py — 批量解包验证】
  功能：对170条命中逐个解包，验证是否为有效PNG/DDS
  成果：170/170 PNG解包验证通过（path_id命中≠成功，必须解包验证）
  用法：
    python filename_restore_verify_001.py
  输出：
    resource_path_verified.json  验证结果（path/file_id/entry/flag/大小/type）
    resource_path_verified.csv   CSV格式

【扩充路径字典的方法】
  方法1：从 BinDict 配置表提取（最高效，已验证170条）
  方法2：从 exe 字符串表扫描（未做，可能还原数千条）
  方法3：按已知模式批量生成（中效）
  方法4：手动扩充 path_dictionary.txt（低效但精确）

【注意事项】
  - path_id 命中 ≠ 成功，必须解包验证（配置表字符串有拼接残留，如 capture_dist+main_v4_icon 粘连）
  - FPK manifest 纹理名与 NPK path_id 无关（不同体系），不要混淆
  - 资源路径无 ui/ 前缀，脚本路径有 com/ 前缀


================================================================================
七、文档索引（拆包成果必须写入此处）
================================================================================

【重要规则】
  每次拆包完成后，必须把拆包成果（包内容、新发现、文件类型统计等）
  写入 文档索引/ 目录下的对应文档，保持索引与实际成果同步。

【文档索引目录】
  文档索引/
    ├── 资源包索引.md          每个包里是什么内容（55个gpk+64个fpk+ui.npk+脚本包）
    ├── 资源更新时间表.md      体验服vs正式服对比，哪些是新增/更新的
    └── 资源更新时间表.json    同上，JSON格式，方便脚本读取

【拆包后写入流程】
  1. 用拆包器解包目标包（gpk/fpk/npk等）
  2. 统计文件类型（DDS/PNG/模型/音频/配置等）
  3. 搜索关键词（铠甲勇士/AUG/装备改造转移/新时装等）
  4. 把发现写入 文档索引/资源包索引.md 对应包的条目
  5. 如果是8月新更新的包，同时更新 文档索引/资源更新时间表.md
  6. 删除临时拆包文件（保留analysis.json和有价值的发现）

【资源包索引.md 格式】
  每个包包含：
    - 包名、大小、修改时间、条目数
    - 主要内容类型（人物/武器/UI/场景/特效等）
    - 文件类型统计（DDS多少个、PNG多少个、模型多少个等）
    - 已知资源定位（如"刑天载具音频在sound.gpk→000933.bin"）
    - 关键词命中（铠甲勇士/AUG/装备改造转移等）

【资源更新时间表.md 格式】
  按时间倒序列出所有包：
    - 包名、路径、大小、修改时间
    - 体验服/正式服是否存在
    - 是否为体验服独有（新增）
    - 8月更新标记

【更新工具】
  scan_package_times.py  自动扫描所有包，生成资源更新时间表
  用法：python scan_package_times.py
  输出：文档索引/资源更新时间表.md + .json

【注意事项】
  - 文档索引是唯一权威来源，所有拆包成果必须汇总到此处
  - 不要在多个地方分散记录，避免信息混乱
  - 发现新格式/新资源时，及时更新索引
  - 删除临时文件前，确认有价值的发现已写入索引


================================================================================
八、常见问题
================================================================================

Q: exe 双击没反应？
A: 首次启动需要解压运行库，等待 10-30 秒。如果仍无法运行，
   检查是否被杀毒软件拦截，添加信任即可。

Q: 解包出来的文件全是 .bin 和 .dds，看不了？
A: .dds 是纹理格式，可以用拆包器的"预览"标签页打开（自动转 PNG）。
   .bin 是配置/模型/音频等二进制文件，需要对应格式的解析器。
   音频 .bin（FSB5 格式）可以用 vgmstream 工具转 WAV。

Q: 为什么有些文件解包失败？
A: 目前 FPK 加密网格（013/020/021）、.enc_jpg 时装图标、lifeafter.exe 脱壳
   尚未完全破解。已破解的部分（gpk全量/FPK明文帧/wpk 1DPW/BinDict）可正常解包。

Q: 怎么找未上线的新内容？
A: 方法一：用 resource_locator.py 与正式服解包目录对比，体验服独有的就是新内容。
   方法二：用拆包器的"近30天内更新"模式，只解包最近修改的文件。
   方法三：用"定向搜索"模式，搜已知新内容的关键词（如 AUG、装备改造转移）。

Q: 解包速度很慢？
A: gpk 解包是 CPU 密集型任务，全量解包（138万文件）需要 30-60 分钟。
   建议先用定向搜索缩小范围，不要全量解包。
   resource_locator.py 支持多进程（workers 参数），可充分利用多核 CPU。

Q: DDS 预览是空白或花屏？
A: 部分 DDS 是压缩格式（BC1/BC3/BC7），Pillow 可能不支持。
   可以用 Intel Texture Works、NVIDIA Texture Tools 或 GIMP 打开。

Q: 文件名怎么还原？
A: 用 filename_restorer.py，基于双 Murmur3 算法匹配路径字典。
   路径字典越大，还原率越高。可手动扩充 path_dictionary.txt。


================================================================================
八、文件格式破解进度总结（v4.0，2026-08-29）
================================================================================

【已完全破解】
  .gpk      AES-ECB 解密 + 32字节条目表 + lz4/zstd 解压 + 魔数判扩展名
  .npk(PC)  NXPK 魔数 + AES-ECB 头/表 + 48字节条目 + Murmur3 双哈希 path_id
  .fpk      32字节文件头 + Zstd帧流（连续Zstd帧，magic 28 B5 2F FD，帧间1-3B间隔）
            64包分类：DDS纹理流58个/活动时装001/MP4 002/FSB5 010/模型网格8个/半加密3个
  .wpk/.idx 1DPW 外壳 + AC/PC/XC 派生 AES-ECB + 尾部XOR + ENON/DTSZ + Zstd → DDS
  .ktx      伪装 KTX 头 + ASTC 8x8 压缩 + mipmap 链 → PNG
  APK script.bin  AES-ECB + 16字节头 + zlib
  FSB5      音频库解析（采样名、轨道数），vgmstream 转 WAV
  THFB(.thx/.thh) 24B条目[16B hash][u32][u32]，27.3万条全量提取，映射链 hash→IDX→1DPW→DDS
  BinDict .nxs  完整 codec：x{容器 + 0x76索引/0x96行式 + D6/C6 schema + bitmap + 标量值流
              武器 attrs: field23=hurt(攻击力), field35=power(火力)
              转印消耗表 KJ1: 11配方×6配置完整数值
              attribute_data: 1404池, 48字段schema
  文件名还原  双Murmur3 x86_32（高seed 0x77777777, 低seed 0x66666666），11已知路径全验证

【部分破解】
  FPK加密网格（013/020/021）：明文float元数据头(44/56B) + 加密数据体（熵6.84/8，疑似流变换，收益递减先搁置）

【未破解】
  lifeafter.exe  修改版 UPX + 整体加密（标准脱壳失败），唯一剩余主线
  .enc_jpg 时装图标  伪装JPEG，样本未找到（扫描3个gpk包无候选），待别的模型处理

【已证伪】
  gres .gpk 分卷  RPGF/CPGF/KPGF 非魔数，是加密数据偶然字节；正式服 character = 1DPW 格式


================================================================================
                            工具包版本：v4.0
                            更新日期：2026-08-29
        （新增 FPK 解包器/THFB破解/BinDict完整codec/文件名还原器/GPK伪装扫描）
================================================================================
