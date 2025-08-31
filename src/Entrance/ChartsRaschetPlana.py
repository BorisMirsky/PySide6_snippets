from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtCharts import *
import csv
import pandas as pd
import random
from random import uniform
import math

#file = "example_csv_file.csv"
charts_dict = {1:['plan_mes','plan_prj', 'План'],
               2:['prof_mes','prof_prj', 'Уровень'],
               3:['vozv_mes','vozv_prj', 'Профиль'],
               4:['plan_d'],
               5:['prof_d']}


class ChartClass(QWidget):
    def __init__(self, file, n):
        super().__init__()
        self.setStyleSheet("margin:5px; border:1px solid rgb(0, 0, 0); ")
        self.resize(2000, 250)
        self.file = file
        self.n = n
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        try:
            view = self.create_linechart(self.file, self.n)  # n
            layout.addWidget(view)
            self.setLayout(layout)
        except TypeError:
            pass

    def read_csv_file(self, file, n):
        try:
            df = pd.read_csv(file)
            col = df.loc[:, n]
            print(col.tolist())
            print('')
            print(col)
            print('')
            print(type(col.tolist()), type(col))
            return col.tolist()
        except FileNotFoundError:
            pass

    def create_linechart(self, file, n):
        data2 = None
        title = None
        if n in [1,2,3]:
            data1 = self.read_csv_file(file, charts_dict[n][0])
            data2 = self.read_csv_file(file, charts_dict[n][1])
            title = charts_dict[n][2]
        else:
            data1 = self.read_csv_file(file, charts_dict[n][0])
        y_axis = QValueAxis()
        y_axis.setRange(min(data1), max(data1))
        #y_axis.setLabelFormat("%1.0f")
        y_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        y_axis.setTickInterval(20)
        x_axis = QValueAxis()
        x_axis.setRange(0.0, len(data1))
        #x_axis.setLabelFormat("%1.0f")
        #x_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        x_axis.setTickInterval(1)
        series1 = QLineSeries()
        series2 = QLineSeries()
        for i in range(0, len(data1)):
            series1.append(i, data1[i])
            if data2:
                series2.append(i, data2[i])
            #print(data[i])
        chart = QChart()
        self._chart = chart
        #      title.   .setAlignment(Qt.AlignmentFlag)
        chart.setTitle(title)
        chart.setTitleFont(QFont('Impact', 16, QFont.Bold))  # QFont.italic))
        chart.legend().hide()
        chart.addAxis(x_axis, Qt.AlignmentFlag.AlignBottom)
        chart.addAxis(y_axis, Qt.AlignmentFlag.AlignLeft)
        chart.legend().setVisible(True)
        chart.layout().setContentsMargins(0,0,0,0)   #
        chart.setMargins(QMargins())
        series1.setColor(QColor("green"))
        series2.setColor(QColor("red"))
        chart.addSeries(series1)
        chart.addSeries(series2)
        chart.createDefaultAxes()
        chart.setMinimumWidth(500)

        chartview = QChartView(chart)
        chartview.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        chartview.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        return chartview

class VerticalLineModel(QAbstractTableModel):
    def __init__(startX: float = 0, yMin: float = -200, yMax: float = 200, parent: QObject = None):
        super().__init__(parent)
        self.__currentX = startX
        self.__yMin = yMin
        self.__yMax = yMax

    def rowCount(self, parent, PySide6_QtCore_QModelIndex=None, PySide6_QtCore_QPersistentModelIndex=None, *args, **kwargs):
        return 2
    def columnCount(self, parent, PySide6_QtCore_QModelIndex=None, PySide6_QtCore_QPersistentModelIndex=None, *args, **kwargs):
        return 2
    def data(self, index, PySide6_QtCore_QModelIndex=None, PySide6_QtCore_QPersistentModelIndex=None, *args, **kwargs):
        if not index.isValid():
            return None

        if index.row() == 0 and index.column() == 0:
            return self.__currentX
        elif index.row() == 1 and index.column() == 0:
            return self.__currentX
        elif index.row() == 0 and index.column() == 1:
            return self.__yMin
        elif index.row() == 1 and index.column() == 1:
            return self.__yMax
        else:
            return None

    def moveLine(self, xDiff: float):
        self.__currentX += xDiff
        self.dataChanged()

class DynamicChart(QChart):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.__series = QLineSeries()
        self.__axisX = QValueAxis()
        self.__axisY = QValueAxis()
        self.addSeries(self.__series)
        self.addAxis(self.__axisX, Qt.AlignmentFlag.AlignBottom)
        self.addAxis(self.__axisY, Qt.AlignmentFlag.AlignLeft)
        self.__series.attachAxis(self.__axisX)
        self.__series.attachAxis(self.__axisY)
        self.__axisX.setRange(0, 10)
        self.__axisY.setRange(-5, 10)

        for index in range(100):
            self.__series.append(index, math.sin(index))


class DoubleChartView(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.__currentLineX = 20
        self.__chart_1 = QChart()
        self.__chart_2 = QChart()

        generator = QRandomGenerator()
        self.__data_1 = QLineSeries()
        self.__data_2 = QLineSeries()
        for i in range(100):
            self.__data_1.append(QPointF(i, generator.bounded(2) + 1))
            self.__data_2.append(QPointF(i, generator.bounded(2) + 1))
        self.__axisX = QValueAxis()
        self.__axisY = QValueAxis()
        self.__chart_1.addSeries(self.__data_1)
        self.__chart_2.addSeries(self.__data_2)
        #self.__chart_1.addAxis(self.__axisX, Qt.AlignmentFlag.AlignBottom)
        #self.__chart_1.addAxis(self.__axisY, Qt.AlignmentFlag.AlignLeft)
        #self.__chart_2.addAxis(self.__axisX, Qt.AlignmentFlag.AlignBottom)
        #self.__chart_2.addAxis(self.__axisY, Qt.AlignmentFlag.AlignLeft)
        #self.__data_1.attachAxis(self.__axisX)
        #self.__data_1.attachAxis(self.__axisY)
        #self.__data_2.attachAxis(self.__axisX)
        #self.__data_2.attachAxis(self.__axisY)
        self.__windowLayout = QVBoxLayout()
        self.__windowLayout.addWidget(QChartView(self.__chart_1))
        self.__windowLayout.addWidget(QChartView(self.__chart_2))
        self.setLayout(self.__windowLayout)
        #
        self.__line = QLineSeries()
        self.__line.setPen(QPen(QBrush(Qt.GlobalColor.darkMagenta), 4))
        self.__line.replace([QPointF(20, -200), QPointF(20, 200)])
        #self.move_line(0)
        self.__chart_1.addSeries(self.__line)
        self.__chart_2.addSeries(self.__line)

        self.__chart_1.createDefaultAxes()
        self.__chart_2.createDefaultAxes()

        #self.chart_1._chart.addSeries(self.__line)
        #self.chart_2._chart.addSeries(self.__line)
        # for axis in self.__chart_1.axes():
        #     self.__line.attachAxis(axis)
        # for axis in self.__chart_2.axes():
        #     self.__line.attachAxis(axis)

        self.__line_move_timer = QTimer()
        self.__line_move_timer.timeout.connect(lambda: self.move_line(0.1))
        self.__line_move_timer.timeout.connect(lambda: print("he-he"))
        self.__line_move_timer.start(100)

    def move_line(self, xDiff: float):
        self.__currentLineX += xDiff
        print(f'Move line to x: {self.__currentLineX}')
        self.__line.replace([QPointF(self.__currentLineX, -200), QPointF(self.__currentLineX, 200)])


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    #gallery = DoubleChartView()
    gallery = QChartView(DynamicChart())
    gallery.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
    #gallery = ChartClass("example_csv_file.csv", 2)
    gallery.show()
    sys.exit(app.exec())