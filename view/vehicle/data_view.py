from enum import Enum
from PyQt6.QtWidgets import (
    QLabel, QHBoxLayout, QVBoxLayout, 
    QWidget, QPushButton, QGraphicsScene, 
    QComboBox, QToolBar, QDialog,
    QGridLayout, QDialogButtonBox, QSplitter
)
from PyQt6.QtCharts import QLineSeries, QChart, QChartView, QVXYModelMapper
from PyQt6.QtGui import QPainter, QTransform
from PyQt6.QtCore import QRectF, QSize, Qt

from model.data_models import DataModel


class EditDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self._data_list = ["None", "data 1", "data 2", "data 3"]
        self._format_list = ["Line Graph"]

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
        format = self.format_entry.currentText()
        print("Editing graph: ")
        print("  data 1 -> ", data1)
        print("  data 2 -> ", data2)
        print("  data 3 -> ", data3)
        print("  format -> ", format)
        self.accept()


class Formats(Enum):
    LINE = 1


class GraphWidget(QWidget):
    def __init__(self, index, format=Formats.LINE):
        super(GraphWidget, self).__init__()
        self.index = index

        # Tool Bar Config
        self.setMinimumSize(QSize(300, 200))
        toolbar = QToolBar()
        config_button = QPushButton("Edit")
        config_button.setStyleSheet("color: white; background-color: #FF5656")
        config_button.pressed.connect(self.edit)
        start_button = QPushButton("Start")
        start_button.pressed.connect(self.start)
        start_button.setStyleSheet("color: white; background-color: #07D807")
        record_button = QPushButton("Record")
        record_button.pressed.connect(self.record)
        record_button.setStyleSheet("color: white; background-color: #0977E6")
        toolbar.addWidget(config_button)
        toolbar.addWidget(start_button)
        toolbar.addWidget(record_button)

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
        self.add_series("Accel X", "Line 1")
        
        # Layout Config
        layout = QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(chart_view)
        self.setLayout(layout)


    def edit(self):
        dlg = EditDialog(self)
        dlg.exec()
        print("Edited graph")

    def start(self):
        pass

    def record(self):
        pass

    def add_series(self, data_type, series_name):
        model = DataModel() # TODO: select based on data type
        series = QLineSeries()
        series.setName(series_name)
        mapper = QVXYModelMapper(self)
        mapper.setXColumn(0)
        mapper.setYColumn(1)
        mapper.setSeries(series)
        mapper.setModel(model)
        self.chart.addSeries(series)
        self.chart.createDefaultAxes()



class DataView(QWidget):
    def __init__(self):
        super(DataView, self).__init__()
        self.data_list = ["data 1", "data 2", "data 3"]
        self.format_list = ["format 1", "format 2", "format 3"]

        self.setStyleSheet("QSplitter { background-color: #f0f0f0} QSplitterHandle { background-color: #999999 }")

        g1 = GraphWidget(1)
        g2 = GraphWidget(2)
        self.row1 = QSplitter()
        self.row1.addWidget(g1)
        self.row1.addWidget(g2)

        g3 = GraphWidget(3)
        g4 = GraphWidget(4)
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
