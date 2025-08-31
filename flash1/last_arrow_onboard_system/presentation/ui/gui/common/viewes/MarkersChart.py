# This Python file uses the following encoding: utf-8
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import  Qt, QPen, QPainter, QBrush
from PySide6.QtCharts import QChartView, QLineSeries,QVXYModelMapper, QScatterSeries
from PySide6.QtCore import *
from typing import List, Any, Tuple

from domain.dto.Workflow import ProgramTaskCalculationOptionsDto
from domain.dto.Travelling import PicketDirection, LocationVector1D
from domain.dto.Markers import RailwayMarker, RailwayMarkerLocation, RailwayMarkerType
from presentation.ui.gui.common.viewes.TableDataChartsView import HorizontalMarkersChart
from domain.models.StepIndexedDataFramePositionedModel import ReducedStepIndexedPositionedModel
from domain.models.VerticalLineModel import VerticalLineModel
import numpy as np


class NumpyTableModel(QAbstractTableModel):
    def __init__(self, data: np.array, parent: QObject = None):
        super().__init__(parent)
        self.__data: np.array = data
        self.removed_picket_index = 0

    def columnCount(self, parent: QModelIndex) -> int:
        return self.__data.shape[1]

    def rowCount(self, parent: QModelIndex) -> int:
        return self.__data.shape[0]

    def data(self, index: QModelIndex, role: int) -> Any:
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if not index.isValid():
            return None
        return str(self.__data[index.row()][index.column()])

    def appendRow(self, record: List[float]):
        self.beginInsertRows(QModelIndex(), self.rowCount(QModelIndex()), self.rowCount(QModelIndex()))
        self.__data = np.vstack([self.__data, record])
        self.endInsertRows()


class MarkersChart(QWidget):
    def __init__(self, 
                 options: ProgramTaskCalculationOptionsDto, 
                 title:str = None,
                 verticalModel: VerticalLineModel = None,
                 parent: QWidget = None ) ->None:
        super().__init__(parent)
        self.__options = options
        self.__title = title
        self.__model = verticalModel
        #self.__restrictions = options.restrictions

        self.measurements_model = ReducedStepIndexedPositionedModel(
            step=self.__options.measuring_trip.measurements.step,
            data=self.__options.measuring_trip.measurements.data,
            parent=self,
        )
        
        self.position_multiplyer: int = self.__options.picket_direction.multiplier()
        self.position_range: tuple[LocationVector1D, LocationVector1D] = self.measurements_model.minmaxPosition()
        self.start_picket = self.__options.start_picket.meters
        self.position_min: float = self.position_multiplyer * self.position_range[0].meters + self.start_picket
        self.position_max: float = self.position_multiplyer * self.position_range[1].meters + self.start_picket
        self.currentPosition = self.start_picket

        self.markers: List[Tuple[RailwayMarker, float]] = self.__options.measuring_trip.tags

        self.__situation_empty_chart: HorizontalMarkersChart
        self.__situation_empty_chart = self.__createChart()
        self.__chart = self.__fillChart()

    def getChart(self):
        return self.__chart
    
    def __createChart(self):
        chart = HorizontalMarkersChart((self.position_min, self.position_max),
                                    self.__options.picket_direction == PicketDirection.Backward, False,
                                    x_tick=100, y_tick=10,
                                    title=self.__title,
                                    xMinorTickCount=9,
                                    xGridLineColor="gray", yGridLineColor="gray",
                                    xMinorGridLineColor="gray", yMinorGridLineColor="gray",
                                    is_y_zero_axe_visible=False
                                    )
        if self.__model:
            # вертикальная черта, одинаковая (общая) для всех
            vertical_line_series = QLineSeries()
            vertical_line_series.setPen(QPen(Qt.GlobalColor.magenta, 2))
            lineMapper = QVXYModelMapper(self)
            lineMapper.setXColumn(0)
            lineMapper.setYColumn(1)
            lineMapper.setSeries(vertical_line_series)
            lineMapper.setModel(self.__model)
            # вторая статичная
            self.vertical_static_line_series_plan = QLineSeries()
            self.vertical_static_line_series_plan.setPen(QPen(Qt.GlobalColor.green, 2))
            self.vertical_static_line_series_profile = QLineSeries()
            self.vertical_static_line_series_profile.setPen(QPen(Qt.GlobalColor.green, 2))
            self.vertical_static_line_series_speed = QLineSeries()
            self.vertical_static_line_series_speed.setPen(QPen(Qt.GlobalColor.green, 2))
            self.lineMapper_for_static_line = QVXYModelMapper(self)
            self.lineMapper_for_static_line.setXColumn(0)
            self.lineMapper_for_static_line.setYColumn(1)
            #self.lineMapper_for_static_line.setSeries(self.vertical_static_line_series_plan)
            #
            chart.addSeries(vertical_line_series)
            vertical_line_series.attachAxis(chart.axisX())
            vertical_line_series.attachAxis(chart.axisY())
            #

        chart.legend().hide()
        chart.layout().setContentsMargins(0, 0, 0, 0)
        chart.setMargins(QMargins(0, 0, 0, 0))
        chart.axes(Qt.Orientation.Horizontal)[0].setGridLineVisible(True)
        chart.axes(Qt.Orientation.Vertical)[0].setGridLineVisible(True)
        chart.setObjectName("situation_empty_chart")
        return chart
    
    def __fillChart(self):
        self.scatter_model_1 = NumpyTableModel(np.ones((0, 2)), qApp)
        self.scatter_model_2 = NumpyTableModel(np.ones((0, 2)), qApp)
        self.scatter_model_3 = NumpyTableModel(np.ones((0, 2)), qApp)
        self.scatter_model_4 = NumpyTableModel(np.ones((0, 2)), qApp)
        self.scatter_model_5 = NumpyTableModel(np.ones((0, 2)), qApp)
        self.scatter_model_6 = NumpyTableModel(np.ones((0, 2)), qApp)
        self.scatter_model_7 = NumpyTableModel(np.ones((0, 2)), qApp)
        self.scatter_model_8 = NumpyTableModel(np.ones((0, 2)), qApp)
        self.scatter_model_9 = NumpyTableModel(np.ones((0, 2)), qApp)
        self.scatter_model_10 = NumpyTableModel(np.ones((0, 2)), qApp)

        self.marker_series_1 = QScatterSeries(self.scatter_model_1)
        self.marker_series_2 = QScatterSeries(self.scatter_model_2)
        self.marker_series_3 = QScatterSeries(self.scatter_model_3)
        self.marker_series_4 = QScatterSeries(self.scatter_model_4)
        self.marker_series_5 = QScatterSeries(self.scatter_model_5)
        self.marker_series_6 = QScatterSeries(self.scatter_model_6)
        self.marker_series_7 = QScatterSeries(self.scatter_model_7)
        self.marker_series_8 = QScatterSeries(self.scatter_model_8)
        self.marker_series_9 = QScatterSeries(self.scatter_model_9)
        self.marker_series_10 = QScatterSeries(self.scatter_model_10)

        self.__situation_empty_chart.addSeries(self.marker_series_1)
        self.__situation_empty_chart.addSeries(self.marker_series_2)
        self.__situation_empty_chart.addSeries(self.marker_series_3)
        self.__situation_empty_chart.addSeries(self.marker_series_4)
        self.__situation_empty_chart.addSeries(self.marker_series_5)
        self.__situation_empty_chart.addSeries(self.marker_series_6)
        self.__situation_empty_chart.addSeries(self.marker_series_7)
        self.__situation_empty_chart.addSeries(self.marker_series_8)
        self.__situation_empty_chart.addSeries(self.marker_series_9)
        self.__situation_empty_chart.addSeries(self.marker_series_10)

        mapper_for_markers_1 = QVXYModelMapper(self)
        mapper_for_markers_1.setXColumn(0)
        mapper_for_markers_1.setYColumn(1)
        mapper_for_markers_1.setModel(self.scatter_model_1)
        mapper_for_markers_1.setSeries(self.marker_series_1)

        mapper_for_markers_2 = QVXYModelMapper(self)
        mapper_for_markers_2.setXColumn(0)
        mapper_for_markers_2.setYColumn(1)
        mapper_for_markers_2.setModel(self.scatter_model_2)
        mapper_for_markers_2.setSeries(self.marker_series_2)

        mapper_for_markers_3 = QVXYModelMapper(self)
        mapper_for_markers_3.setXColumn(0)
        mapper_for_markers_3.setYColumn(1)
        mapper_for_markers_3.setModel(self.scatter_model_3)
        mapper_for_markers_3.setSeries(self.marker_series_3)

        mapper_for_markers_4 = QVXYModelMapper(self)
        mapper_for_markers_4.setXColumn(0)
        mapper_for_markers_4.setYColumn(1)
        mapper_for_markers_4.setModel(self.scatter_model_4)
        mapper_for_markers_4.setSeries(self.marker_series_4)

        mapper_for_markers_5 = QVXYModelMapper(self)
        mapper_for_markers_5.setXColumn(0)
        mapper_for_markers_5.setYColumn(1)
        mapper_for_markers_5.setModel(self.scatter_model_5)
        mapper_for_markers_5.setSeries(self.marker_series_5)

        mapper_for_markers_6 = QVXYModelMapper(self)
        mapper_for_markers_6.setXColumn(0)
        mapper_for_markers_6.setYColumn(1)
        mapper_for_markers_6.setModel(self.scatter_model_6)
        mapper_for_markers_6.setSeries(self.marker_series_6)

        mapper_for_markers_7 = QVXYModelMapper(self)
        mapper_for_markers_7.setXColumn(0)
        mapper_for_markers_7.setYColumn(1)
        mapper_for_markers_7.setModel(self.scatter_model_7)
        mapper_for_markers_7.setSeries(self.marker_series_7)

        mapper_for_markers_8 = QVXYModelMapper(self)
        mapper_for_markers_8.setXColumn(0)
        mapper_for_markers_8.setYColumn(1)
        mapper_for_markers_8.setModel(self.scatter_model_8)
        mapper_for_markers_8.setSeries(self.marker_series_8)

        mapper_for_markers_9 = QVXYModelMapper(self)
        mapper_for_markers_9.setXColumn(0)
        mapper_for_markers_9.setYColumn(1)
        mapper_for_markers_9.setModel(self.scatter_model_9)
        mapper_for_markers_9.setSeries(self.marker_series_9)

        mapper_for_markers_10 = QVXYModelMapper(self)
        mapper_for_markers_10.setXColumn(0)
        mapper_for_markers_10.setYColumn(1)
        mapper_for_markers_10.setModel(self.scatter_model_10)
        mapper_for_markers_10.setSeries(self.marker_series_10)
        #
        marker_position_dict = {RailwayMarkerLocation.Left: 25,
                         RailwayMarkerLocation.Middle: 15,
                         RailwayMarkerLocation.Right: 5}
        marker_type_dict = {RailwayMarkerType.UNDEFINED: [QScatterSeries.MarkerShapeCircle, 'red'],
                            RailwayMarkerType.RfidTag: [QScatterSeries.MarkerShapeRectangle, 'cyan'],
                            RailwayMarkerType.ContactNetwork: [QScatterSeries.MarkerShapePentagon, 'green'],
                            RailwayMarkerType.Platform: [QScatterSeries.MarkerShapeStar, 'yellow'],
                            RailwayMarkerType.Tunnel: [QScatterSeries.MarkerShapeCircle, 'gray'],
                            RailwayMarkerType.ArrowPointer: [QScatterSeries.MarkerShapeTriangle, 'blue'],
                            RailwayMarkerType.ArrowCross: [QScatterSeries.MarkerShapePentagon, 'magenta'],
                            RailwayMarkerType.StationaryBrakeStop: [QScatterSeries.MarkerShapeRectangle, 'darkGreen'],
                            RailwayMarkerType.CrossPipe: [QScatterSeries.MarkerShapeStar, 'darkRed'],
                            RailwayMarkerType.Miscellaneous: [QScatterSeries.MarkerShapeTriangle, 'darkBlue'],
                            }
        if self.markers:
            for marker in self.markers:
                if marker[0].type == RailwayMarkerType.UNDEFINED:
                    self.marker_series_1.setMarkerShape(marker_type_dict[marker[0].type][0])
                    self.marker_series_1.setMarkerSize(10.0)
                    self.marker_series_1.setColor(marker_type_dict[marker[0].type][1])
                    self.marker_series_1.attachAxis(self.__situation_empty_chart.axisX())
                    self.marker_series_1.attachAxis(self.__situation_empty_chart.axisY())
                    self.scatter_model_1.appendRow([round(marker[1].meters), marker_position_dict[marker[0].location]])
                elif marker[0].type == RailwayMarkerType.RfidTag:
                    self.marker_series_2.setMarkerShape(marker_type_dict[marker[0].type][0])
                    self.marker_series_2.setMarkerSize(10.0)
                    self.marker_series_2.setColor(marker_type_dict[marker[0].type][1])
                    self.marker_series_2.attachAxis(self.__situation_empty_chart.axisX())
                    self.marker_series_2.attachAxis(self.__situation_empty_chart.axisY())
                    self.scatter_model_2.appendRow([round(marker[1].meters), marker_position_dict[marker[0].location]])
                elif marker[0].type == RailwayMarkerType.ContactNetwork:
                    self.marker_series_3.setMarkerShape(marker_type_dict[marker[0].type][0])
                    self.marker_series_3.setMarkerSize(10.0)
                    self.marker_series_3.setColor(marker_type_dict[marker[0].type][1])
                    self.marker_series_3.attachAxis(self.__situation_empty_chart.axisX())
                    self.marker_series_3.attachAxis(self.__situation_empty_chart.axisY())
                    self.scatter_model_3.appendRow([round(marker[1].meters), marker_position_dict[marker[0].location]])
                elif marker[0].type == RailwayMarkerType.Platform:
                    self.marker_series_4.setMarkerShape(marker_type_dict[marker[0].type][0])
                    self.marker_series_4.setMarkerSize(10.0)
                    self.marker_series_4.setColor(marker_type_dict[marker[0].type][1])
                    self.marker_series_4.attachAxis(self.__situation_empty_chart.axisX())
                    self.marker_series_4.attachAxis(self.__situation_empty_chart.axisY())
                    self.scatter_model_4.appendRow([round(marker[1].meters), marker_position_dict[marker[0].location]])
                elif marker[0].type == RailwayMarkerType.Tunnel:
                    self.marker_series_5.setMarkerShape(marker_type_dict[marker[0].type][0])
                    self.marker_series_5.setMarkerSize(10.0)
                    self.marker_series_5.setColor(marker_type_dict[marker[0].type][1])
                    self.marker_series_5.attachAxis(self.__situation_empty_chart.axisX())
                    self.marker_series_5.attachAxis(self.__situation_empty_chart.axisY())
                    self.scatter_model_5.appendRow([round(marker[1].meters), marker_position_dict[marker[0].location]])
                elif marker[0].type == RailwayMarkerType.ArrowPointer:
                    self.marker_series_6.setMarkerShape(marker_type_dict[marker[0].type][0])
                    self.marker_series_6.setMarkerSize(10.0)
                    self.marker_series_6.setColor(marker_type_dict[marker[0].type][1])
                    self.marker_series_6.attachAxis(self.__situation_empty_chart.axisX())
                    self.marker_series_6.attachAxis(self.__situation_empty_chart.axisY())
                    self.scatter_model_6.appendRow([round(marker[1].meters), marker_position_dict[marker[0].location]])
                elif marker[0].type == RailwayMarkerType.ArrowCross:
                    self.marker_series_7.setMarkerShape(marker_type_dict[marker[0].type][0])
                    self.marker_series_7.setMarkerSize(10.0)
                    self.marker_series_7.setColor(marker_type_dict[marker[0].type][1])
                    self.marker_series_7.attachAxis(self.__situation_empty_chart.axisX())
                    self.marker_series_7.attachAxis(self.__situation_empty_chart.axisY())
                    self.scatter_model_7.appendRow([round(marker[1].meters), marker_position_dict[marker[0].location]])
                elif marker[0].type == RailwayMarkerType.StationaryBrakeStop:
                    self.marker_series_8.setMarkerShape(marker_type_dict[marker[0].type][0])
                    self.marker_series_8.setMarkerSize(10.0)
                    self.marker_series_8.setColor(marker_type_dict[marker[0].type][1])
                    self.marker_series_8.attachAxis(self.__situation_empty_chart.axisX())
                    self.marker_series_8.attachAxis(self.__situation_empty_chart.axisY())
                    self.scatter_model_8.appendRow([round(marker[1].meters), marker_position_dict[marker[0].location]])
                elif marker[0].type == RailwayMarkerType.CrossPipe:
                    self.marker_series_9.setMarkerShape(marker_type_dict[marker[0].type][0])
                    self.marker_series_9.setMarkerSize(10.0)
                    self.marker_series_9.setColor(marker_type_dict[marker[0].type][1])
                    self.marker_series_9.attachAxis(self.__situation_empty_chart.axisX())
                    self.marker_series_9.attachAxis(self.__situation_empty_chart.axisY())
                    self.scatter_model_9.appendRow([round(marker[1].meters), marker_position_dict[marker[0].location]])
                elif marker[0].type == RailwayMarkerType.Miscellaneous:
                    self.marker_series_10.setMarkerShape(marker_type_dict[marker[0].type][0])
                    self.marker_series_10.setMarkerSize(10.0)
                    self.marker_series_10.setColor(marker_type_dict[marker[0].type][1])
                    self.marker_series_10.attachAxis(self.__situation_empty_chart.axisX())
                    self.marker_series_10.attachAxis(self.__situation_empty_chart.axisY())
                    self.scatter_model_10.appendRow([round(marker[1].meters), marker_position_dict[marker[0].location]])
        #
        chart = QChartView(self.__situation_empty_chart)
        chart.setFocusPolicy(Qt.NoFocus)
        chart.setObjectName("chart_view_situation_empty_chart")
        chart.chart().setBackgroundBrush(QBrush("black"))
        chart.setRenderHint(QPainter.Antialiasing)
        return chart