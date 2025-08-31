from PySide6.QtCore import *
from PySide6.QtGui import QKeySequence
import math
import pandas as pd
import numpy as np
from typing import List, Any


class VerticalLineModel(QAbstractTableModel):
    positionChanged = Signal(int)
    def __init__(self, startX, parent: QObject = None):
        super().__init__(parent)
        self.__currentX = startX
        self.__minY = -1000.0
        self.__maxY = 1000.0

    def currentX(self):
        return  self.__currentX

    def rowCount(self, parent):
        return 2

    def columnCount(self, parent):
        return 2

    def data(self, index: QModelIndex, role: int):
        if not index.isValid():
            return None
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if index.column() == 0:
            return self.__currentX
        elif index.column() == 1 and index.row() == 0:
            return self.__minY
        elif index.column() == 1 and index.row() == 1:
            return self.__maxY
        else:
            return
        
    def shiftLine(self, newX: float):
        if newX == 0:
            return
        self.__currentX = self.__currentX + newX
        self.dataChanged.emit(self.index(0, 0), self.index(1, 1), [Qt.ItemDataRole.DisplayRole])
        self.positionChanged.emit(self.__currentX)
        return  self.__currentX




class HorizontalLineModel(QAbstractTableModel):
    positionChanged = Signal(int)
    def __init__(self, startY, startX, endX, parent: QObject = None):   # startX=False, endX=False,
        super().__init__(parent)
        self.__currentY = startY
        self.__startX = startX
        self.__endX = endX

    def currentY(self):
        return self.__currentY

    def rowCount(self, parent):
        return 2

    def columnCount(self, parent):
        return 2

    def data(self, index: QModelIndex, role: int):
        if not index.isValid():
            return None
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if index.column() == 0:
            return self.__currentY
        elif index.column() == 1 and index.row() == 0:
            return self.__startX
        elif index.column() == 1 and index.row() == 1:
            return self.__endX
        else:
            return

    def shiftLine(self, newY: float):
        if newY == 0:
            return
        if float(self.__currentY) <= 0 and newY < 0:
            return
        self.__currentY = self.__currentY + newY
        self.dataChanged.emit(self.index(0, 0), self.index(1, 1), [Qt.ItemDataRole.DisplayRole])
        self.positionChanged.emit(self.__currentY)
        return self.__currentY


class NumpyTableModel(QAbstractTableModel):
    def __init__(self, data: np.array, parent: QObject = None):
        super().__init__(parent)
        self.__data: np.array = data
        self.removed_picket_index = 0

    def columnCount(self, parent: QModelIndex) -> int:
        return self.__data.shape[1]

    def rowCount(self, parent: QModelIndex) -> int:
        return self.__data.shape[0]

    def data(self, index: QModelIndex, role: int) -> Any:
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if not index.isValid():
            return None
        return str(self.__data[index.row()][index.column()])

    def appendRow(self, record: List[float]):
        self.beginInsertRows(QModelIndex(), self.rowCount(QModelIndex()), self.rowCount(QModelIndex()))
        self.__data = np.vstack([self.__data, record])
        self.endInsertRows()
