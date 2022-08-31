from enum import Enum
from typing import Callable

from PyQt6.QtWidgets import (
    QLabel, QVBoxLayout, 
    QWidget, QPushButton, 
    QComboBox, QToolBar, QDialog,
    QGridLayout, QDialogButtonBox,
    QSplitter
)
from PyQt6.QtCharts import (
    QLineSeries, QChart, QChartView, 
    QVXYModelMapper
)
from PyQt6.QtGui import QPainter
from PyQt6.QtCore import QSize, Qt

from ner_telhub.model.data_models import DataModel
from ner_processing.master_mapping import DATA_IDS


class Format(Enum):
    LINE = 1
    VALUE = 2


class EditDialog(QDialog):
    def __init__(self, parent: QWidget, callback: Callable):
        super().__init__(parent)
        self._data_list = ["None", *[DATA_IDS[d] for d in DATA_IDS]]
        self._format_list = [f.name for f in Format]
        self.callback = callback

        self.setWindowTitle("Edit Graph")

        self.data_entry_1 = QComboBox()
        self.data_entry_2 = QComboBox()
        self.data_entry_3 = QComboBox()
        self.format_entry = QComboBox()
        self.data_entry_1.addItems(self._data_list)
        self.data_entry_2.addItems(self._data_list)
        self.data_entry_3.addItems(self._data_list)
        self.format_entry.addItems(self._format_list)

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
    
    def on_accept(self):
        data1 = self.data_entry_1.currentText()
        data2 = self.data_entry_2.currentText()
        data3 = self.data_entry_3.currentText()
        format = Format[self.format_entry.currentText()]
        self.callback((data1, data2, data3, format))
        self.accept()


class GraphWidget(QWidget):
    def __init__(self, index, model: DataModel, format=Format.LINE):
        super(GraphWidget, self).__init__()
        self.index = index
        self.model = model

        # Tool Bar Config
        self.setMinimumSize(QSize(300, 200))
        toolbar = QToolBar()
        config_button = QPushButton("Edit")
        config_button.setStyleSheet("color: white; background-color: #FF5656")
        config_button.pressed.connect(lambda: EditDialog(self, self.edit_callback).exec())
        toolbar.addWidget(config_button)

        # Chart Config
        self.chart = QChart()
        self.chart.legend().hide()
        self.chart.createDefaultAxes()
        self.chart.setTitle(f"Graph {index}")
        self.chart.setTheme(QChart.ChartTheme.ChartThemeLight)
        self.chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

        # View Config
        chart_view = QChartView(self.chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        chart_view.setStyleSheet("background-color: #f0f0f0")

        # Model Config
        self.add_series("Accel X")

        # Layout Config
        layout = QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(chart_view)
        self.setLayout(layout)

    def edit_callback(self, graph_descriptor):
        try:
            data1 = graph_descriptor[0]
            data2 = graph_descriptor[1]
            data3 = graph_descriptor[2]
            format = graph_descriptor[3]
        except:
            print("error with args in add_series")
            return
        print("Received edit callback")

    def add_series(self, name):
        series = QLineSeries()
        series.setName(name)
        mapper = QVXYModelMapper(self)
        mapper.setXColumn(0)
        mapper.setYColumn(1)
        mapper.setSeries(series)
        mapper.setModel(DataModel()) # TODO: Change to be actual model
        self.chart.addSeries(series)
        self.chart.createDefaultAxes()


class GraphDashboardWidget(QWidget):
    def __init__(self, model: DataModel):
        super(GraphDashboardWidget, self).__init__()
        self.data_list = ["data 1", "data 2", "data 3"]
        self.format_list = ["format 1", "format 2", "format 3"]

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