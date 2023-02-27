# autopep8: off
import os
import sys

sys.path.append(os.path.dirname(__file__) + "/ner_processing")

# This must be after the above line for the ner_processing library to load correctly
from ner_telhub import app


if __name__ == '__main__':
    app.run()
