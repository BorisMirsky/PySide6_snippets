
from PySide6.QtWidgets import QWidget, QListWidget, QListWidgetItem, QVBoxLayout, QApplication, QHBoxLayout, QSpinBox
from PySide6.QtCharts import QLineSeries, QVXYModelMapper, QChart, QChartView, QValueAxis, QAreaSeries
from PySide6.QtGui import QFont, QIcon, QShortcut, Qt, QPen, QPainter, QImage, QPixmap, QColor, QKeySequence, QBrush
from PySide6.QtCore import Qt, QTimer, QObject, QDateTime, QCoreApplication, Signal, QTimer, QEvent
import sys
import numpy as np
from VerticalLine import VerticalLineModel1, VerticalLineModel2


class ChartWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.counter = 0
        self.start_point = 0
        self.resize(700, 500)
        self.chart = QChart()
        self.chart.legend().setVisible(False)
        self.x_start = 0
        self.x_stop = 700
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
        self.draw_line()
        #for i in range (0, 500, 1):
        #    self.straight_line_series.append(i, 0.1*i)
        self.straight_line_series.setPen(QPen(Qt.GlobalColor.red, 2))
        self.chart.addSeries(self.straight_line_series)
        self.straight_line_series.attachAxis(self.x_axis)
        self.straight_line_series.attachAxis(self.y_axis)

        right_column = self.right_column()
        self.installEventFilter(self)
        chart_view = QChartView(self.chart)
        hbox = QHBoxLayout()
        hbox.addWidget(chart_view, 5)
        hbox.addWidget(right_column, 1)
        self.setLayout(hbox)
        self.setFocus()

    def draw_line(self):
        for i in range(0, 700, 1):
            if i < 100:
                self.straight_line_series.append(i, 30)
            elif 100 <= i <= 200:
                result = self.line_equation(100, 30, 200, 10)
                self.straight_line_series.append(i, (result[0] * i) + result[1])
            elif 200 <= i <= 300:
                #result = self.line_equation(200, 10, 200, 10)
                #self.straight_line_series.append(i, (result[0] * i) + result[1])
                self.straight_line_series.append(i, 10)
            elif 300 <= i <= 500:
                result = self.line_equation(300, 10, 500, 30)
                self.straight_line_series.append(i, (result[0] * i) + result[1])
            else:  #if 500 < i:
                self.straight_line_series.append(i, 30)
            
    def line_equation(self, x1, y1, x2, y2):
        #if x1 == x2:
        #    return (-x1, x1 ** 2)  #f"x = {x1}" # Вертикальная линия
        #elif y1 == y2:
        #    return (0, y1)   #f"y = {y1}" # Горизонтальная линия
        #else:
        slope = (y2 - y1) / (x2 - x1)
        intercept = y1 - slope * x1
        return (slope, intercept) 
        

                
    def right_column(self):
        sb = QSpinBox()
        sb.setRange(-100,100)
        sb.setValue(0)
        sb.valueChanged.connect(self.__handleSpinBox)
        return sb

    def __handleSpinBox(self, value):
        pass



if __name__ == '__main__':
    app = QApplication(sys.argv)
    cw = ChartWindow()
    cw.show()
    sys.exit(app.exec())




