from PySide6.QtWidgets import * 
from PySide6.QtCharts import * 
from PySide6.QtCore import * 
from PySide6.QtGui import *
import math
import sys
from funcs_for_charts import *
from random import uniform


class ClassCharts(QMainWindow):   # QWidget
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 900, 300)
        view1 = self.create_linechart1()
        view2 = self.create_linechart2()
        view3 = self.create_linechart3()
        view4 = self.create_linechart4()
        view5 = self.create_linechart5()
        view6 = self.create_linechart6()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        lay = QVBoxLayout(central_widget)
        lay.addWidget(view1, stretch=1)
        lay.addWidget(view2, stretch=1)
        lay.addWidget(view3, stretch=1)
        lay.addWidget(view4, stretch=1)
        lay.addWidget(view5, stretch=1)
        lay.addWidget(view6, stretch=1)

    def create_linechart1(self):
        y_axis = QValueAxis()
        y_axis.setRange(0.0, 160.0)
        y_axis.setLabelFormat("%0.1f")
        y_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        #y_axis.setTickInterval(20)
        x_axis = QValueAxis()
        x_axis.setRange(0.0, 100.0)
        x_axis.setLabelFormat("%0.1f")
        x_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        x_axis.setTickInterval(10)
        series = QLineSeries(name="random serie 1")
        for i in range(100):
            series.append(i, uniform(0, 160))
        chart = QChart()
        chart.addAxis(x_axis, Qt.AlignmentFlag.AlignBottom)
        chart.addAxis(y_axis, Qt.AlignmentFlag.AlignLeft)
        chart.legend().setVisible(True)
        series.setColor(QColor("salmon"))
        chart.addSeries(series)
        chart.setTitle("уст. и доп. скорости")
        chartview = QChartView(chart)
        return chartview

    def create_linechart2(self):
        y_axis = QValueAxis()
        y_axis.setRange(-150.0, 150.0)
        y_axis.setLabelFormat("%0.1f")
        y_axis.setTickType(QValueAxis.TickType.TicksDynamic)
            #y_axis.setTickInterval(20)
        x_axis = QValueAxis()
        x_axis.setRange(0.0, 100.0)
        x_axis.setLabelFormat("%0.1f")
        x_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        x_axis.setTickInterval(10)
        series = QLineSeries(name="random serie 2")
        for i in range(100):
            series.append(i, uniform(-150, 150))
        chart = QChart()
        chart.addAxis(x_axis, Qt.AlignmentFlag.AlignBottom)
        chart.addAxis(y_axis, Qt.AlignmentFlag.AlignLeft)
        chart.legend().setVisible(True)
        series.setColor(QColor("cyan"))
        chart.addSeries(series)
        chart.setTitle("план")
        chartview = QChartView(chart)
        return chartview

    def create_linechart3(self):
        y_axis = QValueAxis()
        y_axis.setRange(-150.0, 150.0)
        y_axis.setLabelFormat("%0.1f")
        y_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        #y_axis.setTickInterval(20)
        x_axis = QValueAxis()
        x_axis.setRange(0.0, 100.0)
        x_axis.setLabelFormat("%0.1f")
        x_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        x_axis.setTickInterval(10)
        series = QLineSeries(name="random serie 3")
        for i in range(100):
            series.append(i, uniform(-150, 150))
        chart = QChart()
        chart.addAxis(x_axis, Qt.AlignmentFlag.AlignBottom)
        chart.addAxis(y_axis, Qt.AlignmentFlag.AlignLeft)
        chart.legend().setVisible(True)
        series.setColor(QColor("yellow"))
        chart.addSeries(series)
        chart.setTitle("уровень")
        chartview = QChartView(chart)
        return chartview


#----------------------------------------------
    def create_linechart4(self):
        y_axis = QValueAxis()
        y_axis.setRange(-150.0, 150.0)
        y_axis.setLabelFormat("%0.1f")
        y_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        #y_axis.setTickInterval(20)
        x_axis = QValueAxis()
        x_axis.setRange(0.0, 100.0)
        x_axis.setLabelFormat("%0.1f")
        x_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        x_axis.setTickInterval(10)
        series = QLineSeries(name="random serie 4")
        for i in range(100):
            series.append(i, uniform(-150, 150))
        chart = QChart()
        chart.addAxis(x_axis, Qt.AlignmentFlag.AlignBottom)
        chart.addAxis(y_axis, Qt.AlignmentFlag.AlignLeft)
        chart.legend().setVisible(True)
        series.setColor(QColor("red"))
        chart.addSeries(series)
        chart.setTitle("профиль")
        chartview = QChartView(chart)
        return chartview

    def create_linechart5(self):
        y_axis = QValueAxis()
        y_axis.setRange(-150.0, 150.0)
        y_axis.setLabelFormat("%0.1f")
        y_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        #y_axis.setTickInterval(20)
        x_axis = QValueAxis()
        x_axis.setRange(0.0, 100.0)
        x_axis.setLabelFormat("%0.1f")
        x_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        x_axis.setTickInterval(10)
        series = QLineSeries(name="random serie 5")
        for i in range(100):
            series.append(i, uniform(-150, 150))
        chart = QChart()
        chart.addAxis(x_axis, Qt.AlignmentFlag.AlignBottom)
        chart.addAxis(y_axis, Qt.AlignmentFlag.AlignLeft)
        chart.legend().setVisible(True)
        #series.setColor(QColor("yellow"))
        chart.addSeries(series)
        chart.setTitle("динамическая оценка")
        chartview = QChartView(chart)
        return chartview

    def create_linechart6(self):
        y_axis = QValueAxis()
        y_axis.setRange(-150.0, 150.0)
        y_axis.setLabelFormat("%0.1f")
        y_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        #y_axis.setTickInterval(20)
        x_axis = QValueAxis()
        x_axis.setRange(0.0, 100.0)
        x_axis.setLabelFormat("%0.1f")
        x_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        x_axis.setTickInterval(10)
        series = QLineSeries(name="random serie 6")
        for i in range(100):
            series.append(i, uniform(-150, 150))
        chart = QChart()
        chart.addAxis(x_axis, Qt.AlignmentFlag.AlignBottom)
        chart.addAxis(y_axis, Qt.AlignmentFlag.AlignLeft)
        chart.legend().setVisible(True)
        #series.setColor(QColor("yellow"))
        chart.addSeries(series)
        chart.setTitle("потребность в выправочных работах")
        chartview = QChartView(chart)
        return chartview

if __name__ == "__main__":
    App = QApplication(sys.argv)
    window = ClassCharts()
    window.show()
    sys.exit(App.exec())


