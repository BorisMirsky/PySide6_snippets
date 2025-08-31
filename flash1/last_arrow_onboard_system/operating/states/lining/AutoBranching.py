from typing import Optional
from PySide6.QtCore import QObject, Signal
from domain.calculations.branching import BranchType
from domain.units.MemoryBufferUnit import MemoryBufferUnit

class AutoBranchingProcessor(QObject):
    started: Signal = Signal(float)
    stopped: Signal = Signal(float)

    def __init__(self, enabled: bool, track_length: float, branch_length: float = 6, parent: Optional[QObject] = None):
        super().__init__(parent)

        self.__active = False
        self.__current_position = 0
        self.__branch_type: BranchType = None

        # Длина всего участка пути
        self.__track_length = track_length

        # Включен или выключен отвод
        self.__enabled = enabled
        # Длина автоматического отвода (по умолчанию 6 метров)
        self.__branch_length = branch_length
        
        # Граница автоматического отвода спереди и сзади
        self.__frontRange = [0, self.__branch_length]
        self.__backRange = [self.__track_length - self.__branch_length, self.__track_length]

        # Логирование отвода
        self.__log_unit_adapt_multiplier: MemoryBufferUnit = None

    def active(self) -> bool:
        return self.__active
    def enabled(self) -> bool:
        return self.__enabled
    
    def log_units(self) -> dict:
        """
            Возвращает словарь юнитов: {Имя_юнита: Юнит}. Если юниты логирования не созданы, то создаем их.            
            Пока для логирования достаточно одного юнита.
        """
        if self.__log_unit_adapt_multiplier is None:
            self.__log_unit_adapt_multiplier = MemoryBufferUnit(self.adapt_multiplier())
        return {'log_autobranch_multiplier': self.__log_unit_adapt_multiplier}
    
    def __write_log(self):
        if self.__log_unit_adapt_multiplier is None:
            return
        self.__log_unit_adapt_multiplier.write(self.adapt_multiplier())

    def setPosition(self, position: float):
        self.__current_position = position
        
        if not self.__enabled: 
            return
        
        # Логируем
        self.__write_log()

        # отвод в начале
        if (self.__frontRange[0] <= position < self.__frontRange[1]):
            self.__start()
            self.__branch_type = BranchType.Project
        # отвод в конце
        elif (self.__backRange[0] <= position < self.__backRange[1]):
            self.__start()
            self.__branch_type = BranchType.Fact
        # в середине отвода нет
        else:
            self.__stop()
            self.__branch_type = None

    def __start(self):
        if not self.__active:
            self.__active = True
            self.started.emit(self.__current_position)

    def __stop(self):
        if self.__active:
            self.__active = False
            self.stopped.emit(self.__current_position)

    def position(self) -> float:
        return self.__current_position
    
    def adapt_multiplier(self) -> float:
        """
            Коэффициент на который умножыется сдвижка или подъемка в случае если
            отвод активен. Его значения меняются в диапазоне от [0, 1] в начале отвода и от [1, 0] в конце. 
            Всегда возвращает 1 если отвод не активен.
        """
        if not self.__active:
            return 1 
        # в начале (от факта к проекту)
        if self.__branch_type == BranchType.Project:
            return self.__current_position / self.__branch_length
        # в конце (от проекта к факту)
        if self.__branch_type == BranchType.Fact:
           return (self.__track_length - self.__current_position) / self.__branch_length
        
        return 1
    
    def adapt(self, value: float) -> float:
        return value * self.adapt_multiplier()
    
    def adapt_plan(self, value: float) -> float:
        return self.adapt(value)
    
    def adapt_prof_left(self, value: float) -> float:
        return self.adapt(value)
    
    def adapt_prof_right(self, value: float) -> float:
        return self.adapt(value)
