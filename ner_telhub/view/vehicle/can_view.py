from PyQt6.QtWidgets import (
    QLabel, QLineEdit, QHBoxLayout,
    QVBoxLayout, QWidget, QListView,
    QGridLayout, QCheckBox, QMessageBox, QComboBox
)
from PyQt6.QtCore import Qt

from Ner_Processing.master_mapping import MESSAGE_IDS
from ner_telhub.widgets.styled_widgets import NERButton
from ner_telhub.model.filter_models import ReceiveFilterModel
from ner_telhub.model.message_models import MessageModel


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
            interval = int(self.interval_entry.text()) if self.interval_entry.text() != "" else 0
            self.model.addFilter(id, interval)
        except RuntimeError:
            QMessageBox.critical(self, "Input Error", f"Filter with ID {id} already exists")
        except Exception:
            QMessageBox.critical(self, "Input Error", "Error with the input fields.")

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
        self.store_message_checkbox = QCheckBox("record messages")
        self.store_message_checkbox.setChecked(self.store_messages)
        self.store_message_checkbox.setToolTip("Record raw messages to be able to see them in the above box.")
        self.model.setRecordState(self.store_messages)
        self.store_message_checkbox.stateChanged.connect(lambda state : self.model.setRecordState(state))

        layout = QVBoxLayout()
        layout.addWidget(self.view)
        layout.addWidget(self.store_message_checkbox)

        self.setLayout(layout)


class CanView(QWidget):
    """
    Main CAN view class.
    """
    
    def __init__(self, parent: QWidget,
            message_model: MessageModel, 
            receive_filter_model: ReceiveFilterModel):
        super(CanView, self).__init__(parent)

        filter_layout = QVBoxLayout()
        filter_layout.addWidget(ReceiveFilters(self, receive_filter_model))
        
        layout = QHBoxLayout()
        layout.addWidget(MessageFeed(self, message_model))
        layout.addLayout(filter_layout)

        self.setLayout(layout)