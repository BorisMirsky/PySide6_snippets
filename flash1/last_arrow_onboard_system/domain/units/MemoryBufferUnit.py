from .AbstractUnit import AbstractReadWriteUnit
from typing import TypeVar, Generic, Optional
from PySide6.QtCore import QObject

UnitType = TypeVar('UnitGenericType')
class MemoryBufferUnit(AbstractReadWriteUnit[UnitType]):
    def __init__(self, value: UnitType = None, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.__value = value

    def read(self) ->UnitType:
        return self.__value

    def write(self, value: UnitType) ->None:
        self.__value = value
        self.changed.emit(self.__value)
