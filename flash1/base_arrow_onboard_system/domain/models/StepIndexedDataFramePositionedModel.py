# This Python file uses the following encoding: utf-8
from PySide6.QtCore import Qt, QObject, QModelIndex, QPersistentModelIndex
from .AbstractPositionedTableModel import AbstractPositionedTableModel, AbstractPositionedReadTableModel
from ..dto.Travelling import LocationVector1D
from typing import Optional, Union, List, Dict, Any, Tuple
import pandas
import numpy as np

class StepIndexedDataFramePositionedModel(AbstractPositionedTableModel):
    def __init__(self, columns: List[str], step: LocationVector1D = None, parent: Optional[QObject] = None) ->None:
        super().__init__(parent)
        self.__storage: pandas.DataFrame = None
        self.__step: LocationVector1D = None
        data = pandas.DataFrame(columns = columns)
        data.index.name = 'step'
        self.reset(step, data)

    # ===========================================================================
    def columnCount(self, parent: Union[QModelIndex, QPersistentModelIndex] = QModelIndex()) -> int:
        return self.modelColumnCount()
    def rowCount(self, parent: Union[QModelIndex, QPersistentModelIndex] = QModelIndex()) -> int:
        return len(self.__storage)
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return 'position' if section == 0 else self.__storage.columns[section - 1]
    def data(self, index: Union[QModelIndex, QPersistentModelIndex], role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole:
            return None
        elif index.column() == 0:
            return float(index.row() * self.__step.meters)
        else:
            return float(self.__storage.iloc[index.row(), index.column() - 1])
    # ===========================================================================
    def step(self) ->LocationVector1D:
        return self.__step
    def dataframe(self) ->pandas.DataFrame:
        return self.__storage
    def reset(self, step: LocationVector1D, data: pandas.DataFrame):
        if 'position' in data.columns:
            raise Exception(f'DataframPositionedModel: "columns" field must not have a "position" column: {self.__columns}')
        if data.index.name != 'step':
            raise Exception(f'DataframPositionedModel: "index.name" field be a "step": {data.index.name}')

        self.beginResetModel()
        self.__storage = data
        self.__step = step
        self.endResetModel()

    # ===========================================================================
    def minmaxPosition(self) ->Tuple[LocationVector1D, LocationVector1D]:
        return (LocationVector1D(self.__storage.index.min() * self.__step.meters), LocationVector1D(self.__storage.index.max() * self.__step.meters))

    def minmaxValueByColumn(self, column: str) ->Tuple[float, float]:
        return self.minmaxValueByIndex(self.valueColumnIndexAtName(column))
    def minmaxValueByIndex(self, index: int) ->Tuple[float, float]:
        return (self.__storage.iloc[:, index].min(), self.__storage.iloc[:, index].max())

    # =========================================================================
    def minmaxValueByColumnInRange(self, column: str, start_step: int, end_step: int) ->Tuple[float, float]:
        return self.minmaxValueByIndexInRange(self.valueColumnIndexAtName(column), start_step, end_step)
    def minmaxValueByIndexInRange(self, index: int, start_step: int, end_step: int) ->Tuple[float, float]:
        return(self.__storage.iloc[start_step:end_step, index].min(), self.__storage.iloc[start_step:end_step, index].max())

    # ===========================================================================
    def valueColumns(self) ->List[str]:
        return self.__storage.columns
    def valueColumnCount(self) ->int:
        return len(self.__storage.columns)
    def valueColumnIndexAtName(self, name: str) ->int:
        return self.__storage.columns.get_loc(name)
    def valueColumnNameAtIndex(self, index: int) ->str:
        return self.__storage.columns[index]

    def rowAtPosition(self, position: LocationVector1D) ->Dict[str, float]:
        try:
            return self.__storage.iloc[self.__positionAsIndex(position)]
        except:  # noqa: E722
            return None
    def cellAtPosition(self, position: LocationVector1D, column: str) ->float:
        return self.rowAtPosition(position)[column]
    def setRowAtPosition(self, position: LocationVector1D, values: Dict[str, float]) ->None:
        step: int = self.__positionAsIndex(position)
        self.__removeAfterPosition(step)
        self.__fillRowsByValues(step, values)
        pass
    # ===========================================================================
    def __positionAsIndex(self, position: LocationVector1D) ->int:
        return int(round(position.meters / self.__step.meters, 0))
    def __removeAfterPosition(self, step_to: int) ->None:
        dataRemoveRange = self.__storage[self.__storage.index >= step_to]
        if len(dataRemoveRange) != 0:
            self.beginRemoveRows(QModelIndex(), len(self.__storage) - len(dataRemoveRange), len(self.__storage) - 1)
            self.__storage.drop(dataRemoveRange.index, inplace=True)
            self.endRemoveRows()
    def __fillRowsByValues(self, step_to: int, values: Dict[str, float]) ->None:
        if len(self.__storage) != 0:
            values_from: Dict[str, float] = self.__storage.iloc[-1]
            step_from: int = self.__storage.index[-1] + 1
        else:
            values_from: Dict[str, float] = values
            step_from: int = 0

        values_delta = { field: values[field] - values_from[field] for field in self.__storage.columns }
        append_steps_space: List[int] = list(range(step_from, step_to + 1))
        self.beginInsertRows(QModelIndex(), len(self.__storage), len(self.__storage) + len(append_steps_space) - 1)
        for position_index in range(len(append_steps_space)):
            insertion_values = [values_from[field] + values_delta[field] * (position_index + 1) / len(append_steps_space) for field in self.__storage.columns]
            self.__storage.loc[append_steps_space[position_index]] = insertion_values
        self.endInsertRows()
    # ===========================================================================


class ReducedStepIndexedPositionedModel(AbstractPositionedReadTableModel):
    def __init__(self, data: pandas.DataFrame, step: LocationVector1D, skip_coefficient: float = 0.002, parent: Optional[QObject] = None) ->None:
        super().__init__(parent)
        # self.__storage: pandas.DataFrame = None        
        total_steps = data.shape[0]
        skip_steps = round(skip_coefficient * total_steps)
        remain_indexes = np.array([i for i in np.array(range(total_steps)) if i % skip_steps == 0])
        reduced_data = data.iloc[remain_indexes]
        reduced_data.reset_index(drop=True, inplace=True)
        reduced_data.index.name = 'step'
        
        self.__storage = reduced_data
        self.__step: LocationVector1D = LocationVector1D(skip_steps * step.meters)

    # ===========================================================================
    def columnCount(self, parent: Union[QModelIndex, QPersistentModelIndex] = QModelIndex()) -> int:
        return self.modelColumnCount()
    def rowCount(self, parent: Union[QModelIndex, QPersistentModelIndex] = QModelIndex()) -> int:
        return len(self.__storage)
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return 'position' if section == 0 else self.__storage.columns[section - 1]
    def data(self, index: Union[QModelIndex, QPersistentModelIndex], role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole:
            return None
        elif index.column() == 0:
            return float(index.row() * self.__step.meters)
        else:
            return float(self.__storage.iloc[index.row(), index.column() - 1])
    # ===========================================================================
    def step(self) ->LocationVector1D:
        return self.__step
    def dataframe(self) ->pandas.DataFrame:
        return self.__storage
    def reset(self, step: LocationVector1D, data: pandas.DataFrame):
        if 'position' in data.columns:
            raise Exception(f'DataframPositionedModel: "columns" field must not have a "position" column: {self.__columns}')
        if data.index.name != 'step':
            raise Exception(f'DataframPositionedModel: "index.name" field be a "step": {data.index.name}')

        self.beginResetModel()
        self.__storage = data
        self.__step = step
        self.endResetModel()

    # ===========================================================================
    def minmaxPosition(self) ->Tuple[LocationVector1D, LocationVector1D]:
        return (LocationVector1D(self.__storage.index.min() * self.__step.meters), LocationVector1D(self.__storage.index.max() * self.__step.meters))

    def minmaxValueByColumn(self, column: str) ->Tuple[float, float]:
        return self.minmaxValueByIndex(self.valueColumnIndexAtName(column))
    def minmaxValueByIndex(self, index: int) ->Tuple[float, float]:
        return (self.__storage.iloc[:, index].min(), self.__storage.iloc[:, index].max())

    # =========================================================================
    def minmaxValueByColumnInRange(self, column: str, start_step: int, end_step: int) ->Tuple[float, float]:
        return self.minmaxValueByIndexInRange(self.valueColumnIndexAtName(column), start_step, end_step)
    def minmaxValueByIndexInRange(self, index: int, start_step: int, end_step: int) ->Tuple[float, float]:
        return(self.__storage.iloc[start_step:end_step, index].min(), self.__storage.iloc[start_step:end_step, index].max())

    # ===========================================================================
    def valueColumns(self) ->List[str]:
        return self.__storage.columns
    def valueColumnCount(self) ->int:
        return len(self.__storage.columns)
    def valueColumnIndexAtName(self, name: str) ->int:
        return self.__storage.columns.get_loc(name)
    def valueColumnNameAtIndex(self, index: int) ->str:
        return self.__storage.columns[index]

    def rowAtPosition(self, position: LocationVector1D) ->Dict[str, float]:
        try:
            return self.__storage.iloc[self.__positionAsIndex(position)]
        except:  # noqa: E722
            return None
    def cellAtPosition(self, position: LocationVector1D, column: str) ->float:
        return self.rowAtPosition(position)[column]
    def setRowAtPosition(self, position: LocationVector1D, values: Dict[str, float]) ->None:
        step: int = self.__positionAsIndex(position)
        self.__removeAfterPosition(step)
        self.__fillRowsByValues(step, values)
        pass
    # ===========================================================================
    def __positionAsIndex(self, position: LocationVector1D) ->int:
        return int(round(position.meters / self.__step.meters, 0))
    def __removeAfterPosition(self, step_to: int) ->None:
        dataRemoveRange = self.__storage[self.__storage.index >= step_to]
        if len(dataRemoveRange) != 0:
            self.beginRemoveRows(QModelIndex(), len(self.__storage) - len(dataRemoveRange), len(self.__storage) - 1)
            self.__storage.drop(dataRemoveRange.index, inplace=True)
            self.endRemoveRows()
    def __fillRowsByValues(self, step_to: int, values: Dict[str, float]) ->None:
        if len(self.__storage) != 0:
            values_from: Dict[str, float] = self.__storage.iloc[-1]
            step_from: int = self.__storage.index[-1] + 1
        else:
            values_from: Dict[str, float] = values
            step_from: int = 0

        values_delta = { field: values[field] - values_from[field] for field in self.__storage.columns }
        append_steps_space: List[int] = list(range(step_from, step_to + 1))
        self.beginInsertRows(QModelIndex(), len(self.__storage), len(self.__storage) + len(append_steps_space) - 1)
        for position_index in range(len(append_steps_space)):
            insertion_values = [values_from[field] + values_delta[field] * (position_index + 1) / len(append_steps_space) for field in self.__storage.columns]
            self.__storage.loc[append_steps_space[position_index]] = insertion_values
        self.endInsertRows()
    # ===========================================================================
