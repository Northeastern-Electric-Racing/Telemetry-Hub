from PyQt6.QtWidgets import (
    QWidget, 
    QHBoxLayout, 
    QVBoxLayout, 
    QLabel
)

from ner_telhub.model.filter_models import ReceiveFilterModel

class FaultWidget(QWidget):
    fault_ids : dict = None
    model : ReceiveFilterModel = None
    
    def __init__(self, fault_ids: dict, model: ReceiveFilterModel):
        super().__init__()
        self.fault_ids = fault_ids
        self.model = model

    def setFilters(self):
        for id in self.fault_ids:
            print(id)
            self.model.addFilter(id)

class FaultView(QWidget):
    """
    View for debugging faults from the car
    """

    BMS_FAULT_IDS = {
        0: ""
    }

    MC_FAULT_IDS = {
        0: ""
    }

    CONTROLS_FAULT_IDS = {
        0: ""
    }

    TELEMETRY_FAULT_IDS = {
        0: ""
    }

    DRIVERIO_FAULT_IDS = {
        0: ""
    }

    def __init__(self, parent: QWidget, model: ReceiveFilterModel):
        super(FaultView, self).__init__(parent)
        layout = QVBoxLayout()

        mc_fault = FaultWidget(fault_ids=self.MC_FAULT_IDS, model=model)
        bms_fault = FaultWidget(fault_ids=self.BMS_FAULT_IDS, model=model)
        tractive_fault_layout = QHBoxLayout()
        tractive_fault_layout.addWidget(QLabel("Tractive Faults:"))
        tractive_fault_layout.addWidget(mc_fault)
        tractive_fault_layout.addWidget(bms_fault)

        controls_fault = FaultWidget(fault_ids=self.CONTROLS_FAULT_IDS, model=model)
        telemetry_fault = FaultWidget(fault_ids=self.TELEMETRY_FAULT_IDS, model=model)
        driverio_fault = FaultWidget(fault_ids=self.DRIVERIO_FAULT_IDS, model=model)
        lv_fault_layout = QHBoxLayout()
        tractive_fault_layout.addWidget(QLabel("Low Voltage Faults:"))
        lv_fault_layout.addWidget(controls_fault)
        lv_fault_layout.addWidget(telemetry_fault)
        lv_fault_layout.addWidget(driverio_fault)

        layout.addLayout(tractive_fault_layout)
        layout.addLayout(lv_fault_layout)

        self._model = model

        self.setLayout(layout)