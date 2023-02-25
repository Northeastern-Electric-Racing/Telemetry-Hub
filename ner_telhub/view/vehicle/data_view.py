from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout
)

from ner_telhub.model.data_models import DataModelManager
from ner_telhub.widgets.graphing_widgets import GraphDashboardWidget


class DataView(QWidget):
    """
    View for graphing data.
    """

    def __init__(self, parent: QWidget, model: DataModelManager):
        super(DataView, self).__init__(parent)
        layout = QVBoxLayout()
        layout.addWidget(GraphDashboardWidget(self, model, True))
        self.setLayout(layout)
