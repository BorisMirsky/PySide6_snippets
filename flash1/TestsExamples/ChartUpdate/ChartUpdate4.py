
from PySide6.QtCore import QTimerEvent
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QMainWindow, QApplication
from PySide6.QtCharts import QChart, QBarSet, QBarSeries, QChartView
import sys

class MainWindow(QMainWindow):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)

        self._data=[
            [1,2,3,4,5,4,3,2,1],
            [5,4,3,2,1,2,3,4,5]
        ]
        self._currentDataIdx=0

        self._barSet=QBarSet("Bar Set")
        self._barSet.setColor(QColor(0,230,0))
        self._barSet.append(self._data[self._currentDataIdx])

        self._barSeries=QBarSeries()
        self._barSeries.setBarWidth(1)
        self._barSeries.append(self._barSet)

        self._chart=QChart()
        self._chart.addSeries(self._barSeries)
        self._chart.createDefaultAxes()
        self._chart.legend().hide()
        self._chart.axisX(self._barSeries).setVisible(False)
        self._chart.axisY(self._barSeries).setVisible(False)

        # Set the Y-axis range/limits 0 to 6
        self._chart.axisY(self._barSeries).setRange(0,6)

        self._chartView=QChartView(self._chart)

        self.setCentralWidget(self._chartView)

        self._timerId=self.startTimer(1000)

    def timerEvent(self, event:QTimerEvent):
        if self._timerId!=event.timerId():
            return

        self._currentDataIdx=1 if not self._currentDataIdx else 0
        for i,n in enumerate(self._data[self._currentDataIdx]):
            self._barSet.replace(i,n)

if __name__=="__main__":
    #from sys import arg, exit
    a=QApplication(sys.argv)
    m=MainWindow()
    m.show()
    m.resize(640,480)
    exit(a.exec())

