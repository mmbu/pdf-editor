# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

block_cipher = None

tessdata = Path("resources/tessdata")
datas = []
if tessdata.exists():
    datas = [(str(tessdata), "resources/tessdata")]

tesseract_exe = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")
binaries = []
if tesseract_exe.exists():
    tess_dir = tesseract_exe.parent
    binaries.append((str(tesseract_exe), "tesseract"))
    for dll in tess_dir.glob("*.dll"):
        binaries.append((str(dll), "tesseract"))

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=['fitz', 'pytesseract', 'PIL'],
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PDFEditor',
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
)
