from domain.units.AbstractUnit import AbstractReadUnit
from presentation.utils.interpolation.Strategies import LinearInterpolationStrategy
from domain.dto.Travelling import RailPressType
from PySide6.QtCore import QObject
from typing import Optional

class StrelographUnit(AbstractReadUnit[int]):
    def __init__(self, origin: AbstractReadUnit[int], params: dict, parent: Optional[QObject] = None):
        super().__init__(parent)

        self.__origin: AbstractReadUnit[int] = origin
        self.__origin.changed.connect(self.__onOriginValueChanged)
        self.__multiplyer = -1 if params.get('inverse', False) else 1
        self.__value = None
        self.__interpolation = None

        delta = params.get('right_press_delta', 0) * self.__multiplyer
        self.__left_interpolation = LinearInterpolationStrategy(
                                        definitionArea = (params['projection_range']['min'], params['projection_range']['max']),
                                        valueArea = (params['value_range']['min'], params['value_range']['max']) )
        self.__right_interpolation = LinearInterpolationStrategy(
                                        definitionArea = (params['projection_range']['min'], params['projection_range']['max']),
                                        valueArea = (params['value_range']['min'] + delta, params['value_range']['max'] + delta) )
        self.set_press_type(RailPressType.Left)

    def read(self) ->int:
        return self.__value
    
    def __onOriginValueChanged(self):
        self.__value = self.__multiplyer * self.__interpolation.interpolateXtoY(self.__origin.read())
        self.changed.emit(self.__value)
    
    def set_press_type(self, rail_press: RailPressType) ->None:
        self.__interpolation = self.__left_interpolation if rail_press == RailPressType.Left else self.__right_interpolation
