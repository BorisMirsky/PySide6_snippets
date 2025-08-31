# This Python file uses the following encoding: utf-8
from PySide6.QtCore import Qt, QObject, QModelIndex, QAbstractTableModel, QPersistentModelIndex
from domain.units.AbstractUnit import AbstractReadUnit, AbstractReadWriteUnit
from domain.dto.Travelling import LocationVector1D, PicketDirection
from typing import Optional, Union, List, Dict, Any
import pandas
import sys
from PySide6.QtWidgets import QApplication, QTableView, QHBoxLayout, QWidget
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QVXYModelMapper
from PySide6.QtGui import QStandardItemModel, QStandardItem
from presentation.ui.gui.common.viewes.TableDataChartsView import DynamicLineSeries, HorizontalChart

@dataclass(frozen=True)
class RemakeRailwaySpace:
    data: pandas.DataFrame
    step_size: LocationVector1D
    start_picket: LocationVector1D
    picket_direction: PicketDirection



class RemakeAbstractPositionedTableModel(QAbstractTableModel):
    def roundedVector(self, vector: LocationVector1D) ->LocationVector1D:
        step_meters: float = self.step().meters
        return LocationVector1D(round(vector.meters / step_meters) * step_meters)

    def reset(self, space: RemakeRailwaySpace) ->None:
        pass
    def space(self) ->RemakeRailwaySpace:
        pass

    def minmaxPosition(self) ->(LocationVector1D, LocationVector1D):
        pass
    def minmaxValueByColumn(self, column: str) ->(float, float):
        pass
    def minmaxValueByIndex(self, index: int) ->(float, float):
        pass

    def valueColumns(self) ->List[str]:
        pass
    def valueColumnCount(self) ->int:
        pass
    def valueColumnIndexAtName(self, name: str) ->int:
        pass
    def valueColumnNameAtIndex(self, index: int) ->str:
        pass

    def modelColumns(self) ->List[str]:
        return ['position'] + self.valueColumns()
    def modelColumnCount(self) ->int:
        return 1 + self.valueColumnCount()
    def modelColumnIndexAtName(self, name: str) ->int:
        return 0 if name == 'position' else 1 + self.valueColumnIndexAtName(name)
    def modelColumnNameAtIndex(self, index: int) ->str:
        return 'position' if index == 0 else self.valueColumnNameAtIndex(index - 1)

    def rowAtPosition(self, position: LocationVector1D) ->Dict[str, float]:
        pass
    def cellAtPosition(self, position: LocationVector1D, column: str) ->float:
        pass
    def setRowAtPosition(self, position: LocationVector1D, values: Dict[str, float]) ->None:
        pass



class RemakeStepIndexedDataFramePositionedModel(AbstractPositionedTableModel):
    def __init__(self, start_picket_unit: AbstractReadWriteUnit[LocationVector1D], picket_direction: PicketDirection, columns: List[str], step_size: LocationVector1D, parent: Optional[QObject] = None) ->None:
            super().__init__(parent)
            self.__start_picket_unit: AbstractReadWriteUnit[LocationVector1D] = start_picket_unit
            self.__storage: pandas.DataFrame = pandas.DataFrame(columns = columns)
            self.__picket_direction: PicketDirection = picket_direction
            self.__step_size: LocationVector1D = step_size
            
            self.__start_picket_unit.changed.connect(self.__on_start_picket_changed)
            self.__storage.index.name = 'step'
            
    def __on_start_picket_changed(self) ->None:
        self.dataChanged(self.index(0, 0), self.index(self.rowCount(), 0))
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
            return float(self.__start_picket_unit.read().meters + index.row() * self.__step.meters)
        else:
            return float(self.__storage.iloc[index.row(), index.column() - 1])
    # ===========================================================================

    def reset(self, space: RemakeRailwaySpace) ->None:
        if 'position' in space.stepped_space.data.columns:
            raise Exception(f'RemakeStepIndexedDataFramePositionedModel: "columns" field must not have a "position" column: {space.stepped_space.data.columns}')
        if space.stepped_space.data.index.name != 'step':
            raise Exception(f'RemakeStepIndexedDataFramePositionedModel: "index.name" field be a "step": {space.stepped_space.data.index.name}')
        if space.picket_direction != PicketDirection.Forward:
            raise Exception(f'RemakeStepIndexedDataFramePositionedModel: "picket_direction" field be a "Forward": {space.picket_direction}')
        if space.start_picket.meters != 0.0:
            raise Exception(f'RemakeStepIndexedDataFramePositionedModel: "start_picket" field be a "0": {space.start_picket.meters}')

        self.beginResetModel()
        self.__start_picket_unit.write(space.start_picket)
        self.__picket_direction = space.picket_direction
        self.__step_size = space.step_size
        self.__storage = space.data
        self.endResetModel()
    def space(self) ->RemakeRailwaySpace:
        return RemakeRailwaySpace(
            data = self.__storage,
            step_size = self.__step_size,
            start_picket = self.__start_picket_unit.read(),
            picket_direction = self.__picket_direction
        )

    # ===========================================================================
    def minmaxPosition(self) ->(LocationVector1D, LocationVector1D):
        current_picket: float = self.__start_picket_unit.read().meters
        return (
            LocationVector1D(meters = current_picket + self.__storage.index.min() * self.__step_size.meters), 
            LocationVector1D(meters = current_picket + self.__storage.index.max() * self.__step_size.meters)
        )
    def minmaxValueByColumn(self, column: str) ->(float, float):
        return self.minmaxValueByIndex(self.valueColumnIndexAtName(column))
    def minmaxValueByIndex(self, index: int) ->(float, float):
        return (self.__storage.iloc[:, index].min(), self.__storage.iloc[:, index].max())
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
        except:
            return None
    def cellAtPosition(self, position: LocationVector1D, column: str) ->float:
        return self.rowAtPosition(position)[column]
    def setRowAtPosition(self, position: LocationVector1D, values: Dict[str, float]) ->None:
        if len(self.__storage) == 0:
            self.beginInsertRows(QModelIndex(), 0, 0)
            self.__storage.iloc[self.__positionAsIndex(position)] = values
            self.endInsertRows()
        else:
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


if __name__ == '__main__':
    app = QApplication(sys.argv)

    model = QStandardItemModel()
    model.setColumnCount(4)

    model.setItem(0, 0, QStandardItem('4'))
    model.setItem(0, 1, QStandardItem('43'))

    model.setItem(1, 0, QStandardItem('66'))
    model.setItem(1, 1, QStandardItem('12'))

    model.setItem(2, 0, QStandardItem('77'))
    model.setItem(2, 1, QStandardItem('42'))
    print(model.rowCount())


    series_1 = DynamicLineSeries(model, 0, 1, 'test-1')
    series_2 = DynamicLineSeries(model, 0, 2, 'test-2')
    series_3 = DynamicLineSeries(model, 0, 3, 'test-3')
    chart = HorizontalChart([series_1, series_2, series_3], (0, 100), False, (-50, 50), False)

    chart_view = QChartView(chart)
    table_view = QTableView()
    table_view.setModel(model)

    window = QWidget()
    layout = QHBoxLayout()
    window.setLayout(layout)
    layout.addWidget(table_view)
    layout.addWidget(chart_view)
    window.show()

    sys.exit(app.exec())

