# This Python file uses the following encoding: utf-8
from domain.units.AbstractUnit import AbstractReadUnit
from presentation.models.PicketPositionedTableModel import PicketPositionedTableModel
from PySide6.QtCharts import (QChartView, QChart, QAbstractAxis, QValueAxis, QAbstractSeries,
                              QLineSeries, QVXYModelMapper, QAreaSeries )
from PySide6.QtCore import QAbstractItemModel, QModelIndex, QObject, Qt, QPointF
from PySide6.QtWidgets import QGraphicsItem, QStyle
from PySide6.QtGui import QFont, QBrush, QColor, QPen
from typing import List, Tuple, Optional
import math

# ========================
# QLineSeries, выставляемая как нулевая ось || OX
class ZeroAxisSeries(QLineSeries):
    def __init__(self, parent: Optional[QObject] = None) ->None:
        super().__init__(parent)
        self.append(0, -10000000)
        self.append(0, 10000000)

# QLineSeries, берущий X и Y из колонок таблицы QAbstractItemModel
class DynamicLineSeries(QLineSeries):
    def __init__(self, model: QAbstractItemModel, xColumn: int, yColumn: int, name: Optional[str] = '', parent: Optional[QObject] = None) ->None:
        super().__init__(parent)
        self.__model: QAbstractItemModel = model
        self.__mapper = QVXYModelMapper(self)
        self.__mapper.setSeries(self)
        self.__mapper.setXColumn(xColumn)
        self.__mapper.setYColumn(yColumn)
        self.__mapper.setModel(self.__model)
        self.setName(name)
    def model(self) -> QAbstractItemModel:
        return self.__model
    def mapper(self) -> QVXYModelMapper:
        return self.__mapper


class AbstractChartOrientationMixin:
    def positionAxis(self) ->QAbstractAxis:
        pass
    def valueAxis(self) ->QAbstractAxis:
        pass

class HorizontalChartOrientationMixin(AbstractChartOrientationMixin):
    def positionAxis(self) ->QAbstractAxis:
        return self.axisX()
    def valueAxis(self) ->QAbstractAxis:
        return self.axisY()

class VerticalChartOrientationMixin(AbstractChartOrientationMixin):
    def positionAxis(self) ->QAbstractAxis:
        return self.axisY()
    def valueAxis(self) ->QAbstractAxis:
        return self.axisX()

####################################
class AutomaticalSeriesVerticalChart(QChart):
    def __init__(self, series: List[QAbstractSeries],
                 positionRange: Tuple[float, float],
                 positionReverse: bool, valueRange: Tuple[float, float], valueReverse: bool,
                 x_tick=False, y_tick=False, title=False,
                 xMinorTickCount=False, yMinorTickCount=False,
                 xGridLineColor=False, yGridLineColor=False,
                 xMinorGridLineColor=False, yMinorGridLineColor=False,
                 XAxisHideLabels=False, YAxisHideLabels=False,
                 parent: Optional[QGraphicsItem] = None) ->None:
        super().__init__(parent)
        for line in series:
            self.addSeries(line)
        self.x_axis = QValueAxis()
        self.y_axis = QValueAxis()
        self.x_axis.setLabelFormat("%d")
        self.y_axis.setLabelFormat("%d")       # "%d" "%+05d
        self.setAxisX(self.x_axis)
        self.setAxisY(self.y_axis)
        if x_tick:
            self.x_axis.setTickType(QValueAxis.TickType.TicksDynamic)
            self.x_axis.setTickInterval(x_tick)
        if y_tick:
            self.y_axis.setTickType(QValueAxis.TickType.TicksDynamic)
            for v in valueRange:
                if 0 < math.fabs(v) < 50:
                    y_tick = y_tick
                elif 50 < math.fabs(v) < 100:
                    y_tick = y_tick * 2
                elif 100 < math.fabs(v) < 500:
                    y_tick = y_tick * 5
                elif 500 < math.fabs(v) < 1000:
                    y_tick = y_tick * 10
            self.y_axis.setTickInterval(y_tick)
        self.x_axis.tickType()
        font_axis_y = QFont()
        font_axis_y.setPixelSize(12)
        self.y_axis.setLabelsFont(font_axis_y)
        self.x_axis.setLabelsFont(font_axis_y)
        axis_brush = QBrush(QColor("white"))
        self.legend().setLabelColor(QColor('white'))
        if title:
            self.y_axis.setTitleText(title)
            self.y_axis.setTitleBrush(axis_brush)
        self.y_axis.setLabelsBrush(axis_brush)
        self.x_axis.setLabelsBrush(axis_brush)
        if xMinorTickCount:
            self.x_axis.setMinorTickCount(xMinorTickCount)
        if yMinorTickCount:
            self.y_axis.setMinorTickCount(yMinorTickCount)
        if xGridLineColor:
            self.x_axis.setGridLineColor(QColor(xGridLineColor))
        if yGridLineColor:
            self.y_axis.setGridLineColor(QColor(yGridLineColor))
        if xMinorGridLineColor:
            self.x_axis.setMinorGridLineColor(xMinorGridLineColor)
        if yMinorGridLineColor:
            self.y_axis.setMinorGridLineColor(yMinorGridLineColor)
        if XAxisHideLabels:
            self.x_axis.setLabelsVisible(False)
        if YAxisHideLabels:
            self.y_axis.setLabelsVisible(False)
        #
        if title:
            self.y_axis.setTitleText(title)
            font_title = QFont()
            font_title.setPixelSize(16)
            self.y_axis.setTitleFont(font_title)
            self.y_axis.setTitleBrush(QBrush(QColor("white")))
            #self.y_axis.setTitleText(title)
            #self.y_axis.setTitleBrush(axis_brush)
        # if 'title' in kwargs.keys():
        #     self.y_axis.setTitleText(kwargs['title'])
        #     self.y_axis.setTitleBrush(axis_brush)
        # if 'titleLeftSide' in kwargs.keys():
        #     self.y_axis.setTitleText(kwargs['titleLeftSide'])
        #     font_title = QFont()
        #     font_title.setPixelSize(16)
        #     self.y_axis.setTitleFont(font_title)
        #     self.y_axis.setTitleBrush(QBrush(QColor("white")))
        #
        self.y_zero_series = QLineSeries()
        self.y_zero_series.append(QPointF(0,0))
        self.y_zero_series.append(QPointF(0, 10000))
        self.y_zero_series.setPen(QPen(Qt.GlobalColor.white, 1, Qt.DotLine))
        self.addSeries(self.y_zero_series)
        self.y_zero_series.attachAxis(self.y_axis)
        self.y_zero_series.attachAxis(self.x_axis)
        # Прячем все series из лeгенды
        markersList = self.legend().markers()
        markersList[-1].setVisible(False)      # zero_line
        markersList[-2].setVisible(False)      # position
        self.x_axis.setReverse(positionReverse)
        self.x_axis.setRange(*valueRange) #positionRange)
        self.y_axis.setReverse(valueReverse)
        #self.y_axis.setRange(*valueRange)
        for line in series:
            line.attachAxis(self.x_axis)
            line.attachAxis(self.y_axis)

class AutomaticalSeriesChart(QChart):
    def __init__(self, positionRange: Tuple[float, float], positionReverse: bool,
                 valueRange: Tuple[float, float], valueReverse: bool,
                 parent: Optional[QGraphicsItem] = None, **kwargs,) ->None:
        super().__init__(parent)
        self.x_axis = QValueAxis()
        self.y_axis = QValueAxis()
        if 'areaSeries' in kwargs.keys():
            self.zeroHorizontalAxeSeries = QLineSeries()
            self.zeroHorizontalAxeSeries.append(QPointF(0, 0))
            self.zeroHorizontalAxeSeries.append(QPointF(100000, 0))
            self.series = kwargs['areaSeries']
            self.areaSeries = QAreaSeries(self.series, self.zeroHorizontalAxeSeries)
            self.areaSeries.setBrush(QBrush(kwargs['areaSeriesColor']))
            for line in [self.areaSeries]:
                self.addSeries(line)
        if 'series0' in kwargs.keys():
            for line in kwargs['series0']:
                self.addSeries(line)
        if 'series1' in kwargs.keys():
            for line in kwargs['series1']:
                self.addSeries(line)
        if 'series2' in kwargs.keys():
            for line in kwargs['series2']:
                self.addSeries(line)
        self.setAxisX(self.x_axis)
        self.setAxisY(self.y_axis)
        if 'levelBoundaryLine1' in kwargs.keys():
            if kwargs['levelBoundaryLine1'] == 'pass':
                pass
            else:
                self.levelBoundaryLine1 = QLineSeries()
                self.levelBoundaryLine1.append(QPointF(positionRange[0], kwargs['levelBoundaryLine1']))
                self.levelBoundaryLine1.append(QPointF(positionRange[1],  kwargs['levelBoundaryLine1']))
                self.levelBoundaryLine1.setPen(QPen(Qt.GlobalColor.yellow, 2)) #, Qt.DashDotLine))
                self.addSeries(self.levelBoundaryLine1)
                self.levelBoundaryLine1.attachAxis(self.y_axis)
                self.levelBoundaryLine1.attachAxis(self.x_axis)
        if 'levelBoundaryLine2' in kwargs.keys():
            if kwargs['levelBoundaryLine2'] == 'pass':
                pass
            else:
                self.levelBoundaryLine2 = QLineSeries()
                self.levelBoundaryLine2.append(QPointF(positionRange[0], kwargs['levelBoundaryLine2']))
                self.levelBoundaryLine2.append(QPointF(positionRange[1], kwargs['levelBoundaryLine2']))
                self.levelBoundaryLine2.setPen(QPen(Qt.GlobalColor.yellow, 2)) #, Qt.DashDotLine))
                self.addSeries(self.levelBoundaryLine2)
                self.levelBoundaryLine2.attachAxis(self.y_axis)
                self.levelBoundaryLine2.attachAxis(self.x_axis)
        font_axis_y = QFont()
        font_axis_y.setPixelSize(12)
        self.x_axis.setLabelFormat("%d")
        self.y_axis.setLabelFormat('%d')    #"%d")   # Надо так "{:4d}" или так "{:<4}"      "%.3d"  '%+05d' - добавляет нули, не годится
        if 'x_tick' in kwargs.keys():
            self.x_axis.setTickType(QValueAxis.TickType.TicksDynamic)
            self.x_axis.setTickInterval(kwargs['x_tick'])
        if 'y_tick' in kwargs.keys():
            self.y_axis.setTickType(QValueAxis.TickType.TicksDynamic)                     # Статичные графики
            #  default    y_tick=10
            chart_window_size = math.fabs(valueRange[0]) + math.fabs(valueRange[1])        # размер окна по Y
            if 0 < chart_window_size < 0.5:
                y_tick = kwargs['y_tick'] * 0.01    # 0.1
                #self.y_axis.setLabelFormat("%2g")   # !
            elif 0.5 < chart_window_size < 1:
                y_tick = kwargs['y_tick'] * 0.02   # 0.2
                #self.y_axis.setLabelFormat("%2g")  #  !
            elif 1 < chart_window_size < 5:
                y_tick = kwargs['y_tick'] * 0.1   # 1
            elif 5 < chart_window_size < 10:
                y_tick = kwargs['y_tick'] * 0.2   # 2
            elif 10 < chart_window_size < 50:
                y_tick = kwargs['y_tick']         # 10
            elif 50 < chart_window_size < 100:
                y_tick = kwargs['y_tick'] * 2     # 20
            elif 100 < chart_window_size < 500:
                y_tick = kwargs['y_tick'] * 10    # 100
            elif 500 < chart_window_size < 1000:
                y_tick = kwargs['y_tick'] * 20    # 200
            elif 1000 < chart_window_size < 5000:
                y_tick = kwargs['y_tick'] * 100   # 1000
            elif 5000 < chart_window_size:
                y_tick = kwargs['y_tick'] * 200    # 2000
            #
            if (chart_window_size / y_tick) < 2:      # чтобы не было пустых клеток
                y_tick = (y_tick / 2)
            if type(y_tick) == float:
                self.y_axis.setLabelFormat("%2g")
            else:
                self.y_axis.setLabelFormat("%d")
            self.y_axis.setTickInterval(y_tick)
        if 'xMinorTickCount' in kwargs.keys():
            self.x_axis.setMinorTickCount(kwargs['xMinorTickCount'])
        if 'yMinorTickCount' in kwargs.keys():
            self.y_axis.setMinorTickCount(kwargs['yMinorTickCount'])
        if 'xGridLineColor' in kwargs.keys():
            self.x_axis.setGridLineColor(QColor(kwargs['xGridLineColor']))
        if 'yGridLineColor' in kwargs.keys():
            self.y_axis.setGridLineColor(QColor(kwargs['yGridLineColor']))
        if 'xMinorGridLineColor' in kwargs.keys():
            self.x_axis.setMinorGridLineColor(kwargs['xMinorGridLineColor'])
        if 'yMinorGridLineColor' in kwargs.keys():
            self.y_axis.setMinorGridLineColor(kwargs['yMinorGridLineColor'])
        if 'XAxisHideLabels' in kwargs.keys():
            self.x_axis.setLabelsVisible(False)
        if 'YAxisHideLabels' in kwargs.keys():
            self.y_axis.setLabelsVisible(False)
        self.y_axis.setLabelsFont(QFont('monospace', 9))      #font_axis_y)
        self.x_axis.setLabelsFont(font_axis_y)
        axis_brush = QBrush(QColor("white"))
        if 'title' in kwargs.keys():
            self.y_axis.setTitleText(kwargs['title'])
            self.y_axis.setTitleBrush(axis_brush)
        if 'titleLeftSide' in kwargs.keys():
            self.y_axis.setTitleText(kwargs['titleLeftSide'])
            font_title = QFont()
            font_title.setPixelSize(16)
            self.y_axis.setTitleFont(font_title)
            self.y_axis.setTitleBrush(QBrush(QColor("white")))
        self.y_axis.setLabelsBrush(axis_brush)
        self.x_axis.setLabelsBrush(axis_brush)
        self.y_zero_series = QLineSeries()
        self.y_zero_series.append(QPointF(positionRange[0], 0))
        self.y_zero_series.append(QPointF(positionRange[1], 0))
        self.y_zero_series.setPen(QPen(Qt.GlobalColor.white, 2, Qt.DashDotLine))    # yellow   DashLine
        #self.addSeries(self.y_zero_series)
        if kwargs.get('is_y_zero_axe_visible', True):
                self.addSeries(self.y_zero_series)
                self.y_zero_series.attachAxis(self.y_axis)
                self.y_zero_series.attachAxis(self.x_axis)
        self.x_axis.setReverse(positionReverse)
        self.x_axis.setRange(*positionRange)
        self.y_axis.setReverse(valueReverse)
        self.y_axis.setRange(*valueRange)
        if 'areaSeries' in kwargs.keys():
            for line in [self.areaSeries]:
                line.attachAxis(self.x_axis)
                line.attachAxis(self.y_axis)
        if 'series0' in kwargs.keys():
            for line in kwargs['series0']:
                line.attachAxis(self.x_axis)
                line.attachAxis(self.y_axis)
        if 'series1' in kwargs.keys():
            for line in kwargs['series1']:
                line.attachAxis(self.x_axis)
                line.attachAxis(self.y_axis)
        if 'series2' in kwargs.keys():
            for line in kwargs['series2']:
                line.attachAxis(self.x_axis)
                line.attachAxis(self.y_axis)


##################################
class HorizontalChart(HorizontalChartOrientationMixin, AutomaticalSeriesChart):    # LiningView.EmergencyExtractionProcessView  !?
    pass

class VerticalChart(VerticalChartOrientationMixin, AutomaticalSeriesVerticalChart):       # measuring trip
    pass
# ========================

# Класс для обновления состояния графиков в ВЫПРАВОЧНой + ИЗМЕРИТЕЛЬНой поездках
class ChartSlidingWindowProvider(QObject):
    def __init__(self,
                 position: AbstractReadUnit[float],
                 viewes: List[QChartView],
                 charts: List[AbstractChartOrientationMixin],
                 windowSize: Tuple[float, float],
                 mappers: List[QVXYModelMapper],
                 windowPoints: Tuple[int, int],
                 isVertical: bool,
                 program_task_by_picket: PicketPositionedTableModel = False,
                 parent: Optional[QObject] = None) ->None:

        super().__init__(parent)
        self.__mappers: List[QVXYModelMapper] = mappers
        self.__windowPoints: Tuple[int, int] = windowPoints
        self.__charts: List[AbstractChartOrientationMixin] = charts
        self.__windowSize: Tuple[float, float] = windowSize
        self.__viewes: List[QChartView] = viewes
        self.__position: AbstractReadUnit[float] = position
        self.__next_mapper_jump_position: float = 0
        if program_task_by_picket:
            self.__start_picket = program_task_by_picket.startPicket()
            self.__multiplier = program_task_by_picket.picketDirection().multiplier()
            self.__program_task = program_task_by_picket.sourceModel()
        self.isVertical = isVertical

    def enableViewUpdates(self) ->None:
        for view in self.__viewes:
            view.setUpdatesEnabled(True)

    def disableViewUpdates(self) ->None:
        for view in self.__viewes:
            view.setUpdatesEnabled(False)

    def updateChartsState(self) ->None:
        currentPosition = self.__position.read()
        if self.isVertical:
            from_position = currentPosition - self.__windowSize[0]
            to_position = currentPosition + self.__windowSize[1]
            for chart in self.__charts:
                chart.positionAxis().setRange(from_position, to_position)

        else:
            from_position = currentPosition - self.__windowSize[0] * self.__multiplier
            to_position = currentPosition + self.__windowSize[1] * self.__multiplier

            from_index = int( (from_position - self.__start_picket) * self.__multiplier / self.__program_task.step().meters )
            to_index = int( (to_position - self.__start_picket) * self.__multiplier / self.__program_task.step().meters )

            for chart in self.__charts:          # chart - одна картинка (ChartView), может быть с несколькими Series
                one_chart_min_max_points = []    # все min & max всех Series одного chart'a
                chart.positionAxis().setRange(min(from_position, to_position), max(from_position, to_position))
                for column_name in chart.column_names:    # column_name - одна Series
                    value_min, value_max = self.__program_task.minmaxValueByColumnInRange(column_name, from_index, to_index)
                    one_chart_min_max_points.append(value_min)
                    one_chart_min_max_points.append(value_max)
                    if value_min is None or value_max is None:
                        continue
                chart_window_size: float = math.fabs(max(0, max(one_chart_min_max_points)) - min(0, min(one_chart_min_max_points)))
                if 0 < chart_window_size < 1:
                    y_tick = 0.1
                elif 1 < chart_window_size < 5:
                    y_tick = 1
                elif 5 < chart_window_size < 10:
                    y_tick = 2
                elif 10 < chart_window_size < 50:
                    y_tick = 10
                elif 50 < chart_window_size < 100:
                    y_tick = 20
                elif 100 < chart_window_size < 500:
                    y_tick = 100
                elif 500 < chart_window_size < 1000:
                    y_tick = 200
                else:
                    y_tick = 500
                if (chart_window_size / y_tick) < 2:
                    y_tick = (y_tick / 2)
                chart.valueAxis().setTickInterval(y_tick)
#                y_axis.setTickInterval(y_tick)
                chart.valueAxis().setRange(min(0, min(one_chart_min_max_points)) - chart_window_size*0.05,
                                           max(0, max(one_chart_min_max_points)) + chart_window_size*0.05)

            if self.__next_mapper_jump_position < currentPosition:
                self.__next_mapper_jump_position = currentPosition + self.__windowPoints[0]
            for mapper in self.__mappers:
                if mapper.series().count() > mapper.count() * 0.8:
                    mapper.setFirstRow(max(0, mapper.model().rowCount(QModelIndex()) - self.__windowPoints[1]))

# ========================


# Класс для обновления состояния графиков в ИЗМЕРИТЕЛЬНОЙ поездка
# Не используется
# class ChartSlidingWindowProviderMeasuringTrip(QObject):
#     def __init__(self,
#                  position: AbstractReadUnit[float],
#                  viewes: List[QChartView],
#                  charts: List[AbstractChartOrientationMixin],
#                  windowSize: Tuple[float, float],
#                  mappers: List[QVXYModelMapper],
#                  windowPoints: Tuple[int, int],
#                  parent: Optional[QObject] = None) ->None:
#         super().__init__(parent)
#         self.__mappers: List[QVXYModelMapper] = mappers
#         self.__windowPoints: Tuple[int, int] = windowPoints
#         self.__charts: List[AbstractChartOrientationMixin] = charts
#         self.__windowSize: Tuple[float, float] = windowSize
#         self.__viewes: List[QChartView] = viewes
#
#         self.__position: AbstractReadUnit[float] = position
#         self.__next_mapper_jump_position: float = 0
#
#     def enableViewUpdates(self) ->None:
#         for view in self.__viewes:
#             view.setUpdatesEnabled(True)
#     def disableViewUpdates(self) ->None:
#         for view in self.__viewes:
#             view.setUpdatesEnabled(False)
#
#     def updateChartsState(self) ->None:
#         currentPosition = self.__position.read()
#         from_position = currentPosition - self.__windowSize[0] - 0.1
#         to_position = currentPosition + self.__windowSize[1]  - 0.1
#         for chart in self.__charts:
#             chart.positionAxis().setRange(from_position, to_position)

# ========================

