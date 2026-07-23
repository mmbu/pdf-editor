import sys

from PySide6.QtWidgets import QApplication

from app.ui.main_window import MainWindow
from app.ui.styles import APP_STYLESHEET

APP_VERSION = "1.0.0"


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("PDF Editor")
    app.setApplicationVersion(APP_VERSION)
    app.setStyleSheet(APP_STYLESHEET)
    window = MainWindow()
    window.setAcceptDrops(True)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
