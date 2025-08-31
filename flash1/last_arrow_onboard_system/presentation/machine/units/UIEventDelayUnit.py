import time
from PySide6.QtCore import QCoreApplication, QObject, QEvent, Signal, Qt


class TraceEventDispatcherQueueReceiver(QObject):
    traced_event_received = Signal(float)
    class TraceEventDispatcherQueueEvent(QEvent):
        def __init__(self) ->None: 
            super().__init__(QEvent.Type(QEvent.Type.User + 1000))
            self.__creation_time: float = time.time()
        @property
        def creation_time(self) ->float:
            return self.__creation_time
        @property
        def elapsed(self) ->float:
            return time.time() - self.__creation_time

    def __init__(self, delay: int, parent: QObject | None = None) ->None: 
        super().__init__(parent = parent)
        self.startTimer(delay)
    def timerEvent(self, e) ->None:
        super().timerEvent(e)
        QCoreApplication.instance().postEvent(self, TraceEventDispatcherQueueReceiver.TraceEventDispatcherQueueEvent(), Qt.EventPriority.LowEventPriority.value)
    def event(self, e: QEvent) ->bool:
        if not isinstance(e, TraceEventDispatcherQueueReceiver.TraceEventDispatcherQueueEvent):
            return super().event(e)
        else:
            # print(f'Handle trace event: {e.creation_time}|{e.elapsed:.4f}')
            self.traced_event_received.emit(round(e.elapsed, 4))
            return True
