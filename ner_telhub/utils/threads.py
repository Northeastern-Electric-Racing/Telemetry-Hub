import sys, traceback
from PyQt6.QtCore import QObject, QRunnable, QThreadPool, pyqtSignal, QThread


class WorkerSignals(QObject):
    """Defines the signals available from a running worker thread.
    Supported signals are:

    finished
        None
    error
        tuple (exctype, value, traceback.format_exc() )
    result
        object data returned from processing, anything
    progress
        int indicating % progress
    message
        str message from the worker function
    """

    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)
    message = pyqtSignal(str)



class Worker(QRunnable):
    """Threaded worker which runs a process on a seperate thread. 

    Threads are deployed by the QThreadPool object, which creates and manages QThreads 
    to get optimal system performance. 
    
    Example Implementation
    ----------------------
    def work(*args, **kwargs) -> Any:
        .... perform work ....

    worker = BasicWorker(work)
    try:
        worker.signals.finished.connect(...)
        worker.signals.error.connect(...)
        worker.start()
    except Exception as e: 
        .... handle error ....
    """

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self.kwargs["progress"] = self.signals.progress # Give function access to progress/message signals
        self.kwargs["message"] = self.signals.message
        self.runningThread = None
    

    def run(self):
        """Runs the actual thread function, emitting status signals."""
        self.runningThread = QThread.currentThread()
        try:
            result = self.fn(*self.args, **self.kwargs)
            self.signals.result.emit(result)
            self.signals.finished.emit()
        except:
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
            self.signals.finished.emit()


    def start(self) -> None:
        """Starts this QRunnable instance on the global threadpool.

        Issues may arise depending on the number of optimal threads per user system, so establishing
        multiple threadpool instances may be necessary.
        """

        if self.runningThread != None:
            raise RuntimeError("Thread is already running!")

        threadpool = QThreadPool.globalInstance()
        if threadpool.activeThreadCount() >= threadpool.maxThreadCount():
            raise RuntimeError(f"Exceeded max system thread count of {threadpool.maxThreadCount()}")
        threadpool.start(self)


    def stop(self):
        """Stops this thread and emits corresponding signals."""

        self.runningThread.terminate()
        self.runningThread = None
        self.signals.finished.emit()





        


