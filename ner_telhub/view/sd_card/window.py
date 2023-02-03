from typing import Dict
from PyQt6.QtWidgets import (
    QMainWindow, QLabel, QHBoxLayout, 
    QVBoxLayout, QWidget, QFileDialog,
    QListView, QTextEdit,
    QGridLayout, QProgressBar, QDialog,
    QDialogButtonBox, QLineEdit, QMessageBox,
    QCheckBox, QMenu
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QSize, Qt

from ner_telhub.model.file_models import FileModel
from ner_telhub.model.data_models import DataModelManager
from ner_processing.decode_files import LogFormat
from ner_telhub.widgets.menu_widgets import MessageIds, DataIds
from ner_telhub.widgets.graphing_widgets import GraphDashboardWidget
from ner_telhub.widgets.styled_widgets import NERButton, NERToolbar
from ner_telhub.utils.timestream import TimestreamIngestionService


class GraphDialog(QDialog):
    """Shows a dashboard for data in the system."""

    def __init__(self, parent: QWidget, model: DataModelManager):
        super().__init__(parent)
        self.setWindowTitle("Graph View")

        toolbar = NERToolbar()
        toolbar.setStyleSheet("background-color: white; padding: 5%")
        self.screen_button = NERButton("Full Screen", NERButton.Styles.GRAY)
        self.screen_button.pressed.connect(self.changeScreen)
        toolbar.addLeft(self.screen_button)

        layout = QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(GraphDashboardWidget(parent, model, False))
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
        self.directory_button = NERButton("...")
        self.directory_button.addStyle("font-size: 20px")
        self.directory_button.setMaximumSize(45, 25)
        self.directory_button.pressed.connect(self.choose_directory)

        self.layout = QGridLayout()
        self.layout.addWidget(QLabel("File name: "), 0, 0)
        self.layout.addWidget(self.filename_input, 0, 1)
        self.layout.addWidget(QLabel("Directory name: "), 1, 0)
        self.layout.addWidget(self.directory_input, 1, 1)
        self.layout.addWidget(self.directory_button, 1, 2)
        
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


class DatabaseDialog(QDialog):
    """Dialog to export data to a the database."""

    def __init__(self, parent: QWidget, model: DataModelManager):
        super().__init__(parent)

        self.setWindowTitle("Database Export")
        self.model = model

        self.testid_input = QLineEdit();
        self.label = QLabel("""The test ID is a unique identifier that you can use to identify a testing session.
Make sure the test ID is a meaningful name so you can reload previous sessions by their ID.""")

        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel("Test ID:"))
        self.layout.addWidget(self.testid_input)
        self.layout.addWidget(self.label)
        
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttonBox.accepted.connect(self.on_accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def on_accept(self):
        if self.model.getDataCount() == 0:
            QMessageBox.critical(self, "Error", "Cannot export data - data model is empty.")
            return 

        testid = self.testid_input.text()
        if testid == "":
            QMessageBox.critical(self, "Error", "You must specify a test ID")
            return 

        models = [self.model.getDataModel(id) for id in self.model.getAvailableIds()]
        worker = TimestreamIngestionService.getIngestionWorker(models, testid)
        worker.signals.error.connect(lambda error : QMessageBox.critical(self, "Export Error", error[1].__str__()))
        worker.signals.message.connect(lambda msg : QMessageBox.about(self, "Export Status", msg))
        try:
            worker.start()
        except RuntimeError as e: 
            QMessageBox.critical(self, "Internal Error", str(e))
        self.accept()


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
        self.remove_button = NERButton("Remove Files", NERButton.Styles.RED)
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

    def __init__(self, parent: QWidget, file_model: FileModel, data_model: DataModelManager):
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
            button = QMessageBox.question(self, "Warning", "Current model data will be lost. \n" \
                "Would you like to continue?")
            if button == QMessageBox.StandardButton.No:
                return

        self.data_model.deleteAllData()
        self.start_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.clear_view()

        worker = self.file_model.getProcessWorker(self.data_model)
        worker.signals.finished.connect(self.stop_process)
        worker.signals.error.connect(lambda error: QMessageBox.critical(self, "Processing Error", error[1].__str__()))
        worker.signals.message.connect(self.update_view)
        worker.signals.progress.connect(lambda val: self.progress_bar.setValue(val))

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



class OptionsView(QWidget):
    """Menu for actions on the data processed from the SD log files."""

    def __init__(self, parent: QWidget, data_model: DataModelManager):
        super(OptionsView, self).__init__(parent)

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
        self.clear_button = NERButton("Clear", NERButton.Styles.RED)
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
        self.filter_button = NERButton("Filter", NERButton.Styles.BLUE)
        self.filter_button.pressed.connect(self.applyFilters)
        layout2.addLayout(filter_layout)
        layout2.addWidget(self.filter_button)

        # Populate layout 3
        self.graph_button = NERButton("Graph", NERButton.Styles.BLUE)
        self.graph_button.pressed.connect(lambda: GraphDialog(self, self.data_model).exec())
        self.csv_button = NERButton("CSV", NERButton.Styles.BLUE)
        self.csv_button.pressed.connect(lambda: ExportDialog(self, self.data_model).exec())
        self.database_button = NERButton("Database", NERButton.Styles.BLUE)
        self.database_button.pressed.connect(lambda: DatabaseDialog(self, self.data_model).exec())
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


class SdCardWindow(QMainWindow):
    """Main window in for the SD Card connection."""

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.setWindowTitle("Telemetry Hub")
        self.setMinimumSize(QSize(800, 480))

        self.file_model = FileModel(self)
        data_model = DataModelManager(self)

        # Setup window
        hlayout = QHBoxLayout()
        hlayout.addWidget(FileView(self, self.file_model))
        hlayout.addWidget(ProcessView(self, self.file_model, data_model))

        vlayout = QVBoxLayout()
        vlayout.addLayout(hlayout)
        vlayout.addWidget(OptionsView(self, data_model))

        widget = QWidget()
        widget.setLayout(vlayout)
        self.setCentralWidget(widget)

        # Setup menu bar
        menu = self.menuBar()
        edit_menu = menu.addMenu("Edit")
        help_menu = menu.addMenu("Help")

        format_submenu = QMenu("Format", self)
        edit_menu.addMenu(format_submenu)

        self.options: Dict[int, QAction] = {}
        self.enabled_id = self.file_model.getFormat().value

        for format in LogFormat:
            act = QAction(format.name, self)
            format_submenu.addAction(act)
            act.setCheckable(True)
            act.triggered.connect(lambda state, id=format.value : self.formatClicked(state, id))
            self.options[format.value] = act

        self.options.get(self.enabled_id).setChecked(True)
        
        help_action_1 = help_menu.addAction("Message Info")
        help_action_2 = help_menu.addAction("Data Info")
        help_action_1.triggered.connect(lambda : MessageIds(self).show())
        help_action_2.triggered.connect(lambda : DataIds(self).show())
    
    def formatClicked(self, state: bool, id: int):
        """
        Callback for format menu options to verify one and always one format is selected at a time.
            - state is whether the format given by id should be checked or not
        """
        if not state:
            self.options.get(id).setChecked(True)
        else:
            self.options.get(self.enabled_id).setChecked(False)
            self.enabled_id = id
            self.file_model.setFormat(LogFormat(id))






