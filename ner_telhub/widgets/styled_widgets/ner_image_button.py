from enum import Enum
import os

from ner_telhub.widgets.styled_widgets.ner_button import NERButton
from PyQt6.QtGui import QIcon

resources = os.path.dirname(__file__) + "../../../../resources"


class NERImageButton(NERButton):
    """
    Creates a button using an icon.
    """
    class Icons(Enum):
        """
        Defines file names for available icons.
        """
        EDIT = "edit_icon.png"
        EXPORT = "export_icon.png"
        REFRESH = "refresh_icon.png"
        START = "start_icon.png"
        STOP = "stop_icon.png"
        TRASH = "trash_icon.png"
        CLOSE = "close_icon.png"
        INFO = "info_icon.png"

    def __init__(self, icon_file: Icons, style=NERButton.Styles.DEFAULT):
        super().__init__("", style=style)
        self.resetIcon(icon_file)

    def resetIcon(self, icon_file: Icons):
        self.setIcon(QIcon(os.path.join(resources, icon_file.value)))

