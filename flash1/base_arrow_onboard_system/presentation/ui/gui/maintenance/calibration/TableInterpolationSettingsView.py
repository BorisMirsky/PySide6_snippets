from .....utils.interpolation.Strategies import AbstractInterpolationStrategy
from domain.units.AbstractUnit import AbstractReadUnit
from ...common.elements.SingleLineModel import SingleLineModel
from PySide6.QtCore import QModelIndex, QPersistentModelIndex, QAbstractItemModel, QPoint, QObject, Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem, QShortcut, QKeySequence
from PySide6.QtWidgets import QWidget, QLabel, QTableView, QHeaderView, QGridLayout
from PySide6.QtCharts import QChartView, QChart, QVXYModelMapper, QLineSeries
from typing import Optional, Union, Tuple


class TableInterpolationSettingsView(QWidget):
    def __init__(self, origin: AbstractReadUnit[float], xRange: Tuple[float, float], yRange: Tuple[float, float], parent: Optional[QWidget] = None) ->None:
        super().__init__(parent)
        self.__origin: AbstractReadUnit[float] = origin
        self.__model = QStandardItemModel(parent = self)
        self.__model.setColumnCount(2)

        # ============================================

        self.__horizontal_line_model = SingleLineModel()
        horizontal_line_series = QLineSeries()
        self.__horizontal_line_mapper = QVXYModelMapper()
        self.__horizontal_line_mapper.setModel(self.__horizontal_line_model)
        self.__horizontal_line_mapper.setSeries(horizontal_line_series)
        self.__horizontal_line_mapper.setXColumn(1)
        self.__horizontal_line_mapper.setYColumn(0)

        self.__vertical_line_model = SingleLineModel()
        vertical_line_series = QLineSeries()
        self.__vertical_line_mapper = QVXYModelMapper()
        self.__vertical_line_mapper.setModel(self.__vertical_line_model)
        self.__vertical_line_mapper.setSeries(vertical_line_series)
        self.__vertical_line_mapper.setXColumn(0)
        self.__vertical_line_mapper.setYColumn(1)
        
        # ============================================

        chart_view_series = QLineSeries()
        self.__chart_view_mapper = QVXYModelMapper()
        self.__chart_view_mapper.setModel(self.__model)
        self.__chart_view_mapper.setSeries(chart_view_series)
        self.__chart_view_mapper.setXColumn(0)
        self.__chart_view_mapper.setYColumn(1)

        # ============================================
        
        chart = QChart()
        chart.addSeries(chart_view_series)
        chart.addSeries(vertical_line_series)
        # chart.addSeries(horizontal_line_series)
        chart.createDefaultAxes()
        chart.axisX().setRange(*xRange)
        chart.axisY().setRange(*yRange)
        chart_view = QChartView(chart)
        
        # ============================================


        table_view = QTableView()
        table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table_view.verticalHeader().hide()
        table_view.setModel(self.__model)

        # ============================================

        labels_view = QWidget()
        labels_view_layout = QGridLayout()
        labels_view.setLayout(labels_view_layout)
        labels_view_layout.addWidget(QLabel("D"), 1, 0)
        labels_view_layout.addWidget(QLabel("A"), 1, 1)

        # ============================================

        layout = QGridLayout()
        self.setLayout(layout)
        layout.setRowStretch(0, 4)
        layout.setRowStretch(1, 1)
        layout.setColumnStretch(0, 2)
        layout.setColumnStretch(0, 1)
        layout.addWidget(chart_view, 0, 0)
        layout.addWidget(table_view, 0, 1)
        layout.addWidget(labels_view, 1, 0)

        # ============================================

        self.__moveTargetToTop = QShortcut(QKeySequence('W'), self)
        self.__moveTargetToTop.activated.connect(self.__onMoveTargetToTop)
        self.__moveTargetToBottom = QShortcut(QKeySequence('S'), self)
        self.__moveTargetToBottom.activated.connect(self.__onMoveTargetToBottom)
        self.__moveTargetToRight = QShortcut(QKeySequence('D'), self)
        self.__moveTargetToRight.activated.connect(self.__onMoveTargetToRight)
        self.__moveTargetToLeft = QShortcut(QKeySequence('A'), self)
        self.__moveTargetToLeft.activated.connect(self.__onMoveTargetToLeft)
        self.__writeCurrentOriginValue = QShortcut(QKeySequence('Space'), self)
        self.__writeCurrentOriginValue.activated.connect(self.__onWriteCurrentOriginValue)

    def __onMoveTargetToTop(self) ->None:
        self.__horizontal_line_model.setPosition(self.__horizontal_line_model.position() + 1)
    def __onMoveTargetToBottom(self) ->None:
        self.__horizontal_line_model.setPosition(self.__horizontal_line_model.position() - 1)
    def __onMoveTargetToRight(self) ->None:
        self.__vertical_line_model.setPosition(self.__vertical_line_model.position() + 10)
    def __onMoveTargetToLeft(self) ->None:
        self.__vertical_line_model.setPosition(self.__vertical_line_model.position() - 10)
    def __onWriteCurrentOriginValue(self) ->None:
        self.__model.appendRow([QStandardItem(str(self.__vertical_line_model.position())), QStandardItem(str(self.__origin.read()))])
    
