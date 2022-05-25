from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QLineEdit, 
    QHBoxLayout, QVBoxLayout, QWidget, QPushButton, 
    QMenu, QMenu, QStackedLayout
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QSize, Qt

from actions import onFileAction1, onFileAction2

from views.can_view import CanView


class Test_View(QWidget):
    def __init__(self):
        super(Test_View, self).__init__()
        layout = QHBoxLayout()
        layout.addWidget(QLabel("This is the TEST view"))
        self.setLayout(layout)

class Data_View(QWidget):
    def __init__(self):
        super(Data_View, self).__init__()
        layout = QHBoxLayout()
        layout.addWidget(QLabel("This is the TEST view"))
        self.setLayout(layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Window config
        self.setWindowTitle("Telemetry Hub")
        self.setFixedSize(QSize(900, 500))

        # Multi-view config
        main_layout = QStackedLayout()
        main_layout.addWidget(CanView())
        main_layout.addWidget(Test_View())
        main_layout.addWidget(Data_View())

        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

        # Menu bar
        menu = self.menuBar()

        file_menu = menu.addMenu("File")
        file_action_1 = QAction("file action 1", self)
        file_action_2 = QAction("file action 2", self)
        file_action_1.triggered.connect(onFileAction1)
        file_action_2.triggered.connect(onFileAction2)
        file_menu.addAction(file_action_1)
        file_menu.addAction(file_action_2)

        views_menu = menu.addMenu("View")
        views_select_can = QAction("CAN", self)
        views_select_data = QAction("Data/Graphs", self)
        views_select_test = QAction("Tests", self)
        views_menu.addAction(views_select_can)
        views_menu.addAction(views_select_data)
        views_menu.addAction(views_select_test)






class MainWindow1(QMainWindow):
    def __init__(self):
        super().__init__()

        self.button_is_checked = True
        
        self.setWindowTitle("Telemetry Hub")
        self.setFixedSize(QSize(900, 500))

        self.button = QPushButton("Start")
        self.button.clicked.connect(self.button_clicked)

        self.text_label = QLabel()
        self.event_label = QLabel()

        self.input = QLineEdit()
        self.input.textChanged.connect(self.text_label.setText)

        layout = QVBoxLayout()
        layout.addWidget(self.input)
        layout.addWidget(self.text_label)
        layout.addWidget(self.event_label)
        layout.addWidget(self.button)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)

    def contextMenuEvent(self, e):
        context = QMenu(self)
        context.addAction(QAction("test 1", self))
        context.addAction(QAction("test 2", self))
        context.addAction(QAction("test 3", self))
        context.exec(e.globalPos())

    def button_clicked(self):
        if self.button_is_checked:
            self.button.setText("Stop")
        else:
            self.button.setText("Start")

        self.button_is_checked = not self.button_is_checked
        print("The button was clicked")

    def mouseMoveEvent(self, e):
        self.event_label.setText("mouseMoveEvent")

    def mousePressEvent(self, e):
        self.event_label.setText("mousePressEvent")

    def mouseReleaseEvent(self, e):
        self.event_label.setText("mouseReleaseEvent")

    def mouseDoubleClickEvent(self, e):
        self.event_label.setText("mouseDoubleClickEvent")


app = QApplication([])

window = MainWindow()
window.show()

app.exec()