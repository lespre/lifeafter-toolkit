# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_submodules


a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[('../01_核心解包器', '01_核心解包器'),
           ('../07_纹理转换', '07_纹理转换'),
           ('../06_皮肤定位链/gpk_npk_index.py', '06_皮肤定位链'),
           ('../08_GUI界面/shadcn.qss', '08_GUI界面')],
    hiddenimports=['Crypto', 'Crypto.Cipher', 'PIL', 'PIL.Image', 'argparse', 'cryptography', 'glob', 'hashlib', 'io', 'json', 'lz4.block', 'npk_reader', 'os', 'resource_resolver', 'struct', 'sys', 'time', 'zstandard'] + collect_submodules('Crypto'),  # 2026-09-21: 补全运行时动态加载的 gpk_npk_index.py 依赖（PyInstaller 静态图看不见）
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='明日之后拆包器_新',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # 2026-09-21: UPX 压坏 Qt6 DLL(ImportError DLL load failed / 找不到指定的程序)，禁用
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
