from PySide6.QtWidgets import * 
from PySide6.QtCharts import * 
from PySide6.QtCore import * 
from PySide6.QtGui import *
import math
import sys
from funcs_for_charts import *



class ClassCharts(QMainWindow):
    def __init__(self): 
        super().__init__()
        self.setGeometry(100, 100, 800, 200) 
        self.chartsLayout = QVBoxLayout()
        self.createLinechart()
        self.setLayout(self.chartsLayout)
   
    def createLinechart(self):     
        chart1 =  QChart()
        series1 = QLineSeries()
        series1.append([QPointF(i[0], i[1]) for i in func1(1,250)])
        chart1.addSeries(series1)
        chart1.createDefaultAxes()
        chartview1 = QChartView(chart1)
        self.chartsLayout.addWidget(chartview1)

        chart2 =  QChart()
        series2 = QLineSeries()
        series2.append([QPointF(i[0], i[1]) for i in func2(1,250)])
        chart2.addSeries(series2)
        chart2.createDefaultAxes()
        chartview2 = QChartView(chart2)
        self.chartsLayout.addWidget(chartview2)

        chart3 =  QChart()
        series3 = QLineSeries()
        series3.append([QPointF(i[0], i[1]) for i in func3(1,250)])
        chart3.addSeries(series3)
        chart3.createDefaultAxes()
        chartview3 = QChartView(chart3)
        #self.chartsLayout.addWidget(chartview3)

        chart4 =  QChart()
        series4 = QLineSeries()
        series4.append([QPointF(i[0], i[1]) for i in func4(1,250)])
        chart4.addSeries(series4)
        chart4.createDefaultAxes()
        chartview4 = QChartView(chart4)
        #self.chartsLayout.addWidget(chartview4)

        chart5 =  QChart()
        series5 = QLineSeries()
        series5.append([QPointF(i[0], i[1]) for i in func5(1,250)])
        chart5.addSeries(series5)
        chart5.createDefaultAxes()
        chartview5 = QChartView(chart5)
        #self.chartsLayout.addWidget(chartview5)

        #self.chartsLayout = QVBoxLayout()
        #self.chartsLayout.addWidget(chart1)
        #self.chartsLayout.addWidget(chart2)
        #self.chartsLayout.addWidget(chart3)
        #self.chartsLayout.addWidget(chart4)
        #self.chartsLayout.addWidget(chart5)

        backgroundGradient = QLinearGradient()
        backgroundGradient.setStart(QPointF(0, 0))
        backgroundGradient.setColorAt(0.0, qRgb(0,0,0))
        #chart.legend().setVisible(True)
        #chart.legend().setAlignment(Qt.AlignBottom)
        #chartview = QChartView(chart)
        chartview1.setRenderHint(QPainter.Antialiasing)
        self.setCentralWidget(chartview1)
        chartview2.setRenderHint(QPainter.Antialiasing)
        self.setCentralWidget(chartview2)
        #series.setColor(QColor(qRgb(0,150,150)))
 
 
App = QApplication(sys.argv)
window = ClassCharts()
window.show()
sys.exit(App.exec())
 

 
