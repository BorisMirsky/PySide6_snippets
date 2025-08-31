from PySide6.QtWidgets import * 
from PySide6.QtCharts import * 
from PySide6.QtCore import * 
from PySide6.QtGui import *
import math
import sys
from funcs_for_charts import *
from random import uniform


class Chart(QMainWindow):
    def __init__(self):  
        super().__init__()
        #self.setGeometry(100, 100, 900, 150)
        view = self.create_linechart1()
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        lay = QVBoxLayout(central_widget)
        lay.addWidget(view, stretch=1)
        #self.createLinechart() 
  
    def create_linechart1(self):
        y_axis = QValueAxis()
        y_axis.setRange(-70.0, 70.0)
        y_axis.setLabelFormat("%0.1f")
        y_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        y_axis.setTickInterval(20)
        x_axis = QValueAxis()
        x_axis.setRange(0.0, 100.0)
        x_axis.setLabelFormat("%0.1f")
        #x_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        x_axis.setTickInterval(1)
        series = QLineSeries()
        for i in range(100):
            series.append(i, uniform(-70, 70))
        chart = QChart()
        chart.resize(900, 200)
        chart.addAxis(x_axis, Qt.AlignmentFlag.AlignBottom)
        chart.addAxis(y_axis, Qt.AlignmentFlag.AlignLeft)
        chart.legend().setVisible(True)
        chart.layout().setContentsMargins(0,0,0,0)   #
        chart.setMargins(QMargins())                 #
        series.setColor(QColor("green"))
        chart.addSeries(series)
        chartview = QChartView(chart)
        #chartview.setBackgroundBrush(QBrush(QColor("salmon")))
        #chartview.resize(900, 900)
        return chartview
 
    def createLinechart(self): 
        chart =  QChart()
        chart.createDefaultAxes()
        series = QLineSeries()
        series.append([QPointF(i[0], i[1]) for i in func1(1,250)])
        series.setColor(QColor('red'))
        chart.addSeries(series)          
        backgroundGradient = QLinearGradient()
        backgroundGradient.setStart(QPointF(0, 0))
        # цвет фона
        backgroundGradient.setColorAt(0.0, qRgb(0,0,0))
        # градиент цвета фона
        backgroundGradient.setCoordinateMode(QGradient.ObjectBoundingMode)
        chart.setBackgroundBrush(backgroundGradient)
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)
        chartview = QChartView(chart)
        chartview.setRenderHint(QPainter.Antialiasing)
        self.setCentralWidget(chartview)
        series.setColor(QColor(qRgb(0,150,150)))
 
 
#App = QApplication(sys.argv)
#window = Chart()
#window.show()
#sys.exit(App.exec())
 

 
