import sys

from PySide6.QtWidgets import QApplication

from app.image import MainWindow
from app.database import init_db
from app.processor import process_folder


def main():

    app = QApplication(sys.argv)

    app.setStyleSheet("""

        QWidget#centralWidget {
            background-color: #111111;
            color: #eeeeee;
            font-family: Arial, Helvetica, sans-serif;
        }

        QWidget#viewerPage {
            background-color: #111111;
            color: #eeeeee;
            font-family: "Roboto", "Arial";
        }

        QLabel#viewerFilename {
            color: #ffffff;
            font-size: 16px;
            font-weight: bold;
        }

        QLabel#viewerFileInfo {
            color: #aaaaaa;
            font-size: 13px;
        }

        QLabel#viewerImage {
            background-color: #111111;
        }

        QPushButton#backButton,
        QPushButton#navigationButton {
            background-color: #292929;
            color: #eeeeee;
            border: 1px solid #3a3a3a;
            border-radius: 8px;
            padding: 9px 15px;
            font-size: 13px;
        }

        QPushButton#backButton:hover,
        QPushButton#navigationButton:hover {
            background-color: #404040;
        }

        QPushButton#navigationButton:disabled {
            color: #666666;
            background-color: #202020;
        }

        QLabel#pageTitle {
            color: #ffffff;
            font-size: 20px;
            font-weight: bold;
        }

        QLabel#subtitle {
            color: #888888;
            font-size: 13px;
        }

        QLineEdit#searchInput {
            background-color: #222222;
            color: #ffffff;
            border: 1px solid #303030;
            border-radius: 10px;
            padding: 11px 14px;
            font-size: 13px;
        }

        QLineEdit#searchInput:focus {
            border: 1px solid #666666;
        }

        QPushButton#refreshButton {
            background-color: #eeeeee;
            color: #111111;
            border: none;
            border-radius: 9px;
            padding: 11px 17px;
            font-weight: bold;
            font-size: 13px;
        }

        QPushButton#refreshButton:hover {
            background-color: #cccccc;
        }

        QScrollArea#galleryScrollArea {
            background-color: #111111;
            border: none;
        }

        QWidget#qt_scrollarea_viewport {
            background-color: #111111;
            border: none;
        }

        QWidget#gallery {
            background-color: #111111;
            border: none;
        }

        QWidget#galleryColumn {
            background-color: transparent;
            border: none;
        }

        QLabel#emptyLabel {
            color: #888888;
            font-size: 16px;
            padding: 30px;
        }

        QScrollBar:vertical {
            background: transparent;
            width: 8px;
            margin: 0;
        }

        QScrollBar::handle:vertical {
            background: #444444;
            border-radius: 4px;
            min-height: 30px;
        }

        QScrollBar::handle:vertical:hover {
            background: #666666;
        }

        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {
            height: 0;
        }

    """)

    init_db()

    # Initial scan
    for folder in MainWindow.FOLDERS:
        result = process_folder(folder)
        print(f"{folder}: {result}")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()