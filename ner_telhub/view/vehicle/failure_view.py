from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QToolBar, QHBoxLayout, QLabel, QScrollArea
)
from PyQt6.QtCore import Qt

from ner_telhub.widgets.styled_widgets import NERButton

class FaultEntry(QWidget):
    """
    A row in the fault table.
    """

    def __init__(self, parent: QWidget, name, val, last_time_high, last_time_low, width, heading=False):
        super(FaultEntry, self).__init__(parent)
        self.setFixedSize(width, 100)

        layout = QHBoxLayout()

        self.name = QLabel(name)
        layout.addWidget(self.name)
        self.val = QLabel(val)
        layout.addWidget(self.val)
        self.last_time_high = QLabel(last_time_high)
        layout.addWidget(self.last_time_high)
        self.last_time_low = QLabel(last_time_low)
        layout.addWidget(self.last_time_low)

        if not heading:
            self.del_button = NERButton("Delete", NERButton.Styles.RED)
            self.del_button.pressed.connect(self.delete)
            layout.addWidget(self.del_button)
        else:
            layout.addWidget(QLabel("Remove Fault"))

        self.setLayout(layout)
        

    def delete(self):
        self.parent().parent().parent().parent().remove_fault(self)

class ErrorView(QWidget):
    """
    View for monitoring of common failure messages.
    """

    def __init__(self, parent: QWidget):
        super(ErrorView, self).__init__(parent)
        
        layout = QVBoxLayout()
        toolbar = QToolBar()

        self.setStyleSheet("background-color: white; padding: 5%")
        add_fault = NERButton("Add Fault", NERButton.Styles.RED)
        add_fault.addStyle("margin-right: 5%")
        add_fault.pressed.connect(self.add_new_fault)
        toolbar.addWidget(add_fault)
        layout.addWidget(toolbar)

        self.scroll = QScrollArea()
        
        self.faults = QVBoxLayout()

        self.fault_headings = FaultEntry(self, "Fault", "Current Val", "Last Time High", "Last Time Low", 800, heading=True)
        self.faults.addWidget(self.fault_headings)

        self.fault_entries = QVBoxLayout()
        self.fault_entries_widget = QWidget()
        self.fault_entries_widget.setLayout(self.fault_entries)
        
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.fault_entries_widget)

        self.faults.addWidget(self.scroll)

        layout.addLayout(self.faults)

        self.setLayout(layout)

    def add_new_fault(self):
        self.fault_headings.setFixedWidth(self.width())
        self.fault_entries.addWidget(
            FaultEntry(self, "test", "123", "some time", "another time", self.width())
        )

    def remove_fault(self, fault: QWidget):
        self.fault_entries.removeWidget(fault)
        fault.deleteLater()