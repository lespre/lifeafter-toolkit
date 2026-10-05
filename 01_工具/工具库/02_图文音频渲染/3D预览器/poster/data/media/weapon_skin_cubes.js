/* weapon_skin_cubes.js — 环境立方体（IBL cube）清册（自动生成，勿手改）
 * 生成：_cubepick_build.py @ 2026-09-20 22:45:40
 * 定位：名字哈希 mm3(path,0x66666666)/mm3(path,0x77777777)；GPK 载荷=block_base+off+20；FPK 载荷=off。
 * status: source_verified=哈希命中且六面全解出 / partial=命中但解码不全 / unresolved=未找到。
 * resolve: skin=优先 <皮肤>/src_cube/faces（接线前既有路径，零回归）；shared=走皮肤无关的 _shared/cubes/<name>/faces。
 * in_skin: 仅作**磁盘观测**（该皮肤 src_cube/faces 下当前是否已有这六面），不参与解析决策。
 * ⚠ 源数据里**没有**「预览该用哪一套 cube」的选择器；本表是取证/对比素材，不代表游戏的选择。
 */
window.WIKI_WEAPON_SKIN_CUBES = {
 "schema": "weapon_skin_cubes/v1",
 "generated_at": "2026-09-20 22:45:40",
 "default": "qiangpi",
 "source_selector": "none",
 "note": "源数据中没有选择器决定预览用哪一套 cube（c159 材质容器各只声明一套；special_preview_model_path 只指 .gim，与 cube 无关）。本表仅供取证/对比，qiangpi 是查看器既有默认档。",
 "counts": {
  "candidates": 56,
  "located": 49,
  "source_verified": 32,
  "partial": 17,
  "unresolved": 7
 },
 "cubes": [
  {
   "name": "basement_boxing_ring",
   "logical": "common\\env_map\\basement_boxing_ring.cube",
   "status": "source_verified",
   "container": "0000.gpk",
   "row": 12303,
   "sha16": "5b461a4733ed6dd5",
   "dims": "128x128",
   "format": "B8G8R8A8_UNORM cubemap mips=8 caps2=0xFE00",
   "n_faces": 6,
   "resolve": "shared",
   "in_skin": true,
   "faces": [
    "assets/3d/weapon_skin/_shared/cubes/basement_boxing_ring/faces/basement_boxing_ring_f0_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/basement_boxing_ring/faces/basement_boxing_ring_f1_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/basement_boxing_ring/faces/basement_boxing_ring_f2_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/basement_boxing_ring/faces/basement_boxing_ring_f3_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/basement_boxing_ring/faces/basement_boxing_ring_f4_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/basement_boxing_ring/faces/basement_boxing_ring_f5_m0.png"
   ],
   "is_default": false,
   "provenance": [
    "known_verified"
   ]
  },
  {
   "name": "bg61f_light_spherereflectioncapture2",
   "logical": "common\\env_map\\bg61f_light_spherereflectioncapture2.cube",
   "status": "source_verified",
   "container": "0045.gpk",
   "row": 93763,
   "sha16": "8d0047fb56726870",
   "dims": "128x128",
   "format": "B8G8R8A8_UNORM cubemap mips=8 caps2=0xFE00",
   "n_faces": 6,
   "resolve": "shared",
   "in_skin": false,
   "faces": [
    "assets/3d/weapon_skin/_shared/cubes/bg61f_light_spherereflectioncapture2/faces/bg61f_light_spherereflectioncapture2_f0_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/bg61f_light_spherereflectioncapture2/faces/bg61f_light_spherereflectioncapture2_f1_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/bg61f_light_spherereflectioncapture2/faces/bg61f_light_spherereflectioncapture2_f2_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/bg61f_light_spherereflectioncapture2/faces/bg61f_light_spherereflectioncapture2_f3_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/bg61f_light_spherereflectioncapture2/faces/bg61f_light_spherereflectioncapture2_f4_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/bg61f_light_spherereflectioncapture2/faces/bg61f_light_spherereflectioncapture2_f5_m0.png"
   ],
   "is_default": false,
   "provenance": [
    "env_table:PROBE_CUBE_mod_D9AC3FDF0378051F.bin:paired_rgbm"
   ]
  },
  {
   "name": "bg61f_light_spherereflectioncapture_1",
   "logical": "common\\env_map\\bg61f_light_spherereflectioncapture_1.cube",
   "status": "source_verified",
   "container": "0045.gpk",
   "row": 93760,
   "sha16": "8d0047fb56726870",
   "dims": "128x128",
   "format": "B8G8R8A8_UNORM cubemap mips=8 caps2=0xFE00",
   "n_faces": 6,
   "resolve": "shared",
   "in_skin": false,
   "faces": [
    "assets/3d/weapon_skin/_shared/cubes/bg61f_light_spherereflectioncapture_1/faces/bg61f_light_spherereflectioncapture_1_f0_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/bg61f_light_spherereflectioncapture_1/faces/bg61f_light_spherereflectioncapture_1_f1_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/bg61f_light_spherereflectioncapture_1/faces/bg61f_light_spherereflectioncapture_1_f2_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/bg61f_light_spherereflectioncapture_1/faces/bg61f_light_spherereflectioncapture_1_f3_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/bg61f_light_spherereflectioncapture_1/faces/bg61f_light_spherereflectioncapture_1_f4_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/bg61f_light_spherereflectioncapture_1/faces/bg61f_light_spherereflectioncapture_1_f5_m0.png"
   ],
   "is_default": false,
   "provenance": [
    "env_table:PROBE_CUBE_mod_D9AC3FDF0378051F.bin:paired_rgbm"
   ]
  },
  {
   "name": "bonifacio_aragon_stairs",
   "logical": "common\\env_map\\bonifacio_aragon_stairs.cube",
   "status": "source_verified",
   "container": "0000.gpk",
   "row": 12349,
   "sha16": "7ec0d460d432428b",
   "dims": "128x128",
   "format": "B8G8R8A8_UNORM cubemap mips=8 caps2=0xFE00",
   "n_faces": 6,
   "resolve": "shared",
   "in_skin": true,
   "faces": [
    "assets/3d/weapon_skin/_shared/cubes/bonifacio_aragon_stairs/faces/bonifacio_aragon_stairs_f0_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/bonifacio_aragon_stairs/faces/bonifacio_aragon_stairs_f1_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/bonifacio_aragon_stairs/faces/bonifacio_aragon_stairs_f2_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/bonifacio_aragon_stairs/faces/bonifacio_aragon_stairs_f3_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/bonifacio_aragon_stairs/faces/bonifacio_aragon_stairs_f4_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/bonifacio_aragon_stairs/faces/bonifacio_aragon_stairs_f5_m0.png"
   ],
   "is_default": false,
   "provenance": [
    "env_table:PROBE_CUBE_mod_D9AC3FDF0378051F.bin:paired_rgbm"
   ]
  },
  {
   "name": "bonifacio_aragon_stairs_pc",
   "logical": "common\\env_map\\bonifacio_aragon_stairs_pc.cube",
   "status": "partial",
   "container": "0000.gpk",
   "row": 12371,
   "sha16": "ec0e0a031a7be9db",
   "dims": null,
   "format": null,
   "n_faces": 0,
   "resolve": "shared",
   "in_skin": false,
   "faces": [],
   "is_default": false,
   "provenance": [
    "env_table:PROBE_CUBE_mod_BFBE907B687BF2E6.bin:cube_literal"
   ]
  },
  {
   "name": "bonifacio_street",
   "logical": "common\\env_map\\bonifacio_street.cube",
   "status": "source_verified",
   "container": "0000.gpk",
   "row": 12264,
   "sha16": "c0554a4fd5de107a",
   "dims": "128x128",
   "format": "B8G8R8A8_UNORM cubemap mips=8 caps2=0xFE00",
   "n_faces": 6,
   "resolve": "shared",
   "in_skin": false,
   "faces": [
    "assets/3d/weapon_skin/_shared/cubes/bonifacio_street/faces/bonifacio_street_f0_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/bonifacio_street/faces/bonifacio_street_f1_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/bonifacio_street/faces/bonifacio_street_f2_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/bonifacio_street/faces/bonifacio_street_f3_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/bonifacio_street/faces/bonifacio_street_f4_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/bonifacio_street/faces/bonifacio_street_f5_m0.png"
   ],
   "is_default": false,
   "provenance": [
    "env_table:PROBE_CUBE_mod_D9AC3FDF0378051F.bin:paired_rgbm"
   ]
  },
  {
   "name": "bonifacio_street_pc",
   "logical": "common\\env_map\\bonifacio_street_pc.cube",
   "status": "partial",
   "container": "0000.gpk",
   "row": 12431,
   "sha16": "e3eecce5c3d76171",
   "dims": null,
   "format": null,
   "n_faces": 0,
   "resolve": "shared",
   "in_skin": false,
   "faces": [],
   "is_default": false,
   "provenance": [
    "env_table:PROBE_CUBE_mod_BFBE907B687BF2E6.bin:cube_literal"
   ]
  },
  {
   "name": "car_studio01",
   "logical": "common\\env_map\\car_studio01.cube",
   "status": "source_verified",
   "container": "0000.gpk",
   "row": 12132,
   "sha16": "bea649d8525cdc3e",
   "dims": "128x128",
   "format": "B8G8R8A8_UNORM cubemap mips=8 caps2=0xFE00",
   "n_faces": 6,
   "resolve": "shared",
   "in_skin": true,
   "faces": [
    "assets/3d/weapon_skin/_shared/cubes/car_studio01/faces/car_studio01_f0_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/car_studio01/faces/car_studio01_f1_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/car_studio01/faces/car_studio01_f2_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/car_studio01/faces/car_studio01_f3_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/car_studio01/faces/car_studio01_f4_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/car_studio01/faces/car_studio01_f5_m0.png"
   ],
   "is_default": false,
   "provenance": [
    "env_table:PROBE_CUBE_mod_D9AC3FDF0378051F.bin:paired_rgbm",
    "known_verified"
   ]
  },
  {
   "name": "car_studio01_pc",
   "logical": "common\\env_map\\car_studio01_pc.cube",
   "status": "partial",
   "container": "0000.gpk",
   "row": 11866,
   "sha16": "44112167af1384e5",
   "dims": null,
   "format": null,
   "n_faces": 0,
   "resolve": "shared",
   "in_skin": false,
   "faces": [],
   "is_default": false,
   "provenance": [
    "env_table:PROBE_CUBE_mod_BFBE907B687BF2E6.bin:cube_literal"
   ]
  },
  {
   "name": "cave_entry_in_the_forest",
   "logical": "common\\env_map\\cave_entry_in_the_forest.cube",
   "status": "source_verified",
   "container": "0000.gpk",
   "row": 12472,
   "sha16": "5d4ea5f2262e0e94",
   "dims": "128x128",
   "format": "B8G8R8A8_UNORM cubemap mips=8 caps2=0xFE00",
   "n_faces": 6,
   "resolve": "shared",
   "in_skin": false,
   "faces": [
    "assets/3d/weapon_skin/_shared/cubes/cave_entry_in_the_forest/faces/cave_entry_in_the_forest_f0_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/cave_entry_in_the_forest/faces/cave_entry_in_the_forest_f1_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/cave_entry_in_the_forest/faces/cave_entry_in_the_forest_f2_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/cave_entry_in_the_forest/faces/cave_entry_in_the_forest_f3_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/cave_entry_in_the_forest/faces/cave_entry_in_the_forest_f4_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/cave_entry_in_the_forest/faces/cave_entry_in_the_forest_f5_m0.png"
   ],
   "is_default": false,
   "provenance": [
    "env_table:PROBE_CUBE_mod_D9AC3FDF0378051F.bin:paired_rgbm"
   ]
  },
  {
   "name": "cave_entry_in_the_forest_pc",
   "logical": "common\\env_map\\cave_entry_in_the_forest_pc.cube",
   "status": "partial",
   "container": "0000.gpk",
   "row": 12361,
   "sha16": "18f6b4486425fefc",
   "dims": null,
   "format": null,
   "n_faces": 0,
   "resolve": "shared",
   "in_skin": false,
   "faces": [],
   "is_default": false,
   "provenance": [
    "env_table:PROBE_CUBE_mod_BFBE907B687BF2E6.bin:cube_literal"
   ]
  },
  {
   "name": "character_envmap_metal_01",
   "logical": "common\\env_map\\character_envmap_metal_01.cube",
   "status": "source_verified",
   "container": "0000.gpk",
   "row": 12460,
   "sha16": "6edc35915695df34",
   "dims": "128x128",
   "format": "B8G8R8A8_UNORM cubemap mips=8 caps2=0xFE00",
   "n_faces": 6,
   "resolve": "shared",
   "in_skin": true,
   "faces": [
    "assets/3d/weapon_skin/_shared/cubes/character_envmap_metal_01/faces/character_envmap_metal_01_f0_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/character_envmap_metal_01/faces/character_envmap_metal_01_f1_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/character_envmap_metal_01/faces/character_envmap_metal_01_f2_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/character_envmap_metal_01/faces/character_envmap_metal_01_f3_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/character_envmap_metal_01/faces/character_envmap_metal_01_f4_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/character_envmap_metal_01/faces/character_envmap_metal_01_f5_m0.png"
   ],
   "is_default": false,
   "provenance": [
    "known_verified"
   ]
  },
  {
   "name": "clould_weather",
   "logical": "common\\env_map\\clould_weather.cube",
   "status": "source_verified",
   "container": "0000.gpk",
   "row": 11575,
   "sha16": "b99fe3da2a820e41",
   "dims": "128x128",
   "format": "B8G8R8A8_UNORM cubemap mips=8 caps2=0xFE00",
   "n_faces": 6,
   "resolve": "shared",
   "in_skin": false,
   "faces": [
    "assets/3d/weapon_skin/_shared/cubes/clould_weather/faces/clould_weather_f0_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/clould_weather/faces/clould_weather_f1_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/clould_weather/faces/clould_weather_f2_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/clould_weather/faces/clould_weather_f3_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/clould_weather/faces/clould_weather_f4_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/clould_weather/faces/clould_weather_f5_m0.png"
   ],
   "is_default": false,
   "provenance": [
    "env_table:PROBE_CUBE_mod_D9AC3FDF0378051F.bin:paired_rgbm"
   ]
  },
  {
   "name": "clould_weather_pc",
   "logical": "common\\env_map\\clould_weather_pc.cube",
   "status": "partial",
   "container": "0000.gpk",
   "row": 12378,
   "sha16": "e29eaa04c7f05400",
   "dims": null,
   "format": null,
   "n_faces": 0,
   "resolve": "shared",
   "in_skin": false,
   "faces": [],
   "is_default": false,
   "provenance": [
    "env_table:PROBE_CUBE_mod_BFBE907B687BF2E6.bin:cube_literal"
   ]
  },
  {
   "name": "corsica_beach",
   "logical": "common\\env_map\\corsica_beach.cube",
   "status": "source_verified",
   "container": "0000.gpk",
   "row": 12427,
   "sha16": "f4e0e2f15b8e2eec",
   "dims": "128x128",
   "format": "B8G8R8A8_UNORM cubemap mips=8 caps2=0xFE00",
   "n_faces": 6,
   "resolve": "shared",
   "in_skin": false,
   "faces": [
    "assets/3d/weapon_skin/_shared/cubes/corsica_beach/faces/corsica_beach_f0_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/corsica_beach/faces/corsica_beach_f1_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/corsica_beach/faces/corsica_beach_f2_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/corsica_beach/faces/corsica_beach_f3_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/corsica_beach/faces/corsica_beach_f4_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/corsica_beach/faces/corsica_beach_f5_m0.png"
   ],
   "is_default": false,
   "provenance": [
    "env_table:PROBE_CUBE_mod_D9AC3FDF0378051F.bin:paired_rgbm"
   ]
  },
  {
   "name": "corsica_beach_pc",
   "logical": "common\\env_map\\corsica_beach_pc.cube",
   "status": "partial",
   "container": "0000.gpk",
   "row": 12316,
   "sha16": "da5ebc9eee665fb4",
   "dims": null,
   "format": null,
   "n_faces": 0,
   "resolve": "shared",
   "in_skin": false,
   "faces": [],
   "is_default": false,
   "provenance": [
    "env_table:PROBE_CUBE_mod_BFBE907B687BF2E6.bin:cube_literal"
   ]
  },
  {
   "name": "fashion_bawangbieji",
   "logical": "common\\env_map\\fashion_bawangbieji.cube",
   "status": "source_verified",
   "container": "0000.gpk",
   "row": 12029,
   "sha16": "e1d1cd63d550c97b",
   "dims": "128x128",
   "format": "B8G8R8A8_UNORM cubemap mips=8 caps2=0xFE00",
   "n_faces": 6,
   "resolve": "shared",
   "in_skin": true,
   "faces": [
    "assets/3d/weapon_skin/_shared/cubes/fashion_bawangbieji/faces/fashion_bawangbieji_f0_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/fashion_bawangbieji/faces/fashion_bawangbieji_f1_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/fashion_bawangbieji/faces/fashion_bawangbieji_f2_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/fashion_bawangbieji/faces/fashion_bawangbieji_f3_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/fashion_bawangbieji/faces/fashion_bawangbieji_f4_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/fashion_bawangbieji/faces/fashion_bawangbieji_f5_m0.png"
   ],
   "is_default": false,
   "provenance": [
    "known_verified"
   ]
  },
  {
   "name": "fashion_qiangpi",
   "logical": "common\\env_map\\fashion_qiangpi.cube",
   "status": "source_verified",
   "container": "0000.gpk",
   "row": 12399,
   "sha16": "34252fcb4d641227",
   "dims": "128x128",
   "format": "B8G8R8A8_UNORM cubemap mips=8 caps2=0xFE00",
   "n_faces": 6,
   "resolve": "shared",
   "in_skin": true,
   "faces": [
    "assets/3d/weapon_skin/_shared/cubes/fashion_qiangpi/faces/fashion_qiangpi_f0_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/fashion_qiangpi/faces/fashion_qiangpi_f1_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/fashion_qiangpi/faces/fashion_qiangpi_f2_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/fashion_qiangpi/faces/fashion_qiangpi_f3_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/fashion_qiangpi/faces/fashion_qiangpi_f4_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/fashion_qiangpi/faces/fashion_qiangpi_f5_m0.png"
   ],
   "is_default": false,
   "provenance": [
    "known_verified"
   ]
  },
  {
   "name": "fashion_tiandizhizhu",
   "logical": "common\\env_map\\fashion_tiandizhizhu.cube",
   "status": "source_verified",
   "container": "0000.gpk",
   "row": 12404,
   "sha16": "757d2e55caa6b6e4",
   "dims": "128x128",
   "format": "B8G8R8A8_UNORM cubemap mips=8 caps2=0xFE00",
   "n_faces": 6,
   "resolve": "shared",
   "in_skin": true,
   "faces": [
    "assets/3d/weapon_skin/_shared/cubes/fashion_tiandizhizhu/faces/fashion_tiandizhizhu_f0_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/fashion_tiandizhizhu/faces/fashion_tiandizhizhu_f1_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/fashion_tiandizhizhu/faces/fashion_tiandizhizhu_f2_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/fashion_tiandizhizhu/faces/fashion_tiandizhizhu_f3_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/fashion_tiandizhizhu/faces/fashion_tiandizhizhu_f4_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/fashion_tiandizhizhu/faces/fashion_tiandizhizhu_f5_m0.png"
   ],
   "is_default": false,
   "provenance": [
    "known_verified"
   ]
  },
  {
   "name": "gdansk_shipyard_buildings",
   "logical": "common\\env_map\\gdansk_shipyard_buildings.cube",
   "status": "source_verified",
   "container": "0000.gpk",
   "row": 12384,
   "sha16": "3c838953a5db91c1",
   "dims": "128x128",
   "format": "B8G8R8A8_UNORM cubemap mips=8 caps2=0xFE00",
   "n_faces": 6,
   "resolve": "shared",
   "in_skin": false,
   "faces": [
    "assets/3d/weapon_skin/_shared/cubes/gdansk_shipyard_buildings/faces/gdansk_shipyard_buildings_f0_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/gdansk_shipyard_buildings/faces/gdansk_shipyard_buildings_f1_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/gdansk_shipyard_buildings/faces/gdansk_shipyard_buildings_f2_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/gdansk_shipyard_buildings/faces/gdansk_shipyard_buildings_f3_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/gdansk_shipyard_buildings/faces/gdansk_shipyard_buildings_f4_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/gdansk_shipyard_buildings/faces/gdansk_shipyard_buildings_f5_m0.png"
   ],
   "is_default": false,
   "provenance": [
    "env_table:PROBE_CUBE_mod_D9AC3FDF0378051F.bin:cube_literal",
    "env_table:PROBE_CUBE_mod_D9AC3FDF0378051F.bin:paired_rgbm"
   ]
  },
  {
   "name": "gdansk_shipyard_buildings02",
   "logical": "common\\env_map\\gdansk_shipyard_buildings02.cube",
   "status": "source_verified",
   "container": "0000.gpk",
   "row": 11706,
   "sha16": "d28948b4cffe512a",
   "dims": "128x128",
   "format": "B8G8R8A8_UNORM cubemap mips=8 caps2=0xFE00",
   "n_faces": 6,
   "resolve": "shared",
   "in_skin": true,
   "faces": [
    "assets/3d/weapon_skin/_shared/cubes/gdansk_shipyard_buildings02/faces/gdansk_shipyard_buildings02_f0_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/gdansk_shipyard_buildings02/faces/gdansk_shipyard_buildings02_f1_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/gdansk_shipyard_buildings02/faces/gdansk_shipyard_buildings02_f2_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/gdansk_shipyard_buildings02/faces/gdansk_shipyard_buildings02_f3_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/gdansk_shipyard_buildings02/faces/gdansk_shipyard_buildings02_f4_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/gdansk_shipyard_buildings02/faces/gdansk_shipyard_buildings02_f5_m0.png"
   ],
   "is_default": false,
   "provenance": [
    "env_table:PROBE_CUBE_mod_BFBE907B687BF2E6.bin:paired_rgbm"
   ]
  },
  {
   "name": "gdansk_shipyard_buildings_pc",
   "logical": "common\\env_map\\gdansk_shipyard_buildings_pc.cube",
   "status": "partial",
   "container": "0000.gpk",
   "row": 12420,
   "sha16": "d4ec22ccad95359c",
   "dims": null,
   "format": null,
   "n_faces": 0,
   "resolve": "shared",
   "in_skin": false,
   "faces": [],
   "is_default": false,
   "provenance": [
    "env_table:PROBE_CUBE_mod_BFBE907B687BF2E6.bin:cube_literal"
   ]
  },
  {
   "name": "glazed_patio",
   "logical": "common\\env_map\\glazed_patio.cube",
   "status": "source_verified",
   "container": "0000.gpk",
   "row": 12451,
   "sha16": "3c06f63dc94ed8f7",
   "dims": "128x128",
   "format": "B8G8R8A8_UNORM cubemap mips=8 caps2=0xFE00",
   "n_faces": 6,
   "resolve": "shared",
   "in_skin": false,
   "faces": [
    "assets/3d/weapon_skin/_shared/cubes/glazed_patio/faces/glazed_patio_f0_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/glazed_patio/faces/glazed_patio_f1_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/glazed_patio/faces/glazed_patio_f2_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/glazed_patio/faces/glazed_patio_f3_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/glazed_patio/faces/glazed_patio_f4_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/glazed_patio/faces/glazed_patio_f5_m0.png"
   ],
   "is_default": false,
   "provenance": [
    "env_table:PROBE_CUBE_mod_D9AC3FDF0378051F.bin:paired_rgbm"
   ]
  },
  {
   "name": "glazed_patio_pc",
   "logical": "common\\env_map\\glazed_patio_pc.cube",
   "status": "partial",
   "container": "0000.gpk",
   "row": 12439,
   "sha16": "302dce0b32db1873",
   "dims": null,
   "format": null,
   "n_faces": 0,
   "resolve": "shared",
   "in_skin": false,
   "faces": [],
   "is_default": false,
   "provenance": [
    "env_table:PROBE_CUBE_mod_BFBE907B687BF2E6.bin:cube_literal"
   ]
  },
  {
   "name": "indoor",
   "logical": "common\\env_map\\indoor.cube",
   "status": "source_verified",
   "container": "0000.gpk",
   "row": 11681,
   "sha16": "a464190b0febb360",
   "dims": "128x128",
   "format": "B8G8R8A8_UNORM cubemap mips=8 caps2=0xFE00",
   "n_faces": 6,
   "resolve": "shared",
   "in_skin": true,
   "faces": [
    "assets/3d/weapon_skin/_shared/cubes/indoor/faces/indoor_f0_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/indoor/faces/indoor_f1_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/indoor/faces/indoor_f2_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/indoor/faces/indoor_f3_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/indoor/faces/indoor_f4_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/indoor/faces/indoor_f5_m0.png"
   ],
   "is_default": false,
   "provenance": [
    "known_verified"
   ]
  },
  {
   "name": "industrial_pipe_and_valve_01_4k",
   "logical": "common\\env_map\\industrial_pipe_and_valve_01_4k.cube",
   "status": "source_verified",
   "container": "0000.gpk",
   "row": 12401,
   "sha16": "184ba01b6b4df766",
   "dims": "128x128",
   "format": "B8G8R8A8_UNORM cubemap mips=8 caps2=0xFE00",
   "n_faces": 6,
   "resolve": "shared",
   "in_skin": false,
   "faces": [
    "assets/3d/weapon_skin/_shared/cubes/industrial_pipe_and_valve_01_4k/faces/industrial_pipe_and_valve_01_4k_f0_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/industrial_pipe_and_valve_01_4k/faces/industrial_pipe_and_valve_01_4k_f1_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/industrial_pipe_and_valve_01_4k/faces/industrial_pipe_and_valve_01_4k_f2_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/industrial_pipe_and_valve_01_4k/faces/industrial_pipe_and_valve_01_4k_f3_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/industrial_pipe_and_valve_01_4k/faces/industrial_pipe_and_valve_01_4k_f4_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/industrial_pipe_and_valve_01_4k/faces/industrial_pipe_and_valve_01_4k_f5_m0.png"
   ],
   "is_default": false,
   "provenance": [
    "env_table:PROBE_CUBE_mod_D9AC3FDF0378051F.bin:paired_rgbm"
   ]
  },
  {
   "name": "industrial_pipe_and_valve_01_4k_pc",
   "logical": "common\\env_map\\industrial_pipe_and_valve_01_4k_pc.cube",
   "status": "partial",
   "container": "0000.gpk",
   "row": 12476,
   "sha16": "968df215b6e07761",
   "dims": null,
   "format": null,
   "n_faces": 0,
   "resolve": "shared",
   "in_skin": false,
   "faces": [],
   "is_default": false,
   "provenance": [
    "env_table:PROBE_CUBE_mod_BFBE907B687BF2E6.bin:cube_literal"
   ]
  },
  {
   "name": "jiayuan02a",
   "logical": "common\\env_map\\jiayuan02a.cube",
   "status": "source_verified",
   "container": "0000.gpk",
   "row": 12366,
   "sha16": "3e88584a9a3febda",
   "dims": "128x128",
   "format": "B8G8R8A8_UNORM cubemap mips=8 caps2=0xFE00",
   "n_faces": 6,
   "resolve": "skin",
   "in_skin": true,
   "faces": [
    "assets/3d/weapon_skin/_shared/cubes/jiayuan02a/faces/jiayuan02a_f0_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/jiayuan02a/faces/jiayuan02a_f1_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/jiayuan02a/faces/jiayuan02a_f2_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/jiayuan02a/faces/jiayuan02a_f3_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/jiayuan02a/faces/jiayuan02a_f4_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/jiayuan02a/faces/jiayuan02a_f5_m0.png"
   ],
   "is_default": false,
   "provenance": [
    "env_table:PROBE_CUBE_mod_D9AC3FDF0378051F.bin:paired_rgbm",
    "known_verified"
   ]
  },
  {
   "name": "jiayuan02a_night",
   "logical": "common\\env_map\\jiayuan02a_night.cube",
   "status": "source_verified",
   "container": "0000.gpk",
   "row": 12353,
   "sha16": "350ab923e73cab8b",
   "dims": "128x128",
   "format": "B8G8R8A8_UNORM cubemap mips=8 caps2=0xFE00",
   "n_faces": 6,
   "resolve": "shared",
   "in_skin": false,
   "faces": [
    "assets/3d/weapon_skin/_shared/cubes/jiayuan02a_night/faces/jiayuan02a_night_f0_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/jiayuan02a_night/faces/jiayuan02a_night_f1_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/jiayuan02a_night/faces/jiayuan02a_night_f2_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/jiayuan02a_night/faces/jiayuan02a_night_f3_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/jiayuan02a_night/faces/jiayuan02a_night_f4_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/jiayuan02a_night/faces/jiayuan02a_night_f5_m0.png"
   ],
   "is_default": false,
   "provenance": [
    "env_table:PROBE_CUBE_mod_D9AC3FDF0378051F.bin:paired_rgbm"
   ]
  },
  {
   "name": "jiayuan02a_night_pc",
   "logical": "common\\env_map\\jiayuan02a_night_pc.cube",
   "status": "partial",
   "container": "0000.gpk",
   "row": 12466,
   "sha16": "7370e5e910e5cba2",
   "dims": null,
   "format": null,
   "n_faces": 0,
   "resolve": "shared",
   "in_skin": false,
   "faces": [],
   "is_default": false,
   "provenance": [
    "env_table:PROBE_CUBE_mod_BFBE907B687BF2E6.bin:cube_literal"
   ]
  },
  {
   "name": "jiayuan02a_pc",
   "logical": "common\\env_map\\jiayuan02a_pc.cube",
   "status": "partial",
   "container": "0000.gpk",
   "row": 12468,
   "sha16": "f6726198e1492c81",
   "dims": null,
   "format": null,
   "n_faces": 0,
   "resolve": "shared",
   "in_skin": false,
   "faces": [],
   "is_default": false,
   "provenance": [
    "env_table:PROBE_CUBE_mod_BFBE907B687BF2E6.bin:cube_literal"
   ]
  },
  {
   "name": "login40",
   "logical": "common\\env_map\\login40.cube",
   "status": "source_verified",
   "container": "0000.gpk",
   "row": 12421,
   "sha16": "ebf972c599b9956f",
   "dims": "128x128",
   "format": "B8G8R8A8_UNORM cubemap mips=8 caps2=0xFE00",
   "n_faces": 6,
   "resolve": "shared",
   "in_skin": true,
   "faces": [
    "assets/3d/weapon_skin/_shared/cubes/login40/faces/login40_f0_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/login40/faces/login40_f1_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/login40/faces/login40_f2_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/login40/faces/login40_f3_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/login40/faces/login40_f4_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/login40/faces/login40_f5_m0.png"
   ],
   "is_default": false,
   "provenance": [
    "known_verified"
   ]
  },
  {
   "name": "neight_02",
   "logical": "common\\env_map\\neight_02.cube",
   "status": "source_verified",
   "container": "0000.gpk",
   "row": 12090,
   "sha16": "cd34d72b43186b9e",
   "dims": "128x128",
   "format": "B8G8R8A8_UNORM cubemap mips=8 caps2=0xFE00",
   "n_faces": 6,
   "resolve": "shared",
   "in_skin": false,
   "faces": [
    "assets/3d/weapon_skin/_shared/cubes/neight_02/faces/neight_02_f0_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/neight_02/faces/neight_02_f1_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/neight_02/faces/neight_02_f2_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/neight_02/faces/neight_02_f3_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/neight_02/faces/neight_02_f4_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/neight_02/faces/neight_02_f5_m0.png"
   ],
   "is_default": false,
   "provenance": [
    "env_table:PROBE_CUBE_mod_D9AC3FDF0378051F.bin:paired_rgbm"
   ]
  },
  {
   "name": "neight_02_pc",
   "logical": "common\\env_map\\neight_02_pc.cube",
   "status": "partial",
   "container": "0000.gpk",
   "row": 12379,
   "sha16": "7a05fbf16adfede9",
   "dims": null,
   "format": null,
   "n_faces": 0,
   "resolve": "shared",
   "in_skin": false,
   "faces": [],
   "is_default": false,
   "provenance": [
    "env_table:PROBE_CUBE_mod_BFBE907B687BF2E6.bin:cube_literal"
   ]
  },
  {
   "name": "nielian01",
   "logical": "common\\env_map\\nielian01.cube",
   "status": "source_verified",
   "container": "0000.gpk",
   "row": 10267,
   "sha16": "a48170773484bbff",
   "dims": "128x128",
   "format": "B8G8R8A8_UNORM cubemap mips=8 caps2=0xFE00",
   "n_faces": 6,
   "resolve": "shared",
   "in_skin": false,
   "faces": [
    "assets/3d/weapon_skin/_shared/cubes/nielian01/faces/nielian01_f0_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/nielian01/faces/nielian01_f1_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/nielian01/faces/nielian01_f2_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/nielian01/faces/nielian01_f3_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/nielian01/faces/nielian01_f4_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/nielian01/faces/nielian01_f5_m0.png"
   ],
   "is_default": false,
   "provenance": [
    "env_table:PROBE_CUBE_mod_D9AC3FDF0378051F.bin:paired_rgbm"
   ]
  },
  {
   "name": "nielian01_pc",
   "logical": "common\\env_map\\nielian01_pc.cube",
   "status": "partial",
   "container": "0000.gpk",
   "row": 11159,
   "sha16": "e1c7ebf78aa53c46",
   "dims": null,
   "format": null,
   "n_faces": 0,
   "resolve": "shared",
   "in_skin": false,
   "faces": [],
   "is_default": false,
   "provenance": [
    "env_table:PROBE_CUBE_mod_BFBE907B687BF2E6.bin:cube_literal"
   ]
  },
  {
   "name": "night_clearsky",
   "logical": "common\\env_map\\night_clearsky.cube",
   "status": "source_verified",
   "container": "0000.gpk",
   "row": 12300,
   "sha16": "097d28d48d462e63",
   "dims": "128x128",
   "format": "B8G8R8A8_UNORM cubemap mips=8 caps2=0xFE00",
   "n_faces": 6,
   "resolve": "shared",
   "in_skin": false,
   "faces": [
    "assets/3d/weapon_skin/_shared/cubes/night_clearsky/faces/night_clearsky_f0_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/night_clearsky/faces/night_clearsky_f1_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/night_clearsky/faces/night_clearsky_f2_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/night_clearsky/faces/night_clearsky_f3_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/night_clearsky/faces/night_clearsky_f4_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/night_clearsky/faces/night_clearsky_f5_m0.png"
   ],
   "is_default": false,
   "provenance": [
    "env_table:PROBE_CUBE_mod_D9AC3FDF0378051F.bin:paired_rgbm"
   ]
  },
  {
   "name": "night_clearsky02",
   "logical": "common\\env_map\\night_clearsky02.cube",
   "status": "source_verified",
   "container": "0000.gpk",
   "row": 11525,
   "sha16": "5c02a9bec582d890",
   "dims": "128x128",
   "format": "B8G8R8A8_UNORM cubemap mips=8 caps2=0xFE00",
   "n_faces": 6,
   "resolve": "shared",
   "in_skin": false,
   "faces": [
    "assets/3d/weapon_skin/_shared/cubes/night_clearsky02/faces/night_clearsky02_f0_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/night_clearsky02/faces/night_clearsky02_f1_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/night_clearsky02/faces/night_clearsky02_f2_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/night_clearsky02/faces/night_clearsky02_f3_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/night_clearsky02/faces/night_clearsky02_f4_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/night_clearsky02/faces/night_clearsky02_f5_m0.png"
   ],
   "is_default": false,
   "provenance": [
    "env_table:PROBE_CUBE_mod_BFBE907B687BF2E6.bin:paired_rgbm"
   ]
  },
  {
   "name": "night_clearsky03",
   "logical": "common\\env_map\\night_clearsky03.cube",
   "status": "source_verified",
   "container": "0000.gpk",
   "row": 12320,
   "sha16": "4400691ae32b1e19",
   "dims": "128x128",
   "format": "B8G8R8A8_UNORM cubemap mips=8 caps2=0xFE00",
   "n_faces": 6,
   "resolve": "shared",
   "in_skin": false,
   "faces": [
    "assets/3d/weapon_skin/_shared/cubes/night_clearsky03/faces/night_clearsky03_f0_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/night_clearsky03/faces/night_clearsky03_f1_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/night_clearsky03/faces/night_clearsky03_f2_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/night_clearsky03/faces/night_clearsky03_f3_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/night_clearsky03/faces/night_clearsky03_f4_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/night_clearsky03/faces/night_clearsky03_f5_m0.png"
   ],
   "is_default": false,
   "provenance": [
    "env_table:PROBE_CUBE_mod_D9AC3FDF0378051F.bin:paired_rgbm"
   ]
  },
  {
   "name": "night_clearsky_pc",
   "logical": "common\\env_map\\night_clearsky_pc.cube",
   "status": "partial",
   "container": "0000.gpk",
   "row": 12380,
   "sha16": "7a05fbf16adfede9",
   "dims": null,
   "format": null,
   "n_faces": 0,
   "resolve": "shared",
   "in_skin": false,
   "faces": [],
   "is_default": false,
   "provenance": [
    "env_table:PROBE_CUBE_mod_BFBE907B687BF2E6.bin:cube_literal"
   ]
  },
  {
   "name": "over_the_clouds",
   "logical": "common\\env_map\\over_the_clouds.cube",
   "status": "source_verified",
   "container": "0000.gpk",
   "row": 11938,
   "sha16": "351ecd26e9867100",
   "dims": "128x128",
   "format": "B8G8R8A8_UNORM cubemap mips=8 caps2=0xFE00",
   "n_faces": 6,
   "resolve": "shared",
   "in_skin": false,
   "faces": [
    "assets/3d/weapon_skin/_shared/cubes/over_the_clouds/faces/over_the_clouds_f0_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/over_the_clouds/faces/over_the_clouds_f1_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/over_the_clouds/faces/over_the_clouds_f2_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/over_the_clouds/faces/over_the_clouds_f3_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/over_the_clouds/faces/over_the_clouds_f4_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/over_the_clouds/faces/over_the_clouds_f5_m0.png"
   ],
   "is_default": false,
   "provenance": [
    "env_table:PROBE_CUBE_mod_D9AC3FDF0378051F.bin:paired_rgbm"
   ]
  },
  {
   "name": "over_the_clouds_pc",
   "logical": "common\\env_map\\over_the_clouds_pc.cube",
   "status": "partial",
   "container": "0000.gpk",
   "row": 12255,
   "sha16": "92b57ea7013c9d40",
   "dims": null,
   "format": null,
   "n_faces": 0,
   "resolve": "shared",
   "in_skin": false,
   "faces": [],
   "is_default": false,
   "provenance": [
    "env_table:PROBE_CUBE_mod_BFBE907B687BF2E6.bin:cube_literal"
   ]
  },
  {
   "name": "panorama",
   "logical": "common\\env_map\\panorama.cube",
   "status": "source_verified",
   "container": "0000.gpk",
   "row": 12398,
   "sha16": "981e673b31890610",
   "dims": "128x128",
   "format": "B8G8R8A8_UNORM cubemap mips=8 caps2=0xFE00",
   "n_faces": 6,
   "resolve": "shared",
   "in_skin": false,
   "faces": [
    "assets/3d/weapon_skin/_shared/cubes/panorama/faces/panorama_f0_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/panorama/faces/panorama_f1_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/panorama/faces/panorama_f2_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/panorama/faces/panorama_f3_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/panorama/faces/panorama_f4_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/panorama/faces/panorama_f5_m0.png"
   ],
   "is_default": false,
   "provenance": [
    "env_table:PROBE_CUBE_mod_D9AC3FDF0378051F.bin:paired_rgbm"
   ]
  },
  {
   "name": "panorama_pc",
   "logical": "common\\env_map\\panorama_pc.cube",
   "status": "partial",
   "container": "0000.gpk",
   "row": 12462,
   "sha16": "29f8bee94a265153",
   "dims": null,
   "format": null,
   "n_faces": 0,
   "resolve": "shared",
   "in_skin": false,
   "faces": [],
   "is_default": false,
   "provenance": [
    "env_table:PROBE_CUBE_mod_BFBE907B687BF2E6.bin:cube_literal"
   ]
  },
  {
   "name": "qiangpi",
   "logical": "common\\env_map\\qiangpi.cube",
   "status": "source_verified",
   "container": "0000.gpk",
   "row": 12388,
   "sha16": "173d52990b3ab836",
   "dims": "128x128",
   "format": "B8G8R8A8_UNORM cubemap mips=8 caps2=0xFE00",
   "n_faces": 6,
   "resolve": "skin",
   "in_skin": true,
   "faces": [
    "assets/3d/weapon_skin/_shared/cubes/qiangpi/faces/qiangpi_f0_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/qiangpi/faces/qiangpi_f1_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/qiangpi/faces/qiangpi_f2_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/qiangpi/faces/qiangpi_f3_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/qiangpi/faces/qiangpi_f4_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/qiangpi/faces/qiangpi_f5_m0.png"
   ],
   "is_default": true,
   "provenance": [
    "env_table:PROBE_CUBE_mod_D9AC3FDF0378051F.bin:paired_rgbm",
    "known_verified"
   ]
  },
  {
   "name": "snow",
   "logical": "common\\env_map\\snow.cube",
   "status": "source_verified",
   "container": "0000.gpk",
   "row": 11915,
   "sha16": "a974343d3689cc1a",
   "dims": "128x128",
   "format": "B8G8R8A8_UNORM cubemap mips=8 caps2=0xFE00",
   "n_faces": 6,
   "resolve": "shared",
   "in_skin": false,
   "faces": [
    "assets/3d/weapon_skin/_shared/cubes/snow/faces/snow_f0_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/snow/faces/snow_f1_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/snow/faces/snow_f2_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/snow/faces/snow_f3_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/snow/faces/snow_f4_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/snow/faces/snow_f5_m0.png"
   ],
   "is_default": false,
   "provenance": [
    "env_table:PROBE_CUBE_mod_D9AC3FDF0378051F.bin:paired_rgbm"
   ]
  },
  {
   "name": "snow_pc",
   "logical": "common\\env_map\\snow_pc.cube",
   "status": "partial",
   "container": "0000.gpk",
   "row": 12432,
   "sha16": "0f113b8a1cda003d",
   "dims": null,
   "format": null,
   "n_faces": 0,
   "resolve": "shared",
   "in_skin": false,
   "faces": [],
   "is_default": false,
   "provenance": [
    "env_table:PROBE_CUBE_mod_BFBE907B687BF2E6.bin:cube_literal"
   ]
  },
  {
   "name": "bg61e_1_light_boxreflectioncapture2_0",
   "logical": "scene\\instance\\bg61e_1_content\\captures\\bg61e_1_light_boxreflectioncapture2_0.cube",
   "status": "source_verified",
   "container": "scene_02.gpk",
   "row": 102966,
   "sha16": "0ca1493d3fa30b93",
   "dims": "128x128",
   "format": "B8G8R8A8_UNORM cubemap mips=8 caps2=0xFE00",
   "n_faces": 6,
   "resolve": "shared",
   "in_skin": false,
   "faces": [
    "assets/3d/weapon_skin/_shared/cubes/bg61e_1_light_boxreflectioncapture2_0/faces/bg61e_1_light_boxreflectioncapture2_0_f0_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/bg61e_1_light_boxreflectioncapture2_0/faces/bg61e_1_light_boxreflectioncapture2_0_f1_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/bg61e_1_light_boxreflectioncapture2_0/faces/bg61e_1_light_boxreflectioncapture2_0_f2_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/bg61e_1_light_boxreflectioncapture2_0/faces/bg61e_1_light_boxreflectioncapture2_0_f3_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/bg61e_1_light_boxreflectioncapture2_0/faces/bg61e_1_light_boxreflectioncapture2_0_f4_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/bg61e_1_light_boxreflectioncapture2_0/faces/bg61e_1_light_boxreflectioncapture2_0_f5_m0.png"
   ],
   "is_default": false,
   "provenance": [
    "env_table:PROBE_CUBE_mod_D9AC3FDF0378051F.bin:paired_rgbm"
   ]
  },
  {
   "name": "bg61e_1_light_boxreflectioncapture_1",
   "logical": "scene\\instance\\bg61e_1_content\\captures\\bg61e_1_light_boxreflectioncapture_1.cube",
   "status": "source_verified",
   "container": "scene_02.gpk",
   "row": 102970,
   "sha16": "4a4dc4ad3410b25c",
   "dims": "128x128",
   "format": "B8G8R8A8_UNORM cubemap mips=8 caps2=0xFE00",
   "n_faces": 6,
   "resolve": "shared",
   "in_skin": false,
   "faces": [
    "assets/3d/weapon_skin/_shared/cubes/bg61e_1_light_boxreflectioncapture_1/faces/bg61e_1_light_boxreflectioncapture_1_f0_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/bg61e_1_light_boxreflectioncapture_1/faces/bg61e_1_light_boxreflectioncapture_1_f1_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/bg61e_1_light_boxreflectioncapture_1/faces/bg61e_1_light_boxreflectioncapture_1_f2_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/bg61e_1_light_boxreflectioncapture_1/faces/bg61e_1_light_boxreflectioncapture_1_f3_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/bg61e_1_light_boxreflectioncapture_1/faces/bg61e_1_light_boxreflectioncapture_1_f4_m0.png",
    "assets/3d/weapon_skin/_shared/cubes/bg61e_1_light_boxreflectioncapture_1/faces/bg61e_1_light_boxreflectioncapture_1_f5_m0.png"
   ],
   "is_default": false,
   "provenance": [
    "env_table:PROBE_CUBE_mod_D9AC3FDF0378051F.bin:paired_rgbm"
   ]
  },
  {
   "name": "qiangpi_pc",
   "logical": "common\\env_map\\qiangpi_pc.cube",
   "status": "unresolved",
   "container": null,
   "row": null,
   "sha16": "",
   "dims": null,
   "format": null,
   "n_faces": 0,
   "resolve": "shared",
   "in_skin": false,
   "faces": [],
   "is_default": false,
   "provenance": [
    "env_table:PROBE_CUBE_mod_BFBE907B687BF2E6.bin:cube_literal"
   ]
  },
  {
   "name": "bg61f_light_spherereflectioncapture2_pc",
   "logical": "scene\\instance\\bg61f_content\\captures\\bg61f_light_spherereflectioncapture2_pc.cube",
   "status": "unresolved",
   "container": null,
   "row": null,
   "sha16": "",
   "dims": null,
   "format": null,
   "n_faces": 0,
   "resolve": "shared",
   "in_skin": false,
   "faces": [],
   "is_default": false,
   "provenance": [
    "env_table:PROBE_CUBE_mod_BFBE907B687BF2E6.bin:cube_literal"
   ]
  },
  {
   "name": "bg61f_light_spherereflectioncapture_1_pc",
   "logical": "scene\\instance\\bg61f_content\\captures\\bg61f_light_spherereflectioncapture_1_pc.cube",
   "status": "unresolved",
   "container": null,
   "row": null,
   "sha16": "",
   "dims": null,
   "format": null,
   "n_faces": 0,
   "resolve": "shared",
   "in_skin": false,
   "faces": [],
   "is_default": false,
   "provenance": [
    "env_table:PROBE_CUBE_mod_BFBE907B687BF2E6.bin:cube_literal"
   ]
  },
  {
   "name": "bg61e_1_light_boxreflectioncapture2_0_pc",
   "logical": "scene\\instance\\bg61e_1_content\\captures\\bg61e_1_light_boxreflectioncapture2_0_pc.cube",
   "status": "unresolved",
   "container": null,
   "row": null,
   "sha16": "",
   "dims": null,
   "format": null,
   "n_faces": 0,
   "resolve": "shared",
   "in_skin": false,
   "faces": [],
   "is_default": false,
   "provenance": [
    "env_table:PROBE_CUBE_mod_BFBE907B687BF2E6.bin:cube_literal"
   ]
  },
  {
   "name": "bg61e_1_light_boxreflectioncapture_1_pc",
   "logical": "scene\\instance\\bg61e_1_content\\captures\\bg61e_1_light_boxreflectioncapture_1_pc.cube",
   "status": "unresolved",
   "container": null,
   "row": null,
   "sha16": "",
   "dims": null,
   "format": null,
   "n_faces": 0,
   "resolve": "shared",
   "in_skin": false,
   "faces": [],
   "is_default": false,
   "provenance": [
    "env_table:PROBE_CUBE_mod_BFBE907B687BF2E6.bin:cube_literal"
   ]
  },
  {
   "name": "epic_quad_panorama_gray_pc",
   "logical": "common\\env_map\\epic_quad_panorama_gray_pc.cube",
   "status": "unresolved",
   "container": null,
   "row": null,
   "sha16": "",
   "dims": null,
   "format": null,
   "n_faces": 0,
   "resolve": "shared",
   "in_skin": false,
   "faces": [],
   "is_default": false,
   "provenance": [
    "env_table:PROBE_CUBE_mod_BFBE907B687BF2E6.bin:cube_literal"
   ]
  },
  {
   "name": "login27_cube",
   "logical": "common\\env_map\\login27_cube.cube",
   "status": "unresolved",
   "container": null,
   "row": null,
   "sha16": "",
   "dims": null,
   "format": null,
   "n_faces": 0,
   "resolve": "shared",
   "in_skin": false,
   "faces": [],
   "is_default": false,
   "provenance": [
    "known_verified"
   ]
  }
 ]
};
