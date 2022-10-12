from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QToolBar
)

from ner_telhub.model.data_models import DataModelManager
from ner_telhub.widgets.graphing_widgets import GraphDashboardWidget
from ner_telhub.widgets.styled_widgets import NERButton


class DataView(QWidget):
    """
    View for graphing data.
    """
    
    def __init__(self, model: DataModelManager):
        super(DataView, self).__init__()

        toolbar = QToolBar()
        toolbar.setStyleSheet("background-color: white; padding: 5%")
        start_button = NERButton("Start", NERButton.Styles.GREEN)
        start_button.addStyle("margin-right: 5%")
        start_button.pressed.connect(self.start)
        record_button = NERButton("Record", NERButton.Styles.BLUE)
        record_button.addStyle("margin-right: 5%")
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