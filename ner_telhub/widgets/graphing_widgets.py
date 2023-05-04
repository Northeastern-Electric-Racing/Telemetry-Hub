from abc import abstractmethod
from datetime import datetime
from enum import Enum
from functools import partial
from typing import Callable, List

from PyQt6.QtWidgets import (
    QLabel, QVBoxLayout,
    QWidget, QComboBox,
    QDialog, QGridLayout,
    QDialogButtonBox, QSplitter,
    QTableView, QMessageBox,
    QSizePolicy, QLineEdit,
    QCheckBox, QDateTimeEdit
)
from PyQt6.QtCharts import (
    QLineSeries, QChart, QChartView,
    QVXYModelMapper, QDateTimeAxis,
    QValueAxis
)
from PyQt6.QtGui import QPainter
from PyQt6.QtCore import QSize, Qt, QTimer, QMargins

from ner_telhub import colors
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

    def __init__(
            self,
            data: List = None,
            format: Format = Format.LINE,
            auto_y: bool = True,
            auto_x: bool = True,
            y_range: List[float] = None,
            x_range: List[datetime] = None):
        if data is not None:
            self.data = data
        else:
            self.data = []

        self.format = format
        self.auto_y = auto_y # says whether or not we use automatic y axis scaling
        self.auto_x = auto_x
        self.y_range = y_range # current y range
        self.x_range = x_range


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


class GraphDashboard(QWidget):
    @abstractmethod
    def removeGraph(self, graph):
        pass


class GraphWidget(QWidget):
    """
    Main graph widget for displaying data in charts.
    """

    def __init__(
            self,
            parent: GraphDashboard,
            model: DataModelManager,
            dynamic=False,
            format=Format.LINE):
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
        toolbar.setStyleSheet(
            "QToolBar { background-color: " +
            colors.LIGHT1 +
            "; border: none }")
        config_button = NERImageButton(
            NERImageButton.Icons.EDIT,
            NERButton.Styles.BLUE)
        config_button.pressed.connect(
            lambda: EditDialog(
                self,
                self.reset,
                self.model,
                self.state,
                dynamic).exec())
        config_button.setToolTip("Edit the configuration of this graph")
        toolbar.addLeft(config_button)
        reset_button = NERImageButton(
            NERImageButton.Icons.TRASH,
            NERButton.Styles.RED)
        reset_button.pressed.connect(self.reset)
        reset_button.setToolTip("Reset this to be a blank graph")
        toolbar.addLeft(reset_button)

        # Configure buttons on the right
        show_button = NERImageButton(
            NERImageButton.Icons.EXPORT,
            NERButton.Styles.GRAY)
        show_button.pressed.connect(self.showTables)
        show_button.setToolTip("Show the data in this graph in a tabular form")
        toolbar.addRight(show_button)
        remove_button = NERImageButton(
            NERImageButton.Icons.CLOSE,
            NERButton.Styles.RED)
        remove_button.pressed.connect(self.remove)
        remove_button.setToolTip("Delete this graph")
        toolbar.addRight(remove_button)

        # Specific config for real time graphs
        if dynamic:
            self.timer = QTimer()
            self.timer.timeout.connect(self.updateChart)
            self.timer.start()

        # Chart Config
        self.chart = QChart()
        self.chart.setTheme(QChart.ChartTheme.ChartThemeLight)
        self.chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        self.chart.setMargins(QMargins(0, 0, 0, 0))

        # View Config
        self.chart_view = QChartView(self.chart)
        self.chart_view.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding)
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.chart_view.setStyleSheet(f"background-color: {colors.LIGHT1}")

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
        if len(self.state.data) > 0:
            self.axis_y.setTitleText(
                self.model.getDataUnit(
                    self.state.data[0]))
        else:
            self.axis_y.setTitleText("Data")
        self.chart.addAxis(self.axis_y, Qt.AlignmentFlag.AlignLeft)

        # Set axes if user specified
        if not self.state.auto_y:
            self.axis_y.setRange(self.state.y_range[0], self.state.y_range[1])
        if not self.state.auto_x:
            self.axis_x.setRange(self.state.x_range[0], self.state.x_range[1])

        # Add data if provided
        for data in self.state.data:
            if data is not None:
                self.addSeries(self.model.getDataType(data), data)

    def showTables(self):
        """
        Shows current data tables.
        """
        for data in self.state.data:
            if data is not None:
                DataTable(self, self.model.getDataModel(data)).show()

    def updateChart(self):
        """
        Updates the axis of the chart by finding the max/min
        """

        for data in self.state.data:
            if data is not None:
                try:
                    self.updateAxis(
                        self.model.getDataModel(data).getMinTime(),
                        self.model.getDataModel(data).getMaxTime(),
                        self.model.getDataModel(data).getMinValue(),
                        self.model.getDataModel(data).getMaxValue())
                except ValueError:  # for invalid data IDs
                    self.reset()

        self.chart_view.update()

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
        self.updateAxis(
            self.model.getDataModel(data_id).getMinTime(),
            self.model.getDataModel(data_id).getMaxTime(),
            self.model.getDataModel(data_id).getMinValue(),
            self.model.getDataModel(data_id).getMaxValue())
        series.attachAxis(self.axis_x)
        series.attachAxis(self.axis_y)

    def updateAxis(
            self,
            xmin: datetime,
            xmax: datetime,
            ymin: float,
            ymax: float):
        """
        Updates the axis to use the new data values if they expand the bounds of the graph.
        """
        if ymin == ymax:  # Add offset to equal min/max to prevent display bug
            ymin = ymin - .001
            ymax = ymax + .001

        if self.state.auto_x:  # only dynamically update x-axis if user did not hard code values
            if self.state.x_range is None:
                self.state.x_range = [xmin, xmax]
            else:
                self.state.x_range[0] = xmin
                self.state.x_range[1] = xmax

        if self.state.auto_y:  # only dynamically update y-axis if user did not hard code values
            if self.state.y_range is None:
                self.state.y_range = [ymin, ymax]
            else:
                if ymin < self.state.y_range[0]:
                    self.state.y_range[0] = ymin
                if ymax > self.state.y_range[1]:
                    self.state.y_range[1] = ymax

        self.axis_x.setRange(self.state.x_range[0], self.state.x_range[1])
        self.axis_y.setRange(self.state.y_range[0], self.state.y_range[1])

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

    def __init__(
            self,
            parent: QWidget,
            model: DataModelManager,
            dynamic=False):
        """
        Creates a graph dashboard with the given model. If dynamic is true, this dashboard will
        support real time plotting.
        """
        super(GraphDashboardWidget, self).__init__(parent)
        self.setStyleSheet("""QSplitter { background-color: #f0f0f0}
            QSplitter::handle { background-color: #999999 }""")

        self.model = model
        self.dynamic = dynamic

        g = GraphWidget(self, self.model, self.dynamic)
        self.graphs1 = [g]
        self.graphs2 = []
        self.graphs3 = []

        self.toolbar = NERToolbar()
        self.toolbar.setStyleSheet(
            f"background-color: {colors.PRIMARY_BACKGROUND}; border: none")
        add_button = NERButton("Add Graph", NERButton.Styles.GRAY)
        add_button.setToolTip("Add a graph to the dashboard")
        add_button.pressed.connect(self.add)
        self.toolbar.addLeft(add_button)

        default_graph_button = NERButton(
            "Load Default Graphs", NERButton.Styles.GRAY)
        default_graph_button.pressed.connect(self.loadDefaultGraphs)
        default_graph_button.setToolTip(
            "Set the graphs to show important data points")
        self.toolbar.addRight(default_graph_button)

        self.row1 = QSplitter()
        self.row2 = QSplitter()
        self.row3 = QSplitter()
        self.row1.addWidget(g)
        self.row2.hide()
        self.row3.hide()

        self.graphs = QSplitter()
        self.graphs.setOrientation(Qt.Orientation.Vertical)
        self.graphs.addWidget(self.row1)
        self.graphs.addWidget(self.row2)
        self.graphs.addWidget(self.row3)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.toolbar)
        main_layout.addWidget(self.graphs)
        self.setLayout(main_layout)

    def add(self):
        """
        Creates a new graph and adds it to the display.
        """

        if len(self.graphs1) + len(self.graphs2) + len(self.graphs3) == 6:
            QMessageBox.critical(
                self,
                "Graph Error",
                "Cannot have more than 6 graphs on the dashboard")
            return

        gi = GraphWidget(self, self.model, self.dynamic)

        if len(
            self.graphs1) <= len(
            self.graphs2) and len(
            self.graphs1) <= len(
                self.graphs3):
            self.row1.addWidget(gi)
            self.graphs1.append(gi)
        elif len(self.graphs2) <= len(self.graphs3):
            self.row2.addWidget(gi)
            self.graphs2.append(gi)
        else:
            self.row3.addWidget(gi)
            self.graphs3.append(gi)

        # Shows any non-empty rows.
        if self.graphs1:
            self.row1.show()

        if self.graphs2:
            self.row2.show()

        if self.graphs3:
            self.row3.show()

    def removeGraph(self, graph):
        """
        Removes the given graph and closes its view.
        """

        if len(self.graphs1) + len(self.graphs2) + len(self.graphs3) == 1:
            QMessageBox.critical(
                self,
                "Graph Error",
                "Must have at least 1 graph on the dashboard")
            return

        if graph in self.graphs1:
            self.graphs1.remove(graph)
        elif graph in self.graphs2:
            self.graphs2.remove(graph)
        elif graph in self.graphs3:
            self.graphs3.remove(graph)

        graph.close()

        # Hides any non-empty rows.
        if not self.graphs1:
            self.row1.hide()

        if not self.graphs2:
            self.row2.hide()

        if not self.graphs3:
            self.row3.hide()

    def loadDefaultGraphs(self):
        expected_default_ids = [
            [45], [101], [
                91, 92, 93], [
                2, 89, 51], [1], [
                10, 28]]
        actual_default_ids = [[], [], [], [], [], []]
        model_ids = self.model.getAvailableIds()

        if len(model_ids) == 0:
            QMessageBox.critical(
                self,
                "Error adding graphs",
                "There is no data to add to graphs")
            return

        for i in range(len(expected_default_ids)):
            for id in expected_default_ids[i]:
                if id in model_ids:
                    actual_default_ids[i].append(id)

        new_graphs = []
        for i in range(len(actual_default_ids)):
            new_graphs.append(GraphWidget(self, self.model, self.dynamic))
            new_graphs[i].reset(GraphState(actual_default_ids[i], Format.LINE))

        graphs = [self.graphs1, self.graphs2, self.graphs3]
        rows = [self.row1, self.row2, self.row3]
        for i in range(len(graphs)):
            for graph in graphs[i]:
                graph.close()

            graphs[i] = [new_graphs[i], new_graphs[i + 3]]
            for graph in graphs[i]:
                rows[i].addWidget(graph)

            rows[i].show()

        self.graphs1 = graphs[0]
        self.graphs2 = graphs[1]
        self.graphs3 = graphs[2]
