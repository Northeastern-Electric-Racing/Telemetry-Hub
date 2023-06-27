from PyQt6.QtWidgets import (
      QWidget, QVBoxLayout, QLabel, QGridLayout)
from PyQt6.QtCore import Qt, QTimer
from ner_live.utils import getConnection
from ner_telhub.model.data_models import DataModelManager
from ner_telhub.model.message_models import MessageModel

class LiveMonitoring(QWidget):
    """
    Portion of the UI that shows live input configuring and monitoring information.
    """

    def __init__(
            self,
            parent: QWidget,
            message_model: MessageModel,
            data_model: DataModelManager):
        super(LiveMonitoring, self).__init__(parent)

        self.setMinimumWidth(300)

        self.message_model = message_model
        self.data_model = data_model

        self.datacount_label = QLabel("0")
        self.biterror_label = QLabel("0")
        self.valueerror_label = QLabel("0")
        self.errorrate_label = QLabel("0.0 %")
        self.setStyleSheet("QLabel { font-size: 16px; }")

        label_layout = QGridLayout()
        label_layout.addWidget(QLabel("Data Count:"), 0, 0)
        label_layout.addWidget(self.datacount_label, 0, 1)
        label_layout.addWidget(QLabel("Bit Errors:"), 1, 0)
        label_layout.addWidget(self.biterror_label, 1, 1)
        label_layout.addWidget(QLabel("Value Errors:"), 2, 0)
        label_layout.addWidget(self.valueerror_label, 2, 1)
        label_layout.addWidget(QLabel("Error Rate:"), 3, 0)
        label_layout.addWidget(self.errorrate_label, 3, 1)

        header = QLabel("Connection Info")
        header.setStyleSheet("font-size: 30px; font-weight: bold")
        header.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        layout = QVBoxLayout()
        layout.addWidget(header)
        layout.addLayout(label_layout)
        layout.addSpacing(150)
        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.updateErrorCounts)
        self.timer.start(100)

    def updateErrorCounts(self):
        connection = getConnection()
        if connection is not None:
            error_count = connection.getErrorCount()
            success_count = connection.getSuccessCount()
            if error_count + success_count == 0:
                error_rate = 0.0
            else:
                error_rate = round(100 * error_count /
                                   (error_count + success_count), 2)
            self.biterror_label.setText(str(error_count))
            self.errorrate_label.setText(f"{error_rate} %")

        self.datacount_label.setText(str(self.data_model.getDataCount()))
        self.valueerror_label.setText(str(self.data_model.getErrorCount()))
