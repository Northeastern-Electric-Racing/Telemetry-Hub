from typing import List
from PyQt6.QtCore import QAbstractListModel, Qt

from model.data_models import DataModel
from model.processing.decode_files import LogFormat, process_line


class FileModel(QAbstractListModel):
    """A model class to represent the log files in the system."""

    def __init__(self, *args, **kwargs):
        super(FileModel, self).__init__(*args, **kwargs)
        self.__filepaths = []
        self.file_format = LogFormat.TEXTUAL1 # Default format as binary is not supported yet

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

    def processData(self, model: DataModel) -> None:
        """Processes this model's log file paths, storing results in the given data model."""
        self.processFileData(self.__filepaths, model)

    @staticmethod
    def processFileData(filepaths: List[str], model: DataModel) -> None:
        for fp in filepaths:
            print("Processing file path: ", fp)
            with open(fp) as file:
                line_count = 0
                for line in file:
                    line_count += 1
                    try:
                        timestamp, id, length, data = process_line(line, LogFormat.TEXTUAL1) # TODO: Make this user selectable
                    except:
                        print("Bad line structure: file - ", fp, ", line - ", line_count)
                    try:
                        model.addRawData(id, timestamp, length, data)
                    except Exception as e:
                        print("Error processing data value: file - ", fp, ", line - ", line_count)
                        print("  ", e)


