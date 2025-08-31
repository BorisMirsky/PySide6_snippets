# This Python file uses the following encoding: utf-8
from ..units.AbstractUnit import AbstractReadUnit, AbstractReadWriteUnit
from ..dto.Markers import RailwayMarker, RailwayMarkerType
from ..dto.Travelling import LocationVector1D
from .AbstractMarkerModel import AbstractMarkerModel
from PySide6.QtCore import QObject
from typing import Optional, Dict

class RailwayMarkerPositionSyncronizer(QObject):
    def __init__(self,
    position_provider: AbstractReadWriteUnit[float],
    markers: AbstractMarkerModel, 
    parent: Optional[QObject] = None):
        super().__init__(parent)
        self.__position_provider: AbstractReadWriteUnit[float] = position_provider
        self.__markers: AbstractMarkerModel = markers

    def syncronizeByMarker(self, marker: RailwayMarker) ->None:
        if (current_position := self.__markers.positionAtMarker(marker)) is not None:
            self.__position_provider.write(current_position)
class RailwayMarkerPositionWriter(QObject):
    def __init__(self, position_provider: AbstractReadUnit[float], markers: AbstractMarkerModel, parent: Optional[QObject] = None) ->None:
        super().__init__(parent)
        self.__position_provider: AbstractReadUnit[float] = position_provider
        self.__markers: AbstractMarkerModel = markers
    def markerReceived(self, marker: RailwayMarker) ->None:
        self.__markers.insertMarkerAtPosition(marker = marker,
            position = LocationVector1D(meters = self.__position_provider.read()))
