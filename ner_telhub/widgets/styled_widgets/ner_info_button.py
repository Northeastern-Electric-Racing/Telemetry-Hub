from PyQt6.QtWidgets import QMessageBox
from ner_telhub.widgets.styled_widgets.ner_button import NERButton
from ner_telhub.widgets.styled_widgets.ner_image_button import NERImageButton


class NERInfoButton(NERImageButton):
    """
    Info button that opens a popup window with a description
    """

    def __init__(self, text: str):
        super(
            NERInfoButton,
            self).__init__(
            NERImageButton.Icons.INFO,
            NERButton.Styles.BLUE)
        self.setFixedSize(20, 20)
        self.pressed.connect(
            lambda: QMessageBox.information(
                self, "Information", text))
