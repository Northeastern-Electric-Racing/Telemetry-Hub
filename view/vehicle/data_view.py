from PyQt6.QtWidgets import QLabel, QHBoxLayout, QWidget

class DataView(QWidget):
    def __init__(self):
        super(DataView, self).__init__()
        layout = QHBoxLayout()
        layout.addWidget(QLabel("This is the Data view"))
        self.setLayout(layout)