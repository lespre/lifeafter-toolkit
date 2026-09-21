/* weapon_skin_cubes_custom.js —— **自造近似**环境立方体清单（custom / self-authored）
 *
 * ⚠️⚠️ 本文件里的 cube **不是游戏资产**。它由游戏自己的背景板重采样而来，属于**自造近似**
 *      （status = self_authored_approximate），authority = user_authorized_manual_20260920。
 *      **不得**当作「游戏实际使用该环境」的证据，**不得**计入「源数据驱动」目标。
 *
 * 为什么单独一个文件：`weapon_skin_cubes.js`（真源 cube 总清单，schema weapon_skin_cubes/v1）
 * 由另一路代理生成。为了**不互相覆盖**，自造条目写在本文件，并导出 mergeInto() 供上级并入：
 *
 *     window.WikiWeaponSkinCubesCustom.mergeInto(window.WIKI_WEAPON_SKIN_CUBES);
 *
 * ⚠ 给选择器实现者的两条注意：
 *   ① 本条目 status='self_authored_approximate'，**故意落在**总清单既有枚举
 *      (source_verified/partial/unresolved) **之外** —— 这样它绝不会被误统计为「已定位源 cube」。
 *      若要让它出现在下拉里，请**显式**接受该状态，并把它排到单独分组、标「自造近似（非游戏资产）」。
 *   ② faces[] 指向 **rgbm/** 子目录：查看器源 IBL 分支按 asm 542-544 `pow(rgb*a*16,2)` 解码、
 *      且 cube 纹理 colorSpace=NoColorSpace，源六面 alpha≈0.015 即 RGBM 乘子。
 *      直接喂**无 alpha** 的 sRGB 面会 a=1.0 ⇒ 亮约 4400×（实测 p50 0.9679 / >0.85 76.58%，
 *      纯属编码假象）。faces_srgb[] 仅供人眼看图，**不要**喂给查看器。
 *
 * 本文件**无副作用**、不自动改 DOM、不改任何查看器状态；只注册两个全局对象（若主清单已在则顺带合并）。
 * 由 _shared/cubes/custom_studio_20260920/_emit_manifest.py 生成 —— 请勿手改，改生成器。
 */
(function () {
  'use strict';

  var CUSTOM_CUBES = [
  {
    "name": "custom_studio_20260920",
    "status": "self_authored_approximate",
    "authority": "user_authorized_manual_20260920",
    "fidelity": "approximate",
    "is_game_asset": false,
    "derived_from": [
      "08Lifeafter wiki/assets/3d/weapon_skin/_shared/bg_weapon_skin_ingame.png sha256:e60c1a1d5e16b1b40bf891d6b796f328eed551aa75b45d2131e40ac26e908f26"
    ],
    "method": "背墙面=房间图（±X 侧墙/顶灯带/地面各自取源背板对应色带裁切缩放），正面=背墙镜像重模糊并向房间均色渐变，六面边界再向房间均色羽化 35% 以抑制接缝。",
    "note": "**自造近似立方体，非游戏资产**。仅用于观察环境反射对观感的影响；不得作为「游戏实际使用该环境」的证据，也不得计入「源数据驱动」目标。",
    "logical": "self_authored://custom_studio_20260920",
    "container": null,
    "row": null,
    "sha16": null,
    "dims": "512x512",
    "format": "PNG RGBA RGBM(a=multiplier) — 与源 B8G8R8A8_UNORM + asm542-544 解码约定对齐",
    "n_faces": 6,
    "resolve": "self_authored",
    "in_skin": false,
    "identity_basis": "self_authored_approximate — 无容器/无哈希命中，**不是**源 cube",
    "selectable": true,
    "group": "self_authored（自造近似，非游戏资产）",
    "requires_status_whitelist_extend": true,
    "cubemap_order": [
      "+X",
      "-X",
      "+Y",
      "-Y",
      "+Z",
      "-Z"
    ],
    "faces": [
      "assets/3d/weapon_skin/_shared/cubes/custom_studio_20260920/rgbm/custom_studio_20260920_f0_m0.png",
      "assets/3d/weapon_skin/_shared/cubes/custom_studio_20260920/rgbm/custom_studio_20260920_f1_m0.png",
      "assets/3d/weapon_skin/_shared/cubes/custom_studio_20260920/rgbm/custom_studio_20260920_f2_m0.png",
      "assets/3d/weapon_skin/_shared/cubes/custom_studio_20260920/rgbm/custom_studio_20260920_f3_m0.png",
      "assets/3d/weapon_skin/_shared/cubes/custom_studio_20260920/rgbm/custom_studio_20260920_f4_m0.png",
      "assets/3d/weapon_skin/_shared/cubes/custom_studio_20260920/rgbm/custom_studio_20260920_f5_m0.png"
    ],
    "faces_srgb": [
      "assets/3d/weapon_skin/_shared/cubes/custom_studio_20260920/custom_studio_20260920_f0_m0.png",
      "assets/3d/weapon_skin/_shared/cubes/custom_studio_20260920/custom_studio_20260920_f1_m0.png",
      "assets/3d/weapon_skin/_shared/cubes/custom_studio_20260920/custom_studio_20260920_f2_m0.png",
      "assets/3d/weapon_skin/_shared/cubes/custom_studio_20260920/custom_studio_20260920_f3_m0.png",
      "assets/3d/weapon_skin/_shared/cubes/custom_studio_20260920/custom_studio_20260920_f4_m0.png",
      "assets/3d/weapon_skin/_shared/cubes/custom_studio_20260920/custom_studio_20260920_f5_m0.png"
    ],
    "faces_encoding": "rgbm",
    "face_sha256_rgbm": [
      "985146752d03729cd8f78c2b1ea02a542d7efef5758a1301128252357681d90e",
      "2f8917e26ecd5b9ae42cd21e7e817bd31867b869b43c5bcc4afc0d1339c0881e",
      "2e45c0f0a314d1c8300dea5bd5d4715eb31f4076a1784d1d179e7267cf40de7b",
      "0b9c656c9081f40715257e9316e9d5f69cdabe7c810ee0b1ac6c7e44b6e0b0bd",
      "bb191ef0fcb85d7cafd0933fd3139ec81865efc7d6f199522ed11416d5272ef6",
      "8f815e6642047b5c6505ebefa5d5f7c2420c4e62650435377c1d8e19f78647ff"
    ],
    "face_sha256_srgb": [
      "78e55829e2d351d494b8d388ae9b13290829e1781d09bf39ebd5a572b5d0299f",
      "55343f5a9876a67b262773624437dc5937eafd8fd4c764746c9845a856c79d8c",
      "5b1a3d6e0d73fae471370e4c78c235982764f24db4aaf4db7054c06ff1242525",
      "621beacb4406b8b898da94dcef04462d574c0fd34a6bcda8bf5403d65c60e9e2",
      "6dcf5d33bcc598213c6baa04361a04cbd2233056b557f05d2b646d0f52677dfa",
      "a8528acd9ba931e1b3c1f21ce3c2b352da7a64f6e8d69b5b6d0565c5dfaf4f8a"
    ],
    "rgbm_encoding": {
      "why": "查看器源 IBL 分支按 asm 542-544 解码 pow(rgb*a*16,2)，且 cube 纹理 colorSpace=NoColorSpace；源六面 alpha mean 0.015(qiangpi)/0.028(jiayuan02a) 即 RGBM 乘子。最初只输出 RGB（a=1.0）⇒ 解码亮约 4400×，读数 p50=0.7898/>0.85=40.90% 属**编码假象**。",
      "decode_in_viewer": "q_L = pow(rgb * a * 16.0, 2.0)   /* asm 542-544 */",
      "texture_colorSpace": "NoColorSpace (viewer L1799)",
      "encode": "s = sqrt(srgb_to_linear(rgb))/16 ; a = clamp(max_ch(s),1/255,1) ; rgb_out = s/a",
      "target_radiance": "L = srgb_to_linear(交付 sRGB 面片值) —— 物理线性化，非为凑指标",
      "verified": "RGBM PNG 回读解码与目标 L 的最大绝对误差见各面 decode_roundtrip_max_abs_err"
    },
    "summary": {
      "cube_mean_rgb": [
        0.0667,
        0.1745,
        0.1715
      ],
      "cube_mean_lum": 0.1514,
      "cube_p50_lum": 0.1327,
      "cube_p95_lum": 0.315
    },
    "no_photometric_gain": true,
    "limitations": [
      "由单张 LDR 显示用背板重建 ⇒ 只保留大域颜色/亮度结构（暗青绿墙、顶灯带、地面格栅），不复原真实几何",
      "±X/±Y/−Y 面是源图对应色带的平面缩放，**不是**真实拍摄方向 ⇒ 反射中的具体形状不可当真",
      "源为已 tone-mapped 的显示用背板，直接当线性 HDR 环境使用 ⇒ 能量偏低",
      "未使用 .cube 容器的六面朝向/基变换证据 ⇒ 面朝向按 three.js 约定，未与引擎采样约定对齐"
    ]
  },
  {
    "name": "custom_bright_20260921",
    "superseded_by": "custom_bright_snow_20260921",
    "superseded_note": "已被 custom_bright_snow_20260921 取代：实测金属区发黑由 cube 中 L>1 纹素占比决定，本项（基于 gdansk_shipyard_buildings02、只抬底、会削弱 HDR 亮点）对金属帮助有限。保留仅为可比对，不再是默认。",
    "status": "self_authored_approximate",
    "authority": "user_authorized_manual_20260921",
    "fidelity": "approximate",
    "is_game_asset": false,
    "derived_from": [
      "assets/3d/weapon_skin/_shared/cubes/gdansk_shipyard_buildings02 (cube sha256:d28948b4cffe512ae170fa142cb28e3e556967466ea25700bf117d1b236571e3, sha16:d28948b4cffe512a, container 0000.gpk row 11706, B8G8R8A8_UNORM 128x128 mips=8) 六面 mip0 PNG —— **唯一**像素来源（未混任何其它 cube）"
    ],
    "method": "逐面：源解码辐射 L_src = (rgb_src * a_src * 16)^2（asm 542-544）→ 自造标定 L_new = sqrt((K*L_src)^2 + L_FLOOR^2)（K=0.57525 由「六面 p50 ≤ 0.45」反解取最大；L_FLOOR=0.12 为逐像素下界）→ 反解 RGBM：q=sqrt(L_new), s=q/16, M=ceil_8bit(max_c s_c), rgb_out=s/M。未混其它 cube（实测 gdansk 六面无大面积近黑 ⇒ 规格允许的「补面」不需要）；未做任何图像域增益/模糊/裁剪整形。",
    "note": "**自造近似、非游戏资产**；源侧**无选择器** ⇒ 默认改用它属**产品选择**（authority=product_choice_20260921）；目的 = **消除金属镜面方向的纯黑**。像素基底取自游戏资产 gdansk_shipyard_buildings02 六面，但**辐射标定（增益 K + 抬底 L_FLOOR + RGBM alpha 反解）是本写手自造的** —— 不得作为「游戏实际使用该环境」的证据，不得标成 source_verified，不得顶替源资产，也不得计入「源数据驱动」目标。",
    "logical": "self_authored://custom_bright_20260921",
    "container": null,
    "row": null,
    "sha16": null,
    "dims": "128x128",
    "format": "PNG RGBA RGBM(a=multiplier) — 与源 B8G8R8A8_UNORM + asm542-544 解码约定对齐",
    "n_faces": 6,
    "resolve": "self_authored",
    "in_skin": false,
    "identity_basis": "self_authored_approximate — 无容器/无哈希命中，**不是**源 cube",
    "selectable": true,
    "group": "self_authored（自造近似，非游戏资产）",
    "requires_status_whitelist_extend": true,
    "cubemap_order": [
      "+X",
      "-X",
      "+Y",
      "-Y",
      "+Z",
      "-Z"
    ],
    "faces": [
      "assets/3d/weapon_skin/_shared/cubes/custom_bright_20260921/rgbm/custom_bright_20260921_f0_m0.png",
      "assets/3d/weapon_skin/_shared/cubes/custom_bright_20260921/rgbm/custom_bright_20260921_f1_m0.png",
      "assets/3d/weapon_skin/_shared/cubes/custom_bright_20260921/rgbm/custom_bright_20260921_f2_m0.png",
      "assets/3d/weapon_skin/_shared/cubes/custom_bright_20260921/rgbm/custom_bright_20260921_f3_m0.png",
      "assets/3d/weapon_skin/_shared/cubes/custom_bright_20260921/rgbm/custom_bright_20260921_f4_m0.png",
      "assets/3d/weapon_skin/_shared/cubes/custom_bright_20260921/rgbm/custom_bright_20260921_f5_m0.png"
    ],
    "faces_srgb": [
      "assets/3d/weapon_skin/_shared/cubes/custom_bright_20260921/faces/custom_bright_20260921_f0_m0.png",
      "assets/3d/weapon_skin/_shared/cubes/custom_bright_20260921/faces/custom_bright_20260921_f1_m0.png",
      "assets/3d/weapon_skin/_shared/cubes/custom_bright_20260921/faces/custom_bright_20260921_f2_m0.png",
      "assets/3d/weapon_skin/_shared/cubes/custom_bright_20260921/faces/custom_bright_20260921_f3_m0.png",
      "assets/3d/weapon_skin/_shared/cubes/custom_bright_20260921/faces/custom_bright_20260921_f4_m0.png",
      "assets/3d/weapon_skin/_shared/cubes/custom_bright_20260921/faces/custom_bright_20260921_f5_m0.png"
    ],
    "faces_encoding": "rgbm",
    "face_sha256_rgbm": [
      "f34ca3cb3a9e49f33dd06370e232a8b18bd257d1eabac772e0536ae5f0a83899",
      "4836558badcc2eb991bcb26482639ca585a5038875c482e0d6884b34ba714e63",
      "1759b3116866edfdf7fdae0a6e62526e821f9fd5bada372b19f3b1431dfc9c84",
      "c279eaa54eb8c2b8ffce4d8d89408433dab9ad90f78708aeb9e11e144187480e",
      "e9b2f7cb8dd50b98bb910cde1d7786fa8097478c7e9a926be21227fa2fd002f4",
      "16d9d9b3656c53dfd535475647fbe414ea66e317783cc9f7a41f30e09d355708"
    ],
    "face_sha256_srgb": [
      "6d86aaf1895cc98eee538984f0876ec8ad209187d5a3d47556016c7335610ff0",
      "6f2377972648ab351820122d5eeccbfaf594e8e91f8df970c9acd18e41f3082f",
      "5c12f55c69ef10a1b01e5121cbfdbcd1d6a6595c2ad339e2f3f0f283f70c33ac",
      "283aeccedfadb7c769ec8514efbe32563c81b6bce27aca5f30bc0053f729f59c",
      "7128755e815a58418a260258c64561df344982b9a706bbca524b76b1c52f6c53",
      "cc67e9362e193920335263bb99f0b2b119354c3917397434e43719ffd23fd1a0"
    ],
    "source_face_sha256": [
      "7b82819e724ad5417fe02be34cba16d93416907d9ae9fa58c4e3a853d40ca465",
      "148ba40aa8bb9cca09806016911fa99072cccd7f4fdc41095b4c1f29b3fc76fe",
      "dfa4a8bc35952b9acb072f23c4c4715e5e357c30778b79ae3cfa615d44665264",
      "9828cd2ed58d889b1be1b74bd2d2460a1750de25784bf30f77e3c431df9e3920",
      "9c94dbff535c0446f14e2570853e72900964ae6b13779f99d7f158c42cf3720d",
      "f8c3080987ec88e41b6c952be770fb8c67ee10d55dec813f2fae774eed82b180"
    ],
    "rgbm_encoding": {
      "decode_in_viewer": "q_L = pow(rgb * a * 16.0, 2.0)   /* asm 542-544 */",
      "texture_colorSpace": "NoColorSpace (viewer L1799/L2021)",
      "encode": "q = sqrt(L_new) ; s = q/16 ; M = ceil_8bit(max_c s_c) ; rgb_out = s / M",
      "alpha_is_rgbm_multiplier": true,
      "ceil_not_round_why": "M 取 ceil 到 8bit 网格 ⇒ M ≥ max_c s_c 恒成立 ⇒ rgb_out ≤ 1 **无需裁剪**，回读误差只剩 rgb_out 的 8bit 量化（见各面 decode_roundtrip_max_abs_err，~1e-3 量级）。",
      "why_alpha_matters": "源 IBL 分支解码 pow(rgb*a*16,2)，alpha 就是 RGBM 乘子 M。实测 qiangpi alpha≈0.015 ⇒ 解码辐射≈0.05 ⇒ 金属镜面发黑。"
    },
    "radiance_calibration": {
      "is_self_authored": true,
      "formula": "L_new = sqrt( (K * L_src)^2 + L_FLOOR^2 )   逐通道；L_src = (rgb_src * a_src * 16)^2",
      "K": 0.57525,
      "K_rule": "取满足「六面解码 p50 全部 ≤ 0.45」的**最大** K —— 即在规格给定区间内把有效辐射顶到最高。二分反解，约束单调。",
      "L_FLOOR": 0.12,
      "L_FLOOR_rule": "软抬底（quadrature）：保证 L_new ≥ 0.12 对**每一像素**成立 ⇒ 任何方向都不黑。",
      "target_band_p50": [
        0.25,
        0.45
      ],
      "floor_dominated_px_pct_per_face": [
        43.469,
        31.598,
        15.002,
        0.0,
        42.261,
        33.02
      ],
      "no_image_domain_gain": "未施加任何图像域增益/对比度/模糊/裁剪整形；也未混其它 cube （实测 gdansk 六面均无大面积近黑 ⇒ 规格允许的「补面」不需要）。",
      "forbidden_touched": "未改 exposure / ACES / bloom / 灯 / 环境强度 / lighting_approx 既有值。"
    },
    "per_face_alpha": [
      {
        "axis": "+X",
        "alpha_M_min": 0.023529,
        "alpha_M_p50": 0.035294,
        "alpha_M_max": 0.054902,
        "alpha_M_byte_min": 6,
        "alpha_M_byte_p50": 9,
        "alpha_M_byte_max": 14,
        "decoded_L_p50": 0.30651,
        "decoded_L_min": 0.12037,
        "source_decoded_L_p50": 0.489709,
        "source_alpha_p50": 0.047059,
        "floor_dominated_px_pct": 43.469
      },
      {
        "axis": "-X",
        "alpha_M_min": 0.023529,
        "alpha_M_p50": 0.035294,
        "alpha_M_max": 0.105882,
        "alpha_M_byte_min": 6,
        "alpha_M_byte_p50": 9,
        "alpha_M_byte_max": 27,
        "decoded_L_p50": 0.308967,
        "decoded_L_min": 0.12037,
        "source_decoded_L_p50": 0.493851,
        "source_alpha_p50": 0.047059,
        "floor_dominated_px_pct": 31.598
      },
      {
        "axis": "+Y",
        "alpha_M_min": 0.023529,
        "alpha_M_p50": 0.05098,
        "alpha_M_max": 0.713725,
        "alpha_M_byte_min": 6,
        "alpha_M_byte_p50": 13,
        "alpha_M_byte_max": 182,
        "decoded_L_p50": 0.449767,
        "decoded_L_min": 0.12037,
        "source_decoded_L_p50": 0.748505,
        "source_alpha_p50": 0.066667,
        "floor_dominated_px_pct": 15.002
      },
      {
        "axis": "-Y",
        "alpha_M_min": 0.035294,
        "alpha_M_p50": 0.035294,
        "alpha_M_max": 0.035294,
        "alpha_M_byte_min": 9,
        "alpha_M_byte_p50": 9,
        "alpha_M_byte_max": 9,
        "decoded_L_p50": 0.308967,
        "decoded_L_min": 0.308967,
        "source_decoded_L_p50": 0.493851,
        "source_alpha_p50": 0.047059,
        "floor_dominated_px_pct": 0.0
      },
      {
        "axis": "+Z",
        "alpha_M_min": 0.023529,
        "alpha_M_p50": 0.035294,
        "alpha_M_max": 0.309804,
        "alpha_M_byte_min": 6,
        "alpha_M_byte_p50": 9,
        "alpha_M_byte_max": 79,
        "decoded_L_p50": 0.308967,
        "decoded_L_min": 0.12037,
        "source_decoded_L_p50": 0.493851,
        "source_alpha_p50": 0.047059,
        "floor_dominated_px_pct": 42.261
      },
      {
        "axis": "-Z",
        "alpha_M_min": 0.023529,
        "alpha_M_p50": 0.035294,
        "alpha_M_max": 0.058824,
        "alpha_M_byte_min": 6,
        "alpha_M_byte_p50": 9,
        "alpha_M_byte_max": 15,
        "decoded_L_p50": 0.308967,
        "decoded_L_min": 0.12037,
        "source_decoded_L_p50": 0.493851,
        "source_alpha_p50": 0.047059,
        "floor_dominated_px_pct": 33.02
      }
    ],
    "summary": {
      "decoded_L_p50_per_face": [
        0.30651,
        0.308967,
        0.449767,
        0.308967,
        0.308967,
        0.308967
      ],
      "decoded_L_min_per_face": [
        0.12037,
        0.12037,
        0.12037,
        0.308967,
        0.12037,
        0.12037
      ],
      "decoded_L_p50_min_face": 0.30651,
      "decoded_L_p50_max_face": 0.449767,
      "decoded_L_min_over_all": 0.12037,
      "src_decoded_L_p50_per_face": [
        0.489709,
        0.493851,
        0.748505,
        0.493851,
        0.493851,
        0.493851
      ],
      "K_applied_to_source_p50_ratio": 0.4095,
      "band_p50": [
        0.25,
        0.45
      ],
      "all_faces_p50_in_band": true,
      "all_pixels_at_or_above_floor": true,
      "near_black_px_pct_all_faces": 0.0,
      "source_near_black_luma_pct_all_faces": 0.0,
      "source_dark_L_lt_0.01_pct_per_face": [
        2.8503,
        1.9592,
        0.0,
        0.0,
        5.3833,
        0.6042
      ]
    },
    "limitations": [
      "像素基底是**游戏资产**，但**辐射标定（K / 抬底 / alpha）是自造的** ⇒ 整体为自造近似，非源环境。",
      "平滑抬底把 L<0.12 的深黑方向抬成**近中性灰**（逐通道取同一底）⇒ 这些方向**丢失细节、趋于消色差**；这是「任何方向都不黑」的必然代价，已如实登记（见 floor_dominated_px_pct_per_face）。",
      "源 +Y 面解码辐射最大到 224.9（源里有极亮的灯/太阳像素）；本 cube 保留之（经 K 衰减），故仍是高动态范围环境，不是「均匀灰箱」。",
      "面朝向沿用源 cube 的 six-face 顺序（+X,-X,+Y,-Y,+Z,-Z，与 three.js CubeTextureLoader 一致），未与引擎采样基变换重新对齐。",
      "该 cube **不是**游戏实际使用的环境；只是为消除金属镜面纯黑而自造的显示用近似环境。"
    ]
  },
  {
    "name": "custom_bright_snow_20260921",
    "status": "self_authored_approximate",
    "authority": "user_authorized_manual_20260921",
    "fidelity": "approximate",
    "is_game_asset": false,
    "derived_from": [
      "assets/3d/weapon_skin/_shared/cubes/snow (cube sha256:a974343d3689cc1a729d03edc05c35a9700e19f78cc6a1a7d1ffda117d269a55, sha16:a974343d3689cc1a, logical common\\env_map\\snow.cube, container 0000.gpk row 11915, 128x128) 的 **f0/f1/f2/f4/f5 五面** mip0 PNG 为像素基底；**f3(−Y) 面由本写手用 +Y(f2) 天花垂直镜像 + 高斯 σ=10 + 压暗 ×0.85 自造补出**（该面在源容器里全黑：maxRGB=0 / maxA=1 ⇒ 解码 100% 近黑）。"
    ],
    "method": "逐面：源解码辐射 L_src = (rgb_src * a_src * 16)^2（asm 542-544，已由游戏 DXBC 逐指令证实） → 自造软抬底 L_new = sqrt(L_src^2 + a^2)，**增益恒为 1.0（不加任何增益）**，a=0.0505（由「逐面近黑 L<0.05 占比 == 0」反解；因 luma 是各通道凸组合，min_channel(L_new)=a，再留 8bit 量化余量） → 反解 RGBM：q=sqrt(L_new), s=q/16, M=ceil_8bit(max_c s_c), rgb_out=s/M。f3(−Y)：+Y 天花**垂直镜像** → 逐通道高斯模糊 σ=10 → 均匀压暗 ×0.85（保留 HDR 感，不做平灰箱）。未混任何其它 cube 的像素；未做任何图像域增益/对比度/裁剪整形（唯一整形是 f3 的模糊与压暗）。",
    "note": "**自造近似、非游戏资产**；源侧**无选择器** ⇒ 默认改用它属**产品选择**（authority=product_choice_20260921）；目的 = **消除武器金属镜面发黑**。像素基底取自游戏资产 snow 的 f0/f1/f2/f4/f5 五面，**f3(−Y) 面是自造的**（源该面全黑 ⇒ 用 +Y 天花镜像补出），并逐像素加了软抬底 a=0.0505（反解 RGBM 的 M）。**不得**作为「游戏实际使用该环境」的证据，**不得**标成 source_verified，**不得**顶替源资产，也不得计入「源数据驱动」目标。本项**取代**上一版自造基底 custom_bright_20260921（基于 gdansk、只抬底、会削弱 HDR 亮点、对金属帮助有限）。",
    "supersedes": "custom_bright_20260921",
    "logical": "self_authored://custom_bright_snow_20260921",
    "container": null,
    "row": null,
    "sha16": null,
    "dims": "128x128",
    "format": "PNG RGBA RGBM(a=multiplier) — 与源 B8G8R8A8_UNORM + asm542-544 解码约定对齐",
    "n_faces": 6,
    "resolve": "self_authored",
    "in_skin": false,
    "identity_basis": "self_authored_approximate — 无容器/无哈希命中，**不是**源 cube",
    "selectable": true,
    "group": "self_authored（自造近似，非游戏资产）",
    "requires_status_whitelist_extend": true,
    "cubemap_order": [
      "+X",
      "-X",
      "+Y",
      "-Y",
      "+Z",
      "-Z"
    ],
    "faces": [
      "assets/3d/weapon_skin/_shared/cubes/custom_bright_snow_20260921/rgbm/custom_bright_snow_20260921_f0_m0.png",
      "assets/3d/weapon_skin/_shared/cubes/custom_bright_snow_20260921/rgbm/custom_bright_snow_20260921_f1_m0.png",
      "assets/3d/weapon_skin/_shared/cubes/custom_bright_snow_20260921/rgbm/custom_bright_snow_20260921_f2_m0.png",
      "assets/3d/weapon_skin/_shared/cubes/custom_bright_snow_20260921/rgbm/custom_bright_snow_20260921_f3_m0.png",
      "assets/3d/weapon_skin/_shared/cubes/custom_bright_snow_20260921/rgbm/custom_bright_snow_20260921_f4_m0.png",
      "assets/3d/weapon_skin/_shared/cubes/custom_bright_snow_20260921/rgbm/custom_bright_snow_20260921_f5_m0.png"
    ],
    "faces_srgb": [
      "assets/3d/weapon_skin/_shared/cubes/custom_bright_snow_20260921/faces/custom_bright_snow_20260921_f0_m0.png",
      "assets/3d/weapon_skin/_shared/cubes/custom_bright_snow_20260921/faces/custom_bright_snow_20260921_f1_m0.png",
      "assets/3d/weapon_skin/_shared/cubes/custom_bright_snow_20260921/faces/custom_bright_snow_20260921_f2_m0.png",
      "assets/3d/weapon_skin/_shared/cubes/custom_bright_snow_20260921/faces/custom_bright_snow_20260921_f3_m0.png",
      "assets/3d/weapon_skin/_shared/cubes/custom_bright_snow_20260921/faces/custom_bright_snow_20260921_f4_m0.png",
      "assets/3d/weapon_skin/_shared/cubes/custom_bright_snow_20260921/faces/custom_bright_snow_20260921_f5_m0.png"
    ],
    "faces_encoding": "rgbm",
    "face_sha256_rgbm": [
      "5f3fb394dc238cfd0bf8447082d5a933f51daf5e2b81e124ed8cb149ec72f5a0",
      "8a0d31d8eca7dd684524620d0872158d1257226361348480a039ad5373d1967d",
      "0a0ee9e99c4a23d4606cadad8b6850b5d9421ec0b673ea88853f5ba8bda23f0b",
      "3087e103a3638754c0958c4da6d79a3e5d5e47fb03d57667370e4eb24cbb6309",
      "6fe6d749e24e22df18c0021283b2864142ffe1085cf4ec4548acbde9fe541663",
      "f9087fa9b928073f9dd7fe60f0c338130bb23eb771c4a9e20a821e2304d32ec6"
    ],
    "face_sha256_srgb": [
      "c2a901b5ec2f3b1e2b8d11763ecde74e16bc4d36de8dd1d4c90d3ba17520f7e1",
      "4791cf5b39ad0b5f814c6e43a028c56a60025bd01014b676786d466b9f4642e1",
      "08f44d2d9ba05c3d02c1a649fd87ea43312a2b0f18096dd0c1009022f97d7938",
      "da5db3eaea9cad2e2d4b56da10179f93e5d94190d9d3b9e67bd462db4a2d86ff",
      "19eb2fbe2519021b5f7d046a3c88633c7a83678b593f79ebb3d4e8251765e929",
      "640162b44cc33881d80c311089a4eb430451d23e15b1ebec286ac22a3240743f"
    ],
    "source_face_sha256": [
      "88d496966b101abeaff2aa5db2ce857a918819831b36e5ebf8bbd95c3d0500f4",
      "bb8fbf565620a08afdab4c16ee5ce4e5f0daee292205e2a9fba90ac926f0e27e",
      "0df874f659cfd2a56204a73210ccfa832951b614474c17ade4b60d71339f001d",
      "a37162d1ad434720de04ea1774d259f618b361ce58b5e20b489d88cfe26ca274",
      "c27028072de94554b19455be51f669439270877c9b26045e782433c0a5441278",
      "c7aa379cca910ae69a572b9e6920df60be28509a4950df6adec09fc06474180b"
    ],
    "source_face_sha256_note": "f0/f1/f2/f4/f5 = snow 源面原件哈希；f3 = 源 snow_f3 的哈希（该面全黑，本项的 f3 是自造补面，见 per_face[3].is_self_authored_fill）",
    "rgbm_encoding": {
      "decode_in_viewer": "q_L = pow(rgb * a * 16.0, 2.0)   /* asm 542-544 */",
      "texture_colorSpace": "NoColorSpace (viewer L2001/L5106/L5223)",
      "encode": "q = sqrt(L_new) ; s = q/16 ; M = ceil_8bit(max_c s_c) ; rgb_out = s / M",
      "alpha_is_rgbm_multiplier": true,
      "ceil_not_round_why": "M 取 ceil 到 8bit 网格 ⇒ M ≥ max_c s_c 恒成立 ⇒ rgb_out ≤ 1 **无需裁剪**，回读误差只剩 rgb_out 的 8bit 量化。",
      "why_alpha_matters": "源 IBL 分支解码 pow(rgb*a*16,2)，alpha 就是 RGBM 乘子 M。实测 qiangpi alpha≈0.015 ⇒ 解码辐射≈0.05 ⇒ 金属镜面发黑。"
    },
    "radiance_calibration": {
      "is_self_authored": true,
      "formula": "L_new = sqrt( L_src^2 + a^2 )   逐通道；L_src = (rgb_src * a_src * 16)^2",
      "GAIN": 1.0,
      "GAIN_rule": "**恒为 1.0，不加任何增益** —— 对源里已经亮的像素逐值不动。这是对「自造近似」最小侵入的选择，避免\"靠整体变亮换金属\"。",
      "L_FLOOR_A": 0.0505,
      "L_FLOOR_A_rule": "a 由硬约束反解：逐面「近黑 L<0.05 占比 == 0」。luma 是各通道的凸组合 ⇒ min_channel(L_new) = a ⇒ a ≥ 0.05 数学上即恒成立。但 RGBM 落 8bit 后回读会略降：实测 a=0.0500 回读 min=0.049917（差 8.3e-5）、a=0.047619 回读 min=0.0476 ⇒ 取 a = 0.0505（回读 min=0.050358 > 0.05，余量 0.72%），刚好覆盖 8bit 量化误差、不浪费能量。",
      "f3_fill": {
        "method": "+Y(f2) 垂直镜像 → 逐通道高斯 σ=10.0 → 均匀压暗 ×0.85",
        "sigma": 10.0,
        "dim": 0.85,
        "src_f3_sha256": "a37162d1ad434720de04ea1774d259f618b361ce58b5e20b489d88cfe26ca274",
        "src_f3_all_black": true,
        "built_f3_L_min": 0.320769,
        "built_f3_L_p50": 0.743295,
        "built_f3_gt1_pct": 20.8374
      },
      "no_image_domain_gain": "未施加任何图像域增益/对比度/裁剪整形（g 恒 1.0）。唯一的图像域整形是 f3 补面的高斯模糊与均匀压暗。",
      "forbidden_touched": "未改 exposure / ACES / bloom / 灯 / 环境强度 / lighting_approx 既有值。"
    },
    "per_face_alpha": [
      {
        "axis": "+X",
        "face": 0,
        "is_self_authored_fill": false,
        "alpha_M_min": 0.015686,
        "alpha_M_p50": 0.031373,
        "alpha_M_max": 0.133333,
        "alpha_M_byte_min": 4,
        "alpha_M_byte_p50": 8,
        "alpha_M_byte_max": 34,
        "decoded_L_min": 0.050358,
        "decoded_L_p50": 0.214427,
        "dark_L_lt_0.05_pct": 0.0,
        "gt1_pct": 22.644,
        "gt085_pct": 28.6133,
        "source_face_sha256": "88d496966b101abeaff2aa5db2ce857a918819831b36e5ebf8bbd95c3d0500f4",
        "source_decoded_L_p50": 0.208626,
        "source_dark_L_lt_0.05_pct": 49.2188,
        "source_gt1_pct": 22.6501,
        "source_is_all_black": false
      },
      {
        "axis": "-X",
        "face": 1,
        "is_self_authored_fill": false,
        "alpha_M_min": 0.015686,
        "alpha_M_p50": 0.031373,
        "alpha_M_max": 0.247059,
        "alpha_M_byte_min": 4,
        "alpha_M_byte_p50": 8,
        "alpha_M_byte_max": 63,
        "decoded_L_min": 0.050358,
        "decoded_L_p50": 0.204069,
        "dark_L_lt_0.05_pct": 0.0,
        "gt1_pct": 17.5964,
        "gt085_pct": 19.8914,
        "source_face_sha256": "bb8fbf565620a08afdab4c16ee5ce4e5f0daee292205e2a9fba90ac926f0e27e",
        "source_decoded_L_p50": 0.198163,
        "source_dark_L_lt_0.05_pct": 49.2188,
        "source_gt1_pct": 17.5964,
        "source_is_all_black": false
      },
      {
        "axis": "+Y",
        "face": 2,
        "is_self_authored_fill": false,
        "alpha_M_min": 0.027451,
        "alpha_M_p50": 0.078431,
        "alpha_M_max": 0.160784,
        "alpha_M_byte_min": 7,
        "alpha_M_byte_p50": 20,
        "alpha_M_byte_max": 41,
        "decoded_L_min": 0.15299,
        "decoded_L_p50": 0.88904,
        "dark_L_lt_0.05_pct": 0.0,
        "gt1_pct": 39.3005,
        "gt085_pct": 53.9917,
        "source_face_sha256": "0df874f659cfd2a56204a73210ccfa832951b614474c17ade4b60d71339f001d",
        "source_decoded_L_p50": 0.88904,
        "source_dark_L_lt_0.05_pct": 0.0,
        "source_gt1_pct": 39.2761,
        "source_is_all_black": false
      },
      {
        "axis": "-Y",
        "face": 3,
        "is_self_authored_fill": true,
        "alpha_M_min": 0.043137,
        "alpha_M_p50": 0.07451,
        "alpha_M_max": 0.098039,
        "alpha_M_byte_min": 11,
        "alpha_M_byte_p50": 19,
        "alpha_M_byte_max": 25,
        "decoded_L_min": 0.32508,
        "decoded_L_p50": 0.746466,
        "dark_L_lt_0.05_pct": 0.0,
        "gt1_pct": 21.0571,
        "gt085_pct": 35.8337,
        "source_face_sha256": "a37162d1ad434720de04ea1774d259f618b361ce58b5e20b489d88cfe26ca274",
        "source_decoded_L_p50": 0.0,
        "source_dark_L_lt_0.05_pct": 100.0,
        "source_gt1_pct": 0.0,
        "source_is_all_black": true
      },
      {
        "axis": "+Z",
        "face": 4,
        "is_self_authored_fill": false,
        "alpha_M_min": 0.015686,
        "alpha_M_p50": 0.035294,
        "alpha_M_max": 0.129412,
        "alpha_M_byte_min": 4,
        "alpha_M_byte_p50": 9,
        "alpha_M_byte_max": 33,
        "decoded_L_min": 0.050358,
        "decoded_L_p50": 0.256512,
        "dark_L_lt_0.05_pct": 0.0,
        "gt1_pct": 35.7361,
        "gt085_pct": 40.5396,
        "source_face_sha256": "c27028072de94554b19455be51f669439270877c9b26045e782433c0a5441278",
        "source_decoded_L_p50": 0.251437,
        "source_dark_L_lt_0.05_pct": 49.2188,
        "source_gt1_pct": 35.7483,
        "source_is_all_black": false
      },
      {
        "axis": "-Z",
        "face": 5,
        "is_self_authored_fill": false,
        "alpha_M_min": 0.015686,
        "alpha_M_p50": 0.031373,
        "alpha_M_max": 0.133333,
        "alpha_M_byte_min": 4,
        "alpha_M_byte_p50": 8,
        "alpha_M_byte_max": 34,
        "decoded_L_min": 0.050358,
        "decoded_L_p50": 0.206467,
        "dark_L_lt_0.05_pct": 0.0,
        "gt1_pct": 6.9824,
        "gt085_pct": 8.783,
        "source_face_sha256": "c7aa379cca910ae69a572b9e6920df60be28509a4950df6adec09fc06474180b",
        "source_decoded_L_p50": 0.199735,
        "source_dark_L_lt_0.05_pct": 49.2188,
        "source_gt1_pct": 6.9824,
        "source_is_all_black": false
      }
    ],
    "summary": {
      "decoded_L_p50_per_face": [
        0.214427,
        0.204069,
        0.88904,
        0.746466,
        0.256512,
        0.206467
      ],
      "decoded_L_min_per_face": [
        0.050358,
        0.050358,
        0.15299,
        0.32508,
        0.050358,
        0.050358
      ],
      "dark_L_lt_0.05_pct_per_face": [
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0
      ],
      "gt1_pct_per_face": [
        22.644,
        17.5964,
        39.3005,
        21.0571,
        35.7361,
        6.9824
      ],
      "gt1_pct_cube": 23.8861,
      "gt1_pct_cube_source_snow": 20.3756,
      "gt1_ge_source_snow": true,
      "decoded_L_mean_cube": 0.656212,
      "decoded_L_mean_cube_source_snow": 0.504959,
      "decoded_L_min_over_all_faces": 0.050358,
      "dark_L_lt_0.05_pct_worst_face": 0.0,
      "all_faces_dark_zero": true,
      "all_faces_min_gt_0.05": true,
      "source_snow_f3_all_black": true
    },
    "limitations": [
      "**f3(−Y) 面是自造的**（源该面在容器里全黑）⇒ 六面里有一面不是源像素，整体为自造近似。",
      "软抬底把 L<0.05 的深黑方向抬成**近中性灰**（逐通道取同一底）⇒ 这些方向**丢失细节、趋于消色差**；这是「任何方向都不黑」的必然代价，已如实登记（见 dark_L_lt_0.05_pct_per_face 与逐面 min）。",
      "本 cube 启用 f3 补面后**整体均值必然高于源 snow**（0.5050 → 0.6562），因为源 snow 的 −Y 面是纯黑(贡献 0)、补面后该面贡献真实辐射。这部分升亮**不是**人为增益，而是\"补全一个全黑面\"的直接后果，已如实登记。",
      "\"L>1 占比决定金属发黑\" 这条是 GI2 终报给出的**相关性**结论，未做逐反射方向的半球/镜面方向积分证明；本 cube 的达标线按该相关性口径验收。",
      "面朝向沿用源 cube 的 six-face 顺序（+X,-X,+Y,-Y,+Z,-Z，与 three.js CubeTextureLoader 一致），未与引擎采样基变换重新对齐。",
      "该 cube **不是**游戏实际使用的环境；只是为消除金属镜面发黑而自造的显示用近似环境。"
    ],
    "builder_script": "_shared/cubes/custom_bright_snow_20260921/_build_snow_cube.py"
  }
];

  var API = {
    version: '20260920',
    kind: 'custom_self_authored',
    schema: 'weapon_skin_cubes_custom/v1',
    merges_into: 'WIKI_WEAPON_SKIN_CUBES (schema weapon_skin_cubes/v1)',
    /** ★ 全局诚实标注：本清单内所有 cube 均为自造近似，非游戏资产 */
    disclaimer: '**自造近似立方体，非游戏资产**。仅用于观察环境反射对观感的影响；不得作为「游戏实际使用该环境」的证据，也不得计入「源数据驱动」目标。',
    cubes: CUSTOM_CUBES,
    get: function (name) {
      var n = String(name == null ? '' : name).trim();
      for (var i = 0; i < CUSTOM_CUBES.length; i++) { if (CUSTOM_CUBES[i].name === n) return CUSTOM_CUBES[i]; }
      return null;
    },
    names: function () { return CUSTOM_CUBES.map(function (c) { return c.name; }); },
    isCustom: function (name) { return !!this.get(name); },
    /** 喂给查看器的六面 URL（RGBM 编码档），顺序 +X,-X,+Y,-Y,+Z,-Z */
    viewerFaces: function (name) { var c = this.get(name); return c ? c.faces.slice() : null; },
    /** 人眼看的六面 URL（sRGB 档），**不要**喂查看器 */
    displayFaces: function (name) { var c = this.get(name); return c ? c.faces_srgb.slice() : null; },
    /** 并入主清单：只追加，不覆盖同名条目（避免踩到真源 cube） */
    mergeInto: function (main) {
      if (!main || typeof main !== 'object') return { merged: 0, reason: 'no main manifest' };
      if (!Array.isArray(main.cubes)) main.cubes = [];
      var have = {};
      for (var i = 0; i < main.cubes.length; i++) { if (main.cubes[i] && main.cubes[i].name) have[main.cubes[i].name] = 1; }
      var n = 0;
      for (var j = 0; j < CUSTOM_CUBES.length; j++) {
        var c = CUSTOM_CUBES[j];
        if (have[c.name]) continue;
        var copy = JSON.parse(JSON.stringify(c));
        copy.origin = 'weapon_skin_cubes_custom.js';
        copy.is_game_asset = false;
        main.cubes.push(copy);
        n++;
      }
      if (!main.custom_merged) {
        main.custom_merged = { count: 0, source: 'weapon_skin_cubes_custom.js', disclaimer: API.disclaimer };
      }
      main.custom_merged.count += n;
      return { merged: n, total: main.cubes.length };
    }
  };

  if (typeof window !== 'undefined') {
    window.WikiWeaponSkinCubesCustom = API;
    /* 若主清单已先加载，顺手合并（幂等：同名不重复追加） */
    try { if (window.WIKI_WEAPON_SKIN_CUBES) API.mergeInto(window.WIKI_WEAPON_SKIN_CUBES); } catch (e) {}
  }
})();
