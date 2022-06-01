from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QLineEdit, 
    QHBoxLayout, QVBoxLayout, QWidget, QPushButton, 
    QSlider, QMenu, QSpinBox
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


class Feed(QWidget):
    def __init__(self):
        super(Feed, self).__init__()
        self.setFixedSize(QSize(800, 300))

        layout = QVBoxLayout()
        layout.addWidget(Color('red'))
        layout.addWidget(QPushButton("Start Feed"))

        self.setLayout(layout)


class ReceiveFilters(QWidget):
    def __init__(self):
            super(ReceiveFilters, self).__init__()
            self.setFixedSize(QSize(300, 150))

            layout = QVBoxLayout()

            header = QLabel("Receive Filters")
            font = header.font()
            font.setPointSize(30)
            header.setFont(font)
            header.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
            layout.addWidget(header)
            
            layout.addWidget(QLineEdit())
            layout.addWidget(QSlider(Qt.Orientation.Horizontal))
            layout.addWidget(QSpinBox())

            self.setLayout(layout)


class Message(QLineEdit):
    def __init__(self):
        super(Message, self).__init__()
        self.setFixedSize(QSize(300, 150))

        layout = QVBoxLayout()
        header = QLabel("Send Message")
        font = header.font()
        font.setPointSize(30)
        header.setFont(font)
        header.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        layout.addWidget(header)

        self.setLayout(layout)


class CanView(QWidget):
    def __init__(self):
        super(CanView, self).__init__()
        
        receive_layout = QHBoxLayout()
        receive_layout.addWidget(Message())
        receive_layout.addWidget(ReceiveFilters())

        layout = QVBoxLayout()
        layout.addLayout(receive_layout)
        layout.addWidget(Feed())

        self.setLayout(layout)