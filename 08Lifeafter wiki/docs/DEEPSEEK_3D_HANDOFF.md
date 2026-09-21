# DeepSeek 接入 Wiki 3D 查看器

目标只有一个：DeepSeek 交付模型后，Wiki 的对应皮肤卡片自动出现“3D 预览”按钮，可旋转并截图。

## 光影咏叹调的固定入口

- Wiki 皮肤 ID：`1110171`
- 新建目录：`assets/3d/weapon_skin/1110171/`
- 将双枪模型放为：`dual.glb`
- 将单枪模型放为：`single.glb`
- 可选截图海报：`poster.webp`
- 把 `_template/viewer.json` 复制到该目录，文件名保持 `viewer.json`

P1/P2/P3 是双枪的不同观察角度，不应拆成三个模型；P4 是单枪形态。模型文件只需双枪、单枪两个，角度交给查看器相机。

## 最后一步

在 Wiki 根目录运行：

```powershell
python tools/rebuild_weapon_skin_media.py
```

脚本只会登记真实存在且配置有效的 GLB；模型缺失时会直接报错，不会让 Wiki 出现一个坏按钮。然后用本地 HTTP 服务打开 `board.html?view=weapon-skin`，搜索“光影咏叹调”，点击“3D 预览”即可截图。

## DeepSeek 必须遵守的交付约定

- GLB 需自包含网格、材质和纹理；不要引用电脑上的绝对路径。
- 模型以原点为中心，尺度统一；双枪组合关系应烘焙进 `dual.glb`。
- 如需修正初始姿态，使用 `rotation_degrees: [x, y, z]`；单位明确为角度。不要把角度填写进旧的 `rotation`（该字段单位为弧度）。
- 正面方向必须与游戏参考一致，不能用镜像代替翻面。
- `viewer.json` 中的 `material` 只能填 `source_matched`、`source` 或 `approximate`；无法证明完全一致时填 `approximate`。
- 当前不接 SFX，保持 `sfx: "none"` 和 `effects.status: "none"`。
