from domain.units.AbstractUnit import AbstractReadUnit, AbstractReadWriteUnit
from domain.dto.DiscreteSignals import DiscreteSignalsContainer
from typing import Optional, Callable
from PySide6.QtCore import QObject

class ConditionalServoValveUnit(AbstractReadWriteUnit[float]):
    def __init__(self, servo_valve_power: AbstractReadWriteUnit[float], discrete_signals: AbstractReadUnit[DiscreteSignalsContainer], predicate: Callable[[DiscreteSignalsContainer], bool], parent: Optional[QObject] = None) ->None:
        super().__init__(parent)
        self.__servo_valve_power: AbstractReadWriteUnit[float] = servo_valve_power
        self.__discrete_signals: AbstractReadUnit[DiscreteSignalsContainer] = discrete_signals
        self.__predicate: Callable[[DiscreteSignalsContainer], bool] = predicate

        self.__servo_valve_power.changed.connect(self.__write_target_value)
        self.__discrete_signals.changed.connect(self.__write_target_value)
        self.__target_power: float = 0.0
        self.write(0.0)
    def read(self) ->float:
        return self.__servo_valve_power.read()
    def write(self, value: float) ->None:
        self.__target_power = value
        self.__write_target_value()
    def __write_target_value(self) ->None:
        current_signals: DiscreteSignalsContainer = self.__discrete_signals.read()
        if not current_signals is None and self.__predicate(current_signals):
            self.__servo_valve_powerower.write(self.__target_power)
        else:
            self.__servo_valve_powerower.write(0.0)

def is_left_lifting_servo_valve_enabled(signals: DiscreteSignalsContainer) -> bool:
    return signals.enable_lifting_left
def is_right_lifting_servo_valve_enabled(signals: DiscreteSignalsContainer) -> bool:
    return signals.enable_lifting_left
def is_shifting_servo_valve_enabled(signals: DiscreteSignalsContainer) -> bool:
    return signals.enable_shifting
