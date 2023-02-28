from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QStackedLayout,
    QMessageBox, QDialog, QDialogButtonBox,
    QVBoxLayout, QLabel, QLineEdit,
    QGridLayout, QFileDialog
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QSize

from ner_live.xbee import XBee
from ner_live.live_input import LiveInput, LiveInputException

from ner_telhub import colors
from ner_telhub.model.data_models import DataModelManager
from ner_telhub.model.message_models import MessageModel
from ner_telhub.model.filter_models import ReceiveFilterModel
from ner_telhub.view.vehicle.can_view import CanView
from ner_telhub.view.vehicle.data_view import DataView
from ner_telhub.widgets.menu_widgets import MessageIds, DataIds
from ner_telhub.widgets.styled_widgets import NERButton, NERToolbar


class FileDialog(QDialog):
    """Dialog to export data to a CSV file."""

    def __init__(self, parent: QWidget, model: DataModelManager):
        super().__init__(parent)

        self.setWindowTitle("Export as CSV")
        self.model = model

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
        worker.signals.error.connect(
            lambda error: QMessageBox.critical(
                self, "Export Error", error[1].__str__()))
        worker.signals.message.connect(
            lambda msg: QMessageBox.about(
                self, "Export Status", msg))
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


class LiveToolbar(NERToolbar):
    def __init__(
            self,
            parent: QWidget,
            message_model: MessageModel,
            data_model: DataModelManager,
            input: LiveInput):
        super(LiveToolbar, self).__init__(parent)

        self.message_model = message_model
        self.model = data_model
        self.input = input
        self.feed_started = False
        self.setStyleSheet(
            "QToolBar { background-color: " +
            colors.SECONDARY_BACKGROUND +
            "; padding: 5%; border: none}")

        self.start_button = NERButton("Start", NERButton.Styles.GREEN)
        self.start_button.pressed.connect(self.start)
        self.start_button.setToolTip("Start/stop the live data feed")
        clear_button = NERButton("Clear", NERButton.Styles.RED)
        clear_button.pressed.connect(self.clear)
        clear_button.setToolTip("Clear all data currently received")
        export_button = NERButton("Export", NERButton.Styles.BLUE)
        export_button.pressed.connect(self.export)
        export_button.setToolTip("Export received data to a CSV file")
        self.addLeft(self.start_button)
        self.addLeft(clear_button)
        self.addLeft(export_button)

    def start(self):
        if not self.feed_started:
            try:
                self.input.start()
                self.start_button.setText("Stop")
                self.start_button.changeStyle(NERButton.Styles.RED)
                self.feed_started = not self.feed_started
            except LiveInputException as e:
                QMessageBox.information(
                    self, "Couldn't start input: ", e.message)
        else:
            try:
                self.input.stop()
                self.start_button.setText("Start")
                self.start_button.changeStyle(NERButton.Styles.GREEN)
                self.feed_started = not self.feed_started
            except LiveInputException as e:
                QMessageBox.information(
                    self, "Couldn't stop input:", e.message)

    def clear(self):
        self.model.deleteAllData()
        self.message_model.deleteAllMessages()

    def export(self):
        if not self.feed_started:
            FileDialog(self, self.model).exec()
        else:
            QMessageBox.information(
                self,
                "Export failed",
                "Cannot export to CSV while collecting data.")


class VehicleWindow(QMainWindow):
    """
    Main vehicle window containing various views.
    """

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.data_model = DataModelManager(self)
        self.message_model = MessageModel(self, self.data_model)
        self.receive_filter_model = ReceiveFilterModel(
            self, self.message_model)
        self.connection = XBee(self.message_model)

        self.views = {0: ("CAN",
                          CanView(self,
                                  self.message_model,
                                  self.data_model,
                                  self.receive_filter_model,
                                  self.connection)),
                      1: ("Data",
                          DataView(self,
                                   self.data_model))}

        # Window config
        self.setWindowTitle("Telemetry Hub")
        self.setMinimumSize(QSize(960, 720))

        # Multi-view layout config
        self.stacked_layout = QStackedLayout()
        for view in self.views.values():
            self.stacked_layout.addWidget(view[1])
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(
            LiveToolbar(
                self,
                self.message_model,
                self.data_model,
                self.connection))
        self.main_layout.addLayout(self.stacked_layout)

        widget = QWidget(self)
        widget.setLayout(self.main_layout)
        self.setCentralWidget(widget)

        # Menu bar
        menu = self.menuBar()
        help_menu = menu.addMenu("Help")
        views_menu = menu.addMenu("View")

        help_action_1 = help_menu.addAction("Message Info")
        help_action_2 = help_menu.addAction("Data Info")
        help_action_1.triggered.connect(lambda: MessageIds(self).show())
        help_action_2.triggered.connect(lambda: DataIds(self).show())

        views_select_can = QAction(self.views.get(0)[0], self)
        views_select_data = QAction(self.views.get(1)[0], self)
        views_select_can.triggered.connect(self.selectCanView)
        views_select_data.triggered.connect(self.selectDataView)
        views_menu.addAction(views_select_can)
        views_menu.addAction(views_select_data)

        self.current_view_menu = menu.addMenu(
            self.views.get(self.stacked_layout.currentIndex())[0])
        self.current_view_menu.setDisabled(True)

    def selectCanView(self):
        self.stacked_layout.setCurrentIndex(0)
        self.current_view_menu.setTitle(self.views.get(0)[0])

    def selectDataView(self):
        self.stacked_layout.setCurrentIndex(1)
        self.current_view_menu.setTitle(self.views.get(1)[0])
