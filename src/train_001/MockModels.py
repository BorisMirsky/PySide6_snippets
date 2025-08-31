from AbstractModels import AbstractReadWriteModel
from AbstractModels import AbstractWriteModel
from AbstractModels import AbstractReadModel
from PySide6.QtCore import QObject, QTimer
from typing import TypeVar
import random
import math
import time

MockModelType = TypeVar('MockModelType')
class MockReadWriteModel(QObject, AbstractReadWriteModel[MockModelType]):
    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        self.__value = None

    def read(self) ->MockModelType:
        print(f'Read value from mock model: {self.__value}')
        return self.__value

    def write(self, value: MockModelType) ->None:
        print(f'Write value to mock model: {self.__value} => {value}')
        self.__value = value
        self.valueChanged.emit()



BlackHoleModelType = TypeVar('BlackHoleModelType')
class BlackHoleModel(QObject, AbstractWriteModel[BlackHoleModelType]):
    def __init__(self, parent: QObject = None):
        super().__init__(parent)

    def write(self, value: BlackHoleModelType) ->None:
        print(f'Write value to black hole model: {value}')
        self.valueChanged.emit()




class SinMockModel(QObject, AbstractReadModel[float]):
    def __init__(self, amplitude: float = 1, frequency: float = 1, pollution: float = 0.1, parent: QObject = None):
        super().__init__(parent)
        self.__value = None

        def __processMockValue():
            self.__value = amplitude * math.sin(frequency * time.time()) + random.random() * pollution
            self.valueChanged.emit()

        mockValueTimer = QTimer(self)
        for i in range(10):
            mockValueTimer.timeout.connect(__processMockValue)
        mockValueTimer.start(10)

    def read(self) ->float:
        return self.__value



