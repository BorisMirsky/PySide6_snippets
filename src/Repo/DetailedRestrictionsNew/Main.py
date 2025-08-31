from PySide6.QtWidgets import QWidget, QLabel, QCheckBox, QVBoxLayout, QApplication, QHBoxLayout, QGridLayout
from PySide6.QtCharts import QLineSeries, QVXYModelMapper, QChart, QChartView, QValueAxis
from PySide6.QtGui import QFont, Qt, QPen,QColor
from PySide6.QtCore import Qt, QObject, QCoreApplication, Signal, QObject, QEvent
import sys
#from ServiceInfo import DATA_LEN
from Charts import Chart2 #, Chart2   #ChartsWidget
from VerticalLine import VerticalLineModel1
from HorizontalLine import HorizontalLineModel
from ServiceInfo import *


class MainWidget(QWidget):
    def __init__(self, v_model:VerticalLineModel1):
        super().__init__()
        self.vertical_model = v_model
        grid = QGridLayout()
        #self.chart1 = Chart1('plan_prj', 'plan_fact', self.vertical_model)
        self.chart1 = self.chart1()
        chart2 = Chart2('plan_delta', self.vertical_model)
        grid.addLayout(self.chart1, 0, 0, 5, 8)
        grid.addWidget(chart2, 5, 0, 3, 8)
        rcw = self.rightColumnWidget()
        grid.addLayout(rcw, 1, 9, 1, 2)
        self.installEventFilter(self)
        self.currentPosition = 0
        self.setLayout(grid)
        self.setFocus()

    def rightColumnWidget(self):    
        vbox = QVBoxLayout()
        hbox1 = QHBoxLayout()
        hbox2 = QHBoxLayout()
        widget = QWidget()
        hbox1 = QHBoxLayout()
        hbox2 = QHBoxLayout()
        hbox3 = QHBoxLayout()
        hbox4 = QHBoxLayout()
        label_name = QLabel("План")
        label_name.setStyleSheet("font:bold; font-size:16pt;") # color:white;background-color:black")
        hbox1.addWidget(label_name)
        label_prj_name = QLabel("Проект")
        label_prj_name.setStyleSheet("font:bold; font-size:13pt; color:red;") #background-color:black")
        self.label_prj_value = QLabel()
        self.label_prj_value.setStyleSheet("font:bold; font-size:13pt; color:yellow; background-color:blue")
        self.label_prj_value.setMaximumHeight(25)
        hbox2.addWidget(label_prj_name)
        hbox2.addWidget(self.label_prj_value)
        label_fact_name = QLabel("Натура")
        label_fact_name.setStyleSheet("font:bold; font-size:13pt; color:green;")
        self.label_fact_value = QLabel()
        self.label_fact_value.setStyleSheet("font:bold; font-size:13pt; color:yellow; background-color:blue")
        self.label_fact_value.setMaximumHeight(25)
        hbox2.addWidget(label_fact_name)
        hbox2.addWidget(self.label_fact_value)
        self.checkBox_prj = QCheckBox() #"Проект")
        self.checkBox_prj.setChecked(True)
        self.checkBox_prj.stateChanged.connect(self.handleCheckBoxPrj)
        self.checkBox_fact = QCheckBox() #"Натура")
        self.checkBox_fact.setChecked(True)
        self.checkBox_fact.stateChanged.connect(self.handleCheckBoxFact)
        hbox3.addWidget(self.checkBox_prj)
        hbox3.addWidget(self.checkBox_fact)
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)
        return vbox
        #self.setLayout(vbox)


    def handleCheckBoxPrj(self, checked):
        if checked:
            self.series2.show()
        else:
            self.series2.hide()
        self.show()
 
    def handleCheckBoxFact(self, checked):
        if checked:
            self.series1.show()
        else:
            self.series1.hide()
        self.show()

    def chart1(self):
        self.vertical_model1 = VerticalLineModel1(1000)
        self.chart_column_name1 = 'plan_prj'
        self.chart = QChart()
        self.chart.legend().setVisible(False)
        self.data1 = get_csv_column(FILENAME, self.chart_column_name1)
        self.series1 = QLineSeries()
        for i in range(0, DATA_LEN, 1):
            self.series1.append(i, self.data1[i])
        self.x_start = 0
        self.x_stop = DATA_LEN  #
        self.setFocusPolicy(Qt.NoFocus)
        self.series1.setPen(QPen(Qt.GlobalColor.red, 2))
        self.chart.addSeries(self.series1)
        self.chart_column_name2 = 'plan_fact'
        self.data2 = get_csv_column(FILENAME, self.chart_column_name2)
        self.series2 = QLineSeries()
        for i in range(0, DATA_LEN, 1):
            self.series2.append(i, self.data2[i])
        self.series2.setPen(QPen(Qt.GlobalColor.green, 2))
        self.chart.addSeries(self.series2)
        y_axis = QValueAxis()
        y_axis.setRange(min(self.data1), max(self.data1))
        y_axis.setLabelFormat("%0.2f")
        y_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        y_axis.setTickInterval(20)
        y_axis.setTitleText("Вертикальные стрелы изгиба, мм")
        x_axis = QValueAxis()
        x_axis.setRange(self.x_start, self.x_stop)
        x_axis.setLabelFormat("%d")
        x_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        x_axis.setTickInterval(200)
        self.chart.addAxis(x_axis, Qt.AlignmentFlag.AlignBottom)
        self.chart.addAxis(y_axis, Qt.AlignmentFlag.AlignLeft)
        self.series1.attachAxis(x_axis)
        self.series1.attachAxis(y_axis)
        self.vertical_line_series1 = QLineSeries()
        self.vertical_line_series1.setPen(QPen(Qt.GlobalColor.magenta, 2))  # первая основная динамическая
        self.lineMapper1 = QVXYModelMapper(self)
        self.lineMapper1.setXColumn(0)
        self.lineMapper1.setYColumn(1)
        self.lineMapper1.setSeries(self.vertical_line_series1)
        self.lineMapper1.setModel(self.vertical_model1)
        self.chart.addSeries(self.vertical_line_series1)
        self.vertical_line_series1.attachAxis(x_axis)
        self.vertical_line_series1.attachAxis(y_axis)
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
        #self.setLayout(vbox)
        return vbox   #self.chart_view

    def eventFilter(self, watched: QObject, event: QEvent):
        if event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_D:
                self.vertical_model1.shiftLine(1)
                self.__returnData(1)
                return True
            elif event.key() == Qt.Key.Key_A:
                self.vertical_model1.shiftLine(-1)
                self.__returnData(-1)
                return True
        return False

    def __returnData(self, i: int):
        self.currentPosition += i
        self.label_prj_value.setNum(
            round(self.data1[self.currentPosition], 1))
        self.label_fact_value.setNum(
            round(self.data2[self.currentPosition], 1))




#if __name__ == '__main__':
app = QApplication(sys.argv)
MW = MainWidget(VerticalLineModel1(1000))
MW.show()
sys.exit(app.exec())

