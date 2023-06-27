from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QTabWidget, QVBoxLayout)
from PyQt6.QtCore import QSize
from ner_telhub.model.data_models import DataModelManager
from ner_telhub.model.message_model import MessageModel
from ner_telhub.model.filter_models import ReceiveFilterModel
from ner_telhub.view.vehicle.can_view.can_view import CanView
from ner_telhub.view.vehicle.data_view.data_view import DataView
from ner_telhub.view.vehicle.fault_view.fault_view import FaultView
from ner_telhub.view.vehicle.live_toolbar import LiveToolbar
from ner_telhub.view.vehicle.map_view.map_view import MapView
from ner_telhub.widgets.menu_widgets.data_ids import DataIds
from ner_telhub.widgets.menu_widgets.message_ids import MessageIds


class VehicleWindow(QMainWindow):
    """
    Main vehicle window containing various views.
    """

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.data_model = DataModelManager(self)
        self.data_model.setDataLimiting(True)
        self.message_model = MessageModel(self, self.data_model)
        self.receive_filter_model = ReceiveFilterModel(
            self, self.message_model)

        self.views = {0: ("CAN",
                          CanView(self,
                                  self.message_model,
                                  self.data_model,
                                  self.receive_filter_model)),
                      1: ("Data",
                          DataView(self,
                                   self.data_model)),
                      2: ("Map",
                          MapView(self,
                                  self.data_model)),
                      3: ("Fault",
                          FaultView(self,
                                    self.data_model))}

        # Window config
        self.setWindowTitle("Telemetry Hub")
        self.setMinimumSize(QSize(960, 720))

        # Create a QTabWidget
        self.tab_widget = QTabWidget(self)

        # Add the views as tabs to the QTabWidget
        for view in self.views.values():
            self.tab_widget.addTab(view[1], view[0])

        # Modify the QVBoxLayout to include the QTabWidget instead of the
        # QStackedLayout
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(
            LiveToolbar(
                self,
                self.message_model,
                self.data_model))
        self.main_layout.addWidget(self.tab_widget)

        widget = QWidget(self)
        widget.setLayout(self.main_layout)
        self.setCentralWidget(widget)

        # Menu bar
        menu = self.menuBar()
        help_menu = menu.addMenu("Help")
        help_action_1 = help_menu.addAction("Message Info")
        help_action_2 = help_menu.addAction("Data Info")
        help_action_1.triggered.connect(lambda: MessageIds(self).show())
        help_action_2.triggered.connect(lambda: DataIds(self).show())
