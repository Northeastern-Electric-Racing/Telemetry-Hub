from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QMessageBox,
    QVBoxLayout, QLabel, QToolBar, 
    QSizePolicy, QLineEdit, QGridLayout,
    QDialogButtonBox, QDialog, QTableWidget,
    QTableWidgetItem, QProgressBar
)
from PyQt6.QtCore import QSize
from typing import List, Callable

from ner_telhub.model.data_models import DataModelManager
from ner_telhub.widgets.menu_widgets import DataIds
from ner_telhub.widgets.styled_widgets import NERButton
from ner_telhub.widgets.graphing_widgets import GraphDashboardWidget
from ner_telhub.utils.timestream import TimestreamQueryService, DATE_TIME_FORMAT


class TestIdDialog(QDialog):
    """
    Shows information on test ids available in the database.
    """

    def __init__(self, test_ids: List[str], parent: QWidget = None):
        super().__init__(parent)
        self.setWindowTitle("Test IDs")

        # Create table 
        table = QTableWidget(self)
        table.setRowCount(len(test_ids))
        table.setColumnCount(1)
        table.verticalHeader().hide()

        # Set table data
        for i in range(len(test_ids)):
            item = QTableWidgetItem(test_ids[i])  
            table.setItem(i, 0, item)
        table.setHorizontalHeaderLabels(["Test ID"])
        table.resizeRowsToContents()

        layout = QVBoxLayout()
        layout.addWidget(table)
        self.setLayout(layout)


class QueryDialog(QDialog):
    """
    Dialog window allowing the user to input arguments to query the database.
    """

    def __init__(self, 
                 parent: QWidget, 
                 model: DataModelManager, 
                 query_service: TimestreamQueryService,
                 result_callback: Callable):
        super(QueryDialog, self).__init__(parent)
        self.model = model
        self.query_service = query_service
        self.callback = result_callback
        self.setWindowTitle("Query Data")

        self.testid_input = QLineEdit()
        self.dataid_input = QLineEdit()
        self.mintime_input = QLineEdit()
        self.maxtime_input = QLineEdit()
        self.maxtime_input.setMinimumWidth(200)
        self.testid_button = NERButton("Show Options", NERButton.Styles.GRAY)
        self.dataid_button = NERButton("Show Options", NERButton.Styles.GRAY)
        self.mintime_button = NERButton("Get Session Start", NERButton.Styles.GRAY)
        self.maxtime_button = NERButton("Get Session End", NERButton.Styles.GRAY)
        self.testid_button.pressed.connect(self.findTestIds)
        self.dataid_button.pressed.connect(lambda : DataIds().exec())
        self.mintime_button.pressed.connect(self.findMinTime)
        self.maxtime_button.pressed.connect(self.findMaxTime)

        self.layout = QGridLayout()
        self.layout.addWidget(QLabel("Test Session ID: "), 0, 0)
        self.layout.addWidget(self.testid_input, 0, 1)
        self.layout.addWidget(self.testid_button, 0, 2)
        self.layout.addWidget(QLabel("Data ID: "), 1, 0)
        self.layout.addWidget(self.dataid_input, 1, 1)
        self.layout.addWidget(self.dataid_button, 1, 2)
        self.layout.addWidget(QLabel("Min Time: "), 2, 0)
        self.layout.addWidget(self.mintime_input, 2, 1)
        self.layout.addWidget(self.mintime_button, 2, 2)
        self.layout.addWidget(QLabel("Max Time: "), 3, 0)
        self.layout.addWidget(self.maxtime_input, 3, 1)
        self.layout.addWidget(self.maxtime_button, 3, 2)
        
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttonBox.accepted.connect(self.onAccept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def findTestIds(self):
        try:
            test_ids = self.query_service.getTestIds()
            TestIdDialog(test_ids).exec()
        except:
            QMessageBox.critical(self, "Error", "Could not get the available test IDs. Internal Error")

    def findMinTime(self):
        test_id = self.testid_input.text()
        if test_id == "":
            QMessageBox.critical(self, "Error", "You must include a test session ID to find the start time")
        else:
            try:
                start_time = self.query_service.getStartTimeForSession(test_id)
                self.mintime_input.setText(start_time.toString(DATE_TIME_FORMAT))
            except:
                QMessageBox.critical(self, "Error", "Could not get test session start time. Invalid ID")
    
    def findMaxTime(self):
        test_id = self.testid_input.text()
        if test_id == "":
            QMessageBox.critical(self, "Error", "You must include a test session ID to find the end time")
            return
        try:
            end_time = self.query_service.getEndTimeForSession(test_id)
            self.maxtime_input.setText(end_time.toString(DATE_TIME_FORMAT))
        except:
            QMessageBox.critical(self, "Error", "Could not get test session end time. Invalid ID")

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
        test_id = self.testid_input.text()
        data_id = self.dataid_input.text()
        min_time = self.mintime_input.text()
        max_time = self.maxtime_input.text()

        query_args = {}
        if test_id == "":
            raise RuntimeError("You must specify a test session ID")
        query_args["test_id"] = test_id
        
        if (min_time != "" and max_time == "") or (min_time == "" and max_time != ""):
            raise RuntimeError("Min/Max times must either both be specified or both be blank")
        elif min_time != "" and max_time != "":
            query_args["time_range"] = (min_time, max_time)
        
        if data_id != "":
            query_args["data_id"] = data_id

        return query_args


class QueryToolbar(QToolBar):
    def __init__(self, 
                 parent: QWidget, 
                 data_model: DataModelManager, 
                 query_service: TimestreamQueryService,
                 progress_bar: QProgressBar,
                 query_status_label: QLabel):
        super(QueryToolbar, self).__init__(parent)
        
        self.process_started = False
        self.worker = None
        self.data_model = data_model
        self.query_service = query_service
        self.data_model.layoutChanged.connect(self.modelUpdated)
        self.setStyleSheet("background-color: white; padding: 5%")

        self.progress_bar = progress_bar
        self.query_status_label = query_status_label

        # Left side of toolbar
        self.load_button = NERButton("Load Data", NERButton.Styles.BLUE)
        self.load_button.addStyle("margin-right: 5%")
        self.load_button.pressed.connect(self.loadData)
        self.addWidget(self.load_button)

        # Middle of toolbar using spacers
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.addWidget(spacer)
        
        # Right side of toolbar
        self.model_info = QLabel("0 data points")
        self.clear_button = NERButton("Clear Data", NERButton.Styles.RED)
        self.clear_button.addStyle("margin-right: 5%")
        self.clear_button.pressed.connect(lambda: self.data_model.deleteAllData())
        self.addWidget(self.model_info)    
        self.addWidget(self.clear_button)
    
    def modelUpdated(self):
        self.model_info.setText(f"{self.data_model.getDataCount()} data points")

    def loadData(self):
        """
        Gets called when either the user wants to start a query (in which the input dialog
        is opened), or when they want to stop the running query.
        """
        if self.process_started:
            try:
                if self.worker is not None:
                    self.worker.stop()
            except:
                pass
        if not self.data_model.isEmpty():
            button = QMessageBox.question(self, "Warning", "The application currently holds data. Further queries will " \
                "mix the data together. Clear the data if this is not desired. \nWould you like to continue?")
            if button == QMessageBox.StandardButton.No:
                return
        QueryDialog(self, self.data_model, self.query_service, self.startQuery).exec()
    
    def startQuery(self, **kwargs):
        """
        Starts the worker to load data into the model given the user specified arguments.
        """
        self.process_started = True
        self.load_button.setText("Stop Query")
        self.load_button.changeStyle(NERButton.Styles.RED)
        self.load_button.addStyle("margin-right: 5%")
        self.clear_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.query_status_label.setVisible(True)

        self.worker = self.query_service.getQueryWorker(self.data_model, **kwargs)
        self.worker.signals.finished.connect(self.stopQuery)
        self.worker.signals.error.connect(lambda error: QMessageBox.critical(self, "Query Error", error[1].__str__()))
        self.worker.signals.message.connect(lambda msg : self.query_status_label.setText(msg))
        self.worker.signals.progress.connect(lambda val: self.progress_bar.setValue(val))

        try:
            self.worker.start()
        except RuntimeError as e: 
            self.stopQuery()
            QMessageBox.critical(self, "Internal Error", str(e))

    def stopQuery(self):
        self.process_started = False
        self.worker = None
        self.load_button.setText("Load Data")
        self.load_button.changeStyle(NERButton.Styles.BLUE)
        self.load_button.addStyle("margin-right: 5%")
        self.clear_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
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
        self.setMinimumSize(QSize(800, 480))

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.label = QLabel()
        self.label.setVisible(False)

        # Layout config
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(QueryToolbar(self, self.data_model, self.query_service, self.progress_bar, self.label))
        self.main_layout.addWidget(self.progress_bar)
        self.main_layout.addWidget(self.label)
        self.main_layout.addWidget(GraphDashboardWidget(self, self.data_model, False))

        widget = QWidget(self)
        widget.setLayout(self.main_layout)
        self.setCentralWidget(widget)

        # Menu bar
        menu = self.menuBar()
        help_menu = menu.addMenu("Help")

        help_action_1 = help_menu.addAction("Data Info")
        help_action_1.triggered.connect(lambda : DataIds(self).show())

