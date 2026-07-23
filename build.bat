@echo off
setlocal
cd /d "%~dp0"

python -m pip install -r requirements.txt
python -m PyInstaller pdf_editor.spec --noconfirm

echo.
echo Готово: dist\PDFEditor.exe
pause
