from typing import Dict, List

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QHBoxLayout, QDialog
)

from ner_telhub.colors import TABLE_BACKGROUND_1, TABLE_BACKGROUND_2
from ner_telhub.model.data_models import DataModelManager
from ner_processing.decode_statuses import STATUS_MAP, getStatus
from ner_telhub.view.vehicle.fault_view.add_dialog import AddDialog
from ner_telhub.view.vehicle.fault_view.fault_entry import FaultEntry
from ner_telhub.view.vehicle.fault_view.remove_dialog import RemoveDialog

class FaultView(QWidget):
    """
    View for displaying faults.
    """

    def __init__(self, parent: QWidget, model: DataModelManager):
        super(FaultView, self).__init__(parent)
        self.model = model
        # Stores the faults used to populate the table
        self.faults: Dict[int, List[FaultEntry]] = {}

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["Last Time Updated", "Fault ID", "Fault Statuses", "Status Value", "Last Time Faulted"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Add the Add and Remove buttons
        add_button = QPushButton("Add")
        remove_button = QPushButton("Remove")
        add_button.clicked.connect(self.add_fault)
        remove_button.clicked.connect(self.remove_fault)

        button_layout = QHBoxLayout()
        button_layout.addWidget(add_button)
        button_layout.addWidget(remove_button)

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_table)
        self.timer.start(250)

    def update_table(self):
        """
        Update the table with the latest fault data.
        """
        self.table.setRowCount(0)  # Clear the table

        # Add rows with fault data
        for _, data_id in enumerate(self.faults):
            for fault_index, fault in enumerate(self.faults[data_id]):
                row_position = self.table.rowCount()
                self.table.insertRow(row_position)
                # Adjust row height for sub-rows
                self.table.setRowHeight(row_position, 30)

                # Set alternating row colors
                if row_position % 2 == 0:
                    background_color = QColor(*TABLE_BACKGROUND_1)
                else:
                    background_color = QColor(*TABLE_BACKGROUND_2)

                # Create QTableWidgetItem for the fault name
                fault_item = QTableWidgetItem(fault.name)
                fault_item.setBackground(background_color)

                # Set font style and size
                font = QFont()
                font.setPointSize(14)
                fault_item.setFont(font)

                self.table.setItem(row_position, 2, fault_item)

                fault.update()
                if fault.value is not None:
                    data_value = fault.value
                    data_time = fault.time
                    last_time_faulted = fault.last_time_high
                    status_value = getStatus(data_id, data_value, fault.name)
                else:
                    status_value = "None"
                    data_time = "None"
                    last_time_faulted = "None"

                # Create QTableWidgetItem for the status value
                value_item = QTableWidgetItem(str(status_value))
                value_item.setBackground(background_color)
                value_item.setFont(font)

                self.table.setItem(row_position, 3, value_item)

                last_time_faulted_item = QTableWidgetItem(
                    str(last_time_faulted))
                last_time_faulted_item.setBackground(background_color)
                last_time_faulted_item.setFont(font)

                self.table.setItem(row_position, 4, last_time_faulted_item)

                # Create QTableWidgetItem for Time and Fault ID only for the
                # first status
                if fault_index == 0:
                    time_item = QTableWidgetItem(str(data_time))
                    data_item = QTableWidgetItem(
                        self.model.getDataType(data_id))

                    time_item.setBackground(background_color)
                    data_item.setBackground(background_color)

                    time_item.setFont(font)
                    data_item.setFont(font)

                    self.table.setItem(row_position, 0, time_item)
                    self.table.setItem(row_position, 1, data_item)

            # Merge cells in the Time and Fault ID columns after all associated
            # statuses have been processed
            num_statuses = len(self.faults[data_id])
            if num_statuses > 1:
                self.table.setSpan(
                    row_position - num_statuses + 1, 0, num_statuses, 1)
                self.table.setSpan(
                    row_position - num_statuses + 1, 1, num_statuses, 1)

    def add_fault(self):
        """
        Add a new fault using the AddDialog.
        """
        dialog = AddDialog(self, self.model)
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            added_ids = dialog.get_selected_fault_ids()
            added_statuses = dialog.get_selected_statuses()
            for index, fault_id in enumerate(added_ids):
                self.faults[fault_id] = [
                    FaultEntry(
                        fault_id,
                        status,
                        self.model) for status in added_statuses[index]]

    def remove_fault(self):
        """
        Remove the selected fault from the table and data model using a popup window with a drop-down menu to select the Fault ID to remove.
        """
        dialog = RemoveDialog(self, self.model, self.faults.keys())
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted and dialog.removed_fault is not None:
            self.faults.pop(dialog.removed_fault)








