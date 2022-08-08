from PyQt6.QtWidgets import (
    QMainWindow, QLabel, QHBoxLayout, 
    QVBoxLayout, QWidget, QFileDialog,
    QListView, QPushButton, QTextEdit,
    QGridLayout, QProgressBar, QDialog,
    QDialogButtonBox, QLineEdit
)
from PyQt6.QtCore import QSize, Qt

from model.file_models import FileModel
from model.data_models import DataModel


class FileSelection(QWidget):
    def __init__(self, file_model: FileModel, data_model: DataModel):
        super(FileSelection, self).__init__()

        self.file_model = file_model
        self.data_model = data_model


        header = QLabel("Selected Files")
        header.setStyleSheet("font-size: 18px; font-weight: 400")
        header.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.view = QListView()
        self.view.setModel(self.file_model)

        self.add_button = QPushButton("Add Files")
        self.remove_button = QPushButton("Remove Files")
        self.add_button.pressed.connect(self.add_files)
        self.remove_button.pressed.connect(self.remove_files)
        self.add_button.setStyleSheet("color: white; background-color: #07D807")
        self.remove_button.setStyleSheet("color: white; background-color: #FF5656")

        layout = QVBoxLayout()
        layout.addWidget(header)
        layout.addWidget(self.view)
        layout.addWidget(self.add_button)
        layout.addWidget(self.remove_button)

        self.setLayout(layout)

    
    def add_files(self):
        filepaths = QFileDialog().getOpenFileNames()[0]
        for fp in filepaths:
            self.file_model.addFile(fp)

    def remove_files(self):
        indexes = self.view.selectedIndexes()
        if indexes:
            index = indexes[0]
            self.file_model.deleteFile(index)
            self.view.clearSelection()
        


class ProcessingProgressBar(QWidget):
    def __init__(self):
        super(ProcessingProgressBar, self).__init__()

        label = QLabel("Status:")
        progress_bar = QProgressBar()
        progress_bar.setMinimum(0)
        progress_bar.setMaximum(0)

        layout = QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(progress_bar)
        self.setLayout(layout)



class ProcessView(QWidget):
    def __init__(self, file_model: FileModel, data_model: DataModel):
        super(ProcessView, self).__init__()

        self.process_started = False
        self.file_model = file_model
        self.data_model = data_model

        header = QLabel("Status Logs")
        header.setStyleSheet("font-size: 18px; font-weight: 400")
        header.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.view = QTextEdit()
        self.view.setReadOnly(True)

        self.start_button = QPushButton("Start")
        self.start_button.pressed.connect(self.process_logs)
        self.start_button.setStyleSheet("color: white; background-color: #07D807")

        self.progress_bar = ProcessingProgressBar()
        self.progress_bar.setVisible(False)

        layout = QVBoxLayout()
        layout.addWidget(header)
        layout.addWidget(self.view)
        layout.addWidget(self.start_button)
        layout.addWidget(self.progress_bar)
        self.setLayout(layout)

    def process_logs(self):
        self.process_started = not self.process_started
        if self.process_started:
            self.start_button.setText("Stop")
            self.start_button.setStyleSheet("color: white; background-color: #FF5656")
            self.progress_bar.setVisible(True)

            # TODO: Start a new thread to do the processing
            try:
                self.file_model.processData(self.data_model)
            except Exception as e: 
                print("Error running processing scripts")
                print(e)
        else:
            self.start_button.setText("Start")
            self.start_button.setStyleSheet("color: white; background-color: #07D807")
            self.progress_bar.setVisible(False)

            # TODO: End processing




class ExportDialog(QDialog):
    def __init__(self, data_model: DataModel):
        super().__init__()

        self.setWindowTitle("Export CSV")
        self.data_model = data_model

        self.filename_input = QLineEdit()
        self.directory_input = QLineEdit()
        self.directory_input.setReadOnly(True)
        self.directory_button = QPushButton("Choose Directory")
        self.directory_button.pressed.connect(self.choose_directory)
        self.reset_button = QPushButton("Reset Fields")
        self.reset_button.pressed.connect(self.reset_fields)

        self.layout = QGridLayout()
        self.layout.addWidget(QLabel("File name: "), 0, 0)
        self.layout.addWidget(self.filename_input, 0, 1)
        self.layout.addWidget(QLabel("Directory name: "), 1, 0)
        self.layout.addWidget(self.directory_input, 1, 1)
        self.layout.addWidget(self.directory_button, 2, 0)
        self.layout.addWidget(self.reset_button, 2, 1)
        
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttonBox.accepted.connect(self.on_accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def choose_directory(self):
        dir = QFileDialog().getExistingDirectory(self)
        self.directory_input.setText(dir)

    def reset_fields(self):
        self.filename_input.setText("")
        self.directory_input.setText("")
    
    def on_accept(self):
        filename = self.filename_input.text()
        directory = self.directory_input.text()
        full_path = directory + "/" + filename
        print(full_path)

        try:
            self.data_model.exportCSV(full_path)
            self.accept()
        except Exception as E:
            print("Error exporting CSV.")
            print(E.with_traceback)
            self.reject()




class OptionsMenu(QWidget):
    def __init__(self, data_model: DataModel):
        super(OptionsMenu, self).__init__()

        self.data_model = data_model

        header = QLabel("Options")
        header.setStyleSheet("font-size: 26px; font-weight: 600")
        header.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.csv_button = QPushButton("Generate CSV")
        self.graph_button = QPushButton("Graph Data")
        self.database_button = QPushButton("Database Export")
        self.csv_button.pressed.connect(self.generate_csv)
        self.graph_button.pressed.connect(self.graph_data)
        self.database_button.pressed.connect(self.database_export)

        menu_layout = QGridLayout()
        menu_layout.addWidget(self.csv_button, 0, 0)
        menu_layout.addWidget(self.graph_button, 0, 1)
        menu_layout.addWidget(self.database_button, 0, 2)

        layout = QVBoxLayout()
        layout.addWidget(header)
        layout.addLayout(menu_layout)
        self.setLayout(layout)
    
    def generate_csv(self):
        dlg = ExportDialog(self.data_model)
        dlg.exec()

    def graph_data(self):
        pass

    def database_export(self):
        pass






class SdCardWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Telemetry Hub")
        self.setMinimumSize(QSize(800, 480))

        file_model = FileModel()
        data_model = DataModel()

        hlayout = QHBoxLayout()
        hlayout.addWidget(FileSelection(file_model, data_model))
        hlayout.addWidget(ProcessView(file_model, data_model))

        vlayout = QVBoxLayout()
        vlayout.addLayout(hlayout)
        vlayout.addWidget(OptionsMenu(data_model))

        # Setup menu bar
        menu = self.menuBar()
        file_menu = menu.addMenu("File")
        help_menu = menu.addMenu("Edit")
        edit_menu = menu.addMenu("Help")

        widget = QWidget()
        widget.setLayout(vlayout)
        self.setCentralWidget(widget)


