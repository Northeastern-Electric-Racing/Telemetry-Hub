import csv
from datetime import datetime
import numpy as np
import sys
from typing import List, Any, Tuple

from PyQt6.QtCore import (
    QAbstractTableModel, Qt,
    QReadWriteLock, QModelIndex,
    QReadLocker, QWriteLocker,
    pyqtBoundSignal, pyqtSignal,
    QObject
)

from ner_processing.data import Data
from ner_processing.decode_statuses import getStatus, getStatuses
from ner_processing.master_mapping import DATA_IDS
from ner_telhub.utils.threads import Worker


class DataModel(QAbstractTableModel):
    """
    Represents a model for values of a single data type.
    """

    def __init__(self, id: int, parent: QObject = None) -> None:
        """
        Initializes the data list and mutex for thread access control.
        """
        super(DataModel, self).__init__(parent)
        if DATA_IDS.keys().__contains__(id):
            self._id = id
        else:
            raise ValueError("Invalid data id.")
        self._data: List[Tuple[datetime, Any]] = []
        self.error_count = 0
        self._lock = QReadWriteLock()
        self._reset_state()

    def _reset_state(self):
        QWriteLocker(self._lock)
        self._data.clear()
        self.error_count = 0
        self.min_value = sys.maxsize
        self.max_value = -sys.maxsize
        # Stores whether we are currently removing duplicated data values
        self.compressing = False

    def data(self, index: QModelIndex, role: int) -> Any:
        """
        Gets the data at the specified index in the specified form.
        """
        QReadLocker(self._lock)
        if role == Qt.ItemDataRole.DisplayRole:
            value = self._data[index.row()][index.column()]
            if isinstance(value, datetime):
                return int(value.timestamp() * 1000)
            return value

    def rowCount(self, index=None) -> int:
        """
        Returns the number of data elements.
        """
        return len(self._data)

    def columnCount(self, index=None) -> int:
        """
        Returns a fixed value of 2 for each data piece having a time and value.
        """
        return 2

    def getDataId(self) -> int:
        """
        Returns the fixed data id of this model.
        """
        return self._id

    def getDataType(self) -> str:
        """
        Returns the fixed data type of this model.
        """
        return DATA_IDS[self._id]["name"]

    def getErrorCount(self) -> int:
        """
        Returns the error count of this model.
        """
        return self.error_count

    def getData(self) -> List[Tuple[datetime, Any]]:
        """
        Gets the list of data currently in the model.
        """
        QReadLocker(self._lock)
        return self._data

    def getDataAsArray(self) -> np.ndarray:
        """
        Gets a numpy array of the data currently in the model.

        WARNING: May block application if data model is large enough
        TODO: Add threading
        """
        QReadLocker(self._lock)
        return np.array(self._data, Tuple[datetime, Any])

    def getMinTime(self) -> datetime:
        """
        Gets the time of the first data element (which is the min time for valid data sets).
        """
        QReadLocker(self._lock)
        try:
            return self._data[0][0]
        except IndexError:
            # Give big min time when no data
            return datetime.fromtimestamp(9999999999.999)

    def getMaxTime(self) -> datetime:
        """
        Gets the time of the last data element (which is the max time for valid data sets).
        """
        QReadLocker(self._lock)
        try:
            return self._data[len(self._data) - 1][0]
        except IndexError:
            # Give small max time when no data
            return datetime.fromtimestamp(0)

    def getMinValue(self) -> Any:
        """
        Gets the minimum value of the data in the model.
        """
        return self.min_value

    def getMaxValue(self) -> Any:
        """
        Gets the maximum value of the data in the model.
        """
        return self.max_value

    def addData(self, timestamp: datetime, value: Any) -> None:
        """
        Adds the given piece of data to the model.

        Performs filtering of numeric data values by checking for sudden spikes. A spike is
        recognized as a sudden change in value of both more than 1000 and greater than 100%
        of the previous value.

        Performs compression of consecutive data points with the same values to reduce storage.
        This is done by starting to 'compress' once two consecutive data points have the same
        value, and stoping when a new value is reached.
        """
        QWriteLocker(self._lock)
        # If the value is numeric, perform filtering (from wireless errors) and
        # bounds checking
        if isinstance(value, int) or isinstance(value, float):
            # Filter out erroneous data values
            if (len(self._data) != 0) and (DATA_IDS[self._id]["units"] != ""):
                last_value = self._data[-1][1]
                difference = abs(value - last_value)
                if (difference > last_value) and (difference > 1000):
                    self.error_count += 1
                    return
            # Check/update bounds
            if value < self.min_value:
                self.min_value = value
            if value > self.max_value:
                self.max_value = value

        # Add data point if it is distinct
        if len(self._data) == 0:
            self._data.append((timestamp, value))
        else:
            last_value = self._data[-1][1]
            if self.compressing:
                if value == last_value:
                    # Reset last value in list instead of adding on
                    self._data[-1] = (timestamp, value)
                else:
                    # Add new distinct value and stop compressing
                    self._data.append((timestamp, value))
                    self.compressing = False
            else:
                self._data.append((timestamp, value))
                if value == last_value:
                    self.compressing = True  # Start compressing if two consecutive values found

        self.layoutChanged.emit()

    def deleteAllData(self) -> None:
        """
        Deletes all data from the model.
        """
        QWriteLocker(self._lock)
        self._reset_state()
        self.layoutChanged.emit()


class DataModelManager(QObject):
    """
    Manager class for a group of data models.

    Offers a fast way to store and retrieve various types of data.
    If dealing with a single type of data, use DataModel.
    """

    layoutChanged = pyqtSignal()

    def __init__(self, parent: QObject) -> None:
        """
        Initializes the model manager.
        """
        super(DataModelManager, self).__init__(parent)
        self._datamap: dict[int, DataModel] = {}

    def _createModelIfNone(self, id: int) -> None:
        """
        Creates a data model for the given ID if none exists already.
        """
        if id not in self._datamap:
            self._datamap[id] = DataModel(id)
            self._datamap[id].moveToThread(self.thread())
            self._datamap[id].setParent(self)

    @staticmethod
    def getDataType(id: int) -> str:
        """
        Gets the type of data of the given ID.
        """
        if id in DATA_IDS:
            return DATA_IDS[id]["name"]
        else:
            raise ValueError("Invalid data ID")

    @staticmethod
    def getDecodedStatuses(data: Data) -> dict[str, int]:
        """
        Gets the decoded status of the data value. Throws a KeyError if an error occurs.
        """
        return getStatuses(data)

    @staticmethod
    def getDecodedStatus(data: Data, status_name: str) -> int:
        """
        Gets the specific decoded status of the data value. Throws a KeyError if an error occurs.
        """
        return getStatus(data, status_name)

    def addData(self, data: Data) -> None:
        """
        Adds a single data point to the model. Creates a new model if one
        for the given data ID doesn't exist.
        """
        self._createModelIfNone(data.id)
        self._datamap[data.id].addData(data.timestamp, data.value)
        self.layoutChanged.emit()

    def addDataList(self, data_list: List[Data]) -> None:
        """
        Adds a list of data to the model. Creates a new model if one for any of
        the given data IDs doesn't exist.
        """
        for data in data_list:
            self._createModelIfNone(data.id)
            self._datamap[data.id].addData(data.timestamp, data.value)
        self.layoutChanged.emit()

    def filter(self, ids: List[int], keep_ids: bool = True) -> None:
        """
        Filters the model using the given list of IDs.

        The keep_ids flag specifies whether the given IDs should be the ones
        that are kept or the ones that are removed from the model.
        TODO: Add support for filtering by timestamps
        """
        if keep_ids:
            def filter_func(id): return id not in ids
        else:
            def filter_func(id): return id in ids

        remove_ids = list(filter(filter_func, self._datamap.keys()))
        for id in remove_ids:
            self._datamap[id].deleteAllData()
            self._datamap.pop(id)
        self.layoutChanged.emit()

    def deleteData(self, id: int) -> None:
        """
        Removes all data from the model specified by the given ID.
        """
        if id in self._datamap:
            self._datamap[id].deleteAllData()
            self._datamap.pop(id)
            self.layoutChanged.emit()
        else:
            raise ValueError("Invalid data ID")

    def deleteAllData(self) -> None:
        """
        Removes all data from each of the data models in this manager.
        """
        for model in self._datamap.values():
            model.deleteAllData()
        self._datamap.clear()
        self.layoutChanged.emit()

    def getAvailableIds(self) -> List[int]:
        """
        Gets a list of data IDs present in this manager.
        """
        return list(self._datamap.keys())

    def isEmpty(self) -> bool:
        """
        Returns whether or not this manager is empty.
        """
        return len(self._datamap) == 0

    def getDataCount(self) -> int:
        """
        Gets the current number of data points.
        """
        count = 0
        for model in self._datamap.values():
            count += model.rowCount()
        return count

    def getErrorCount(self) -> int:
        """
        Gets the current number of data value errors.
        """
        count = 0
        for model in self._datamap.values():
            count += model.getErrorCount()
        return count

    def getDataModel(self, id: int) -> DataModel:
        """
        Gets the data model for the given ID.
        """
        try:
            return self._datamap[id]
        except KeyError:
            raise ValueError("Invalid data ID")

    def getCSVWorker(self, path: str) -> Worker:
        """
        Returns a worker to export this model's data to a CSV file.
        """
        return Worker(
            self.exportCSV,
            file_path=path,
            models=list(
                self._datamap.values()))

    @staticmethod
    def exportCSV(*args, **kwargs) -> None:
        """Exports the data in this model as a csv to the specified path.

        CAUTION
        -------
        This is a worker function meant to be called from a thread (see Worker).
        Is expecting the following external arguments:
            - kwargs["file_path"] : str
            - kwargs["models"] : List[DataModel]
        """
        try:
            path: str = kwargs["file_path"]
            models: List[DataModel] = kwargs["models"]
            message_signal: pyqtBoundSignal = kwargs["message"]
        except BaseException:
            raise RuntimeError(
                "Internal processing error - thread configuration invalid")

        header = ["time", "data_id", "description", "value", "units"]
        with open(path, "w", encoding="UTF8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(header)

            for model in models:
                id = model.getDataId()
                desc = model.getDataType()
                for data in model.getData():
                    str_time = data[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                    writer.writerow(
                        [str_time, id, desc, data[1], DATA_IDS[id]["units"]])
        message_signal.emit("Finished CSV export")
