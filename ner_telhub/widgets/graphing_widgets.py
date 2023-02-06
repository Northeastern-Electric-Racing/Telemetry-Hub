from abc import abstractmethod
from enum import Enum
from typing import Callable

from PyQt6.QtWidgets import (
    QLabel, QVBoxLayout,
    QWidget, QComboBox,
    QDialog, QGridLayout,
    QDialogButtonBox, QSplitter,
    QTableView, QMessageBox
)
from PyQt6.QtCharts import (
    QLineSeries, QChart, QChartView,
    QVXYModelMapper, QDateTimeAxis,
    QValueAxis
)
from PyQt6.QtGui import QPainter
from PyQt6.QtCore import QSize, Qt, QTimer, QDateTime

from ner_telhub.model.data_models import DataModelManager, DataModel
from ner_telhub.widgets.styled_widgets import NERButton, NERImageButton, NERToolbar


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


class GraphDashboard(QWidget):
    @abstractmethod
    def removeGraph(self, graph):
        pass


class GraphWidget(QWidget):
    """
    Main graph widget for displaying data in charts.
    """

    def __init__(self, parent: GraphDashboard, index: int, model: DataModelManager, dynamic=False, format=Format.LINE):
        """
        Initializes the chart and toolbar. To differentiate between live and static dashboards,
        use the the dynamic variable.
        """
        super(GraphWidget, self).__init__(parent)
        self.model = model
        self.format = format
        self.dashboard = parent

        self.setMinimumSize(QSize(300, 200))

        # Tool Bar Config
        toolbar = NERToolbar()
        config_button = NERImageButton(NERImageButton.Icons.EDIT, NERButton.Styles.BLUE)
        config_button.pressed.connect(lambda: EditDialog(self, self.reset, self.model, self.state).exec())
        toolbar.addLeft(config_button)
        reset_button = NERImageButton(NERImageButton.Icons.RESET, NERButton.Styles.RED)
        reset_button.pressed.connect(self.reset)
        toolbar.addLeft(reset_button)
        show_button = NERImageButton(NERImageButton.Icons.EXPORT, NERButton.Styles.GRAY)
        show_button.pressed.connect(self.showTables)
        toolbar.addLeft(show_button)
        remove_button = NERImageButton(NERImageButton.Icons.CLOSE, NERButton.Styles.GRAY)
        remove_button.pressed.connect(self.remove)
        toolbar.addLeft(remove_button)

        # Specific config for real time graphs
        if dynamic:
            refresh_button = NERImageButton(NERImageButton.Icons.REFRESH, NERButton.Styles.GRAY)
            refresh_button.pressed.connect(self.updateChart)
            toolbar.addRight(refresh_button)
            clear_button = NERImageButton(NERImageButton.Icons.TRASH, NERButton.Styles.RED)
            clear_button.pressed.connect(self.clearData)
            toolbar.addRight(clear_button)
            self.live_data = False
            self.live_button = NERImageButton(NERImageButton.Icons.START, NERButton.Styles.GREEN)
            self.live_button.pressed.connect(self.toggleLiveData)
            toolbar.addRight(self.live_button)

            self.timer = QTimer()
            self.timer.timeout.connect(self.updateChart)

        # Chart Config
        self.chart = QChart()
        self.chart.setTitle(f"Graph {index}")
        self.chart.setTheme(QChart.ChartTheme.ChartThemeLight)
        self.chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

        # View Config
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.chart_view.setStyleSheet("background-color: #f0f0f0")

        # Reset graph state, axes, and series
        self.reset()

        # Layout Config
        layout = QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.chart_view)
        self.setLayout(layout)

    def reset(self, new_state: GraphState = None):
        """
        Resets the graph.
        """
        if new_state is None:
            self.state = GraphState(format=self.format)
        else:
            self.state = new_state
        self.range_x = None
        self.range_y = None

        # Remove existing axes and data series
        self.chart.removeAllSeries()
        for axis in self.chart.axes():
            self.chart.removeAxis(axis)

        # Configure and add axes
        self.axis_x = QDateTimeAxis()
        self.axis_x.setTickCount(5)
        self.axis_x.setFormat("hh:mm:ss.z")
        self.axis_x.setTitleText("Time")
        self.chart.addAxis(self.axis_x, Qt.AlignmentFlag.AlignBottom)
        self.axis_y = QValueAxis()
        self.axis_y.setTitleText("Data")
        self.chart.addAxis(self.axis_y, Qt.AlignmentFlag.AlignLeft)

        # Add data if provided
        if self.state.data1 is not None:
            self.addSeries(self.model.getDataType(self.state.data1), self.state.data1)
        if self.state.data2 is not None:
            self.addSeries(self.model.getDataType(self.state.data2), self.state.data2)
        if self.state.data3 is not None:
            self.addSeries(self.model.getDataType(self.state.data3), self.state.data3)

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
            self.updateAxis(self.model.getDataModel(self.state.data1).getMinTime(),
                            self.model.getDataModel(self.state.data1).getMaxTime(),
                            self.model.getDataModel(self.state.data1).getMinValue(),
                            self.model.getDataModel(self.state.data1).getMaxValue())
        if self.state.data2 is not None:
            self.updateAxis(self.model.getDataModel(self.state.data2).getMinTime(),
                            self.model.getDataModel(self.state.data2).getMaxTime(),
                            self.model.getDataModel(self.state.data2).getMinValue(),
                            self.model.getDataModel(self.state.data2).getMaxValue())
        if self.state.data3 is not None:
            self.updateAxis(self.model.getDataModel(self.state.data3).getMinTime(),
                            self.model.getDataModel(self.state.data3).getMaxTime(),
                            self.model.getDataModel(self.state.data3).getMinValue(),
                            self.model.getDataModel(self.state.data3).getMaxValue())
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
            self.live_button.changeStyle(NERButton.Styles.GREEN)
            self.live_button.resetIcon(NERImageButton.Icons.START)
            self.timer.stop()
        else:
            self.live_button.changeStyle(NERButton.Styles.RED)
            self.live_button.resetIcon(NERImageButton.Icons.STOP)
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
        self.updateAxis(self.model.getDataModel(data_id).getMinTime(), self.model.getDataModel(data_id).getMaxTime(),
                        self.model.getDataModel(data_id).getMinValue(), self.model.getDataModel(data_id).getMaxValue())
        series.attachAxis(self.axis_x)
        series.attachAxis(self.axis_y)

    def updateAxis(self, xmin: QDateTime, xmax: QDateTime, ymin: float, ymax: float):
        """
        Updates the axis to use the new data values if they expand the bounds of the graph.
        """
        if ymin == ymax:  # Add offset to equal min/max to prevent display bug
            ymin = ymin - .001
            ymax = ymax + .001

        if self.range_x is None:
            self.range_x = [xmin, xmax]
        else:
            if xmin < self.range_x[0]:
                self.range_x[0] = xmin
            if xmax > self.range_x[1]:
                self.range_x[1] = xmax

        if self.range_y is None:
            self.range_y = [ymin, ymax]
        else:
            if ymin < self.range_y[0]:
                self.range_y[0] = ymin
            if ymax > self.range_y[1]:
                self.range_y[1] = ymax

        self.axis_x.setRange(self.range_x[0], self.range_x[1])
        self.axis_y.setRange(self.range_y[0], self.range_y[1])

    def remove(self):
        """
        Removes the graph from the display of graphs.
        """

        self.dashboard.removeGraph(self)


class GraphDashboardWidget(GraphDashboard):
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

        """
        store row of QSplitters at the top level
        """

        self.model = model
        self.dynamic = dynamic

        g = GraphWidget(self, 1, self.model, self.dynamic)
        self.graphs1 = [g]
        self.graphs2 = []
        self.next_index = 2

        toolbar = QToolBar()
        add_button = NERButton("+", NERButton.Styles.GRAY)
        add_button.addStyle("margin-right: 5%")
        add_button.pressed.connect(self.add)
        toolbar.addWidget(add_button)

        self.row1 = QSplitter()
        self.row2 = QSplitter()
        self.row1.addWidget(g)

        self.graphs = QSplitter()
        self.graphs.setOrientation(Qt.Orientation.Vertical)
        self.graphs.addWidget(self.row1)
        self.graphs.addWidget(self.row2)

        main_layout = QVBoxLayout()
        main_layout.addWidget(toolbar)
        main_layout.addWidget(self.graphs)
        self.setLayout(main_layout)

    def add(self):
        """
        Creates a new graph and adds it to the display.
        """

        gi = GraphWidget(self, self.next_index, self.model, self.dynamic)
        self.next_index += 1

        if len(self.graphs1) > len(self.graphs2):
            self.row2.addWidget(gi)
            self.graphs2.append(gi)

        else:
            self.row1.addWidget(gi)
            self.graphs1.append(gi)

    def removeGraph(self, graph):
        """
        Removes the given graph and closes its view.
        """

        if graph in self.graphs1:
            self.graphs1.remove(graph)

        if graph in self.graphs2:
            self.graphs2.remove(graph)

        graph.close()
