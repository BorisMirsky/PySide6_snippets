# This Python file uses the following encoding: utf-8
from .Strategies import AbstractInterpolationStrategy
from PySide6.QtCore import QObject, QAbstractTableModel, QModelIndex
from typing import Optional, Any
import numpy



class ForwardInterpolationStrategyTableModel(QAbstractTableModel):
    def __init__(self, strategy: AbstractInterpolationStrategy, definitionArea: (float, float), points: int, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.__strategy = strategy
        self.__points = points
        self.__space = numpy.linspace(definitionArea[0], definitionArea[1], points).tolist()
        print(self.__space)

    def rowCount(self, parent: QModelIndex) ->int:
        return self.__points
    def columnCount(self, parent: QModelIndex) ->int:
        return 2
    def data(self, index: QModelIndex, role: int) ->Any:
        if not index.isValid():
            return None

        if index.column() == 0:
            return self.__space[index.row()]
        if index.column() == 1:
            return self.__strategy.interpolateXtoY(self.__space[index.row()])
        return None
class BackwardInterpolationStrategyTableModel(QAbstractTableModel):
    def __init__(self, strategy: AbstractInterpolationStrategy, definitionArea: (float, float), points: int, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.__strategy = strategy
        self.__points = points
        self.__space = numpy.linspace(definitionArea[0], definitionArea[1], points).tolist()
        print(self.__space)

    def rowCount(self, parent: QModelIndex) ->int:
        return self.__points
    def columnCount(self, parent: QModelIndex) ->int:
        return 2
    def data(self, index: QModelIndex, role: int) ->Any:
        if not index.isValid():
            return None

        if index.column() == 0:
            return self.__space[index.row()]
        if index.column() == 1:
            return self.__strategy.interpolateYtoX(self.__space[index.row()])
        return None



