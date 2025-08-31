from PySide6.QtCore import *
from PySide6.QtGui import QKeySequence
import math
import pandas as pd
import numpy as np
#from ServiceInfo import *



class HorizontalLineModel(QAbstractTableModel):
    positionChanged = Signal(int)
    def __init__(self, startY=False, startX=False, endX=False, parent: QObject = None):   # startX=False, endX=False,
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
        #if 29.5 <= self.__currentY + newY <= 31.5:
        #if self.__currentY + newY == 30:
        #    print(self.__currentY + newY)
        self.__currentY = self.__currentY + newY
        self.dataChanged.emit(self.index(0, 0), self.index(1, 1), [Qt.ItemDataRole.DisplayRole])
        self.positionChanged.emit(self.__currentY)
        return self.__currentY

