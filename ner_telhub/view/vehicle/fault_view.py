from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout
)

from ner_telhub.model.message_models import MessageModel

class FaultView(QWidget):
    """
    View for debugging faults from the car
    """

    def __init__(self, parent: QWidget, model: MessageModel):
        super(FaultView, self).__init__(parent)
        layout = QVBoxLayout()
        
        self._model = model

        self.setLayout(layout)