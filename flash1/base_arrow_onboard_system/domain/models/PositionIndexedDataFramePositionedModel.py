# This Python file uses the following encoding: utf-8
from PySide6.QtCore import Qt, QObject, QModelIndex, QPersistentModelIndex
from .AbstractPositionedTableModel import AbstractPositionedTableModel
from ..dto.Travelling import LocationVector1D
from typing import Optional, Union, List, Dict, Any
import pandas

# Временно замороженная модель
# Показала свою несостоятельность, т.к. точность float-ов на дне
#
# class PositionIndexedDataFramePositionedModel(AbstractPositionedTableModel):
#     def __init__(self, columns: List[str], step: Vector = None, parent: Optional[QObject] = None) ->None:
#         super().__init__(parent)
#         self.reset(step, pandas.DataFrame(columns = columns))
#     # ===========================================================================
#     def columnCount(self, parent: Union[QModelIndex, QPersistentModelIndex] = QModelIndex()) -> int:
#         return len(self.__storage.columns) + 1
#     def rowCount(self, parent: Union[QModelIndex, QPersistentModelIndex] = QModelIndex()) -> int:
#         return len(self.__storage)
#     def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
#         if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
#             return 'position' if section == 0 else self.__storage.columns[section - 1]

#         return None

#     def data(self, index: Union[QModelIndex, QPersistentModelIndex], role: int = Qt.ItemDataRole.DisplayRole) -> Any:
#         if not index.isValid() or role != Qt.ItemDataRole.DisplayRole:
#             return None
#         elif index.column() == 0:
#             return float(self.__storage.index[index.row()])
#         else:
#             return float(self.__storage.iloc[index.row(), index.column() - 1])
#     # ===========================================================================
#     def minmaxPosition(self) ->(Vector, Vector):
#         return (Vector(self.__storage.index.min()), Vector(self.__storage.index.max()))
#     def minmaxValueByColumn(self, column: str) ->(float, float):
#         return (self.__storage[column].min(), self.__storage[column].max())
#     def minmaxValueByIndex(self, index: int) ->(float, float):
#         return (self.__storage.iloc[:, index].min(), self.__storage.iloc[:, index].max())
#     # ===========================================================================
#     def step(self) ->Vector:
#         return self.__step
#     def valueColumns(self) ->List[str]:
#         return self.__storage.columns
#     def valueColumnCount(self) ->int:
#         return len(self.__storage.columns)
#     def modelColumnIndexAtName(self, name: str) ->int:
#         return 0 if name == 'position' else 1 + self.valueColumnIndexAtName(name)
#     def modelColumnNameAtIndex(self, index: int) ->str:
#         return 'position' if index == 0 else self.valueColumnNameAtIndex(index - 1)
#     def valueColumnIndexAtName(self, name: str) ->int:
#         return self.__storage.columns.get_loc(name)
#     def valueColumnNameAtIndex(self, index: int) ->str:
#         return self.__storage.columns[index]
#     def rowAtPosition(self, position: Vector) ->Dict[str, float]:
#         try:
#             return self.__storage.loc[self.roundedVector(position).meters]
#         except:
#             return None
#     def cellAtPosition(self, position: Vector, column: str) ->float:
#         try:
#             return self.rowAtPosition(position)[column]
#         except:
#             return None
#     # ===========================================================================
#     def __removeAfterPosition(self, position: float) ->None:
#         dataRemoveRange = self.__storage[self.__storage.index >= position]
#         if len(dataRemoveRange) != 0:
#             self.beginRemoveRows(QModelIndex(), len(self.__storage) - len(dataRemoveRange), len(self.__storage) - 1)
#             self.__storage.drop(dataRemoveRange.index, inplace=True)
#             self.endRemoveRows()
#     def __fillRowsByValues(self, rounded_position: float, values: Dict[str, float]) ->None:
#         if len(self.__storage) != 0:
#             values_from: Dict[str, float] = self.__storage.iloc[-1]
#             position_from: float = float(self.__storage.index[-1]) + self.__step.meters
#         else:
#             values_from: Dict[str, float] = values
#             position_from: float = 0.0

#         values_delta = { field: values[field] - values_from[field] for field in self.__storage.columns }
#         append_positions_space: List[float] = list(self.position_range(position_from, rounded_position, self.__step.meters))
#         self.beginInsertRows(QModelIndex(), len(self.__storage), len(self.__storage) + len(append_positions_space) - 1)
#         for position_index in range(len(append_positions_space)):
#             position_values = [values_from[field] + values_delta[field] * (position_index + 1) / len(append_positions_space) for field in self.__storage.columns]
#             self.__storage.loc[append_positions_space[position_index]] = position_values
#         self.endInsertRows()
#     def setRowAtPosition(self, position: Vector, values: Dict[str, float]) ->None:
#         rounded_position: float = self.roundedVector(position).meters
#         self.__removeAfterPosition(rounded_position)
#         self.__fillRowsByValues(rounded_position, values)
#     # ===========================================================================
#     def dataframe(self) ->pandas.DataFrame:
#         return self.__storage
#     def reset(self, step: Vector, data: pandas.DataFrame):
#         if 'position' not in data.columns:
#             raise Exception(f'DataframPositionedModel: "columns" field must have a "position" column: {self.__columns}')

#         self.beginResetModel()
#         self.__step = step
#         self.__storage = data
#         self.__storage.set_index('position', inplace = True)
#         self.endResetModel()







# Устраевшая модель
# Содержит пример разделения данных на два буфера. Может понадобиться
#
# class DynamicDataframeTableModel(QAbstractTableModel):
#     def __init__(self, origin: pandas.DataFrame, parent: Optional[QObject] = None) ->None:
#         super().__init__(parent)
#         self.reset(origin)

#     def columnCount(self, parent: Union[QModelIndex, QPersistentModelIndex] = QModelIndex()) -> int:
#         return len(self.__columns)
#     def rowCount(self, parent: Union[QModelIndex, QPersistentModelIndex] = QModelIndex()) -> int:
#         return len(self.__buffer) + len(self.__data)
#     def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
#         if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
#             return self.__columns[section]

#         return None

#     def data(self, index: Union[QModelIndex, QPersistentModelIndex], role: int = Qt.ItemDataRole.DisplayRole) -> Any:
#         if role != Qt.ItemDataRole.DisplayRole:
#             return None
#         if not index.isValid():
#             return None

#         if index.row() < len(self.__data):
#             return float(self.__data.iloc[index.row(), index.column()])
#         else:
#             return float(self.__buffer.iloc[index.row() - len(self.__data), index.column()])

#     def indexAtHeader(self, headerName: str) ->int:
#         return self.__columns.index(headerName)
#     def headerAtIndex(self, index: int) ->str:
#         return self.__columns[index]

#     # @execution_time_logger
#     def removeAfterPosition(self, dataFirstPosition: float) ->None:
#         if len(self.__data) != 0:
#             dataRemoveRange = self.__data[self.__data['position'] >= dataFirstPosition]
#             if len(dataRemoveRange) != 0:
#                 fromRow = len(self.__data) - len(dataRemoveRange)
#                 targetRow = len(self.__buffer) + len(self.__data) - 1
#                 self.beginRemoveRows(QModelIndex(), fromRow, targetRow)
#                 self.__buffer.drop(self.__buffer.index, inplace=True)
#                 self.__data.drop(dataRemoveRange.index, inplace=True)
#                 self.endRemoveRows()
#                 return
#         if len(self.__buffer) != 0:
#             bufferRemoveRange = self.__buffer[self.__buffer['position'] >= dataFirstPosition]
#             if len(bufferRemoveRange) != 0:
#                 self.beginRemoveRows(QModelIndex(), len(self.__buffer) - len(bufferRemoveRange), len(self.__buffer) - 1)
#                 self.__buffer.drop(bufferRemoveRange.index, inplace=True)
#                 self.endRemoveRows()

#     # @execution_time_logger
#     def appendDataFrame(self, data: pandas.DataFrame) ->None:
#         if len(data) == 0:
#             return
#         self.removeAfterPosition(data['position'][0])
#         self.beginInsertRows(QModelIndex(), len(self.__buffer) + len(self.__data), len(self.__buffer) + len(self.__data) + len(data) - 1)
#         self.__buffer = pandas.concat([self.__buffer, data], ignore_index=True)
#         if len(self.__buffer) >= 1000:
#             self.__data = pandas.concat([self.__data, self.__buffer], ignore_index=True)
#             self.__buffer.drop(self.__buffer.index, inplace=True)
#         self.endInsertRows()
#     def dataframe(self) ->pandas.DataFrame:
#         return pandas.concat([self.__data, self.__buffer], ignore_index=True)
#     def reset(self, data: pandas.DataFrame):
#         self.beginResetModel()
#         self.__columns = list(data.columns)
#         self.__buffer = pandas.DataFrame(columns = self.__columns)
#         self.__data = data
#         self.endResetModel()

#     def rowAtPosition(self, position: float, maximum_distance: float = 2):
#         buffer_position_range = self.__buffer[self.__buffer['position'] <= position]
#         if len(buffer_position_range) != 0:
#             if position - buffer_position_range.iloc[-1]['position'] > maximum_distance:
#                 return None
#             else:
#                 return buffer_position_range.iloc[-1]

#         data_position_range = self.__data[self.__data['position'] <= position]
#         if len(data_position_range) != 0:
#             if position - data_position_range.iloc[-1]['position'] > maximum_distance:
#                 return None
#             else:
#                 return data_position_range.iloc[-1]

#         return None

