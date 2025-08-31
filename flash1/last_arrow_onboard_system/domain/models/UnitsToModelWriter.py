# This Python file uses the following encoding: utf-8
from .AbstractPositionedTableModel import AbstractPositionedTableModel
from ..units.AbstractUnit import AbstractReadUnit
from ..dto.Travelling import LocationVector1D
from PySide6.QtCore import QObject
from typing import Optional, Dict
import time

class UnitsToModelWriter(QObject):
    def __init__(self, measurements: AbstractPositionedTableModel, position: AbstractReadUnit[float], models: Dict[str, AbstractReadUnit], write_step: LocationVector1D = LocationVector1D(meters = 0.5), parent: Optional[QObject] = None):
        super().__init__(parent)
        self.__measurements: AbstractPositionedTableModel = measurements
        self.__position: AbstractReadUnit[float] = position
        self.__units: Dict[str, AbstractReadUnit] = models

        self.__position.changed.connect(self.__writeModelsData)
        self.__write_step: LocationVector1D = write_step
        self.__last_value: float = None
        self.__is_active: bool = False

    def __writeModelsData(self, current_position: float) ->None:
        # if self.__is_active and (self.__last_value is None or abs(current_position - self.__last_value) >= self.__write_step.meters):
        if self.__is_active and ((self.__last_value is None or abs(current_position - self.__last_value) >= self.__write_step.meters) or (self.__last_timestamp is None or (time.time()-self.__last_timestamp > 0.25))):
            self.__last_timestamp = time.time()
            self.__last_value = current_position
            record = { name: unit.read() for name, unit in self.__units.items() }
            self.__measurements.setRowAtPosition(LocationVector1D(current_position), record)

    def start(self) ->None:
        self.__is_active = True
        self.__writeModelsData(self.__position.read())
    def stop(self) ->None:
        self.__is_active = False




