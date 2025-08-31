# This Python file uses the following encoding: utf-8
import sys
import numpy as np
from PySide6.QtSerialPort import QSerialPort
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtCharts import *
from PySide6.QtGui import *
from NumpyTableModel import NumpyTableModel
from AbstractModels import AbstractReadModel
from MockModels import SinMockModel
from Table import TableClass





class ChartClass(QWidget):
    def __init__(self,
                 sensor1: AbstractReadModel[float],
                 sensor2: AbstractReadModel[float],
                 timer: QTimer(qApp)):
        super().__init__()
        self.positionValue = 0
        self.sensor1 = sensor1
        self.sensor2 = sensor2
        self.insertionTimer = timer
        self.model = NumpyTableModel(np.ones((0, 3)), qApp)
        self.line_1 = QLineSeries(self.model)
        self.line_2 = QLineSeries(self.model)
        self.mapper_1 = QVXYModelMapper(self.model)
        self.mapper_1.setXColumn(0)
        self.mapper_1.setYColumn(1)
        self.mapper_1.setSeries(self.line_1)
        self.mapper_1.setModel(self.model)
        self.mapper_2 = QVXYModelMapper(self.model)
        self.mapper_2.setXColumn(0)
        self.mapper_2.setYColumn(2)
        self.mapper_2.setSeries(self.line_2)
        self.mapper_2.setModel(self.model)
        self.mapper_1.setRowCount(80)
        self.mapper_2.setRowCount(80)
        self.chart = QChart()
        self.chart.legend().setVisible(False)
        self.chart.addSeries(self.line_1)
        self.chart.addSeries(self.line_2)
        self.chart.createDefaultAxes()
        self.chart.axisY().setRange(-10, 10)
        self.insertionTimer.start(100)
        self.insertionTimer.timeout.connect(self.createNewMeauserment)
        vlayout = QVBoxLayout()
        hlayout = QHBoxLayout()
        view = QChartView(self.chart)
        view.setRenderHint(QPainter.Antialiasing)
        vlayout.addWidget(view)
        vlayout.addLayout(hlayout)
        vlayout.setContentsMargins(0, 0, 0, 0)
        self.setContentsMargins(0,0,0,0)
        self.setLayout(vlayout)


    def createNewMeauserment(self):
        self.positionValue += 1
        chart_point1 = self.sensor1.read()
        chart_point2 = self.sensor2.read()
        self.model.appendRow([self.positionValue, chart_point1, chart_point2])
        maxPosition = max(30, self.positionValue + 3)
        minPosition = max(0, maxPosition - 30)
        self.chart.axisX().setRange(minPosition, maxPosition)
        self.mapper_1.setFirstRow(minPosition)
        self.mapper_2.setFirstRow(minPosition)

    positionValue = 0



class TabClass(QWidget):
    def __init__(self,
                 sensor1: AbstractReadModel[float],
                 sensor2: AbstractReadModel[float],
                 sensor3: AbstractReadModel[float],
                 sensor4: AbstractReadModel[float],
                 timer: QTimer(qApp),
                 parent: QWidget = None) -> None:
        super().__init__(parent)
        insertionTimer = timer
        chart1 = ChartClass(sensor1, sensor2, insertionTimer)
        chart2 = ChartClass(sensor3, sensor4, insertionTimer)
        self.layout = QVBoxLayout(self)
        tab_widget = QTabWidget()
        table = TableClass([None,sensor1, sensor2, sensor3, sensor4], insertionTimer)
        tab1 = QWidget()
        tab2 = QWidget()
        vbox1 = QVBoxLayout()
        vbox1.addWidget(table)
        vbox2 = QVBoxLayout()
        vbox2.addWidget(chart1)
        vbox2.addWidget(chart2)
        tab1.setLayout(vbox1)
        tab2.setLayout(vbox2)
        tab_widget.addTab(tab1, "Table")
        tab_widget.addTab(tab2, "Charts")
        self.layout.addWidget(tab_widget)
        self.setLayout(self.layout)


# if __name__ == "__main__":
#         app = QApplication([])
#         sensor1 = SinMockModel(amplitude=5, frequency=2, parent=app)
#         sensor2 = SinMockModel(amplitude=4, frequency=3, parent=app)
#         sensor3 = SinMockModel(amplitude=3, frequency=4, parent=app)
#         sensor4 = SinMockModel(amplitude=2, frequency=5, parent=app)
#         insertionTimer = QTimer(qApp)
#         #window = LineChartClass(sensor1, sensor2, insertionTimer)
#         window = TabClass(sensor1, sensor2, sensor3, sensor4, insertionTimer)
#         window.show()
#         sys.exit(app.exec())