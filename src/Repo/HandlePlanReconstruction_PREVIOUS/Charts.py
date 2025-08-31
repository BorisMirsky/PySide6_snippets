
from PySide6.QtWidgets import QWidget, QListWidget, QListWidgetItem, QVBoxLayout, QApplication
from PySide6.QtCharts import QLineSeries, QVXYModelMapper, QChart, QChartView, QValueAxis
from PySide6.QtGui import QFont, QIcon, QShortcut, Qt, QPen, QPainter, QImage, QPixmap, QColor
from PySide6.QtCore import Qt, QTimer, QObject, QDateTime, QCoreApplication, Signal, QTimer
import sys
import numpy as np
from NumpyTableModel import NumpyTableModel
from VerticalLine import VerticalLineModel1, VerticalLineModel2 #, MoveLineController
from HorizontalLine import HorizontalLineModel
from ServiceInfo import *


# верхний график с двумя нитками
class Chart1(QWidget):
    def __init__(self, chart_column_name1: str,
                 chart_column_name2:str):
        super().__init__()
        self.chart_column_name1 = chart_column_name1
        self.chart = QChart()
        self.chart.legend().setVisible(False)
        self.data1 = get_csv_column(FILENAME, chart_column_name1)
        self.series1 = QLineSeries()
        for i in range (0, DATA_LEN, 1):
            self.series1.append(i, self.data1[i])
        #
        self.x_start = 0
        self.x_stop = DATA_LEN
        self.zoomFactor = self.x_stop / 10
        self.zoom_value = 0
        #
        self.setFocusPolicy(Qt.NoFocus)

        self.series1.setPen(QPen(Qt.GlobalColor.green, 2))
        self.chart.addSeries(self.series1)
        #
        self.chart_column_name2 = chart_column_name2
        self.data2 = get_csv_column(FILENAME, chart_column_name2)
        self.series2 = QLineSeries()
        for i in range(0, DATA_LEN, 1):
            self.series2.append(i, self.data2[i])
        self.series2.setPen(QPen(Qt.GlobalColor.red, 2))
        self.chart.addSeries(self.series2)
        #self.chart.createDefaultAxes()
        #
        #self.chart.axisX().setRange(self.x_start, self.x_stop)
        #self.chart.axisY().setRange(min(self.data1), max(self.data1))

        y_axis = QValueAxis()
        y_axis.setRange(min(self.data1), max(self.data1))
        y_axis.setLabelFormat("%0.2f")
        y_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        y_axis.setTickInterval(20)
        y_axis.setTitleText("Вертикальные стрелы изгиба, мм")
        #
        x_axis = QValueAxis()
        x_axis.setRange(self.x_start, self.x_stop)
        x_axis.setLabelFormat("%d")
        x_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        x_axis.setTickInterval(200)
        self.chart.addAxis(x_axis, Qt.AlignmentFlag.AlignBottom)
        self.chart.addAxis(y_axis, Qt.AlignmentFlag.AlignLeft)
        self.series1.attachAxis(x_axis)
        self.series1.attachAxis(y_axis)
        #
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
    def __init__(self,
                 chart_column_name1: str,
                 v_model1: VerticalLineModel1):    #v_model2: VerticalLineModel2,  #h_model: HorizontalLineModel):
        super().__init__()
        self.vertical_model1 = v_model1
        #self.vertical_model2 = v_model2
        #self.horizontal_model = h_model
        self.chart_column_name1 = chart_column_name1
        self.chart = QChart()
        self.chart.legend().setVisible(False)
        self.data1 = get_csv_column(FILENAME, chart_column_name1)
        self.series1 = QLineSeries()
        for i in range (0, DATA_LEN, 1):
            self.series1.append(i, self.data1[i])
        #
        self.x_start = 0
        self.x_stop = DATA_LEN
        self.zoomFactor = self.x_stop / 10
        self.zoom_value = 0
        self.setFocusPolicy(Qt.NoFocus)
        self.series1.setPen(QPen(Qt.GlobalColor.green, 2))
        self.chart.addSeries(self.series1)
        self.series2 = QLineSeries()
        #
        self.first_point_horizontal_line = None
        self.second_point_horizontal_line = None
        #
        y_axis = QValueAxis()
        y_axis.setRange(min(self.data1), max(self.data1))
        y_axis.setLabelFormat("%0.2f")
        y_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        y_axis.setTickInterval(10)
        y_axis.setTitleText("Сдвиги, мм")
        axisBrush = QBrush(Qt.GlobalColor.black)
        y_axis.setTitleBrush(axisBrush)
        #
        x_axis = QValueAxis()
        x_axis.setRange(self.x_start, self.x_stop)
        x_axis.setLabelFormat("%d")
        x_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        x_axis.setTickInterval(100)
        self.chart.addAxis(x_axis, Qt.AlignmentFlag.AlignBottom)
        self.chart.addAxis(y_axis, Qt.AlignmentFlag.AlignLeft)
        self.series1.attachAxis(x_axis)
        self.series1.attachAxis(y_axis)
        #
        labelsFont = QFont()
        labelsFont.setPixelSize(12)
        x_axis.setLabelsFont(labelsFont)
        y_axis.setLabelsFont(labelsFont)
        x_axis.setLabelsBrush(axisBrush)
        y_axis.setLabelsBrush(axisBrush)
        #
        self.vertical_line_series1 = QLineSeries()
        self.vertical_line_series1.setPen(QPen(Qt.GlobalColor.magenta, 3))
        self.vertical_line_series2 = QLineSeries()
        self.vertical_line_series2.setPen(QPen(Qt.GlobalColor.magenta, 3))
        self.horizontal_line_series = QLineSeries()
        self.horizontal_line_series.setPen(QPen(Qt.GlobalColor.magenta, 3))
        #
        self.lineMapper1 = QVXYModelMapper(self)
        self.lineMapper1.setXColumn(0)
        self.lineMapper1.setYColumn(1)
        self.lineMapper1.setSeries(self.vertical_line_series1)
        self.lineMapper1.setModel(self.vertical_model1)
        #
        self.chart.addSeries(self.vertical_line_series1)
        self.chart.addSeries(self.vertical_line_series2)
        self.chart.addSeries(self.horizontal_line_series)
        self.vertical_line_series1.attachAxis(x_axis)
        self.vertical_line_series1.attachAxis(y_axis)
        self.vertical_line_series2.attachAxis(x_axis)
        self.vertical_line_series2.attachAxis(y_axis)
        self.horizontal_line_series.attachAxis(x_axis)
        self.horizontal_line_series.attachAxis(y_axis)
        #
        self.chart_view = QChartView(self.chart)
        vbox = QVBoxLayout()
        vbox.addWidget(self.chart_view)
        self.setLayout(vbox)

    def eventFilter(self, watched: QObject, event: QEvent):
        if event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_D:
                #self.__line1.shiftLine(1)
                self.vertical_model1.shiftLine(1)
                return True
            elif event.key() == Qt.Key.Key_A:
                #self.__line1.shiftLine(-1)
                self.vertical_model1.shiftLine(-1)
                return True
            elif event.key() == (Qt.Key.Key_D and Qt.Key.Key_Control) or event.key() == (Qt.Key.Key_A and Qt.Key.Key_Control):
                self.lineMapper2 = QVXYModelMapper(self)
                self.lineMapper2.setXColumn(0)
                self.lineMapper2.setYColumn(1)
                self.lineMapper2.setSeries(self.vertical_line_series2)
                self.vertical_model2 = VerticalLineModel2(self.vertical_model1.currentX())
                self.lineMapper2.setModel(self.vertical_model2)
                self.first_point_horizontal_line = self.vertical_model1.currentX()
                #self.second_point_horizontal_line = None
                #print('Key_D/Key_A + Key_Control', self.vertical_model1.currentX())
                return True
        if event.type() == QEvent.Type.KeyRelease:
            if event.key() == (Qt.Key.Key_D and Qt.Key.Key_Control) or event.key() == (Qt.Key.Key_A and Qt.Key.Key_Control):
                self.lineMapper3 = QVXYModelMapper(self)
                self.lineMapper3.setXColumn(0)
                self.lineMapper3.setYColumn(1)
                self.second_point_horizontal_line = self.vertical_model1.currentX()
                self.lineMapper3.setSeries(self.horizontal_line_series)
                self.horizontal_model = HorizontalLineModel(30,
                                                            min(self.first_point_horizontal_line,  self.second_point_horizontal_line),
                                                            max(self.first_point_horizontal_line, self.second_point_horizontal_line)
                                                            )
                self.lineMapper3.setModel(self.horizontal_model)
                print(self.first_point_horizontal_line,  self.second_point_horizontal_line)
                return True
        return False





# model1 = VerticalLineModel1(1000)    #first_points[0])
# model2 = VerticalLineModel2()
# model3 = HorizontalLineModel()
#
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     #c1 = Chart1('plan_prj', 'plan_fact')
#     c2 = Chart2('plan_delta', model1, model2,model3)
#     c2.show()
#     sys.exit(app.exec())
