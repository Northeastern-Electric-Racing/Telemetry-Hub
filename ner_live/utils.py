from ner_live.candapter import Candapter
from ner_live.live_input import LiveInput, InputType
from ner_live.xbee import XBee
from ner_telhub.model.message_models import MessageModel


def createConnection(
        input_type: InputType,
        message_model: MessageModel) -> LiveInput:
    """
    Create a live input of the given type.
    """
    if LiveInput.instance is None:
        if input_type is InputType.XBEE:
            LiveInput.instance = XBee(message_model)
        elif input_type is InputType.CANDAPTER:
            LiveInput.instance = Candapter(message_model)
        else:
            raise ValueError("Invalid live input type")
    return LiveInput.instance


def getConnection() -> LiveInput:
    """
    Gets the live input instance.
    """
    return LiveInput.instance


def deleteConnection() -> None:
    """
    Deletes the live instance object. Make sure to stop the connection before doing this.
    """
    LiveInput.instance = None
