# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src\\main.py'],
    pathex=['./src', './src/ui'],
    binaries=[],
    datas=[('C:\\Workspace\\Python\\Autocorrect\\venv\\Lib\\site-packages\\tiktoken', 'tiktoken'), ('C:\\Workspace\\Python\\Autocorrect\\venv\\Lib\\site-packages\\send2trash', 'send2trash'), ('C:\\Workspace\\Python\\Autocorrect\\venv\\Lib\\site-packages\\regex', 'regex'), ('C:\\Workspace\\Python\\Autocorrect\\venv\\Lib\\site-packages\\tiktoken_ext', 'tiktoken_ext')],
    hiddenimports=['settings_window', 'settings_manager', 'command_executer' 'autocorrect_service', 'tiktoken', 'concurrent', 'concurrent.futures', 'regex', 'send2trash', 'uuid'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0
)


pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='FIX',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='./src/assets/icon.ico'
)
