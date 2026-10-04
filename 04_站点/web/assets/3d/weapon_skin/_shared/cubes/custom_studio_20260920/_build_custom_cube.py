# -*- coding: utf-8 -*-
u"""_build_custom_cube.py —— 自造近似环境立方体 custom_studio_20260920 的**可复现构造脚本**（v2 盒式法）。

⚠️ 本产物是 **自造近似、非游戏资产**（self_authored_approximate）。
   像素**唯一**来源 = 游戏自己的武器皮肤背景板 `bg_weapon_skin_ingame.png`（房间内景，无武器无 HUD）。
   目的：让查看器有一个"房间感"的环境反射可看。**不得**当作"游戏实际使用该环境"的证据。

为什么用盒式法而不是全景投影（v1 失败记录，可复核）：
   v1 把背板当柱面全景重采样到六面。**实测失败**：两极是等距柱状的奇点 ⇒
   +Y 面出现漏斗状旋涡、−Y 面出现同心圆靶环（面图像被吸向极点），不可用。
   ⇒ 改用任务书允许的第二方案：「背墙面=房间图，其余面用房间图的模糊/渐变延拓」。
   该方案按**色带**直接映射，不存在极点，六面各自可读。

构造方法（一句话）：
   按对源背板逐行/逐列亮度扫描测出的 5 条色带（顶灯带 / 背墙 / 左右侧墙 / 地面格栅 / 警示条）
   分别裁切并缩放成对应立方体面（背墙→−Z、侧墙→±X、顶灯带→+Y、地面→−Y、正面=背墙镜像+重模糊
   并向房间均色渐变），再对每面边界做向房间均色的羽化以抑制面间接缝。

关键技术纪律（可复核）：
  ① **只用游戏自己的素材**；不引入任何网络图片。
  ② **不做任何全局增益/曝光/ACES/对比度调整** —— 只有裁切/缩放/高斯模糊/边界羽化，
     因此本 cube 的整体亮度 ＝ 源背板的亮度（源是暗色棚拍背板 ⇒ IBL 偏暗，这是**源的性质**，
     已如实登记，绝不用它去凑游戏参考图的亮度指标）。
  ③ 六面顺序与查看器现有约定一致：f0=+X f1=−X f2=+Y f3=−Y f4=+Z f5=−Z（three.js CubeTextureLoader）。
  ④ 源图 sha256 与产出六面 sha256 全部写进 provenance.json。

用法：
  $env:PYTHONIOENCODING='utf-8'
  & '<venv>\\python.exe' '<本文件>'
"""
import hashlib
import json
import os

import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
WIKI = r'E:\la拆包项目\04_站点\\web'
SRC = os.path.join(WIKI, r'assets\3d\weapon_skin\_shared\bg_weapon_skin_ingame.png')

FACE = 512
NAME = 'custom_studio_20260920'

# 源背板实测色带（1672×941；行号来自逐行亮度/亮带扫描，见构造报告 §色带实测）
Y_CEIL_TOP, Y_CEIL_BOT = 0, 215        # 顶灯带（y≈48–59 / 106–210 为亮条，max≈0.90）
Y_WALL_TOP, Y_WALL_BOT = 215, 690       # 背墙暗青绿面板（地平线≈415 落于其中）
Y_FLOOR_TOP, Y_FLOOR_BOT = 690, 886     # 地面格栅 + 黄黑警示条（y≈831–846）
X_WALL_L = (30, 320)                    # 左侧墙（背墙左缘≈337 之左）
X_WALL_R = (1352, 1642)                 # 右侧墙
X_BACK = (337, 1341)                    # 背墙横向范围（面板格栅主体）

BORDER_FEATHER = 0.35                   # 面边界向房间均色羽化的最大强度
BORDER_MARGIN = 0.18                    # 羽化过渡带占面边长的比例


def sha256_file(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def crop_resize(src_img, box, blur):
    c = src_img.crop(box).resize((FACE, FACE), Image.LANCZOS)
    if blur > 0:
        c = c.filter(ImageFilter.GaussianBlur(blur))
    return np.asarray(c).astype(np.float32) / 255.0


def feather_to(face, mean_rgb, strength=BORDER_FEATHER, margin=BORDER_MARGIN):
    """把面边界向房间均色羽化（1 → 中心无影响，0 → 边界处 strength 权重）。"""
    m = max(1, int(FACE * margin))
    lin = np.arange(FACE, dtype=np.float32)
    d = np.minimum(lin, FACE - 1 - lin)[None, :]
    d2 = np.minimum(lin, FACE - 1 - lin)[:, None]
    w = np.clip(np.minimum(d, d2) / float(m), 0.0, 1.0)[:, :, None]
    w = w * w * (3.0 - 2.0 * w)                      # smoothstep
    k = strength * (1.0 - w)
    return face * (1.0 - k) + mean_rgb[None, None, :] * k


def main():
    src_img = Image.open(SRC).convert('RGB')
    src_arr = np.asarray(src_img).astype(np.float32) / 255.0
    print('src      :', SRC)
    print('src size :', src_img.size, ' sha256:', sha256_file(SRC))

    wall_band = src_arr[Y_WALL_TOP:Y_WALL_BOT, X_BACK[0]:X_BACK[1]]
    mean_rgb = wall_band.reshape(-1, 3).mean(0)
    print('房间(背墙带)均色 rgb =', mean_rgb.round(4))

    # ---- 六面 ----
    f5 = crop_resize(src_img, (X_BACK[0], Y_WALL_TOP, X_BACK[1], Y_WALL_BOT), 2.0)   # -Z 背墙
    f4 = np.asarray(Image.fromarray((f5 * 255).astype(np.uint8), 'RGB')
                    .transpose(Image.FLIP_LEFT_RIGHT)
                    .filter(ImageFilter.GaussianBlur(20))).astype(np.float32) / 255.0
    f4 = f4 * 0.55 + mean_rgb[None, None, :] * 0.45                                  # +Z 正面（延拓）
    f1 = crop_resize(src_img, (X_WALL_L[0], Y_WALL_TOP, X_WALL_L[1], Y_WALL_BOT), 4.0)  # -X 左墙
    f0 = crop_resize(src_img, (X_WALL_R[0], Y_WALL_TOP, X_WALL_R[1], Y_WALL_BOT), 4.0)  # +X 右墙
    f2 = crop_resize(src_img, (0, Y_CEIL_TOP, src_img.width, Y_CEIL_BOT), 7.0)       # +Y 顶灯带
    f3 = crop_resize(src_img, (0, Y_FLOOR_TOP, src_img.width, Y_FLOOR_BOT), 5.0)     # -Y 地面

    faces = [feather_to(f, mean_rgb) for f in (f0, f1, f2, f3, f4, f5)]

    prov_faces = []
    for i, f in enumerate(faces):
        p = os.path.join(HERE, '%s_f%d_m0.png' % (NAME, i))
        Image.fromarray((np.clip(f, 0, 1) * 255.0 + 0.5).astype(np.uint8), 'RGB').save(p, optimize=True)
        lum = 0.2126 * f[:, :, 0] + 0.7152 * f[:, :, 1] + 0.0722 * f[:, :, 2]
        prov_faces.append({'face': i, 'axis': ['+X', '-X', '+Y', '-Y', '+Z', '-Z'][i],
                           'file': os.path.basename(p), 'sha256': sha256_file(p),
                           'bytes': os.path.getsize(p),
                           'mean_rgb': [round(float(f[:, :, c].mean()), 4) for c in range(3)],
                           'mean_lum': round(float(lum.mean()), 4),
                           'p95_lum': round(float(np.percentile(lum, 95)), 4)})
        print('  f%d %-3s %-42s sha256=%s  meanLum=%.4f' % (
            i, prov_faces[-1]['axis'], os.path.basename(p),
            prov_faces[-1]['sha256'][:16], prov_faces[-1]['mean_lum']))

    sheet = Image.new('RGB', (FACE * 3, FACE * 2), (0, 0, 0))
    for i, f in enumerate(faces):
        sheet.paste(Image.fromarray((np.clip(f, 0, 1) * 255.0 + 0.5).astype(np.uint8), 'RGB'),
                    ((i % 3) * FACE, (i // 3) * FACE))
    sheet.save(os.path.join(HERE, '_contact_sheet.png'), optimize=True)

    allf = np.concatenate([f.reshape(-1, 3) for f in faces], 0)
    alllum = 0.2126 * allf[:, 0] + 0.7152 * allf[:, 1] + 0.0722 * allf[:, 2]
    summary = {'cube_mean_rgb': [round(float(allf[:, c].mean()), 4) for c in range(3)],
               'cube_mean_lum': round(float(alllum.mean()), 4),
               'cube_p50_lum': round(float(np.percentile(alllum, 50)), 4),
               'cube_p95_lum': round(float(np.percentile(alllum, 95)), 4)}
    print('cube summary:', summary)

    prov = {
        'name': NAME,
        'status': 'self_authored_approximate',
        'authority': 'user_authorized_manual_20260920',
        'fidelity': 'approximate',
        'not_a_game_asset': True,
        'derived_from': [{'path': '04_站点\\web/assets/3d/weapon_skin/_shared/bg_weapon_skin_ingame.png',
                          'sha256': sha256_file(SRC),
                          'role': '游戏内武器皮肤背景板（房间内景，无武器、无 HUD）—— 本 cube 的**唯一**像素来源'}],
        'method': ('背墙面=房间图（±X 侧墙/顶灯带/地面各自取源背板对应色带裁切缩放），'
                   '正面=背墙镜像重模糊并向房间均色渐变，六面边界再向房间均色羽化 35% 以抑制接缝。'),
        'rejected_method': ('v1「柱面全景投影到六面」已实测失败并弃用：等距柱状两极是奇点，'
                            '+Y 出现漏斗旋涡、−Y 出现同心靶环，六面不可用（见报告 §失败记录）。'),
        'crop_bands': {'ceiling': [Y_CEIL_TOP, Y_CEIL_BOT], 'wall': [Y_WALL_TOP, Y_WALL_BOT],
                       'floor': [Y_FLOOR_TOP, Y_FLOOR_BOT], 'wall_left_x': list(X_WALL_L),
                       'wall_right_x': list(X_WALL_R), 'back_x': list(X_BACK)},
        'border_feather': {'strength': BORDER_FEATHER, 'margin': BORDER_MARGIN},
        'no_photometric_gain': True,
        'photometric_note': ('构造过程未施加任何全局增益/曝光/ACES/对比度调整；只有裁切、LANCZOS 缩放、'
                             '高斯模糊与边界羽化。源背板本身是暗色棚拍图，故本 cube 整体偏暗'
                             '（cube mean lum %.4f）—— 这是**源的性质**，已如实登记，'
                             '绝不用它去凑游戏参考图的亮度指标。' % summary['cube_mean_lum']),
        'cubemap_order': ['+X', '-X', '+Y', '-Y', '+Z', '-Z'],
        'face_size': FACE,
        'builder_script': os.path.basename(__file__),
        'faces': prov_faces,
        'summary': summary,
        'limitations': [
            '由单张 LDR 显示用背板重建 ⇒ 只保留大域颜色/亮度结构（暗青绿墙、顶灯带、地面格栅），不复原真实几何',
            '±X/±Y/−Y 面是源图对应色带的平面缩放，**不是**真实拍摄方向 ⇒ 反射中的具体形状不可当真',
            '源为已 tone-mapped 的显示用背板，直接当线性 HDR 环境使用 ⇒ 能量偏低',
            '未使用 .cube 容器的六面朝向/基变换证据 ⇒ 面朝向按 three.js 约定，未与引擎采样约定对齐',
        ],
        'note': '**自造近似立方体，非游戏资产**。仅用于观察环境反射对观感的影响；不得作为「游戏实际使用该环境」的证据，也不得计入「源数据驱动」目标。',
    }
    with open(os.path.join(HERE, 'provenance.json'), 'w', encoding='utf-8') as fh:
        json.dump(prov, fh, ensure_ascii=False, indent=1)
    print('wrote provenance.json')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
