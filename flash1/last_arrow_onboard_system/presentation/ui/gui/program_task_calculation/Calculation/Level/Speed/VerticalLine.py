from PySide6.QtCore import *
from PySide6.QtGui import QKeySequence
import math
import pandas as pd
import numpy as np
from domain.models import VerticalLineModel


class MoveLineController(QObject):
    def __init__(self,
                 line1: VerticalLineModel,
                 line2: VerticalLineModel,
                 startPicket: float,
                 parent: QObject = None):
        super().__init__(parent)
        self.__line1 = line1
        self.__line2 = line2
        self.counter = 0
        self.step = 0.185
        self.startPicket = startPicket

    def eventFilter(self, direction: str, data_start: list = False, data_end: list = False, counter: int = False):
        if counter:
            self.counter = counter
        if direction == "to right":
            self.__line1.shiftLine(data_start[self.counter + 1] + self.startPicket)
            self.__line2.shiftLine(data_end[self.counter + 1] + self.startPicket)
            self.counter += 1
        elif direction == "to left":
            self.__line1.shiftLine(data_start[self.counter - 1] + self.startPicket)
            self.__line2.shiftLine(data_end[self.counter - 1] + self.startPicket)
            self.counter -= 1
        return False