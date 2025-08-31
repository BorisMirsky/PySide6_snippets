# This Python file uses the following encoding: utf-8
from domain.dto.Workflow import ProgramTaskCalculationOptionsDto, ProgramTaskCalculationResultDto
from domain.dto.Travelling import LocationVector1D
from domain.calculations.progtask import program_task_caculation

from cantok import CancellationError, AbstractToken, SimpleToken
from PySide6.QtCore import Signal, QObject, QThread
from typing import Optional
import traceback


class AsyncProgramTaskCalculator(QThread):
    progressChanged: Signal = Signal(float)
    success: Signal = Signal(ProgramTaskCalculationResultDto)
    # cancel: Signal = Signal(CancellationError)
    error: Signal = Signal(Exception)
    def __init__(self, options: ProgramTaskCalculationOptionsDto, step: LocationVector1D = LocationVector1D(0.185), parent: Optional[QObject] = None) ->None:
        super().__init__(parent)
        self.__external_cancellation_token: AbstractToken = SimpleToken()
        self.__options: ProgramTaskCalculationOptionsDto = options
        self.__step: LocationVector1D = step
    def cancellation_token(self) ->AbstractToken:
        return self.__external_cancellation_token
    def run(self) ->None:
        print('Start ProgramTask calculation')
        try:                
            base_task, machine_task, summary = program_task_caculation(
                                    self.__options, 
                                    data_step = self.__step.meters,
                                    cancellation_token = self.__external_cancellation_token,
                                    progress = self.progressChanged.emit)
            print('Success program task calculation')
            if self.isInterruptionRequested():
                return

            # task.index.name = 'step'
            # task.drop('position', axis = 1, inplace = True)
            # print(task)
            self.success.emit(
                ProgramTaskCalculationResultDto(options=self.__options, base=base_task, calculated_task=machine_task, summary=summary))
            
        except CancellationError as error:
            print('Program task calculation was cancelled')
            if not self.isInterruptionRequested():
                # self.cancel.emit(error)
                self.error.emit(error)
        except Exception as error:
            print('Error program task calculation')
            print(traceback.format_exc())
            if not self.isInterruptionRequested():
                self.error.emit(error)
