from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtCharts import *
import pandas as pd



#----------------------------------------------------------------------------
# Для получения длины графика
def read_csv_file( file, n):
    try:
        df = pd.read_csv(file)
        col = df.iloc[:, n]
        return col.values.tolist()
    except FileNotFoundError:
        pass

DATAFILE = "example_csv_file.csv"

LENGTH_OF_CHART = len(read_csv_file(DATAFILE, 0))
#----------------------------------------------------------------------------

# Модель вертикальной черты
class VerticalLineModel(QAbstractTableModel):
    positionChanged = Signal(int) #float)
    def __init__(self, startX=20, minY=-200, maxY=200, parent: QObject = None):
        super().__init__(parent)
        self.__currentX = startX
        self.__minY = minY
        self.__maxY = maxY

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

    def moveLine(self, xDiff: float):
        if self.__currentX <= 0 and xDiff < 0:
            return
        if self.__currentX >= LENGTH_OF_CHART and xDiff > 0:             
            return
        self.__currentX += xDiff
        self.dataChanged.emit(self.index(0, 0), self.index(1, 1), [Qt.ItemDataRole.DisplayRole])
        self.positionChanged.emit(self.__currentX)


# управление вертикальной чертой
class MoveLineController(QObject):
    def __init__(self, line: VerticalLineModel, parent: QObject = None):
        super().__init__(parent)
        self.__line = line

    def eventFilter(self, watched: QObject, event: QEvent):
        if event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_D:
                self.__line.moveLine(1)
            if event.key() == Qt.Key.Key_A:
                self.__line.moveLine(-1)
        #if event.type() == QEvent.Type.
        return False

