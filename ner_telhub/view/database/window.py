from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QMessageBox,
    QVBoxLayout, QLabel, QProgressBar,
    QDialogButtonBox, QDialog, QComboBox,
    QLineEdit, QGridLayout
)
from PyQt6.QtCore import QSize
from typing import Callable

from ner_telhub import colors
from ner_telhub.model.data_models import DataModelManager
from ner_telhub.widgets.menu_widgets import DataIds
from ner_telhub.widgets.styled_widgets import NERButton, NERToolbar
from ner_telhub.widgets.graphing_widgets import GraphDashboardWidget
from ner_telhub.utils.timestream import TimestreamQueryService, DATE_TIME_FORMAT


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


class QueryToolbar(NERToolbar):
    def __init__(self,
                 parent: QWidget,
                 data_model: DataModelManager,
                 query_service: TimestreamQueryService,
                 progress_bar: QProgressBar,
                 query_status_label: QLabel):
        super(QueryToolbar, self).__init__(parent)

        self.data_model = data_model
        self.query_service = query_service
        self.data_model.layoutChanged.connect(self.modelUpdated)
        self.setStyleSheet(
            "QToolBar { background-color: " +
            colors.SECONDARY_BACKGROUND +
            "; padding: 5%; border: none}")

        self.progress_bar = progress_bar
        self.query_status_label = query_status_label

        # Left side of toolbar
        self.testid_entry = QComboBox()
        test_ids = self.findTestIds()
        self.testid_entry.addItems(test_ids)
        self.testid_entry.setMinimumWidth(150)
        self.load_button = NERButton("Load Data", NERButton.Styles.GREEN)
        self.load_button.addStyle("margin-left: 5%; margin-right: 5%")
        self.load_button.pressed.connect(self.loadData)
        self.load_button.setToolTip(
            "Open a window to specify load parameters for given test ID")
        self.addLeft(QLabel("Test Session ID:"))
        self.addLeft(self.testid_entry)
        self.addLeft(self.load_button)

        # Right side of toolbar
        self.model_info = QLabel("0 data points")
        self.clear_button = NERButton("Clear Data", NERButton.Styles.RED)
        self.clear_button.addStyle("margin-right: 5%")
        self.clear_button.pressed.connect(
            lambda: self.data_model.deleteAllData())
        self.clear_button.setToolTip("Clear all loaded data")
        self.addRight(self.model_info)
        self.addRight(self.clear_button)

    def modelUpdated(self):
        self.model_info.setText(
            f"{self.data_model.getDataCount()} data points")

    def findTestIds(self):
        try:
            return self.query_service.getTestIds()
        except BaseException:
            QMessageBox.critical(
                self, "Error", "Could not get the available test IDs. Internal Error")
            return []

    def loadData(self):
        """
        Gets called when either the user wants to start a query.
        """
        if not self.data_model.isEmpty():
            button = QMessageBox.question(
                self, "Warning", "The application currently holds data. Further queries will "
                "mix the data together. Clear the data if this is not desired. \nWould you like to continue?")
            if button == QMessageBox.StandardButton.No:
                return
        try:
            test_id = self.testid_entry.currentText()
        except BaseException:
            QMessageBox.critical(
                self, "Error", "No Test ID specified, could not load data")
            return
        try:
            QueryDialog(
                self,
                self.data_model,
                self.query_service,
                self.startQuery,
                test_id).exec()
        except BaseException:
            QMessageBox.critical(
                self,
                "Error",
                "Could not connect to database to load data. Check credentials")

    def startQuery(self, **kwargs):
        """
        Starts the worker to load data into the model given the user specified arguments.
        """
        self.load_button.setEnabled(False)
        self.clear_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.query_status_label.setVisible(True)

        worker = self.query_service.getQueryWorker(self.data_model, **kwargs)
        worker.signals.finished.connect(self.stopQuery)
        worker.signals.error.connect(
            lambda error: QMessageBox.critical(
                self, "Query Error", error[1].__str__()))
        worker.signals.message.connect(
            lambda msg: self.query_status_label.setText(msg))
        worker.signals.progress.connect(
            lambda val: self.progress_bar.setValue(val))

        try:
            worker.start()
        except RuntimeError as e:
            self.stopQuery()
            QMessageBox.critical(self, "Internal Error", str(e))

    def stopQuery(self):
        self.load_button.setEnabled(True)
        self.clear_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.query_status_label.setVisible(False)
        self.progress_bar.setValue(0)
        self.query_status_label.setText("")


class DatabaseWindow(QMainWindow):
    """
    Main database window for querying/showing historical data.
    """

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.data_model = DataModelManager(self)
        self.query_service = TimestreamQueryService()

        # Window config
        self.setWindowTitle("Telemetry Hub")
        self.setMinimumSize(QSize(960, 720))

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.label = QLabel()
        self.label.setVisible(False)

        # Layout config
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(
            QueryToolbar(
                self,
                self.data_model,
                self.query_service,
                self.progress_bar,
                self.label))
        self.main_layout.addWidget(self.progress_bar)
        self.main_layout.addWidget(self.label)
        self.main_layout.addWidget(
            GraphDashboardWidget(
                self, self.data_model, False))

        widget = QWidget(self)
        widget.setLayout(self.main_layout)
        self.setCentralWidget(widget)

        # Menu bar
        menu = self.menuBar()
        help_menu = menu.addMenu("Help")

        help_action_1 = help_menu.addAction("Data Info")
        help_action_1.triggered.connect(lambda: DataIds(self).show())
