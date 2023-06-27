from typing import Callable
from PyQt6.QtWidgets import (
      QDialog, QVBoxLayout, QDialogButtonBox, QWidget, QComboBox, QLabel, QRadioButton
)
from ner_live.live_input import InputType, LiveInput

class ConnectionDialog(QDialog):
    """
    Connection dialog showing serial port connection information.
    """

    def __init__(self, parent: QWidget, callback: Callable):
        super().__init__(parent)

        self.setWindowTitle("Wireless Connection")
        self.callback = callback
        self.layout = QVBoxLayout()

        self.layout.addWidget(QLabel("Choose from the available ports:"))
        self.ports = LiveInput.serialPorts()
        if len(self.ports) == 0:
            self.layout.addWidget(QLabel("No connections found"))
        self.com_options = []
        for i in range(len(self.ports)):
            self.com_options.append(
                QRadioButton(f"{self.ports[i][0]} - {self.ports[i][1]}"))
            self.layout.addWidget(self.com_options[i])

        self.layout.addWidget(QLabel("Choose an input source:"))
        self.input_entry = QComboBox()
        self.input_entry.addItems([it.name for it in InputType])
        self.layout.addWidget(self.input_entry)

        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttonBox.accepted.connect(self.onAccept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def onAccept(self):
        for i in range(len(self.com_options)):
            if self.com_options[i].isChecked():
                self.accept()
                self.callback(self.ports[i][0],
                              InputType[self.input_entry.currentText()])
                return
            self.reject()
