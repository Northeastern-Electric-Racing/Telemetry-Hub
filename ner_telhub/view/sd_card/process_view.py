from PyQt6.QtWidgets import (
      QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QTextEdit,
      QMessageBox)
from ner_telhub.model.data_models import DataModelManager

from ner_telhub.model.file_models import FileModel
from ner_telhub.widgets.styled_widgets.styled_widgets import NERButton
from PyQt6.QtCore import Qt

class ProcessView(QWidget):
    """View section with processing information an control."""

    def __init__(
            self,
            parent: QWidget,
            file_model: FileModel,
            data_model: DataModelManager):
        super(ProcessView, self).__init__(parent)

        self.file_model = file_model
        self.data_model = data_model

        header = QLabel("Processing Information")
        header.setStyleSheet("font-size: 16px; font-weight: 400")
        header.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.view = QTextEdit()
        self.view.setReadOnly(True)
        self.view_text = ""

        self.start_button = NERButton("Start", NERButton.Styles.GREEN)
        self.start_button.pressed.connect(self.start_process)
        self.start_button.setToolTip(
            "Start/stop processing the specified log files")

        # Setup Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)

        layout = QVBoxLayout()
        layout.addWidget(header)
        layout.addWidget(self.view)
        layout.addWidget(self.start_button)
        layout.addWidget(self.progress_bar)
        self.setLayout(layout)

    def start_process(self):
        if not self.data_model.isEmpty():
            button = QMessageBox.question(
                self, "Warning", "Current model data will be lost. \n"
                "Would you like to continue?")
            if button == QMessageBox.StandardButton.No:
                return

        self.data_model.deleteAllData()
        self.start_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.clear_view()

        worker = self.file_model.getProcessWorker(self.data_model)
        worker.signals.finished.connect(self.stop_process)
        worker.signals.error.connect(
            lambda error: QMessageBox.critical(
                self, "Processing Error", error[1].__str__()))
        worker.signals.message.connect(self.update_view)
        worker.signals.progress.connect(
            lambda val: self.progress_bar.setValue(val))

        try:
            worker.start()
        except RuntimeError as e:
            self.stop_process()
            QMessageBox.critical(self, "Internal Error", str(e))

    def stop_process(self):
        self.start_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)

    def update_view(self, message: str):
        self.view_text += message
        self.view_text += "\n"
        self.view.setText(self.view_text)

    def clear_view(self):
        self.view_text = ""
        self.view.setText("")
