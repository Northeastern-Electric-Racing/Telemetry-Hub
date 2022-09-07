import sys, os

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, 
    QVBoxLayout, QWidget, QPushButton
)
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon, QPixmap

from ner_telhub.view.database.window import DatabaseWindow
from ner_telhub.view.network.window import NetworkWindow
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

        self.vehicle_window = None
        self.network_window = None
        self.sd_card_window = None
        self.database_window = None

        self.setWindowTitle("Telemetry Hub")
        self.setFixedSize(QSize(400, 400))
        self.setWindowIcon(QIcon(os.path.join(resources, "ner_logo.ico")))

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
        vehicle_button = QPushButton("Vehicle")
        network_button = QPushButton("Network")
        sd_card_button = QPushButton("SD Card")
        database_button = QPushButton("Database")
        vehicle_button.clicked.connect(self.openVehicleWindow)
        network_button.clicked.connect(self.openNetworkWindow)
        sd_card_button.clicked.connect(self.openSdCardWindow)
        database_button.clicked.connect(self.openDatabaseWindow)
        vehicle_button.setStyleSheet("color: white; background-color: #FF5656")
        sd_card_button.setStyleSheet("color: white; background-color: #FF5656")
        network_button.setDisabled(True)
        database_button.setDisabled(True)
        layout.addWidget(vehicle_button)
        layout.addWidget(network_button)
        layout.addWidget(sd_card_button)
        layout.addWidget(database_button)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def openVehicleWindow(self):
        if self.vehicle_window is None:
            self.vehicle_window = VehicleWindow()
            self.vehicle_window.show()
        else:
            self.vehicle_window.close()
            self.vehicle_window = None

    def openNetworkWindow(self):
        if self.network_window is None:
            self.network_window = NetworkWindow()
            self.network_window.show()
        else:
            self.network_window.close()
            self.network_window = None

    def openSdCardWindow(self):
        if self.sd_card_window is None:
            self.sd_card_window = SdCardWindow()
            self.sd_card_window.show()
        else:
            self.sd_card_window.close()
            self.sd_card_window = None

    def openDatabaseWindow(self):
        if self.database_window is None:
            self.database_window = DatabaseWindow()
            self.database_window.show()
        else:
            self.database_window.close()
            self.database_window = None
    

def run():
    """
    Runs the app by creating and executing the main window. 
    """
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()