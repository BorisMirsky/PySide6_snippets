import random
from PySide6.QtCore import QObject
from PySide6.QtWidgets import QApplication
from typing import Dict, Optional

from domain.units.AbstractUnit import AbstractReadUnit, AbstractReadWriteUnit
from domain.units.AbstractUnitProvider import AbstractUnitProvider
from domain.dto.Travelling import MovingDirection
from presentation.machine.units.DiscreteSignalsUnit import DiscreteSignalsUnit
from domain.dto.DiscreteSignals import DiscreteSignalsContainer
from presentation.machine.units.DistanceTravelledUnits import DistanceTravelledProvider
from presentation.machine.units.UIEventDelayUnit import TraceEventDispatcherQueueReceiver
from presentation.machine.units.StrelographUnit import StrelographUnit
from domain.units.MemoryBufferUnit import MemoryBufferUnit
from presentation.machine.units.mock.MockUnits import IntMockUnit, SinMockUnit, ConstantValueMockUnit, TickCounterMockProvider
from presentation.machine.units.DistanceTravelledUnits import TickCounterProvider, TickCounterProvider2
from presentation.utils.interpolation.Units import ReadInterpolationUnit
from presentation.utils.interpolation.Strategies import LinearInterpolationStrategy


class MockUnitProvider(AbstractUnitProvider):
    def __init__(self, config: dict, sensors: Dict[str, AbstractReadUnit] = None, controls: Dict[str, AbstractReadWriteUnit] = None, parent: Optional[QObject] = None) ->None:
        super().__init__(parent)
        self.__controls = controls if controls is not None else self.create_controls(config)
        self.__sensors = sensors if sensors is not None else self.create_sensors(config)

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
    
    def create_sensors(self, configuration: dict) -> dict:
        sensors = dict()
        for sensor_name, sensor_params in configuration['models']['sensors'].items():
            if sensor_name == 'tick_counter':
                # 1. Эмуляция движения:
                register = TickCounterMockProvider(25, ticks_direction=MovingDirection.Backward, parent=QApplication.instance())
                sensors[sensor_name] = TickCounterProvider(register, sensor_params['inverse'], register)
                # 2. Стоим на месте:
                # sensors[sensor_name] = ConstantValueMockUnit(value=100, parent=QApplication.instance())
            elif sensor_name == 'discrete_signals':
                # sensors[sensor_name] = ConstantValueMockUnit(value=0, parent=QApplication.instance())
                sensors[sensor_name] = IntMockUnit(bottom=0, top=117, parent=QApplication.instance())
            elif sensor_name == 'sagging_left':
                sensors[sensor_name] = ConstantValueMockUnit(value=-10, parent=QApplication.instance())
                # sensors[sensor_name] = IntMockUnit(bottom=-10, top=18, parent=QApplication.instance())
            elif sensor_name == 'sagging_right':
                # sensors[sensor_name] = IntMockUnit(bottom=-10, top=2, parent=QApplication.instance())
                sensors[sensor_name] = ConstantValueMockUnit(value=-10, parent=QApplication.instance())
            elif sensor_name == 'strelograph_work':
                mock_unit = ConstantValueMockUnit(value=357, parent=QApplication.instance())
                # sensors[sensor_name] = IntMockUnit(bottom=-12, top=17, parent=QApplication.instance())
                sensors[sensor_name] = StrelographUnit(origin=mock_unit, params=sensor_params, parent=QApplication.instance())
            elif sensor_name == 'pendulum_front':
                sensors[sensor_name] = ConstantValueMockUnit(value=20, parent=QApplication.instance())
                # sensors[sensor_name] = IntMockUnit(bottom=0, top=15, parent=QApplication.instance())
            elif sensor_name == 'pendulum_control':
                sensors[sensor_name] = ConstantValueMockUnit(value=-2, parent=QApplication.instance())
                # sensors[sensor_name] = IntMockUnit(bottom=0, top=10, parent=QApplication.instance())
            elif sensor_name == 'pendulum_work':
                mock_unit = ConstantValueMockUnit(value=0, parent=QApplication.instance())
                projection = ReadInterpolationUnit(mock_unit, LinearInterpolationStrategy(
                        (sensor_params['projection_range']['min'], sensor_params['projection_range']['max']),
                        (sensor_params['value_range']['min'], sensor_params['value_range']['max'])     ), 
                        inverse=sensor_params.get('inverse', False), 
                        parent=QApplication.instance())
                sensors[sensor_name] = projection
                # sensors[sensor_name] = ConstantValueMockUnit(value=30, parent=QApplication.instance())
                # sensors[sensor_name] = IntMockUnit(bottom=0, top=10, parent=QApplication.instance())
            elif sensor_name == 'satellite':
                sensors[sensor_name] = ConstantValueMockUnit(value=0)
                # sensors[sensor_name] = IntMockUnit(bottom=0, top=2, parent=QApplication.instance())
            else:
                sensors[sensor_name] = SinMockUnit(2, random.uniform(0.1, 0.2), 0.1)

        return sensors
    

    def create_controls(self, configuration: dict) -> dict:
        # sensors = dict()
        controls = dict()
        controls['enable_register'] = MemoryBufferUnit(1)

        for control_name, control_params in configuration['models']['controls'].items():
            controls[control_name] = MemoryBufferUnit(0.0)

        return controls