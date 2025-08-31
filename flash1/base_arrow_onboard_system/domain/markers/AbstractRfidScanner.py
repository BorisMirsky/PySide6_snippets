# This Python file uses the following encoding: utf-8
from PySide6.QtCore import QThread, QObject, Signal
from ..dto.Markers import RailwayMarker
from typing import Optional

class AbstractRfidScanner(QObject):
    tagReceived: Signal = Signal(RailwayMarker, float)
    def __init__(self, parent: Optional[QObject] = None) ->None:
        super().__init__(parent)
