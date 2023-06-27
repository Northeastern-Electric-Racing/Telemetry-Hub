from typing import Callable
from PyQt6.QtWidgets import (
      QDialog, QDialogButtonBox, QGridLayout, QLabel, QLineEdit, QWidget, QVBoxLayout, QMessageBox)
from ner_telhub.model.data_models import DataModelManager
from ner_telhub.utils.timestream import TimestreamQueryService
from ner_telhub.utils.timestream_constants import DATE_TIME_FORMAT
from ner_telhub.widgets.menu_widgets import DataIds
from ner_telhub.widgets.styled_widgets.styled_widgets import NERButton


class QueryDialog(QDialog):
    """
    Dialog window allowing the user to input arguments to query the database.
    """

    def __init__(self,
                 parent: QWidget,
                 model: DataModelManager,
                 query_service: TimestreamQueryService,
                 result_callback: Callable,
                 test_id: int):
        super(QueryDialog, self).__init__(parent)
        self.model = model
        self.query_service = query_service
        self.callback = result_callback
        self.test_id = test_id
        self.setWindowTitle("Query Data")

        self.mintime_input = QLineEdit()
        self.maxtime_input = QLineEdit()
        self.dataid_input = QLineEdit()
        self.dataid_input.setMinimumWidth(150)
        self.mintime_button = NERButton("Reset", NERButton.Styles.GRAY)
        self.mintime_button.setToolTip(
            "Reset to the overall session minimum time")
        self.maxtime_button = NERButton("Reset", NERButton.Styles.GRAY)
        self.maxtime_button.setToolTip(
            "Reset to the overall session maximum time")
        self.dataid_button = NERButton("Show Options", NERButton.Styles.GRAY)
        self.dataid_button.setToolTip("Show table of potential data IDs")
        self.dataid_button.pressed.connect(lambda: DataIds().exec())
        self.mintime_button.pressed.connect(self.findMinTime)
        self.maxtime_button.pressed.connect(self.findMaxTime)
        self.findMinTime()
        self.findMaxTime()

        self.data_count_label = QLabel("Query size - 0 data points")
        self.data_count_button = NERButton(
            "Calculate Size", NERButton.Styles.BLUE)
        self.data_count_button.pressed.connect(self.findDataCount)
        self.data_count_button.setToolTip(
            "Find data count for the above parameters")
        self.help_label = QLabel(
            "Note: It is recommended for your queries to be under 1 million data points to prevent \n"
            "long running operations. Calculate the potential size after specifying fields to verify this.")
        self.findDataCount()

        self.form_layout = QGridLayout()
        self.form_layout.addWidget(QLabel("Data ID (optional):"), 1, 0)
        self.form_layout.addWidget(self.dataid_input, 1, 1)
        self.form_layout.addWidget(self.dataid_button, 1, 2)
        self.form_layout.addWidget(QLabel("Min Time:"), 2, 0)
        self.form_layout.addWidget(self.mintime_input, 2, 1)
        self.form_layout.addWidget(self.mintime_button, 2, 2)
        self.form_layout.addWidget(QLabel("Max Time:"), 3, 0)
        self.form_layout.addWidget(self.maxtime_input, 3, 1)
        self.form_layout.addWidget(self.maxtime_button, 3, 2)

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.form_layout)
        self.main_layout.addWidget(self.data_count_label)
        self.main_layout.addWidget(self.data_count_button)
        self.main_layout.addWidget(self.help_label)

        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttonBox.accepted.connect(self.onAccept)
        self.buttonBox.rejected.connect(self.reject)

        self.main_layout.addWidget(self.buttonBox)
        self.setLayout(self.main_layout)

    def findMinTime(self):
        try:
            start_time = self.query_service.getStartTimeForSession(
                self.test_id)
            self.mintime_input.setText(start_time.toString(DATE_TIME_FORMAT))
        except Exception as e:
            raise RuntimeError(
                "Could not get test session start time: " + str(e))

    def findMaxTime(self):
        try:
            end_time = self.query_service.getEndTimeForSession(self.test_id)
            self.maxtime_input.setText(end_time.toString(DATE_TIME_FORMAT))
        except Exception as e:
            raise RuntimeError(
                "Could not get test session end time: " + str(e))

    def findDataCount(self):
        try:
            data_id = self.dataid_input.text()
            min_time = self.mintime_input.text()
            max_time = self.maxtime_input.text()
            if data_id != "":
                data_count = self.query_service.getDataCount(
                    self.test_id, data_id=data_id, time_range=(min_time, max_time))
            else:
                data_count = self.query_service.getDataCount(
                    self.test_id, time_range=(min_time, max_time))
            self.data_count_label.setText(
                f"Query size - {data_count} data points")
        except Exception as e:
            raise RuntimeError("Could not get the query data count: " + str(e))

    def onAccept(self):
        """
        Actions to perform when the window OK button is pressed.
        """
        try:
            worker_kwargs = self._getQueryArguments()
        except RuntimeError as e:
            QMessageBox.critical(self, "Error", e.args[0])
            return

        self.callback(**worker_kwargs)
        self.accept()

    def _getQueryArguments(self):
        """
        Get the args for the query, raising an error if invalid args have been given.
        Returns the args in a map to be passed into the query worker.
        """
        data_id = self.dataid_input.text()
        min_time = self.mintime_input.text()
        max_time = self.maxtime_input.text()

        query_args = {}
        query_args["test_id"] = self.test_id

        if (min_time != "" and max_time == "") or (
                min_time == "" and max_time != ""):
            raise RuntimeError(
                "Min/Max times must either both be specified or both be blank")
        elif min_time != "" and max_time != "":
            query_args["time_range"] = (min_time, max_time)

        if data_id != "":
            query_args["data_id"] = data_id

        return query_args
