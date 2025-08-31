
from PySide6.QtWidgets import QWidget, QListWidget, QListWidgetItem, QVBoxLayout, QApplication
from PySide6.QtCharts import QLineSeries, QVXYModelMapper, QChart, QChartView, QValueAxis
from PySide6.QtGui import QFont, QIcon, QShortcut, Qt, QPen, QPainter, QImage, QPixmap, QColor, QKeySequence,QBrush
from PySide6.QtCore import Qt, QTimer, QObject, QDateTime, QCoreApplication, Signal, QTimer, QPointF
import sys
import numpy as np
from math import sin, cos


class Chart1(QWidget):
    def __init__(self): 
        super().__init__()
        self.chart = QChart()
        self.chart.legend().setVisible(False)
        self.series1 = QLineSeries()
        for i in range (0, 500, 1):
            self.series1.append([QPointF(i, cos(i * 50) * 100)])
        self.x_start = 0
        self.x_stop = 500
        self.setFocusPolicy(Qt.NoFocus)
        self.series1.setPen(QPen(Qt.GlobalColor.green, 2))
        self.chart.addSeries(self.series1)
        self.series2 = QLineSeries()
        for i in range(0, 500, 1):
            self.series2.append([QPointF(i, cos(i) * 100)])
        self.series2.setPen(QPen(Qt.GlobalColor.red, 2))
        self.chart.addSeries(self.series2)
        y_axis = QValueAxis()
        y_axis.setRange(-100,100)
        y_axis.setLabelFormat("%.4d")
        y_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        y_axis.setTickInterval(20)
        x_axis = QValueAxis()
        x_axis.setRange(self.x_start, self.x_stop)
        x_axis.setLabelFormat("%d")
        x_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        x_axis.setTickInterval(100)
        self.chart.addAxis(x_axis, Qt.AlignmentFlag.AlignBottom)
        self.chart.addAxis(y_axis, Qt.AlignmentFlag.AlignLeft)
        self.series1.attachAxis(x_axis)
        self.series1.attachAxis(y_axis)
        labelsFont = QFont()
        labelsFont.setPixelSize(12)
        x_axis.setLabelsFont(labelsFont)
        y_axis.setLabelsFont(labelsFont)
        axisBrush = QBrush(Qt.GlobalColor.black)
        x_axis.setLabelsBrush(axisBrush)
        y_axis.setLabelsBrush(axisBrush)
        self.chart_view = QChartView(self.chart)
        vbox = QVBoxLayout()
        vbox.addWidget(self.chart_view)
        self.setLayout(vbox)


class Chart2(QWidget):
    def __init__(self): 
        super().__init__()
        self.chart = QChart()
        self.chart.legend().setVisible(False)
        self.series1 = QLineSeries()
        for i in range (0, 500, 1):
            self.series1.append([QPointF(i, cos(i * 0.01))])
        self.x_start = 0
        self.x_stop = 500
        self.setFocusPolicy(Qt.NoFocus)
        self.series1.setPen(QPen(Qt.GlobalColor.green, 2))
        self.chart.addSeries(self.series1)
        self.y_axis = QValueAxis()
        self.y_axis.setRange(-5,5)
        self.y_axis.setLabelFormat("%04d")
        self.y_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        self.y_axis.setTickInterval(10)
        axisBrush = QBrush(Qt.GlobalColor.black)
        self.y_axis.setTitleBrush(axisBrush)
        self.x_axis = QValueAxis()
        self.x_axis.setRange(self.x_start, self.x_stop)
        self.x_axis.setLabelFormat("%d")
        self.x_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        self.x_axis.setTickInterval(100)
        self.chart.addAxis(self.x_axis, Qt.AlignmentFlag.AlignBottom)
        self.chart.addAxis(self.y_axis, Qt.AlignmentFlag.AlignLeft)
        self.series1.attachAxis(self.x_axis)
        self.series1.attachAxis(self.y_axis)
        labelsFont = QFont()
        labelsFont.setPixelSize(12)
        self.x_axis.setLabelsFont(labelsFont)
        self.y_axis.setLabelsFont(labelsFont)
        self.x_axis.setLabelsBrush(axisBrush)
        self. y_axis.setLabelsBrush(axisBrush)
        self.chart_view = QChartView(self.chart)
        vbox = QVBoxLayout()
        vbox.addWidget(self.chart_view)
        self.setLayout(vbox)


class ChartsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setContentsMargins(0,0,0,0)
        chart1 = Chart1()       
        chart2 = Chart2() 
        vbox = QVBoxLayout()
        vbox.addWidget(chart1,2)
        vbox.addWidget(chart2,1)
        self.setLayout(vbox)



if __name__ == '__main__':
     app = QApplication(sys.argv)
     c1 = Chart1() 
     c2 = Chart2() 
     cw = ChartsWidget()
     cw.show()
     sys.exit(app.exec())




