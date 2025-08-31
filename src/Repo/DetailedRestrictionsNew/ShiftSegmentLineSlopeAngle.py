
from PySide6.QtWidgets import QWidget, QListWidget, QListWidgetItem, QVBoxLayout, QApplication, QHBoxLayout, QSpinBox
from PySide6.QtCharts import QLineSeries, QVXYModelMapper, QChart, QChartView, QValueAxis, QAreaSeries
from PySide6.QtGui import QFont, QIcon, QShortcut, Qt, QPen, QPainter, QImage, QPixmap, QColor, QKeySequence, QBrush
from PySide6.QtCore import Qt, QTimer, QObject, QDateTime, QCoreApplication, Signal, QTimer, QEvent
import sys
import numpy as np
from VerticalLine import VerticalLineModel1, VerticalLineModel2

"""
при обновлении графика оставлять предыдущие сегменты
Очищать (перерисовывать) только в диапазоне [self.start_point, self.counter]



отмена последнего действия

наклонные линии
"""

class ChartWindow(QWidget):
    def __init__(self,
                 chart_column_name3: str,
                 v_model1: VerticalLineModel1):
        super().__init__()
        self.counter = 0
        self.start_point_y = 30
        self.start_point = 0
        self.vertical_model2_flag=False
        self.resize(700, 500)
        self.vertical_model1 = v_model1
        self.chart_column_name = chart_column_name3
        self.chart = QChart()
        self.chart.legend().setVisible(False)
        self.x_start = 0
        self.x_stop = 500
        self.first_point_horizontal_line = None
        self.second_point_horizontal_line = None
        self.y_axis = QValueAxis()
        self.y_axis.setRange(0, 50)
        self.y_axis.setLabelFormat("%0.2f")
        self.y_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        self.y_axis.setTickInterval(10)
        axisBrush = QBrush(Qt.GlobalColor.black)
        self.y_axis.setTitleBrush(axisBrush)
        self.x_axis = QValueAxis()
        self.x_axis.setRange(self.x_start, self.x_stop)
        self.x_axis.setLabelFormat("%d")
        self.x_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        self.x_axis.setTickInterval(100)
        self.chart.addAxis(self.x_axis, Qt.AlignmentFlag.AlignBottom)
        self.chart.addAxis(self.y_axis, Qt.AlignmentFlag.AlignLeft)
        labelsFont = QFont()
        labelsFont.setPixelSize(12)
        self.x_axis.setLabelsFont(labelsFont)
        self.y_axis.setLabelsFont(labelsFont)
        self.x_axis.setLabelsBrush(axisBrush)
        self. y_axis.setLabelsBrush(axisBrush)

        # прямая красная
        self.straight_line_series = QLineSeries()
        self.data = [[None, None] for _ in range(700)]
        for i in range (0, 700, 1):
            self.data[i][0] = i
            self.data[i][1] = 30
            self.straight_line_series.append(self.data[i][0], self.data[i][1])
        
        self.straight_line_series.setPen(QPen(Qt.GlobalColor.red, 1))
        self.chart.addSeries(self.straight_line_series)
        self.straight_line_series.attachAxis(self.x_axis)
        self.straight_line_series.attachAxis(self.y_axis)
       #
        self.vertical_line_series1 = QLineSeries()
        self.vertical_line_series1.setPen(QPen(Qt.GlobalColor.magenta, 2))   # первая динамическая
        self.vertical_line_series2 = QLineSeries()
        self.vertical_line_series2.setPen(QPen(Qt.GlobalColor.magenta, 2))  # вторая статичная
        self.area_series = QAreaSeries(self.vertical_line_series1, self.vertical_line_series2)
        self.area_series.setPen(QPen(Qt.GlobalColor.magenta, 2))
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
        #
        # self.lineMapper3 = QVXYModelMapper(self)
        # self.lineMapper3.setXColumn(0)
        # self.lineMapper3.setYColumn(1)
        # self.lineMapper3.setSeries(self.area_series)
        #
        self.chart.addSeries(self.vertical_line_series1)
        self.chart.addSeries(self.vertical_line_series2)
        self.chart.addSeries(self.straight_line_series)
        # self.chart.addSeries(self.area_series)

        self.vertical_line_series1.attachAxis(self.x_axis)
        self.vertical_line_series1.attachAxis(self.y_axis)
        self.vertical_line_series2.attachAxis(self.x_axis)
        self.vertical_line_series2.attachAxis(self.y_axis)
        self.straight_line_series.attachAxis(self.x_axis)
        self.straight_line_series.attachAxis(self.y_axis)
        # self.straight_line_series.attachAxis(self.area_series)
        # self.straight_line_series.attachAxis(self.area_series)
        #
        right_column = self.right_column()
        self.installEventFilter(self)
        chart_view = QChartView(self.chart)
        hbox = QHBoxLayout()
        hbox.addWidget(chart_view, 5)
        hbox.addWidget(right_column, 1)
        self.setLayout(hbox)
        self.setFocus()

    def right_column(self):
        sb = QSpinBox()
        sb.setRange(-100,100)
        sb.setValue(0)
        sb.valueChanged.connect(self.__handleSpinBox)
        return sb

    def line_equation(self, x1, y1, x2, y2):
        #if x1 == x2:
        #    return (-x1, x1 ** 2)  #f"x = {x1}" # Вертикальная линия
        #elif y1 == y2:
        #    return (0, y1)   #f"y = {y1}" # Горизонтальная линия
        #else:
        slope = (y2 - y1) / (x2 - x1)
        intercept = y1 - slope * x1
        return (slope, intercept) 

    def __handleSpinBox(self, value):
        #self.straight_line_series.clear()
        #for i in range(self.start_point, self.counter, 1):
        #    self.data = None
        new_line = 30 + value 
        #result = self.line_equation(self.start_point, self.start_point_y, self.counter, new_line)
        #print((self.start_point, 30), (self.counter, new_line))
        for i in range(0, 700, 1):
            if i < self.start_point:
                self.straight_line_series.append(i, 30)
            elif self.start_point <= i <= self.counter:
                #if self.start_point == self.counter:                # vertical
                #    pass
                #if self.start_point_y == 30:                         # horizontal
                #    pass
                #if self.start_point != self.counter and self.start_point_y != 30:
                #    result = self.line_equation(self.start_point, self.start_point_y, self.counter, new_line)
                    #self.straight_line_series.append(i, (result[0] * i) + result[1])
                #self.straight_line_series.append(i, new_line)
                for i in range(self.start_point, self.counter, 1):
                    self.data[i][0],self.data[i][1]  = None, None
                    self.data[i][0],self.data[i][1]  = i, new_line
            elif i > self.counter:
                self.straight_line_series.append(i, 30)
            #
            self.straight_line_series.append(self.data[i][0], self.data[i][1])
            



    def eventFilter(self, watched: QObject, event: QEvent):
        if event.type() == QEvent.Type.KeyPress:
            self.setFocus()
            # Двигаем вертикальную черту
            if event.key() == Qt.Key.Key_Right:
                self.vertical_model1.shiftLine(1)
                self.counter+=1
                #if self.vertical_model2_flag:
               #     self.__drawAreaSeries(self.start_point, self.counter)
                return True
            elif event.key() == Qt.Key.Key_Left:
                self.vertical_model1.shiftLine(-1)
                self.counter-=1
                return True
            elif event.key() == Qt.Key.Key_D:
                self.vertical_model2 = VerticalLineModel1
                self.lineMapper2.setModel(self.vertical_model2(self.counter))
                self.start_point = self.counter
                self.vertical_model2_flag=True
                return True
            # elif event.key() == Qt.Key.Key_Escape:
            #     self.vertical_line_series2.hide()
            #     return True
        return False



model1 = VerticalLineModel1

if __name__ == '__main__':
    app = QApplication(sys.argv)
    cw = ChartWindow('plan_delta', model1(0))
    cw.show()
    sys.exit(app.exec())




