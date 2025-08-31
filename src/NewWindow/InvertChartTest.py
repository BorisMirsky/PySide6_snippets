from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtCharts import *
from random import randrange
from math import *
import sys
import numpy as np


def random_between(low, high, seed):
    return randrange(100)


class ChartClass(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(600, 1000)
        self.initUI()

    def initUI(self):
        seed = 0
        chart_view = QChartView()
        hlayout = QHBoxLayout()
        hlayout.addWidget(chart_view)
        seed = random_between(0, 100, seed)
        series1 = QLineSeries()
        series2 = QLineSeries()
        k = 0
        while k <= 100:
            series1.append(QPointF(sin((seed + k) * 0.1), k))
            series2.append(QPointF(sin((seed + k) * 0.05), k))
            k += 1
        chart = QChart()
        chart.addSeries(series1)
        chart.addSeries(series2)
        axisX = QValueAxis()
        axisX.setTitleText("x, м")
        axisX.setLabelFormat("%i")
        axisX.setTickCount(1)
        chart.addAxis(axisX, Qt.AlignmentFlag.AlignBottom)
        axisY = QValueAxis()
        axisY.setTitleText("t, мс")
        axisY.setLabelFormat("%g")
        axisY.setTickCount(5)
        chart.addAxis(axisY, Qt.AlignmentFlag.AlignLeft)
        series1.attachAxis(axisX)
        series1.attachAxis(axisY)
        series2.attachAxis(axisX)
        series2.attachAxis(axisY)
        chart_view.setChart(chart)
        self.setLayout(hlayout)


if __name__ == "__main__":
    app = QApplication([])
    window = ChartClass()
    window.show()
    sys.exit(app.exec())
