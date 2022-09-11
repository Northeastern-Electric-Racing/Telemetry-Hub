from typing import List, Any, Tuple

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import (
    QAbstractListModel, Qt,
    QModelIndex
)


class ReceiveFilterModel(QAbstractListModel):
    """
    A model class to represent the desired messages to receive from the car.
    """

    def __init__(self, parent: QWidget) -> None:
        """
        Initializes the list of filters.
        """
        super(ReceiveFilterModel, self).__init__(parent)
        self._filters: List[Tuple[int, int]] = []

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
        self._filters.append((id, interval))
        self.layoutChanged.emit()

    def deleteFilter(self, index: QModelIndex) -> None:
        """
        Removes a filter from the model.
        """
        self._filters.pop(index.row())
        self.layoutChanged.emit()


class SendFilterModel(QAbstractListModel):
    """
    A model class to represent the desired messages to send to the car.
    """

    def __init__(self, parent: QWidget) -> None:
        """
        Initializes the list of filters.
        """
        super(SendFilterModel, self).__init__(parent)
        self._filters: List[Tuple[int, int, List[int]]] = []

    def data(self, index: QModelIndex, role: int) -> Any:
        """
        Retrieves filters from the model.
        """
        if role == Qt.ItemDataRole.DisplayRole:
            id, interval, data = self._filters[index.row()]
            return f"ID - {id}, Int - {interval} ms, Data - {data}"
    
    def rowCount(self, index=None) -> int:
        """
        Finds the number of data rows in the model.
        """
        return len(self._filters)

    def addFilter(self, id: int, interval: int, data: List[int]) -> None:
        """
        Adds a filter to the model.
        """
        self._filters.append((id, interval, data))
        self.layoutChanged.emit()

    def deleteFilter(self, index: QModelIndex) -> None:
        """
        Removes a filter from the model.
        """
        self._filters.pop(index.row())
        self.layoutChanged.emit()