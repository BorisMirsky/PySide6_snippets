from PySide6.QtCore import *
from PySide6.QtGui import QKeySequence
import math
import pandas as pd
import numpy as np
#from ServiceInfo import *


class GorizontalLineModel(QAbstractTableModel):
    positionChanged = Signal(int)

    def __init__(self, startX, endX, startY, parent: QObject = None):
        super().__init__(parent)
        self.__startX = startX
        self.__endX = endX
        self.__currentY = startY

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

    # Удержание полосы на месте
    # def keep_line_position(self, pos:float):
    #     self.__currentX = pos
    #     self.dataChanged.emit(self.index(0, 0), self.index(1, 1), [Qt.ItemDataRole.DisplayRole])
    #     self.positionChanged.emit(self.__currentX)



#
# class MoveGorizontalLineController(QObject):
#     def __init__(self, minPosition: float,
#                  line: GorizontalLineModel,
#                  parent: QObject = None):
#         super().__init__(parent)
#         self.minPosition = minPosition
#         self.__line = line
#         self.counter = 0
#
#
#     def eventFilter(self, watched: QObject, event: QEvent):
#         if event.type() == QEvent.Type.KeyPress:
#             if event.key() == Qt.Key.Key_W:
#                 self.__line.shiftLine(1)
#             elif event.key() == Qt.Key.Key_S:
#                 self.__line.shiftLine(-1)
#             elif event.key() == (Qt.Key.Key_D and Qt.Key.Key_Control):
#                 pass
#                 # print('self.__line1.currentX() ', self.__line1.currentX())
#         return False
#






