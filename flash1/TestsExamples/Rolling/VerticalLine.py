from PySide6.QtCore import Qt, QObject, QAbstractTableModel, Signal, QModelIndex



class VerticalLineModel(QAbstractTableModel):
    positionChanged = Signal(int)
    def __init__(self, startX=5.0, minY=-50.0, maxY=50.0, parent: QObject = None):
        super().__init__(parent)
        self.__currentX = startX
        self.__minY = minY
        self.__maxY = maxY

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

    # Удержание полосы на месте
    def keep_line_position(self, pos:float):
        self.__currentX = pos
        self.dataChanged.emit(self.index(0, 0), self.index(1, 1), [Qt.ItemDataRole.DisplayRole])
        self.positionChanged.emit(self.__currentX)

# 
# class MoveLineController(QObject):
#     def __init__(self, minPosition: float, line: VerticalLineModel, parent: QObject = None):
#         super().__init__(parent)
#         self.minPosition = minPosition
#         self.__line = line
