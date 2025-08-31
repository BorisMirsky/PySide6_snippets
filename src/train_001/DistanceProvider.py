# This Python file uses the following encoding: utf-8
from AbstractModels import AbstractReadModel
from PySide6.QtCore import QObject

class DistanceProvider(QObject, AbstractReadModel[float]):
    def __init__(self, parent: QObject = None) ->None:
        super().__init__(parent)
        self.startTimer(100)
        self.__value = 0
    def read(self) ->float:
        return self.__value
    def timerEvent(self, event) ->None:
        super().timerEvent(event)
        self.__value += 0.214
        self.valueChanged.emit()
