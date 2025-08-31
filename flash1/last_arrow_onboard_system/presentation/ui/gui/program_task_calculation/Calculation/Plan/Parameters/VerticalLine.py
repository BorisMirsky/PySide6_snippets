from PySide6.QtCore import *
import math
import pandas as pd
import numpy as np
from domain.dto.Workflow import ProgramTaskCalculationResultDto
from domain.calculations.plan_model import TrackProjectModel, TrackProjectType
from domain.models import VerticalLineModel


class MoveLineController(QObject):
    def __init__(self,
                 line1: VerticalLineModel,
                 line2: VerticalLineModel,
                 line3: VerticalLineModel,
                 calculation_result,
                 parent: QObject = None):
        super().__init__(parent)
        self.__line1 = line1
        self.__line2 = line2
        self.__line3 = line3
        self.__calculation_result = calculation_result
        self.counter = 0
        self.step = 0.185
        self.summary = TrackProjectModel.create(TrackProjectType.Plan,
                                                self.__calculation_result)
        self.summary_len = len(self.summary.elements())
        self.startPicket = self.__calculation_result.options.start_picket.meters
        self.options: ProgramTaskCalculationResultDto = self.__calculation_result.options
        self.position_multiplyer = self.options.picket_direction.multiplier()
        self.summary_len = len(self.summary.elements())

    # picket_direction:int,
    def eventFilter1(self, direction:str, data_start: list = False, data_end: list = False, middlePoint: float = False):
        if direction == "to right":
            self.__line1.shiftLine(self.startPicket + self.position_multiplyer * data_start[self.counter + 1])
            self.__line2.shiftLine(self.startPicket + self.position_multiplyer * data_end[self.counter + 1])
            #print('MoveLineController to right',
            #          self.startPicket + data_start[self.counter + 1], self.startPicket + data_end[self.counter + 1])
            self.counter += 1
        elif direction == "to left":
            self.__line1.shiftLine(self.startPicket + self.position_multiplyer * data_start[self.counter - 1])
            self.__line2.shiftLine(self.startPicket + self.position_multiplyer * data_end[self.counter - 1])
            #print('MoveLineController to left',
            #      self.startPicket + data_start[self.counter + 1], self.startPicket + data_end[self.counter + 1])
            self.counter -= 1
        elif direction == "divide":
            if self.position_multiplyer == 1:
                self.__line3.shiftLine(middlePoint)
        elif direction == "hide":
            if self.position_multiplyer == 1:
                self.__line3.shiftLine(-10)
        return False

    def eventFilter(self, direction: str, data_start: list = False, data_end: list = False, middlePoint: float = False):
        if direction == "to right":
            if self.position_multiplyer == 1:
                self.__line1.shiftLine(self.startPicket + data_start[self.counter + 1])
                self.__line2.shiftLine(self.startPicket + data_end[self.counter + 1])
                self.counter += 1
            elif self.position_multiplyer == -1:
                self.__line1.shiftLine(self.startPicket - data_start[self.counter + 1])
                self.__line2.shiftLine(self.startPicket - data_end[self.counter + 1])
                self.counter += 1
        elif direction == "to left":
            if self.position_multiplyer == 1:
                self.__line1.shiftLine(self.startPicket + data_start[self.counter - 1])
                self.__line2.shiftLine(self.startPicket + data_end[self.counter - 1])
                self.counter -= 1
            elif self.position_multiplyer == -1:
                self.__line1.shiftLine(self.startPicket - data_start[self.counter - 1])
                self.__line2.shiftLine(self.startPicket - data_end[self.counter - 1])
                self.counter -= 1
        elif direction == "divide":
            if self.position_multiplyer == 1:
                self.__line3.shiftLine(middlePoint)
        elif direction == "hide":  # переделать
            if self.position_multiplyer == 1:
                self.__line3.shiftLine(-10)
        return False

