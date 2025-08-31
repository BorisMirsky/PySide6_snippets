from PySide6.QtCore import *

from domain.dto.Workflow import ProgramTaskCalculationResultDto
from domain.calculations.plan_model import TrackProjectModel, TrackProjectType



class VerticalLineModel(QAbstractTableModel):
    positionChanged = Signal(int)
    def __init__(self, startX, rangeX:tuple[float, float] = (0, 100000), parent: QObject = None, accValue: bool = False):
        super().__init__(parent)
        self.__currentX = startX
        self.__minY = -100000.0
        self.__maxY = 100000.0
        self.__minX = rangeX[0]
        self.__maxX = rangeX[1]
        self.__accValue = accValue

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

        if self.__accValue:
            if self.__currentX + newX < self.__minX or self.__currentX + newX > self.__maxX:
                return
            self.__currentX = self.__currentX + newX
        else:
            if newX < self.__minX or newX > self.__maxX:
                return
            self.__currentX = newX
        self.dataChanged.emit(self.index(0, 0), self.index(1, 1), [Qt.ItemDataRole.DisplayRole])
        self.positionChanged.emit(self.__currentX)
        return  self.__currentX

