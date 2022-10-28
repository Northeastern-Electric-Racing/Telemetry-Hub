from asyncio.windows_events import NULL
from enum import Enum
from typing import Callable

from PyQt6.QtWidgets import (
    QLabel, QVBoxLayout, 
    QWidget, QComboBox, QToolBar,
    QDialog, QGridLayout,
    QDialogButtonBox, QSplitter,
    QTableView
)
from PyQt6.QtCharts import (
    QLineSeries, QChart, QChartView, 
    QVXYModelMapper, QValueAxis
)
from PyQt6.QtGui import QPainter
from PyQt6.QtCore import QSize, Qt
from ner_telhub.model.data_models import DataModelManager, DataModel
from ner_processing.master_mapping import DATA_IDS
from ner_telhub.widgets.styled_widgets import NERButton


class Format(Enum):
    """
    Specifies available graph formats.
    """
    LINE = 1


class GraphState():
    """
    Data class holding the current state of a graph.
    """
    def __init__(self, data1: int = None, data2: int = None, data3: int = None, format: Format = Format.LINE):
        self.data1 = data1
        self.data2 = data2
        self.data3 = data3
        self.format = format



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



class EditDialog(QDialog):
    """
    Edit dialog window allowing the user to change graph state.
    """

    def __init__(self, parent: QWidget, callback: Callable, model: DataModelManager, state: GraphState):
        super(EditDialog, self).__init__(parent)
        self.callback = callback
        self.model = model
        self._data_list = ["None", *[self.dataToText(d) for d in model.getAvailableIds()]]
        self._format_list = [f.name for f in Format]

        self.setWindowTitle("Edit Graph")

        self.data_entry_1 = QComboBox()
        self.data_entry_2 = QComboBox()
        self.data_entry_3 = QComboBox()
        self.format_entry = QComboBox()
        self.data_entry_1.addItems(self._data_list)
        self.data_entry_2.addItems(self._data_list)
        self.data_entry_3.addItems(self._data_list)
        self.format_entry.addItems(self._format_list)
        self.data_entry_1.setCurrentText(self.dataToText(state.data1))
        self.data_entry_2.setCurrentText(self.dataToText(state.data2))
        self.data_entry_3.setCurrentText(self.dataToText(state.data3))
        self.format_entry.setCurrentText(state.format.name)

        layout = QGridLayout()
        layout.addWidget(QLabel("Data 1:"), 0, 0)
        layout.addWidget(self.data_entry_1, 0, 1)
        layout.addWidget(QLabel("Data 2:"), 1, 0)
        layout.addWidget(self.data_entry_2, 1, 1)
        layout.addWidget(QLabel("Data 3:"), 2, 0)
        layout.addWidget(self.data_entry_3, 2, 1)
        layout.addWidget(QLabel("Format:"), 3, 0)
        layout.addWidget(self.format_entry, 3, 1)

        buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttonBox.accepted.connect(self.on_accept)
        buttonBox.rejected.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addWidget(buttonBox)
        self.setLayout(main_layout)

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
        except:
            return None

    def on_accept(self):
        """
        Actions to perform when the window OK button is pressed.
        """
        data1 = self.textToData(self.data_entry_1.currentText())
        data2 = self.textToData(self.data_entry_2.currentText())
        data3 = self.textToData(self.data_entry_3.currentText())
        format = Format[self.format_entry.currentText()]
        state = GraphState(data1, data2, data3, format)
        self.callback(state)
        self.accept()



class GraphWidget(QWidget):
    """
    Main graph widget for displaying data in charts.
    """

    def __init__(self, index, model: DataModelManager, format=Format.LINE):
        """
        Initializes the chart and toolbar.
        """
        super(GraphWidget, self).__init__()
        self.index = index
        self.model = model
        self.state = GraphState(format=format)

        # Tool Bar Config
        self.setMinimumSize(QSize(300, 200))
        toolbar = QToolBar()
        config_button = NERButton("Edit", NERButton.Styles.GREEN)
        config_button.addStyle("margin-right: 5%")
        config_button.pressed.connect(lambda: EditDialog(self, self.edit_callback, self.model, self.state).exec())
        reset_button = NERButton("Reset", NERButton.Styles.RED)
        reset_button.addStyle("margin-right: 5%")
        reset_button.pressed.connect(self.reset)
        show_button = NERButton("Data", NERButton.Styles.BLUE)
        show_button.addStyle("margin-right: 5%")
        show_button.pressed.connect(self.showTables)
        toolbar.addWidget(config_button)
        toolbar.addWidget(reset_button)
        toolbar.addWidget(show_button)

        # Chart Config
        self.chart = QChart()
        self.chart.setTitle(f"Graph {index}")
        self.chart.setTheme(QChart.ChartTheme.ChartThemeLight)
        self.chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

        # View Config
        chart_view = QChartView(self.chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        chart_view.setStyleSheet("background-color: #f0f0f0")

        # Layout Config
        layout = QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(chart_view)
        self.setLayout(layout)

    def edit_callback(self, state: GraphState):
        """
        Handles a changed state from the edit dialog box.
        """
        if self.state.format != state.format:
            pass # In the future, change graph type
        if self.state.data1 != state.data1:
            if self.state.data1 != None:
                self.remove_series(self.model.getDataType(self.state.data1))
            self.add_series(self.model.getDataType(state.data1), state.data1)
        if self.state.data2 != state.data2:
            if self.state.data2 != None:
                self.remove_series(self.model.getDataType(self.state.data2))
            self.add_series(self.model.getDataType(state.data2), state.data2)
        if self.state.data3 != state.data3:
            if self.state.data3 != None:
                self.remove_series(self.model.getDataType(self.state.data3))
            self.add_series(self.model.getDataType(state.data3), state.data3)
        self.state = state

    def showTables(self):
        """
        Shows current data tables.
        """
        if self.state.data1 is not None:
            DataTable(self, self.model.getDataModel(self.state.data1)).show()
        if self.state.data2 is not None:
            DataTable(self, self.model.getDataModel(self.state.data2)).show()
        if self.state.data3 is not None:
            DataTable(self, self.model.getDataModel(self.state.data3)).show()

    def reset(self):
        """
        Resets the graph.
        """
        self.chart.removeAllSeries()
        self.state = GraphState()

    def add_series(self, name: str, data_id: int):
        """
        Adds a data series by the given name to the chart.
        """
        if data_id is None:
            return
        series = QLineSeries()
        series.setName(name)
        mapper = QVXYModelMapper(self)
        mapper.setXColumn(0)
        mapper.setYColumn(1)
        mapper.setSeries(series)
        mapper.setModel(self.model.getDataModel(data_id))
        self.chart.addSeries(series)
        self.chart.createDefaultAxes()

    def remove_series(self, name: str):
        """
        Removes the data series specified by the given name from the chart.
        """
        try:
            for series in self.chart.series():
                if series.name() == name:
                    self.chart.removeSeries(series)
        except:
            pass




class GraphDashboardWidget(QWidget):
    """
    Top level widget holding a set of graphs.

    This is the widget to embed in other views to get a dashboard.
    """
    
    def __init__(self, model: DataModelManager):
        super(GraphDashboardWidget, self).__init__()
        self.setStyleSheet("QSplitter { background-color: #f0f0f0} QSplitterHandle { background-color: #999999 }")

        g1 = GraphWidget(1, model)
        g2 = GraphWidget(2, model)
        self.row1 = QSplitter()
        self.row1.addWidget(g1)
        self.row1.addWidget(g2)

        g3 = GraphWidget(3, model)
        g4 = GraphWidget(4, model)
        self.row2 = QSplitter()
        self.row2.addWidget(g3)
        self.row2.addWidget(g4)

        self.graphs = QSplitter()
        self.graphs.setOrientation(Qt.Orientation.Vertical)
        self.graphs.addWidget(self.row1)
        self.graphs.addWidget(self.row2)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.graphs)
        self.setLayout(main_layout) 