from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QLineEdit, 
    QHBoxLayout, QVBoxLayout, QWidget, QPushButton, 
    QMenu, QMenu, QStackedLayout
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QSize, Qt

from actions import onFileAction1, onFileAction2

from views.can_view import CanView
from views.data_view import DataView
from views.test_view import TestView


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.views = {
            0: ("CAN", CanView()), 
            1: ("Data", DataView()), 
            2: ("Test", TestView())
        }

        # Window config
        self.setWindowTitle("Telemetry Hub")
        self.setFixedSize(QSize(900, 500))

        # Multi-view config
        self.main_layout = QStackedLayout()
        for view in self.views.values():
            self.main_layout.addWidget(view[1])

        widget = QWidget()
        widget.setLayout(self.main_layout)
        self.setCentralWidget(widget)

        # Menu bar
        menu = self.menuBar()
        file_menu = menu.addMenu("File")
        help_menu = menu.addMenu("Edit")
        edit_menu = menu.addMenu("Help")
        views_menu = menu.addMenu("View")

        file_action_1 = QAction("file action 1", self)
        file_action_2 = QAction("file action 2", self)
        file_action_1.triggered.connect(onFileAction1)
        file_action_2.triggered.connect(onFileAction2)
        file_menu.addAction(file_action_1)
        file_menu.addAction(file_action_2)

        views_select_can = QAction(self.views.get(0)[0], self)
        views_select_data = QAction(self.views.get(1)[0], self)
        views_select_test = QAction(self.views.get(2)[0], self)
        views_select_can.triggered.connect(self.select_can_view)
        views_select_data.triggered.connect(self.select_data_view)
        views_select_test.triggered.connect(self.select_test_view)
        views_menu.addAction(views_select_can)
        views_menu.addAction(views_select_data)
        views_menu.addAction(views_select_test)

        self.current_view_menu = menu.addMenu(self.views.get(self.main_layout.currentIndex())[0])
        self.current_view_menu.setDisabled(True)

        
    
    def select_can_view(self):
        self.main_layout.setCurrentIndex(0)
        self.current_view_menu.setTitle(self.views.get(0)[0])
    def select_data_view(self):
        self.main_layout.setCurrentIndex(1)
        self.current_view_menu.setTitle(self.views.get(1)[0])
    def select_test_view(self):
        self.main_layout.setCurrentIndex(2)
        self.current_view_menu.setTitle(self.views.get(2)[0])



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