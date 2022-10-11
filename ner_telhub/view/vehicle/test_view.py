from PyQt6.QtWidgets import (
    QLabel, QLineEdit, QGridLayout, 
    QVBoxLayout, QWidget, QListView
)
from PyQt6.QtCore import QDateTime

from ner_telhub.model.message_models import Message
from ner_telhub.widgets.styled_widgets import NERButton


class MessageFeed(QWidget):
    """
    Text box used for reading in the current message feed.
    """

    def __init__(self, model):
        super(MessageFeed, self).__init__()

        self.view = QListView()
        self.model = model
        self.view.setModel(self.model)

        self.timestamp_entry = QLineEdit()
        self.id_entry = QLineEdit()
        self.data_entry = QLineEdit()

        layout_entry = QGridLayout()
        layout_entry.addWidget(QLabel("Timestamp:"), 0, 0)
        layout_entry.addWidget(self.timestamp_entry, 0, 1)
        layout_entry.addWidget(QLabel("Id:"), 1, 0)
        layout_entry.addWidget(self.id_entry, 1, 1)
        layout_entry.addWidget(QLabel("Data:"), 2, 0)
        layout_entry.addWidget(self.data_entry, 2, 1)

        self.add_button = NERButton("Add")
        self.delete_button = NERButton("Delete")
        self.add_button.pressed.connect(self.add)
        self.delete_button.pressed.connect(self.delete)

        layout = QVBoxLayout()
        layout.addWidget(self.view)
        layout.addLayout(layout_entry)
        layout.addWidget(self.add_button)
        layout.addWidget(self.delete_button)

        self.setLayout(layout)

    def add(self):
        try:
            timestamp = QDateTime.fromMSecsSinceEpoch(int(float(self.timestamp_entry.text())*1000))
            id = int(self.id_entry.text())
            data = self.data_entry.text()
            data = [int(s) for s in data.split(" ")]

            msg = Message(timestamp, id, data)
            self.model.addMessage(msg)
        except Exception as e:
            # TODO: Add popup window for error
            print("Error with the fields")

        self.timestamp_entry.setText("")
        self.id_entry.setText("")
        self.data_entry.setText("")

    def delete(self):
        indexes = self.view.selectedIndexes()
        if indexes:
            # Indexes is a list of a single item in single-select mode.
            index = indexes[0]
            # Remove the item and refresh.
            self.model.deleteMessage(index)
            self.view.clearSelection()


class TestView(QWidget):
    """
    Window to use for testing access to the message models.
    """
    
    def __init__(self, model):
        super(TestView, self).__init__()
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Test view for adding messages to the application model"))
        layout.addWidget(MessageFeed(model))

        self.setLayout(layout)