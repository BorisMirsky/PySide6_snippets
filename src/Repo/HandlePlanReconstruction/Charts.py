
from PySide6.QtWidgets import QWidget, QListWidget, QListWidgetItem, QVBoxLayout, QApplication
from PySide6.QtCharts import QLineSeries, QVXYModelMapper, QChart, QChartView, QValueAxis
from PySide6.QtGui import QFont, QIcon, QShortcut, Qt, QPen, QPainter, QImage, QPixmap, QColor, QKeySequence
from PySide6.QtCore import Qt, QTimer, QObject, QDateTime, QCoreApplication, Signal, QTimer
import sys
import numpy as np
from NumpyTableModel import NumpyTableModel
from VerticalLine import VerticalLineModel1, VerticalLineModel2
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
        self.x_start = 0
        self.x_stop = DATA_LEN #
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
                 chart_column_name3: str,
                 v_model1: VerticalLineModel1):
        super().__init__()
        #print('type(v_model1 ', type(v_model1))
        self.vertical_model1 = v_model1
        self.chart_column_name = chart_column_name3
        self.chart = QChart()
        self.chart.legend().setVisible(False)
        self.data1 = get_csv_column(FILENAME, self.chart_column_name)
        self.series1 = QLineSeries()
        for i in range (0, DATA_LEN, 1):
            self.series1.append(i, self.data1[i])
        self.x_start = 0
        self.x_stop = DATA_LEN
        self.setFocusPolicy(Qt.NoFocus)
        self.series1.setPen(QPen(Qt.GlobalColor.green, 2))
        self.chart.addSeries(self.series1)
        self.first_point_horizontal_line = None
        self.second_point_horizontal_line = None
        self.y_axis = QValueAxis()
        self.y_axis.setRange(min(self.data1) - 5, max(self.data1) + 5)
        self.y_axis.setLabelFormat("%0.2f")
        self.y_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        self.y_axis.setTickInterval(10)
        self.y_axis.setTitleText("Сдвиги, мм")
        axisBrush = QBrush(Qt.GlobalColor.black)
        self.y_axis.setTitleBrush(axisBrush)
        self.x_axis = QValueAxis()
        self.x_axis.setRange(self.x_start, self.x_stop)
        self.x_axis.setLabelFormat("%d")
        self.x_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        self.x_axis.setTickInterval(100)
        self.chart.addAxis(self.x_axis, Qt.AlignmentFlag.AlignBottom)
        self.chart.addAxis(self.y_axis, Qt.AlignmentFlag.AlignLeft)
        self.series1.attachAxis(self.x_axis)
        self.series1.attachAxis(self.y_axis)
        labelsFont = QFont()
        labelsFont.setPixelSize(12)
        self.x_axis.setLabelsFont(labelsFont)
        self.y_axis.setLabelsFont(labelsFont)
        self.x_axis.setLabelsBrush(axisBrush)
        self. y_axis.setLabelsBrush(axisBrush)

        self.vertical_line_series1 = QLineSeries()
        self.vertical_line_series1.setPen(QPen(Qt.GlobalColor.cyan, 4))   # первая основная динамическая
        self.vertical_line_series2 = QLineSeries()
        self.vertical_line_series2.setPen(QPen(Qt.GlobalColor.magenta, 2))  # первая статичная
        self.vertical_line_series3 = QLineSeries()
        self.vertical_line_series3.setPen(QPen(Qt.GlobalColor.magenta, 2))  # вторая статичная
        self.horizontal_line_series = QLineSeries()
        self.horizontal_line_series.setPen(QPen(Qt.GlobalColor.magenta, 2))  # горизонтальная
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
        self.lineMapper3 = QVXYModelMapper(self)
        self.lineMapper3.setXColumn(0)
        self.lineMapper3.setYColumn(1)
        self.lineMapper3.setSeries(self.vertical_line_series3)
        #
        self.lineMapper4 = QVXYModelMapper(self)
        self.lineMapper4.setXColumn(1)
        self.lineMapper4.setYColumn(0)
        self.lineMapper4.setSeries(self.horizontal_line_series)
        #
        self.chart.addSeries(self.vertical_line_series1)
        self.chart.addSeries(self.vertical_line_series2)
        self.chart.addSeries(self.vertical_line_series3)
        self.chart.addSeries(self.horizontal_line_series)
        self.vertical_line_series1.attachAxis(self.x_axis)
        self.vertical_line_series1.attachAxis(self.y_axis)
        self.vertical_line_series2.attachAxis(self.x_axis)
        self.vertical_line_series2.attachAxis(self.y_axis)
        self.vertical_line_series3.attachAxis(self.x_axis)
        self.vertical_line_series3.attachAxis(self.y_axis)
        self.horizontal_line_series.attachAxis(self.x_axis)
        self.horizontal_line_series.attachAxis(self.y_axis)
        #
        self.shift_to_lower = 0
        self.y_range_max = 0
        self.rugby_gate = False
        self.installEventFilter(self)
        self.chart_view = QChartView(self.chart)
        vbox = QVBoxLayout()
        vbox.addWidget(self.chart_view)
        self.setLayout(vbox)


    def eventFilter(self, watched: QObject, event: QEvent):
        if event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_D:
                self.vertical_model1.shiftLine(1)
                return True
            elif event.key() == Qt.Key.Key_A:
                self.vertical_model1.shiftLine(-1)
                return True
            elif event.key() == Qt.Key_Return:
                #self.shift_to_lower = self.vertical_model1.currentX()                  # !
                self.run_reconstruction(self.vertical_model1.currentX())
                return True
            # Двигаем горизонтальную черту
            elif event.key() == Qt.Key.Key_S:                      # ПЕРЕДЕЛАТЬ В СТРЕЛКУ
                self.horizontal_model.shiftLine(-1)
                return True
            # ЗАКРЫТИЕ ЦИКЛА
            elif event.key() == Qt.Key.Key_Escape:
                self.stop_reconstruction()
                return True
            # ОТМЕНА ПОСЛЕДНЕГО ДЕЙСТВИЯ
            elif event.key() == QKeySequence(Qt.Key.Key_Backspace):  #, Qt.Key.Key_Control):   # Key_Back
                return True
        return False


    # запускается по enter
    def run_reconstruction(self, current_x_point):
        self.vertical_line_series1.hide()
        if self.rugby_gate == False:                        # первое использование
            print(1, current_x_point)
            #self.lineMapper2.setSeries(self.vertical_line_series2)
            self.vertical_model2 = VerticalLineModel2(self.vertical_model1.currentX() - 100)
            self.lineMapper2.setModel(self.vertical_model2)
            #self.lineMapper3.setSeries(self.vertical_line_series3)
            self.vertical_model3 = VerticalLineModel2(self.vertical_model1.currentX() + 100)
            self.lineMapper3.setModel(self.vertical_model3)
            #self.current_x_point = self.vertical_model1.currentX()
            #self.lineMapper4.setSeries(self.horizontal_line_series)
            self.y_range = get_csv_column_range(FILENAME, self.chart_column_name,
                                                round(current_x_point - 100), round(current_x_point + 100))
            self.horizontal_model = HorizontalLineModel(max(self.y_range), current_x_point - 100,
                                                        current_x_point + 100)
            self.lineMapper4.setModel(self.horizontal_model)
            self.rugby_gate = True
        else:
            print(2, current_x_point)
            self.vertical_line_series2.show()
            self.vertical_line_series3.show()
            self.horizontal_line_series.show()


    # запускается по esc
    def stop_reconstruction(self):
        self.vertical_line_series1.show()
        self.vertical_line_series2.hide()
        self.vertical_line_series3.hide()
        self.horizontal_line_series.hide()




class ChartsWidget(QWidget):
    def __init__(self,
                 chart_column_name1: str, chart_column_name2: str, chart_column_name3: str,
                 model: VerticalLineModel1):
        super().__init__()
        self.model = model
        self.setContentsMargins(0,0,0,0)
        chart1 = Chart1(chart_column_name1, chart_column_name2)
        chart2 = Chart2(chart_column_name3, self.model)
        vbox = QVBoxLayout()
        vbox.addWidget(chart1,2)
        vbox.addWidget(chart2,1)
        self.setLayout(vbox)



model1 = VerticalLineModel1

if __name__ == '__main__':
    app = QApplication(sys.argv)
     #c1 = Chart1('plan_prj', 'plan_fact')
    c2 = Chart2('plan_delta', model1(round(DATA_LEN/2)))
    c2.show()
    sys.exit(app.exec())




