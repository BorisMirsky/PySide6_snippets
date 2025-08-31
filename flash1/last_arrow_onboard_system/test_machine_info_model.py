# from PySide6.QtWidgets import QApplication, QHeaderView, QTabWidget, QTableView, QGridLayout, QVBoxLayout, QHBoxLayout, QGraphicsItem, QPushButton, QDoubleSpinBox, QSpinBox, QWidget, QLabel
# from PySide6.QtCharts import QChartView, QChart, QLineSeries, QVXYModelMapper, QAbstractAxis
# from PySide6.QtCore import QTimer, QAbstractTableModel, QIdentityProxyModel, QCoreApplication, QObject, QAbstractItemModel, QPersistentModelIndex, QModelIndex, QPoint, Qt
# from PySide6.QtGui import QShortcut, QKeySequence, QIcon
# from domain.units.MemoryBufferUnit import MemoryBufferUnit
# from domain.units.AbstractUnit import AbstractReadUnit, AbstractReadWriteUnit
# from domain.dto.Travelling import PicketDirection, LocationVector1D
# from domain.dto.Markers import RailwayMarker, RailwayMarkerLocation, RailwayMarkerType
# from domain.markers.BaseRailwayMarkerModel import BaseRailwayMarkerModel
# from domain.markers.AbstractMarkerModel import AbstractMarkerModel
# from presentation.ui.gui.common.viewes.RailwayMarkerView import RailwayMarkerLinesScatter, SelectCurrentMarkerWindow
from typing import Optional, Union, Dict, List, Any
from dataclasses import dataclass
import pandas
import random
import math
import sys
import socketserver
import http.server
from PySide6.QtCharts import QSplineSeries, QChart, QChartView, QLineSeries, QLegend, QValueAxis, QCategoryAxis
from PySide6.QtGui import QPainter, QImage, QColor, QPolygon, QPaintEvent, QConicalGradient, QGradient, QBrush, QRegion, QResizeEvent
from PySide6.QtCore import Signal, QObject, QSize, QRect, QPoint, QPointF, Qt
from PySide6.QtWidgets import QApplication, QHeaderView, QWidget, QDialog, QLineEdit, QSpinBox, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout, QSizePolicy
from typing import List, Tuple, Optional
import numpy
import uuid

class ZeroAxisSeries(QLineSeries):
    def __init__(self, parent: Optional[QObject] = None) ->None:
        super().__init__(parent)
        self.append(QPointF(0, -10000000))
        self.append(QPointF(0, 10000000))


if __name__ == '__main__':
    app = QApplication(sys.argv)


    zero_axis = ZeroAxisSeries()

    series = QLineSeries()
    series.append(0, 10)
    series.append(10, 20)
    series.append(20, 5)

    chart = QChart()
    chart.setTitle("Chart with Zero Line")

    axisX = QValueAxis()
    axisX.setMin(-20)  # Минимальное значение оси X
    axisX.setMax(20)  # Максимальное значение оси X
    axisX.setLabelFormat("%d")  # Формат меток оси X

    axisY = QValueAxis()
    axisY.setMin(-20)  # Минимальное значение оси Y
    axisY.setMax(20)  # Максимальное значение оси Y
    axisY.setLabelFormat("%d")  # Формат меток оси Y

    chart.addAxis(axisX, Qt.AlignBottom)  # Добавляем ось X
    chart.addAxis(axisY, Qt.AlignLeft)  # Добавляем ось Y

    # Включаем нулевую линию для осей X и Y
    axisX.setLinePenColor(QColor(Qt.red))  # Цвет нулевой линии по оси X
    axisX.setLineVisible(True)  # Отображение нулевой линии по оси X

    axisY.setLinePenColor(QColor(Qt.blue))  # Цвет нулевой линии по оси Y
    axisY.setLineVisible(True)  # Отображение нулевой линии по оси Y


    chart.addSeries(series)
    chart.addSeries(zero_axis)
    series.attachAxis(axisX)
    series.attachAxis(axisY)
    zero_axis.attachAxis(axisY)
    zero_axis.attachAxis(axisX)


    chartView = QChartView(chart)
    chartView.setRenderHint(QPainter.Antialiasing)
    chartView.show()

    sys.exit(app.exec_())
