from ..dto.Markers import RailwayMarker, RailwayMarkerType
from ..dto.Travelling import LocationVector1D
from .AbstractMarkerModel import AbstractMarkerModel
from PySide6.QtCore import QPersistentModelIndex, QModelIndex, QObject, Qt
from typing import Optional, Union, Dict, List, Tuple, Any

class BaseRailwayMarkerModel(AbstractMarkerModel):
    def __init__(self, parent: Optional[QObject] = None) ->None:
        super().__init__(parent)
        self.__storage: List[Tuple[RailwayMarker, LocationVector1D]] = []

    def rowCount(self, parent: Union[QModelIndex, QPersistentModelIndex] = QModelIndex()) -> int:
        return len(self.__storage)
    def data(self, index: Union[QModelIndex, QPersistentModelIndex], role: int = Qt.ItemDataRole.DisplayRole) ->Any:
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole:
            return None
        match index.column():
            case 0:
                return self.__storage[index.row()][1].meters
            case 1:
                return self.__storage[index.row()][0].title
            case 2:
                return self.__storage[index.row()][0].type
            case 3:
                return self.__storage[index.row()][0].location
            case _:
                return None
                
    # ==================================================
    def markers(self) ->List[Tuple[RailwayMarker, LocationVector1D]]:
        return self.__storage
    def positionAtMarker(self, marker: RailwayMarker) ->Optional[LocationVector1D]:
        for position, search_marker in self.__storage:
            if search_marker == marker:
                return position
    def markerAtPosition(self, position: LocationVector1D, precision: LocationVector1D) ->Optional[RailwayMarker]:
        result_marker: Tuple[RailwayMarker, float] = None
        for search_position, search_marker in storage:
            disance: float = abs(search_position.meters - position.meters)
            if disance < precision.meters:
                if result_marker is None or result_marker[1] > disance:
                    result_marker = (search_marker, disance)

        return result_marker[0]
    # ==================================================
    def nextMarkerFromPosition(self, position: LocationVector1D) ->Optional[RailwayMarker]:
        result_marker: Tuple[RailwayMarker, float] = None
        for marker_position, marker in self.__storage:
            if marker_position.meters < position.meters:
                distance: float = abs(marker_position.meters - position.meters)
                if distance < result_marker[1]:
                    result_marker = (marker, disance)
                    
        return result_marker[0]
    def prevMarkerFromPosition(self, position: LocationVector1D) ->Optional[RailwayMarker]:
        result_marker: Tuple[RailwayMarker, float] = None
        for marker_position, marker in self.__storage:
            if marker_position.meters > position.meters:
                distance: float = abs(marker_position.meters - position.meters)
                if distance < result_marker[1]:
                    result_marker = (marker, disance)
                    
        return result_marker[0]
    # ==================================================
    def insertMarkerAtPosition(self, marker: RailwayMarker, position: LocationVector1D) ->None:
        print(f'BaseRailwayMarkerModel.insertMarkerAtPosition: [{position}/{marker}]')
        self.beginInsertRows(QModelIndex(), len(self.__storage), len(self.__storage))
        self.__storage.append((marker, position))
        self.endInsertRows()
    def removeMarker(self, marker: RailwayMarker) ->None:
        target_index = -1
        for index, (position, search_marker) in enumerate(self.__storage):
            if search_marker == marker:
                target_index = index
                break
        
        if target_index == -1:
            return

        self.beginRemoveRows(QModelIndex(), target_index, target_index)
        del self.__storage[target_index]
        self.endInsertRows()
        