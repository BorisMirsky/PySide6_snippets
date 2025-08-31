# This Python file uses the following encoding: utf-8
from PySide6.QtWidgets import QWidget, QStackedLayout, QPushButton, QVBoxLayout, QLabel, QFileDialog
from PySide6.QtCore import QCoreApplication, Signal, Qt
import pandas
import gc
import cProfile

from operating.states.ApplicationStateMachine import ApplicationStateMachine
from operating.states.program_task_calculation.ProgramTaskCalculationState import ProgramTaskCalculationSuccessState
from .idle.IdleView import IdleView
from .program_task_calculation.ProgramTaskCalculationView import ProgramTaskCalculationView
from .maintenance.MaintenanceView import MaintenanceView
from .measuring.MeasuringView import MeasuringView
from .lining.LiningView import LiningView


class ApplicationView(QWidget):
    def __init__(self, state: ApplicationStateMachine, parent: QWidget = None):
        super().__init__(parent)
        # disable [x]
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)
        #
        #self.showFullScreen()     # -> all views inherit fullSizeScreen
        #
        self.__state: ApplicationStateMachine = state
        #self.__state1: ProgramTaskCalculationSuccessState = state1
        self.__state.idle.entered.connect(self.__onIdleStateEntered)
        self.__state.idle.exited.connect(self.__onIdleStateExited)
        self.__state.programTaskCalculation.entered.connect(self.__onProgramTaskCalculationStateEntered)
        self.__state.programTaskCalculation.exited.connect(self.__onProgramTaskCalculationStateExited)
        self.__state.maintenance.entered.connect(self.__onMaintenanceStateEntered)
        self.__state.maintenance.exited.connect(self.__onMaintenanceStateExited)
        self.__state.measuring.entered.connect(self.__onMeasuringStateEntered)
        self.__state.measuring.exited.connect(self.__onMeasuringStateExited)
        self.__state.lining.entered.connect(self.__onLiningStateEntered)
        self.__state.lining.exited.connect(self.__onLiningStateExited)
        self.__state.quit.entered.connect(self.__onQuitStateEntered)
        self.__state.quit.exited.connect(self.__onQuitStateExited)

        self.__currentView: QWidget = None
        self.__layout: QStackedLayout = QStackedLayout()
        self.__layout.setStackingMode(QStackedLayout.StackingMode.StackOne)
        self.setLayout(self.__layout)

    def __onIdleStateEntered(self) ->None:
        gc.collect()
        self.__currentView = IdleView(self.__state.idle)
        self.__layout.addWidget(self.__currentView)
    def __onIdleStateExited(self) ->None:
        gc.collect()
        self.__currentView.deleteLater()
    def __onProgramTaskCalculationStateEntered(self) ->None:
        gc.collect()
        self.__currentView = ProgramTaskCalculationView(self.__state.programTaskCalculation)
        self.__layout.addWidget(self.__currentView)
    def __onProgramTaskCalculationStateExited(self) ->None:
        gc.collect()
        self.__currentView.deleteLater()
    def __onMaintenanceStateEntered(self) ->None:
        gc.collect()
        self.__currentView = MaintenanceView(self.__state.maintenance)
        self.__layout.addWidget(self.__currentView)
    def __onMaintenanceStateExited(self) ->None:
        gc.collect()
        self.__currentView.deleteLater()
    def __onMeasuringStateEntered(self) ->None:
        gc.collect()
        self.__currentView = MeasuringView(self.__state.measuring)
        self.__layout.addWidget(self.__currentView)
    def __onMeasuringStateExited(self) ->None:
        gc.collect()
        self.__currentView.deleteLater()
    def __onLiningStateEntered(self) ->None:
        gc.collect()
        self.__currentView = LiningView(self.__state.lining)  #, self.__state1)
        self.__layout.addWidget(self.__currentView)
    def __onLiningStateExited(self) ->None:
        gc.collect()
        self.__currentView.deleteLater()
    def __onQuitStateEntered(self) ->None:
        gc.collect()
        pass
    def __onQuitStateExited(self) ->None:
        gc.collect()
        pass

