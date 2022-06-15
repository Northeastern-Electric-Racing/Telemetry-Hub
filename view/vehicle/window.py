from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QStackedLayout, 
    QMessageBox, QDialog, QDialogButtonBox,
    QVBoxLayout, QLabel, QGridLayout, 
    QRadioButton, QButtonGroup
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QSize

from view.vehicle.can_view import CanView
from view.vehicle.data_view import DataView
from view.vehicle.test_view import TestView

from utils.xbee import XBee, XBeeException

from model.message_models import MessageModel


class VehicleWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.model = MessageModel()
        self.connection = XBee(self.model)
        self.port_name = None

        self.views = {
            0: ("CAN", CanView()), 
            1: ("Data", DataView()), 
            2: ("Test", TestView(self.model))
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

        file_action_1 = QAction("connect", self)
        file_action_2 = QAction("disconnect", self)
        file_action_1.triggered.connect(self.connect)
        file_action_2.triggered.connect(self.disconnect)
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

    def connect(self):
        dlg = ConnectionDialog(self)
        port_status = dlg.exec()

        # If a proper port was selected
        if port_status == 1:
            msg = QMessageBox(self)
            msg.setWindowTitle("Connection Status")

            try:
                self.connection.start(self.port_name)
                msg.setText(f"Successfully connected to {self.port_name}")
            except XBeeException as xe:
                msg.setText(xe.message)

            msg.exec()

    def disconnect(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Disconnection Status")

        try:
            self.connection.stop()
            msg.setText("Successfully disconnected from the serial port")
            self.port_name = None
        except XBeeException as xe:
                msg.setText(xe.message)

        msg.exec()



class ConnectionDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)

        self.setWindowTitle("Wireless Connection")

        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel("Choose from the available ports:"))

        self.ports = XBee.port_info()

        if len(self.ports) == 0:
            self.layout.addWidget(QLabel("No connections found"))

        self.com_options = []
        for i in range(len(self.ports)):
            self.com_options.append(QRadioButton(f"{self.ports[i][0]} - {self.ports[i][1]}"))
            self.layout.addWidget(self.com_options[i])

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttonBox.accepted.connect(self.on_accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
    
    def on_accept(self):
        for i in range(len(self.com_options)):
            if self.com_options[i].isChecked():
                print("Connecting to port: ", self.com_options[i].text())
                self.parentWidget().port_name = self.ports[i][0]
                self.accept()
                return
            self.reject()
            