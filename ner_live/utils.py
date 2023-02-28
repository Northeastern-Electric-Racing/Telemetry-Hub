from ner_live.candapter import Candapter
from ner_live.live_input import LiveInput, InputType
from ner_live.xbee import XBee
from ner_telhub.model.message_models import MessageModel


def getConnection(
        input_type: InputType,
        message_model: MessageModel) -> LiveInput:
    """
    Factory function to create a live input of the given type
    """
    if input_type is InputType.XBEE:
        return XBee(message_model)
    elif input_type is InputType.CANDAPTER:
        return Candapter(message_model)
    else:
        raise ValueError("Invalid live input type")
