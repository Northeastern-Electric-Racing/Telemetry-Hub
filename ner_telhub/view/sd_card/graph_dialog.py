from PyQt6.QtWidgets import (
      QWidget, QVBoxLayout, QDialog
)
from ner_telhub import colors
from ner_telhub.model.data_models import DataModelManager
from ner_telhub.widgets.graphing_widgets.graph_dashboard_widget import GraphDashboardWidget
from ner_telhub.widgets.styled_widgets.ner_button import NERButton
from ner_telhub.widgets.styled_widgets.ner_toolbar import NERToolbar

class GraphDialog(QDialog):
    """Shows a dashboard for data in the system."""

    def __init__(self, parent: QWidget, model: DataModelManager):
        super().__init__(parent)
        self.setWindowTitle("Graph View")

        toolbar = NERToolbar()
        self.setStyleSheet(
            "QToolBar { background-color: " +
            colors.SECONDARY_BACKGROUND +
            "; padding: 5%; border: none}")
        self.screen_button = NERButton("Full Screen", NERButton.Styles.GRAY)
        self.screen_button.pressed.connect(self.changeScreen)
        toolbar.addLeft(self.screen_button)

        layout = QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(GraphDashboardWidget(parent, model, False))
        self.setLayout(layout)

    def changeScreen(self):
        if self.screen_button.text() == "Full Screen":
            self.showFullScreen()
            self.screen_button.setText("Minimize")
        else:
            self.showNormal()
            self.screen_button.setText("Full Screen")
