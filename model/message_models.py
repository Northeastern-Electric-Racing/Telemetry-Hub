from PyQt6.QtCore import QAbstractListModel, Qt


class MessageFormatException(Exception):
    """A class to represent exceptions related to invalid message formats.
    
    Attributes
    ----------
    message : str
        Message to describe the exception
    status : int
        status code to denote the error type, one of:
            0 - incomplete (missing data)
            1 - malformed fields
            2 - other
    """

    def __init__(self, message, status):
        self.message = message
        self.status = status



class Message:
    """A class to represent a message coming from/to the car.

    Attributes
    ----------
    timestamp : int
        unix timestamp (seconds since Jan 1st, 1970)
    id : int
        id number of the message
    length : int
        number of data bytes
    data : list[int]
        array of of data bytes

    Methods
    -------
    """
    start_token = "s"

    def __init__(self, timestamp, id, length, data):
        if any(arg is None for arg in (timestamp, id, length, data)):
            raise MessageFormatException("Must specify all fields", 0)
        if length != len(data):
            raise MessageFormatException("The specified length does not match the data length", 2)
        # TODO: Add more error checking of the fields - error type 1

        self.timestamp = timestamp
        self.id = id
        self.length = length
        self.data = data

    def __str__(self):
        return f"{self.timestamp} - {self.id} - {self.length} - {self.data}"

    @staticmethod
    def parse_message(msg):
        """Parses a string message into its fields"""

        fields = msg.strip().split(" ")
        if len(fields) < 3:
            raise MessageFormatException("Not enough fields in the message", 0)
        
        try:
            timestamp = int(fields[0])
            id = int(fields[1])
            length = int(fields[2])  # get the data length to use for processing data array
            data = []

            if len(fields) < (3 + length):
                raise MessageFormatException("Too few data bytes", 0)
            elif len(fields) > (3 + length):
                raise MessageFormatException("Too many data bytes", 2)

            for i in range(length):
                data.append(int(fields[i + 3]))

            return (timestamp, id, length, data)
        except ValueError:
            raise MessageFormatException("Message has malformed fields", 1)




class MessageModel(QAbstractListModel):
    """A model class to represent the list of messages in the application.

    Attributes
    ----------
    messages : list[Message]
        list of messages in the system

    Methods
    -------
    addMessage(timestamp, id, length, data)
        Adds a message to the model
    deleteMessage(index)
        Removes a message from the model
    """

    def __init__(self, *args, **kwargs):
        super(MessageModel, self).__init__(*args, **kwargs)
        self._messages = []

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            message = self._messages[index.row()]
            return str(message)

    def rowCount(self, index):
        return len(self._messages)

    def addMessage(self, timestamp, id, length, data):
        self._messages.append(Message(timestamp, id, length, data))
        self.layoutChanged.emit()

    def deleteMessage(self, index):
        del self._messages[index.row()]
        self.layoutChanged.emit()
        


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

    def deleteFilter(self, index):
        del self._filters[index.row()]



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

    def deleteFilter(self, index):
        del self._filters[index.row()]

