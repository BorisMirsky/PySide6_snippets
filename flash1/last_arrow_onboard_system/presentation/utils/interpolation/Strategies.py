# This Python file uses the following encoding: utf-8
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, Tuple
import numpy

class AbstractInterpolationStrategy(ABC):
    @abstractmethod
    def interpolateXtoY(self, x: float) ->float:
        pass
    @abstractmethod
    def interpolateYtoX(self, y: float) ->float:
        pass

@dataclass(frozen=True)
class LinearInterpolationStrategy(AbstractInterpolationStrategy):
    definitionArea: Tuple[float, float]
    valueArea: Tuple[float, float]
    def interpolateXtoY(self, x: float) ->float:
        return float(numpy.interp(x, self.definitionArea, self.valueArea))
    def interpolateYtoX(self, y: float) ->float:
        return float(numpy.interp(y, self.valueArea, self.definitionArea))

@dataclass(frozen=True)
class FunctionInterpolationStrategy(AbstractInterpolationStrategy):
    XtoYinterpolator: Callable[[float], float]
    YtoXinterpolator: Callable[[float], float]
    def interpolateXtoY(self, x: float) ->float:
        return float(self.XtoYinterpolator(x))
    def interpolateYtoX(self, y: float) ->float:
        return float(self.YtoXinterpolator(y))




