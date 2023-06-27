from typing import List
from PyQt6.QtWidgets import (
      QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QComboBox
)
from ner_processing.decode_statuses import STATUS_MAP
from ner_telhub.view.vehicle.fault_view.data_utils import DataUtils

class FaultLayout(QWidget):
    """
    Class to represent an entry for a fault status in the Add Dialog.
    """

    def __init__(self, parent: QWidget):
        super(FaultLayout, self).__init__(parent)

        # Create data ID entry layout
        self.data_layout = QHBoxLayout()
        self.data_layout.addWidget(QLabel("Select Fault ID:"))

        self.data_combo = QComboBox()
        data_names = [DataUtils.data_to_text(d) for d in STATUS_MAP.keys()]
        self.data_combo.addItems(data_names)
        self.data_combo.currentTextChanged.connect(self.update_statuses)

        self.data_layout.addWidget(self.data_combo)
        self.data_layout.setStretch(1, 1)

        # Create status entry layout
        self.status_layout = QHBoxLayout()
        self.status_layout.addWidget(QLabel("Select Status:"))

        self.status_combos = []
        status_combo = QComboBox()
        self.status_combos.append(status_combo)

        self.add_status_button = QPushButton("Add Status")
        self.remove_status_button = QPushButton("Remove Status")
        self.remove_status_button.setEnabled(False)
        self.add_status_button.clicked.connect(self.add_status)
        self.remove_status_button.clicked.connect(self.remove_status)

        self.status_layout.addWidget(status_combo)
        self.status_layout.addWidget(self.add_status_button)
        self.status_layout.addWidget(self.remove_status_button)

        layout = QVBoxLayout()
        layout.addLayout(self.data_layout)
        layout.addLayout(self.status_layout)
        self.setLayout(layout)

        self.update_statuses(self.data_combo.currentText())

    def update_statuses(self, selected_data):
        """
        Updates a status combo box with the statuses for a specific ID.
        """
        data_id = DataUtils.text_to_data(selected_data)
        status_list = list(STATUS_MAP[data_id].keys())
        for sc in self.status_combos:
            sc.clear()
            sc.addItems(status_list)
            sc.setEnabled(True)

    def add_status(self):
        """
        Adds a status combo box.
        """
        status_combo = QComboBox()
        data_id = DataUtils.text_to_data(self.data_combo.currentText())
        status_list = list(STATUS_MAP[data_id].keys())
        status_combo.addItems(status_list)
        self.status_layout.insertWidget(
            len(self.status_combos) + 1, status_combo)
        self.status_combos.append(status_combo)
        self.remove_status_button.setEnabled(True)

    def remove_status(self):
        """
        Removes the last status combo box.
        """
        if len(self.status_combos) > 1:
            self.status_layout.removeWidget(self.status_combos.pop())
        if len(self.status_combos) == 1:
            self.remove_status_button.setEnabled(False)

    def get_data_id(self) -> int:
        """
        Gets the data ID of this widget.
        """
        return DataUtils.text_to_data(self.data_combo.currentText())

    def get_statuses(self) -> List[str]:
        """
        Gets the selected status list of this widget.
        """
        return [sc.currentText() for sc in self.status_combos]
