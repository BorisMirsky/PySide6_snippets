
from PySide6.QtCore import Signal, QTimer, QPointF
from PySide6.QtWidgets import QWidget, QListWidget, QListWidgetItem, QVBoxLayout, QApplication
from PySide6.QtCharts import QScatterSeries, QLineSeries, QVXYModelMapper, QChart, QChartView, QValueAxis
from PySide6.QtGui import QFont, QIcon, QShortcut, Qt, QPen, QPainter, QImage, QPixmap, QColor
import sys
import math
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from NumpyTableModel import NumpyTableModel
from VerticalLine import VerticalLineModel




def read_csv_file(filename):
    df = pd.read_csv(filename, sep=";")
    return df

def get_csv_column(filename, column_name):
    df = read_csv_file(filename)
    column = df.loc[:, column_name]
    return column #.tolist()



vertical_model = VerticalLineModel()

##################################################################################################################
class Chart(QWidget):
    def __init__(self, timer: QTimer(qApp), n: int, model: any, parent: QWidget = None):
        super().__init__(parent)
        self.insertionTimer = timer
        self.vertical_model = model
        self.counter = 0
        self.minPosition = 0
        self.data = get_csv_column('data.csv', 'plan_delta')
        self.model1 = NumpyTableModel(np.ones((0, 2)), qApp)
        self.series1 = QLineSeries(self.model1)
        #
        self.mapper1 = QVXYModelMapper(self.model1)
        self.mapper1.setXColumn(1)
        self.mapper1.setYColumn(0)
        self.mapper1.setModel(self.model1)
        self.mapper1.setSeries(self.series1)

        self.mapper_for_mapping_only = QVXYModelMapper(self.model1)     # Этот маппер только для отображения
        self.mapper_for_mapping_only.setXColumn(1)
        self.mapper_for_mapping_only.setYColumn(0)
        #
        self.vertical_line_series = QLineSeries()
        self.vertical_line_series.setPen(QPen(Qt.GlobalColor.magenta, 3))
        self.lineMapper = QVXYModelMapper(self)
        self.lineMapper.setXColumn(0)
        self.lineMapper.setYColumn(1)
        self.lineMapper.setSeries(self.vertical_line_series)
        self.lineMapper.setModel(self.vertical_model)
        self.vertical_line_position = 0
        #
        self.y_zero_series = QLineSeries()
        self.y_zero_series.append(QPointF(0, 0))
        self.y_zero_series.append(QPointF(2216, 0))
        self.y_zero_series.setPen(QPen(Qt.GlobalColor.green, 1, Qt.DashLine))  # DotLine
        #
        self.axisX = QValueAxis()
        self.axisY = QValueAxis()
        #
        self.chart = QChart()
        self.chart.legend().setVisible(False)
        self.chart.addSeries(self.series1)
        self.chart.addSeries(self.vertical_line_series)
        self.chart.addSeries(self.y_zero_series)
        #
        self.chart.setAxisX(self.axisX)
        self.chart.setAxisY(self.axisY)
        self.chart.axisY().setRange(-5.0, 5.0)
        #
        self.series1.attachAxis(self.axisX)
        self.series1.attachAxis(self.axisY)
        self.vertical_line_series.attachAxis(self.axisX)
        self.vertical_line_series.attachAxis(self.axisY)
        self.y_zero_series.attachAxis(self.axisX)
        self.y_zero_series.attachAxis(self.axisY)
        self.chart.legend().setVisible(False)
        #
        self.chart.axes(Qt.Orientation.Horizontal)[0].setGridLineVisible(False)             # прячем сетку графикa
        self.chart.axes(Qt.Orientation.Vertical)[0].setGridLineVisible(False)
        #
        self.vlayout = QVBoxLayout()
        self.insertionTimer.start(n)
        self.insertionTimer.timeout.connect(self.update_field)
        self.view = QChartView(self.chart)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.vlayout.addWidget(self.view)
        self.setLayout(self.vlayout)

    def update_field(self) ->None:
        maxPosition = max(500, self.counter + 5)
        self.minPosition = 0 #max(0, maxPosition - 500)
        self.vertical_line_position = self.minPosition + 10                        # где будет стоять отсечка
        self.vertical_model.keep_line_position(self.vertical_line_position)        # Удержание отсечки в поле видимости
        self.chart.axisX().setRange(self.minPosition, maxPosition)
        self.series1.append([QPointF(self.counter, self.data[self.counter])])
        my_list = [self.data[i] for i in range(self.minPosition, maxPosition, 1)]
        self.chart.axisY().setRange(min(0, min(my_list)), max(0, max(my_list)))
        self.counter += 1



if __name__ == '__main__':
    insertionTimer = QTimer(qApp)
    app = QApplication(sys.argv)
    window = Chart(insertionTimer, 10, vertical_model)
    window.show()
    sys.exit(app.exec())
