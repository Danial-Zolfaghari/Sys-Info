# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

root = Path(SPECPATH).resolve().parent

a = Analysis(
    [str(root / 'sys-info.py')],
    pathex=[str(root)],
    binaries=[],
    datas=[],
    hiddenimports=['psutil', 'collector', 'collector.sys_info_collector'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['rich'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='sys-info-collector',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_debug=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='sys-info-collector',
)
