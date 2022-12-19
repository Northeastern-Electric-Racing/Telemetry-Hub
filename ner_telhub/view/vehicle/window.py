from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QStackedLayout, 
    QMessageBox, QDialog, QDialogButtonBox,
    QVBoxLayout, QLabel, QRadioButton,
    QToolBar
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QSize

from ner_processing.live.xbee import XBee
from ner_processing.live.live_input import LiveInput, LiveInputException

from ner_telhub.model.data_models import DataModelManager
from ner_telhub.model.message_models import MessageModel
from ner_telhub.model.filter_models import ReceiveFilterModel, SendFilterModel
from ner_telhub.view.vehicle.can_view import CanView
from ner_telhub.view.vehicle.data_view import DataView
from ner_telhub.view.vehicle.fault_view import FaultView
from ner_telhub.widgets.menu_widgets import MessageIds, DataIds
from ner_telhub.widgets.styled_widgets import NERButton

class ConnectionDialog(QDialog):
    """
    Connection dialog showing serial port connection information.
    """
    
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.setWindowTitle("Wireless Connection")

        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel("Choose from the available ports:"))

        self.ports = XBee.serialPorts()

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
                self.parentWidget().port_name = self.ports[i][0]
                self.accept()
                return
            self.reject()


class LiveToolbar(QToolBar):
    def __init__(self, parent: QWidget, message_model: MessageModel, data_model: DataModelManager, input: LiveInput):
        super(LiveToolbar, self).__init__(parent)

        self.message_model = message_model
        self.model = data_model
        self.input = input
        self.feed_started = False

        self.setStyleSheet("background-color: white; padding: 5%")
        self.start_button = NERButton("Start", NERButton.Styles.GREEN)
        self.start_button.addStyle("margin-right: 5%")
        self.start_button.pressed.connect(self.start)
        clear_button = NERButton("Clear", NERButton.Styles.RED)
        clear_button.addStyle("margin-right: 5%")
        clear_button.pressed.connect(self.clear)
        record_button = NERButton("Record", NERButton.Styles.BLUE)
        record_button.addStyle("margin-right: 5%")
        record_button.pressed.connect(self.record)
        self.addWidget(self.start_button)
        self.addWidget(clear_button)
        self.addWidget(record_button)
    
    def start(self):
        if not self.feed_started:
            try:
                self.input.start()
                self.start_button.setText("Stop")
                self.start_button.changeStyle(NERButton.Styles.RED)
                self.start_button.addStyle("margin-right: 5%")
                self.feed_started = not self.feed_started
            except LiveInputException as e:
                QMessageBox.information(self, "Couldn't start input: ", e.message)
        else:
            try:
                self.input.stop()
                self.start_button.setText("Start")
                self.start_button.changeStyle(NERButton.Styles.GREEN)
                self.start_button.addStyle("margin-right: 5%")
                self.feed_started = not self.feed_started
            except LiveInputException as e:
                QMessageBox.information(self, "Couldn't stop input:", e.message)

    def clear(self):
        self.model.deleteAllData()
        self.message_model.deleteAllMessages()

    def record(self):
        pass


class VehicleWindow(QMainWindow):
    """
    Main vehicle window containing various views.
    """

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.data_model = DataModelManager(self)
        self.message_model = MessageModel(self, self.data_model)
        self.receive_filter_model = ReceiveFilterModel(self)
        self.send_filter_model = SendFilterModel(self)
        self.connection = XBee(self.message_model)
        self.connection.addCallback("vehicle", self.message_model.addMessage)
        self.port_name = None

        self.views = {
            0: ("CAN", CanView(self, self.message_model, self.receive_filter_model, self.send_filter_model)), 
            1: ("Data", DataView(self, self.data_model)),
            2: ("Faults", FaultView(self, self.receive_filter_model))
        }

        # Window config
        self.setWindowTitle("Telemetry Hub")
        self.setMinimumSize(QSize(800, 480))

        # Multi-view layout config
        self.stacked_layout = QStackedLayout()
        for view in self.views.values():
            self.stacked_layout.addWidget(view[1])
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(LiveToolbar(self, self.message_model, self.data_model, self.connection))
        self.main_layout.addLayout(self.stacked_layout)

        widget = QWidget(self)
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

        help_action_1 = help_menu.addAction("Message Info")
        help_action_2 = help_menu.addAction("Data Info")
        help_action_1.triggered.connect(lambda : MessageIds(self).show())
        help_action_2.triggered.connect(lambda : DataIds(self).show())

        views_select_can = QAction(self.views.get(0)[0], self)
        views_select_data = QAction(self.views.get(1)[0], self)
        views_select_fault = QAction(self.views.get(2)[0], self)
        views_select_can.triggered.connect(self.selectCanView)
        views_select_data.triggered.connect(self.selectDataView)
        views_select_fault.triggered.connect(self.selectFaultView)
        views_menu.addAction(views_select_can)
        views_menu.addAction(views_select_data)
        views_menu.addAction(views_select_fault)

        self.current_view_menu = menu.addMenu(self.views.get(self.stacked_layout.currentIndex())[0])
        self.current_view_menu.setDisabled(True)
    
    def selectCanView(self):
        self.stacked_layout.setCurrentIndex(0)
        self.current_view_menu.setTitle(self.views.get(0)[0])

    def selectDataView(self):
        self.stacked_layout.setCurrentIndex(1)
        self.current_view_menu.setTitle(self.views.get(1)[0])

    def selectFaultView(self):
        self.stacked_layout.setCurrentIndex(2)
        self.current_view_menu.setTitle(self.views.get(2)[0])
        self.

    def connect(self):
        dlg = ConnectionDialog(self)
        port_status = dlg.exec()

        # If a proper port was selected
        if port_status == 1:
            try:
                self.connection.connect(self.port_name)
                msg = "Successfully connected to " + self.port_name
            except LiveInputException as e:
                msg = e.message
            except TypeError as e:
                msg = "Internal Error"
            QMessageBox.information(self, "Connection Status", msg)

    def disconnect(self):
        try:
            self.connection.disconnect()
            msg = "Successfully disconnected from the serial port"
            self.port_name = None
        except LiveInputException as e:
            msg = e.message
        QMessageBox.information(self, "Disconnection Status", msg)

