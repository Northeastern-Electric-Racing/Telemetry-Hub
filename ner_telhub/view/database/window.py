from PyQt6.QtWidgets import (
    QMainWindow, QLabel, QWidget
)
from PyQt6.QtCore import QSize


class DatabaseWindow(QMainWindow):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.setWindowTitle("Telemetry Hub")
        self.setFixedSize(QSize(900, 500))

        self.setCentralWidget(QLabel("Database Window"))
