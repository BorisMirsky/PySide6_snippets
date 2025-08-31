from PySide6.QtCore import QAbstractTableModel, QPersistentModelIndex, QModelIndex, QObject, Qt, Signal
from typing import Optional, Union




# Модель вертикальной черты
class SingleLineModel(QAbstractTableModel):
    positionChanged = Signal(float)
    def __init__(self, startX: float = 0, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.__currentX: float = startX
        self.__minY = -100000
        self.__maxY = 100000
    def rowCount(self, parent):
        return 2
    def columnCount(self, parent):
        return 2
    def data(self, index: Union[QModelIndex, QPersistentModelIndex], role: int = Qt.ItemDataRole.DisplayRole):
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
            return None

    def position(self):
        return self.__currentX

    def setPosition(self, newX: float):
        if newX == self.__currentX:
            return
        self.__currentX = newX
        self.dataChanged.emit(self.index(0, 0), self.index(1, 1), [Qt.ItemDataRole.DisplayRole])
        self.positionChanged.emit(self.__currentX)
        return self.__currentX


