from PyQt6.QtCore import QAbstractTableModel, Qt


class DataModel(QAbstractTableModel):
    def __init__(self, *args, **kwargs):
        super(DataModel, self).__init__(*args, **kwargs)
        self._data = [[0, 1], [1, 4], [2, 6], [3, 2], [4, 5], [5, 10]]

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            message = self._data[index.row()][index.column()]
            return message

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self._data)
        
