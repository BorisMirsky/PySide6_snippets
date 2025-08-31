from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtCharts import *
from PySide6.QtGui import *
from NumpyTableModel import NumpyTableModel
from VerticalLine2 import MoveLineController, VerticalLineModel
import sys
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import math



def read_csv_file(filename):
    df = pd.read_csv(filename)
    return df

def get_csv_column(filename, column_name):
    df = read_csv_file(filename)
    column = df.loc[:, column_name]
    return column.tolist()


class Chart(QWidget):
    def __init__(self, y_value1: float, y_value2: float, y_value3: float,
                 datafile: str, timer: QTimer(qApp), n: int, model: any,
                 parent: QWidget = None):
        super().__init__(parent)
        self.datafile = datafile
        self.data = read_csv_file(self.datafile)
        self.start_x = 10
        self.positionValue = 0
        self.y_value1 = y_value1
        self.y_value2 = y_value2
        self.y_value3 = y_value3
        self.insertionTimer = timer
        self.vertical_model = model
        self.counter = 0
        self.result_label1 = QLabel()
        self.result_label1.setStyleSheet("border: 10px solid green; font: bold 14px;")
        self.result_label1.setContentsMargins(20, 20, 20, 20)
        self.result_label1.setMinimumWidth(200)
        self.result_label1.setMinimumHeight(100)
        self.result_label2 = QLabel()
        self.result_label2.setStyleSheet("border: 10px solid blue; font: bold 14px;")
        self.result_label2.setContentsMargins(20, 20, 20, 20)
        self.result_label2.setMinimumWidth(200)
        self.result_label2.setMinimumHeight(100)
        self.result_label3 = QLabel()
        self.result_label3.setStyleSheet("border: 10px solid red; font: bold 14px;")
        self.result_label3.setContentsMargins(20, 20, 20, 20)
        self.result_label3.setMinimumWidth(200)
        self.result_label3.setMinimumHeight(100)
        self.formatted_label_text = ""
        #
        self.minPosition = 0
        self.lineMover = MoveLineController(self.vertical_model, 'strela_data.csv', self.minPosition)
        self.installEventFilter(self.lineMover)
        #
        self.model1 = NumpyTableModel(np.ones((0, 2)), qApp)
        self.model2 = NumpyTableModel(np.ones((0, 2)), qApp)
        self.model3 = NumpyTableModel(np.ones((0, 2)), qApp)
        #
        self.series1 = QScatterSeries(self.model1)
        self.series1.setMarkerShape(QScatterSeries.MarkerShapeRectangle)    # квадрат
        self.series1.setMarkerSize(20.0)
        self.mapper1 = QVXYModelMapper(self.model1)
        self.mapper1.setXColumn(0)
        self.mapper1.setYColumn(1)
        self.mapper1.setModel(self.model1)
        self.mapper1.setRowCount(200)
        self.mapper1.setSeries(self.series1)
        self.series1.setColor('green')
        #
        self.series2 = QScatterSeries(self.model2)
        self.mapper2 = QVXYModelMapper(self.model2)
        self.mapper2.setXColumn(0)
        self.mapper2.setYColumn(1)
        self.mapper2.setModel(self.model2)
        self.mapper2.setRowCount(200)
        self.mapper2.setSeries(self.series2)
        self.series2.setColor('blue')
        #
        self.series3 = QScatterSeries(self.model3)
        self.series3.setMarkerShape(QScatterSeries.MarkerShapeRectangle)
        self.series3.setMarkerSize(15.0)
        self.mapper3 = QVXYModelMapper(self.model3)
        self.mapper3.setXColumn(0)
        self.mapper3.setYColumn(1)
        self.mapper3.setModel(self.model3)
        self.mapper3.setRowCount(200)
        self.mapper3.setSeries(self.series3)
        self.series3.setColor('red')
        #
        self.mapper4 = QVXYModelMapper(self.model1)            # спец. маппер для отображенияdd
        self.mapper4.setXColumn(0)
        self.mapper4.setYColumn(1)
        self.mapper4.setRowCount(80)
        #
        verticalLine = QLineSeries()
        verticalLine.setPen(QPen(Qt.GlobalColor.cyan, 10))
        self.lineMapper = QVXYModelMapper(self)
        self.lineMapper.setXColumn(0)
        self.lineMapper.setYColumn(1)
        self.lineMapper.setSeries(verticalLine)
        self.lineMapper.setModel(self.vertical_model)
        #
        self.chart = QChart()
        self.chart.legend().setVisible(False)
        self.chart.addSeries(self.series1)
        self.chart.addSeries(self.series2)
        self.chart.addSeries(self.series3)
        self.chart.addSeries(verticalLine)
        self.chart.createDefaultAxes()
        self.chart.axisY().setRange(-1.0, 3.0)
        self.chart.axes(Qt.Orientation.Horizontal)[0].setGridLineVisible(False)             # прячем сетку графикa
        self.chart.axes(Qt.Orientation.Vertical)[0].setGridLineVisible(False)
        self.vlayout = QVBoxLayout()
        self.insertionTimer.start(n)
        self.insertionTimer.timeout.connect(self.create_new_point)
        self.view = QChartView(self.chart)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.vlayout.addWidget(self.view)
        self.setLayout(self.vlayout)

    def create_new_point(self):
        maxPosition = max(50, self.counter + 5)
        self.minPosition = max(0, maxPosition - 50)
        self.chart.axisX().setRange(self.minPosition, maxPosition)
        self.mapper4.setFirstRow(self.minPosition)                         # mapper4 для отображения позиции
        ################# если не NaN -> заносим точку в модель и на график #################################
        current_x1 = get_csv_column(self.datafile, 'Rfid')[self.counter]
        if math.isnan(current_x1):
            pass
        else:
            self.model1.appendRow([self.counter, self.y_value1])
        #
        current_x2 = get_csv_column(self.datafile, 'Label_picket')[self.counter]
        if math.isnan(current_x2):
            pass
        else:
            self.model2.appendRow([self.counter, self.y_value2])
        #
        current_x3 = get_csv_column(self.datafile, 'Isso')[self.counter]
        try:
            if math.isnan(current_x3):
                pass
        except TypeError:
            self.model3.appendRow([self.counter, self.y_value3])

        ###########################   Отсечка стоит на месте, метки движутся   #########################################
        if math.isnan(current_x1):
            pass
        elif self.counter >= (self.vertical_model.currentX() - 1) and self.counter <= (self.vertical_model.currentX() + 1):
            self.result_label1.setText("   ")
            self.formatted_label_text1 = "Значение метки {0}\nКоордината {1}".format(self.counter, current_x1)
            self.result_label1.setText(self.formatted_label_text1)
        if math.isnan(current_x2):
            pass
        elif self.counter >= (self.vertical_model.currentX() - 1) and self.counter <= (self.vertical_model.currentX() + 1):
            self.result_label1.setText("   ")
            self.formatted_label_text1 = "Значение метки {0}\nКоордината {1}".format(self.counter, current_x2)
            self.result_label1.setText(self.formatted_label_text1)
        try:
            if math.isnan(current_x3):
                pass
        except TypeError:
            if self.counter >= (self.vertical_model.currentX() - 1) and self.counter <= (self.vertical_model.currentX() + 1):
                self.result_label1.setText("   ")
                self.formatted_label_text1 = "Значение метки {0}\nКоордината {1}".format(self.counter, current_x3)
                self.result_label1.setText(self.formatted_label_text1)

        # Отсечка двигается -> координаты приходят из LineMover
        if self.lineMover.coord_value1:
            self.result_label1.setText("   ")
            self.formatted_label_text1 = "Значение метки {0}\nКоордината {1}".format(self.lineMover.coord_value1, self.lineMover.coord_index1)
            self.result_label1.setText(self.formatted_label_text1)
        if self.lineMover.coord_value2:
            self.result_label2.setText("   ")
            self.formatted_label_text2 = "Значение метки {0}\nКоордината {1}".format(self.lineMover.coord_value2, self.lineMover.coord_index2)
            self.result_label2.setText(self.formatted_label_text2)
        if self.lineMover.coord_value3:
            self.result_label3.setText("   ")
            self.formatted_label_text3 = "Значение метки {0}\nКоордината {1}".format(self.lineMover.coord_value3, self.lineMover.coord_index3)
            self.result_label3.setText(self.formatted_label_text3)

        self.positionValue += 1
        self.counter += 1

    positionValue = 0


vertical_model = VerticalLineModel()
class Main(QWidget):
    def __init__(self,  timer: QTimer(qApp), n: int):
        super().__init__()
        self.timer = timer
        chart = Chart(0.0, 1.0, 2.0, 'strela_data.csv', insertionTimer, n, vertical_model)
        vbox = QVBoxLayout()
        hbox1 = QHBoxLayout()
        labels_name1 = QLabel("RFID метки")
        labels_name1.setStyleSheet("font: bold 16px;")
        labels_name2 = QLabel("Пикеты")
        labels_name2.setStyleSheet("font: bold 16px;")
        labels_name3 = QLabel("Искусственные объекты")
        labels_name3.setStyleSheet("font: bold 16px;")
        hbox1.addWidget(labels_name1)
        hbox1.addWidget(labels_name2)
        hbox1.addWidget(labels_name3)
        hbox2 = QHBoxLayout()
        vbox.addWidget(chart)
        hbox2.addWidget(chart.result_label1)
        hbox2.addWidget(chart.result_label2)
        hbox2.addWidget(chart.result_label3)
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        self.setLayout(vbox)



if __name__ == '__main__':
    insertionTimer = QTimer(qApp)
    app = QApplication(sys.argv)
    window = Main(insertionTimer, 100)
    window.show()
    sys.exit(app.exec())