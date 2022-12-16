from typing import Any, List, Tuple, Dict

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import (
    QAbstractListModel, Qt,
    QModelIndex, QDateTime
)

from ner_processing.data import Data
from ner_processing.message import Message
from ner_telhub.model.data_models import DataModelManager


class MessageModel(QAbstractListModel):
    """
    A model class to represent the list of messages in the application.
    """

    def __init__(self, parent: QWidget, data_model: DataModelManager = None) -> None:
        """
        Initializes the list of messages and a potential data model to forward to.
        The filters store as a dictionary where:
          - the key is the id
          - the value is a tuple of the interval and the last time data was sent using the given id
        """
        super(MessageModel, self).__init__(parent)
        self._messages: List[Message] = []
        self._model = data_model
        self._record = False
        self._filters: Dict[int, Tuple[int, QDateTime]] = {}

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
        Add a message to the model if it matches the filters.
        """
        if not self._filters or msg.id in self._filters.keys():
            """
            If there are no filters or the message has a filtered id, continue.
            """
            if self._filters and self._filters[msg.id][1].msecsTo(msg.timestamp) >= self._filters[msg.id][0]:
                """
                If the message is past the interval, continue and set the last time.
                """
                self._filters[msg.id] = (self._filters[msg.id][0], msg.timestamp)

            elif self._filters:
                """
                If there are filters and the message is not past the interval, do not add the message.
                """
                return

            if self._record:
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

    def deleteAllMessages(self) -> None:
        """
        Removes a message from the model.
        """
        self._messages.clear()
        self.layoutChanged.emit()

    def setRecordState(self, state: bool) -> None:
        """
        Sets whether or not messages will be stored in the model (or data will just 
        be passed through to the data models).
        """
        self._record = state

    def getRecordState(self) -> bool:
        """
        Gets whether or not messages are being stored in the model.
        """
        return self._record

    def addFilter(self, id: int, interval: int) -> None:
        """
        Adds the given filter to the list of filters.
        """
        self._filters[id] = (interval, QDateTime.currentDateTime())

    def deleteFilter(self, index: QModelIndex):
        """
        Removes the filter with the given index.
        """
        self._filters.pop(index.row())

