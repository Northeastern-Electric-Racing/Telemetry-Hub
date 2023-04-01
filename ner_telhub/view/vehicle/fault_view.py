import os
import json
from PyQt6.QtCore import QDateTime, QUrl, QTimer, Qt
import sys
from ner_telhub.model.data_models import DataModelManager
from PyQt6.QtWidgets import (
    QLabel, QVBoxLayout, QWidget, QMessageBox, QApplication, QHBoxLayout, QSizePolicy, QFrame, QApplication
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from ner_telhub.widgets.styled_widgets import NERButton
from datetime import datetime

class FaultView(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        # Dashboard title
        title_label = QLabel("Fault View")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")

        # Example data label
        data_label = QLabel("Example Data: 0")
        data_label.setObjectName("data_label")

        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        layout.addWidget(title_label, stretch=0)
        layout.addWidget(data_label, stretch=0)

        # Add other UI components here
        # ...

        self.setLayout(layout)
        
        #Initialize data models
        
        # try:
        #     logging_model = model.getDataModel(...)
        #     self.logging_data = logging_model.getData()
        # except Exception as e:
        #     #QMessageBox.critical(self, "Error", f"Error getting data. {e}")
        #     self.logging_data = [
        #         (datetime.now(), 0),
        #     ]

        try:
            twelvev_model = model.getDataModel(113)
            self.twelvev_data = twelvev_model.getData()
        except Exception as e:
            #QMessageBox.critical(self, "Error", f"Error getting data. {e}")
            self.twelvev_data = [
                (datetime.now(), 0),
            ]

        try:
            packsoc_model = model.getDataModel(113)
            self.packsoc_data = packsoc_model.getData()
        except Exception as e:
            #QMessageBox.critical(self, "Error", f"Error getting data. {e}")
            self.packsoc_data = [
                (datetime.now(), 0),
            ]
            

        self.setLayout(layout)
        self.timer = QTimer(self)
        #self.timer.timeout.connect(self.update_logging_status)
        self.timer.timeout.connect(self.update_batteryvoltage)
        self.timer.timeout.connect(self.update_packsoc)
        self.timer.start(250)  # Call the update_map function every 500ms.
    
    def update_batteryvoltage(self):
        try:
            twelvev_model = model.getDataModel(113)
            self.twelvev_data = twelvev_model.getData()
        except Exception as e:
            #QMessageBox.critical(self, "Error", f"Error getting data. {e}")
            self.twelvev_data = [
                (datetime.now(), 0),
            ]
        


    def update_packsoc(self):
        try:
            packsoc_model = model.getDataModel(113)
            self.packsoc_data = packsoc_model.getData()
        except Exception as e:
            #QMessageBox.critical(self, "Error", f"Error getting data. {e}")
            self.packsoc_data = [
                (datetime.now(), 0),
            ]
        

        

        