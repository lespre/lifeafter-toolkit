# 渲染后端：PC 测试服已带 Vulkan 路径（2026-10-22）

## 证据（全部来自本地文件，非推测）

在 PC 测试服 `E:\mrzh` 里找到 Vulkan 专用组件，且**多个引擎构建目录都有**：

```
bin/x64-a50/VkLayer_khronos_validation.dll     17 MB   Khronos 官方校验层
bin/x64-a50/VkLayer_crash_diagnostic.dll               Vulkan 崩溃诊断层
bin/x64-a50/cc_bin/HookCaptureVK64.json                 Vulkan 抓帧钩子配置
bin/x64-a50-2/…                                         同上（第二套构建）
Documents/bin/x64/…                                     同上（可写层构建）
Documents/bin/x64-3/…                                   同上
```

`HookCaptureVK64.json` 是关键：只有走 Vulkan 的客户端才会配这根抓帧钩子。
`VkLayer_*` 也需要 `vkCreateInstance` 链路才会被加载。

## 这改变了什么

| 层面 | 影响 |
|---|---|
| 资源格式 | 无影响，spine/图集/贴图仍是同一套 |
| spine 逻辑 | 无影响，仍是 cocos2d-x 的 spine-c（在 libclient 里已确认） |
| 渲染验证 | 有影响：以后要和实机逐像素对照，得按 Vulkan 的颜色空间/采样设置去比 |
| 抓帧分析 | 可以直接用 Vulkan 抓帧钩子，比 OpenGL 时代好取证 |

## 与 PE（安卓侧）的关系

安卓侧 `libclient_emulator_arm64.so` 的图形后端是 GLES/Vulkan 取决于设备；
本次只确认了 **PC 测试服已经有 Vulkan 路径**，安卓侧尚未逐一验证。

## 建议

以后做「渲染一致」类验收（皮肤立绘、spine 头像、材质出图）时，先确认对照端用的是哪条后端：
Vulkan 与 GL 在 sRGB / 预乘 alpha / 采样上会差一点点，逐像素比会误判成「渲染错」。
