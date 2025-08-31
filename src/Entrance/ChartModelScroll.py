from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtCharts import *
import csv
import pandas as pd
import random
from random import uniform
import math
import sys
#from ScrollTest import *
from ScrolledChart import length_of_chart


# отсечка
class VerticalLineModel(QAbstractTableModel):
    def __init__(self, startX=20, minY=-100, maxY=100, parent: QObject = None):   #minY=-200, maxY=200
        super().__init__(parent)
        self.__currentX = startX
        self.__minY = minY
        self.__maxY = maxY

    def rowCount(self, parent):
        return 2

    def columnCount(self, parent):
        return 2

    def data(self, index: QModelIndex, role: int):
        if not index.isValid():
            return None
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if index.column() == 0:
            return self.__currentX
        elif index.column() == 1 and index.row() == 0:
            return self.__minY
        elif index.column() == 1 and index.row() == 1:
            return self.__maxY
        else:
            return

    def moveLine(self, xDiff: float):
        if self.__currentX <= 0 and xDiff < 0:
            return
        if self.__currentX >= 100 and xDiff > 0:              # 100
            return
        self.__currentX += xDiff
        self.dataChanged.emit(self.index(0, 0), self.index(1, 1), [Qt.ItemDataRole.DisplayRole])
        print(self.__currentX)


class MoveLineController(QObject):
    def __init__(self, line: VerticalLineModel, parent: QObject = None):
        super().__init__(parent)
        self.__line = line

    def eventFilter(self, watched: QObject, event: QEvent):
        if event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_D:
                self.__line.moveLine(1)
            if event.key() == Qt.Key.Key_A:
                self.__line.moveLine(-1)
        return False


class ScrollChartClass(QWidget):
    def __init__(self, chart):
        super().__init__()
        self.chart = chart
        self.initUI()

    def initUI(self):
        self.scroll = QScrollArea()
        self.hbox = QHBoxLayout()
        self.scroll.setWidget(self.chart)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.hbox.addWidget(self.scroll)
        self.setLayout(self.hbox)
        return


if __name__ == "__main__":
    app = QApplication([])

    model = VerticalLineModel()

    dataTableView = QTableView()
    dataTableView.setModel(model)

    seriesData1 = QLineSeries()
    seriesData2 = QLineSeries()
    for x in range(200):
        seriesData1.append(QPointF(x, math.sin(x)))
        seriesData2.append(QPointF(x, math.cos(x)))

    verticalLine1 = QLineSeries()
    verticalLine2 = QLineSeries()
    lineMapper1 = QVXYModelMapper()
    lineMapper2 = QVXYModelMapper()

    lineMapper1.setXColumn(0)
    lineMapper2.setXColumn(0)
    lineMapper1.setYColumn(1)
    lineMapper2.setYColumn(1)
    lineMapper1.setSeries(verticalLine1)
    lineMapper2.setSeries(verticalLine2)
    lineMapper1.setModel(model)
    lineMapper2.setModel(model)

    chartModel1 = QChart()
    chartModel2 = QChart()
    chartModel1.addSeries(seriesData1)
    chartModel2.addSeries(seriesData2)
    chartModel1.createDefaultAxes()
    chartModel2.createDefaultAxes()

    chartModel1.addSeries(verticalLine1)
    chartModel2.addSeries(verticalLine2)
    for axis in chartModel1.axes():
        verticalLine1.attachAxis(axis)
    for axis in chartModel2.axes():
        verticalLine2.attachAxis(axis)

    window = QWidget()
    windowLayout = QGridLayout()
    window.setLayout(windowLayout)
    windowLayout.addWidget(dataTableView, 0, 0)

    scroll_chart_class1 = ScrollChartClass(QChartView(chartModel1))
    scroll_chart_class2 = ScrollChartClass(QChartView(chartModel2))
    windowLayout.addWidget(scroll_chart_class1, 0, 1)
    windowLayout.addWidget(scroll_chart_class2, 1, 1)

    #windowLayout.addWidget(QChartView(chartModel1), 0, 1)
    #windowLayout.addWidget(QChartView(chartModel2), 1, 1)
    windowLayout.setColumnStretch(0, 1)
    windowLayout.setColumnStretch(1, 4)

    lineMover = MoveLineController(model)
    window.installEventFilter(lineMover)

    window.show()
    sys.exit(app.exec())