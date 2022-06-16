from PyQt6.QtCore import QAbstractListModel, Qt

from message_models import Message

class ReceiveFilterModel(QAbstractListModel):
    """A class to represent the desired messages to receive from the car.

    Attributes
    ----------
    filters : list[(int, int)]
        list of tuples representing an (id, time interval) filter pair

    Methods
    -------
    addFilter(id, interval)
        Adds a filter to the model
    deleteFilter(index)
        Removes a filter from the model
    """

    def __init__(self, *args, filters=None, **kwargs):
        super(ReceiveFilterModel, self).__init__(*args, **kwargs)
        self._filters = filters or []

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            id, interval = self._filters[index.row()]
            return f"id: {id} - {interval}ms"
    
    def rowCount(self, index):
        return len(self._filters)

    def addFilter(self, id, interval=0):
        self._filters.append((id, interval))
        self.layoutChanged.emit()

    def deleteFilter(self, index):
        del self._filters[index.row()]
        self.layoutChanged.emit()



class SendFilterModel(QAbstractListModel):
    """A class to represent the desired messages to send to the car.

    Attributes
    ----------
    filters : list[(Message, int)]
        list of tuples representing a (message, time interval) filter pair

    Methods
    -------
    addFilter(id, length, data, interval)
        Adds a filter to the model
    deleteFilter(index)
        Removes a filter from the model
    """

    def __init__(self, *args, filters=None, **kwargs):
        super(SendFilterModel, self).__init__(*args, **kwargs)
        self._filters = filters or []

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            message, interval = self._filters[index.row()]
            return f"id: {message.id} - {interval}ms"
    
    def rowCount(self, index):
        return len(self._filters)

    def addFilter(self, id, length, data, interval):
        self._filters.append((Message(0, id, length, data), interval))
        self.layoutChanged.emit()

    def deleteFilter(self, index):
        del self._filters[index.row()]
        self.layoutChanged.emit()
