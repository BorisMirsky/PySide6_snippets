# This Python file uses the following encoding: utf-8
from PySide6.QtCore import QAbstractTableModel, QPersistentModelIndex, QModelIndex, QByteArray, QObject, Qt
from typing import TypeVar, Any, Dict, Union, Optional
from ..dto.Travelling import LocationVector1D
from ..dto.Markers import RailwayMarker
from typing import Dict, List, Tuple


class AbstractMarkerModel(QAbstractTableModel):
    def __init__(self, parent: Optional[QObject] = None) ->None:
        super().__init__(parent)
        self.__headers = ['position', 'title', 'type', 'location']
    def columnCount(self, parent: Union[QModelIndex, QPersistentModelIndex]) ->int:
        return 0 if parent.isValid() else 4
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if role != Qt.ItemDataRole.DisplayRole or orientation != Qt.Orientation.Horizontal:
            return super().headerData(section, orientation, role)
        
        return self.__headers[section] if section < len(self.__headers) else None
    # ==================================================
    def markers(self) ->List[Tuple[RailwayMarker, LocationVector1D]]:
        pass
    def positionAtMarker(self, marker: RailwayMarker) ->Optional[LocationVector1D]:
        pass
    def markerAtPosition(self, position: LocationVector1D, precision: LocationVector1D) ->Optional[RailwayMarker]:
        pass
    def nextMarkerFromPosition(self, position: LocationVector1D) ->Optional[RailwayMarker]:
        pass
    def prevMarkerFromPosition(self, position: LocationVector1D) ->Optional[RailwayMarker]:
        pass
    # ==================================================
    def insertMarkerAtPosition(self, marker: RailwayMarker, position: LocationVector1D) ->None:
        pass
    def removeMarker(self, marker: RailwayMarker) ->None:
        pass

