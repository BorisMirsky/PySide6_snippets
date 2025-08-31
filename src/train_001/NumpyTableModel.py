# This Python file uses the following encoding: utf-8
from PySide6.QtCore import QAbstractTableModel, QModelIndex, QObject, Qt
from typing import List, Any
import numpy

class NumpyTableModel(QAbstractTableModel):
    def __init__(self, data: numpy.array, parent: QObject = None):
        super().__init__(parent)
        self.__data: numpy.array = data

    def columnCount(self, parent: QModelIndex) ->int:
        return self.__data.shape[1]
    def rowCount(self, parent: QModelIndex) ->int:
        return self.__data.shape[0]
    def data(self, index: QModelIndex, role: int) ->Any:
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if not index.isValid():
            return None
        return str(self.__data[index.row()][index.column()])

    def appendRow(self, record: List[float]):
        self.beginInsertRows(QModelIndex(), self.rowCount(QModelIndex()), self.rowCount(QModelIndex()))
        self.__data = numpy.vstack([self.__data, record])
        self.endInsertRows()
