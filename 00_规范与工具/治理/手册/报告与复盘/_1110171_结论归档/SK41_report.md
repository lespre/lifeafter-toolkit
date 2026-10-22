# task-41 交付：`skeleton_preview.html`（层级结构 + 挂点坐标架，诚实标注非真实姿态）

## 交付物（全部新建，未改任何既有文件）
| 文件 | 字节 | sha256(前16) |
|---|---|---|
| `08Lifeafter wiki\skeleton_preview.html` | 24037 | `b89ee5802dff587f` |
| `08Lifeafter wiki\assets\skel_preview\skel_data.js` | 136953 | `adf9d477783978f3` |

- 打开：`http://127.0.0.1:8765/skeleton_preview.html` → **HTTP 200**（实测）。
- 依赖：**无外部 CDN**；three.js 用仓库内 `assets/vendor/three/three.module.min.js`（ES module import）。
  相机控制是页面内自写的 ~30 行 orbit（拖拽旋转/滚轮缩放/切皮肤重置），**没有**引 OrbitControls（避免 import map）。
- 数据来源（只读）：`03拆包产物\_gim_out\skel\*_skeleton.json`(24) / `*_mount.json`(13) / `03拆包产物\_target_1110171\SKEL2_all_37.json`；
  中文名取 `08Lifeafter wiki\data\boards\weapon_skin_sfx_text_sources.json`（115 条 id→name，实测全部命中）。
  这些 `03拆包产物\` 路径不在 wiki 根下、页面取不到 ⇒ 我把**所需字段**（层级 parent/children、self_check、mesh sha16/row、mount 矩阵与 sockets、unresolved）生成进 `assets/skel_preview/skel_data.js`（含 `sources` 指纹段：各源文件 sha16 + mtime）。

## 页面实现（对照要求）
1. 左列 **37 行**，按 `典藏(L5)`(22) / `传世(L6)`(15) 分组，每行 `id 名称 · N 骨 / 无骨架`，点选切换（无骨架行橙色「无骨架」）。
2. 右侧 3D：
   - **24 个有骨架**：页面 `fetch` 对应 `assets/3d/weapon_skin/_skeletons/<id>_skeleton.glb`，**自己解析 GLB 的 JSON chunk**（magic/chunk 校验）取 `nodes[].name` + `children[]` + `scenes[0].nodes`（根）；每骨画球（根=黄、其余=蓝）、父子画线；**自动树形布局**：角度按**叶子数**分配、半径∝√深度（压缩深链），根在原点；可选骨名标签（默认关）。
   - **13 个无骨架**：读 `mount` 数据，`MatrixToBone` 4×4 画成**坐标架**（RGB 三轴 + 线框盒），每个**有矩阵的 socket** 另画一个橙色坐标架；socket 列表逐条给 `must_show` 与「有 4×4（已画坐标架）/ **None（不画零矩阵）**」。
3. 诚实标注（页面可见，非注释）：
   - 顶部横幅：**「⚠ 层级/结构预览 —— 逐骨 TRS 未定证，位置为自动布局，非游戏内真实姿态（源侧与 GLB 均无 TRS：`gltf.extras.transforms = not_emitted_unresolved`）」**；
   - 每皮肤小字：`来源 res\weapon.gpk#<mesh row>`（含 variant/字节）、`mesh sha16`、gim 行、`Σchildren+roots == bone_count`（✓/✗/`unresolved`）、`parent<self 违规`（条数+示例；无 self_check 段时显示 `unresolved`）、cycle/可达、节点来源（GLB/skeleton.json）、骨架 JSON 名与 sha16 + 「含逐骨 92 B 原始字节，字段语义 unresolved」；
   - 无骨架皮肤：**「源侧无骨架：已导出挂点复原（MatrixToBone + Socket*）」** + `mount.json` 自述的 unresolved 5 条原文列出；
   - 右侧底部固定 `unresolved：逐骨 TRS / 姿态 / 骨骼长度 —— 源侧与 GLB 都没有 ⇒ 本页只画层级与自动布局，不画真实姿态`。
4. 交互：`roots[]` 与骨数/节点数/连线数显示在左上 HUD，`重置视角` 按钮，切皮肤时相机按内容包围球重设（网格按内容缩放）。

## 验收读数（真实浏览器、单浏览器、逐项切换 37 个 id）
- `ready=function`、`SKEL_DATA.rows.length=37`；**24/24 有骨架全部「节点+连线」非空**、**13/13 无骨架全部「≥1 坐标架」**（逐行见 `03拆包产物\_target_1110171\SK41_verify.json`）。
- 截图（稳定性门 N=5 连续帧 sha 相同，`gate_tries=5`；取帧前复核 canvas 尺寸）——**我逐张亲看过**：
  | 皮肤 | 类型 | 截图 | sha256(前16) |
  |---|---|---|---|
  | 1110032 九霄狐啸 | 有骨架 52 骨 | `SK41_1110032.png` | `793154417aba5179` |
  | 1110013 幻影猎蝎 | 有骨架 14 骨 | `SK41_1110013.png` | `baaf877e99061749` |
  | **1110171 光影蝶呦嗝** | **无骨架**（挂点） | `SK41_1110171.png` | `0f7d9f97b34c1d57` |
- `window.__errs = []`（页面自收 `error` / `unhandledrejection`，并显示红条）；`console` 错误 **仅 favicon.ico 404**（允许项，无其它 error）。
- 浏览器已 `taskkill /T /F` 关闭，端口 10041 **无 LISTEN**（已复查）；本次只起 1 个浏览器。

## 发现的问题 / 与预期不符之处（如实）
1. **节点数/连线数全部自洽**：24 个 GLB 的 `json_nodes == bone_count`、连线数 == 节点数 − 根数，**没有不符的皮肤**。
2. **4 个皮肤是 2 个根**（不是 1 条树）：`1110021` roots=[0,17]、`1110128`=[0,18]、`1110129`=[0,14]、`1110146`=[0,3] ⇒ 画面上是两条互不相连的链，页面如实显示 `roots=[...]`。
3. **`parent<self` 违规**：`1110032` **44 处**（status=`ok_with_selfcheck_warning`）、`1110160`/`1110161` 各 1 处（`bone 29 → parent 31`）。页面把这些标红；注意 `cycle=ok / 全节点可达` 仍为真 ⇒ 我画的是 GLB 的 `children` 父子关系（真树），**没有**按 parent 索引去连。
4. **`1110115` 的 `skeleton.json` 无 `self_check` 段** ⇒ 页面该行显示 `unresolved`（节点 5 / 连线 4 仍正常画出）。
5. 挂点侧：每皮肤「坐标架数 = 1（MatrixToBone）+ 有矩阵的 socket 数」；无矩阵的 socket 例如 `1110171` 的 `pifuguashi` 标 **None 且不画**（其余：1110024/1110031/1110137/1110145/1110165/11101451 各 8 sockets/7 矩阵；1110121/1110152/1110171 各 7/6；1110169/11101691 6/5；1110177/11101771 5/4）。
6. `11101451` / `11101691` / `11101771` 是与 `1110145/1110169/1110177` 同名的**独立 id**（名单里确实各占一行，名称带「（14天）/（7天）」等）——按名单原样列出，未合并。

## 需要 Lead 做的一件事（不在我写域）
`skeletons.html` 顶部请加一条导航：`<a href="skeleton_preview.html">▶ 3D 层级预览（新）</a>` —— 我**没有**改 `skeletons.html`。

## 纪律
- 只新建上述两个路径；未改 `skeletons.html` / `board.html` / `wiki.html` / viewer.js / adapter / 任何 manifest / `_skeletons/` 资产。
- 不编造：GLB 无 TRS ⇒ 不画姿态；`MatrixToBone` 语义未验证 ⇒ 只按矩阵**数值**直绘并标 unresolved；无矩阵的 socket **不画零矩阵**。
- 浏览器卫生：单浏览器 + `taskkill /T /F` + 端口复查，已写在上文验收节。
