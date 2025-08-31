from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtCharts import *
from VerticalLine import MoveLineController, VerticalLineModel
import csv
import pandas as pd
import random
from random import uniform
import sys



DATAFILE = "example_csv_file.csv"
charts_dict = {1:['plan_mes','plan_prj', 'План'],
               2:['prof_mes','prof_prj', 'Уровень'],
               3:['vozv_mes','vozv_prj', 'Профиль'],
               4:['plan_d'],
               5:['prof_d']}



def read_csv_file( file, n):
    try:
        df = pd.read_csv(file)
        col = df.loc[:, n]
        return col.values.tolist()
    except FileNotFoundError:
        pass


length_of_chart = len(read_csv_file(DATAFILE, charts_dict[1][0]))

model = VerticalLineModel()

class ScrollChartClass(QWidget):
    def __init__(self, chart):
        super().__init__()
        self.chart = chart
        self.init_UI()
        self.len_of_file = 0

    def init_UI(self):
        self.scroll = QScrollArea()
        self.hbox = QHBoxLayout()
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setWidgetResizable(False)
        self.scroll.sizePolicy()
        self.scroll.setWidget(self.chart)
        self.hbox.addWidget(self.scroll)
        self.setLayout(self.hbox)
        return


class ChartClass(QWidget):
    def __init__(self, file, n):
        super().__init__()
        self.resize(length_of_chart * 20, 135)
        self.file = file
        self.n = n
        self.init_UI()
        self.current_position = 0

    def init_UI(self):
        layout = QVBoxLayout()
        #self.model = VerticalLineModel()
        #model.positionChanged.connect(self.updateCurrentPositionInfo)
        self.lineMover = MoveLineController(model)
        self.installEventFilter(self.lineMover)

        try:
            view = self.create_linechart(self.file, self.n)  # n
            layout.addWidget(view)
            self.setLayout(layout)
        except TypeError:
            pass

    #def updateCurrentPositionInfo(self, position: float):
        # self.current_position = position
    #    return position

    def create_linechart(self, file, n):
        data1, data2, title = None, None, None
        seriesData1, seriesData2 = QLineSeries(), QLineSeries()
        pen = QPen()
        pen.setWidth(2)
        seriesData1.setPen(pen)
        seriesData2.setPen(pen)
        if n in [1,2,3]:
            data1 = read_csv_file(file, charts_dict[n][0])
            data2 = read_csv_file(file, charts_dict[n][1])
            title = charts_dict[n][2]
            seriesData1.setColor(QColor("green"))
            seriesData1.setName(charts_dict[n][0])
            seriesData2.setColor(QColor("red"))
            seriesData2.setName(charts_dict[n][1])
            for x in range(len(data1)):
                seriesData1.append(QPointF(x, data1[x]))
                seriesData2.append(QPointF(x, data2[x]))
        else:
            data1 = read_csv_file(file, charts_dict[n][0])
            title = charts_dict[n][0]
            seriesData1.setColor(QColor("green"))
            seriesData1.setName(charts_dict[n][0])
            for x in range(len(data1)):
                seriesData1.append(QPointF(x, data1[x]))

        x_axis = QValueAxis()
        x_axis.setRange(0.0, len(data1))
        x_axis.setTickInterval(1)
        y_axis = QValueAxis()
        y_axis.setRange(min(data1), max(data1))
        y_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        y_axis.setTickInterval(20)

        verticalLine = QLineSeries()                                 #
        lineMapper = QVXYModelMapper(self)
        lineMapper.setXColumn(0)
        lineMapper.setYColumn(1)
        lineMapper.setSeries(verticalLine)
        lineMapper.setModel(model)

        chart = QChart()
        chart.addAxis(x_axis, Qt.AlignmentFlag.AlignBottom)
        chart.addAxis(y_axis, Qt.AlignmentFlag.AlignLeft)
        chart.legend().setVisible(False)
        chart.layout().setContentsMargins(0, 0, 0, 0)
        chart.addSeries(seriesData1)
        chart.addSeries(seriesData2)
        chart.createDefaultAxes()
        chart.addSeries(verticalLine)                                   #
        chart.setTitle(title)
        chart.setTitleFont(QFont('Impact', 9, QFont.Bold))
        for axis in chart.axes():                                        #
            verticalLine.attachAxis(axis)                                #
        view = QChartView(chart)
        view.setRenderHint(QPainter.Antialiasing)
        chartview = QChartView(chart)
        return chartview


if __name__ == '__main__':
    app = QApplication(sys.argv)
    chart = ChartClass(DATAFILE, 3)
    scroll = ScrollChartClass(chart)
    scroll.show()
    sys.exit(app.exec())

