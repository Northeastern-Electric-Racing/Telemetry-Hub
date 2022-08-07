from typing import List
from PyQt6.QtCore import QAbstractListModel, Qt

from model.data.utils import process_data_bytes
from model.data_models import DataModel


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

    def processData(self, model: DataModel):
        """Processes this model's log file paths, storing results in the given data model."""
        self.processFileData(self.__filepaths, model)

    @staticmethod
    def processFileData(filepaths: List[str], model: DataModel):
        for fp in filepaths:
            print("Processing file path: ", fp)
            with open(fp) as file:
                line_count = 0
                for line in file:
                    line_count += 1
                    info = line.strip().split(" ")

                    # Get the individual fields for each message
                    try:
                        timestamp, can_id, length, data = (
                            info[0],
                            info[1],
                            info[2],
                            process_data_bytes(info[3:][0]),
                        )
                    except:
                        print("Bad line structure: file - ", fp, ", line - ", line_count)

                    model.addData(can_id, timestamp, length, data)


