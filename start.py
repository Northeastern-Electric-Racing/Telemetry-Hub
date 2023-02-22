import os
import sys

sys.path.append(os.path.dirname(__file__ ) + "/Ner_Processing")

from ner_telhub import app

if __name__ == '__main__':
    app.run()