from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtCharts import *
import pandas as pd
import re
from ScrolledChart import ChartClass, ScrollChartClass
from VerticalLine import VerticalLineModel, MoveLineController

datafile = "example_csv_file.csv"

charts_dict = {1:['plan_mes','plan_prj', 'План'],
               2:['prof_mes','prof_prj', 'Уровень'],
               3:['vozv_mes','vozv_prj', 'Профиль'],
               4:['plan_d'],
               5:['prof_d']}



def read_csv_file( file, n):
    df = pd.read_csv(file)
    col = df.loc[:, n]
    return col.tolist()


class ScrollChartClass(QWidget):
    def __init__(self, chart):
        super().__init__()
        self.chart = chart
        self.initUI()

    def initUI(self):
        self.scroll = QScrollArea()
        self.hbox = QHBoxLayout()
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.chart)
        self.hbox.addWidget(self.scroll)
        self.setLayout(self.hbox)
        return


class Main(QWidget):
    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        self.inputCoord = None
        self.filename = datafile
        (self.current_x, self.lbl1, self.lbl2, self.lbl3, self.lbl4,
                                   self.lbl5, self.lbl6, self.lbl7, self.lbl8) = (QLabel('     '), QLabel('    '), QLabel('    '),
                                   QLabel('    '), QLabel('    '), QLabel('    '), QLabel('    '), QLabel('    '), QLabel('    '))
        self.createLeftWidget()
        self.initUI()


    def initUI(self):
        self.data1_1 = read_csv_file(self.filename, charts_dict[1][0])
        self.data1_2 = read_csv_file(self.filename, charts_dict[1][1])
        self.data2_1 = read_csv_file(self.filename, charts_dict[2][0])
        self.data2_2 = read_csv_file(self.filename, charts_dict[2][1])
        self.data3_1 = read_csv_file(self.filename, charts_dict[3][0])
        self.data3_2 = read_csv_file(self.filename, charts_dict[3][1])
        self.data4 = read_csv_file(self.filename, charts_dict[4][0])
        self.data5 = read_csv_file(self.filename, charts_dict[5][0])

        self.model = VerticalLineModel()
        self.model.positionChanged.connect(self.updateCurrentPositionInfo)
        #
        dataTableView = QTableView()
        dataTableView.setModel(self.model)
        #
        seriesData1_1 = QLineSeries()
        seriesData1_2 = QLineSeries()
        seriesData2_1 = QLineSeries()
        seriesData2_2 = QLineSeries()
        seriesData3_1 = QLineSeries()
        seriesData3_2 = QLineSeries()
        seriesData4 = QLineSeries()
        seriesData5 = QLineSeries()
        #
        seriesData1_1.setColor(QColor("green"))
        seriesData1_1.setName('plan_mes')
        seriesData1_2.setColor(QColor("red"))
        seriesData1_2.setName('plan_prj')
        seriesData2_1.setColor(QColor("green"))
        seriesData2_1.setName('prof_mes')
        seriesData2_2.setColor(QColor("red"))
        seriesData2_2.setName('prof_prj')
        seriesData3_1.setColor(QColor("green"))
        seriesData3_1.setName('vozv_mes')
        seriesData3_2.setColor(QColor("red"))
        seriesData3_2.setName('vozv_prj')
        seriesData4.setColor(QColor("green"))
        seriesData4.setName('plan_d')
        seriesData5.setColor(QColor("green"))
        seriesData5.setName('prof_d')

        for x in range(len(self.data1_1)):                            # для всех графиков одинаковая длина
            seriesData1_1.append(QPointF(x, self.data1_1[x]))
            seriesData1_2.append(QPointF(x, self.data1_2[x]))
            seriesData2_1.append(QPointF(x, self.data2_1[x]))
            seriesData2_2.append(QPointF(x, self.data2_2[x]))
            seriesData3_1.append(QPointF(x, self.data3_1[x]))
            seriesData3_2.append(QPointF(x, self.data3_2[x]))
            seriesData4.append(QPointF(x, self.data4[x]))
            seriesData5.append(QPointF(x, self.data5[x]))
        #
        verticalLine1 = QLineSeries()
        verticalLine2 = QLineSeries()
        verticalLine3 = QLineSeries()
        verticalLine4 = QLineSeries()
        verticalLine5 = QLineSeries()
        #
        self.lineMapper1 = QVXYModelMapper()
        self.lineMapper2 = QVXYModelMapper()
        self.lineMapper3 = QVXYModelMapper()
        self.lineMapper4 = QVXYModelMapper()
        self.lineMapper5 = QVXYModelMapper()
        #
        self.lineMapper1.setXColumn(0)
        self.lineMapper2.setXColumn(0)
        self.lineMapper3.setXColumn(0)
        self.lineMapper4.setXColumn(0)
        self.lineMapper5.setXColumn(0)
        #
        self.lineMapper1.setYColumn(1)
        self.lineMapper2.setYColumn(1)
        self.lineMapper3.setYColumn(1)
        self.lineMapper4.setYColumn(1)
        self.lineMapper5.setYColumn(1)
        #
        self.lineMapper1.setSeries(verticalLine1)
        self.lineMapper2.setSeries(verticalLine2)
        self.lineMapper3.setSeries(verticalLine3)
        self.lineMapper4.setSeries(verticalLine4)
        self.lineMapper5.setSeries(verticalLine5)
        self.lineMapper1.setModel(self.model)
        self.lineMapper2.setModel(self.model)
        self.lineMapper3.setModel(self.model)
        self.lineMapper4.setModel(self.model)
        self.lineMapper5.setModel(self.model)
        #
        x_axis = QValueAxis()
        x_axis.setRange(0.0, len(self.data1_1))
        #x_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        x_axis.setTickInterval(1)
        y_axis = QValueAxis()
        y_axis.setRange(min(self.data1_1), max(self.data1_1))
        y_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        y_axis.setTickInterval(20)
        #
        chart1 = QChart()
        chart2 = QChart()
        chart3 = QChart()
        chart4 = QChart()
        chart5 = QChart()
        #
        chart1.addSeries(seriesData1_1)
        chart1.addSeries(seriesData1_2)
        chart2.addSeries(seriesData2_1)
        chart2.addSeries(seriesData2_2)
        chart3.addSeries(seriesData3_1)
        chart3.addSeries(seriesData3_2)
        chart4.addSeries(seriesData4)
        chart5.addSeries(seriesData5)
        #
        chart1.createDefaultAxes()
        chart2.createDefaultAxes()
        chart3.createDefaultAxes()
        chart4.createDefaultAxes()
        chart5.createDefaultAxes()
        #
        chart1.addSeries(verticalLine1)
        chart2.addSeries(verticalLine2)
        chart3.addSeries(verticalLine3)
        chart4.addSeries(verticalLine4)
        chart5.addSeries(verticalLine5)
        #
        for axis in chart1.axes():
            verticalLine1.attachAxis(axis)
        for axis in chart2.axes():
            verticalLine2.attachAxis(axis)
        for axis in chart3.axes():
            verticalLine3.attachAxis(axis)
        for axis in chart4.axes():
            verticalLine4.attachAxis(axis)
        for axis in chart5.axes():
            verticalLine5.attachAxis(axis)

        #windowLayout.addWidget(dataTableView, 0, 0)
        view1 = QChartView(chart1)
        view1.setRenderHint(QPainter.Antialiasing)
        #vbox1 = QVBoxLayout()
        #vbox1.addWidget(view1)
        self.scroll1  = ScrollChartClass(view1)
        #
        GridLayout = QGridLayout()
        GridLayout.addWidget(self.leftWidget, 0, 0)
        GridLayout.addWidget(self.scroll1, 0, 1)
        GridLayout.addWidget(QChartView(chart2), 1, 1)
        GridLayout.addWidget(QChartView(chart3), 2, 1)
        GridLayout.addWidget(QChartView(chart4), 3, 1)
        GridLayout.addWidget(QChartView(chart5), 4, 1)

        #windowLayout.setColumnStretch(0, 1)
        GridLayout.setColumnStretch(1, 4)
        self.lineMover = MoveLineController(self.model)
        self.installEventFilter(self.lineMover)
        self.setLayout(GridLayout)


    def updateCurrentPositionInfo(self, position: float):
        self.current_x.setText(str(position))
        self.lbl1.setText(str(self.data1_1[int(position)]))
        self.lbl2.setText(str(self.data1_2[int(position)]))
        self.lbl3.setText(str(self.data2_1[int(position)]))
        self.lbl4.setText(str(self.data2_2[int(position)]))
        self.lbl5.setText(str(self.data3_1[int(position)]))
        self.lbl6.setText(str(self.data3_2[int(position)]))
        self.lbl7.setText(str(self.data4[int(position)]))
        self.lbl8.setText(str(self.data5[int(position)]))


    def createLeftWidget(self):
        leftLayout = QVBoxLayout()

        hbox0 = QHBoxLayout()
        lbl0name = QLabel('current X')
        hbox0.addWidget(lbl0name)
        hbox0.addWidget(self.current_x)
        leftLayout.addLayout(hbox0)

        hbox1 = QHBoxLayout()
        lbl1name = QLabel('plan_mes')
        hbox1.addWidget(lbl1name)
        hbox1.addWidget(self.lbl1)
        leftLayout.addLayout(hbox1)

        hbox2 = QHBoxLayout()
        lbl2name = QLabel('plan_prj')
        hbox2.addWidget(lbl2name)
        hbox2.addWidget(self.lbl2)
        leftLayout.addLayout(hbox2)

        hbox3 = QHBoxLayout()
        lbl3name = QLabel('prof_mes')
        hbox3.addWidget(lbl3name)
        hbox3.addWidget(self.lbl3)
        leftLayout.addLayout(hbox3)

        hbox4 = QHBoxLayout()
        lbl4name = QLabel('prof_prj')
        hbox4.addWidget(lbl4name)
        hbox4.addWidget(self.lbl4)
        leftLayout.addLayout(hbox4)

        hbox5 = QHBoxLayout()
        lbl5name = QLabel('vozv_mes')
        hbox5.addWidget(lbl5name)
        hbox5.addWidget(self.lbl5)
        leftLayout.addLayout(hbox5)

        hbox6 = QHBoxLayout()
        lbl6name = QLabel('vozv_prj')
        hbox6.addWidget(lbl6name)
        hbox6.addWidget(self.lbl6)
        leftLayout.addLayout(hbox6)

        hbox7 = QHBoxLayout()
        lbl7name = QLabel('plan_d')
        hbox7.addWidget(lbl7name)
        hbox7.addWidget(self.lbl7)
        leftLayout.addLayout(hbox7)

        hbox8 = QHBoxLayout()
        lbl8name = QLabel('prof_d')
        hbox8.addWidget(lbl8name)
        hbox8.addWidget(self.lbl8)
        leftLayout.addLayout(hbox8)

        leftLayout.addStretch(3)

        hbox9 = QVBoxLayout()
        lbl9name = QLabel('Переместиться\n на координату')
        hbox9.addWidget(lbl9name)
        self.line = QLineEdit()
        self.line.setFixedWidth(70)
        self.line.textChanged[str].connect(self.getInputNewCoord)
        hbox9.addWidget(self.line)
        leftLayout.addLayout(hbox9)

        self.leftWidget = QWidget()
        self.leftWidget.setLayout(leftLayout)

    def getInputNewCoord(self, data):
        self.inputCoord = data
        #self.updateCurrentPositionInfo(data)



if __name__ == "__main__":
    import sys
    app = QApplication([])
    w = Main()
    w.show()
    sys.exit(app.exec())
