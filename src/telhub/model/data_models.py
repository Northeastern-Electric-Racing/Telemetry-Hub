from datetime import datetime
from typing import List
from PyQt6.QtCore import QAbstractListModel, Qt

from model.processing.master_mapping import MESSAGE_IDS, DECODE_DATA, DATA_IDS
from model.processing.data import Data

import csv


class DataFormatException(Exception):
    """A class to represent exceptions related to invalid data formats."""

    def __init__(self, message):
        self.message = message


class DataModel(QAbstractListModel):
    """Represents a model for all data values."""

    def __init__(self, *args, **kwargs):
        super(DataModel, self).__init__(*args, **kwargs)
        #self.__data = [[0, 1], [1, 4], [2, 6], [3, 2], [4, 5], [5, 10]]
        self.__data: List[Data] = []


    def data(self, index, role) -> Data:
        if role == Qt.ItemDataRole.DisplayRole:
            data = self.__data[index.row()]
            return data


    def rowCount(self, index):
        return len(self.__data)


    def addRawData(self, id: int, timestamp: datetime, len: int, data: List[int]) -> None:
        """Processes the data array and adds value it to the model."""

        try:
            decoded_data = DECODE_DATA[MESSAGE_IDS[id]]["decoder"](data)
        except:
            raise DataFormatException(f"Invalid data format for can id {id}")

        # Add processed data into final list
        for data_id in decoded_data:
            self.addData(Data(timestamp, data_id, decoded_data[data_id]))


    def addData(self, data: Data) -> None:
        """Adds the data directly to the model."""

        self.__data.append(data)


    def exportCSV(self, path: str) -> None:
        """Exports the data in this model as a csv to the specified path."""

        header = ["time", "message_id", "description", "value"]
        with open(path, "w", encoding="UTF8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(header)

            for data in self.__data:
                str_time = data.timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                writer.writerow([str_time, data.id, DATA_IDS[data.id], data.value])
        
