# This Python file uses the following encoding: utf-8
from domain.units.AbstractUnit import AbstractReadUnit, AbstractReadWriteUnit
from domain.dto.Travelling import MovingDirection
from PySide6.QtCore import QObject, QTimer
from typing import Optional

#======================================================================

class TickCounterProvider(AbstractReadUnit[int]):
    def __init__(self, origin: AbstractReadUnit[int], inverse = bool, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.__multiplyer: int = -1 if inverse else 1
        self.__origin: AbstractReadUnit[int] = origin

        self.__origin.changed.connect(self.__updateInternalValue)
        self.__previousValue: int = self.__origin.read()
        self.__ticks: int = 0

    def read(self) ->int:
        return self.__ticks
    def reset(self, ticks: int = 0) ->None:
        self.__previousValue = self.__origin.read()
        self.__ticks = 0
        self.changed.emit(self.read())

    def __updateInternalValue(self):
        if self.__previousValue is None:
            self.__previousValue = self.__origin.read()
            return

        currentValue = self.__origin.read()
        difference = currentValue - self.__previousValue

        self.__previousValue = currentValue
        if difference > 32767:
            self.__ticks -= self.__multiplyer * 65536 - difference
        elif difference < -32767:
            self.__ticks += self.__multiplyer * 65536 + difference
        else:
            self.__ticks += self.__multiplyer * difference
        self.changed.emit(self.__ticks)

#======================================================================

class TickCounterProvider2(AbstractReadUnit[int]):
    def __init__(self, origin: AbstractReadUnit[int], inverse = bool, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.__multiplyer: int = -1 if inverse else 1
        self.__origin: AbstractReadUnit[int] = origin

        self.__origin.changed.connect(self.__updateInternalValue)
        self.__previousValue: int = self.__origin.read()
        self.__ticks: int = 0

    def read(self) ->int:
        return self.__ticks
    def reset(self, ticks: int = 0) ->None:
        self.__previousValue = self.__origin.read()
        self.__ticks = 0
        self.changed.emit(self.read())

    def __updateInternalValue(self):
        if self.__previousValue is None:
            self.__previousValue = self.__origin.read()
            return

        currentValue = self.__origin.read()
        difference = currentValue - self.__previousValue
        self.__previousValue = currentValue
        
        d = 0
        if difference > 32767:
            d -= 65536 - difference
        elif difference < -32767:
            d += 65536 + difference
        else:
            d += difference

        self.__ticks += self.__multiplyer * d
        self.changed.emit(self.__ticks)

class DistanceTravelledProvider(AbstractReadWriteUnit[float]):
    def __init__(self, direction: MovingDirection, tick_counter: AbstractReadUnit[int], ticks_per_meter: float, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.__tick_counter: AbstractReadUnit[int] = tick_counter
        self.__multiplyer: int = direction.multiplier()
        self.__ticks_per_meter: float = ticks_per_meter
        self.__offset: float = 0
        self.__tick_counter.changed.connect(lambda: self.changed.emit(self.read()))

    def write(self, value: float) ->None:
        current_position: float = self.__multiplyer * self.__tick_counter.read() / self.__ticks_per_meter
        self.__offset = value - current_position
        self.changed.emit(self.read())
    def read(self) ->float:
        return self.__offset + self.__multiplyer * self.__tick_counter.read() / self.__ticks_per_meter

