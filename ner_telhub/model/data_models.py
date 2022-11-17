import csv
import numpy as np
import sys
from typing import List, Any, Tuple

from PyQt6.QtCore import (
    QAbstractTableModel, Qt, 
    QReadWriteLock, QModelIndex,
    QReadLocker, QWriteLocker,
    pyqtBoundSignal, pyqtSignal,
    QObject, QDateTime
)

from ner_processing.master_mapping import DATA_IDS
from ner_processing.data import Data
from ner_telhub.utils.threads import Worker


class DataModel(QAbstractTableModel):
    """
    Represents a model for values of a single data type.
    """

    def __init__(self, parent: QObject, id: int) -> None:
        """
        Initializes the data list and mutex for thread access control.
        """
        super(DataModel, self).__init__(parent)
        if DATA_IDS.keys().__contains__(id):
            self._id = id
        else:
            raise ValueError("Invalid data id.")

        self._data: List[Tuple[QDateTime, Any]] = []
        self._lock = QReadWriteLock()
        self.min_value = sys.maxsize
        self.max_value = -sys.maxsize

    def data(self, index: QModelIndex, role: int) -> Any:
        """
        Gets the data at the specified index in the specified form.
        """
        QReadLocker(self._lock)
        if role == Qt.ItemDataRole.DisplayRole:
            value = self._data[index.row()][index.column()]
            if isinstance(value, QDateTime):
                return value.toMSecsSinceEpoch()
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
        return DATA_IDS[self._id]

    def getData(self) -> List[Tuple[QDateTime, Any]]:
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
        return np.array(self._data, Tuple[QDateTime, Any])

    def getMinTime(self) -> QDateTime:
        """
        Gets the time of the first data element (which is the min time for valid data sets).
        """
        QReadLocker(self._lock)
        try:
            return self._data[0][0]
        except IndexError:
            return QDateTime.fromMSecsSinceEpoch(9999999999999) # Give big min time when no data

    def getMaxTime(self) -> QDateTime:
        """
        Gets the time of the last data element (which is the max time for valid data sets).
        """
        QReadLocker(self._lock)
        try:
            return self._data[len(self._data) - 1][0]
        except IndexError:
            return QDateTime.fromMSecsSinceEpoch(0) # Give small max time when no data

    def getMinValue(self) -> QDateTime:
        """
        Gets the minimum value of the data in the model.
        """
        return self.min_value

    def getMaxValue(self) -> QDateTime:
        """
        Gets the maximum value of the data in the model.
        """
        return self.max_value

    def addData(self, timestamp: QDateTime, value: Any) -> None:
        """
        Adds the given piece of data to the model.
        
        Slow operation due to the locking of the mutex for a single data point. 
        For adding multiple elements at the same time, see addDataList().
        """
        QWriteLocker(self._lock)
        # TODO: Add filtering like the lines below here 
        # if self._id == 45 and abs(value) > 2000:
        #     print(value)
        #     return
        
        self._data.append((timestamp, value))
        if type(value) == int or type(value) == float:
            if value < self.min_value:
                self.min_value = value
            if value > self.max_value:
                self.max_value = value
        self.layoutChanged.emit()

    def deleteAllData(self) -> None:
        """
        Deletes all data from the model.
        """
        QWriteLocker(self._lock)
        self._data.clear()
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
        try:
            self._datamap[id]
        except KeyError:
            self._datamap[id] = DataModel(self, id)

    @staticmethod
    def getDataType(id: int) -> str:
        """
        Gets the type of data of the given ID.
        """
        try:
            return DATA_IDS[id]
        except KeyError:
            raise ValueError("Invalid data ID")

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
            filter_func = lambda id : id not in ids
        else: 
            filter_func = lambda id : id in ids

        remove_ids = list(filter(filter_func, self._datamap.keys()))
        for id in remove_ids:
            self._datamap[id].deleteAllData()
            self._datamap.pop(id)
        self.layoutChanged.emit()

    def deleteData(self, id: int) -> None:
        """
        Removes all data from the model specified by the given ID.
        """
        try:
            self._datamap[id].deleteAllData()
            self._datamap.pop(id)
        except KeyError:
            raise ValueError("Invalid data ID")
        self.layoutChanged.emit()

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
        return Worker(self.exportCSV, file_path=path, models=list(self._datamap.values()))

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
            progress_signal: pyqtBoundSignal = kwargs["progress"]
            message_signal: pyqtBoundSignal = kwargs["message"]
        except:
            raise RuntimeError("Internal processing error - thread configuration invalid")

        header = ["time", "data_id", "description", "value"]
        with open(path, "w", encoding="UTF8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(header)

            for model in models:
                id = model.getDataId()
                desc = model.getDataType()
                for data in model.getData():
                    str_time = data[0].toString("yyyy-MM-ddTHH:mm:ss.zzzZ")
                    writer.writerow([str_time, id, desc, data[1]])
        message_signal.emit(f"Finished CSV export")


