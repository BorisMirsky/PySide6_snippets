from domain.units.AbstractUnit import AbstractReadUnit, AbstractReadWriteUnit
from domain.units.AbstractUnitProvider import AbstractUnitProvider
from PySide6.QtCore import QObject
from typing import Dict, Optional
from domain.dto.Travelling import MovingDirection
from presentation.machine.units.DiscreteSignalsUnit import DiscreteSignalsUnit
from domain.dto.DiscreteSignals import DiscreteSignalsContainer
from presentation.machine.units.DistanceTravelledUnits import DistanceTravelledProvider
from presentation.machine.units.UIEventDelayUnit import TraceEventDispatcherQueueReceiver

class MockUnitProvider(AbstractUnitProvider):
    def __init__(self, sensors: Dict[str, AbstractReadUnit], controls: Dict[str, AbstractReadWriteUnit], parent: Optional[QObject] = None) ->None:
        super().__init__(parent)
        self.__controls = controls
        self.__sensors = sensors

        # self.__position_unit = DistanceTravelledProvider(MovingDirection.Forward, sensors['tick_counter'], 100)
        self.__ticks_per_meter = 100
        self.__discrete_signals_container: AbstractReadUnit[DiscreteSignalsContainer] = DiscreteSignalsUnit(self.__sensors['discrete_signals'])
        self.__event_dispatcher = TraceEventDispatcherQueueReceiver(100)

    def get_all_read_only_units(self) ->Dict[str, AbstractReadUnit]:
        return self.__sensors
    def get_all_readwrite_units(self) ->Dict[str, AbstractReadWriteUnit]:
        return self.__controls
    
    # def position_unit(self) ->AbstractReadUnit[float]:
    #     return self.__position_unit
    
    def discrete_signals_container(self) ->AbstractReadUnit[float]:
        return self.__discrete_signals_container

    def create_position_unit(self, direction: MovingDirection) ->AbstractReadWriteUnit[float]:
        return DistanceTravelledProvider(direction, self.__sensors['tick_counter'], self.__ticks_per_meter)
    
    def event_dispatcher(self):
        return self.__event_dispatcher