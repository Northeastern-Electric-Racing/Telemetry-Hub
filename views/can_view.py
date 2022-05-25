from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QLineEdit, 
    QHBoxLayout, QVBoxLayout, QWidget, QPushButton, 
    QMenu, QMenu
)
from PyQt6.QtGui import QAction, QPalette, QColor
from PyQt6.QtCore import QSize, Qt


class Color(QWidget):
    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(color))
        self.setPalette(palette)

class CanView(QWidget):
    def __init__(self):
        super(CanView, self).__init__()
        receive_layout = QHBoxLayout()
        receive_layout.addWidget(Color('red'))
        receive_layout.addWidget(Color('blue'))
        layout = QVBoxLayout()
        layout.addLayout(receive_layout)
        layout.addWidget(Color('green'))
        self.setLayout(layout)