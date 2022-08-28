from PyQt6.QtWidgets import (
    QVBoxLayout, QWidget, QDialog,
    QTableWidget, QTableWidgetItem
)
from PyQt6.QtCore import Qt

from ner_telhub.model.processing.master_mapping import *



class MessageIds(QDialog):
    """Shows information on message ids in the system."""

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setWindowTitle("CAN Message Information")
        
        message_ids = MESSAGE_IDS
        message_info = DECODE_DATA

        # Create table 
        table = QTableWidget(self)
        table.setRowCount(len(message_ids))
        table.setColumnCount(3)
        table.verticalHeader().hide()
        table.horizontalHeader().setSectionsClickable(False)

        # Set table data
        for row, id in enumerate(message_ids):
            item0 = QTableWidgetItem(hex(id))
            item1 = QTableWidgetItem(str(message_ids[id])) 
            item2 = QTableWidgetItem(message_info[message_ids[id]]["description"])
            item0.setFlags(Qt.ItemFlag.NoItemFlags)     
            item1.setFlags(Qt.ItemFlag.NoItemFlags)   
            item2.setFlags(Qt.ItemFlag.NoItemFlags) 
            table.setItem(row, 0, item0)
            table.setItem(row, 1, item1)
            table.setItem(row, 2, item2)
        table.setHorizontalHeaderLabels(["CAN ID", "Message ID", "Description"])
        table.resizeColumnsToContents()
        table.resizeRowsToContents()

        layout = QVBoxLayout()
        layout.addWidget(table)
        self.setLayout(layout)



class DataIds(QDialog):
    """Shows information on data ids in the system."""

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setWindowTitle("Data Information")
        data = DATA_IDS

        # Create table 
        table = QTableWidget(self)
        table.setRowCount(len(data))
        table.setColumnCount(2)
        table.verticalHeader().hide()
        table.horizontalHeader().setSectionsClickable(False)

        # Set table data
        for row, id in enumerate(data):
            item0 = QTableWidgetItem(str(id))
            item1 = QTableWidgetItem(data[id]) 
            item0.setFlags(Qt.ItemFlag.NoItemFlags)     
            item1.setFlags(Qt.ItemFlag.NoItemFlags)      
            table.setItem(row, 0, item0)
            table.setItem(row, 1, item1)
        table.setHorizontalHeaderLabels(["ID", "Name"])
        table.resizeColumnsToContents()
        table.resizeRowsToContents()

        layout = QVBoxLayout()
        layout.addWidget(table)
        self.setLayout(layout)
        

