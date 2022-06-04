from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QStackedLayout
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QSize


from view.vehicle.can_view import CanView
from view.vehicle.data_view import DataView
from view.vehicle.test_view import TestView

from utils import xbee
from model.message_models import ReceiveMessageModel

from actions import onFileAction1, onFileAction2


class VehicleWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        #self.connection = xbee.XBee("COM7", 115200)
        #self.receive_model = ReceiveMessageModel()

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
    
    # def add(self):
    #     """
    #     Add an item to our todo list, getting the text from the QLineEdit .todoEdit
    #     and then clearing it.
    #     """
    #     text = self.todoEdit.text()
    #     if text: # Don't add empty strings.
    #         # Access the list via the model.
    #         self.model.todos.append((False, text))
    #         # Trigger refresh.
    #         self.model.layoutChanged.emit()
    #         # Empty the input
    #         self.todoEdit.setText("")
