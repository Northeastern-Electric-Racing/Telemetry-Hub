import os
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QMovie

resources = os.path.dirname(__file__) + "/../../resources"

class NERLoadingSpinner(QLabel):
    """
    Loading circle label to indicate long running tasks.
    """

    def __init__(self):
        super().__init__()

        self.movie = QMovie(os.path.join(resources, "loading_circle.gif"))
        self.setMovie(self.movie)

    def startAnimation(self):
        self.movie.start()
        self.setVisible(True)

    def stopAnimation(self):
        self.movie.stop()
        self.setVisible(False)

