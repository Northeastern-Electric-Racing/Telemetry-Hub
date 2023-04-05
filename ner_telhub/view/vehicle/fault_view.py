from PyQt6.QtCore import Qt

from PyQt6.QtWidgets import (
    QLabel, QVBoxLayout, QWidget
)


class FaultView(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        # Dashboard title
        title_label = QLabel("Fault View")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")

        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        layout.addWidget(title_label, stretch=0)

        self.setLayout(layout)
