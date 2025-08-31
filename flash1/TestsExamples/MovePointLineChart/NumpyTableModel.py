# This Python file uses the following encoding: utf-8
from PySide6.QtCore import QAbstractTableModel, QModelIndex, QObject, Qt
from typing import List, Any
import numpy
import pandas as pd



class NumpyTableModel(QAbstractTableModel):
    def __init__(self, data: numpy.array, parent: QObject = None):
        super().__init__(parent)
        self.__data: numpy.array = data

    def columnCount(self, parent: QModelIndex) -> int:
        return self.__data.shape[1]

    def rowCount(self, parent: QModelIndex) -> int:
        return self.__data.shape[0]

    def data(self, index: QModelIndex, role: int) -> Any:
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if not index.isValid():
            return None
        return str(self.__data[index.row()][index.column()])

    def appendRow(self, record: List[float]):
        self.beginInsertRows(QModelIndex(), self.rowCount(QModelIndex()), self.rowCount(QModelIndex()))
        self.__data = numpy.vstack([self.__data, record])
        self.endInsertRows()

    # Удаление всех данных.
    def removeRows(self, position, rows, parent=QModelIndex()):
        start, end = position, rows
        self.beginRemoveRows(parent, start, end)
        self.__data = numpy.delete(self.__data, [x for x in range(start,end)], axis=0)
        self.endRemoveRows()
        return True

    # Вставка данных.
    def insertRows(self, rows: List[float], parent=QModelIndex()):
        start, end = 0, rows
        self.beginInsertRows(parent, start, len(rows))
        self.__data = numpy.append(self.__data, rows, axis=0)
        self.endInsertRows()


    # previous variant
    def insertRows1(self, shift, rows: List[float], parent=QModelIndex()):
        start, end = 0, rows
        rows = [[i[0], (i[1] + shift)] for i in rows]    # добавляем смещение на каждом шаге
        self.beginInsertRows(parent, start, len(rows))
        self.__data = numpy.append(self.__data, rows, axis=0)
        self.endInsertRows()
