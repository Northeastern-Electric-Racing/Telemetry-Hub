from typing import List
from PyQt6.QtWidgets import (
      QDialog, QVBoxLayout, QDialogButtonBox, QWidget, QComboBox, QLabel
)
from ner_telhub.model.data_models import DataModelManager
from ner_telhub.view.vehicle.fault_view.data_utils import DataUtils

class RemoveDialog(QDialog):
    """
    Dialog box to specify what faults to load in each row.
    """

    def __init__(
            self,
            parent: QWidget,
            model: DataModelManager,
            fault_ids: List[int]):
        super(RemoveDialog, self).__init__(parent)
        self.model = model

        self.setWindowTitle("Select Fault ID to Remove")

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Select Fault ID:"))

        self.fault_id_combo = QComboBox()
        self.fault_id_combo.addItems(
            [DataUtils.data_to_text(f) for f in fault_ids])
        layout.addWidget(self.fault_id_combo)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)
        self.setLayout(layout)

        self.removed_fault = None

    def accept(self):
        self.removed_fault = DataUtils.text_to_data(
            self.fault_id_combo.currentText())
        super().accept()
