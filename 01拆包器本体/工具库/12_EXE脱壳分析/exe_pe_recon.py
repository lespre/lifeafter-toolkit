# -*- coding: utf-8 -*-
"""exe 攻坚 step1：PE 结构 / 节区熵 / 壳特征 / 导入表 侦察。只读。"""
import math, pefile, sys
from pathlib import Path

def shannon(b):
    if not b: return 0.0
    freq=[0]*256
    for x in b: freq[x]+=1
    e=0.0; n=len(b)
    for c in freq:
        if c:
            p=c/n; e-=p*math.log2(p)
    return e

targets=[
    r"E:\mrzh\Documents\bin\x64\lifeafter.exe",     # 最新 8-29
    r"E:\mrzh\bin\x64-2\lifeafter.exe",            # 旧 4-26 对照
]
for tp in targets:
    p=Path(tp)
    if not p.exists(): print("缺失",tp); continue
    print("="*90); print(tp, f"{p.stat().st_size:,} bytes")
    raw=p.read_bytes()
    print("整体熵: %.3f / 8.000"%shannon(raw))
    pe=pefile.PE(tp, fast_load=True)
    print("机器: %#x  入口RVA: %#x  镜像基址: %#x"%(pe.FILE_HEADER.Machine, pe.OPTIONAL_HEADER.AddressOfEntryPoint, pe.OPTIONAL_HEADER.ImageBase))
    print("子系统:",pe.OPTIONAL_HEADER.Subsystem," 节数:",pe.FILE_HEADER.NumberOfSections)
    print("节区:  name        VSize      RawSize    RawPtr     熵     特征")
    ep=pe.OPTIONAL_HEADER.AddressOfEntryPoint
    for s in pe.sections:
        name=s.Name.rstrip(b'\x00').decode('latin1')
        data=s.get_data()
        ent=shannon(data[:2_000_000])
        contains_ep = s.VirtualAddress <= ep < s.VirtualAddress+max(s.Misc_VirtualSize,s.SizeOfRawData)
        flag=[]
        if contains_ep: flag.append("<-入口")
        if ent>7.2: flag.append("高熵(压缩/加密?)")
        if name.upper().startswith(("UPX",".MPRESS",".VMP",".THEMIDA",".ENIGMA")): flag.append("壳节名")
        print("  %-10s %#010x %#010x %#010x %6.3f %s"%(name,s.Misc_VirtualSize,s.SizeOfRawData,s.PointerToRawData,ent," ".join(flag)))
    # 导入表
    pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_IMPORT'],
                                           pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_TLS'],
                                           pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_RESOURCE']])
    dlls=[]; nimp=0
    if hasattr(pe,'DIRECTORY_ENTRY_IMPORT'):
        for e in pe.DIRECTORY_ENTRY_IMPORT:
            dlls.append(e.dll.decode('latin1')); nimp+=len(e.imports)
    print("导入DLL(%d) 函数总数%d:"%(len(dlls),nimp), dlls[:20])
    print("有TLS回调:", hasattr(pe,'DIRECTORY_ENTRY_TLS'))
    # 壳名特征字符串
    for sig in [b'UPX!',b'UPX0',b'.vmp',b'VMProtect',b'Themida',b'Enigma',b'.MPRESS',b'NsPack',b'ASPack']:
        if sig in raw: print("  发现壳签名:",sig)
    pe.close()
