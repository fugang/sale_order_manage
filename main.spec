# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[('config.yaml', '.'), ('ui/add_sale_contract.ui', 'ui'),
        ('ui/base_info.ui', 'ui'), ('ui/cash_in_out.ui', 'ui'),
        ('ui/main_window.ui', 'ui'), ('ui/view_cash.ui', 'ui'),
        ('ui/view_purchase.ui', 'ui'), ("610.ico", "."),
        ('ui/about.ui', 'ui')],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='zk-pt',
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
    icon=['610.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main',
)
