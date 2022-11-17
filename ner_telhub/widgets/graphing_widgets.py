from enum import Enum
from typing import Callable

from PyQt6.QtWidgets import (
    QLabel, QVBoxLayout, 
    QWidget, QComboBox, QToolBar,
    QDialog, QGridLayout,
    QDialogButtonBox, QSplitter,
    QTableView, QMessageBox, 
    QSizePolicy
)
from PyQt6.QtCharts import (
    QLineSeries, QChart, QChartView, 
    QVXYModelMapper, QDateTimeAxis,
    QValueAxis
)
from PyQt6.QtGui import QPainter
from PyQt6.QtCore import QSize, Qt, QTimer, QDateTime

from ner_telhub.model.data_models import DataModelManager, DataModel
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

        # Check to make sure we're not adding the same data series twice
        if (data1 is not None and data1 == data2) or \
                (data1 is not None and data1 == data3) or \
                (data2 is not None and data2 == data3):
            QMessageBox.critical(self, "Input Error", "Each data value should be unique")
            return

        format = Format[self.format_entry.currentText()]
        state = GraphState(data1, data2, data3, format)
        self.callback(state)
        self.accept()



class GraphWidget(QWidget):
    """
    Main graph widget for displaying data in charts.
    """

    def __init__(self, parent: QWidget, index: int, model: DataModelManager, dynamic=False, format=Format.LINE):
        """
        Initializes the chart and toolbar. To differentiate between live and static dashboards,
        use the the dynamic variable.
        """
        super(GraphWidget, self).__init__(parent)
        self.index = index
        self.model = model
        self.state = GraphState(format=format)
        self.xRange = None
        self.yRange = None
        if dynamic:
            self.timer = QTimer()
            self.timer.timeout.connect(self.updateChart)

        self.setMinimumSize(QSize(300, 200))

        # Tool Bar Config
        toolbar = QToolBar()
        config_button = NERButton("Edit", NERButton.Styles.GREEN)
        config_button.addStyle("margin-right: 5%")
        config_button.pressed.connect(lambda: EditDialog(self, self.editCallback, self.model, self.state).exec())
        toolbar.addWidget(config_button)
        reset_button = NERButton("Reset", NERButton.Styles.RED)
        reset_button.addStyle("margin-right: 5%")
        reset_button.pressed.connect(self.reset)
        toolbar.addWidget(reset_button)
        show_button = NERButton("Data", NERButton.Styles.BLUE)
        show_button.addStyle("margin-right: 5%")
        show_button.pressed.connect(self.showTables)
        toolbar.addWidget(show_button)

        if dynamic:
            spacer = QWidget()
            spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            toolbar.addWidget(spacer)
            refresh_button = NERButton("Refresh", NERButton.Styles.GREEN)
            refresh_button.addStyle("margin-right: 5%")
            refresh_button.pressed.connect(self.updateChart)
            toolbar.addWidget(refresh_button)
            clear_button = NERButton("Clear", NERButton.Styles.BLUE)
            clear_button.addStyle("margin-right: 5%")
            clear_button.pressed.connect(self.clearData)
            toolbar.addWidget(clear_button)
            self.live_data = False
            self.live_button = NERButton("Start", NERButton.Styles.GREEN)
            self.live_button.addStyle("margin-right: 5%")
            self.live_button.pressed.connect(self.toggleLiveData)
            toolbar.addWidget(self.live_button)

        # Chart Config
        self.chart = QChart()
        self.chart.setTitle(f"Graph {index}")
        self.chart.setTheme(QChart.ChartTheme.ChartThemeLight)
        self.chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

        # Axis Config
        self.axisX = QDateTimeAxis()
        self.axisX.setTickCount(5)
        self.axisX.setFormat("hh:mm:ss.z")
        self.axisX.setTitleText("Time")

        self.axisY = QValueAxis()
        self.axisY.setTickCount(5)
        self.axisY.setLabelFormat("%i")
        self.axisY.setTitleText("Data")

        # View Config
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.chart_view.setStyleSheet("background-color: #f0f0f0")

        # Layout Config
        layout = QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.chart_view)
        self.setLayout(layout)

    def editCallback(self, newState: GraphState):
        """
        Handles a changed state from the edit dialog box.
        """
        if self.state.format != newState.format:
            pass # In the future, change graph type

        if self.state.data1 != newState.data1:
            if self.state.data1 is not None:
                self.removeSeries(self.model.getDataType(self.state.data1))
            if newState.data1 is not None:
                self.addSeries(self.model.getDataType(newState.data1), newState.data1)

        if self.state.data2 != newState.data2:
            if self.state.data2 is not None:
                self.removeSeries(self.model.getDataType(self.state.data2))
            if newState.data2 is not None:
                self.addSeries(self.model.getDataType(newState.data2), newState.data2)

        if self.state.data3 != newState.data3:
            if self.state.data3 is not None:
                self.removeSeries(self.model.getDataType(self.state.data3))
            if newState.data3 is not None:
                self.addSeries(self.model.getDataType(newState.data3), newState.data3)

        self.state = newState

    def reset(self):
        """
        Resets the graph.
        """
        for axis in self.chart.axes():
            self.chart.removeAxis(axis)
        self.chart.removeAllSeries()
        self.state = GraphState()

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

    def updateChart(self):
        """
        Updates the axis of the chart by finding the max/min 
        """
        if self.state.data1 is not None:
            self.updateAxis(self.model.getDataModel(self.state.data1).getMinTime(), self.model.getDataModel(self.state.data1).getMaxTime(), \
                            self.model.getDataModel(self.state.data1).getMinValue(), self.model.getDataModel(self.state.data1).getMaxValue())
        if self.state.data2 is not None:
            self.updateAxis(self.model.getDataModel(self.state.data2).getMinTime(), self.model.getDataModel(self.state.data2).getMaxTime(), \
                            self.model.getDataModel(self.state.data2).getMinValue(), self.model.getDataModel(self.state.data2).getMaxValue())
        if self.state.data3 is not None:
            self.updateAxis(self.model.getDataModel(self.state.data3).getMinTime(), self.model.getDataModel(self.state.data3).getMaxTime(), \
                            self.model.getDataModel(self.state.data3).getMinValue(), self.model.getDataModel(self.state.data3).getMaxValue())
        self.chart_view.update()
    
    def clearData(self):
        """
        Clears the graph's data from the model.
        """
        if self.state.data1 is not None:
            self.model.getDataModel(self.state.data1).deleteAllData()
        if self.state.data2 is not None:
            self.model.getDataModel(self.state.data2).deleteAllData()
        if self.state.data3 is not None:
            self.model.getDataModel(self.state.data3).deleteAllData()
    
    def toggleLiveData(self):
        """
        Alters the 
        """
        if self.live_data:
            self.live_button.setText("Start")
            self.live_button.changeStyle(NERButton.Styles.GREEN)
            self.live_button.addStyle("margin-right: 5%")
            self.timer.stop()
        else:
            self.live_button.setText("Stop")
            self.live_button.changeStyle(NERButton.Styles.RED)
            self.live_button.addStyle("margin-right: 5%")
            self.timer.start(1000)
        self.live_data = not self.live_data

    def addSeries(self, name: str, data_id: int):
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
        # Configure axes
        self.updateAxis(self.model.getDataModel(data_id).getMinTime(), self.model.getDataModel(data_id).getMaxTime(), \
                        self.model.getDataModel(data_id).getMinValue(), self.model.getDataModel(data_id).getMaxValue())
        self.chart.addAxis(self.axisX, Qt.AlignmentFlag.AlignBottom)
        self.chart.addAxis(self.axisY, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(self.axisX)
        series.attachAxis(self.axisY)

    def removeSeries(self, name: str):
        """
        Removes the data series specified by the given name from the chart.
        """
        try:
            for series in self.chart.series():
                if series.name() == name:
                    self.chart.removeSeries(series)
        except:
            pass

    def updateAxis(self, xmin: QDateTime, xmax: QDateTime, ymin: int, ymax: int):
        """
        Updates the axis to use the new data values if they expand the bounds of the graph.
        """
        if self.xRange is None:
            self.xRange = [xmin, xmax]
        else:
            if xmin < self.xRange[0]:
                self.xRange[0] = xmin
            if xmax > self.xRange[1]:
                self.xRange[1] = xmax
                
        if self.yRange is None:
            self.yRange = [ymin, ymax]
        else:
            if ymin < self.yRange[0]:
                self.yRange[0] = ymin
            if ymax > self.yRange[1]:
                self.yRange[1] = ymax

        self.axisX.setRange(self.xRange[0], self.xRange[1])
        self.axisY.setRange(self.yRange[0], self.yRange[1])



class GraphDashboardWidget(QWidget):
    """
    Top level widget holding a set of graphs.

    This is the widget to embed in other views to get a dashboard.
    """
    
    def __init__(self, parent: QWidget, model: DataModelManager, dynamic=False):
        """
        Creates a graph dashboard with the given model. If dynamic is true, this dashboard will 
        support real time plotting.
        """
        super(GraphDashboardWidget, self).__init__(parent)
        self.setStyleSheet("""QSplitter { background-color: #f0f0f0} 
            QSplitterHandle { background-color: #999999 }""")

        g1 = GraphWidget(self, 1, model, dynamic)
        g2 = GraphWidget(self, 2, model, dynamic)
        self.row1 = QSplitter()
        self.row1.addWidget(g1)
        self.row1.addWidget(g2)

        g3 = GraphWidget(self, 3, model, dynamic)
        g4 = GraphWidget(self, 4, model, dynamic)
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