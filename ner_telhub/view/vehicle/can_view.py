from PyQt6.QtWidgets import (
    QLabel, QLineEdit, QHBoxLayout,
    QVBoxLayout, QWidget, QListView,
    QGridLayout, QCheckBox, QMessageBox,
    QComboBox, QRadioButton, QDialogButtonBox,
    QDialog
)
from PyQt6.QtCore import Qt

from ner_live.live_input import LiveInput, LiveInputException
from ner_live.xbee import XBee
from ner_processing.master_mapping import MESSAGE_IDS
from ner_telhub.widgets.styled_widgets import NERButton
from ner_telhub.model.filter_models import ReceiveFilterModel
from ner_telhub.model.data_models import DataModelManager
from ner_telhub.model.message_models import MessageModel


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
            self.com_options.append(
                QRadioButton(f"{self.ports[i][0]} - {self.ports[i][1]}"))
            self.layout.addWidget(self.com_options[i])

        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
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


class ReceiveFilters(QWidget):
    """
    Section to define inputs for adding receive filters.
    """

    def __init__(self, parent: QWidget, model: ReceiveFilterModel):
        super(ReceiveFilters, self).__init__(parent)

        # Define basic widgets
        self.header = QLabel("Receive Filters")
        ids = ["None", *[self.messageToText(d) for d in MESSAGE_IDS]]
        self.id_entry = QComboBox()
        self.id_entry.addItems(ids)
        self.interval_entry = QLineEdit()

        self.filter_view = QListView()
        self.model = model
        self.filter_view.setModel(self.model)

        self.add_button = NERButton("Add", NERButton.Styles.BLUE)
        self.del_button = NERButton("Delete", NERButton.Styles.RED)
        self.add_button.pressed.connect(self.add)
        self.del_button.pressed.connect(self.delete)

        # Style basic widgets
        self.header.setStyleSheet("font-size: 30px; font-weight: bold")
        self.header.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        inputs_layout = QGridLayout()
        inputs_layout.addWidget(QLabel("ID:"), 0, 0)
        inputs_layout.addWidget(self.id_entry, 0, 1)
        inputs_layout.addWidget(QLabel("Interval (ms):"), 0, 2)
        inputs_layout.addWidget(self.interval_entry, 0, 3)

        buttons_layout = QVBoxLayout()
        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.del_button)

        display_layout = QHBoxLayout()
        display_layout.addWidget(self.filter_view)
        display_layout.addLayout(buttons_layout)

        layout = QVBoxLayout()
        layout.addWidget(self.header)
        layout.addLayout(inputs_layout)
        layout.addLayout(display_layout)
        self.setLayout(layout)

    def add(self):
        if self.id_entry.currentText() == "None":
            QMessageBox.critical(self, "Input Error", "Must select an id.")
            return

        try:
            id = int(self.id_entry.currentText().split(":")[0])
            interval = int(self.interval_entry.text()
                           ) if self.interval_entry.text() != "" else 0
            self.model.addFilter(id, interval)
        except RuntimeError:
            QMessageBox.critical(
                self,
                "Input Error",
                f"Filter with ID {id} already exists")
        except Exception:
            QMessageBox.critical(
                self, "Input Error", "Error with the input fields.")

        self.id_entry.setCurrentText("None")
        self.interval_entry.setText("")

    def delete(self):
        indexes = self.filter_view.selectedIndexes()
        if indexes:
            index = indexes[0]
            self.model.deleteFilter(index)
            self.filter_view.clearSelection()

    def messageToText(self, id):
        return str(id) + ": " + MESSAGE_IDS[id]["description"]


class MessageFeed(QWidget):
    """
    Section showing the current message feed.
    """

    def __init__(self, parent: QWidget, model: MessageModel):
        super(MessageFeed, self).__init__(parent)

        self.view = QListView()
        self.model = model
        self.view.setModel(self.model)

        self.store_messages = False
        self.store_message_checkbox = QCheckBox(
            "record messages (only use for debugging purposes)")
        self.store_message_checkbox.setChecked(self.store_messages)
        self.store_message_checkbox.setToolTip(
            "Record raw messages to be able to see them in the above box.")
        self.model.setRecordState(self.store_messages)
        self.store_message_checkbox.stateChanged.connect(
            lambda state: self.model.setRecordState(state))

        layout = QVBoxLayout()
        layout.addWidget(self.view)
        layout.addWidget(self.store_message_checkbox)

        self.setLayout(layout)


class LiveMonitoring(QWidget):
    """
    Portion of the UI that shows live input configuring and monitoring information.
    """

    def __init__(
            self,
            parent: QWidget,
            data_model: DataModelManager,
            live_input: LiveInput):
        super(LiveMonitoring, self).__init__(parent)

        self.setMinimumWidth(300)

        self.data_model = data_model
        self.data_model.layoutChanged.connect(self.modelUpdated)
        self.live_input = live_input
        self.connected = False
        self.port_name = None

        self.connect_button = NERButton(
            "Setup Connection", NERButton.Styles.GREEN)
        self.connect_button.setToolTip(
            "Connect/Disconnect from a live input source")
        self.connect_button.pressed.connect(self.connect)

        self.connection_label = QLabel("None")
        self.datacount_label = QLabel("0")
        self.biterror_label = QLabel("0")
        self.valueerror_label = QLabel("0")

        label_layout = QGridLayout()
        label_layout.addWidget(QLabel("Connection:"), 0, 0)
        label_layout.addWidget(self.connection_label, 0, 1)
        label_layout.addWidget(QLabel("Data Count:"), 1, 0)
        label_layout.addWidget(self.datacount_label, 1, 1)
        label_layout.addWidget(QLabel("Bit Errors:"), 2, 0)
        label_layout.addWidget(self.biterror_label, 2, 1)
        label_layout.addWidget(QLabel("Value Errors:"), 3, 0)
        label_layout.addWidget(self.valueerror_label, 3, 1)

        layout = QVBoxLayout()
        layout.addWidget(self.connect_button)
        layout.addLayout(label_layout)
        self.setLayout(layout)

    def modelUpdated(self):
        self.datacount_label.setText(str(self.data_model.getDataCount()))

    def connect(self):
        if not self.connected:
            # Try to connect
            dlg = ConnectionDialog(self)
            port_status = dlg.exec()

            # If a proper port was selected
            if port_status == 1:
                try:
                    self.live_input.connect(self.port_name)
                    msg = "Successfully connected to " + self.port_name
                    self.connect_button.setText("Disconnect")
                    self.connect_button.changeStyle(NERButton.Styles.RED)
                    self.connected = True
                    self.connection_label.setText(self.port_name)
                except LiveInputException as e:
                    msg = e.message
                except TypeError as e:
                    msg = "Internal Error"
            QMessageBox.information(self, "Connection Status", msg)
        else:
            # Try to disconnect
            try:
                self.live_input.disconnect()
                msg = "Successfully disconnected from the serial port"
                self.port_name = None
                self.connect_button.setText("Setup Connection")
                self.connect_button.changeStyle(NERButton.Styles.GREEN)
                self.connection_label.setText("None")
                self.connected = False
            except LiveInputException as e:
                msg = e.message
            QMessageBox.information(self, "Disconnection Status", msg)


class CanView(QWidget):
    """
    Main CAN view class.
    """

    def __init__(self, parent: QWidget,
                 message_model: MessageModel,
                 data_model: DataModelManager,
                 receive_filter_model: ReceiveFilterModel,
                 live_input: LiveInput):
        super(CanView, self).__init__(parent)

        sub_layout = QHBoxLayout()
        sub_layout.addWidget(LiveMonitoring(self, data_model, live_input))
        sub_layout.addWidget(MessageFeed(self, message_model))

        layout = QVBoxLayout()
        layout.addLayout(sub_layout)
        layout.addWidget(ReceiveFilters(self, receive_filter_model))
        self.setLayout(layout)
