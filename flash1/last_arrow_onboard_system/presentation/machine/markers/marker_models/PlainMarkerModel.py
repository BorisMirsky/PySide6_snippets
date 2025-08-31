# This Python file uses the following encoding: utf-8
from PySide6.QtCore import QAbstractTableModel, QPersistentModelIndex, QModelIndex, QObject, Qt
from typing import TypeVar, Generic, Any, Union, Optional
from domain.markers.AbstractMarkerModel import AbstractMarkerModel
from domain.dto.Markers import AbstractRailwayMarker
from domain.dto.Travelling import LocationVector1D
import pandas


# PlainMarkerType = TypeVar('PlainMarkerGenericType')
# class PlainMarkerModel(AbstractMarkerModel, Generic[PlainMarkerType]):
#     def __init__(self, parent: Optional[QObject] = None) ->None:
#         super().__init__(parent)
#         self.__data: pandas.DataFrame = pandas.DataFrame(columns = ['position', 'description'], index = 'position')

#     # ==================================================
#     def markerAtPosition(self, position: Vector, precision: Vector) ->Optional[PlainMarkerType]:
#         pass
#     def nextMarkerFromPosition(self, position: Vector, precision: Vector) ->Optional[PlainMarkerType]:
#         pass
#     def prevMarkerFromPosition(self, position: Vector, precision: Vector) ->Optional[PlainMarkerType]:
#         pass
#     # ==================================================
#     def insertMarkerAtPosition(self, position: Vector, precision: Vector) ->None:
#         pass
#     def removeMarkerAtPosition(self, position: Vector, precision: Vector) ->None:
#         pass
