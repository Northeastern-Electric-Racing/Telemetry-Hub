from PyQt6.QtWidgets import (
      QWidget, QVBoxLayout, QListView, QCheckBox
)
from ner_telhub.model.message_model import MessageModel

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
