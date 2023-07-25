from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
      QVBoxLayout, QWidget, QDialog,
      QTableWidget, QTableWidgetItem
)

from ner_processing.master_mapping import MESSAGE_IDS
class MessageIds(QDialog):
    """Shows information on message ids in the system."""

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setWindowTitle("CAN Message Information")

        message_info = MESSAGE_IDS

        # Create table
        table = QTableWidget(self)
        table.setRowCount(len(message_info))
        table.setColumnCount(2)
        table.verticalHeader().hide()
        table.horizontalHeader().setSectionsClickable(False)

        # Set table data
        for row, id in enumerate(message_info):
            item0 = QTableWidgetItem(hex(id))
            item1 = QTableWidgetItem(message_info[id]["description"])
            item0.setFlags(Qt.ItemFlag.NoItemFlags)
            item1.setFlags(Qt.ItemFlag.NoItemFlags)
            table.setItem(row, 0, item0)
            table.setItem(row, 1, item1)
        table.setHorizontalHeaderLabels(["CAN ID", "Description"])
        table.resizeColumnsToContents()
        table.resizeRowsToContents()

        layout = QVBoxLayout()
        layout.addWidget(table)
        self.setLayout(layout)
