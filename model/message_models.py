
from PyQt6.QtCore import QAbstractListModel, Qt

class ReceiveMessageModel(QAbstractListModel):
    """A class to represent the desired receive messages from the car."""
    def __init__(self, *args, messages=None, **kwargs):
        super(ReceiveMessageModel, self).__init__(*args, **kwargs)
        self.messages = messages or []

    def data(self, index, role):
        """Handles requests for data from the view.

        Args:
            index: position of the data (row and column index)
            role: type of data requested
        Returns:
            id: id of the data
            interval: receive interval
        """
        if role == Qt.ItemDataRole.DisplayRole:
            id, interval = self.messages[index.row()]
            return id, interval
    
    def rowCount(self, index):
        return len(self.messages)

