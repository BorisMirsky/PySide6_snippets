# This Python file uses the following encoding: utf-8
from dataclasses import dataclass
from enum import Enum
import pandas
import numpy as np

SLOTS_IF_SUPPORTED = dict(slots=True) if 'slots' in dataclass.__kwdefaults__ else {} # supported starting python 3.10

class BaseRail(Enum):
    Left = 0
    Right = 1

class RailPressType(Enum):
    Left = 0
    Right = 1

class MovingDirection(Enum):
    Forward = 1
    Backward = 2
    def multiplier(self) ->int:
        return 1 if (self == self.Forward) else -1
    def inverted(self):
        return self.Backward if (self == self.Forward) else self.Forward
    
class PicketDirection(Enum):
    Forward = 1
    Backward = 2
    def multiplier(self) ->int:
        return 1 if (self == self.Forward) else -1
    def inverted(self):
        return self.Backward if (self == self.Forward) else self.Forward


# @dataclass(frozen = True, slots = True)
@dataclass(frozen = True, **SLOTS_IF_SUPPORTED)
class LocationVector1D:
    meters: float

@dataclass(frozen=True)
class SteppedData:
    data: pandas.DataFrame
    step: LocationVector1D


class MeasuringTripReverseType(Enum):
    Nothing = 1
    ReverseSigns = 2
    ReverseOrder = 3
    ReverseFull = 4


@dataclass(frozen=True)
class ProgramTaskBaseData:
    measurements_processed: SteppedData
    detailed_restrictions: dict[str, np.ndarray]
    plan: pandas.DataFrame
    prof: pandas.DataFrame
    track_split_plan: pandas.DataFrame
    track_split_prof: pandas.DataFrame
    step: LocationVector1D
    alc_plan: pandas.DataFrame = None
    alc_level: pandas.DataFrame = None
    