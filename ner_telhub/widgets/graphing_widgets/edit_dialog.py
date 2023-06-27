from typing import Callable
from functools import partial
from PyQt6.QtWidgets import (
      QDialog, QDialogButtonBox, QGridLayout, QLabel, QLineEdit, QWidget, QVBoxLayout, QMessageBox, QCheckBox, QDateTimeEdit, QComboBox)
from ner_telhub.model.data_models import DataModelManager
from ner_telhub.widgets.graphing_widgets.format import Format
from ner_telhub.widgets.graphing_widgets.graph_state import GraphState
from ner_telhub.widgets.styled_widgets.styled_widgets import NERButton, NERImageButton

class EditDialog(QDialog):
    """
    Edit dialog window allowing the user to change graph state.
    """

    def __init__(
            self,
            parent: QWidget,
            callback: Callable,
            model: DataModelManager,
            state: GraphState,
            live: bool):
        super(EditDialog, self).__init__(parent)
        self.callback = callback
        self.model = model
        self._data_list = [
            "None", *[self.dataToText(d) for d in model.getAvailableIds()]]
        self._format_list = [f.name for f in Format]
        self.live = live

        self.setWindowTitle("Edit Graph")

        self.data_entry = []
        self.layout = QGridLayout()

        # Format combo box section
        self.format_entry = QComboBox()
        self.format_entry.addItems(self._format_list)
        self.format_entry.setCurrentText(state.format.name)
        self.layout.addWidget(QLabel("Format:"), 0, 0)
        self.layout.addWidget(self.format_entry, 0, 1, 1, 2)

        # Y-Axis section
        self.y_scale = QCheckBox()
        self.y_scale.pressed.connect(self.changeYScale)
        self.y_scale.setChecked(state.auto_y)
        self.ymin_entry = QLineEdit()
        self.ymax_entry = QLineEdit()
        if state.auto_y:
            self.ymin_entry.setEnabled(False)
            self.ymax_entry.setEnabled(False)
        if state.y_range is not None:
            self.ymin_entry.setText(str(state.y_range[0]))
            self.ymax_entry.setText(str(state.y_range[1]))
        self.layout.addWidget(QLabel("Auto scale y-axis:"), 1, 0)
        self.layout.addWidget(self.y_scale, 1, 1)
        self.layout.addWidget(QLabel("Min y-axis"), 2, 0)
        self.layout.addWidget(self.ymin_entry, 2, 1)
        self.layout.addWidget(QLabel("Max y-axis"), 3, 0)
        self.layout.addWidget(self.ymax_entry, 3, 1)

        # X-Axis section (only show on non-live plots)
        self.layout_index = 4 # Next index for rows in the layout
        if not live:
            self.x_scale = QCheckBox()
            self.x_scale.pressed.connect(self.changeXScale)
            self.x_scale.setChecked(state.auto_x)
            self.xmin_entry = QDateTimeEdit()
            self.xmax_entry = QDateTimeEdit()
            if state.auto_x:
                self.xmin_entry.setEnabled(False)
                self.xmax_entry.setEnabled(False)
            if state.x_range is not None:
                self.xmin_entry.setDateTime(state.x_range[0])
                self.xmax_entry.setDateTime(state.x_range[1])
            self.layout.addWidget(QLabel("Auto scale x-axis:"), 4, 0)
            self.layout.addWidget(self.x_scale, 4, 1)
            self.layout.addWidget(QLabel("Min x-axis"), 5, 0)
            self.layout.addWidget(self.xmin_entry, 5, 1)
            self.layout.addWidget(QLabel("Max x-axis"), 6, 0)
            self.layout.addWidget(self.xmax_entry, 6, 1)
            self.layout_index = 7

        # Data input sections
        add_button = NERButton("Add Data Input", NERButton.Styles.GRAY)
        add_button.setToolTip("Add an input to specify data")
        add_button.pressed.connect(self.add)
        self.layout.addWidget(add_button, self.layout_index, 0, 1, -1)
        self.layout_index += 1

        for data in state.data:
            combo_box = QComboBox()
            combo_box.addItems(self._data_list)
            combo_box.setCurrentText(self.dataToText(data))
            self.data_entry.append(combo_box)

            remove_button = NERImageButton(
                NERImageButton.Icons.TRASH, NERButton.Styles.RED)
            remove_button.pressed.connect(
                partial(
                    self.remove,
                    entry=combo_box,
                    button=remove_button))
            self.layout.addWidget(combo_box, self.layout_index, 0, 1, 2)
            self.layout.addWidget(remove_button, self.layout_index, 2)

            self.layout_index += 1

        buttonBox = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttonBox.accepted.connect(self.on_accept)
        buttonBox.rejected.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addLayout(self.layout)
        main_layout.addWidget(buttonBox)
        self.setLayout(main_layout)

    def changeYScale(self):
        use_yscale = self.y_scale.isChecked()
        self.ymin_entry.setEnabled(use_yscale)
        self.ymax_entry.setEnabled(use_yscale)

    def changeXScale(self):
        auto_xscale = self.x_scale.isChecked()
        self.xmin_entry.setEnabled(auto_xscale)
        self.xmax_entry.setEnabled(auto_xscale)

    def dataToText(self, data: int) -> str:
        """
        Converts a data id to the textual type of data recognizable by the user.
        """
        if data is not None:
            return f"{data}  {self.model.getDataType(data)}"
        else:
            return "None"

    def textToData(self, text: str) -> int:
        """
        Converts a textual data input to the data id.
        """
        try:
            return int(text.split(" ")[0])
        except BaseException:
            return None

    def on_accept(self):
        """
        Actions to perform when the window OK button is pressed.
        """
        data = []
        for entry in self.data_entry:
            ent = self.textToData(entry.currentText())

            if ent is None:
                QMessageBox.critical(
                    self, "Input Error", "Data values cannot be \"None\"")
                return

            data.append(ent)

        # Check to make sure we're not adding the same data series twice and
        # that all units match
        units = None
        for d in data:
            if d is not None and data.count(d) > 1:
                QMessageBox.critical(
                    self, "Input Error", "Each data value should be unique")
                return
            if units is None:
                units = self.model.getDataUnit(d)
            else:
                if units != self.model.getDataUnit(d):
                    QMessageBox.critical(
                        self, "Input Error", "Each data value should have matching units")
                    return

        auto_y = self.y_scale.isChecked()
        y_range = None
        if not auto_y:
            try:
                y_range = [float(self.ymin_entry.text()), float(self.ymax_entry.text())]
            except ValueError:
                QMessageBox.critical(
                    self, "Input Error", "Invalid y-axis arguments")
                return
        
        if not self.live:
            auto_x = self.x_scale.isChecked()
            x_range = None
            if not auto_x:
                try:
                    x_range = [self.xmin_entry.dateTime().toPyDateTime(), self.xmax_entry.dateTime().toPyDateTime()]
                except ValueError:
                    QMessageBox.critical(
                        self, "Input Error", "Invalid x-axis arguments")
                    return
        else:
            auto_x = True
            x_range = None

        format = Format[self.format_entry.currentText()]
        state = GraphState(data, format, auto_y, auto_x, y_range, x_range)
        self.callback(state)
        self.accept()

    def add(self):
        if len(self._data_list) == 1:
            QMessageBox.critical(
                self,
                "Error adding data",
                "There is no data to add")
            return

        combo_box = QComboBox()
        combo_box.addItems(self._data_list)
        self.data_entry.append(combo_box)

        remove_button = NERImageButton(
            NERImageButton.Icons.TRASH,
            NERButton.Styles.RED)
        remove_button.pressed.connect(
            partial(
                self.remove,
                entry=combo_box,
                button=remove_button))
        self.layout.addWidget(combo_box, self.layout_index, 0, 1, 2)
        self.layout.addWidget(remove_button, self.layout_index, 2)

        self.layout_index += 1

    def remove(self, entry: QComboBox, button: NERImageButton):
        self.data_entry.remove(entry)
        entry.close()
        button.close()
