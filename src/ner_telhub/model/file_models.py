import os
from typing import List, Tuple
from PyQt6.QtCore import QAbstractListModel, Qt, pyqtBoundSignal

from ner_telhub.model.data_models import DataModel
from ner_telhub.model.processing.decode_files import LogFormat, process_line
from ner_telhub.utils.threads import Worker


class FileModel(QAbstractListModel):
    """A model class to represent the log files in the system."""

    def __init__(self, *args, **kwargs):
        super(FileModel, self).__init__(*args, **kwargs)
        self.__filepaths = []
        self.file_format = LogFormat.TEXTUAL1 # Default format

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            filepath = self.__filepaths[index.row()]
            return filepath

    def rowCount(self, index):
        return len(self.__filepaths)

    def addFile(self, filepath: str):
        self.__filepaths.append(filepath)
        self.layoutChanged.emit()

    def deleteFile(self, index):
        del self.__filepaths[index.row()]
        self.layoutChanged.emit()

    def deleteAll(self):
        self.__filepaths.clear()
        self.layoutChanged.emit()

    def getFormat(self) -> LogFormat:
        return self.file_format

    def setFormat(self, format: LogFormat) -> None:
        self.file_format = format


    def getProcessWorker(self, model: DataModel) -> Worker:
        """Returns a worker to process this model's log file paths, storing results 
        in the given data model.
        """

        return Worker(self.processFileData, *self.__filepaths, format=self.file_format, data_model=model)


    @staticmethod
    def processFileData(*args, **kwargs) -> None:
        """Processes a file from inside a Worker thread."""

        try:
            filepaths = args
            format: LogFormat = kwargs["format"]
            model: DataModel = kwargs["data_model"]
            progress_signal: pyqtBoundSignal = kwargs["progress"]
            message_signal: pyqtBoundSignal = kwargs["message"]
        except:
            raise RuntimeError("Internal processing error - thread configuration invalid")

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
                        timestamp, id, length, data = process_line(line, format)
                        processed_data.extend(model.processData(id, timestamp, length, data))
                    except:
                        error_count += 1
                        message_signal.emit(f" Error processing line {file_line_count}")
                        if error_count >= max_error_count:
                            raise RuntimeError(f"Malformed file or wrong processing format.\nHit max error count ({max_error_count}).")
                    progress_pct = int(100 * lines_processed / estimated_line_count)
                    if progress_pct != current_progress_pct:
                        current_progress_pct = progress_pct
                        progress_signal.emit(progress_pct)
                message_signal.emit(f"Done with file {fp}")

        model.addDataList(processed_data)
        message_signal.emit(f"Total message count: {lines_processed}")


    @staticmethod
    def getLineCount(filepaths: List[str]) -> int:
        """Gets the total line count of all the files in the list.
        
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
        

            



