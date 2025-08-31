from PySide6.QtCore import *




class VerticalLineModel(QAbstractTableModel):
    positionChanged = Signal(float)

    def __init__(self, startX=2, minY=-5, maxY=5, parent: QObject = None):
        super().__init__(parent)
        self.__currentX = startX
        self.__minY = minY
        self.__maxY = maxY
        self.__currentY = 0
        self.yDiff = 0.0
        self.myFlag = None

    def currentX(self):
        return self.__currentX

    def currentY(self):
        return round(self.__currentY, 2)

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

    def shiftLineX(self, xDiff: float):
        if xDiff == 0:
            return
        if self.__currentX <= 0 and xDiff < 0:
            return
        if self.__currentX >= 100 and xDiff > 0:
            return
        self.__currentX += xDiff
        self.dataChanged.emit(self.index(0, 0), self.index(1, 1), [Qt.ItemDataRole.DisplayRole])
        self.positionChanged.emit(self.__currentX)


    def shiftLineY(self, yDiff: float):
        if yDiff == 0:
            return
        if self.__currentY <= -10 and yDiff < 0:
            return
        if self.__currentY >= 10 and yDiff > 0:
            return
        if yDiff > 0:
            self.myFlag = True
        else:
            self.myFlag = False
        self.__currentY += yDiff
        self.dataChanged.emit(self.index(0, 0), self.index(1, 1), [Qt.ItemDataRole.DisplayRole])
        self.positionChanged.emit(round(self.__currentY, 3))


class MoveLineController(QObject):
    def __init__(self, line: VerticalLineModel, parent: QObject = None):
        super().__init__(parent)
        self.__line = line

    def eventFilter(self, watched: QObject, event: QEvent):
        if event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_D:
                self.__line.shiftLineX(1.0)
            elif event.key() == Qt.Key.Key_A:
                self.__line.shiftLineX(-1.0)
            elif event.key() == Qt.Key.Key_W:
                self.__line.shiftLineY(0.1)
                self.__line.yDiff = 0.1
            elif event.key() == Qt.Key.Key_X:
                self.__line.shiftLineY(-0.1)
                self.__line.yDiff = -0.1
        return False




