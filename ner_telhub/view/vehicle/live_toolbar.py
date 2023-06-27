from PyQt6.QtWidgets import QMessageBox, QWidget
from ner_live.live_input import InputType, LiveInputException
from ner_live.utils import createConnection, deleteConnection, getConnection
from ner_telhub import colors
from ner_telhub.model.data_models import DataModelManager
from ner_telhub.model.message_model import MessageModel
from ner_telhub.view.vehicle.connection_dialog import ConnectionDialog
from ner_telhub.view.vehicle.file_dialog import FileDialog
from ner_telhub.widgets.styled_widgets.ner_button import NERButton
from ner_telhub.widgets.styled_widgets.ner_toolbar import NERToolbar

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
        if not self.started:
            FileDialog(self, self.model).exec()
        else:
            QMessageBox.information(
                self,
                "Export failed",
                "Cannot export to CSV while collecting data.")
