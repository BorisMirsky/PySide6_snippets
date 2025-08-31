from .AbstractUnit import AbstractReadUnit, AbstractReadWriteUnit
from typing import Optional, Union, Dict, Set
from PySide6.QtCore import QObject
from domain.dto.Travelling import MovingDirection


class AbstractUnitProvider(QObject):
    def __init__(self, parent: Optional[QObject] = None) ->None:
        super().__init__(parent)

    def create_position_unit(self, direction: MovingDirection) ->AbstractReadWriteUnit[float]:
        pass
    
    def get_all_read_only_units(self) ->Dict[str, AbstractReadUnit]:
        pass
    def get_read_only_unit(self, name: str) ->AbstractReadUnit:
        return self.get_all_read_only_units().get(name)
    def get_read_only_names(self) ->Set[str]:
        return self.get_all_read_only_units().keys()

    def get_all_readwrite_units(self) ->Dict[str, AbstractReadWriteUnit]:
        pass
    def get_readwrite_unit(self, name: str) ->AbstractReadWriteUnit:
        return self.get_all_readwrite_units().get(name)
    def get_readwrite_names(self) ->Set[str]:
        return self.get_all_readwrite_units().keys()

