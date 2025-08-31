# This Python file uses the following encoding: utf-8
from domain.units.AbstractUnit import AbstractReadUnit, AbstractReadWriteUnit
from .Strategies import AbstractInterpolationStrategy
from PySide6.QtCore import QObject
from typing import Optional

class ReadInterpolationUnit(AbstractReadUnit[float]):
    def __init__(self, origin: AbstractReadUnit[float], interpolation: AbstractInterpolationStrategy, inverse: bool = False, parent: Optional[QObject] = None) ->None:
        super().__init__(parent)
        self.__multiplyer = -1 if inverse else 1
        self.__interpolation = interpolation
        self.__origin = origin
        # self.__value = None
        self.__value = origin.read()
        self.__origin.changed.connect(self.__onOriginValueUpdated)

    def read(self) ->float:
        return self.__value
    def __onOriginValueUpdated(self):
        self.__value = self.__multiplyer * self.__interpolation.interpolateXtoY(self.__origin.read())
        self.changed.emit(self.__value)
class ReadWriteInterpolationUnit(AbstractReadWriteUnit[float]):
    def __init__(self, origin: AbstractReadWriteUnit[float], interpolation: AbstractInterpolationStrategy, inverse: bool = False, parent: Optional[QObject] = None) ->None:
        super().__init__(parent)
        self.__multiplyer = -1 if inverse else 1
        self.__interpolation = interpolation
        self.__origin = origin
        self.__value = None
        self.__origin.changed.connect(self.__onOriginValueUpdated)

    def read(self) ->float:
        return self.__value
    def write(self, value: float) ->None:
        self.__origin.write(self.__interpolation.interpolateYtoX(self.__multiplyer * value))
    def __onOriginValueUpdated(self):
        self.__value = self.__multiplyer * self.__interpolation.interpolateXtoY(self.__origin.read())
        self.changed.emit(self.__value)
