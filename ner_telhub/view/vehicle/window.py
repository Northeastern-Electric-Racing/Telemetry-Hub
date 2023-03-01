from typing import Callable
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QStackedLayout,
    QMessageBox, QDialog, QDialogButtonBox,
    QVBoxLayout, QLabel, QLineEdit,
    QGridLayout, QFileDialog, QRadioButton,
    QComboBox
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QSize

from ner_live.live_input import LiveInput, LiveInputException, InputType
from ner_live.utils import getConnection, createConnection, deleteConnection
from ner_telhub import colors
from ner_telhub.model.data_models import DataModelManager
from ner_telhub.model.message_models import MessageModel
from ner_telhub.model.filter_models import ReceiveFilterModel
from ner_telhub.view.vehicle.can_view import CanView
from ner_telhub.view.vehicle.data_view import DataView
from ner_telhub.widgets.menu_widgets import MessageIds, DataIds
from ner_telhub.widgets.styled_widgets import NERButton, NERToolbar


class ConnectionDialog(QDialog):
    """
    Connection dialog showing serial port connection information.
    """

    def __init__(self, parent: QWidget, callback: Callable):
        super().__init__(parent)

        self.setWindowTitle("Wireless Connection")
        self.callback = callback
        self.layout = QVBoxLayout()

        self.layout.addWidget(QLabel("Choose from the available ports:"))
        self.ports = LiveInput.serialPorts()
        if len(self.ports) == 0:
            self.layout.addWidget(QLabel("No connections found"))
        self.com_options = []
        for i in range(len(self.ports)):
            self.com_options.append(
                QRadioButton(f"{self.ports[i][0]} - {self.ports[i][1]}"))
            self.layout.addWidget(self.com_options[i])

        self.layout.addWidget(QLabel("Choose an input source:"))
        self.input_entry = QComboBox()
        self.input_entry.addItems([it.name for it in InputType])
        self.layout.addWidget(self.input_entry)

        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttonBox.accepted.connect(self.onAccept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def onAccept(self):
        for i in range(len(self.com_options)):
            if self.com_options[i].isChecked():
                self.accept()
                self.callback(self.ports[i][0],
                              InputType[self.input_entry.currentText()])
                return
            self.reject()


class FileDialog(QDialog):
    """Dialog to export data to a CSV file."""

    def __init__(self, parent: QWidget, model: DataModelManager):
        super().__init__(parent)

        self.setWindowTitle("Export as CSV")
        self.model = model

        self.filename_input = QLineEdit()
        self.directory_input = QLineEdit()
        self.directory_button = NERButton("...", NERButton.Styles.GRAY)
        self.directory_button.addStyle("font-size: 20px")
        self.directory_button.setMaximumSize(45, 25)
        self.directory_button.pressed.connect(self.choose_directory)
        self.directory_button.setToolTip("Choose from file system")

        self.layout = QGridLayout()
        self.layout.addWidget(QLabel("File name: "), 0, 0)
        self.layout.addWidget(self.filename_input, 0, 1)
        self.layout.addWidget(QLabel("Directory name: "), 1, 0)
        self.layout.addWidget(self.directory_input, 1, 1)
        self.layout.addWidget(self.directory_button, 1, 2)

        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttonBox.accepted.connect(self.on_accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def choose_directory(self):
        dir = QFileDialog().getExistingDirectory(self)
        self.directory_input.setText(dir)

    def on_accept(self):
        try:
            filename = self.create_extension(self.filename_input.text())
        except BaseException:
            QMessageBox.critical(
                self,
                "Invalid File Name",
                "File must be either a .csv or contain no extension.")
            return

        directory = self.directory_input.text()
        full_path = directory + "/" + filename

        worker = self.model.getCSVWorker(full_path)
        worker.signals.error.connect(
            lambda error: QMessageBox.critical(
                self, "Export Error", error[1].__str__()))
        worker.signals.message.connect(
            lambda msg: QMessageBox.about(
                self, "Export Status", msg))
        try:
            worker.start()
        except RuntimeError as e:
            QMessageBox.critical(self, "Internal Error", str(e))
        self.accept()

    @staticmethod
    def create_extension(name: str):
        """Verifies the file name has a csv extension, or adds one if not."""
        components = name.split(".")
        if len(components) == 1:
            return name + ".csv"
        elif len(components) == 2 and components[1] == "csv":
            return name
        else:
            raise ValueError("Invalid file name format")


class LiveToolbar(NERToolbar):
    def __init__(
            self,
            parent: QWidget,
            message_model: MessageModel,
            data_model: DataModelManager):
        super(LiveToolbar, self).__init__(parent)

        self.message_model = message_model
        self.model = data_model
        self.connected = False
        self.started = False
        self.setStyleSheet(
            "QToolBar { background-color: " +
            colors.SECONDARY_BACKGROUND +
            "; padding: 5%; border: none}")

        self.connect_button = NERButton(
            "Setup Connection", NERButton.Styles.GREEN)
        self.connect_button.pressed.connect(self.changeConnection)
        self.connect_button.setToolTip(
            "Connect/disconnect from the live data feed")
        self.start_button = NERButton("Start", NERButton.Styles.GREEN)
        self.start_button.pressed.connect(self.start)
        self.start_button.setToolTip("Start/stop the live data feed")
        clear_button = NERButton("Clear Data", NERButton.Styles.RED)
        clear_button.pressed.connect(self.clear)
        clear_button.setToolTip("Clear all data currently received")
        export_button = NERButton("Export Data", NERButton.Styles.BLUE)
        export_button.pressed.connect(self.export)
        export_button.setToolTip("Export received data to a CSV file")
        self.addLeft(self.connect_button)
        self.addLeft(self.start_button)
        self.addRight(clear_button)
        self.addRight(export_button)

    def changeConnection(self):
        if not self.connected:
            # Try to connect
            dlg = ConnectionDialog(self, self._connect)
            status = dlg.exec()
            if status == 0:
                QMessageBox.critical(
                    self, "Error", "Invalid entries, please try again")
        else:
            # Try to disconnect
            try:
                getConnection().disconnect()
                deleteConnection()
                msg = "Successfully disconnected from the serial port"
                self.connect_button.setText("Setup Connection")
                self.connect_button.changeStyle(NERButton.Styles.GREEN)
                self.connected = False
            except LiveInputException as e:
                msg = e.message
            QMessageBox.information(self, "Disconnection Status", msg)

    def _connect(self, port_name: str, input_type: InputType):
        try:
            connection = createConnection(input_type, self.message_model)
            connection.connect(port_name)
            msg = "Successfully connected to " + port_name
            self.connect_button.setText("Disconnect")
            self.connect_button.changeStyle(NERButton.Styles.RED)
            self.connected = True
        except LiveInputException as e:
            msg = e.message
        except TypeError as e:
            msg = "Internal Error"
        QMessageBox.information(self, "Connection Status", msg)

    def start(self):
        if not self.connected:
            QMessageBox.critical(
                self, "Error", "Live input connection not set")
            return

        if not self.started:
            try:
                getConnection().start()
                self.start_button.setText("Stop")
                self.start_button.changeStyle(NERButton.Styles.RED)
                self.started = True
            except LiveInputException as e:
                QMessageBox.information(
                    self, "Couldn't start input: ", e.message)
        else:
            try:
                getConnection().stop()
                self.start_button.setText("Start")
                self.start_button.changeStyle(NERButton.Styles.GREEN)
                self.started = False
            except LiveInputException as e:
                QMessageBox.information(
                    self, "Couldn't stop input:", e.message)

    def clear(self):
        self.model.deleteAllData()
        self.message_model.deleteAllMessages()

    def export(self):
        if not self.feed_started:
            FileDialog(self, self.model).exec()
        else:
            QMessageBox.information(
                self,
                "Export failed",
                "Cannot export to CSV while collecting data.")


class VehicleWindow(QMainWindow):
    """
    Main vehicle window containing various views.
    """

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.data_model = DataModelManager(self)
        self.message_model = MessageModel(self, self.data_model)
        self.receive_filter_model = ReceiveFilterModel(
            self, self.message_model)

        self.views = {0: ("CAN",
                          CanView(self,
                                  self.message_model,
                                  self.data_model,
                                  self.receive_filter_model)),
                      1: ("Data",
                          DataView(self,
                                   self.data_model))}

        # Window config
        self.setWindowTitle("Telemetry Hub")
        self.setMinimumSize(QSize(960, 720))

        # Multi-view layout config
        self.stacked_layout = QStackedLayout()
        for view in self.views.values():
            self.stacked_layout.addWidget(view[1])
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(
            LiveToolbar(
                self,
                self.message_model,
                self.data_model))
        self.main_layout.addLayout(self.stacked_layout)

        widget = QWidget(self)
        widget.setLayout(self.main_layout)
        self.setCentralWidget(widget)

        # Menu bar
        menu = self.menuBar()
        help_menu = menu.addMenu("Help")
        views_menu = menu.addMenu("View")

        help_action_1 = help_menu.addAction("Message Info")
        help_action_2 = help_menu.addAction("Data Info")
        help_action_1.triggered.connect(lambda: MessageIds(self).show())
        help_action_2.triggered.connect(lambda: DataIds(self).show())

        views_select_can = QAction(self.views.get(0)[0], self)
        views_select_data = QAction(self.views.get(1)[0], self)
        views_select_can.triggered.connect(self.selectCanView)
        views_select_data.triggered.connect(self.selectDataView)
        views_menu.addAction(views_select_can)
        views_menu.addAction(views_select_data)

        self.current_view_menu = menu.addMenu(
            self.views.get(self.stacked_layout.currentIndex())[0])
        self.current_view_menu.setDisabled(True)

    def selectCanView(self):
        self.stacked_layout.setCurrentIndex(0)
        self.current_view_menu.setTitle(self.views.get(0)[0])

    def selectDataView(self):
        self.stacked_layout.setCurrentIndex(1)
        self.current_view_menu.setTitle(self.views.get(1)[0])
