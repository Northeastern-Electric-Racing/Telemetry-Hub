from typing import List
from PyQt6.QtWidgets import (
      QDialog, QVBoxLayout, QPushButton, QHBoxLayout, QDialogButtonBox, QWidget
)
from ner_telhub.model.data_models import DataModelManager
from ner_telhub.view.vehicle.fault_view.fault_layout import FaultLayout

class AddDialog(QDialog):
    """
    Dialog box to specify what faults to load in each row.
    """

    def __init__(
            self,
            parent: QWidget,
            model: DataModelManager):
        super(AddDialog, self).__init__(parent)
        self.model = model

        layout = QVBoxLayout()
        self.setLayout(layout)

        add_fault_button = QPushButton("Add Fault")
        remove_fault_button = QPushButton("Remove Fault")
        add_fault_button.clicked.connect(self.add_fault_layout)
        remove_fault_button.clicked.connect(self.remove_fault_layout)

        fault_button_layout = QHBoxLayout()
        fault_button_layout.addWidget(add_fault_button)
        fault_button_layout.addWidget(remove_fault_button)

        layout.addLayout(fault_button_layout)

        self.fault_layouts = []
        self.main_fault_layout = QVBoxLayout()
        layout.addLayout(self.main_fault_layout)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)

    def add_fault_layout(self):
        fault_layout = FaultLayout(self)
        self.main_fault_layout.addWidget(fault_layout)
        self.fault_layouts.append(fault_layout)

    def remove_fault_layout(self):
        self.main_fault_layout.removeWidget(self.fault_layouts.pop())

    def accept(self):
        # self.selected_fault_ids = [layout.itemAt(1).widget().currentText() for layout in self.fault_layouts]
        # self.selected_statuses = [
        #     tuple(layout.itemAt(i).widget().currentText() for i in range(1, layout.count() - 2))
        #     for layout in self.status_layouts
        # ]
        super().accept()

    def get_selected_fault_ids(self) -> List[int]:
        return [fl.get_data_id() for fl in self.fault_layouts]

    def get_selected_statuses(self) -> List[List[str]]:
        return [fl.get_statuses() for fl in self.fault_layouts]
