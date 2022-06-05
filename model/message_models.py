from PyQt6.QtCore import QAbstractListModel, Qt


class MessageFormatException(Exception):
    """A class to represent exceptions related to invalid message formats"""

    def __init__(self, message):
        self.message = message


class Message:
    """A class to represent a message coming from/to the car."""

    def __init__(self, timestamp, id, length, data):
        if any(arg is None for arg in (timestamp, id, length, data)):
            raise MessageFormatException("Must specify all fields")
        if length != len(data):
            raise MessageFormatException("The specified length does not match the data length")
        # TODO: Add more error checking of the fields

        self._timestamp = timestamp
        self._id = id
        self._length = length
        self._data = data

    def __str__(self):
        return f"{self._timestamp} - {self._id} - {self._length} - {self._data}"



class MessageModel(QAbstractListModel):
    """A model class to represent the list of messages in the application."""

    def __init__(self, *args, messages=None, **kwargs):
        super(MessageModel, self).__init__(*args, **kwargs)
        self._messages = messages or []

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            message = self._messages[index.row()]
            return str(message)

    def rowCount(self, index):
        return len(self._messages)

    def addMessage(self, timestamp, id, length, data):
        """Add a message to the model."""
        self._messages.append(Message(timestamp, id, length, data))

    def deleteMessage(self, index):
        del self._messages[index.row()]
        


class ReceiveFilterModel(QAbstractListModel):
    """A class to represent the desired messages to receive from the car."""

    def __init__(self, *args, messages=None, **kwargs):
        super(ReceiveFilterModel, self).__init__(*args, **kwargs)
        self._messages = messages or []

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            id, interval = self._messages[index.row()]
            return id, interval
    
    def rowCount(self, index):
        return len(self._messages)


class SendFilterModel(QAbstractListModel):
    """A class to represent the desired messages to send to the car."""
    def __init__(self, *args, messages=None, **kwargs):
        super(SendFilterModel, self).__init__(*args, **kwargs)
        self._messages = messages or []

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            id, interval = self._messages[index.row()]
            return id, interval
    
    def rowCount(self, index):
        return len(self._messages)

