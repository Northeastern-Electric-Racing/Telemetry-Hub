import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel,
    QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton
)
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon, QPixmap, QFont, QFontDatabase

from ner_telhub.view.database.window import DatabaseWindow
from ner_telhub.view.sd_card.window import SdCardWindow
from ner_telhub.view.vehicle.window import VehicleWindow

resources = os.path.dirname(__file__) + "/../resources"

try:
    from ctypes import windll  # Only exists on Windows.
    myappid = 'ner.telhub'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass


class MainWindow(QMainWindow):
    """
    Main window which opens first when running the app.
    """

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Telemetry Hub")
        self.setFixedSize(QSize(960, 720))
        self.setWindowIcon(QIcon(os.path.join(resources, "ner_logo.ico")))

        self.vehicle_window = None
        self.sd_card_window = None
        self.database_window = None

        main_layout = QVBoxLayout()
        bottom_layout = QHBoxLayout()

        id = QFontDatabase.addApplicationFont(
            os.path.join(resources, "MachineGunk.ttf"))
        families = QFontDatabase.applicationFontFamilies(id)

        title = QLabel("--- T E L E M E T R Y   H U B ---")
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter |
                           Qt.AlignmentFlag.AlignVCenter)
        title_font = QFont(families[0], 80)
        title_font.setBold(True)
        title_font.setItalic(True)
        title_font.setPointSize(40)
        title.setFont(title_font)
        main_layout.addWidget(title)

        lbl = QLabel()
        lbl.setPixmap(QPixmap(os.path.join(resources, "aoun_racing2.png")))
        lbl.setAlignment(Qt.AlignmentFlag.AlignRight |
                         Qt.AlignmentFlag.AlignBottom)
        main_layout.addWidget(lbl)

        BUTTON_STYLE = """QPushButton {color: white; background-color: #EE3535; font-size: 20px; border-radius: 10px; padding: 10% 10%;}
            QPushButton:hover {background-color: #ff8080; color: white;}"""

        self.vehicle_button = QPushButton("Vehicle", self)
        self.vehicle_button.setStyleSheet(BUTTON_STYLE)
        self.sd_card_button = QPushButton("SD Card", self)
        self.sd_card_button.setStyleSheet(BUTTON_STYLE)
        self.database_button = QPushButton("Database", self)
        self.database_button.setStyleSheet(BUTTON_STYLE)

        self.vehicle_button.clicked.connect(self.openVehicleWindow)
        self.sd_card_button.clicked.connect(self.openSdCardWindow)
        self.database_button.clicked.connect(self.openDatabaseWindow)
        self.vehicle_button.setToolTip(
            "Open a live connection with the vehicle")
        self.sd_card_button.setToolTip(
            "Open a window for processing SD card log files")
        self.database_button.setToolTip(
            "Open a window for querying historical data")
        bottom_layout.addWidget(self.vehicle_button)
        bottom_layout.addWidget(self.sd_card_button)
        bottom_layout.addWidget(self.database_button)
        main_layout.addLayout(bottom_layout)

        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

    def openVehicleWindow(self):
        self.vehicle_button.setDisabled(True)
        self.vehicle_window = VehicleWindow(self)
        self.vehicle_window.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.vehicle_window.destroyed.connect(
            lambda: self.vehicle_button.setDisabled(False))
        self.vehicle_window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.vehicle_window.show()

    def openSdCardWindow(self):
        self.sd_card_button.setDisabled(True)
        self.sd_card_window = SdCardWindow(self)
        self.sd_card_window.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.sd_card_window.destroyed.connect(
            lambda: self.sd_card_button.setDisabled(False))
        self.sd_card_window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.sd_card_window.show()

    def openDatabaseWindow(self):
        self.database_button.setDisabled(True)
        self.database_window = DatabaseWindow(self)
        self.database_window.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.database_window.destroyed.connect(
            lambda: self.database_button.setDisabled(False))
        self.database_window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.database_window.show()


def run():
    """
    Runs the app by creating and executing the main window.
    """
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
