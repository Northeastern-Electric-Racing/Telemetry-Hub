from PyQt6.QtCore import QAbstractListModel, Qt


class FileModel(QAbstractListModel):
    """A model class to represent the log files in the system."""

    def __init__(self, *args, **kwargs):
        super(FileModel, self).__init__(*args, **kwargs)
        self.__filepaths = []

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            filepath = self.__filepaths[index.row()]
            return filepath

    def rowCount(self, index):
        return len(self.__filepaths)

    def addFile(self, filepath):
        self.__filepaths.append(filepath)
        self.layoutChanged.emit()

    def deleteFile(self, index):
        del self.__filepaths[index.row()]
        self.layoutChanged.emit()
