# This Python file uses the following encoding: utf-8
from typing import TypeVar, Generic, Optional, Any
from PySide6.QtCore import QObject, Signal

UnitType = TypeVar('UnitGenericType')
class AbstractReadUnit(QObject, Generic[UnitType]):
    changed = Signal(object)
    def __init__(self, parent: Optional[QObject] = None) ->None:
        super().__init__(parent)
    def read(self) ->UnitType:
        pass

class AbstractReadWriteUnit(AbstractReadUnit[UnitType]):
    def write(self, value: UnitType) ->None:
        pass

