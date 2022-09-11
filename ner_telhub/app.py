import sys, os

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, 
    QVBoxLayout, QWidget
)
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon, QPixmap

from ner_telhub.view.database.window import DatabaseWindow
from ner_telhub.view.sd_card.window import SdCardWindow
from ner_telhub.view.vehicle.window import VehicleWindow
from ner_telhub.widgets.styled_widgets import NERButton

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
        self.setFixedSize(QSize(400, 400))
        self.setWindowIcon(QIcon(os.path.join(resources, "ner_logo.ico")))

        self.vehicle_window = None
        self.sd_card_window = None
        self.database_window = None

        layout = QVBoxLayout()

        title = QLabel("Telemetry Hub")
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        title_font = title.font()
        title_font.setBold(True)
        title_font.setPointSize(20)
        title.setFont(title_font)
        layout.addWidget(title)

        lbl = QLabel()
        lbl.setPixmap(QPixmap(os.path.join(resources, "ner_logo.png")))
        lbl.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(lbl)

        layout.addWidget(QLabel("Select an option below to connect to:"))
        self.vehicle_button = NERButton("Vehicle", NERButton.Styles.RED)
        self.sd_card_button = NERButton("SD Card", NERButton.Styles.RED)
        self.database_button = NERButton("Database")
        self.vehicle_button.clicked.connect(self.openVehicleWindow)
        self.sd_card_button.clicked.connect(self.openSdCardWindow)
        self.database_button.clicked.connect(self.openDatabaseWindow)
        self.database_button.setDisabled(True)
        layout.addWidget(self.vehicle_button)
        layout.addWidget(self.sd_card_button)
        layout.addWidget(self.database_button)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def openVehicleWindow(self):
        self.vehicle_button.setDisabled(True)
        self.vehicle_window = VehicleWindow(self)
        self.vehicle_window.destroyed.connect(lambda: self.vehicle_button.setDisabled(False))
        self.vehicle_window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.vehicle_window.show()

    def openSdCardWindow(self):
        self.sd_card_button.setDisabled(True)
        self.sd_card_window = SdCardWindow(self)
        self.sd_card_window.destroyed.connect(lambda: self.sd_card_button.setDisabled(False))
        self.sd_card_window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.sd_card_window.show()

    def openDatabaseWindow(self):
        self.database_button.setDisabled(True)
        self.database_window = DatabaseWindow(self)
        self.database_window.destroyed.connect(lambda: self.database_button.setDisabled(False))
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