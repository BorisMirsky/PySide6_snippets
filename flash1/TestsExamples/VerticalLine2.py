from PySide6.QtCore import *
import math
import pandas as pd
import numpy as np



class VerticalLineModel(QAbstractTableModel):
    positionChanged = Signal(int)
    def __init__(self, startX=10.0, minY=-2.0, maxY=2.5, parent: QObject = None):
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

    # При ручном смещении
    def shiftLine(self, xDiff: float):
        if xDiff == 0:
            return
        if self.__currentX <= 0 and xDiff < 0:
            return
        self.__currentX += xDiff
        self.dataChanged.emit(self.index(0, 0), self.index(1, 1), [Qt.ItemDataRole.DisplayRole])
        self.positionChanged.emit(self.__currentX)


#minPos = 0.0
class MoveLineController(QObject):
    def __init__(self, minPosition: float, line: VerticalLineModel, filename: str, parent: QObject = None):
        super().__init__(parent)
        self.minPosition = minPosition
        self.__line = line
        self.filename = filename
        self.coord_value1 = None
        self.coord_index1 = None
        self.coord_value2 = None
        self.coord_index2 = None
        self.coord_value3 = None
        self.coord_index3 = None


    def read_csv_file(self, filename):
        df = pd.read_csv(filename)
        return df

    def get_csv_column(self, filename, column_name):
        df = self.read_csv_file(filename)
        column = df.loc[:, column_name]
        return column.tolist()

    # ручное перемещение отсечки
    def eventFilter(self, watched: QObject, event: QEvent):
        if event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_D:
                self.__line.shiftLine(1.0)
            elif event.key() == Qt.Key.Key_A:
                self.__line.shiftLine(-1.0)
    # Пересечение с метками
    # coord_value - значение метки, coord_OX - координата метки по ОХ
            coord_value1 = self.get_csv_column(self.filename, 'Rfid')[int(self.__line.currentX())]
            coord_OX1 = int(self.__line.currentX())
            if math.isnan(coord_value1):
                pass
            else:
                self.coord_value1 = coord_value1
                self.coord_OX1 = coord_OX1
            #
            coord_value2 = self.get_csv_column(self.filename, 'Label_picket')[int(self.__line.currentX())]
            coord_OX2 = int(self.__line.currentX())
            if math.isnan(coord_value2):
                pass
            else:
                self.coord_value2 = coord_value2
                self.coord_OX2 = coord_OX2
            #
            coord_value3 = self.get_csv_column(self.filename, 'Isso')[int(self.__line.currentX())]
            coord_OX3 = int(self.__line.currentX())
            if coord_value3 in ['nan', np.nan, ... ]:
                pass
            else:
                self.coord_value3 = coord_value3
                self.coord_OX3 = coord_OX3
        return False
