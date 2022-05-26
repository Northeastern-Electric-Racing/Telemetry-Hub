from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QLineEdit, 
    QVBoxLayout, QWidget, QPushButton, 
    QMenu, QStackedLayout
)
from PyQt6.QtGui import QAction, QCloseEvent
from PyQt6.QtCore import QSize, Qt

from actions import onFileAction1, onFileAction2

from views.can_view import CanView
from views.data_view import DataView
from views.test_view import TestView


class VehicleWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.views = {
            0: ("CAN", CanView()), 
            1: ("Data", DataView()), 
            2: ("Test", TestView())
        }

        # Window config
        self.setWindowTitle("Telemetry Hub")
        self.setFixedSize(QSize(900, 500))

        # Multi-view config
        self.main_layout = QStackedLayout()
        for view in self.views.values():
            self.main_layout.addWidget(view[1])

        widget = QWidget()
        widget.setLayout(self.main_layout)
        self.setCentralWidget(widget)

        # Menu bar
        menu = self.menuBar()
        file_menu = menu.addMenu("File")
        help_menu = menu.addMenu("Edit")
        edit_menu = menu.addMenu("Help")
        views_menu = menu.addMenu("View")

        file_action_1 = QAction("file action 1", self)
        file_action_2 = QAction("file action 2", self)
        file_action_1.triggered.connect(onFileAction1)
        file_action_2.triggered.connect(onFileAction2)
        file_menu.addAction(file_action_1)
        file_menu.addAction(file_action_2)

        views_select_can = QAction(self.views.get(0)[0], self)
        views_select_data = QAction(self.views.get(1)[0], self)
        views_select_test = QAction(self.views.get(2)[0], self)
        views_select_can.triggered.connect(self.select_can_view)
        views_select_data.triggered.connect(self.select_data_view)
        views_select_test.triggered.connect(self.select_test_view)
        views_menu.addAction(views_select_can)
        views_menu.addAction(views_select_data)
        views_menu.addAction(views_select_test)

        self.current_view_menu = menu.addMenu(self.views.get(self.main_layout.currentIndex())[0])
        self.current_view_menu.setDisabled(True)
    
    def select_can_view(self):
        self.main_layout.setCurrentIndex(0)
        self.current_view_menu.setTitle(self.views.get(0)[0])
    def select_data_view(self):
        self.main_layout.setCurrentIndex(1)
        self.current_view_menu.setTitle(self.views.get(1)[0])
    def select_test_view(self):
        self.main_layout.setCurrentIndex(2)
        self.current_view_menu.setTitle(self.views.get(2)[0])


# This is currently being used as a playground for exploring new widgets
class NetworkWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.button_is_checked = True
        
        self.setWindowTitle("Telemetry Hub")
        self.setFixedSize(QSize(900, 500))

        self.button = QPushButton("Start")
        self.button.clicked.connect(self.button_clicked)

        self.text_label = QLabel()
        self.event_label = QLabel()

        self.input = QLineEdit()
        self.input.textChanged.connect(self.text_label.setText)

        layout = QVBoxLayout()
        layout.addWidget(self.input)
        layout.addWidget(self.text_label)
        layout.addWidget(self.event_label)
        layout.addWidget(self.button)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)

    def contextMenuEvent(self, e):
        context = QMenu(self)
        context.addAction(QAction("test 1", self))
        context.addAction(QAction("test 2", self))
        context.addAction(QAction("test 3", self))
        context.exec(e.globalPos())

    def button_clicked(self):
        if self.button_is_checked:
            self.button.setText("Stop")
        else:
            self.button.setText("Start")

        self.button_is_checked = not self.button_is_checked
        print("The button was clicked")

    def mouseMoveEvent(self, e):
        self.event_label.setText("mouseMoveEvent")

    def mousePressEvent(self, e):
        self.event_label.setText("mousePressEvent")

    def mouseReleaseEvent(self, e):
        self.event_label.setText("mouseReleaseEvent")

    def mouseDoubleClickEvent(self, e):
        self.event_label.setText("mouseDoubleClickEvent")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.vehicle_window = None
        self.network_window = None
        self.sd_card_window = None
        self.influxdb_window = None

        self.setWindowTitle("Telemetry Hub")
        self.setFixedSize(QSize(300, 220))

        layout = QVBoxLayout()

        title = QLabel("Telemetry Hub")
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        title_font = title.font()
        title_font.setBold(True)
        title_font.setPointSize(20)
        title.setFont(title_font)
        layout.addWidget(title)

        layout.addWidget(QLabel("Select an option below to connect to:"))
        vehicle_button = QPushButton("Vehicle")
        network_button = QPushButton("Network")
        sd_card_button = QPushButton("SD Card")
        influxdb_button = QPushButton("InfluxDB")
        vehicle_button.clicked.connect(self.open_vehicle_window)
        network_button.clicked.connect(self.open_network_window)
        sd_card_button.clicked.connect(self.open_sd_card_window)
        influxdb_button.clicked.connect(self.open_influxdb_window)
        layout.addWidget(vehicle_button)
        layout.addWidget(network_button)
        layout.addWidget(sd_card_button)
        layout.addWidget(influxdb_button)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def open_vehicle_window(self):
        if self.vehicle_window is None:
            self.vehicle_window = VehicleWindow()
            self.vehicle_window.show()
        else:
            self.vehicle_window.close()
            self.vehicle_window = None
    def open_network_window(self):
        if self.network_window is None:
            self.network_window = NetworkWindow()
            self.network_window.show()
        else:
            self.network_window.close()
            self.network_window = None
    def open_sd_card_window(self):
        pass
    def open_influxdb_window(self):
        pass
    


app = QApplication([])

window = MainWindow()
window.show()

app.exec()