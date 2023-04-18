from typing import Dict, List

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QHBoxLayout, QDialog, QDialogButtonBox, QComboBox
)

from ner_telhub.colors import TABLE_BACKGROUND_1, TABLE_BACKGROUND_2
from ner_telhub.model.data_models import DataModelManager
from ner_processing.decode_statuses import STATUS_MAP, getStatus


class FaultEntry():
    def __init__(self, data_id: int, name: str, model: DataModelManager):
        self.data_id = data_id
        self.name = name
        self.model = model
        self.value = None
        self.time = None
        self.last_time_high = None

    def update(self):
        try:
            self.value = self.model.getDataModel(
                self.data_id).getLastestValue()
            self.time = self.model.getDataModel(self.data_id).getLastestTime()
            if self.value == 1:
                self.last_time_high = self.time
        except BaseException:
            self.value = None
            self.time = None
            self.last_time_high = None


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


class DataUtils():
    """
    Utility methods for data converstions
    """

    @staticmethod
    def text_to_data(input_text: str) -> int:
        """
        Converts a textual type of data to the internal data ID.
        """
        parts = input_text.split(' ', 1)
        if len(parts) > 1:
            return int(parts[0])
        return None

    @staticmethod
    def data_to_text(data_id: int) -> str:
        """
        Converts a data ID to the textual type of data recognizable by the user.
        """
        if data_id is not None:
            return f"{data_id} {DataModelManager.getDataType(data_id)}"
        else:
            return "None"


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
