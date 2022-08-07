from PyQt6.QtCore import QAbstractTableModel, Qt

from model.data.master_mapping import MESSAGE_IDS, DECODE_DATA
from model.data.data import Data


class DataFormatException(Exception):
    """A class to represent exceptions related to invalid data formats."""

    def __init__(self, message):
        self.message = message


class DataModel(QAbstractTableModel):
    """Represents a model for all data values."""

    def __init__(self, *args, **kwargs):
        super(DataModel, self).__init__(*args, **kwargs)
        self.__data = [[0, 1], [1, 4], [2, 6], [3, 2], [4, 5], [5, 10]] # TODO: modify to store Data values

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            data = self.__data[index.row()][index.column()]
            return data

    def rowCount(self, index):
        return len(self.__data)

    def columnCount(self, index):
        return len(self.__data)

    def addRawData(self, id, timestamp, len, data):
        """Processes the data array and adds value it to the model.""" 
        try:
            decoded_data = DECODE_DATA[MESSAGE_IDS[id]]["decoder"](data)
        except:
            raise DataFormatException("Invalid data format for can id ", id)

        # Add processed data into final list
        for data_id in decoded_data:
            self.addData(Data(timestamp, data_id, decoded_data[data_id]))

    def addData(self, data: Data):
        """Adds the data directly to the model."""
        self.__data.append(data)
        
