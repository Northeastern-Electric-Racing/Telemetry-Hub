from PyQt6.QtWidgets import (
    QMainWindow, QLabel
)
from PyQt6.QtCore import QSize


class DatabaseWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Telemetry Hub")
        self.setFixedSize(QSize(900, 500))

        self.setCentralWidget(QLabel("Database Window"))
