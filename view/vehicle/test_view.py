from PyQt6.QtWidgets import QLabel, QHBoxLayout, QWidget

class TestView(QWidget):
    def __init__(self):
        super(TestView, self).__init__()
        layout = QHBoxLayout()
        layout.addWidget(QLabel("This is the Test view"))
        self.setLayout(layout)