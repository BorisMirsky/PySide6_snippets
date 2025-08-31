# This Python file uses the following encoding: utf-8
from domain.units.AbstractUnit import AbstractReadWriteUnit
from domain.dto.Travelling import PicketDirection
from PySide6.QtCore import QObject
from typing import Optional


class PicketPositionUnit(AbstractReadWriteUnit[float]):
    def __init__(self, origin: AbstractReadWriteUnit[float], direction: PicketDirection, start_picket: float = 0.0, parent: Optional[QObject] = None) ->None:
        super().__init__(parent)
        origin.changed.connect(lambda: self.changed.emit(self.read()))
        self.__multiplyer: float = 1 if direction == PicketDirection.Forward else -1
        self.__origin: AbstractReadWriteUnit[float] = origin
        self.__start_picket: float = start_picket


    def setStartPicket(self, start_picket: float = 0.0) ->float:
        self.__start_picket = start_picket
        self.changed.emit(self.read())
        return self.__start_picket
    def startPicket(self) ->float:
        return self.__start_picket

    def write(self, value: float) ->None:
        self.__origin.write((value - self.__start_picket) * self.__multiplyer)
    def read(self) ->float:
        return self.__start_picket + self.__origin.read() * self.__multiplyer
