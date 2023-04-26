# autopep8: off
import os

from ner_telhub import app

root_dir = os.path.dirname(__file__)


if __name__ == '__main__':
    app.run()
