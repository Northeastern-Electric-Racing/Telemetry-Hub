from PyQt6.QtWidgets import (
      QWidget, QHBoxLayout, QVBoxLayout, QLabel, QCheckBox, QLineEdit, QGridLayout, QMessageBox)
from ner_telhub.descriptions import SD_OPTIONS_DESC
from ner_telhub.model.data_models import DataModelManager
from ner_telhub.view.sd_card.database_dialog import DatabaseDialog
from ner_telhub.view.sd_card.export_dialog import ExportDialog
from ner_telhub.view.sd_card.graph_dialog import GraphDialog
from ner_telhub.widgets.styled_widgets.ner_button import NERButton
from ner_telhub.widgets.styled_widgets.ner_info_button import NERInfoButton
from ner_telhub.widgets.styled_widgets.ner_loading_spinner import NERLoadingSpinner
from PyQt6.QtCore import Qt

class OptionsView(QWidget):
    """Menu for actions on the data processed from the SD log files."""

    def __init__(self, parent: QWidget, data_model: DataModelManager):
        super(OptionsView, self).__init__(parent)

        self.data_model = data_model
        self.data_model.layoutChanged.connect(self.modelUpdated)

        header = QHBoxLayout()
        header_label = QLabel("Data Options")
        header_label.setStyleSheet("font-size: 24px; font-weight: 600")
        header_info = NERInfoButton(SD_OPTIONS_DESC)
        header.addStretch()
        header.addWidget(header_label)
        header.addWidget(header_info)
        header.addStretch()

        # Setup layouts
        layout1: QVBoxLayout = self.generateLayout("Current Data")
        layout2: QVBoxLayout = self.generateLayout("Filters")
        layout3: QVBoxLayout = self.generateLayout("Export")

        # Populate layout 1
        self.model_info = QLabel("0 data points")
        self.clear_button = NERButton("Clear", NERButton.Styles.RED)
        self.clear_button.pressed.connect(self.clearModel)
        self.clear_button.setToolTip("Delete all data in the application")
        layout1.addWidget(self.model_info)
        layout1.addWidget(self.clear_button)

        # Populate layout 2
        self.id_input = QLineEdit()
        self.id_input.setToolTip("Space separated list of data IDs.")
        self.filter_method = QCheckBox()
        self.filter_method.setToolTip(
            "Whether to keep or delete the specified IDs")
        self.is_method_keep = True
        self.filter_method.setChecked(self.is_method_keep)
        self.setFilterMethod(self.is_method_keep)
        self.filter_method.stateChanged.connect(self.setFilterMethod)
        filter_layout = QGridLayout()
        filter_layout.addWidget(QLabel("IDs:"), 0, 0)
        filter_layout.addWidget(self.id_input, 0, 1)
        filter_layout.addWidget(QLabel("Filter Method:"), 1, 0)
        filter_layout.addWidget(self.filter_method, 1, 1)
        self.filter_button = NERButton("Filter", NERButton.Styles.BLUE)
        self.filter_button.pressed.connect(self.applyFilters)
        self.filter_button.setToolTip("Start the filter")
        layout2.addLayout(filter_layout)
        layout2.addWidget(self.filter_button)

        # Populate layout 3
        self.graph_button = NERButton("Graph", NERButton.Styles.BLUE)
        self.graph_button.setFixedWidth(150)
        self.graph_button.setToolTip(
            "Open a graph dashboard with the loaded data")
        self.graph_button.pressed.connect(
            lambda: GraphDialog(
                self, self.data_model).exec())
        self.csv_button = NERButton("CSV", NERButton.Styles.BLUE)
        self.csv_button.setFixedWidth(150)
        self.csv_button.setToolTip("Export the data to a CSV file")
        self.csv_spinner = NERLoadingSpinner()
        self.csv_button.pressed.connect(lambda: ExportDialog(
            self, self.data_model, self.csv_spinner).exec())
        csv_layout = QHBoxLayout()
        csv_layout.addWidget(self.csv_button)
        csv_layout.addWidget(self.csv_spinner)
        self.database_button = NERButton("Database", NERButton.Styles.BLUE)
        self.database_button.setFixedWidth(150)
        self.database_button.setToolTip("Export the data to the database")
        self.database_spinner = NERLoadingSpinner()
        self.database_button.pressed.connect(lambda: DatabaseDialog(
            self, self.data_model, self.database_spinner).exec())
        database_layout = QHBoxLayout()
        database_layout.addWidget(self.database_button)
        database_layout.addWidget(self.database_spinner)
        layout3.addWidget(self.graph_button)
        layout3.addLayout(csv_layout)
        layout3.addLayout(database_layout)

        # Populate main layout
        sub_layout = QHBoxLayout()
        sub_layout.addStretch()
        sub_layout.addLayout(layout1)
        sub_layout.addStretch()
        sub_layout.addLayout(layout2)
        sub_layout.addStretch()
        sub_layout.addLayout(layout3)
        sub_layout.addStretch()
        main_layout = QVBoxLayout()
        main_layout.addLayout(header)
        main_layout.addLayout(sub_layout)
        self.setLayout(main_layout)

    def modelUpdated(self):
        self.model_info.setText(
            f"{self.data_model.getDataCount()} data points")

    def generateLayout(self, label: str):
        layout = QVBoxLayout()
        layout_label = QLabel(label)
        layout_label.setStyleSheet("font-size: 16px; font-weight: 400")
        layout_label.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        layout.addWidget(layout_label)
        return layout

    def clearModel(self):
        self.data_model.deleteAllData()
        self.modelUpdated()

    def setFilterMethod(self, checked):
        self.is_method_keep = checked
        if self.is_method_keep:
            self.filter_method.setText("(keep ids)")
        else:
            self.filter_method.setText("(remove ids)")

    def applyFilters(self):
        try:
            filter_list = [int(id) for id in self.id_input.text().split(" ")]
        except BaseException:
            QMessageBox.critical(
                self,
                "ID Format Error",
                "Expecting a list of IDs seperated by spaces.")
            return

        self.data_model.filter(filter_list, self.is_method_keep)
