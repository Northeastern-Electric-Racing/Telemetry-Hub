from abc import abstractmethod
from PyQt6.QtWidgets import QWidget

class GraphDashboard(QWidget):
    @abstractmethod
    def removeGraph(self, graph):
        pass
