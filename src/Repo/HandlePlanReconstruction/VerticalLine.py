from PySide6.QtCore import *
from PySide6.QtGui import QKeySequence
import math
import pandas as pd
import numpy as np
from ServiceInfo import *


class VerticalLineModel1(QAbstractTableModel):
    positionChanged = Signal(int)
    def __init__(self, startX=100, parent: QObject = None):
        super().__init__(parent)
        self.__currentX = startX
        self.__minY = -100.0
        self.__maxY = 100.0

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
        if float(self.__currentX) <= 0 and newX < 0:
            return
        self.__currentX = self.__currentX + newX
        self.dataChanged.emit(self.index(0, 0), self.index(1, 1), [Qt.ItemDataRole.DisplayRole])
        self.positionChanged.emit(self.__currentX)
        return  self.__currentX

    # Удержание полосы на месте  
    # def keep_line_position(self, pos:float):
    #     self.__currentX = pos
    #     self.dataChanged.emit(self.index(0, 0), self.index(1, 1), [Qt.ItemDataRole.DisplayRole])
    #     self.positionChanged.emit(self.__currentX)


class VerticalLineModel2(QAbstractTableModel):
    positionChanged = Signal(int)
    def __init__(self, startX=False, parent: QObject = None):
        super().__init__(parent)
        self.__currentX = startX
        self.__minY = -100.0
        self.__maxY = 100.0

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
        if float(self.__currentX) <= 0 and newX < 0:
            return
        self.__currentX = newX
        self.dataChanged.emit(self.index(0, 0), self.index(1, 1), [Qt.ItemDataRole.DisplayRole])
        self.positionChanged.emit(self.__currentX)
        return  self.__currentX

    







    
