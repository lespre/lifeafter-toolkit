# -*- coding: utf-8 -*-
"""exe step5：入口首条 call 目标是否=未加密解压 loader；并找 UPX1 里最像代码的区域。"""
import pefile
from capstone import *
tp=r"E:\mrzh\Documents\bin\x64\lifeafter.exe"
raw=open(tp,'rb').read()
pe=pefile.PE(tp,fast_load=True)
base=pe.OPTIONAL_HEADER.ImageBase
def rva2off(rva):
    for s in pe.sections:
        if s.VirtualAddress<=rva<s.VirtualAddress+max(s.Misc_VirtualSize,s.SizeOfRawData):
            return s.PointerToRawData+(rva-s.VirtualAddress),s.Name.rstrip(b'\0').decode('latin1')
    return None,None
md=Cs(CS_ARCH_X86,CS_MODE_64)
# 入口 call 目标 VA=0x14f6bf073
for tgt_va in (0x14f6bf073,):
    rva=tgt_va-base; off,sec=rva2off(rva)
    print(f"call目标 VA {tgt_va:#x} RVA {rva:#x} -> 节{sec} 文件偏移 {off:#x}")
    code=raw[off:off+200]
    print("反汇编:")
    n=0
    for ins in md.disasm(code,tgt_va):
        print("  %#012x %-9s %s"%(ins.address,ins.mnemonic,ins.op_str)); n+=1
        if n>=30: break
# 扫描 UPX1 前 4MB，统计“可连续反汇编长度”，找最长的规整代码块
upx1=[s for s in pe.sections if s.Name.rstrip(b'\0')==b'UPX1'][0]
start=upx1.PointerToRawData; va=base+upx1.VirtualAddress
best=(0,0)
step=0x1000
for off in range(start,start+0x400000,step):
    code=raw[off:off+step]
    cnt=0
    for ins in md.disasm(code,va+(off-start)): cnt+=1
    if cnt>best[1]: best=(off,cnt)
print("\nUPX1前4MB最长连续反汇编块: 文件偏移%#x 指令数%d(每块最多~%d)"%(best[0],best[1],step//3))
