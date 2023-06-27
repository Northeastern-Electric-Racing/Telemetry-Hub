from typing import Dict
from PyQt6.QtWidgets import (
    QMainWindow, QHBoxLayout,
    QVBoxLayout, QWidget, QMenu
)
from PyQt6.QtGui import QAction
from ner_telhub.model.file_models import FileModel
from ner_telhub.model.data_models import DataModelManager
from ner_processing.decode_files import LogFormat
from ner_telhub.view.sd_card.file_view import FileView
from ner_telhub.view.sd_card.options_view import OptionsView
from ner_telhub.view.sd_card.process_view import ProcessView
from PyQt6.QtCore import QSize
from ner_telhub.widgets.menu_widgets.data_ids import DataIds

from ner_telhub.widgets.menu_widgets.message_ids import MessageIds


class SdCardWindow(QMainWindow):
    """Main window in for the SD Card connection."""

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.setWindowTitle("Telemetry Hub")
        self.setMinimumSize(QSize(960, 720))

        self.file_model = FileModel(self)
        data_model = DataModelManager(self)

        # Setup window
        hlayout = QHBoxLayout()
        hlayout.addWidget(FileView(self, self.file_model))
        hlayout.addWidget(ProcessView(self, self.file_model, data_model))

        vlayout = QVBoxLayout()
        vlayout.addLayout(hlayout)
        vlayout.addWidget(OptionsView(self, data_model))

        widget = QWidget()
        widget.setLayout(vlayout)
        self.setCentralWidget(widget)

        # Setup menu bar
        menu = self.menuBar()
        edit_menu = menu.addMenu("Edit")
        help_menu = menu.addMenu("Help")

        format_submenu = QMenu("Format", self)
        format_submenu.setToolTip("Change the format of the log files")
        edit_menu.addMenu(format_submenu)

        self.options: Dict[int, QAction] = {}
        self.enabled_id = self.file_model.getFormat().value

        for format in LogFormat:
            act = QAction(format.name, self)
            format_submenu.addAction(act)
            act.setCheckable(True)
            act.triggered.connect(
                lambda state,
                id=format.value: self.formatClicked(
                    state,
                    id))
            self.options[format.value] = act

        self.options.get(self.enabled_id).setChecked(True)

        help_action_1 = help_menu.addAction("Message Info")
        help_action_2 = help_menu.addAction("Data Info")
        help_action_1.triggered.connect(lambda: MessageIds(self).show())
        help_action_2.triggered.connect(lambda: DataIds(self).show())

    def formatClicked(self, state: bool, id: int):
        """
        Callback for format menu options to verify one and always one format is selected at a time.
            - state is whether the format given by id should be checked or not
        """
        if not state:
            self.options.get(id).setChecked(True)
        else:
            self.options.get(self.enabled_id).setChecked(False)
            self.enabled_id = id
            self.file_model.setFormat(LogFormat(id))
