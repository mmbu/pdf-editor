APP_STYLESHEET = """
QMainWindow, QWidget {
    background: #f8f9fb;
    color: #1f1f1f;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 13px;
}
QToolBar {
    background: #ffffff;
    border-bottom: 1px solid #e3e6ea;
    spacing: 6px;
    padding: 4px;
}
QToolButton {
    padding: 6px 10px;
}
QStatusBar {
    background: #ffffff;
    border-top: 1px solid #e3e6ea;
}
QPushButton {
    background: #ffffff;
    border: 1px solid #cfd6df;
    border-radius: 6px;
    padding: 6px 12px;
}
QPushButton:hover {
    background: #eef3ff;
    border-color: #4285f4;
}
QLineEdit, QListWidget, QScrollArea {
    background: #ffffff;
    border: 1px solid #d7dde5;
    border-radius: 4px;
}
QMenuBar::item:selected, QMenu::item:selected {
    background: #e8f0fe;
}
"""

SHORTCUTS_HELP = """
Горячие клавиши

Ctrl+O — открыть PDF (в редакторе)
Ctrl+S — сохранить как PDF (в редакторе)
Ctrl+Z — отменить
Ctrl+Y — повторить
Ctrl+H — на главный экран
F1 — эта справка
"""
