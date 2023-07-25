from datetime import datetime
from PyQt6.QtCore import QSize, Qt, QTimer, QMargins
from PyQt6.QtGui import QPainter
from PyQt6.QtWidgets import (
      QWidget, QVBoxLayout, QSizePolicy)
from PyQt6.QtCharts import (
      QChart, QChartView, QLineSeries, QVXYModelMapper,
      QDateTimeAxis, QValueAxis)
from ner_telhub.model.data_models import DataModelManager
from ner_telhub.widgets.graphing_widgets.data_table import DataTable
from ner_telhub.widgets.graphing_widgets.edit_dialog import EditDialog
from ner_telhub.widgets.graphing_widgets.format import Format
from ner_telhub.widgets.graphing_widgets.graph_state import GraphState
from ner_telhub.widgets.styled_widgets.ner_button import NERButton
from ner_telhub.widgets.styled_widgets.ner_image_button import NERImageButton
from ner_telhub.widgets.styled_widgets.ner_toolbar import NERToolbar
from ner_telhub import colors

class GraphWidget(QWidget):
    """
    Main graph widget for displaying data in charts.
    """

    def __init__(
            self,
            parent: QWidget,
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
