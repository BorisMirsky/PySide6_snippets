# This Python file uses the following encoding: utf-8
from PySide6.QtStateMachine import QState
from PySide6.QtCore import QEvent, Signal

class ApplicationIdleState(QState):
    programTaskCalculation: Signal = Signal()
    maintenance: Signal = Signal()
    measuring: Signal = Signal()
    lining: Signal = Signal()
    quit: Signal = Signal()
    def __init__(self, parent: QState = None):
        super().__init__(QState.ChildMode.ExclusiveStates, parent)

    def onEntry(self, event: QEvent):
        super().onEntry(event)
        print('[application/idle][entered]')
    def onExit(self, event: QEvent):
        super().onExit(event)
        print('[application/idle][exited]')
