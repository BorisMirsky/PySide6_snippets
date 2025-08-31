# This Python file uses the following encoding: utf-8
from PySide6.QtStateMachine import QStateMachine, QState
from PySide6.QtCore import QObject, QEvent
from domain.markers.AbstractRfidScanner import AbstractRfidScanner
from domain.units.AbstractUnitProvider import AbstractUnitProvider
from domain.units.AbstractUnit import AbstractReadWriteUnit
from .idle.ApplicationIdleState import ApplicationIdleState
from .program_task_calculation.ProgramTaskCalculationState import ProgramTaskCalculationState
from .maintenance.ApplicationMaintenanceState import ApplicationMaintenanceState
from .measuring.ApplicationMeasuringState import ApplicationMeasuringState
from .lining.ApplicationLiningState import ApplicationLiningState
from .quit.ApplicationQuitState import ApplicationQuitState
from typing import Optional

class ApplicationStateMachine(QStateMachine):
    def __init__(self, config: dict, units: AbstractUnitProvider, rfid_tag_scanner: AbstractRfidScanner, parent: Optional[QObject] = None):
        super().__init__(QState.ChildMode.ExclusiveStates, parent)
        self.idle = ApplicationIdleState(self)
        self.programTaskCalculation = ProgramTaskCalculationState(config, self)
        self.maintenance = ApplicationMaintenanceState(config, units, rfid_tag_scanner, self)
        # self.measuring = ApplicationMeasuringState(config, position_unit, units, rfid_tag_scanner, self)
        self.measuring = ApplicationMeasuringState(config, units, rfid_tag_scanner, self)
        # self.lining = ApplicationLiningState(config, position_unit, units, rfid_tag_scanner, self)
        self.lining = ApplicationLiningState(config, units, rfid_tag_scanner, self)
        self.quit = ApplicationQuitState(units, self)

        self.idle.addTransition(self.idle.programTaskCalculation, self.programTaskCalculation)
        self.idle.addTransition(self.idle.maintenance, self.maintenance)
        self.idle.addTransition(self.idle.measuring, self.measuring)
        self.idle.addTransition(self.idle.lining, self.lining)
        self.idle.addTransition(self.idle.quit, self.quit)

        self.programTaskCalculation.addTransition(self.programTaskCalculation.finished, self.idle)
        self.maintenance.addTransition(self.maintenance.maintenanceCompleted, self.idle)
        self.measuring.addTransition(self.measuring.finished, self.idle)
        self.lining.addTransition(self.lining.finished, self.idle)
        self.setInitialState(self.idle)
    def onEntry(self, event: QEvent):
        super().onEntry(event)
        print('[application][entered]')
    def onExit(self, event: QEvent):
        super().onExit(event)
        print('[application][exited]')
