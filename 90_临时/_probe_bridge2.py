# -*- coding: utf-8 -*-
"""appear_id_2_equip_id：payload = [u32 de][0x76 01 01 索引尾...]，
de=8 → blob 从 payload[0:8]？ 用 bindict_73.parse_index_73 直接试"""
import pathlib, struct, collections, sys
PROJ=pathlib.Path('E:/la拆包项目')
sys.path.insert(0,str(PROJ/'00_规范与工具/工具/工具库/00_共享核心'))
from toolkit_core import bindict_73 as B73
CD=PROJ/'01_索引与产物/41_还原树/pe/配置/com/cdata'
raw=(CD/'appear_id_2_equip_id.py').read_bytes()
payload=raw[269:269+7792]
# payload[8:] 是 76 01 01 ...
body=payload[8:]
print('body[0:16]', body[:16].hex())
de=struct.unpack_from('<I',body,0)[0]
print('de', de, 'body[de]', hex(body[de]) if de < len(body) else 'OOB')
try:
    pairs, meta = B73.parse_index_73(body)
    print('parse_index_73 ok, pairs', len(pairs))
    print('meta', {k:v for k,v in meta.items() if k!='errors'})
    print('样例 pairs', pairs[:8])
except Exception as e:
    import traceback; traceback.print_exc()
