from ner_telhub import colors
from ner_telhub.model.data_models import DataModelManager
from ner_telhub.utils.timestream import TimestreamQueryService
from ner_telhub.view.database.query_dialog import QueryDialog
from PyQt6.QtWidgets import (
      QWidget, QProgressBar, QLabel, QComboBox, QMessageBox)

from ner_telhub.widgets.styled_widgets.ner_button import NERButton
from ner_telhub.widgets.styled_widgets.ner_toolbar import NERToolbar

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
