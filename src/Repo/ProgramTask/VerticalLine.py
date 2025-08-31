from PySide6.QtCore import *
import math
import pandas as pd
import numpy as np
from ServiceInfo import *


class VerticalLineModel1(QAbstractTableModel):
    positionChanged = Signal(int)
    def __init__(self, startX1, parent: QObject = None):
        super().__init__(parent)
        self.__currentX1 = startX1
        self.__minY = -150.0
        self.__maxY = 1.0
    def currentX(self):
        return  self.__currentX1 
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
            return self.__currentX1
        elif index.column() == 1 and index.row() == 0:
            return self.__minY
        elif index.column() == 1 and index.row() == 1:
            return self.__maxY
        else:
            return
        
    def shiftLine(self, newX1: float): 
        if newX1 == 0:
            return
        if float(self.__currentX1) <= 0 and newX1 < 0:
            return
        self.__currentX1 = newX1
        self.dataChanged.emit(self.index(0, 0), self.index(1, 1), [Qt.ItemDataRole.DisplayRole])
        self.positionChanged.emit(self.__currentX1)
        return  self.__currentX1   
    # Удержание полосы на месте  
    # def keep_line_position(self, pos:float):
    #     self.__currentX = pos
    #     self.dataChanged.emit(self.index(0, 0), self.index(1, 1), [Qt.ItemDataRole.DisplayRole])
    #     self.positionChanged.emit(self.__currentX)


class VerticalLineModel2(QAbstractTableModel):
    positionChanged = Signal(int)
    def __init__(self, startX1, parent: QObject = None):
        super().__init__(parent)
        self.__currentX1 = startX1
        self.__minY = -150.0
        self.__maxY = 1.0
    def currentX(self):
        return  self.__currentX1 
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
            return self.__currentX1
        elif index.column() == 1 and index.row() == 0:
            return self.__minY
        elif index.column() == 1 and index.row() == 1:
            return self.__maxY
        else:
            return
    def shiftLine(self, newX1: float): 
        if newX1 == 0:
            return
        if float(self.__currentX1) <= 0 and newX1 < 0:
            return
        self.__currentX1 = newX1
        self.dataChanged.emit(self.index(0, 0), self.index(1, 1), [Qt.ItemDataRole.DisplayRole])
        self.positionChanged.emit(self.__currentX1)
        return  self.__currentX1   

    

class MoveLineController(QObject):
    def __init__(self, minPosition: float,
                 line1: VerticalLineModel1,
                 line2: VerticalLineModel2,
                 parent: QObject = None):
        super().__init__(parent)
        self.minPosition = minPosition
        self.__line1 = line1
        self.__line2 = line2
        self.counter = 0
        self.step = 0.185

    def eventFilter1(self, direction:str):
        if direction == "to right":
            self.__line1.shiftLine(first_points[self.counter + 1] / self.step)
            self.__line2.shiftLine(second_points[self.counter + 1] / self.step)
            self.counter += 1
            #print('first_points ', first_points,
            #      'first_points[self.counter + 1] ', first_points[self.counter + 1])
        elif direction == "to left":
            self.__line1.shiftLine(first_points[self.counter - 1] / self.step)
            self.__line2.shiftLine(second_points[self.counter - 1] / self.step)
            self.counter -= 1
        return False

    # def eventFilter(self, watched: QObject, event: QEvent):
    #     if event.type() == QEvent.Type.KeyPress:
    #         if event.key() == Qt.Key.Key_D:
    #             if 0 <= self.counter < SUMMARY_LEN:
    #                 #print(first_points[self.counter], second_points[self.counter], self.counter)
    #                 self.__line1.shiftLine(first_points[self.counter + 1] / self.step)
    #                 self.__line2.shiftLine(second_points[self.counter + 1] / self.step)
    #                 self.counter += 1
    #         elif event.key() == Qt.Key.Key_A:
    #             if 0 < self.counter <= SUMMARY_LEN:
    #                 self.__line1.shiftLine(first_points[self.counter - 1] / self.step)
    #                 self.__line2.shiftLine(second_points[self.counter - 1] / self.step)
    #                 self.counter -= 1
    #     return False






    
