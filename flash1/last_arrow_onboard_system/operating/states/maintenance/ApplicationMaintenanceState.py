# This Python file uses the following encoding: utf-8
from domain.markers.AbstractRfidScanner import  AbstractRfidScanner
from domain.units.AbstractUnitProvider import AbstractUnitProvider
from PySide6.QtStateMachine import QState
from PySide6.QtCore import QEvent, Signal
from typing import Optional, Dict

class ApplicationMaintenanceState(QState):
    maintenanceCompleted: Signal = Signal()
    def __init__(self, config: dict, units: AbstractUnitProvider, rfid_tag_scanner: AbstractRfidScanner, parent: Optional[QState] = None):
        super().__init__(QState.ChildMode.ExclusiveStates, parent)

    def onEntry(self, event: QEvent):
        super().onEntry(event)
        print('[application/maintenance][entered]')
    def onExit(self, event: QEvent):
        super().onExit(event)
        print('[application/maintenance][exited]')
