from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QToolBar,
    QPushButton
)

from ner_telhub.model.data_models import DataModel
from ner_telhub.widgets.graphing_widgets import GraphDashboardWidget


class DataView(QWidget):
    def __init__(self, model: DataModel):
        super(DataView, self).__init__()

        toolbar = QToolBar()
        start_button = QPushButton("Start")
        start_button.setStyleSheet("color: white; background-color: #07D807")
        start_button.pressed.connect(self.start)
        record_button = QPushButton("Record")
        record_button.setStyleSheet("color: white; background-color: #0977E6")
        record_button.pressed.connect(self.record)
        toolbar.addWidget(start_button)
        toolbar.addWidget(record_button)

        layout = QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(GraphDashboardWidget(model))
        self.setLayout(layout)
    
    def start(self):
        pass

    def record(self):
        pass