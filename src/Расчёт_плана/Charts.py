from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCharts import * #QChart, QChartView, QLineSeries
from PySide6.QtCore import * #QPointF,QPoint
from PySide6.QtGui import * #QPainter, Qt
import math
import sys
from funcs_for_charts import *



class Chart(QMainWindow):
    def __init__(self, number):
        super().__init__()
        #self.setWindowTitle("PyQtChart Line")
        self.setGeometry(100, 100, 800, 200) 
        self.show()
        self.number = number
        self.create_linechart(self.number)
  
 
    def create_linechart(self, number):
        series = QLineSeries(self)
        #data = func(1,20)
        #data1 = [QPointF(i[0], i[1]) for i in data]
        if number == 1:
            series.append([QPointF(i[0], i[1]) for i in func1(1,250)])
        elif number == 2:
            series.append([QPointF(i[0], i[1]) for i in func2(1,250)])
        elif number == 3:
            series.append([QPointF(i[0], i[1]) for i in func3(1,250)])
        elif number == 4:
            series.append([QPointF(i[0], i[1]) for i in func4(1,250)])
        else:
            series.append([QPointF(i[0], i[1]) for i in func5(1,250)])
  
        chart =  QChart()
        chart.addSeries(series)
        chart.createDefaultAxes()

        backgroundGradient = QLinearGradient()
        backgroundGradient.setStart(QPointF(0, 0))
        backgroundGradient.setColorAt(0.0, qRgb(0,0,0))
        #backgroundGradient.setCoordinateMode(QGradient.ObjectBoundingMode)
        chart.setBackgroundBrush(backgroundGradient)
        #chart.setAnimationOptions(QChart.SeriesAnimations)
        #chart.setTitle("Line Chart Example")
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)
        chartview = QChartView(chart)
        chartview.setRenderHint(QPainter.Antialiasing)
        self.setCentralWidget(chartview)
        series.setColor(QColor(qRgb(0,150,150)))
 
 
#App = QApplication(sys.argv)
#window = Chart(2)
#sys.exit(App.exec())
 

 

 
