import os
from typing import List
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import (
    QAbstractListModel, Qt,
    pyqtBoundSignal, QModelIndex,
)
from ner_processing.decode_files import LogFormat, processLine
from ner_processing.message import Message
from ner_telhub.model.data_models import DataModelManager
from ner_telhub.utils.threads import Worker


class FileModel(QAbstractListModel):
    """
    A model class to represent the log files in the system.
    """

    def __init__(self, parent: QWidget, format=LogFormat.TEXTUAL1) -> None:
        """
        Initializes the model with a certain format.
        """
        super(FileModel, self).__init__(parent)
        self._filepaths = []
        self.file_format = format

    def data(self, index: QModelIndex, role: int) -> str:
        """
        Gets the data at the specified index in the specified form.
        """
        if role == Qt.ItemDataRole.DisplayRole:
            filepath = self._filepaths[index.row()]
            return filepath

    def rowCount(self, index=None) -> int:
        """
        Gets the number of elements in the model.
        """
        return len(self._filepaths)

    def addFile(self, filepath: str) -> None:
        """
        Adds a filepath to the model.
        """
        self._filepaths.append(filepath)
        self.layoutChanged.emit()

    def deleteFile(self, index: QModelIndex) -> None:
        """
        Removes the filepath at the specified index.
        """
        self._filepaths.pop(index.row())
        self.layoutChanged.emit()

    def deleteAll(self) -> None:
        """
        Removes all files in the model.
        """
        self._filepaths.clear()
        self.layoutChanged.emit()

    def getFormat(self) -> LogFormat:
        """
        Gets the format of the model.
        """
        return self.file_format

    def setFormat(self, format: LogFormat) -> None:
        """
        Sets the format of the model.
        """
        self.file_format = format

    def getProcessWorker(self, manager: DataModelManager) -> Worker:
        """
        Returns a worker to process this file model's log file paths, storing results
        in the given data model.
        """
        return Worker(
            self._processFileData,
            *self._filepaths,
            format=self.file_format,
            manager=manager)

    @staticmethod
    def _processFileData(*args, **kwargs) -> None:
        """
        Processes a file from inside a Worker thread.

        CAUTION
        -------
        This is a worker function meant to be called from a thread (see Worker).
        Is expecting the following external arguments:
            - kwargs["format"] : LogFormat
            - kwargs["manager"] : DataModelManager
        """
        try:
            filepaths = args
            format: LogFormat = kwargs["format"]
            manager: DataModelManager = kwargs["manager"]
            progress_signal: pyqtBoundSignal = kwargs["progress"]
            message_signal: pyqtBoundSignal = kwargs["message"]
        except BaseException:
            raise RuntimeError(
                "Internal processing error - thread configuration invalid")

        # Create tracking variables for counts/errors
        estimated_line_count = FileModel.getLineCount(filepaths)
        max_error_count = 500
        error_count = 0
        lines_processed = 0
        current_progress_pct = 0
        processed_data = []

        for fp in filepaths:
            with open(fp) as file:
                message_signal.emit(f"Processing file {fp}")
                file_line_count = 0
                for line in file:
                    file_line_count += 1
                    lines_processed += 1
                    try:
                        message: Message = processLine(line, format)
                        processed_data.extend(message.decode())
                    except BaseException:
                        error_count += 1
                        message_signal.emit(
                            f" Error processing line {file_line_count}")
                        if error_count >= max_error_count:
                            raise RuntimeError(
                                f"Malformed file or wrong processing format.\nHit max error count ({max_error_count}).")
                    progress_pct = int(
                        100 * lines_processed / estimated_line_count)
                    if progress_pct != current_progress_pct:
                        current_progress_pct = progress_pct
                        progress_signal.emit(progress_pct)
                message_signal.emit(f"Done with file {fp}")

        manager.addDataList(processed_data)
        message_signal.emit(f"Total message count: {lines_processed}")

    @staticmethod
    def getLineCount(filepaths: List[str]) -> int:
        """
        Gets the total line count of all the files in the list.

        There is no native way to get line counts of files without looping, so
        this function gets the total size and estimates the line count based
        on a subset of N lines.
        """
        if len(filepaths) == 0:
            return 0

        N = 20
        tested_lines = 0
        tested_size = 0
        total_size = sum(os.path.getsize(fp) for fp in filepaths)

        for fp in filepaths:
            with open(fp) as file:
                for line in file:
                    tested_lines += 1
                    tested_size += len(line)
                    if tested_lines >= N:
                        return int(total_size / (tested_size / tested_lines))
        return int(total_size / (tested_size / tested_lines))
