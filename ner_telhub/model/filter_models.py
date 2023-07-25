from typing import List, Any, Tuple
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import (
    QAbstractListModel, Qt,
    QModelIndex
)
from ner_telhub.model.message_model import MessageModel


class ReceiveFilterModel(QAbstractListModel):
    """
    A model class to represent the desired messages to receive from the car.
    """

    def __init__(self, parent: QWidget, message_model: MessageModel) -> None:
        """
        Initializes the list of filters.
        """
        super(ReceiveFilterModel, self).__init__(parent)
        self._filters: List[Tuple[int, int]] = []
        self.message_model = message_model

    def data(self, index: QModelIndex, role: int) -> Any:
        """
        Retrieves filters from the model.
        """
        if role == Qt.ItemDataRole.DisplayRole:
            id, interval = self._filters[index.row()]
            return f"ID - {id}, Int - {interval} ms"

    def rowCount(self, index=None) -> int:
        """
        Finds the number of data rows in the model.
        """
        return len(self._filters)

    def addFilter(self, id: int, interval: int = 0) -> None:
        """
        Adds a filter to the model.
        """
        for filter in self._filters:
            if filter[0] == id:
                raise RuntimeError("Data ID is already in filter list.")
        self._filters.append((id, interval))
        self.message_model.addFilter(id, interval)
        self.layoutChanged.emit()

    def deleteFilter(self, index: QModelIndex) -> None:
        """
        Removes a filter from the model.
        """
        id, _ = self._filters.pop(index.row())
        self.message_model.deleteFilter(id)
        self.layoutChanged.emit()
