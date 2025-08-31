# This Python file uses the following encoding: utf-8
from dataclasses import dataclass
from enum import Enum

class RailwayMarkerLocation(Enum):
    Left = -1
    Middle = 0
    Right = 1
class RailwayMarkerType(Enum):
    UNDEFINED = 0,
    RfidTag = 10,
    ContactNetwork = 20,
    # Platform
    Platform = 30,
    # Tunnel
    Tunnel = 40,
    # Arrow
    ArrowPointer = 50,
    ArrowCross = 51
    # Additional
    StationaryBrakeStop = 100,
    CrossPipe = 101,
    Miscellaneous = 200
    

@dataclass(frozen = True, slots = True)
class RailwayMarker:
    title: str
    type: RailwayMarkerType
    location: RailwayMarkerLocation


