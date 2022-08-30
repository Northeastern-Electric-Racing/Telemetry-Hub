from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout
)

from ner_telhub.model.data_models import DataModel
from ner_telhub.widgets.graphing_widgets import GraphDashboardWidget


class DataView(QWidget):
    def __init__(self, model: DataModel):
        super(DataView, self).__init__()

        layout = QVBoxLayout()
        layout.addWidget(GraphDashboardWidget(model))
        self.setLayout(layout)