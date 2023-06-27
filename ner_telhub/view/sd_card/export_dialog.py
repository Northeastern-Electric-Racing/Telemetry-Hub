from PyQt6.QtWidgets import (
      QDialog, QWidget, QGridLayout, QLabel, QLineEdit, QDialogButtonBox,
      QMessageBox, QFileDialog
)
from ner_telhub.model.data_models import DataModelManager
from ner_telhub.widgets.styled_widgets.ner_button import NERButton
from ner_telhub.widgets.styled_widgets.ner_loading_spinner import NERLoadingSpinner

class ExportDialog(QDialog):
    """Dialog to export data to a CSV file."""

    def __init__(
            self,
            parent: QWidget,
            model: DataModelManager,
            spinner: NERLoadingSpinner):
        super().__init__(parent)

        self.setWindowTitle("Export CSV")
        self.model = model
        self.spinner = spinner

        self.filename_input = QLineEdit()
        self.directory_input = QLineEdit()
        self.directory_button = NERButton("...", NERButton.Styles.GRAY)
        self.directory_button.addStyle("font-size: 20px")
        self.directory_button.setMaximumSize(45, 25)
        self.directory_button.pressed.connect(self.choose_directory)
        self.directory_button.setToolTip("Choose from file system")

        self.layout = QGridLayout()
        self.layout.addWidget(QLabel("File name: "), 0, 0)
        self.layout.addWidget(self.filename_input, 0, 1)
        self.layout.addWidget(QLabel("Directory name: "), 1, 0)
        self.layout.addWidget(self.directory_input, 1, 1)
        self.layout.addWidget(self.directory_button, 1, 2)

        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttonBox.accepted.connect(self.on_accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def choose_directory(self):
        dir = QFileDialog().getExistingDirectory(self)
        self.directory_input.setText(dir)

    def on_accept(self):
        try:
            filename = self.create_extension(self.filename_input.text())
        except BaseException:
            QMessageBox.critical(
                self,
                "Invalid File Name",
                "File must be either a .csv or contain no extension.")
            return

        directory = self.directory_input.text()
        full_path = directory + "/" + filename

        worker = self.model.getCSVWorker(full_path)
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

    @staticmethod
    def create_extension(name: str):
        """Verifies the file name has a csv extension, or adds one if not."""
        components = name.split(".")
        if len(components) == 1:
            return name + ".csv"
        elif len(components) == 2 and components[1] == "csv":
            return name
        else:
            raise ValueError("Invalid file name format")
