from tkinter import filedialog
from ner_telhub.model.file_models import FileModel
from ner_telhub.widgets.styled_widgets.styled_widgets import NERButton
from PyQt6.QtWidgets import (
      QWidget, QVBoxLayout, QLabel, QListView)
from PyQt6.QtCore import Qt

class FileView(QWidget):
    """View section with file information and control."""

    def __init__(self, parent: QWidget, file_model: FileModel):
        super(FileView, self).__init__(parent)

        self.file_model = file_model

        header = QLabel("Selected Files")
        header.setStyleSheet("font-size: 16px; font-weight: 400")
        header.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.view = QListView()
        self.view.setModel(self.file_model)

        self.add_button = NERButton("Add Files", NERButton.Styles.GREEN)
        self.add_button.setToolTip("Add files from the file system to process")
        self.remove_button = NERButton("Remove Files", NERButton.Styles.RED)
        self.remove_button.setToolTip("Remove file(s) from the text box")
        self.add_button.pressed.connect(self.add_files)
        self.remove_button.pressed.connect(self.remove_files)

        layout = QVBoxLayout()
        layout.addWidget(header)
        layout.addWidget(self.view)
        layout.addWidget(self.add_button)
        layout.addWidget(self.remove_button)

        self.setLayout(layout)

    def add_files(self):
        filepaths = filedialog().getOpenFileNames()[0]
        for fp in filepaths:
            self.file_model.addFile(fp)

    def remove_files(self):
        indexes = self.view.selectedIndexes()
        if indexes:
            index = indexes[0]
            self.file_model.deleteFile(index)
            self.view.clearSelection()
        else:
            self.file_model.deleteAll()
