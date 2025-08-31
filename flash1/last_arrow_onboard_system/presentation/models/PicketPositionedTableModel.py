# This Python file uses the following encoding: utf-8
from PySide6.QtCore import Qt, QObject, QIdentityProxyModel, QPersistentModelIndex, QModelIndex
from domain.dto.Travelling import PicketDirection, LocationVector1D
from typing import Optional, Union, Any, Tuple

class PicketPositionedTableModel(QIdentityProxyModel):
    def __init__(self, direction: PicketDirection, start_picket: float = 0.0, parent: Optional[QObject] = None) ->None:
        super().__init__(parent)
        self.__multiplier: float = 1 if direction == PicketDirection.Forward else -1
        self.__start_picket: float = start_picket

    def setStartPicket(self, start_picket: float = 0.0) ->float:
        self.beginResetModel()
        self.__start_picket = start_picket
        self.endResetModel()
        return self.__start_picket

    def startPicket(self) ->float:
        return self.__start_picket
    
    def picketDirection(self) ->PicketDirection:
        return PicketDirection.Forward if self.__multiplier == 1 else PicketDirection.Backward

    def data(self, proxyIndex: Union[QModelIndex, QPersistentModelIndex], role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        result = super().data(proxyIndex, role)
        if proxyIndex.column() == 0 and role == Qt.ItemDataRole.DisplayRole:
            return self.__start_picket + float(result) * self.__multiplier
        else:
            return result

    def getIndexByPicket(self, position: float) -> int:
        return int( (position - self.__start_picket) * self.__multiplier / self.sourceModel().step().meters )
    def getStepByPicket(self, position: float) -> int:
        return self.getIndexByPicket(position)
    
    def minmaxPosition(self) ->Tuple[float, float]:
        min_pos, max_pos = self.sourceModel().minmaxPosition()
        return (self.__start_picket + min_pos.meters * self.__multiplier, self.__start_picket + max_pos.meters * self.__multiplier)
