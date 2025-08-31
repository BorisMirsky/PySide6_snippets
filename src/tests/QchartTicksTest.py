from PySide6.QtWidgets import QVBoxLayout, QApplication
from PySide6.QtCharts import QLineSeries, QChart, QChartView, QValueAxis
from PySide6.QtGui import QColor, QBrush
import sys
import math
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 


class Chart1(QChart):
    def __init__(self):
        super().__init__()
        #self.gridLineColor(QBrush("red"))
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
        x_axis.setTickInterval(10)
        x_axis.setMinorTickCount(5)
        y_axis.setTickInterval(0.2)
        y_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        axis_brush = QBrush(QColor("white"))
        y_axis.setLabelsBrush(axis_brush)
        x_axis.setLabelsBrush(axis_brush)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    c1 = Chart1()
    chart_view = QChartView(c1)
    chart_view.chart().setBackgroundBrush(QBrush("black"))
    chart_view.show()
    sys.exit(app.exec())
