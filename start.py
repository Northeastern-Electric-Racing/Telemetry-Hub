import multiprocessing as mp
from ner_telhub.view.vehicle import window
from ner_processing.live import xbee

if __name__ == '__main__':
    recv, send = mp.Pipe()
    queue = mp.Queue()

    xbee_process = mp.Process(target=xbee.run, args=(queue, recv,))
    window_process = mp.Process(target=window.run, args=(queue, send,))

    xbee_process.start()
    window_process.start()

    while True:
        pass