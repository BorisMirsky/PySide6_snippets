from PySide6.QtCore import Qt, Signal, QObject, QModelIndex, QAbstractTableModel
from PySide6.QtGui import QKeySequence


class HorizontalLineModel(QAbstractTableModel):
    positionChanged = Signal(int)
    def __init__(self, startY=False, startX=False, endX=False, parent: QObject = None):
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
        # print("newY ", newY)
        if newY == 0:
            return
        if float(self.__currentY) <= 0 and newY < 0:
            return
        self.__currentY = self.__currentY + newY
        self.dataChanged.emit(self.index(0, 0), self.index(1, 1), [Qt.ItemDataRole.DisplayRole])
        self.positionChanged.emit(self.__currentY)
        return self.__currentY
    
    def shiftStart(self, delta: float):
        if delta == 0:
            return
        self.__startX += delta
        self.dataChanged.emit(self.index(0, 0), self.index(1, 1), [Qt.ItemDataRole.DisplayRole])
        return self.__startX
    
    def shiftEnd(self, delta: float):
        if delta == 0:
            return
        self.__endX += delta
        self.dataChanged.emit(self.index(0, 0), self.index(1, 1), [Qt.ItemDataRole.DisplayRole])
        return self.__endX
    
    def shiftX(self, delta: float):
        if delta == 0:
            return
        self.__startX += delta
        self.__endX += delta
        self.dataChanged.emit(self.index(0, 0), self.index(1, 1), [Qt.ItemDataRole.DisplayRole])
        return self.__startX, self.__endX
    
    def shiftY(self, delta: float):
        # print("newY ", newY)
        if delta == 0:
            return
        self.__currentY += delta
        self.dataChanged.emit(self.index(0, 0), self.index(1, 1), [Qt.ItemDataRole.DisplayRole])
        self.positionChanged.emit(self.__currentY)
        return self.__currentY

