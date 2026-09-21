# -*- coding: utf-8 -*-
"""exe step3：入口点反汇编，判定是否标准UPX stub还是加密自定义壳。只读。"""
import pefile
tp=r"E:\mrzh\Documents\bin\x64\lifeafter.exe"
pe=pefile.PE(tp, fast_load=True)
ep=pe.OPTIONAL_HEADER.AddressOfEntryPoint
print("入口RVA %#x"%ep)
for s in pe.sections:
    va=s.VirtualAddress; vs=max(s.Misc_VirtualSize,s.SizeOfRawData)
    if va<=ep<va+vs:
        name=s.Name.rstrip(b'\0').decode('latin1')
        off=s.PointerToRawData+(ep-va)
        print("入口在节",name," 文件偏移 %#x"%off)
        raw=open(tp,'rb').read()
        code=raw[off:off+160]
        print("入口160字节hex:",code.hex(' ',1))
        try:
            from capstone import Cs,CS_ARCH_X86,CS_MODE_64
            md=Cs(CS_ARCH_X86,CS_MODE_64)
            print("\n反汇编前40条:")
            for i,ins in enumerate(md.disasm(code,pe.OPTIONAL_HEADER.ImageBase+ep)):
                print("  %#010x  %-10s %s"%(ins.address,ins.mnemonic,ins.op_str))
                if i>=39: break
        except ImportError:
            print("(无capstone，仅hex)")
        break
# TLS 回调
pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_TLS']])
if hasattr(pe,'DIRECTORY_ENTRY_TLS'):
    t=pe.DIRECTORY_ENTRY_TLS.struct
    print("\nTLS AddressOfCallBacks RVA %#x"%t.AddressOfCallBacks)
pe.close()
