
from PySide6.QtWidgets import QWidget, QListWidget, QListWidgetItem, QVBoxLayout, QApplication
from PySide6.QtCharts import QLineSeries, QVXYModelMapper, QChart, QChartView, QValueAxis
from PySide6.QtGui import QFont, QIcon, QShortcut, Qt, QPen, QPainter, QImage, QPixmap, QColor
from PySide6.QtCore import Qt, QTimer, QObject, QDateTime, QCoreApplication, Signal, QTimer
import sys
import numpy as np
from NumpyTableModel import NumpyTableModel
from VerticalLine import VerticalLineModel1, VerticalLineModel2, MoveLineController
from GorizontalLine import GorizontalLineModel
from ServiceInfo import *


v_model = VerticalLineModel1(1000)
g_model = GorizontalLineModel(800, 1700, 40)

class Chart(QWidget):
    def __init__(self, chart_column_name: str,
                 v_model: VerticalLineModel1,
                 g_model: GorizontalLineModel):
        super().__init__()
        self.vertical_model = v_model
        self.gorizontal_model = g_model
        self.chart_column_name = chart_column_name
        self.chart = QChart()
        self.chart.legend().setVisible(False)
        self.data = get_csv_column(FILENAME, chart_column_name)
        self.series = QLineSeries()
        for i in range (0, DATA_LEN, 1):
            self.series.append(i, self.data[i])

        self.series.setPen(QPen(Qt.GlobalColor.green, 2))
        self.chart.addSeries(self.series)

        y_axis = QValueAxis()
        y_axis.setRange(min(self.data), max(self.data))
        y_axis.setLabelFormat("%0.2f")
        y_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        y_axis.setTickInterval(10)
        y_axis.setTitleText("Сдвиги, мм")
        axisBrush = QBrush(Qt.GlobalColor.black)
        y_axis.setTitleBrush(axisBrush)
        #
        self.x_start = 0
        self.x_stop = DATA_LEN
        x_axis = QValueAxis()
        x_axis.setRange(self.x_start, self.x_stop)
        x_axis.setLabelFormat("%d")
        x_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        x_axis.setTickInterval(100)
        self.chart.addAxis(x_axis, Qt.AlignmentFlag.AlignBottom)
        self.chart.addAxis(y_axis, Qt.AlignmentFlag.AlignLeft)
        self.series.attachAxis(x_axis)
        self.series.attachAxis(y_axis)
        #
#        self.lineMover1 = MoveLineController(20, self.vertical_model1)  # , self.vertical_model2)
#        self.installEventFilter(self.lineMover1)
#        self.installEventFilter(True)
        #
        labelsFont = QFont()
        labelsFont.setPixelSize(12)
        x_axis.setLabelsFont(labelsFont)
        y_axis.setLabelsFont(labelsFont)
        x_axis.setLabelsBrush(axisBrush)
        y_axis.setLabelsBrush(axisBrush)
        #
        self.vertical_line_series = QLineSeries()
        self.vertical_line_series.setPen(QPen(Qt.GlobalColor.magenta, 2))
        self.gorizontal_line_series = QLineSeries()
        self.gorizontal_line_series.setPen(QPen(Qt.GlobalColor.magenta, 2))
        #
        self.lineMapper1 = QVXYModelMapper(self)
        self.lineMapper1.setXColumn(0)
        self.lineMapper1.setYColumn(1)
        self.lineMapper1.setSeries(self.vertical_line_series)
        self.lineMapper1.setModel(self.vertical_model)
        #
        self.lineMapper2 = QVXYModelMapper(self)
        self.lineMapper2.setXColumn(0)
        self.lineMapper2.setYColumn(1)
        self.lineMapper2.setSeries(self.gorizontal_line_series)
        self.lineMapper2.setModel(self.gorizontal_model)
        #
        self.chart.addSeries(self.vertical_line_series)
        self.chart.addSeries(self.gorizontal_line_series)
        self.vertical_line_series.attachAxis(x_axis)
        self.vertical_line_series.attachAxis(y_axis)
        self.gorizontal_line_series.attachAxis(x_axis)
        self.gorizontal_line_series.attachAxis(y_axis)
        #
        self.chart_view = QChartView(self.chart)
        vbox = QVBoxLayout()
        vbox.addWidget(self.chart_view)
        self.setLayout(vbox)

    def eventFilter(self, watched: QObject, event: QEvent):
        if event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_D:
                #self.__line1.shiftLine(1)
                self.vertical_model.shiftLine(10)
            elif event.key() == Qt.Key.Key_A:
                #self.__line1.shiftLine(-1)
                self.self.vertical_model.shiftLine(-10)
    #         elif event.key() == (Qt.Key.Key_D and Qt.Key.Key_Control):
    #             self.lineMapper2 = QVXYModelMapper(self)
    #             self.lineMapper2.setXColumn(0)
    #             self.lineMapper2.setYColumn(1)
    #             self.lineMapper2.setSeries(self.vertical_line_series2) #(330))
    #             self.lineMapper2.setModel(self.vertical_model2)
    #             print('self.__line1.currentX() ', self.vertical_model1.currentX())
    #     if event.type() == QEvent.Type.KeyRelease:
    #         if event.key() == (Qt.Key.Key_D and Qt.Key.Key_Control):
    #             self.lineMapper3 = QVXYModelMapper(self)
    #             self.lineMapper3.setXColumn(0)
    #             self.lineMapper3.setYColumn(1)
    #             self.lineMapper3.setSeries(self.gorizontal_line_series)
    #             self.lineMapper3.setModel(self.gorizontal_model)
    #             print("KeyRelease Key_D Key_Control")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    c = Chart('plan_delta', v_model, g_model)
    c.show()
    sys.exit(app.exec())
