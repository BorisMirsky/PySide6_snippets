
from PySide6.QtWidgets import QWidget, QVBoxLayout, QApplication, QHBoxLayout, QSpinBox, QLineEdit, QPushButton
from PySide6.QtCharts import QLineSeries, QVXYModelMapper, QChart, QChartView, QValueAxis, QScatterSeries, QScatterSeries
from PySide6.QtGui import QFont, QShortcut, Qt, QPen, QPainter, QColor, QKeySequence, QBrush, QIntValidator
from PySide6.QtCore import Qt, QObject, QCoreApplication, Signal, QEvent
import sys
import numpy as np
from VerticalLine import VerticalLineModel1, VerticalLineModel2
from itertools import cycle


"""
1 Разбить на сегменты по наличию '30'
2 Ходить по этим сегментам
3 ------------//----------    наносить на них QScatterSeries
4 



"""

class ChartWindow(QWidget):
    def __init__(self,
                 v_model1: VerticalLineModel1):
        super().__init__()
        self.setFocus()
        self.counter = 0
        self.counter1 = 0
        self.data1 = []   #[11, 22, 33]
        self.pool = None #cycle(self.data1)
        self.start_point = 0
        self.start_point_y = 30
        self.vertical_model2_flag=False
        self.resize(700, 500)
        self.vertical_model1 = v_model1
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
        self.data = [[31, 30], [31, 40], [112, 40], [112, 30],
                     [143, 30], [143, 20], [226, 20], [226, 30],
                     [315, 30], [315, 35], [418, 35], [418, 30]]

        # прямая красная
        self.straight_line_series = QLineSeries()
        for i in range (0, 500, 1):
            self.straight_line_series.append(i, 30)
        self.straight_line_series.setPen(QPen(Qt.GlobalColor.red, 1))
        self.chart.addSeries(self.straight_line_series)
        #self.straight_line_series.attachAxis(self.x_axis)
        #self.straight_line_series.attachAxis(self.y_axis)
       #
        self.vertical_line_series1 = QLineSeries()
        self.vertical_line_series1.setPen(QPen(Qt.GlobalColor.magenta, 2))   # первая динамическая
        self.vertical_line_series2 = QLineSeries()
        self.vertical_line_series2.setPen(QPen(Qt.GlobalColor.green, 2))  # вторая статичная

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
        #self.chart.addSeries(self.straight_line_series)

        self.vertical_line_series1.attachAxis(self.x_axis)
        self.vertical_line_series1.attachAxis(self.y_axis)
        self.vertical_line_series2.attachAxis(self.x_axis)
        self.vertical_line_series2.attachAxis(self.y_axis)
        self.straight_line_series.attachAxis(self.x_axis)
        self.straight_line_series.attachAxis(self.y_axis)

        self.all_points = []
        right_column = self.right_column()
        self.installEventFilter(self)
        chart_view = QChartView(self.chart)
        hbox = QHBoxLayout()
        hbox.addWidget(chart_view, 5)
        hbox.addLayout(right_column, 1)
        self.setLayout(hbox)

    def right_column(self):
        vbox = QVBoxLayout()
        self.lineEdit = QLineEdit()
        #self.lineEdit.setPlaceholderText("Значение линии ограниечние на текущей позиции")
        self.lineEdit.setValidator(QIntValidator(-99, 99, self))
        self.lineEdit.returnPressed.connect(self.__handleLineEdit)  # каждое нажатие
        self.btn = QPushButton("go!")
        self.btn.clicked.connect(self.__handleBtn)
        vbox.addStretch(1)
        vbox.addWidget(self.lineEdit)
        vbox.addWidget(self.btn)
        vbox.addStretch(1)
        return vbox

    # делим длинный список на сегменты (т.е. отрезки с началом и концом = 30)
    def divide_data(self, y, data):                    
        counter = 0
        result = []
        for i in range (0, len(data), 1):
            if data[i][1] == y and counter == 0:
                segment = []
                segment.append(data[i])
                counter = 1
            elif data[i][1] != y and counter == 1:
                segment.append(data[i])
            elif data[i][1] == y and counter == 1:
                segment.append(data[i])
                result.append(segment)
                segment = []
                counter = 0
            i += 1
        #print(result)
        return result

    def __handleLineEdit(self):
        new_line = int(self.lineEdit.text())
        for i in range(min(self.start_point, self.counter), max(self.start_point, self.counter), 1):
            self.straight_line_series.replace(i, i, new_line)
        self.all_points.append([min(self.start_point, self.counter), 30])
        self.all_points.append([min(self.start_point, self.counter), new_line])
        self.all_points.append([max(self.start_point, self.counter), new_line])
        self.all_points.append([max(self.start_point, self.counter), 30])

    def __handleBtn(self):
        self.data1 = self.divide_data(30, self.all_points)
        self.pool = cycle(self.data1)


    def eventFilter(self, watched: QObject, event: QEvent):
        if event.type() == QEvent.Type.KeyPress:
            i = 0
            self.setFocus()
            # Двигаем вертикальную черту
            if event.key() == Qt.Key.Key_Right:
                self.vertical_model1.shiftLine(1)
                self.counter+=1
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
            elif event.key() == Qt.Key.Key_Q:
                print(next(self.pool))
                return True
        return False



model1 = VerticalLineModel1

if __name__ == '__main__':
    app = QApplication(sys.argv)
    cw = ChartWindow(model1(0))
    cw.show()
    sys.exit(app.exec())



data = [[31, 30], [31, 40], [112, 40], [112, 30],
        [143, 30], [143, 20], [226, 20], [226, 30],
        [315, 30], [315, 35], [418, 35], [418, 30]]


def divide_data(y, data):                    
    counter = 0
    result = []
    for i in range (0, len(data), 1):
        if data[i][1] == y and counter == 0:
            segment = []
            segment.append(data[i])
            counter = 1
        elif data[i][1] != y and counter == 1:
            segment.append(data[i])
        elif data[i][1] == y and counter == 1:
            segment.append(data[i])
            result.append(segment)
            segment = []
            counter = 0
        i += 1
    return result

#res = divide_data(30, data)
#print(res)
 

