# This Python file uses the following encoding: utf-8
from typing import TypeVar, Generic
from PySide6.QtCore import Signal


ReadModelType = TypeVar('ReadModelGenericType')
class AbstractReadModel(Generic[ReadModelType]):
    valueChanged = Signal()
    def read(self) ->ReadModelType:
        pass

WriteModelType = TypeVar('WriteModelGenericType')
class AbstractWriteModel(Generic[WriteModelType]):
    def write(self, value: WriteModelType) ->None:
        pass

ReadWriteModelType = TypeVar('ReadWriteModelGenericType')
class AbstractReadWriteModel(AbstractReadModel[ReadWriteModelType], AbstractWriteModel[ReadWriteModelType]):
    pass

