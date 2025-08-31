# This Python file uses the following encoding: utf-8
from .AsyncProgramTaskCalculator import AsyncProgramTaskCalculator
from domain.models.AbstractPositionedTableModel import AbstractPositionedTableModel
from domain.models.StepIndexedDataFramePositionedModel import StepIndexedDataFramePositionedModel
from domain.dto.Workflow import ProgramTaskCalculationOptionsDto, ProgramTaskCalculationResultDto
from PySide6.QtStateMachine import QStateMachine, QFinalState, QState
from PySide6.QtCore import QEvent, Signal
from typing import Optional
import json
from presentation.utils.store.workflow.zip.Dto import ProgramTaskCalculationResultDto_to_archive
import zipfile

class ProgramTaskCalculationOptionsState(QState):
    start: Signal = Signal(ProgramTaskCalculationOptionsDto)
    open: Signal = Signal(ProgramTaskCalculationResultDto)
    cancel: Signal = Signal()
    def __init__(self, config: dict, parent: Optional[QState] = None) ->None:
        super().__init__(QState.ChildMode.ExclusiveStates, parent)
        self.__config: dict = config
    def config(self) ->dict:
        return self.__config
    def restrictions(self) ->dict:
        return self.__restrictions
    
    def setRestrictions(self, value: dict) -> None:
        self.__restrictions = value
    
    def onEntry(self, event: QEvent):
        super().onEntry(event)
        print('[application/program_task_calculation/options][entered]')
        self.__restrictions = json.load(open('./resources/restrictions.json'))

    def onExit(self, event: QEvent):
        super().onExit(event)
        print('[application/program_task_calculation/options][exited]')
        self.__restrictions = None

class ProgramTaskCalculationProcessState(QState):
    success: Signal = Signal(ProgramTaskCalculationResultDto)
    error: Signal = Signal(Exception)
    def __init__(self, parent: Optional[QState] = None) ->None:
        super().__init__(QState.ChildMode.ExclusiveStates, parent)
        self.__calculator: AsyncProgramTaskCalculator = None

    def calculator(self) -> AsyncProgramTaskCalculator:
        return self.__calculator
    
    def onEntry(self, event: QStateMachine.SignalEvent):
        super().onEntry(event)
        print('[application/program_task_calculation/process][entered]')
        self.__calculator = AsyncProgramTaskCalculator(event.arguments()[0])
        self.__calculator.success.connect(self.success)
        self.__calculator.error.connect(self.error)
        self.__calculator.start()
        # self.__calculator.run() # Используется вместо start для синхронного запуска (для тестирования)

    def onExit(self, event: QEvent):
        super().onExit(event)
        print('[application/program_task_calculation/process][exited]')
        self.__calculator = None

class ProgramTaskCalculationSuccessState(QState):
    finish: Signal = Signal()
    def __init__(self, parent: Optional[QState] = None) ->None:
        super().__init__(QState.ChildMode.ExclusiveStates, parent)
        self.__program_task: AbstractPositionedTableModel = None
        self.__calculation_result: ProgramTaskCalculationResultDto = None

    def calculation_result(self) ->ProgramTaskCalculationResultDto:
        return self.__calculation_result
    def program_task(self) ->AbstractPositionedTableModel:
        return self.__program_task
    def onEntry(self, event: QEvent):
        super().onEntry(event)
        print('[application/program_task_calculation/success][entered]')
        self.__calculation_result = event.arguments()[0]
        self.__program_task = StepIndexedDataFramePositionedModel(self.__calculation_result.calculated_task.data.columns, self.__calculation_result.calculated_task.step, self)
        self.__program_task.reset(self.__calculation_result.calculated_task.step, self.__calculation_result.calculated_task.data)
       
        # ProgramTaskCalculationResultDto_to_archive(zipfile.ZipFile('program_task.apt', 'w'), self.__calculation_result)
        # print('program task saved!')

    def onExit(self, event: QEvent):
        super().onExit(event)
        print('[application/program_task_calculation/success][exited]')
        self.__program_task = None
        self.__calculation_result = None
    
class ProgramTaskCalculationErrorState(QState):
    finish: Signal = Signal()
    def __init__(self, parent: Optional[QState] = None) ->None:
        super().__init__(QState.ChildMode.ExclusiveStates, parent)
        self.__error: Exception = None
    def error(self) ->Exception:
        return self.__error
    def onEntry(self, event: QStateMachine.SignalEvent):
        super().onEntry(event)
        print('[application/program_task_calculation/error][entered]')
        self.__error = event.arguments()[0]
    def onExit(self, event: QEvent):
        super().onExit(event)
        print('[application/program_task_calculation/error][exited]')
        self.__error = None

class ProgramTaskCalculationFinalState(QFinalState):
    def __init__(self, parent: Optional[QState] = None) ->None:
        super().__init__(parent)
    def onEntry(self, event: QEvent):
        super().onEntry(event)
        print('[application/program_task_calculation/final][entered]')
    def onExit(self, event: QEvent):
        super().onExit(event)
        print('[application/program_task_calculation/final][exited]')

class ProgramTaskCalculationState(QState):
    def __init__(self, config: dict, parent: Optional[QState] = None):
        super().__init__(QState.ChildMode.ExclusiveStates, parent)

        self.options = ProgramTaskCalculationOptionsState(config, self)
        self.process = ProgramTaskCalculationProcessState(self)
        self.success = ProgramTaskCalculationSuccessState(self)
        self.error = ProgramTaskCalculationErrorState(self)
        self.final = ProgramTaskCalculationFinalState(self)

        self.options.addTransition(self.options.start, self.process)
        self.options.addTransition(self.options.open, self.success)
        self.options.addTransition(self.options.cancel, self.final)
        self.process.addTransition(self.process.success, self.success)
        self.process.addTransition(self.process.error, self.error)
        self.success.addTransition(self.success.finish, self.final)
        self.error.addTransition(self.error.finish, self.final)
        self.setInitialState(self.options)

    def onEntry(self, event: QEvent):
        super().onEntry(event)
        print('[application/program_task_calculation][entered]')
    def onExit(self, event: QEvent):
        super().onExit(event)
        print('[application/program_task_calculation][exited]')
