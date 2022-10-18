from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QStackedLayout, 
    QMessageBox, QDialog, QDialogButtonBox, QHBoxLayout,
    QVBoxLayout, QLabel, QGridLayout, 
    QRadioButton, QButtonGroup
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QSize

from ner_telhub.view.vehicle.can_view import CanView
from ner_telhub.view.vehicle.data_view import DataView
from ner_telhub.view.vehicle.test_view import TestView

from ner_telhub.view.sd_card.window import FileView
from ner_telhub.view.sd_card.window import ProcessView
from ner_telhub.model.file_models import FileModel
from ner_telhub.widgets.menu_widgets import MessageIds, DataIds

from ner_processing.live.xbee import XBee, XBeeException
from ner_telhub.model.data_models import DataModelManager
from ner_telhub.model.message_models import MessageModel
from ner_telhub.model.filter_models import ReceiveFilterModel, SendFilterModel



class ConnectionDialog(QDialog):
    """
    Connection dialog showing serial port connection information.
    """
    
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
        self.buttonBox.accepted.connect(self.onAccept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
    
    def onAccept(self):
        for i in range(len(self.com_options)):
            if self.com_options[i].isChecked():
                print("Connecting to port: ", self.com_options[i].text())
                self.parentWidget().port_name = self.ports[i][0]
                self.accept()
                return
            self.reject()


class VehicleWindow(QMainWindow):
    """
    Main vehicle window containing various views.
    """

    def __init__(self):
        super().__init__()

        self.data_model = DataModelManager()
        self.message_model = MessageModel(self.data_model)
        self.receive_filter_model = ReceiveFilterModel()
        self.send_filter_model = SendFilterModel()
        self.connection = XBee(self.message_model)
        self.port_name = None

        self.views = {
            0: ("CAN", CanView(self.message_model, self.receive_filter_model, self.send_filter_model)), 
            1: ("Data", DataView(self.data_model))
        }

        # Window config
        self.setWindowTitle("Telemetry Hub")
        self.setMinimumSize(QSize(800, 480))

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
        edit_menu = menu.addMenu("Edit")
        help_menu = menu.addMenu("Help")
        views_menu = menu.addMenu("View")

        file_action_1 = QAction("connect", self)
        file_action_2 = QAction("disconnect", self)
        file_action_1.triggered.connect(self.connect)
        file_action_2.triggered.connect(self.disconnect)
        file_menu.addAction(file_action_1)
        file_menu.addAction(file_action_2)

        file_model = FileModel()

        help_action_1 = help_menu.addAction("Message Info")
        help_action_2 = help_menu.addAction("Data Info")
        help_action_1.triggered.connect(lambda : MessageIds(self).show())
        help_action_2.triggered.connect(lambda : DataIds(self).show())

        # Setup window
        hlayout = QHBoxLayout()
        hlayout.addWidget(FileView(file_model))
        hlayout.addWidget(ProcessView(file_model, self.data_model))

        views_select_can = QAction(self.views.get(0)[0], self)
        views_select_data = QAction(self.views.get(1)[0], self)
        views_select_can.triggered.connect(self.selectCanView)
        views_select_data.triggered.connect(self.selectDataView)
        views_menu.addAction(views_select_can)
        views_menu.addAction(views_select_data)

        self.current_view_menu = menu.addMenu(self.views.get(self.main_layout.currentIndex())[0])
        self.current_view_menu.setDisabled(True)
    
    def selectCanView(self):
        self.main_layout.setCurrentIndex(0)
        self.current_view_menu.setTitle(self.views.get(0)[0])

    def selectDataView(self):
        self.main_layout.setCurrentIndex(1)
        self.current_view_menu.setTitle(self.views.get(1)[0])

    def connect(self):
        dlg = ConnectionDialog(self)
        port_status = dlg.exec()

        # If a proper port was selected
        if port_status == 1:
            try:
                self.connection.start(self.port_name)
                msg = "Successfully connected to " + self.port_name
            except XBeeException as xe:
                msg = xe.message
            QMessageBox.information(self, "Connection Status", msg)

    def disconnect(self):
        try:
            self.connection.stop()
            msg = "Successfully disconnected from the serial port"
            self.port_name = None
        except XBeeException as xe:
            msg = xe.message
        QMessageBox.information(self, "Disconnection Status", msg)


            