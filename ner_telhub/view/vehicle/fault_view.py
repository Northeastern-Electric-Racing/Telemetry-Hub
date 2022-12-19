from PyQt6.QtWidgets import (
    QWidget, 
    QHBoxLayout, 
    QVBoxLayout, 
    QLabel
)

from ner_telhub.model.message_models import MessageModel

class FaultWidget(QWidget):
    def __init__(self):
        super().__init__()

class FaultView(QWidget):
    """
    View for debugging faults from the car
    """

    BMS_FAULT_IDS = {

    }

    MC_FAULT_IDS = {

    }

    CONTROL_FAULT_IDS = {

    }

    TELEMETRY_FAULT_IDS = {

    }

    DRIVERIO_FAULT_IDS = {

    }

    def __init__(self, parent: QWidget, model: MessageModel):
        super(FaultView, self).__init__(parent)
        layout = QVBoxLayout()

        mc_fault = FaultWidget()
        bms_fault = FaultWidget()
        tractive_fault_layout = QHBoxLayout()
        tractive_fault_layout.addWidget(QLabel("Tractive Faults:"))
        tractive_fault_layout.addWidget(mc_fault)
        tractive_fault_layout.addWidget(bms_fault)

        controls_fault = FaultWidget()
        telemetry_fault = FaultWidget()
        driverio_fault = FaultWidget()
        lv_fault_layout = QHBoxLayout()
        tractive_fault_layout.addWidget(QLabel("Low Voltage Faults:"))
        lv_fault_layout.addWidget(controls_fault)
        lv_fault_layout.addWidget(telemetry_fault)
        lv_fault_layout.addWidget(driverio_fault)

        layout.addLayout(tractive_fault_layout)
        layout.addLayout(lv_fault_layout)

        self._model = model

        self.setLayout(layout)