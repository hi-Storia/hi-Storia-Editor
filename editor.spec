# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['editor.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),  # Includi la cartella dei font
        ('modules/arduino_tool/arduino', 'arduino'),  # Includi la cartella delle immagini
        ('modules/arduino_tool/sketch', 'sketch'),  # Includi la cartella delle immagini
    ],
    hiddenimports=[],
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
    name='editor',
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
    name='main_editor',
)
