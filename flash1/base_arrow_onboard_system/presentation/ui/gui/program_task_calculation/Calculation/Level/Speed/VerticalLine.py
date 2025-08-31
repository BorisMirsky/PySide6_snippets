from PySide6.QtCore import *
from PySide6.QtGui import QKeySequence
import math
import pandas as pd
import numpy as np


class VerticalLineModel(QAbstractTableModel):
    positionChanged = Signal(int)

    def __init__(self, startX, parent: QObject = None):
        super().__init__(parent)
        self.__currentX = startX
        self.__minY = -10000.0
        self.__maxY = 10000.0

    def currentX(self):
        return self.__currentX

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
        return self.__currentX


class MoveLineController(QObject):
    def __init__(self,
                 line1: VerticalLineModel,
                 line2: VerticalLineModel,
                 startPicket: float,
                 parent: QObject = None):
        super().__init__(parent)
        self.__line1 = line1
        self.__line2 = line2
        self.counter = 0
        self.step = 0.185
        self.startPicket = startPicket

    def eventFilter(self, direction: str, data_start: list = False, data_end: list = False, counter: int = False):
        if counter:
            self.counter = counter
        if direction == "to right":
            self.__line1.shiftLine(data_start[self.counter + 1] + self.startPicket)
            self.__line2.shiftLine(data_end[self.counter + 1] + self.startPicket)
            self.counter += 1
        elif direction == "to left":
            self.__line1.shiftLine(data_start[self.counter - 1] + self.startPicket)
            self.__line2.shiftLine(data_end[self.counter - 1] + self.startPicket)
            self.counter -= 1
        return False