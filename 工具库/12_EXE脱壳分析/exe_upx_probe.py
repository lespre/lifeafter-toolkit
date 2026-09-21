# -*- coding: utf-8 -*-
"""exe step2：定位 UPX 魔数篡改情况 / stub 头 / 版本。只读。"""
import re, struct
from pathlib import Path
p=Path(r"E:\mrzh\Documents\bin\x64\lifeafter.exe")
raw=p.read_bytes()
print("大小:",len(raw))

# 1) 标准 UPX! 出现位置
for sig_name,sig in [("UPX!",b"UPX!"),("UPX0",b"UPX0"),("UPX1",b"UPX1")]:
    locs=[m.start() for m in re.finditer(re.escape(sig),raw)]
    print(f"{sig_name}: {len(locs)} 处 -> {[hex(x) for x in locs[:12]]}")

# 2) 文件头 0x40..0x600（UPX1 之前）hex；UPX stub 从 RawPtr=0x600 开始
print("\n0x000-0x040 DOS/PE 头尾部:")
print(raw[0:0x40].hex(' ',1))
print("\nUPX1 stub 起点 0x600 前 192 字节:")
print(raw[0x600:0x600+192].hex(' ',1))

# 3) 找形如 $Info 字符串 / UPX 版本串
for kw in [b'$Info',b'UPX',b'NRV',b'lzma',b'Markus',b'Oberhumer',b'$Id']:
    locs=[m.start() for m in re.finditer(re.escape(kw),raw)]
    if locs:
        print(f"\n串 {kw}: {len(locs)} 处, 首个@{hex(locs[0])} 上下文:",raw[max(0,locs[0]-8):locs[0]+48])

# 4) 0x200-0x600 区域（节表后、UPX1前）通常是 UPX l_info/p_info 头
print("\n0x200-0x600 非零片段:")
seg=raw[0x200:0x600]
# 找连续可打印
runs=re.findall(rb'[\x20-\x7e]{4,}',seg)
print("可打印串:",[r.decode('latin1') for r in runs][:20])
