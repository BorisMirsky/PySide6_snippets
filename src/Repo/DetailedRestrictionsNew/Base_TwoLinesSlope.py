
from PySide6.QtWidgets import QWidget, QListWidget, QListWidgetItem, QVBoxLayout, QApplication, QHBoxLayout, QSpinBox
from PySide6.QtCharts import QLineSeries, QVXYModelMapper, QChart, QChartView, QValueAxis, QAreaSeries
from PySide6.QtGui import QFont, QIcon, QShortcut, Qt, QPen, QPainter, QImage, QPixmap, QColor, QKeySequence, QBrush
from PySide6.QtCore import Qt, QTimer, QObject, QDateTime, QCoreApplication, Signal, QTimer, QEvent
import sys
import numpy as np
from VerticalLine import VerticalLineModel1

"""
1. Поднимать планку с двух источников
2. фокус потерялся
3. собирать все точки в один список
4. разбивать этот список на сегменты
5. esc'ом ходить по сегментам
6. -------------//--------------- выделять сегмент как ScatterSeries
7. Удалять выбранный сегмент



"""

class ChartWindow(QWidget):
    def __init__(self,   v_model1: VerticalLineModel1):
        super().__init__()
        self.counter = 0
        self.start_point_y = 30
        self.start_point = 30
        self.green_line_point = 0                             # static
        self.vertical_model2_flag=False
        self.resize(700, 500)
        self.vertical_model1 = v_model1
        self.vertical_model2 = VerticalLineModel1
        #self.chart_column_name = chart_column_name3
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
        for i in range (0, 700, 1):
            self.straight_line_series.append(i, 30)
        
        self.straight_line_series.setPen(QPen(Qt.GlobalColor.red, 1))
        self.chart.addSeries(self.straight_line_series)
        self.straight_line_series.attachAxis(self.x_axis)
        self.straight_line_series.attachAxis(self.y_axis)
       #
        self.vertical_line_series1 = QLineSeries()
        self.vertical_line_series1.setPen(QPen(Qt.GlobalColor.magenta, 2))   # первая динамическая
        self.vertical_line_series2 = QLineSeries()
        self.vertical_line_series2.setPen(QPen(Qt.GlobalColor.green, 2))  # вторая статичная
        #self.segment_to_edit_series = QLineSeries()
        #self.segment_to_edit_series.setPen(QPen(Qt.GlobalColor.red, 5))
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
        self.chart.addSeries(self.vertical_line_series1)
        self.chart.addSeries(self.vertical_line_series2)
        self.vertical_line_series1.attachAxis(self.x_axis)
        self.vertical_line_series1.attachAxis(self.y_axis)
        self.vertical_line_series2.attachAxis(self.x_axis)
        self.vertical_line_series2.attachAxis(self.y_axis)
        #
        self.edit_decision_list = set()
        self.edit_decision_list_counter = -1

        right_column = self.right_column()
        self.installEventFilter(self)
        chart_view = QChartView(self.chart)
        hbox = QHBoxLayout()
        hbox.addWidget(chart_view, 5)
        hbox.addLayout(right_column, 1)
        self.setLayout(hbox)
        self.setFocus()

    def right_column(self):
        sb1 = QSpinBox()
        sb1.setRange(-100,100)
        sb1.setValue(0)
        sb1.valueChanged.connect(self.__handleSpinBox1)
        #
        sb2 = QSpinBox()
        sb2.setRange(-100, 100)
        sb2.setValue(0)
        #sb2.valueChanged.connect(self.__handleSpinBox2)
        #
        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addWidget(sb1)
        vbox.addWidget(sb2)
        vbox.addStretch(1)
        return vbox

    # примет координаты двух точек, вернёт k & b (проще говоря - построит прямую под углом)
    # добавить возможность построения вертикали и горизонтали
    def line_equation(self, x1, y1, x2, y2):
        slope = (y2 - y1) / (x2 - x1)
        intercept = y1 - slope * x1
        result = [slope, intercept]
        return result

    def __handleSpinBox1(self, value):
        left_edge_x, right_edge_x = min(self.start_point, self.counter), max(self.start_point, self.counter)
        for x in range(left_edge_x, right_edge_x, 1):
            result = self.line_equation(left_edge_x, 30, right_edge_x, 30 + value)
            self.right_edge_y = (result[0] * x) + result[1]
            self.straight_line_series.replace(x, x, self.right_edge_y)


    # def __handleSpinBox2(self, value):
    #     left_edge_x, right_edge_x = min(self.start_point, self.counter), max(self.start_point, self.counter)
    #     for x in range(left_edge_x, right_edge_x, 1):
    #         result = self.line_equation(left_edge_x, 30, right_edge_x, 30 + value)
    #         self.straight_line_series.replace(x, x, (result[0] * x) + result[1])




    # def cancel_last_action(self):
    #     sorted_list = sorted(self.edit_decision_list, key=lambda x: (x[0], x[1]))
    #     last_element = sorted_list[self.edit_decision_list_counter % len(sorted_list)]   # circular list
    #     #self.vertical_model1.newPosition(last_element[0])
    #     #self.vertical_model2.newPosition(last_element[1])
    #     self.edit_decision_list_counter -= 1


    def eventFilter(self, watched: QObject, event: QEvent):
        if event.type() == QEvent.Type.KeyPress:
            #print("eventFilter")
            self.setFocus()
            # Двигаем вертикальную черту
            if event.key() == Qt.Key.Key_Right:
                self.vertical_model1.shiftLine(1)
                self.counter+=1
                #print(self.straight_line_series.points()[self.counter].toTuple()[0])
                return True
            elif event.key() == Qt.Key.Key_Left:
                self.vertical_model1.shiftLine(-1)
                self.counter-=1
                return True
            elif event.key() == Qt.Key.Key_D:
                #self.vertical_model2 = VerticalLineModel1
                self.lineMapper2.setModel(self.vertical_model2(self.counter))
                self.start_point = self.counter
                self.vertical_model2_flag=True
                return True
            # elif event.key() == Qt.Key.Key_Backspace:
            #     self.cancel_last_action()
            #     return True
        return False



model1 = VerticalLineModel1

if __name__ == '__main__':
    app = QApplication(sys.argv)
    cw = ChartWindow(model1(0))
    cw.show()
    sys.exit(app.exec())




