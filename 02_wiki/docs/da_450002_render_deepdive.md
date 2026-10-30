# da_450002（可乐大亨）渲染异常 · 深挖报告

> 时间：2026-10-30
> 结论：**该骨架数据与标准 Spine 2.1 约定不一致**（uv 归一化口径 + 父级缩放已烘焙），
> 现行渲染器按标准约定工作，于是画面散架。已回退官方静态图；修复需要按骨架打覆盖系数。

---

## 1. 现象

卡片动图里：角色 + 蓝色背景框缩在右下角（约画面 40%），左上角另有一坨金色光效，
两者之间大片空白。官方静态立绘是「角色撑满蓝框、金币环绕」。

## 2. 网络侧规范（同款渲染设计）

| 来源 | 关键结论 |
|---|---|
| Spine 官方 JSON 格式文档 <https://esotericsoftware.com/spine-json-format> | mesh 附件的 `uvs` 是**归一化到整张贴图页**的坐标；`triangles` 为三角形索引 |
| spine-cpp 论坛 <https://hr.esotericsoftware.com/forum/d/14397> | `getUVs()` = 「normalized within the entire texture」；`getRegionUVs()` 才是「normalized within the region」 |
| spine-python <https://github.com/terrysimons/spine-python> | 纯 Python 运行时，可用于交叉对照（未在本轮接入） |
| spine-ts MeshAttachment | 运行时用 `regionUVs` + 图集 region 反推页 UV，说明**JSON 里存的是页 UV** |

即：标准做法是「uvs × 页尺寸 → 采样整页」，region 裁切是运行时对 region 附件的优化。

## 3. 本骨架实测（与规范冲突的两处）

### ① uvs 口径

```
页        touxiang_ani_03.png   512 × 256
region 数 24；region "10" = 44×45 @ (277, 49)
mesh 10 的 uvs：x[0.000, 0.976] y[0.032, 1.000]
```

按标准，region 10 的页 UV 应是 x≈[0.541, 0.627]、y≈[0.191, 0.367]；
实测却是 0~1 覆盖整页 ⇒ **这套导出把 uvs 写成了 region 内归一化**（NeoX 变体）。
现行渲染器正好按 region 裁切 + uv 0..1 映射，所以 359 张能对；但对「uv 跨整页、
region 很小」的网格就会错位。

### ② 父级缩放被烘焙进顶点

```
骨树      root → bone(scaleX=scaleY=0.707) → {bg, guang, jinbi, ren(-13.08, -29.72)}
世界矩阵  bg / ren 均为 0.707
权重和    全部顶点恒为 1.0（不是权重缺失问题）
```

对照实验：

| 实验 | 结果 |
|---|---|
| 只渲染背景槽（slot 23） | 蓝色方块铺满整幅 → **背景定位是正常的** |
| 去掉中间骨 `bone` 的 0.707 | **角色恰好撑满蓝框，比例与官方立绘一致** |
| 逐骨归一化缩放（只去缩放保留平移） | 更乱（平移未同步缩放，错位） |
| 不做动画（纯 setup pose） | 同样散架 ⇒ **与动画无关** |

⇒ 该骨架的 mesh 顶点**已经把 0.707 烘焙进坐标**，渲染时再乘一次骨骼世界矩阵，
角色就只剩应有尺寸的 ~1/2；同时远端光效与主体的相对距离被放大，裁剪包围盒被撑开，
最终主体缩在角落。

## 4. 为什么没直接改渲染器

- 「uv 按整页采样」这条一旦整体切换，会**打翻现有 359 张**（它们依赖 region 裁切才对）。
- 逐骨归一化缩放会破坏平移一致性（实验 C）。
- 正确做法是**按骨架打覆盖**：对确认「父级缩放已烘焙」的骨架，给 mesh 顶点乘 1/0.707。
  实验 B 已证明效果正确，但只验证了这 1 个样本，没做全量回归，所以没直接上线。

## 5. 当前状态

```
da_450002        去掉 _media.anim，卡面回落官方静态立绘，标 anim_status=render_broken + 原因
其余 346 张动图   不受影响（da_450129 / af_410003 重渲与线上产物逐像素一致，差异 0.0）
诊断脚本          diag_450002_baked.py / diag_450002_bbox.py / diag_450002_outlier.py /
                  inspect_spine_mesh.py / scan_spine_mesh.py / test_render_one.py
```

## 6. 下一步（按成本排序）

1. **要一张实机截图**（或确认这头像游戏内是否有动效）：确认「角色撑满蓝框」是对的基准。
2. 若确认：把 `MESH_SCALE_OVERRIDE = {"touxiang_ani/touxiang_ani_03": 1/0.707}` 接进渲染器，
   只对该骨架生效，重渲这一条，人工看一遍。
3. 批量体检：用 `scan_spine_mesh.py` 找「中间骨统一缩放 ≠ 1 且 mesh 顶点尺寸 ≈ region 尺寸 × 缩放²」
   的骨架，形成同类清单，逐个验证后再扩大覆盖表。
4. 长期：把「uv 口径」与「缩放是否烘焙」做成骨架级显式字段（在 spine_live 旁的 sidecar 里），
   不让渲染器猜。

> 教训：**结构自洽 ≠ 语义正确**。这套骨架 atlas/uv/权重全部自洽，只有和官方约定对照才看得出错位。
