
from PySide6.QtWidgets import QWidget, QListWidget, QListWidgetItem, QVBoxLayout, QApplication
from PySide6.QtCharts import QLineSeries, QVXYModelMapper, QChart, QChartView, QValueAxis
from PySide6.QtGui import QFont, QIcon, QShortcut, Qt, QPen, QPainter, QImage, QPixmap, QColor
from PySide6.QtCore import Qt, QTimer, QObject, QDateTime, QCoreApplication, Signal, QTimer
import sys
import numpy as np
from NumpyTableModel import NumpyTableModel
from VerticalLine import VerticalLineModel #1, VerticalLineModel2, VerticalLineModel3
from ServiceInfo import *



# верхний график с двумя нитками
class Chart1(QWidget):
    def __init__(self, chart_column_name1: str,
                 chart_column_name2:str,
                 model1:VerticalLineModel,
                 model2:VerticalLineModel,
                 model3:VerticalLineModel):
        super().__init__()
        self.vertical_model1 = model1
        self.vertical_model2 = model2
        self.vertical_model3 = model3
        self.chart_column_name1 = chart_column_name1
        self.chart = QChart()
        self.chart.legend().setVisible(False)
        self.data1 = get_csv_column(FILENAME, chart_column_name1)       #'plan_prj')
        self.series1 = QLineSeries()
        for i in range (0, DATA_LEN, 1):
            self.series1.append(i, self.data1[i])
        #
        self.x_start = 0
        self.x_stop = DATA_LEN
        self.setFocusPolicy(Qt.NoFocus)
        self.series1.setPen(QPen(Qt.GlobalColor.green, 2))
        self.chart.addSeries(self.series1)
        self.chart_column_name2 = chart_column_name2
        self.data2 = get_csv_column(FILENAME, chart_column_name2)
        self.series2 = QLineSeries()
        for i in range(0, DATA_LEN, 1):
            self.series2.append(i, self.data2[i])
        self.series2.setPen(QPen(Qt.GlobalColor.red, 2))
        self.chart.addSeries(self.series2)
        self.y_axis = QValueAxis()
        self.y_axis.setRange(min(self.data1), max(self.data1))
        self.y_axis.setLabelFormat("%0.2f")
        self.y_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        self.y_axis.setTickInterval(20)
        self.y_axis.setTitleText("Стрелы изгиба, мм")
        axisBrush = QBrush(Qt.GlobalColor.white)
        self.y_axis.setTitleBrush(axisBrush)
        self.x_axis = QValueAxis()
        self.x_axis.setRange(self.x_start, self.x_stop)
        self.x_axis.setLabelFormat("%d")
        self.x_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        self.x_axis.setTickInterval(200)
        self.chart.addAxis(self.x_axis, Qt.AlignmentFlag.AlignBottom)
        self.chart.addAxis(self.y_axis, Qt.AlignmentFlag.AlignLeft)
        self.series1.attachAxis(self.x_axis)
        self.series1.attachAxis(self.y_axis)
        self.series2.attachAxis(self.x_axis)
        self.series2.attachAxis(self.y_axis)
        #
        labelsFont = QFont()
        labelsFont.setPixelSize(12)
        self.x_axis.setLabelsFont(labelsFont)
        self.y_axis.setLabelsFont(labelsFont)
        self.x_axis.setLabelsBrush(axisBrush)
        self.y_axis.setLabelsBrush(axisBrush)
        #
        self.vertical_line_series1 = QLineSeries()
        self.vertical_line_series1.setPen(QPen(Qt.GlobalColor.magenta, 2))
        self.vertical_line_series2 = QLineSeries()
        self.vertical_line_series2.setPen(QPen(Qt.GlobalColor.magenta, 2))
        self.vertical_line_series3 = QLineSeries()
        self.vertical_line_series3.setPen(QPen(Qt.GlobalColor.yellow, 2))
        #
        self.lineMapper1 = QVXYModelMapper(self)
        self.lineMapper1.setXColumn(0)
        self.lineMapper1.setYColumn(1)
        self.lineMapper1.setSeries(self.vertical_line_series1)
        self.lineMapper1.setModel(self.vertical_model1)
        #
        self.lineMapper2 = QVXYModelMapper(self)
        self.lineMapper2.setXColumn(0)
        self.lineMapper2.setYColumn(1)
        self.lineMapper2.setSeries(self.vertical_line_series2)
        self.lineMapper2.setModel(self.vertical_model2)
        #
        self.lineMapper3 = QVXYModelMapper(self)
        self.lineMapper3.setXColumn(0)
        self.lineMapper3.setYColumn(1)
        self.lineMapper3.setSeries(self.vertical_line_series3)
        self.lineMapper3.setModel(self.vertical_model3)
        #
        self.chart.addSeries(self.vertical_line_series1)
        self.chart.addSeries(self.vertical_line_series2)
        self.chart.addSeries(self.vertical_line_series3)
        self.vertical_line_series1.attachAxis(self.x_axis)
        self.vertical_line_series1.attachAxis(self.y_axis)
        self.vertical_line_series2.attachAxis(self.x_axis)
        self.vertical_line_series2.attachAxis(self.y_axis)
        self.vertical_line_series3.attachAxis(self.x_axis)
        self.vertical_line_series3.attachAxis(self.y_axis)
        #
        self.chart_view = QChartView(self.chart)
        self.chart_view.chart().setBackgroundBrush(QBrush(QColor("black")))
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.chart_view)
        self.setLayout(self.vbox)

# one thread
class Chart2(QWidget):
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
        self.series1.setPen(QPen(Qt.GlobalColor.blue, 2))
        self.chart.addSeries(self.series1)
        self.setFocusPolicy(Qt.NoFocus)
        y_axis = QValueAxis()
        y_axis.setRange(min(self.data1), max(self.data1))
        y_axis.setLabelFormat("%0.2f")
        y_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        y_axis.setTickInterval(20)
        axisBrush = QBrush(Qt.GlobalColor.white)
        y_axis.setTitleBrush(axisBrush)
        y_axis.setTitleText("Сдвиги, мм")
        #
        self.x_axis = QValueAxis()
        self.x_axis.setRange(self.x_start, self.x_stop)
        self.x_axis.setLabelFormat("%d")
        self.x_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        self.x_axis.setTickInterval(200)
        #
        labelsFont = QFont()
        labelsFont.setPixelSize(12)
        self.x_axis.setLabelsFont(labelsFont)
        y_axis.setLabelsFont(labelsFont)
        self.x_axis.setLabelsBrush(axisBrush)
        y_axis.setLabelsBrush(axisBrush)
        #
        self.chart.addAxis(self.x_axis, Qt.AlignmentFlag.AlignBottom)
        self.chart.addAxis(y_axis, Qt.AlignmentFlag.AlignLeft)
        self.series1.attachAxis(self.x_axis)
        self.series1.attachAxis(y_axis)
        self.chart_view = QChartView(self.chart)
        self.chart_view.chart().setBackgroundBrush(QBrush(QColor("black")))
        vbox = QVBoxLayout()
        vbox.addWidget(self.chart_view)
        self.setLayout(vbox)

class ChartsWidget(QWidget):
    def __init__(self, chart1:QWidget, chart2:QWidget):
        super().__init__()
        self.x_start = 0
        self.x_stop = DATA_LEN
        self.zoomFactor = self.x_stop / 10
        self.zoom_value = 0
        self.chart1 = chart1
        self.chart2 = chart2
        vbox = QVBoxLayout()
        vbox.addWidget(self.chart1, 2)
        vbox.addWidget(self.chart2, 1)
        self.setLayout(vbox)

    def keyPressEvent(self, keyEvent):
        key = keyEvent.key()
        if key == Qt.Key_W and self.zoom_value < 10:
            self.x_start = self.x_start + self.zoomFactor
            self.x_stop = self.x_stop - self.zoomFactor
            self.chart1.x_axis.setRange(self.x_start, self.x_stop)
            self.chart2.x_axis.setRange(self.x_start, self.x_stop)
            self.zoom_value = self.zoom_value + 1
            print(self.x_start, self.x_stop, self.zoom_value, self.zoomFactor)
        elif key == Qt.Key_S and self.zoom_value > 0:
            self.x_start = self.x_start - self.zoomFactor
            self.x_stop = self.x_stop + self.zoomFactor
            self.chart1.x_axis.setRange(self.x_start, self.x_stop)
            self.chart2.x_axis.setRange(self.x_start, self.x_stop)
            self.zoom_value = self.zoom_value - 1
        elif key == Qt.Key_A and self.zoom_value > 0:  # to left
            self.x_start = self.x_start - self.zoomFactor
            self.x_stop = self.x_stop - self.zoomFactor
            self.chart1.x_axis.setRange(self.x_start, self.x_stop)
            self.chart2.x_axis.setRange(self.x_start, self.x_stop)
        if key == Qt.Key_D and self.zoom_value < 10:  # to right
            self.x_start = self.x_start + self.zoomFactor
            self.x_stop = self.x_stop + self.zoomFactor
            self.chart1.x_axis.setRange(self.x_start, self.x_stop)
            self.chart2.x_axis.setRange(self.x_start, self.x_stop)



# model1 = VerticalLineModel1(first_points[0])
# model2 = VerticalLineModel2(first_points[0])
#
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     c1 = Chart1('plan_prj', 'plan_fact', model1, model2)
#     c2 = Chart2('plan_delta')
#     window = ChartsWidget(c1, c2)
#     window.show()
#     c2.show()
#     sys.exit(app.exec())
