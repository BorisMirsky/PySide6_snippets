from PySide6.QtWidgets import QVBoxLayout, QApplication
from PySide6.QtCharts import QLineSeries, QChart, QChartView, QValueAxis,QAbstractAxis 
from PySide6.QtGui import QColor, QBrush
import sys
import math
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

#s = "QTableWidget {gridline-color: #fffff8; }"


class Chart1(QChart):
    def __init__(self):
        super().__init__()
        series = QLineSeries()
        x_axis = QValueAxis()
        y_axis = QValueAxis()
        #print(dir(x_axis))
        x_axis.setGridLineColor(QColor("red"))
        y_axis.setGridLineColor(QColor("red"))
        self.setAxisX(x_axis)
        self.setAxisY(y_axis)
        self.legend().setVisible(False)
        for i in range (0, 100, 1):
            series.append(i, math.sin(i))
        self.addSeries(series)
        self.axisX().setRange(0, 100)
        x_axis.setMinorTickCount(5)
        self.axisY().setRange(-1,1)
        x_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        x_axis.setTickInterval(20)
        y_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        y_axis.setTickInterval(0.2)
        axis_brush = QBrush(QColor("white"))
        y_axis.setLabelsBrush(axis_brush)
        x_axis.setLabelsBrush(axis_brush)
        #x_axis.setStyleSheet(s)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    c1 = Chart1()
    chart_view = QChartView(c1)
    chart_view.chart().setBackgroundBrush(QBrush("black"))
    chart_view.show()
    sys.exit(app.exec())

