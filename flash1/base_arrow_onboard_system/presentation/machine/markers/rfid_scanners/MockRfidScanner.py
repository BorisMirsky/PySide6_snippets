# This Python file uses the following encoding: utf-8
from domain.dto.Markers import RailwayMarker, RailwayMarkerType, RailwayMarkerLocation
from domain.markers.AbstractRfidScanner import AbstractRfidScanner
from PySide6.QtCore import QThread, QObject
from typing import Optional


class MockRfidScanner(AbstractRfidScanner):
    def __init__(self, parent: Optional[QObject] = None) ->None:
        super().__init__(parent)

    def sendRfidTag(self, tag_id: bytes) ->None:
        self.tagReceived.emit(RailwayMarker(
            title = tag_id.decode('utf-8'),
            type = RailwayMarkerType.RfidTag,
            location =  RailwayMarkerLocation.Middle
        ), 100)

