# This Python file uses the following encoding: utf-8
from PySide6.QtCore import QAbstractTableModel, QModelIndex, QObject, Qt
from typing import List, Any
import pandas


class DataframeTableModel(QAbstractTableModel):
    def __init__(self, columns: List[str], parent: QObject = None):
        super().__init__(parent)
        self.__data: pandas.DataFrame = pandas.DataFrame(columns=columns)

    def columnCount(self, parent: QModelIndex) ->int:
        return self.__data.shape[1]
    def rowCount(self, parent: QModelIndex) ->int:
        return self.__data.shape[0]
    def headerData(self, section: int, orientation: Qt.Orientation, role: int):
        if orientation == Qt.Orientation.Vertical:
            return super().headerData(section, orientation, role)
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        return self.__data.columns[section]
    def data(self, index: QModelIndex, role: int) ->Any:
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if not index.isValid():
            return None
        return str(self.__data.iloc[index.row(), index.column()])

    def indexAtHeader(self, headerName: str) ->int:
        return self.__data.columns.get_loc(headerName)
    def headerAtIndex(self, index: int) ->str:
        return self.__data.columns[index]
    def appendDataFrame(self, data: pandas.DataFrame):
        if data.shape[0] == 0:
            return

        remove_range = self.__data[self.__data['position'] >= data['position'][0]]
        if remove_range.shape[0] > 0:
            self.beginRemoveRows(QModelIndex(), self.__data.shape[0] - remove_range.shape[0], self.__data.shape[0] - 1)
            self.__data.drop(remove_range.index, inplace=True)
            self.endRemoveRows()

        self.beginInsertRows(QModelIndex(), self.__data.shape[0], self.__data.shape[0] + data.shape[0] - 1)
        #self.__data = pandas.concat([self.__data, data], ignore_index=True)
        self.__data = pandas.concat([self.__data.astype(data.dtypes), data.astype(self.__data.dtypes)], ignore_index=True)
        #
        self.endInsertRows()
        #Код на случай, если последние строки не надо удалять
        #if (self.__data.shape[0] == 0) or (data['distance_sensor'] > self.__data['distance_sensor'].iloc[-1]):
        #    self.beginInsertRows(QModelIndex(), self.rowCount(QModelIndex()), self.rowCount(QModelIndex()))
        #    self.__data.loc[len(self.__data.index)] = data
        #    self.endInsertRows()
        #elif data['distance_sensor'] == self.__data['distance_sensor'].iloc[-1]:
        #    self.__data.loc[len(self.__data.index) - 1] = data
        #    self.dataChanged.emit(self.index(self.__data.shape[0], 0), self.index(self.__data.shape[0], self.__data.shape[1]), [Qt.ItemDataRole.DisplayRole])
    def reset(self):
        self.beginResetModel()
        self.__data = pandas.DataFrame(columns=self.__data.columns)
        self.endResetModel()
    def resetWith(self, data: pandas.DataFrame):
        self.beginResetModel()
        self.__data = data
        self.endResetModel()
        print(self.__data)
    def dataframe(self) ->pandas.DataFrame:
        return self.__data

    def rowAtPosition(self, position: float):
        passed_range = self.__data[self.__data['position'] < position]
        if passed_range.shape[0] == 0:
            return None
        return passed_range.iloc[-1]
    def saveToCsv(self, filename: str):
        self.__data.to_csv(filename, sep=';', index=False)


