# Ghidra post-script (Jython): 找 GPK 相关字符串的引用并反编译所在函数
# 用法：analyzeHeadless <proj> <name> -import <so> -postScript find_gpk_refs.py
from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

TARGETS = {
    0x943313: "decrypt_content",
    0x851358: "File_too_small_valid_GPK",
    0x82aec1: "AttachGpk_failed",
    0x9767b9: "GPK_API_version",
}

prog = currentProgram
fm = prog.getFunctionManager()
refmgr = prog.getReferenceManager()
af = prog.getAddressFactory().getDefaultAddressSpace()

decomp = DecompInterface()
decomp.openProgram(prog)
monitor = ConsoleTaskMonitor()

print("=== GPK 引用报告 ===")
for va, label in TARGETS.items():
    addr = af.getAddress(va)
    refs = refmgr.getReferencesTo(addr)
    n = 0
    for r in refs:
        from_addr = r.getFromAddress()
        func = fm.getFunctionContaining(from_addr)
        fname = func.getName() if func else "<no-func>"
        fentry = func.getEntryPoint() if func else None
        print("[%s] ref@%s type=%s func=%s entry=%s" % (label, from_addr, r.getReferenceType(), fname, fentry))
        n += 1
        if func and n <= 3:
            res = decomp.decompileFunction(func, 60, monitor)
            if res and res.decompileCompleted():
                c = res.getDecompiledFunction().getC()
                print("---- decompile %s ----" % fname)
                print(c[:6000])
                print("---- end ----")
    print("[%s] total refs=%d" % (label, n))
print("=== 报告结束 ===")
