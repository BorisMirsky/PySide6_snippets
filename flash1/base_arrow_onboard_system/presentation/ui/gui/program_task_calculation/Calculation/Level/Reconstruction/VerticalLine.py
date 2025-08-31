from PySide6.QtCore import *
from PySide6.QtGui import QKeySequence
import math
import pandas as pd
import numpy as np
from domain.dto.Workflow import ProgramTaskCalculationResultDto
from domain.calculations.plan_model import TrackProjectModel, TrackProjectType
from domain.dto.Workflow import ProgramTaskCalculationResultDto

class VerticalLineModel(QAbstractTableModel):
    positionChanged = Signal(int)
    def __init__(self, startX, parent: QObject = None):
        super().__init__(parent)
        self.__currentX = startX
        self.__minY = -10000.0
        self.__maxY = 10000.0

    def currentX(self):
        return  self.__currentX

    def rowCount(self, parent):
        return 2

    def columnCount(self, parent):
        return 2

    def data(self, index: QModelIndex, role: int):
        if not index.isValid():
            return None
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if index.column() == 0:
            return self.__currentX
        elif index.column() == 1 and index.row() == 0:
            return self.__minY
        elif index.column() == 1 and index.row() == 1:
            return self.__maxY
        else:
            return
        
    def shiftLine(self, newX: float):
        if newX == 0:
            return
        if float(self.__currentX) <= 0 and newX < 0:
            return
        self.__currentX = newX
        self.dataChanged.emit(self.index(0, 0), self.index(1, 1), [Qt.ItemDataRole.DisplayRole])
        self.positionChanged.emit(self.__currentX)
        return self.__currentX


class MoveLineController(QObject):
    def __init__(self,
                 line1: VerticalLineModel,
                 line2: VerticalLineModel,
                 startPicket: float,
                 calculation_result: ProgramTaskCalculationResultDto,
                 #state,
                 parent: QObject = None):
        super().__init__(parent)
        self.__line1 = line1
        self.__line2 = line2
        #self.__state = state
        self.__calculation_result = calculation_result
        self.counter = 0
        self.step = 0.185
        self.startPicket = startPicket
        self.summary = TrackProjectModel.create(TrackProjectType.Plan,
                                                self.__calculation_result)  # = plan_model
        self.summary_len = len(self.summary.elements())
        self.startPicket = self.__calculation_result.options.start_picket.meters
        self.options: ProgramTaskCalculationResultDto = self.__calculation_result.options
        self.position_multiplyer = self.options.picket_direction.multiplier()
        self.summary_len = len(self.summary.elements())

    def eventFilter(self, direction:str, data_start:list = False, data_end:list = False):
        if direction == "to right":
            if self.position_multiplyer == 1:
                self.__line1.shiftLine(self.startPicket + data_start[self.counter + 1])
                self.__line2.shiftLine(self.startPicket + data_end[self.counter + 1])
                self.counter += 1
            elif self.position_multiplyer == -1:
                self.__line1.shiftLine(self.startPicket - data_start[self.counter + 1])
                self.__line2.shiftLine(self.startPicket - data_end[self.counter + 1])
                self.counter += 1
            #print('from vertical line class, to right, counter ', self.position_multiplyer, self.counter)
        elif direction == "to left":
            if self.position_multiplyer == 1:
                self.__line1.shiftLine(self.startPicket + data_start[self.counter - 1])
                self.__line2.shiftLine(self.startPicket + data_end[self.counter - 1])
                self.counter -= 1
            elif self.position_multiplyer == -1:
                self.__line1.shiftLine(self.startPicket - data_start[self.counter - 1])
                self.__line2.shiftLine(self.startPicket - data_end[self.counter - 1])
                self.counter -= 1
            #print('from vertical line class, to left, counter ', self.position_multiplyer, self.counter)
        return False