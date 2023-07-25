from PyQt6.QtWidgets import QToolBar, QHBoxLayout, QWidget, QSizePolicy

class NERToolbar(QToolBar):
    """
    Creates a Toolbar that supports adding Widgets to either side.
    """

    def __init__(self, parent=None):
        super(NERToolbar, self).__init__(parent)

        # Setup left side of toolbar
        left = QWidget()
        self.left_buttons = QHBoxLayout()
        self.left_buttons.setContentsMargins(0, 0, 0, 0)
        left.setLayout(self.left_buttons)
        self.addWidget(left)

        # Setup left spacer
        self.spacer1 = QWidget()
        self.spacer1.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed)
        self.addWidget(self.spacer1)

        # Setup middle of toolbar
        middle = QWidget()
        self.middle_buttons = QHBoxLayout()
        self.middle_buttons.setContentsMargins(0, 0, 0, 0)
        middle.setLayout(self.middle_buttons)
        self.addWidget(middle)

        # Setup right spacer
        self.spacer2 = QWidget()
        self.spacer2.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed)
        self.addWidget(self.spacer2)

        # Setup right side of toolbar
        right = QWidget()
        self.right_buttons = QHBoxLayout()
        self.right_buttons.setContentsMargins(0, 0, 0, 0)
        right.setLayout(self.right_buttons)
        self.addWidget(right)

    def addLeft(self, widget: QWidget):
        self.left_buttons.addWidget(widget)

    def addMiddle(self, widget: QWidget):
        self.middle_buttons.addWidget(widget)

    def addRight(self, widget: QWidget):
        self.right_buttons.addWidget(widget)
