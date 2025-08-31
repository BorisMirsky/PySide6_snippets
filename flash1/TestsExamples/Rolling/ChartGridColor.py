
from PySide6.QtWidgets import QVBoxLayout, QApplication
from PySide6.QtCharts import QLineSeries, QChart, QChartView, QValueAxis
from PySide6.QtGui import QColor, QBrush
import sys
import math


class Chart1(QChart):
    def __init__(self):
        super().__init__()
        series = QLineSeries()
        x_axis = QValueAxis()
        y_axis = QValueAxis()
        self.setAxisX(x_axis)
        self.setAxisY(y_axis)
        self.legend().setVisible(False)
        for i in range (0, 100, 1):
            series.append(i, math.sin(i))
        self.addSeries(series)
        self.axisX().setRange(0, 100)
        self.axisY().setRange(-1,1)
        x_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        x_axis.setTickInterval(20)
        y_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        y_axis.setTickInterval(0.2)
        axis_brush = QBrush(QColor("yellow"))
        y_axis.setLabelsBrush(axis_brush)
        x_axis.setLabelsBrush(axis_brush)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    c1 = Chart1()
    chart_view = QChartView(c1)
    chart_view.chart().setBackgroundBrush(QBrush("black"))
    chart_view.show()
    sys.exit(app.exec())

