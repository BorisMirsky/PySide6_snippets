from domain.dto.DiscreteSignals import DiscreteSignalsContainer
from domain.units.AbstractUnit import AbstractReadUnit
from PySide6.QtCore import QObject
from typing import Optional

class DiscreteSignalsUnit(AbstractReadUnit[DiscreteSignalsContainer]):
    def __init__(self, origin: AbstractReadUnit[int], parent: Optional[QObject] = None) ->None:
        super().__init__(parent)
        self.__discrete_signals: DiscreteSignalsContainer = None
        self.__origin: AbstractReadUnit[int] = origin
        self.__origin.changed.connect(self.__update_discrete_signals)
        self.__update_discrete_signals(self.__origin.read())
        
    def read(self) ->DiscreteSignalsContainer:
        return self.__discrete_signals
    def __update_discrete_signals(self, current_signals: int) ->None:
        if current_signals is None:
            self.__discrete_signals = None
        else:
            self.__discrete_signals = DiscreteSignalsContainer.from_code(current_signals)
        self.changed.emit(self.read())


