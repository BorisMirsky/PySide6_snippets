# This Python file uses the following encoding: utf-8
from PySide6.QtCore import QCoreApplication, QElapsedTimer, QTime, Qt
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout
from .Base import StringLabel


class CurrentTimeLabel(StringLabel):
    def __init__(self, parent: QWidget = None):
        super().__init__(QCoreApplication.translate('UI/Common', 'Current time:'), '--:--:--', parent)
        self.__updateCurrentTime()
        self.startTimer(500)
    def timerEvent(self, event) ->None:
        super().timerEvent(event)
        self.__updateCurrentTime()
    def __updateCurrentTime(self):
        time = "      " + QTime.currentTime().toString('hh:mm:ss') + "     "
        self.setText(time) #QTime.currentTime().toString('hh:mm:ss'))

class ElapsedTimeLabel(StringLabel):
    def __init__(self, parent: QWidget = None):
        super().__init__(QCoreApplication.translate('UI/Common', 'Elapsed time:'), '--:--:--', parent)
        self.__timer = QElapsedTimer()
        self.reset()
        self.__updateCurrentTime()
        self.startTimer(500)
    def reset(self) ->None:
        self.__timer.restart()
    def timerEvent(self, event) ->None:
        super().timerEvent(event)
        self.__updateCurrentTime()
    def __updateCurrentTime(self):
        self.setText(QTime.fromMSecsSinceStartOfDay(self.__timer.elapsed()).toString('hh:mm:ss'))

