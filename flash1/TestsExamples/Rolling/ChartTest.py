from PySide6.QtWidgets import QWidget, QListWidget, QListWidgetItem, QVBoxLayout, QApplication
from PySide6.QtCharts import QLineSeries, QVXYModelMapper, QChart, QChartView
from PySide6.QtGui import QFont, QIcon, QShortcut, Qt, QPen, QPainter, QImage, QPixmap, QColor
from PySide6.QtCore import Qt, QTimer, QObject, QDateTime, QCoreApplication, Signal, QTimer
#from Data import 'data.csv'
# from NumpyTableModel import NumpyTableModel
# from VerticalLine2 import MoveLineController, VerticalLineModel
import sys
import numpy as np
import pandas as pd
#import warnings
#warnings.filterwarnings("ignore", category=DeprecationWarning)
#from ModelTable import *
#import math



def read_csv_file(filename):
    df = pd.read_csv(filename, sep=";")
    return df

def get_csv_column(filename, column_name):
    df = read_csv_file(filename)
    column = df.loc[:, column_name]
    return column.tolist()

FILENAME = 'data.csv'
DATA_LEN = len(get_csv_column(FILENAME, 'vozv_prj'))

chart_names = [['plan_fact', 'plan_prj'],
                'plan_delta',
                ['vozv_fact', 'vozv_prj'],
                ['prof_fact', 'prof_prj'],
                'prof_delta']


class Chart1(QWidget):
    def __init__(self, chart_column_name1: str):
        super().__init__()
        self.x_start = 0
        self.x_stop = DATA_LEN
        self.chart_column_name1 = chart_column_name1
        self.chart = QChart()
        self.chart.legend().setVisible(False)
        self.data1 = get_csv_column(FILENAME, chart_column_name1)
        self.series1 = QLineSeries()
        for i in range (0, DATA_LEN, 1):
            self.series1.append(i, self.data1[i])
        #self.series1.setPen(QPen(Qt.GlobalColor.blue, 2))
        self.chart.addSeries(self.series1)
        self.chart.createDefaultAxes()
        self.chart.axisX().setRange(self.x_start, self.x_stop)
        self.chart.axisY().setRange(min(self.data1), max(self.data1))
        #self.setFocusPolicy(Qt.NoFocus)
        self.chart_view = QChartView(self.chart)
        vbox = QVBoxLayout()
        vbox.addWidget(self.chart_view)
        self.setLayout(vbox)

# верхний график с двумя нитками
class Chart2(QWidget):
    def __init__(self, chart_column_name1: str,
                 chart_column_name2:str):
                 #model1:VerticalLineModel1,
                 #model2:VerticalLineModel2):
        super().__init__()
        #self.vertical_model1 = model1
        #self.vertical_model2 = model2
        self.chart_column_name1 = chart_column_name1
        self.chart = QChart()
        self.chart.legend().setVisible(False)
        self.x_start = 0
        self.x_stop = DATA_LEN
        self.data1 = get_csv_column(FILENAME, chart_column_name1) #'plan_prj')
        self.series1 = QLineSeries()
        for i in range (0, DATA_LEN, 1):
            self.series1.append(i, self.data1[i])
        self.series1.setPen(QPen(Qt.GlobalColor.green, 2))
        self.chart.addSeries(self.series1)
        self.chart_column_name2 = chart_column_name2
        self.data2 = get_csv_column(FILENAME, chart_column_name2)
        self.series2 = QLineSeries()
        for i in range(0, DATA_LEN, 1):
            self.series2.append(i, self.data2[i])
        self.series2.setPen(QPen(Qt.GlobalColor.red, 2))
        self.chart.addSeries(self.series2)
        self.chart.createDefaultAxes()
        #
        self.chart.axisX().setRange(self.x_start, self.x_stop)
        self.chart.axisY().setRange(min(self.data1), max(self.data1))
        self.chart_view = QChartView(self.chart)
        vbox = QVBoxLayout()
        vbox.addWidget(self.chart_view)
        self.setLayout(vbox)




if __name__ == '__main__':
    app = QApplication(sys.argv)
    #window = Chart1(chart_names[1])
    window = Chart1('plan_delta') #chart_names[0][0], chart_names[0][1])
    window.show()
    sys.exit(app.exec())