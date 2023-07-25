from datetime import datetime
from typing import List

from ner_telhub.widgets.graphing_widgets.format import Format


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
