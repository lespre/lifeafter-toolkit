# -*- coding: utf-8 -*-
"""dxbc_disasm.py — 用游戏自带 D3DCompiler_47.dll 反汇编 .pipe 内 DXBC blob
用法: python dxbc_disasm.py <file.pipe> [--out <dir>]
输出: <pipe>_blob{k}_{VS|PS}.asm (含 Resource Bindings 注释头)
"""
import sys, os, struct, ctypes
from ctypes import wintypes

DLLS = [r'E:\mrzh\Documents\bin\x64\D3DCompiler_47.dll',
        r'E:\mrzh\Documents\bin\x64\D3DCompiler_43.dll',
        r'E:\mrzh\Documents\bin\x64-2\D3DCompiler_47.dll']

def load_dll():
    for d in DLLS:
        if os.path.exists(d):
            try:
                return ctypes.WinDLL(d), d
            except Exception as e:
                print('load fail', d, e)
    raise RuntimeError('no D3DCompiler dll')

def disasm_one(dll, data):
    dll.D3DDisassemble.restype = ctypes.c_long
    dll.D3DDisassemble.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_uint,
                                   ctypes.c_char_p, ctypes.POINTER(ctypes.c_void_p)]
    blob = ctypes.c_void_p()
    hr = dll.D3DDisassemble(ctypes.c_char_p(data), ctypes.c_size_t(len(data)),
                            ctypes.c_uint(0), None, ctypes.byref(blob))
    if hr != 0 or not blob.value:
        return None, hr
    # ID3DBlob: vtable[3]=GetBufferPointer, [4]=GetBufferSize
    vt = ctypes.cast(blob, ctypes.POINTER(ctypes.c_void_p))[0]
    fptr = ctypes.cast(vt, ctypes.POINTER(ctypes.c_void_p))
    release = ctypes.WINFUNCTYPE(ctypes.c_ulong, ctypes.c_void_p)(fptr[2])
    get_ptr = ctypes.WINFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p)(fptr[3])
    get_size = ctypes.WINFUNCTYPE(ctypes.c_size_t, ctypes.c_void_p)(fptr[4])
    ptr = get_ptr(blob)
    size = get_size(blob)
    text = ctypes.string_at(ptr, size).decode('latin1')
    release(blob)
    return text, hr

def main():
    p = sys.argv[1]
    outd = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else os.path.dirname(os.path.abspath(p))
    os.makedirs(outd, exist_ok=True)
    b = open(p, 'rb').read()
    dll, dllp = load_dll()
    print('dll:', dllp)
    i = 0; k = 0
    while True:
        i = b.find(b'DXBC', i)
        if i < 0:
            break
        total = struct.unpack_from('<I', b, i + 24)[0]
        data = b[i:i + total]
        text, hr = disasm_one(dll, data)
        tag = 'blob'
        if text:
            head = text[:800]
            if ' vs_5_' in head or ' vs_4_' in head or 'vs_5_0' in head:
                tag = 'VS'
            elif 'ps_5_0' in head or ' ps_5_' in head or 'ps_4_0' in head:
                tag = 'PS'
            fn = os.path.join(outd, os.path.basename(p) + '_blob%d_%s.asm' % (k, tag))
            open(fn, 'w', encoding='utf-8').write(text)
            print('blob%d %s -> %s (%d chars, hr=%s)' % (k, tag, fn, len(text), hex(hr & 0xffffffff)))
            print('---- head ----')
            print(text[:600])
        else:
            print('blob%d disasm FAIL hr=%s' % (k, hex(hr & 0xffffffff)))
        k += 1
        i += 4

if __name__ == '__main__':
    main()
