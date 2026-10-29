import sys
import pathlib
# -*- coding: utf-8 -*-
"""把白底 logo 处理成透明背景 PNG（边界泛洪，保留白色笔画内部）。"""
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import WEB  # noqa: E402

SRC = Path(r"C:/Users/Administrator/AppData/Roaming/Hermes/composer-images/image_135207.png")
DST = Path(WEB / "assets/logo_lifeafter_wiki.png")

im = Image.open(SRC).convert("RGBA")
a = np.array(im)
h, w = a.shape[:2]
rgb = a[:, :, :3].astype(np.int16)
# 近白判定：三通道都 > 244
white = (rgb[:, :, 0] > 244) & (rgb[:, :, 1] > 244) & (rgb[:, :, 2] > 244)

visited = np.zeros((h, w), dtype=bool)
q = deque()
for x in range(w):
    for y in (0, h - 1):
        if white[y, x] and not visited[y, x]:
            visited[y, x] = True
            q.append((y, x))
for y in range(h):
    for x in (0, w - 1):
        if white[y, x] and not visited[y, x]:
            visited[y, x] = True
            q.append((y, x))

while q:
    y, x = q.popleft()
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        ny, nx = y + dy, x + dx
        if 0 <= ny < h and 0 <= nx < w and white[ny, nx] and not visited[ny, nx]:
            visited[ny, nx] = True
            q.append((ny, nx))

out = a.copy()
out[visited, 3] = 0

# 裁掉四周空白
alpha = out[:, :, 3]
ys, xs = np.where(alpha > 8)
y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
cropped = out[y0:y1, x0:x1]

img = Image.fromarray(cropped, "RGBA")
img.save(DST)
print("写出", DST, img.size, "原始", (w, h))
