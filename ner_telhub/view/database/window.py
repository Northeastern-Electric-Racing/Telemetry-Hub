from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QProgressBar
)
from PyQt6.QtCore import QSize
from ner_telhub.model.data_models import DataModelManager
from ner_telhub.view.database.query_toolbar import QueryToolbar
from ner_telhub.widgets.graphing_widgets.graph_dashboard_widget import GraphDashboardWidget
from ner_telhub.utils.timestream import TimestreamQueryService
from ner_telhub.widgets.menu_widgets.data_ids import DataIds



class DatabaseWindow(QMainWindow):
    """
    Main database window for querying/showing historical data.
    """

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.data_model = DataModelManager(self)
        self.query_service = TimestreamQueryService()

        # Window config
        self.setWindowTitle("Telemetry Hub")
        self.setMinimumSize(QSize(960, 720))

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.label = QLabel()
        self.label.setVisible(False)

        # Layout config
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(
            QueryToolbar(
                self,
                self.data_model,
                self.query_service,
                self.progress_bar,
                self.label))
        self.main_layout.addWidget(self.progress_bar)
        self.main_layout.addWidget(self.label)
        self.main_layout.addWidget(
            GraphDashboardWidget(
                self, self.data_model, False))

        widget = QWidget(self)
        widget.setLayout(self.main_layout)
        self.setCentralWidget(widget)

        # Menu bar
        menu = self.menuBar()
        help_menu = menu.addMenu("Help")

        help_action_1 = help_menu.addAction("Data Info")
        help_action_1.triggered.connect(lambda: DataIds(self).show())
