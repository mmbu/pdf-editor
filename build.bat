@echo off
setlocal
cd /d "%~dp0"

python -m pip install -r requirements.txt

if not exist "resources\tessdata\eng.traineddata" (
  echo Downloading Tesseract language packs...
  mkdir "resources\tessdata" 2>nul
  copy /Y "C:\Program Files\Tesseract-OCR\tessdata\eng.traineddata" "resources\tessdata\" >nul 2>&1
  powershell -Command "Invoke-WebRequest -Uri 'https://github.com/tesseract-ocr/tessdata/raw/main/rus.traineddata' -OutFile 'resources\tessdata\rus.traineddata'"
  powershell -Command "Invoke-WebRequest -Uri 'https://github.com/tesseract-ocr/tessdata/raw/main/heb.traineddata' -OutFile 'resources\tessdata\heb.traineddata'"
)

python -m PyInstaller pdf_editor.spec --noconfirm

echo.
echo Ready: dist\PDFEditor.exe
pause
