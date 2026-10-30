# -*- coding: utf-8 -*-
"""诊断：huodong_conf_data.py 里 0xfb 标签候选为何过不了表体校验。"""
from __future__ import annotations

import pathlib
import struct
import sys

ROOT = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import bindict_73 as B73  # noqa: E402

RAW = ROOT / "01_索引与产物/41_还原树/pe/配置/com/cdata/huodong_conf_data.py"


def main() -> int:
    data = RAW.read_bytes()
    print("文件 %.2f MB" % (len(data) / 1e6), "BLOB_TAGS", [hex(t) for t in B73.BLOB_TAGS])
    cands = []
    for i in range(len(data) - 5):
        if data[i] not in B73.BLOB_TAGS:
            continue
        ln = struct.unpack_from("<I", data, i + 1)[0]
        if 64 <= ln <= len(data) - i - 5:
            cands.append((i, ln))
    print("长度合法的候选", len(cands), cands[:8])

    for off, ln in cands[:10]:
        payload = data[off + 5: off + 5 + ln]
        info = B73._looks_like_body(payload)
        print("\n候选 off=%d len=%d → %s" % (off, ln, "通过" if info else "未通过"))
        # 逐条检查
        if len(payload) >= 16:
            cnt, res = struct.unpack_from("<II", payload, 0)
            print("   count=%d reserved=%d" % (cnt, res))
            if res == 0 and 1 <= cnt <= 200_000:
                table_end = 8 + 4 * cnt
                if table_end + 12 <= len(payload):
                    ends = struct.unpack_from("<%dI" % cnt, payload, 8)
                    dm = payload[table_end:]
                    de = struct.unpack_from("<I", dm, 0)[0]
                    print("   ends[-1]=%d table_end=%d | data de=%d len(data)=%d | data[de]=%s tag=%s"
                          % (ends[-1], table_end, de, len(dm), hex(dm[de]) if de < len(dm) else "-",
                             hex(B73.INDEX_TAG)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
