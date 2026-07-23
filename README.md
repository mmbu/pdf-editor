# PDF Editor

Desktop PDF-редактор для Windows. Один `.exe` файл — без установки Python.

## Скачать

**[PDFEditor.exe (v1.0.0)](https://github.com/mmbu/pdf-editor/releases/download/v1.0.0/PDFEditor.exe)** (~81 МБ)

Страница релизов: https://github.com/mmbu/pdf-editor/releases

## Возможности

- **Редактирование PDF** — клик по слову, правка прямо на странице
- **OCR** для сканов (русский, английский, иврит, RTL)
- **Объединение** нескольких PDF в один
- **Разъединение** PDF на отдельные страницы
- **Изменение порядка** страниц (drag-and-drop)
- **Конвертация** изображений в PDF
- Undo/Redo, drag-and-drop файлов

## Запуск

1. Скачайте `PDFEditor.exe` из [Releases](https://github.com/mmbu/pdf-editor/releases)
2. Запустите двойным кликом — установка не нужна

## Горячие клавиши

| Клавиша | Действие |
|---------|----------|
| Ctrl+O | Открыть PDF |
| Ctrl+S | Сохранить как |
| Ctrl+Z | Отменить |
| Ctrl+Y | Повторить |
| Ctrl+H | На главный экран |
| Esc | Назад |
| F1 | Справка |

## Сборка из исходников

```powershell
git clone https://github.com/mmbu/pdf-editor.git
cd pdf-editor
python -m pip install -r requirements.txt
python main.py
```

Сборка `.exe`:

```powershell
.\build.bat
```

## Технологии

Python · PySide6 · PyMuPDF · Tesseract OCR · PyInstaller

## Лицензия

PyMuPDF распространяется под AGPL — при распространении приложения учитывайте условия лицензии.
