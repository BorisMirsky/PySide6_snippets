import random
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCharts import QLineSeries, QChart, QChartView, QValueAxis

baseValuesList = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
randomValuesList = [256, 14, 89, 100, 150, 500, 50, 34, 67, 90, 102, 12, 19, 89, 34, 145, 71, 4, 89, 47]


def listUpdatingFunction():
    baseValuesList.pop(0)
    value = random.choice(randomValuesList)
    baseValuesList.append(value)


class Worker(QtCore.QObject):
    def __init__(self, function, interval):
        super(Worker, self).__init__()
        self._funcion = function
        self._timer = QtCore.QTimer(self, interval=interval, timeout=self.execute)

    @property
    def running(self):
        return self._timer.isActive()

    def start(self):
        self._timer.start()

    def stop(self):
        self._timer.stop()

    def execute(self):
        self._funcion()


class minimalMonitor(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        # Creating QChart
        layout = QtWidgets.QVBoxLayout(self)
        self.chart = QChart()
        self.chart.setAnimationOptions(QChart.AllAnimations)
        self.series = QLineSeries()
        self.chart.addSeries(self.series)
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QtGui.QPainter.Antialiasing)
        layout.addWidget(self.chart_view)
        self.axis_x = QValueAxis()
        self.chart.addAxis(self.axis_x, QtCore.Qt.AlignBottom)
        self.axis_y = QValueAxis()
        self.chart.addAxis(self.axis_y, QtCore.Qt.AlignLeft)
        self.axis_x.setRange(0, 20)
        self.axis_y.setRange(0, 300)
        self.series.attachAxis(self.axis_x)
        self.series.attachAxis(self.axis_y)

        self.worker = Worker(self.update_chart, 1000)

        self.autoUpdateStart = QtWidgets.QPushButton("Start Auto-Update")
        self.autoUpdateStart.setCheckable(False)
        self.autoUpdateStart.toggle()
        self.autoUpdateStart.clicked.connect(self.worker.start)

        self.autoUpdateStop = QtWidgets.QPushButton("Stop Auto-Update")
        self.autoUpdateStop.setCheckable(False)
        self.autoUpdateStop.toggle()
        self.autoUpdateStop.clicked.connect(self.worker.stop)
        layout.addWidget(self.autoUpdateStart)
        layout.addWidget(self.autoUpdateStop)
        self.manualUpdateButton = QtWidgets.QPushButton("Manual Update")
        self.manualUpdateButton.setCheckable(False)
        self.manualUpdateButton.toggle()
        self.manualUpdateButton.clicked.connect(self.update_chart)
        layout.addWidget(self.manualUpdateButton)
        self.update_chart()

    def update_chart(self):
        listUpdatingFunction()
        #print(type(listUpdatingFunction()))
        self.series.clear()
        for i, value in enumerate(baseValuesList):
            self.series.append(i, value)
        self.chart_view.update()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    widget = minimalMonitor()
    widget.show()
    sys.exit(app.exec())