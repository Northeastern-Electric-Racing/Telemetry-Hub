from tkinter import messagebox
from ner_telhub.widgets.graphing_widgets.format import Format
from ner_telhub.widgets.graphing_widgets.graph_dashboard import GraphDashboard
from ner_telhub.widgets.graphing_widgets.graph_state import GraphState
from ner_telhub.widgets.graphing_widgets.graph_widget import GraphWidget
from ner_telhub.widgets.styled_widgets.styled_widgets import NERButton, NERToolbar
from ner_telhub.model.data_models import DataModelManager
from PyQt6.QtWidgets import (
      QSplitter,
      QWidget,
      QVBoxLayout,
      QMessageBox
)
from PyQt6.QtCore import Qt
from ner_telhub import colors


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
            messagebox.critical(
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
