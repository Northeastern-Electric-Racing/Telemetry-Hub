from typing import Dict
from PyQt6.QtWidgets import (
    QMainWindow, QLabel, QHBoxLayout, 
    QVBoxLayout, QWidget, QFileDialog,
    QListView, QTextEdit,
    QGridLayout, QProgressBar, QDialog,
    QDialogButtonBox, QLineEdit, QMessageBox,
    QCheckBox, QMenu, QToolBar
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QSize, Qt

from ner_telhub.model.file_models import FileModel
from ner_telhub.model.data_models import DataModelManager
from ner_processing.decode_files import LogFormat
from ner_telhub.widgets.menu_widgets import MessageIds, DataIds, NERButton
from ner_telhub.widgets.graphing_widgets import GraphDashboardWidget


class GraphDialog(QDialog):
    """Shows a dashboard for data in the system."""

    def __init__(self, parent: QWidget, model: DataModelManager):
        super().__init__(parent)
        self.setWindowTitle("Graph View")

        toolbar = QToolBar()
        toolbar.setStyleSheet("background-color: white; padding: 5%")
        self.screen_button = NERButton("Full Screen", "GRAY")
        self.screen_button.addStyle("margin-right: 5%")
        self.screen_button.pressed.connect(self.changeScreen)
        toolbar.addWidget(self.screen_button)

        layout = QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(GraphDashboardWidget(model))
        self.setLayout(layout)

    def changeScreen(self):
        if self.screen_button.text() == "Full Screen":
            self.showFullScreen()
            self.screen_button.setText("Minimize")
        else:
            self.showNormal()
            self.screen_button.setText("Full Screen")

    


class ExportDialog(QDialog):
    """Dialog to export data to a CSV file."""

    def __init__(self, parent: QWidget, model: DataModelManager):
        super().__init__(parent)

        self.setWindowTitle("Export CSV")
        self.model = model

        self.filename_input = QLineEdit()
        self.directory_input = QLineEdit()
        self.directory_button = NERButton("Choose Directory")
        self.directory_button.pressed.connect(self.choose_directory)

        self.layout = QGridLayout()
        self.layout.addWidget(QLabel("File name: "), 0, 0)
        self.layout.addWidget(self.filename_input, 0, 1)
        self.layout.addWidget(QLabel("Directory name: "), 1, 0)
        self.layout.addWidget(self.directory_input, 1, 1)
        self.layout.addWidget(self.directory_button, 2, 0)
        
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
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
        except:
            QMessageBox.critical(self, "Invalid File Name", "File must be either a .csv or contain no extension.")
            return

        directory = self.directory_input.text()
        full_path = directory + "/" + filename

        worker = self.model.getCSVWorker(full_path)
        worker.signals.error.connect(lambda error : QMessageBox.critical(self, "Export Error", error[1].__str__()))
        worker.signals.message.connect(lambda msg : QMessageBox.about(self, "Export Status", msg))
        try:
            worker.start()
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


class FileView(QWidget):
    """View section with file information and control."""

    def __init__(self, file_model: FileModel):
        super(FileView, self).__init__()

        self.file_model = file_model

        header = QLabel("Selected Files")
        header.setStyleSheet("font-size: 16px; font-weight: 400")
        header.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.view = QListView()
        self.view.setModel(self.file_model)

        self.add_button = NERButton("Add Files", "GREEN")
        self.remove_button = NERButton("Remove Files", "RED")
        self.add_button.pressed.connect(self.add_files)
        self.remove_button.pressed.connect(self.remove_files)

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
        else:
            self.file_model.deleteAll()
        


class ProcessView(QWidget):
    """View section with processing information an control."""

    def __init__(self, file_model: FileModel, data_model: DataModelManager):
        super(ProcessView, self).__init__()

        self.process_started = False
        self.worker = None
        self.file_model = file_model
        self.data_model = data_model

        header = QLabel("Processing Information")
        header.setStyleSheet("font-size: 16px; font-weight: 400")
        header.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.view = QTextEdit()
        self.view.setReadOnly(True)
        self.view_text = ""

        self.start_button = NERButton("Start", "GREEN")
        self.start_button.pressed.connect(self.start_process)

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
        if self.can_start():
            self.data_model.deleteAllData()
            self.process_started = True
            self.start_button.setText("Stop")
            self.start_button.changeColor("RED")
            self.progress_bar.setVisible(True)
            self.clear_view()

            self.worker = self.file_model.getProcessWorker(self.data_model)
            self.worker.signals.finished.connect(self.stop_process)
            self.worker.signals.error.connect(lambda error: QMessageBox.critical(self, "Processing Error", error[1].__str__()))
            self.worker.signals.message.connect(self.update_view)
            self.worker.signals.progress.connect(lambda val: self.progress_bar.setValue(val))
            try:
                self.worker.start()
            except RuntimeError as e: 
                self.stop_process()
                QMessageBox.critical(self, "Internal Error", str(e))
        else:
            try:
                if self.worker is not None:
                    self.worker.stop()
                self.worker = None
            except:
                pass
    
    def stop_process(self):
        self.process_started = False
        self.worker = None
        self.start_button.setText("Start")
        self.start_button.changeColor("GREEN")
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)

    def can_start(self) -> bool:
        if self.process_started:
            return False
        elif not self.data_model.isEmpty():
            button = QMessageBox.question(self, "Warning", "Current model data will be lost. \n" \
                "Would you like to continue?")
            return button == QMessageBox.StandardButton.Yes
        else:
            return True

    def update_view(self, message: str):
        self.view_text += message
        self.view_text += "\n"
        self.view.setText(self.view_text)

    def clear_view(self):
        self.view_text = ""
        self.view.setText("")




class OptionsView(QWidget):
    """Menu for actions on the data processed from the SD log files."""

    def __init__(self, data_model: DataModelManager):
        super(OptionsView, self).__init__()

        self.data_model = data_model
        self.data_model.layoutChanged.connect(self.modelUpdated)

        header = QLabel("Data Options")
        header.setStyleSheet("font-size: 24px; font-weight: 600")
        header.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

        # Setup layouts
        layout1: QVBoxLayout = self.generateLayout("Current Data")
        layout2: QVBoxLayout = self.generateLayout("Filters")
        layout3: QVBoxLayout = self.generateLayout("Export")

        # Populate layout 1
        self.model_info = QLabel("0 data points")
        self.clear_button = NERButton("Clear", "RED")
        self.clear_button.pressed.connect(self.clearModel)
        layout1.addWidget(self.model_info)
        layout1.addWidget(self.clear_button)

        # Populate layout 2
        self.id_input = QLineEdit()
        self.filter_method = QCheckBox()
        self.is_method_keep = True
        self.filter_method.setChecked(self.is_method_keep)
        self.setFilterMethod(self.is_method_keep)
        self.filter_method.stateChanged.connect(self.setFilterMethod)
        filter_layout = QGridLayout()
        filter_layout.addWidget(QLabel("IDs:"), 0, 0)
        filter_layout.addWidget(self.id_input, 0, 1)
        filter_layout.addWidget(QLabel("Filter Method:"), 1, 0)
        filter_layout.addWidget(self.filter_method, 1, 1)
        self.filter_button = NERButton("Filter", "BLUE")
        self.filter_button.pressed.connect(self.applyFilters)
        layout2.addLayout(filter_layout)
        layout2.addWidget(self.filter_button)

        # Populate layout 3
        self.graph_button = NERButton("Graph", "BLUE")
        self.graph_button.pressed.connect(lambda: GraphDialog(self, self.data_model).exec())
        self.csv_button = NERButton("CSV", "BLUE")
        self.csv_button.pressed.connect(lambda: ExportDialog(self, self.data_model).exec())
        self.database_button = NERButton("Database")
        self.database_button.pressed.connect(self.databaseExport)
        self.database_button.setDisabled(True)
        layout3.addWidget(self.graph_button)
        layout3.addWidget(self.csv_button)
        layout3.addWidget(self.database_button)

        # Populate main layout
        sub_layout = QHBoxLayout()
        sub_layout.addStretch()
        sub_layout.addLayout(layout1)
        sub_layout.addStretch()
        sub_layout.addLayout(layout2)
        sub_layout.addStretch()
        sub_layout.addLayout(layout3)
        sub_layout.addStretch()
        main_layout = QVBoxLayout()
        main_layout.addWidget(header)
        main_layout.addLayout(sub_layout)
        self.setLayout(main_layout)

    def modelUpdated(self):
        self.model_info.setText(f"{self.data_model.getDataCount()} data points")

    def generateLayout(self, label: str):
        layout = QVBoxLayout()
        layout_label = QLabel(label)
        layout_label.setStyleSheet("font-size: 16px; font-weight: 400")
        layout_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        layout.addWidget(layout_label)
        return layout

    def clearModel(self):
        self.data_model.deleteAllData()
        self.modelUpdated()

    def setFilterMethod(self, checked):
        self.is_method_keep = checked
        if self.is_method_keep:
            self.filter_method.setText("(keep ids)")
        else: 
            self.filter_method.setText("(remove ids)")

    def applyFilters(self):
        try:
            filter_list = [int(id) for id in self.id_input.text().split(" ")]
        except:
            QMessageBox.critical(self, "ID Format Error", "Expecting a list of IDs seperated by spaces.")
            return 

        self.data_model.filter(filter_list, self.is_method_keep)

    def databaseExport(self):
        pass



class FormatGroup(QWidget):
    """Defines format selection menu inputs for a file model."""

    def __init__(self, file_model: FileModel):
        super().__init__()

        self.file_model = file_model
        self.options: Dict[int, QAction] = {}
        self.enabled_id = self.file_model.getFormat().value

        for format in LogFormat:
            act = QAction(format.name)
            act.setCheckable(True)
            act.triggered.connect(lambda state, id=format.value : self.clicked(state, id))
            self.options[format.value] = act

        self.options.get(self.enabled_id).setChecked(True)

    def clicked(self, state: bool, id: int):
        if state == False:
            self.options.get(id).setChecked(True)
            pass
        else:
            self.options.get(self.enabled_id).setChecked(False)
            self.enabled_id = id
            self.file_model.setFormat(LogFormat(id))

    def addToMenu(self, menu: QMenu) -> None:
        for id in self.options:
            menu.addAction(self.options[id])



class SdCardWindow(QMainWindow):
    """Main window in for the SD Card connection."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Telemetry Hub")
        self.setMinimumSize(QSize(800, 480))

        file_model = FileModel()
        data_model = DataModelManager()

        # Setup menu bar
        menu = self.menuBar()
        file_menu = menu.addMenu("File")
        edit_menu = menu.addMenu("Edit")
        help_menu = menu.addMenu("Help")

        edit_action_export = edit_menu.addAction("Export")
        edit_action_reset = edit_menu.addAction("Reset")
        format_menu = edit_menu.addMenu("Format")
        formats = FormatGroup(file_model)
        formats.addToMenu(format_menu)
        
        help_action_1 = help_menu.addAction("Message Info")
        help_action_2 = help_menu.addAction("Data Info")
        help_action_1.triggered.connect(lambda : MessageIds(self).show())
        help_action_2.triggered.connect(lambda : DataIds(self).show())

        # Setup window
        hlayout = QHBoxLayout()
        hlayout.addWidget(FileView(file_model))
        hlayout.addWidget(ProcessView(file_model, data_model))

        vlayout = QVBoxLayout()
        vlayout.addLayout(hlayout)
        vlayout.addWidget(OptionsView(data_model))

        widget = QWidget()
        widget.setLayout(vlayout)
        self.setCentralWidget(widget)






