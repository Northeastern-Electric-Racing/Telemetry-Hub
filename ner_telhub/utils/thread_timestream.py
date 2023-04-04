from PyQt6.QtCore import QDateTime

from ner_processing.data import Data
from ner_telhub.utils.timestream_constants import DATE_TIME_FORMAT


def thread_timestream(row):
    data = row['Data']

    data_id = int(data[1]['ScalarValue'])
    time = QDateTime.fromString(
        data[2]['ScalarValue'][:-6], DATE_TIME_FORMAT).toPyDateTime()
    try:
        value = float(data[3]['ScalarValue'])
    except Exception:
        value = data[4]['ScalarValue']

    return Data(time, data_id, value)
