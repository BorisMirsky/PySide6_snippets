
from PySide6.QtCore import Signal, QTimer, QPointF
from PySide6.QtWidgets import QWidget,  QVBoxLayout, QApplication
from PySide6.QtCharts import  QLineSeries, QVXYModelMapper, QChart, QChartView, QValueAxis
from PySide6.QtGui import QPen, Qt, QPainter
import sys
import math
import numpy as np
#import pandas as pd
import warnings
from random import randint
warnings.filterwarnings("ignore", category=DeprecationWarning)
from NumpyTableModel import NumpyTableModel
from VerticalLine import VerticalLineModel

vertical_model = VerticalLineModel()

##################################################################################################################
class Chart(QWidget):
    def __init__(self, timer: QTimer(qApp), n: int, model: any, parent: QWidget = None):
        super().__init__(parent)
        self.insertionTimer = timer
        self.vertical_model = model
        self.counter = 0
        self.minPosition = 0
        self.data = [math.sin(i) for i in range(0, 1000, 1)]
        self.model1 = NumpyTableModel(np.ones((0, 2)), qApp)
        self.series1 = QLineSeries(self.model1)
        #
        self.y_start = -5
        self.y_stop = 5
        self.zoomFactor = (self.y_stop - self.y_start) * 0.1 # 0.5
        self.zoom_value = 0
        #
        self.mapper1 = QVXYModelMapper(self.model1)
        self.mapper1.setXColumn(1)
        self.mapper1.setYColumn(0)
        self.mapper1.setModel(self.model1)
        self.mapper1.setSeries(self.series1)

        self.mapper_for_mapping_only = QVXYModelMapper(self.model1)
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
        self.axisX = QValueAxis()
        self.axisY = QValueAxis()
        #
        self.chart = QChart()
        self.chart.legend().setVisible(False)
        self.chart.addSeries(self.series1)
        self.chart.addSeries(self.vertical_line_series)
        #
        self.chart.setAxisX(self.axisX)
        self.chart.setAxisY(self.axisY)
        self.chart.axisY().setRange(-5.0, 5.0)
        #
        self.series1.attachAxis(self.axisX)
        self.series1.attachAxis(self.axisY)
        self.vertical_line_series.attachAxis(self.axisX)
        self.vertical_line_series.attachAxis(self.axisY)
        self.chart.legend().setVisible(False)
        #
        #self.chart.axes(Qt.Orientation.Horizontal)[0].setGridLineVisible(False)
        #self.chart.axes(Qt.Orientation.Vertical)[0].setGridLineVisible(False)
        #
        self.vlayout = QVBoxLayout()
        self.insertionTimer.start(n)
        self.insertionTimer.timeout.connect(self.update_field)
        self.view = QChartView(self.chart)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.vlayout.addWidget(self.view)
        self.setLayout(self.vlayout)

    def update_field(self):
        maxPosition = max(100, self.counter + 5)
        self.minPosition = max(0, maxPosition - 100)
        self.vertical_line_position = self.minPosition + 10
        self.vertical_model.keep_line_position(self.vertical_line_position)
        self.chart.axisX().setRange(self.minPosition, maxPosition)
        self.data.append(math.sin(self.counter * 0.05))
        self.series1.append([QPointF(self.counter, self.data[self.counter])])
        self.counter += 1


    def keyPressEvent(self, keyEvent):
        key = keyEvent.key()
        if key == Qt.Key_W and self.zoom_value < 10:
            self.y_start = self.y_start + self.zoomFactor
            self.y_stop = self.y_stop - self.zoomFactor
            self.chart.axisY().setRange(self.y_start, self.y_stop)
            self.zoom_value = self.zoom_value + 1
            print('Key_W', self.y_start, self.y_stop, self.zoom_value)
        elif key == Qt.Key_S and self.zoom_value > -10:
            self.y_start = self.y_start - self.zoomFactor
            self.y_stop = self.y_stop + self.zoomFactor
            self.chart.axisY().setRange(self.y_start, self.y_stop)
            self.zoom_value = self.zoom_value - 1
            print('Key_S', self.y_start, self.y_stop, self.zoom_value)





if __name__ == '__main__':
    insertionTimer = QTimer(qApp)
    app = QApplication(sys.argv)
    window = Chart(insertionTimer, 50, vertical_model)
    window.show()
    sys.exit(app.exec())
