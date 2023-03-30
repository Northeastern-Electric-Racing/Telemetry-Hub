from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout
)

from ner_telhub.model.data_models import DataModelManager
from PyQt6.QtWidgets import (
    QLabel, QVBoxLayout,
    QWidget, QMessageBox
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
from ner_telhub.widgets.styled_widgets import NERButton
from ner_telhub.model.data_models import DataModelManager


class MapView(QWidget):
    """
    View for showing location data.
    """

    def __init__(self, parent: QWidget, model: DataModelManager):
        super(MapView, self).__init__(parent)

        self.header = QLabel("This is the map view")
        self.button = NERButton("Button", NERButton.Styles.BLUE)
        self.button.pressed.connect(self.callback)

        layout = QVBoxLayout()
        layout.addWidget(self.header)
        layout.addWidget(self.button)

        view = QWebEngineView(self)
        view.load(QUrl("http://qt-project.org/"))
        view.show()

        self.setLayout(layout)

    def callback(self):
        """
        Called when the button is clicked.
        """
        QMessageBox.information(self, "Callback box", "You clicked the button")
