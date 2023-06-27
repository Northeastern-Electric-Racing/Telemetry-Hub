from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
from ner_telhub.model.filter_models import ReceiveFilterModel
from ner_telhub.model.data_models import DataModelManager
from ner_telhub.model.message_models import MessageModel
from ner_telhub.view.vehicle.can_view.live_monitoring import LiveMonitoring
from ner_telhub.view.vehicle.can_view.message_feed import MessageFeed
from ner_telhub.view.vehicle.can_view.receive_filters import ReceiveFilters

class CanView(QWidget):
    """
    Main CAN view class.
    """

    def __init__(self, parent: QWidget,
                 message_model: MessageModel,
                 data_model: DataModelManager,
                 receive_filter_model: ReceiveFilterModel):
        super(CanView, self).__init__(parent)

        sub_layout = QHBoxLayout()
        sub_layout.addWidget(
            LiveMonitoring(
                self,
                message_model,
                data_model))
        sub_layout.addWidget(MessageFeed(self, message_model))

        layout = QVBoxLayout()
        layout.addLayout(sub_layout)
        layout.addWidget(ReceiveFilters(self, receive_filter_model))
        self.setLayout(layout)
