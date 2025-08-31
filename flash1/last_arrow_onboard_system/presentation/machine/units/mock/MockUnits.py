from domain.units.AbstractUnit import AbstractReadUnit
from domain.dto.Travelling import MovingDirection
from PySide6.QtCore import QObject, QTimer
from random import randrange
from typing import Optional
import random
import math
import time


class TickCounterMockProvider(AbstractReadUnit[int]):
    def __init__(self, tick_period_ms: float, ticks_direction: MovingDirection = MovingDirection.Forward, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.__value = 0
        self.__multiplyer: int = ticks_direction.multiplier() # Здаем направление тиков: увеличиваются или уменьшаются.

        def __processMockValue():
            # number = randrange(100)
            # match number:
            #     case 1:
            #         self.__value -= 8
            #     case number if 2 <= number < 40:
            #         pass
            #     case _:
            #         self.__value += 9
            self.__value += randrange(2, 5) * self.__multiplyer
            self.changed.emit(self.__value)

        mockValueTimer = QTimer(self)
        mockValueTimer.timeout.connect(__processMockValue)
        mockValueTimer.start(tick_period_ms)

    def read(self) ->float:
        return self.__value

class SinMockUnit(AbstractReadUnit[float]):
    def __init__(self, offset: float = 0, amplitude: float = 1, frequency: float = 1, pollution: float = 0.1, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.__value: float = None

        def __processMockValue():
            self.__value = offset + amplitude * math.sin(frequency * time.time()) + random.random() * pollution
            self.changed.emit(self.__value)

        mockValueTimer = QTimer(self)
        mockValueTimer.timeout.connect(__processMockValue)
        mockValueTimer.start(50)

    def read(self) ->float:
        return self.__value
class IntMockUnit(AbstractReadUnit[int]):
    def __init__(self, bottom: int, top: int, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.__value: int = None

        def __processMockValue():
            self.__value = random.randint(bottom, top)
            self.changed.emit(self.__value)

        mockValueTimer = QTimer(self)
        mockValueTimer.timeout.connect(__processMockValue)
        mockValueTimer.start(250)

    def read(self) ->float:
        return self.__value

class ConstantValueMockUnit(AbstractReadUnit[float]):
    def __init__(self, value: float, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.__value: float = value

        def __processMockValue():            
            self.changed.emit(self.__value)

        mockValueTimer = QTimer(self)
        mockValueTimer.timeout.connect(__processMockValue)
        mockValueTimer.start(250)

    def read(self) ->float:
        return self.__value

