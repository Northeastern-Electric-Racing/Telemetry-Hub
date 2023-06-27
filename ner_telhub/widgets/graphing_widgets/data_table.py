from PyQt6.QtWidgets import QDialog, QTableView, QVBoxLayout, QWidget
from ner_telhub.model.data_models import DataModel

class DataTable(QDialog):
    """
    Shows information on data in the model in a tabular format.
    """

    def __init__(self, parent: QWidget, model: DataModel):
        super().__init__(parent)
        self.setWindowTitle(model.getDataType())

        view = QTableView(self)
        view.setModel(model)
        view.horizontalHeader().setSectionsClickable(False)
        view.verticalHeader().setSectionsClickable(False)
        view.resizeColumnsToContents()
        view.resizeRowsToContents()

        layout = QVBoxLayout()
        layout.addWidget(view)
        self.setLayout(layout)
