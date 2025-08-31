
from PySide6.QtWidgets import QVBoxLayout, QApplication
from PySide6.QtCharts import QLineSeries, QChart, QChartView, QValueAxis, QAreaSeries
from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QBrush, QPen
import sys
import math
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)



class Chart(QChart):
    def __init__(self):
        super().__init__()
        self.series0 = QLineSeries()
        self.series1 = QLineSeries()
        x_axis = QValueAxis()
        y_axis = QValueAxis()
        self.setAxisX(x_axis)
        self.setAxisY(y_axis)
        self.legend().setVisible(False)
        self.series0.append(QPointF(0, 0))
        self.series0.append(QPointF(1000, 0))
        for i in range (0, 1000, 1):
            self.series1.append(i, math.sin(i * 0.1))
        self.series = QAreaSeries(self.series0, self.series1)
        self.series.setBrush(QBrush("#88F34B"))
        #
        self.series2 = QLineSeries()
        for i in range(0, 1000, 1):
            self.series2.append(i, math.cos(i * 0.1))
        self.pen = QPen("red")
        self.pen.setWidth(2)
        self.series2.setPen(self.pen)

        self.addSeries(self.series)
        self.addSeries(self.series2)
        self.axisX().setRange(0, 1000)
        self.axisY().setRange(-2,2)
        x_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        x_axis.setTickInterval(100)
        y_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        y_axis.setTickInterval(1)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    c= Chart()
    chart_view = QChartView(c)
    chart_view.chart()
    chart_view.show()
    sys.exit(app.exec())

