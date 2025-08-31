# This Python file uses the following encoding: utf-8
from PySide6.QtStateMachine import QFinalState, QState
from PySide6.QtCore import QCoreApplication, QEvent
# from presentation.machine.units.com_port.ComPortUnitProvider import SerialPortUnitProvider
from domain.units.AbstractUnitProvider import AbstractUnitProvider

class ApplicationQuitState(QFinalState):
    def __init__(self, machine: AbstractUnitProvider, parent: QState = None):
        super().__init__(parent)
        self.__machine = machine
    def onEntry(self, event: QEvent):
        super().onEntry(event)
        self.__machine.controller_communication_allowed = False
        print('[application/quit][entered]')
        QCoreApplication.instance().quit()

    def onExit(self, event: QEvent):
        super().onExit(event)
        print('[application/quit][exited]')
