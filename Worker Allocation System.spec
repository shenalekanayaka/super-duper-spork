# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

# Collect all Babel and tkcalendar resources
datas = [
    ('utils', 'utils'),
    ('allocations_json', 'allocations_json'),
    ('exports', 'exports'),
    ('excel', 'excel'),
    ('allocation_history.json', '.'),
    ('audit_trail.json', '.'),
]

binaries = []
hiddenimports = ['tkcalendar']

# Include all Babel files
tmp_babel = collect_all('babel')
datas += tmp_babel[0]
binaries += tmp_babel[1]
hiddenimports += tmp_babel[2]
hiddenimports += ['babel.numbers']  # explicitly include this missing submodule

# Include tkcalendar resources too
tmp_tkcalendar = collect_all('tkcalendar')
datas += tmp_tkcalendar[0]
binaries += tmp_tkcalendar[1]
hiddenimports += tmp_tkcalendar[2]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    [],
    exclude_binaries=True,
    name='Worker Allocation System',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
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
    name='Worker Allocation System',
)
