from PyQt6.QtCore import QAbstractListModel, Qt


class MessageFormatException(Exception):
    """A class to represent exceptions related to invalid message formats."""

    def __init__(self, message, status):
        """
        Parameters
        ----------
        message : str
            Message to describe the exception
        status : int
            status code to denote the error type, one of:
                0 - incomplete (missing data)
                1 - malformed fields
                2 - other
        """
        self.message = message
        self.status = status



class Message:
    """A class to represent a message coming from/to the car."""

    start_token = "s"

    def __init__(self, timestamp, id, length, data):
        """
        Parameters
        ----------
        timestamp : float
            Unix timestamp (seconds since Jan 1st, 1970) with millisecond precision
        id : int
            Id number of the message
        length : int
            Number of data bytes
        data : list[int]
            Array of data bytes

        Raises
        ------
        MessageFormatException
            If the input parameters form an invalid message
        """

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
        """Overrides the string representation of the class."""
        return f"{self.timestamp} - {self.id} - {self.length} - {self.data}"

    @staticmethod
    def parse_message(msg):
        """Parses a string message into its fields.

        Parameters
        ----------
        msg : str
            Message to parse, in the form: "timestamp id length data1 data2 ..."

        Returns
        -------
        Message
            Message object formed from the parsed fields

        Raises
        ------
        MessageFormatException
            If the string cannot be parsed correctly
        """

        fields = msg.strip().split(" ")
        if len(fields) < 3:
            raise MessageFormatException("Not enough fields in the message", 0)
        
        try:
            timestamp = float(fields[0])
            id = int(fields[1])
            length = int(fields[2])  # get the data length to use for processing data array
            data = []

            if len(fields) < (3 + length):
                raise MessageFormatException("Too few data bytes", 0)
            elif len(fields) > (3 + length):
                raise MessageFormatException("Too many data bytes", 2)

            for i in range(length):
                data.append(int(fields[i + 3]))

            return Message(timestamp, id, length, data)
        except ValueError:
            raise MessageFormatException("Message has malformed fields", 1)




class MessageModel(QAbstractListModel):
    """A model class to represent the list of messages in the application."""

    def __init__(self, *args, **kwargs):
        super(MessageModel, self).__init__(*args, **kwargs)
        """Initializes the list of messages."""
        self._messages = []

    def data(self, index, role):
        """Retrieves items from the model

        Parameters
        ----------
        index : QModelIndex
            Index of the item to return
        role : ItemDataRole
            Format of the returned data, see docs

        Returns
        -------
        Any
            Varies for the type of ItemDataRole
        """
        if role == Qt.ItemDataRole.DisplayRole:
            message = self._messages[index.row()]
            return str(message)

    def rowCount(self, index):
        """Finds the number of data rows in the model

        Parameters
        ----------
        index : QModelIndex
            Index of a list item, not used

        Returns
        -------
        int
            The row count
        """
        return len(self._messages)

    def addMessage(self, msg):
        """Add a message to the model.

        Parameters
        ----------
        msg : Message
            Message to add to the model
        """
        self._messages.append(msg)
        self.layoutChanged.emit()

    def deleteMessage(self, index):
        """Removes a message from the model.

        Parameters
        ----------
        index : QModelIndex
            Index of the list item to remove
        """
        del self._messages[index.row()]
        self.layoutChanged.emit()
        

