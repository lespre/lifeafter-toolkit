# B 段验收：board 卡面骨骼行 + `skeleton_preview.html? id=` 深链（含 2 处需 Lead 处理的发现）

## 1. 深链（我的写域，已改）
- `08Lifeafter wiki\skeleton_preview.html` 现 sha16 **`5992b4135754733a`**（25,992 B，mtime 22:15:15）；数据文件 `assets/skel_preview/skel_data.js` sha16 `adf9d477783978f3`（未变）。
- 新增：`?id=<skin_id>` → 打开即选中该皮肤 + 相机重置；顶部蓝条显示「深链 `?id=X` → 已选中 …；相机已重置」。
  无效 id → 顶部黄条「⚠ 未知 id：X —— 本页共 37 个 id（见左列 L5/L6 分组）。已回落到默认选中 1110013 幻影狩蝎。」**不崩**。
  探针新增 `deep_link{requested,hit,reason,resolved,url}`（`window.__skelProbe().deep_link`），另加 `window.__skelSetId(id)` 便于深链自测。
- 实测：
  - `?id=1110171` → `{id:'1110171', kind:'mount', frames:7, sockets:7, sockets_none:1, canvas:[918,862], errors:[], deep_link:{requested:'1110171',hit:'1110171',resolved:'hit'}}` ✔
  - `?id=1110032` → `{id:'1110032', kind:'skeleton', nodes:52, lines:51, errors:[], resolved:'hit'}` ✔
  - `?id=NO_SUCH_ID` → `{id:'1110013', resolved:'fallback', errors:[]}` + 黄条可见（文案见上）✔

## 2. board 端到端（`board.html?b=weapon_skin_sfx_text_sources&view=wiki`）
- `WEAPON_SKIN_SKELETON.skins` = **37 个 id**；页面上 `.skin-skel` 行 = **34**；`骨骼 N 根` 标签 **24**（= 全部有骨架）、`源侧无骨架 · 挂点复原` 标签 **10**、预览链接 **34**、`骨架 GLB/JSON` 链接合计 92；console **无错误**。
- 抽查卡面文本：
  - `1110171` → `源侧无骨架 · 挂点复原 / 3D 挂点预览 / 挂点 JSON`（href `skeleton_preview.html?id=1110171`）✔（1110177 同构 ✔）
  - `1110032` → `骨骼 52 根 / 3D 层级预览 / 骨架 GLB / 骨架 JSON` ✔
- 链接 HTTP：`skeleton_preview.html?id=1110171` **200**；`_skeletons/1110013_skeleton.{glb,json}` 200/200、`1110032` 200/200、`1110129` 200/200；`1110171_mount.json` 200、`1110177_mount.json` 200；`data/media/weapon_skin_skeleton.js` 200。**（无骨架皮肤本就没有 `_skeleton.glb/json`，检查清单只对有骨架的取 GLB/JSON）**
- 截图（稳定性门 N=5 全同、`gate_tries=5`，**我亲看过**）：
  - 卡面 `B_board_card_1110171.png` sha16 **`a3413d14f3d929d5`**（可见 1110171「源侧无骨架 · 挂点复原 + 3D 挂点预览 + 挂点 JSON」，以及另一个有骨架卡的「骨骼 11 根 + GLB/JSON」）
  - 深链落地 `B_deeplink_1110171.png` sha16 **`d912a6a15b455f92`**：可见顶部蓝条「深链 ?id=1110171 → 已选中 1110171 光影咏叹调…」，左列 1110171 高亮、画布 7 个坐标架非空。

## 3. 需 Lead 处理的两条（都不在我的写域）
1. **board 上有 3 个 id 没有自己的骨骼行**：`11101451`、`11101691`、`11101771`（= 名单里 1110145/1110169/1110177 的「时限变体」id；SKEL2_all_37 里它们各自是一行、都是**无骨架**）。
   实测：被覆盖的 id = 34 个，缺的正是这 3 个；页面上有 18 个卡带「时限变体 1」⇒ 这 3 个变体被并进基卡、**没有渲染独立行**。
   建议（二选一，由你定）：① 接受 34/37（变体并入基卡，基卡已显示同类「源侧无骨架 · 挂点复原」）；② 在基卡里把变体的骨骼/挂点信息一并列出。若要求"37 行齐全"则必须改 `board.html`（你的写域）。
2. **`⚠ 处自检告警` 文案 bug**：`data/media/weapon_skin_skeleton.js` 的 `self_check.parent_lt_self_violations` 存的是**数组**，而 `board.html:691-692` 直接 `esc(v)` ⇒
   - 空数组的 21 张卡显示「⚠ 处自检告警」（数字为空）；
   - 有违规的 3 张卡显示「⚠ **[object Object],[object Object],…** 处自检告警」（我截图里就能看到"⚠ 处自检告警"）。
   一行修法：`const n=Array.isArray(v)?v.length:v;` 再用 `n`，并对 `n===0` 不显示告警。

## 4. 运维
- 本轮起了 **2 个**浏览器（两次验收各 1 个，均为单浏览器、无并发），各自 `taskkill /T /F` 收尾；端口 **10045 / 10047 无 LISTEN**，匹配我的 chrome 进程 0 个 ⇒ **已关闭、无残留**。
