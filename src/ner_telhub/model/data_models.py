import csv
from datetime import datetime
from typing import Iterable, List, Dict, Any
import numpy as np

from PyQt6.QtCore import (
    QAbstractListModel, Qt, QReadWriteLock,
    QReadLocker, QWriteLocker,
    pyqtSignal, pyqtBoundSignal
)

from model.processing.master_mapping import MESSAGE_IDS, DECODE_DATA, DATA_IDS
from model.processing.data import Data
from utils.threads import Worker


class DataFormatException(Exception):
    """A class to represent exceptions related to invalid data formats."""

    def __init__(self, message):
        self.message = message


class DataModel(QAbstractListModel):
    """Represents a model for all data values."""

    def __init__(self, *args, **kwargs):
        """Initializes the data list and mutex for thread access control."""

        super(DataModel, self).__init__(*args, **kwargs)
        self._data: List[Data] = []
        self._lock = QReadWriteLock()


    def data(self, index, role) -> Data:
        """Gets the data at the specified index in the specified form."""

        QReadLocker(self._lock)
        if role == Qt.ItemDataRole.DisplayRole:
            data = self._data[index.row()]
            return data


    def rowCount(self, index):
        """Returns the number of data elements."""

        return len(self._data)


    def addData(self, data: Data) -> None:
        """Adds the given data object to the model.
        
        Slow operation due to the locking of the mutex for a single data point. 
        For adding multiple elements at the same time, see addDataList().
        """

        QWriteLocker(self._lock)
        self._data.append(data)
        self.layoutChanged.emit()


    def addDataList(self, list: Iterable[Data]) -> None:
        """Adds a collection of data to this model."""

        QWriteLocker(self._lock)
        self._data.extend(list)
        self.layoutChanged.emit()


    def addRawData(self, id: int, timestamp: datetime, len: int, data: List[int]) -> None:
        """Processes the data and adds the value to the model.
        
        Slow operation due to the locking of the mutex for a single data point. 
        For adding multiple elements at the same time, process externally using
        processData() and add full list using addDataList().
        """

        QWriteLocker(self._lock)
        self._data.extend(self.processData(id, timestamp, len, data))
        self.layoutChanged.emit()


    @staticmethod
    def processData(id: int, timestamp: datetime, len: int, data: List[int]) -> List[Data]:
        """Processes the given message data into a list of data points."""

        try:
            decoded_data: Dict[int, Any] = DECODE_DATA[MESSAGE_IDS[id]]["decoder"](data)
        except:
            raise DataFormatException(f"Invalid data format for can id {id}")
        
        return [Data(timestamp, data_id, decoded_data[data_id]) for data_id in decoded_data]


    def getData(self) -> np.ndarray:
        """Gets a numpy array of the data currently in the model.
        
        WARNING: May block application if data model is large enough
        TODO: Add threading 
        """

        QReadLocker(self._lock)
        return np.array(self._data, Data)


    def deleteAll(self) -> None:
        """Removes all data from the model."""

        QWriteLocker(self._lock)
        self._data.clear()
        self.layoutChanged.emit()

    
    def filter(self, ids: List[int], keep_ids: bool = True) -> None:
        """Filters the given model using the given list of IDs. 
        
        The keep_ids flag specifies whether the given IDs should be the ones 
        that are kept or the ones that are removed from the model.
        TODO: Add support for filtering by timestamps
        """
        
        if keep_ids:
            filter_func = lambda d : d.id in ids
        else: 
            filter_func = lambda d : d.id not in ids

        QWriteLocker(self._lock)
        self._data = list(filter(filter_func, self._data))
        self.layoutChanged.emit()


    def getCSVWorker(self, path: str) -> Worker:
        """Returns a worker to export this model's data to a CSV file."""

        return Worker(self.exportCSV, file_path=path, data=self._data)


    @staticmethod
    def exportCSV(*args, **kwargs) -> None:
        """Exports the data in this model as a csv to the specified path.
        
        CAUTION
        -------
        This is a worker function meant to be called from a thread (see Worker).
        Is expecting the following external arguments:
            - kwargs["file_path"] : str
            - kwargs["data"] : List[Data]
        """

        try:
            path: str = kwargs["file_path"]
            data_list: List[Data] = kwargs["data"]
            progress_signal: pyqtBoundSignal = kwargs["progress"]
            message_signal: pyqtBoundSignal = kwargs["message"]
        except:
            raise RuntimeError("Internal processing error - thread configuration invalid")

        header = ["time", "data_id", "description", "value"]
        with open(path, "w", encoding="UTF8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(header)

            for data in data_list:
                str_time = data.timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                writer.writerow([str_time, data.id, DATA_IDS[data.id], data.value])
        message_signal.emit(f"Finished CSV export")
        
