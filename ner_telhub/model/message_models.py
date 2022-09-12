from typing import Any, List
from PyQt6.QtCore import (
    QAbstractListModel, Qt,
    QModelIndex
)

from ner_processing.data import Data
from ner_processing.message import Message
from ner_telhub.model.data_models import DataModelManager


class MessageModel(QAbstractListModel):
    """
    A model class to represent the list of messages in the application.
    """

    def __init__(self, data_model: DataModelManager = None) -> None:
        """
        Initializes the list of messages and a potential data model to forward to.
        """
        super(MessageModel, self).__init__()
        self._messages: List[Message] = []
        self._model = data_model

    def data(self, index: QModelIndex, role: int) -> Any:
        """
        Retrieves messages from the model.
        """
        if role == Qt.ItemDataRole.DisplayRole:
            message = self._messages[index.row()]
            return str(message)

    def rowCount(self, index=None) -> int:
        """
        Finds the number of data rows in the model.
        """
        return len(self._messages)

    def addMessage(self, msg: Message) -> None:
        """
        Add a message to the model.
        """
        self._messages.append(msg)
        try:
            data_list: List[Data] = msg.decode()
            self._model.addDataList(data_list)
        except:
            pass # TODO: Add error detection
        self.layoutChanged.emit()

    def deleteMessage(self, index: QModelIndex) -> None:
        """
        Removes a message from the model.
        """
        self._messages.pop(index.row())
        self.layoutChanged.emit()

        

