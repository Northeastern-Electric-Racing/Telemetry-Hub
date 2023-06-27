from PyQt6.QtWidgets import (
      QDialog, QDialogButtonBox, QLabel, QLineEdit, QMessageBox, QVBoxLayout,
      QWidget
)
from ner_telhub.model.data_models import DataModelManager
from ner_telhub.utils.timestream import TimestreamIngestionService
from ner_telhub.widgets.styled_widgets.styled_widgets import NERLoadingSpinner

class DatabaseDialog(QDialog):
    """Dialog to export data to a the database."""

    def __init__(
            self,
            parent: QWidget,
            model: DataModelManager,
            spinner: NERLoadingSpinner):
        super().__init__(parent)

        self.setWindowTitle("Database Export")
        self.model = model
        self.spinner = spinner

        self.testid_input = QLineEdit()
        self.label = QLabel(
            """The test ID is a unique identifier that you can use to identify a testing session.
Make sure the test ID is a meaningful name so you can reload previous sessions by their ID.""")

        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel("Test ID:"))
        self.layout.addWidget(self.testid_input)
        self.layout.addWidget(self.label)

        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttonBox.accepted.connect(self.on_accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def on_accept(self):
        if self.model.getDataCount() == 0:
            QMessageBox.critical(
                self, "Error", "Cannot export data - data model is empty.")
            return

        testid = self.testid_input.text()
        if testid == "":
            QMessageBox.critical(self, "Error", "You must specify a test ID")
            return

        button = QMessageBox.question(
            self,
            "Warning",
            "You cannot undo this action, so please make sure you are authorized to complete it."
            "\nWould you like to continue?")
        if button == QMessageBox.StandardButton.No:
            return

        models = [self.model.getDataModel(id)
                  for id in self.model.getAvailableIds()]
        worker = TimestreamIngestionService.getIngestionWorker(models, testid)
        worker.signals.finished.connect(lambda: self.spinner.stopAnimation())
        worker.signals.error.connect(
            lambda error: QMessageBox.critical(
                self, "Export Error", error[1].__str__()))
        worker.signals.message.connect(
            lambda msg: QMessageBox.about(
                self, "Export Status", msg))
        try:
            worker.start()
            self.spinner.startAnimation()
        except RuntimeError as e:
            QMessageBox.critical(self, "Internal Error", str(e))
        self.accept()
