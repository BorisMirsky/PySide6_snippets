
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QApplication, QGroupBox, QHBoxLayout, QLineEdit,
                               QGridLayout, QLabel, QPushButton, QSpinBox, QMessageBox)
from PySide6.QtGui import QFont, QIcon, QShortcut, Qt, QPen, QPainter, QImage, QPixmap, QColor, QBrush, QIntValidator, QShortcut
from PySide6.QtCharts import QChartView, QLineSeries, QAreaSeries, QVXYModelMapper, QScatterSeries
from PySide6.QtCore import Qt, QTimer, QDateTime, QCoreApplication, QPointF, QMargins, Signal, QObject, QEvent
import sys
import json
import copy
import math
from itertools import cycle
from domain.dto.Workflow import ProgramTaskCalculationOptionsDto, ProgramTaskCalculationResultDto
from ....utils.store.workflow.zip.Dto import MeasuringTripResultDto_from_archive
from presentation.models.PicketPositionedTableModel import PicketPositionedTableModel
from domain.models.StepIndexedDataFramePositionedModel import StepIndexedDataFramePositionedModel
from presentation.ui.gui.common.viewes.TableDataChartsView import DynamicLineSeries, HorizontalChart
from domain.dto.Travelling import PicketDirection, LocationVector1D
from operating.states.program_task_calculation.ProgramTaskCalculationState import ProgramTaskCalculationOptionsState
from domain.models.AbstractPositionedTableModel import AbstractPositionedTableModel
from domain.dto.Workflow import ProgramTaskCalculationResultDto
from ....models.TranslatedHeadersTableModel import TranslatedHeadersTableModel
from .VerticalLine import VerticalLineModel, HorizontalLineModel



focus_style = "QWidget:focus { border: 3px solid #FF0000; border-radius: 5px; background-color: white}"
message_box_focus_style = "QMessageBox > QPushButton:focus { border: 3px solid #FF0000; border-radius: 5px; background-color: white}"

class DetailedRestrictionsWidget(QWidget):
    detailedRestrictionsSignal = Signal(str)
    def __init__(self,
                 options: ProgramTaskCalculationOptionsDto,
                 parent: QWidget = None):
        super().__init__(parent)
        self.__options = options
        self.__restrictions = options.restrictions
        charts_column_names_only: List[str] = ['strelograph_work', 'pendulum_work', 'pendulum_control', 'pendulum_front','sagging_left', 'sagging_right']
        self.measurements_model: AbstractPositionedTableModel = StepIndexedDataFramePositionedModel(columns = charts_column_names_only)
        self.measurements_model.reset(self.__options.measuring_trip.measurements.step,
                                 self.__options.measuring_trip.measurements.data)
        self.__picket_measurements_model = PicketPositionedTableModel(options.picket_direction,
                                                                      options.start_picket.meters, self)
        self.__picket_measurements_model.setSourceModel(self.measurements_model)
        # ==============================================
        self.position_multiplyer: int = self.__options.picket_direction.multiplier()
        self.position_range: tuple[LocationVector1D, LocationVector1D] = self.measurements_model.minmaxPosition()
        self.position_min: float = self.position_multiplyer * self.position_range[0].meters + self.__options.start_picket.meters
        self.position_max: float = self.position_multiplyer * self.position_range[1].meters + self.__options.start_picket.meters
        self.currentPosition = self.__options.start_picket.meters
        self.startPicket = self.__options.start_picket.meters
        self.counter = 0 #self.__options.start_picket.meters
        #print(self.__options.start_picket.meters)
        general_hbox = QHBoxLayout()
        general_vbox = QVBoxLayout()
        left_column = QVBoxLayout()
        #
        self.unsavedChanges: bool = False
        self.hbox1 = QHBoxLayout()
        vbox1 = QVBoxLayout()
        self.hbox1.addLayout(vbox1, 9)
        hbox2 = QHBoxLayout()
        hbox3 = QHBoxLayout()
        vbox3 = QVBoxLayout()
        hbox3.addLayout(vbox3, 9)
        hbox4 = QHBoxLayout()
        hbox5 = QHBoxLayout()
        general_vbox.addLayout(self.hbox1, 3)
        general_vbox.addLayout(hbox2, 1)
        general_vbox.addLayout(hbox3, 3)
        general_vbox.addLayout(hbox4, 1)
        general_vbox.addLayout(hbox5, 1)
        self.buttons = []
        left_column.addStretch(1)
        left_column.addWidget(self.__leftColumn())
        self.plan_btn = QPushButton("План")
        self.level_btn = QPushButton("Уровень")
        self.profile_btn = QPushButton("Просадки")
        self.speed_btn = QPushButton("Скорость")
        self.situation_btn = QPushButton("Ситуация")
        #
        self.previous_point_plan_left, self.previous_point_plan_right, self.current_point_plan_left, self.current_point_plan_right = 0, 0, 0, 0
        self.previous_point_profile_left, self.previous_point_profile_right, self.current_point_profile_left, self.current_point_profile_right = 0, 0, 0, 0
        self.previous_point_speed_pass, self.previous_point_speed_gruz, self.current_point_speed_pass, self.current_point_speed_gruz = 0, 0, 0, 0
        self.plan_points, self.profile_points, self.speed_points = [], [], []
        self.plan_segments, self.profile_segments, self.speed_segments = [], [], []
        self.plan_pool = cycle(self.plan_segments)   # закольцованная итерация
        self.profile_pool = cycle(self.profile_segments)
        self.speed_pool = cycle(self.speed_segments)
        self.previous_series_plan, self.previous_series_profile, self.previous_series_speed = QScatterSeries(), QScatterSeries(), QScatterSeries()
        self.current_series_plan, self.current_series_profile, self.current_series_speed =  QScatterSeries(), QScatterSeries(), QScatterSeries()

        self.current_chart_view = ""
        self.static_line_position = 0
        self.model = VerticalLineModel(self.currentPosition)

        ################################# CHARTS #######################################################################
        self.strelograph_chart = self.__createChart(['strelograph_work'], "Стр. план")
        self.strelograph_chart.setObjectName("strelograph_chart")
        self.chart_view_strelograph_chart = QChartView(self.strelograph_chart)
        self.chart_view_strelograph_chart.setFocusPolicy(Qt.NoFocus)
        self.chart_view_strelograph_chart.setObjectName("chart_view_strelograph_chart")
        self.chart_view_strelograph_chart.chart().setBackgroundBrush(QBrush("black"))
        self.chart_view_strelograph_chart.setRenderHint(QPainter.Antialiasing)
        vbox1.addWidget(self.chart_view_strelograph_chart, 1)
        #
        self.strelograph_empty_chart = self.__createChart([], "Сдвиги",
                                                          [self.__restrictions['segments'][0]['shifting_right'] - 5,
                                                            self.__restrictions['segments'][0]['shifting_left'] + 5])
        self.strelograph_empty_chart.setObjectName("strelograph_empty_chart")
        #
        self.strelograph_top_line_series, self.strelograph_bottom_line_series = QLineSeries(), QLineSeries()
        for i in range(0, round(self.position_range[1].meters)):   # round(self.position_max.item())):
            self.strelograph_top_line_series.append(self.startPicket + i * self.position_multiplyer, self.__restrictions['segments'][0]['shifting_left'])
            self.strelograph_bottom_line_series.append(self.startPicket + i * self.position_multiplyer, self.__restrictions['segments'][0]['shifting_right'])
        self.strelograph_top_line_series.setPen(QPen(Qt.GlobalColor.red, 1))
        self.strelograph_bottom_line_series.setPen(QPen(Qt.GlobalColor.red, 1))

        self.strelograph_empty_chart.addSeries(self.strelograph_top_line_series)
        self.strelograph_empty_chart.addSeries(self.strelograph_bottom_line_series)
        self.strelograph_top_line_series.attachAxis(self.strelograph_empty_chart.axisX())
        self.strelograph_top_line_series.attachAxis(self.strelograph_empty_chart.axisY())
        self.strelograph_bottom_line_series.attachAxis(self.strelograph_empty_chart.axisX())
        self.strelograph_bottom_line_series.attachAxis(self.strelograph_empty_chart.axisY())
        self.chart_view_strelograph_empty_chart = QChartView(self.strelograph_empty_chart)
        self.chart_view_strelograph_empty_chart.setFocusPolicy(Qt.NoFocus)
        self.chart_view_strelograph_empty_chart.setObjectName("chart_view_strelograph_empty_chart")
        self.chart_view_strelograph_empty_chart.chart().setBackgroundBrush(QBrush("black"))
        self.chart_view_strelograph_empty_chart.setRenderHint(QPainter.Antialiasing)
        vbox1.addWidget(self.chart_view_strelograph_empty_chart,1)
        #
        self.pendulum_chart = self.__createChart(['pendulum_work'], "ВНР")    # , 'pendulum_control', 'pendulum_front'
        self.pendulum_chart.setObjectName("pendulum_chart")
        self.chart_view_pendulum_chart = QChartView(self.pendulum_chart)
        self.chart_view_pendulum_chart.setFocusPolicy(Qt.NoFocus)
        self.chart_view_pendulum_chart.setObjectName("chart_view_pendulum_chart")
        self.chart_view_pendulum_chart.chart().setBackgroundBrush(QBrush("black"))
        self.chart_view_pendulum_chart.setRenderHint(QPainter.Antialiasing)
        hbox2.addWidget(self.chart_view_pendulum_chart, 9)
        self.sagging_chart = self.__createChart(['sagging_left', 'sagging_right'], "Стр. просадки")
        self.sagging_chart.setObjectName("sagging_chart")
        self.chart_view_sagging_chart = QChartView(self.sagging_chart)
        self.chart_view_sagging_chart.setFocusPolicy(Qt.NoFocus)
        self.chart_view_sagging_chart.setObjectName("chart_view_sagging_chart")
        self.chart_view_sagging_chart.chart().setBackgroundBrush(QBrush("black"))
        self.chart_view_sagging_chart.setRenderHint(QPainter.Antialiasing)
        vbox3.addWidget(self.chart_view_sagging_chart, 1)
        self.profile_empty_chart = self.__createChart([], "Подъёмки",
                                                      [self.__restrictions['segments'][0]['raising_lbound'] - 10,
                                                        self.__restrictions['segments'][0]['raising_ubound'] + 10])
        self.profile_empty_chart.setObjectName("profile_empty_chart")
        self.chart_view_profile_empty_chart = QChartView(self.profile_empty_chart)
        self.chart_view_profile_empty_chart.setFocusPolicy(Qt.NoFocus)
        self.chart_view_profile_empty_chart.setObjectName("chart_view_profile_empty_chart")
        self.chart_view_profile_empty_chart.chart().setBackgroundBrush(QBrush("black"))
        self.chart_view_profile_empty_chart.setRenderHint(QPainter.Antialiasing)
        vbox3.addWidget(self.chart_view_profile_empty_chart, 1)
        #
        self.lifting_top_line_series, self.lifting_bottom_line_series = QLineSeries(), QLineSeries()
        for i in range(0, round(self.position_range[1].meters)):
            self.lifting_top_line_series.append(self.startPicket + i * self.position_multiplyer, self.__restrictions['segments'][0]['raising_ubound'])  # restrictions[0])
            self.lifting_bottom_line_series.append(self.startPicket + i * self.position_multiplyer, self.__restrictions['segments'][0]['raising_lbound'])  # restrictions[1])
        self.lifting_top_line_series.setPen(QPen(Qt.GlobalColor.red, 1))
        self.lifting_bottom_line_series.setPen(QPen(Qt.GlobalColor.red, 1))
        self.profile_empty_chart.addSeries(self.lifting_top_line_series)
        self.profile_empty_chart.addSeries(self.lifting_bottom_line_series)
        self.lifting_top_line_series.attachAxis(self.profile_empty_chart.axisX())
        self.lifting_top_line_series.attachAxis(self.profile_empty_chart.axisY())
        self.lifting_bottom_line_series.attachAxis(self.profile_empty_chart.axisX())
        self.lifting_bottom_line_series.attachAxis(self.profile_empty_chart.axisY())
        self.speed_empty_chart = self.__createChart([], "Скорость",
                                                    [self.__restrictions['segments'][0]['v_gruz'] - 10,
                                                     self.__restrictions['segments'][0]['v_pass'] + 10])
        self.speed_empty_chart.setObjectName("speed_empty_chart")
        self.chart_view_speed_empty_chart = QChartView(self.speed_empty_chart)
        self.chart_view_speed_empty_chart.setFocusPolicy(Qt.NoFocus)
        self.chart_view_speed_empty_chart.setObjectName("chart_view_speed_empty_chart")
        self.chart_view_speed_empty_chart.chart().setBackgroundBrush(QBrush("black"))
        self.chart_view_speed_empty_chart.setRenderHint(QPainter.Antialiasing)
        hbox4.addWidget(self.chart_view_speed_empty_chart, 9)
        self.speed_series_gruz, self.speed_series_pass = QLineSeries(), QLineSeries()
        for i in range(0, round(self.position_range[1].meters)):
            self.speed_series_gruz.append(self.startPicket + i * self.position_multiplyer, self.__restrictions['segments'][0]['v_gruz'])
            self.speed_series_pass.append(self.startPicket + i * self.position_multiplyer, self.__restrictions['segments'][0]['v_pass'])
        self.speed_series_gruz.setPen(QPen(Qt.GlobalColor.red, 1))
        self.speed_series_pass.setPen(QPen(Qt.GlobalColor.red, 1))
        self.speed_empty_chart.addSeries(self.speed_series_gruz)
        self.speed_empty_chart.addSeries(self.speed_series_pass)
        self.speed_series_gruz.attachAxis(self.speed_empty_chart.axisX())
        self.speed_series_gruz.attachAxis(self.speed_empty_chart.axisY())
        self.speed_series_pass.attachAxis(self.speed_empty_chart.axisX())
        self.speed_series_pass.attachAxis(self.speed_empty_chart.axisY())

        #################################################################################
        self.situation_empty_chart = self.__createChart([], "Ситуация",[-10,10] )
        self.situation_empty_chart.setObjectName("situation_empty_chart")
        self.chart_view_situation_empty_chart = QChartView(self.situation_empty_chart)
        self.chart_view_situation_empty_chart.setFocusPolicy(Qt.NoFocus)
        self.chart_view_situation_empty_chart.setObjectName("chart_view_situation_empty_chart")
        self.chart_view_situation_empty_chart.chart().setBackgroundBrush(QBrush("black"))
        self.chart_view_situation_empty_chart.setRenderHint(QPainter.Antialiasing)
        hbox5.addWidget(self.chart_view_situation_empty_chart, 9)
        plan_widget = self.__planWidget()
        level_widget = self.__levelWidget()
        profile_widget = self.__profileWidget()
        speed_widget = self.__speedWidget()
        situation_widget = self.__situationWidget()
        self.hbox1.addWidget(plan_widget, 1)
        hbox2.addWidget(level_widget,1)
        hbox3.addWidget(profile_widget, 1)
        hbox4.addWidget(speed_widget, 1)
        hbox5.addWidget(situation_widget, 1)
        general_hbox.addLayout(left_column)
        general_hbox.addLayout(general_vbox)
        self.installEventFilter(self)
        self.setLayout(general_hbox)
        self.showMaximized()
        self.setFocus()

############################################### сегменты ######################################################
    # разбиваем полный список точек на сегменты (т.е. отрезки с началом и концом = красной полосе)
    def divide_data(self, y, data):
        counter = 0                           # счётчик базовых (от которых начинается сегмент) точек, от 0 до 2
        result = []
        for i in range (0, len(data), 1):
            if data[i][1] == y and counter == 0:
                segment = []
                segment.append(data[i])
                counter = 1
            elif data[i][1] != y and counter == 1:
                segment.append(data[i])
            elif data[i][1] == y and counter == 1:
                segment.append(data[i])
                result.append(segment)
                segment = []
                counter = 0
            i += 1
        return result

    # выделяем сегмент
    def __highlight_segment(self, current_chart_view, pool):
        current_segment_plan, current_segment_profile, current_segment_speed = [], [], []
        if current_chart_view == "plan":
            self.previous_series_plan.hide()
            try:
                current_segment_plan = next(pool)
            except StopIteration:
                pass
            self.current_series_plan = QScatterSeries()
            self.current_series_plan.setMarkerShape(QScatterSeries.MarkerShapeCircle)
            self.current_series_plan.setColor('red')
            self.current_series_plan.setMarkerSize(10.0)
            for point in current_segment_plan:
                self.current_series_plan.append(point[0], point[1])
            self.strelograph_empty_chart.addSeries(self.current_series_plan)
            self.current_series_plan.attachAxis(self.strelograph_empty_chart.axisX())
            self.current_series_plan.attachAxis(self.strelograph_empty_chart.axisY())
            self.previous_series_plan = self.current_series_plan
        elif current_chart_view == "profile":
            self.previous_series_profile.hide()
            try:
                current_segment_profile = next(pool)
            except StopIteration:
                pass
            self.current_series_profile = QScatterSeries()
            self.current_series_profile.setMarkerShape(QScatterSeries.MarkerShapeCircle)
            self.current_series_profile.setColor('red')
            self.current_series_profile.setMarkerSize(10.0)
            for point in current_segment_profile:
                self.current_series_profile.append(point[0], point[1])
            self.profile_empty_chart.addSeries(self.current_series_profile)
            self.current_series_profile.attachAxis(self.profile_empty_chart.axisX())
            self.current_series_profile.attachAxis(self.profile_empty_chart.axisY())
            self.previous_series_profile = self.current_series_profile
        elif current_chart_view == "speed":
            self.previous_series_speed.hide()
            try:
                current_segment_speed = next(pool)
            except StopIteration:
                pass
            self.current_series_speed = QScatterSeries()
            self.current_series_speed.setMarkerShape(QScatterSeries.MarkerShapeCircle)
            self.current_series_speed.setColor('red')
            self.current_series_speed.setMarkerSize(10.0)
            for point in current_segment_speed:
                self.current_series_speed.append(point[0], point[1])
            self.speed_empty_chart.addSeries(self.current_series_speed)
            self.current_series_speed.attachAxis(self.speed_empty_chart.axisX())
            self.current_series_speed.attachAxis(self.speed_empty_chart.axisY())
            self.previous_series_speed = self.current_series_speed
        self.setFocus()

    # удаляем сегмент (выравниваем линию)
    def __delete_segment(self, current_chart_view):
        if current_chart_view == "plan":
            start = int(round(self.current_series_plan.points()[0].x()))
            end = int(round(self.current_series_plan.points()[-1].x()))
            self.current_series_plan.hide()
            if int(round(self.current_series_plan.points()[0].y())) == self.__restrictions['segments'][0]['shifting_left']:
                for i in range(min(start, end), max(start, end), 1):
                    self.strelograph_top_line_series.replace(i, i, self.__restrictions['segments'][0]['shifting_left'])
            elif int(round(self.current_series_plan.points()[0].y())) == self.__restrictions['segments'][0]['shifting_right']:
                for i in range(min(start, end), max(start, end), 1):
                    self.strelograph_bottom_line_series.replace(i, i, self.__restrictions['segments'][0]['shifting_right'])
            for point in self.current_series_plan.points():
                try:
                    self.plan_points.remove([int(round(point.x())), int(round(point.y()))])
                    self.plan_segments.remove([[int(round(point.x())), int(round(point.y()))] for point in self.current_series_plan.points()])
                except ValueError:
                    pass
            del self.plan_pool
            self.plan_pool = cycle(self.plan_segments)
        elif current_chart_view == "profile":
            start = int(round(self.current_series_profile.points()[0].x()))
            end = int(round(self.current_series_profile.points()[-1].x()))
            self.current_series_profile.hide()
            if int(round(self.current_series_profile.points()[0].y())) == self.__restrictions['segments'][0]['raising_ubound']:
                for i in range(min(start, end), max(start, end), 1):
                    self.lifting_top_line_series.replace(i, i, self.__restrictions['segments'][0]['raising_ubound'])
            elif int(round(self.current_series_profile.points()[0].y())) == self.__restrictions['segments'][0]['raising_lbound']:
                for i in range(min(start, end), max(start, end), 1):
                    self.lifting_bottom_line_series.replace(i, i, self.__restrictions['segments'][0]['raising_lbound'])
            for point in self.current_series_profile.points():
                try:
                    self.profile_points.remove([int(round(point.x())), int(round(point.y()))])
                    self.profile_segments.remove([[int(round(point.x())), int(round(point.y()))] for point in
                                                  self.current_series_profile.points()])
                except ValueError:
                    pass
            del self.profile_pool
            self.profile_pool = cycle(self.profile_segments)
        elif current_chart_view == "speed":
            start = int(round(self.current_series_speed.points()[0].x()))
            end = int(round(self.current_series_speed.points()[-1].x()))
            self.current_series_speed.hide()
            if int(round(self.current_series_speed.points()[0].y())) == self.__restrictions['segments'][0]['v_gruz']:
                for i in range(min(start, end), max(start, end), 1):
                    self.speed_series_gruz.replace(i, i, self.__restrictions['segments'][0]['v_gruz'])
            elif int(round(self.current_series_speed.points()[0].y())) == self.__restrictions['segments'][0]['v_pass']:
                for i in range(min(start, end), max(start, end), 1):
                    self.speed_series_pass.replace(i, i, self.__restrictions['segments'][0]['v_pass'])
            for point in self.current_series_speed.points():
                try:
                    self.speed_points.remove([int(round(point.x())), int(round(point.y()))])
                    self.speed_segments.remove([[int(round(point.x())), int(round(point.y()))] for point in
                                                self.current_series_speed.points()])
                except ValueError:
                    pass
            del self.speed_pool
            self.speed_pool = cycle(self.speed_segments)
        self.setFocus()

    # примет (x1,y1,x2,y2), вернёт 'k' & 'b' (формула прямой 'y = kx + b')
    # Для скошенных углов. Сейчас ненужна (временно?)
    # def line_equation(self, x1, y1, x2, y2):
    #     slope = (y2 - y1) / (x2 - x1)
    #     intercept = y1 - slope * x1
    #     result = [slope, intercept]
    #     return result

    #####################################################################################################################

    def __createChart(self, column_name, title:str, restrictions_values_range:list = False):   # restrictions:list = False,
        # Графики с данными, без красных ограничительных линий
        if len(column_name) != 0:
            if len(column_name) == 1:
                chart_value_range0: (float, float) = (
                    self.__options.measuring_trip.measurements.data.loc[:, column_name[0]].min(),
                    self.__options.measuring_trip.measurements.data.loc[:, column_name[0]].max())
                chart_value_range = (
                    min(chart_value_range0[0], chart_value_range0[1], 0),
                    max(chart_value_range0[0], chart_value_range0[1], 0)
                )
                chart_value_range_length = chart_value_range[1] - chart_value_range[0]
                chart_value_min: float = chart_value_range[
                                             0] - chart_value_range_length * 0.05
                chart_value_max: float = chart_value_range[
                                             1] + chart_value_range_length * 0.05
                self.series0 = DynamicLineSeries(self.__picket_measurements_model, 0,
                                                     self.measurements_model.modelColumnIndexAtName(column_name[0]),
                                                     QCoreApplication.translate(
                                                         'Lining trip/process/view/charts/program task', column_name[0]))
                chart = HorizontalChart((self.position_min, self.position_max),
                                        self.__options.picket_direction == PicketDirection.Backward,
                                        (chart_value_min, chart_value_max), False,
                                        series0=[self.series0],
                                        x_tick=100, y_tick=10,
                                        title=title,
                                        xMinorTickCount=9,
                                        xGridLineColor="gray", yGridLineColor="gray",
                                        xMinorGridLineColor="gray", yMinorGridLineColor="gray")
            elif len(column_name) == 2:
                chart_value_range0: (float, float) = (
                    self.__options.measuring_trip.measurements.data.loc[:, column_name[0]].min(),
                    self.__options.measuring_trip.measurements.data.loc[:, column_name[0]].max())
                chart_value_range1: (float, float) = (
                    self.__options.measuring_trip.measurements.data.loc[:, column_name[1]].min(),
                    self.__options.measuring_trip.measurements.data.loc[:, column_name[1]].max())
                chart_value_range = (
                    min(chart_value_range0[0], chart_value_range0[1], chart_value_range1[0], chart_value_range1[1], 0),
                    max(chart_value_range0[0], chart_value_range0[1], chart_value_range1[0], chart_value_range1[1], 0)
                )
                chart_value_range_length = chart_value_range[1] - chart_value_range[0]
                chart_value_min: float = chart_value_range[
                                             0] - chart_value_range_length * 0.05  # 0.00001 - 0.05 * chart_value_range_length
                chart_value_max: float = chart_value_range[
                                             1] + chart_value_range_length * 0.05  # 1.00001 + 0.05 * chart_value_range_length
                self.series0 = DynamicLineSeries(self.__picket_measurements_model, 0,
                                                 self.measurements_model.modelColumnIndexAtName(column_name[0]),
                                                 QCoreApplication.translate(
                                                     'Lining trip/process/view/charts/program task', column_name[0]))
                self.series1 = DynamicLineSeries(self.__picket_measurements_model, 0,
                                                 self.measurements_model.modelColumnIndexAtName(column_name[1]),
                                                 QCoreApplication.translate(
                                                     'Lining trip/process/view/charts/program task', column_name[1]))
                chart = HorizontalChart((self.position_min, self.position_max),
                                        self.__options.picket_direction == PicketDirection.Backward,
                                        (chart_value_min, chart_value_max), False,
                                        series0=[self.series0], series1=[self.series1],
                                        x_tick=100, y_tick=10,
                                        title=title,
                                        xMinorTickCount=9,
                                        xGridLineColor="gray", yGridLineColor="gray",
                                        xMinorGridLineColor="gray", yMinorGridLineColor="gray")
            elif len(column_name) == 3:
                chart_value_range0: (float, float) = (
                    self.__options.measuring_trip.measurements.data.loc[:, column_name[0]].min(),
                    self.__options.measuring_trip.measurements.data.loc[:, column_name[0]].max())
                chart_value_range1: (float, float) = (
                    self.__options.measuring_trip.measurements.data.loc[:, column_name[1]].min(),
                    self.__options.measuring_trip.measurements.data.loc[:, column_name[1]].max())
                chart_value_range2: (float, float) = (
                    self.__options.measuring_trip.measurements.data.loc[:, column_name[2]].min(),
                    self.__options.measuring_trip.measurements.data.loc[:, column_name[2]].max())
                chart_value_range = (
                    min(chart_value_range0[0], chart_value_range0[1], chart_value_range1[0], chart_value_range1[1],
                        chart_value_range2[0], chart_value_range2[1], 0),
                    max(chart_value_range0[0], chart_value_range0[1], chart_value_range1[0], chart_value_range1[1],
                        chart_value_range2[0], chart_value_range2[1], 0))
                chart_value_range_length = chart_value_range[1] - chart_value_range[0]
                chart_value_min: float = chart_value_range[
                                             0] - chart_value_range_length * 0.05  # 0.00001 - 0.05 * chart_value_range_length
                chart_value_max: float = chart_value_range[
                                             1] + chart_value_range_length * 0.05  # 1.00001 + 0.05 * chart_value_range_length
                self.series0 = DynamicLineSeries(self.__picket_measurements_model, 0,
                                                 self.measurements_model.modelColumnIndexAtName(column_name[0]),
                                                 QCoreApplication.translate(
                                                     'Lining trip/process/view/charts/program task', column_name[0]))
                self.series1 = DynamicLineSeries(self.__picket_measurements_model, 0,
                                                 self.measurements_model.modelColumnIndexAtName(column_name[1]),
                                                 QCoreApplication.translate(
                                                     'Lining trip/process/view/charts/program task', column_name[1]))
                self.series2 = DynamicLineSeries(self.__picket_measurements_model, 0,
                                                 self.measurements_model.modelColumnIndexAtName(column_name[2]),
                                                 QCoreApplication.translate(
                                                     'Lining trip/process/view/charts/program task', column_name[2]))
                chart = HorizontalChart((self.position_min, self.position_max),
                                        self.__options.picket_direction == PicketDirection.Backward,
                                        (chart_value_min, chart_value_max), False,
                                        series0=[self.series0], series1=[self.series1], series2=[self.series2],
                                        x_tick=100, y_tick=10,
                                        title=title,
                                        xMinorTickCount=9,
                                        xGridLineColor="gray", yGridLineColor="gray",
                                        xMinorGridLineColor="gray", yMinorGridLineColor="gray")
        # графики только с красными ограничительными линиями
        else:
            chart = HorizontalChart((self.position_min, self.position_max),
                                    self.__options.picket_direction == PicketDirection.Backward,
                                    (restrictions_values_range[0], restrictions_values_range[1]), False,
                                    x_tick=100, y_tick=10,
                                    title=title,
                                    xMinorTickCount=9,
                                    xGridLineColor="gray", yGridLineColor="gray",
                                    xMinorGridLineColor="gray", yMinorGridLineColor="gray")

        # вертикальная черта, одинаковая (общая) для всех
        vertical_line_series = QLineSeries()
        vertical_line_series.setPen(QPen(Qt.GlobalColor.magenta, 2))
        lineMapper = QVXYModelMapper(self)
        lineMapper.setXColumn(0)
        lineMapper.setYColumn(1)
        lineMapper.setSeries(vertical_line_series)
        lineMapper.setModel(self.model)

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
        return chart

    def eventFilter(self, watched: QObject, event: QEvent):
        if event.type() == QEvent.Type.Show:
            self.setFocus()
        if event.type() == QEvent.Type.KeyPress:
            self.setFocus()
            if event.key() == Qt.Key.Key_Left:
                self.model.shiftLine(self.position_multiplyer * -1)
                self.__returnData(-1)
                self.counter -= 1
                #return True
            elif event.key() == Qt.Key.Key_Right:
                self.model.shiftLine(self.position_multiplyer)
                self.__returnData(1)
                self.counter += 1
                #return True
            elif event.key() == Qt.Key.Key_D:
                self.static_vertical_model = VerticalLineModel
                self.lineMapper_for_static_line.setModel(self.static_vertical_model(self.currentPosition))
                self.static_line_position = self.counter
                if self.current_chart_view == "plan":
                    self.vertical_static_line_series_profile.hide()
                    self.vertical_static_line_series_speed.hide()
                    self.vertical_static_line_series_plan.show()
                    self.lineMapper_for_static_line.setSeries(self.vertical_static_line_series_plan)
                elif self.current_chart_view == "profile":
                    self.vertical_static_line_series_plan.hide()
                    self.vertical_static_line_series_speed.hide()
                    self.vertical_static_line_series_profile.show()
                    self.lineMapper_for_static_line.setSeries(self.vertical_static_line_series_profile)
                elif self.current_chart_view == "speed":
                    self.vertical_static_line_series_profile.hide()
                    self.vertical_static_line_series_plan.hide()
                    self.vertical_static_line_series_speed.show()
                    self.lineMapper_for_static_line.setSeries(self.vertical_static_line_series_speed)
                #return True
            elif event.key() == Qt.Key.Key_Backspace:
                if self.current_chart_view == "plan":
                    self.__highlight_segment("plan", self.plan_pool)
                elif self.current_chart_view == "profile":
                    self.__highlight_segment("profile", self.profile_pool)
                elif self.current_chart_view == "speed":
                    self.__highlight_segment("speed", self.speed_pool)
                #return True
            elif event.key() == Qt.Key.Key_Delete:
                if self.current_chart_view == "plan":
                    self.__delete_segment("plan")
                elif self.current_chart_view == "profile":
                    self.__delete_segment("profile")
                elif self.current_chart_view == "speed":
                    self.__delete_segment("speed")
                #return True
            elif event.key() == Qt.Key.Key_F2:
                self.__openReference()
                #return True                                      # ?
            elif event.key() == Qt.Key.Key_F3:
                self.__saveResult()
                #return True                                     # ?
            elif event.key() == Qt.Key.Key_F4:
                self.__quitView()
                #return True                                          # ?
            #elif event.key() == Qt.Key.Key_Tab: pass
            elif event.key() == Qt.Key.Key_Escape:
                self.__back_to_common_state()
                #return True                                        # ?
        return False

    # вернуться в стартовоe общее состояние
    def __back_to_common_state(self):
        for btn in self.buttons:
            btn.setStyleSheet(focus_style)
        self.chart_view_strelograph_empty_chart.setStyleSheet("")
        self.chart_view_profile_empty_chart.setStyleSheet("")
        self.chart_view_speed_empty_chart.setStyleSheet("")
        self.chart_view_situation_empty_chart.setStyleSheet("")
        #
        self.plan_btn.setFocusPolicy(Qt.StrongFocus)
        self.profile_btn.setFocusPolicy(Qt.StrongFocus)
        self.speed_btn.setFocusPolicy(Qt.StrongFocus)
        self.situation_btn.setFocusPolicy(Qt.StrongFocus)
        self.level_btn.setFocusPolicy(Qt.StrongFocus)
        #
        self.shifts_right_value.setFocusPolicy(Qt.NoFocus)
        self.shifts_left_value.setFocusPolicy(Qt.NoFocus)
        self.lifting_right_value.setFocusPolicy(Qt.NoFocus)
        self.lifting_left_value.setFocusPolicy(Qt.NoFocus)
        self.speed_pass_value.setFocusPolicy(Qt.NoFocus)
        self.speed_gruz_value.setFocusPolicy(Qt.NoFocus)
        #
        self.shifts_right_value.clear()
        self.shifts_left_value.clear()
        self.lifting_right_value.clear()
        self.lifting_left_value.clear()
        self.speed_pass_value.clear()
        self.speed_gruz_value.clear()
        self.setFocus()



    #####################################################################################################################
    def __leftColumn(self):
        vbox_btn = QVBoxLayout()
        widget_btn = QWidget()
        widget_btn.setLayout(vbox_btn)
        widget_btn.setContentsMargins(10,50,10,10)
        widget_btn.setProperty("sensorWidgetBox", True)
        current_position_lbl = QLabel("Текущее\n положение")
        self.current_position_value = QLabel("---")
        self.current_position_value.setObjectName("sensorsValue")
        self.current_position_value.setMaximumHeight(40)
        self.reference_btn = QPushButton("Справка F2")
        self.reference_btn.setFocusPolicy(Qt.NoFocus)
        self.buttons.append(self.reference_btn)
        self.reference_btn.clicked.connect(self.__openReference)
        self.reference_btn.setObjectName("reference_btn")
        self.save_btn = QPushButton("Сохранить F3")
        self.save_btn.setFocusPolicy(Qt.NoFocus)
        self.buttons.append(self.save_btn)
        self.save_btn.clicked.connect(self.__saveResult)
        self.save_btn.setObjectName("save_btn")
        self.exit_btn = QPushButton("Выйти F4")
        self.exit_btn.setFocusPolicy(Qt.NoFocus)
        self.buttons.append(self.exit_btn)
        self.exit_btn.setObjectName("exit_btn")
        self.exit_btn.clicked.connect(self.__quitView)
        #self.save_btn.setStyleSheet(focus_style)
        #self.exit_btn.setStyleSheet(focus_style)
        #self.reference_btn.setStyleSheet(focus_style)
        vbox_btn.addStretch(1)
        vbox_btn.addWidget(current_position_lbl)
        vbox_btn.addWidget(self.current_position_value)
        vbox_btn.addWidget(self.reference_btn)
        vbox_btn.addWidget(self.save_btn)
        vbox_btn.addWidget(self.exit_btn)
        return widget_btn

    def __returnData(self, i: int):
        self.currentPosition += self.position_multiplyer * i
        #new_index = math.fabs(int( (self.currentPosition - self.startPicket) * self.position_multiplyer / 0.185 ))
        new_index = self.__picket_measurements_model.getIndexByPicket(self.currentPosition)    # getStepByPicket
        try:
            self.plan_restriction_top.setNum(self.strelograph_top_line_series.points()[round(self.currentPosition)].toTuple()[1])
            self.plan_restriction_bottom.setNum(self.strelograph_bottom_line_series.points()[round(self.currentPosition)].toTuple()[1])
            self.profile_restriction_top.setNum(self.lifting_top_line_series.points()[round(self.currentPosition)].toTuple()[1])
            self.profile_restriction_bottom.setNum(self.lifting_bottom_line_series.points()[round(self.currentPosition)].toTuple()[1])
            self.speed_restriction_gruz.setNum(self.speed_series_gruz.points()[round(self.currentPosition)].toTuple()[1])
            self.speed_restriction_pass.setNum(self.speed_series_pass.points()[round(self.currentPosition)].toTuple()[1])
            self.plan_fact_lbl.setNum(
                round(self.__options.measuring_trip.measurements.data.loc[:,'strelograph_work'].tolist()[new_index], 1))
            self.lbl_profile_value1.setNum(
                round(self.__options.measuring_trip.measurements.data.loc[:,'sagging_left'].tolist()[new_index], 1))
            self.lbl_profile_value2.setNum(
                round(self.__options.measuring_trip.measurements.data.loc[:,'sagging_right'].tolist()[new_index], 1))
            self.level_lbl_value1.setNum(
                round(self.__options.measuring_trip.measurements.data.loc[:, 'pendulum_work'].tolist()[new_index],1))
            # self.level_lbl_value2.setNum(
            #     round(self.__options.measuring_trip.measurements.data.loc[:, 'pendulum_control'].tolist()[new_index],1))
            # self.level_lbl_value3.setNum(
            #     round(self.__options.measuring_trip.measurements.data.loc[:, 'pendulum_front'].tolist()[new_index],1))
            self.current_position_value.setNum(self.currentPosition)
        except (TypeError, IndexError):
            pass

    ##########################    Plan   ###########################################
    def __planWidget(self):
        vbox = QVBoxLayout()
        widget = QWidget()
        widget.setLayout(vbox)
        widget.setProperty("sensorWidgetBox", True)
        self.buttons.append(self.plan_btn)
        self.plan_btn.setObjectName("plan_btn")
        self.plan_btn.setStyleSheet(focus_style)
        self.plan_btn.clicked.connect(self.__handle_plan_btn)
        self.plan_fact_lbl = QLabel("---")
        self.plan_fact_lbl.setObjectName("sensorsValue")
        self.plan_fact_lbl.setMaximumHeight(20)
        #
        self.plan_restriction_top = QLabel("---")
        self.plan_restriction_top.setObjectName("sensorsValue")
        self.plan_restriction_top.setMaximumHeight(20)
        self.plan_restriction_bottom = QLabel("---")
        self.plan_restriction_bottom.setObjectName("sensorsValue")
        self.plan_restriction_bottom.setMaximumHeight(20)
        #
        self.plan_shifts_widget = QWidget()
        plan_shifts_vbox = QVBoxLayout()
        self.plan_shifts_widget.setLayout(plan_shifts_vbox)
        shifts_right_hbox = QHBoxLayout()
        shifts_left_hbox = QHBoxLayout()
        #
        #plan_range_min = self.__restrictions['segments'][0]['shifting_right']  # -50
        #plan_range_max = self.__restrictions['segments'][0]['shifting_left']  #  50
        #plan_range = plan_range_max - plan_range_min
        #
        shifts_right_lbl = QLabel("Право(-)")                          # "shifting_right": -50
        self.shifts_right_value = QLineEdit()
        self.shifts_right_value.setFocusPolicy(Qt.NoFocus)
        self.shifts_right_value.setStyleSheet(focus_style)
        self.shifts_right_value.setFont(QFont('Arial', 12))
        self.shifts_right_value.setValidator(QIntValidator(self.__restrictions['segments'][0]['shifting_right'] + 1,
                                                           self.__restrictions['segments'][0]['shifting_left'] - 1, self))
            #plan_range_min + plan_range * 0.05, plan_range_max - plan_range * 0.05, self))
        #self.shifts_right_value.returnPressed.connect(lambda: self.__handleLineEditRightPlan(self.shifts_right_value.text()))
        self.shifts_right_value.returnPressed.connect(self.__handleLineEditRightPlan)
        self.shifts_right_value.setObjectName("sensorsValue")
        #
        shifts_left_lbl = QLabel("Лево(+)")                     # "shifting_left": 50,
        self.shifts_left_value = QLineEdit()
        self.shifts_left_value.setFocusPolicy(Qt.NoFocus)
        self.shifts_left_value.setStyleSheet(focus_style)
        self.shifts_left_value.setFont(QFont('Arial', 12))
        self.shifts_left_value.setValidator(QIntValidator(self.__restrictions['segments'][0]['shifting_right'] + 1,
                                                           self.__restrictions['segments'][0]['shifting_left'] - 1, self))
        #self.shifts_left_value.returnPressed.connect(lambda: self.__handleLineEditLeftPlan(self.shifts_left_value.text()))
        self.shifts_left_value.returnPressed.connect(self.__handleLineEditLeftPlan)  # каждое нажатие
        self.shifts_left_value.setObjectName("sensorsValue")
        #
        shifts_right_hbox.addWidget(shifts_right_lbl, 1)
        shifts_right_hbox.addWidget(self.shifts_right_value)
        shifts_left_hbox.addWidget(shifts_left_lbl, 1)
        shifts_left_hbox.addWidget(self.shifts_left_value, 1)
        plan_shifts_vbox.addWidget(self.plan_btn, 1)
        plan_shifts_vbox.addStretch(1)
        plan_shifts_vbox.addWidget(self.plan_fact_lbl)
        plan_shifts_vbox.addStretch(3)
        plan_shifts_vbox.addWidget(self.plan_restriction_top)
        plan_shifts_vbox.addLayout(shifts_left_hbox)
        plan_shifts_vbox.addLayout(shifts_right_hbox)
        plan_shifts_vbox.addWidget(self.plan_restriction_bottom)
        vbox.addWidget(self.plan_shifts_widget)
        return widget

    def __handle_plan_btn(self):
        # =============== окраска кнопок ===========================
        sender = self.sender()
        for btn in self.buttons:
            if btn is sender:
                btn.setStyleSheet("background-color: blue")
            else:
                btn.setStyleSheet(focus_style)
        # ==========================================================
        self.chart_view_strelograph_empty_chart.setStyleSheet("border:13px solid blue;border-left: none;border-top: none;border-bottom: none;")
        self.chart_view_profile_empty_chart.setStyleSheet("")
        self.chart_view_speed_empty_chart.setStyleSheet("")
        self.chart_view_situation_empty_chart.setStyleSheet("")
        self.chart_view_sagging_chart.setStyleSheet("")
        self.current_chart_view = "plan"
        self.chart_view_strelograph_empty_chart.chart().addSeries(self.vertical_static_line_series_plan)
        self.vertical_static_line_series_plan.attachAxis(self.chart_view_strelograph_empty_chart.chart().axisX())
        self.vertical_static_line_series_plan.attachAxis(self.chart_view_strelograph_empty_chart.chart().axisY())
        #
        self.level_btn.setFocusPolicy(Qt.NoFocus)
        self.profile_btn.setFocusPolicy(Qt.NoFocus)
        self.speed_btn.setFocusPolicy(Qt.NoFocus)
        self.situation_btn.setFocusPolicy(Qt.NoFocus)
        self.plan_btn.setFocusPolicy(Qt.NoFocus)
        #
        self.shifts_right_value.setFocusPolicy(Qt.StrongFocus)
        self.shifts_left_value.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

    # 50 верхняя
    def __handleLineEditLeftPlan(self):
        if self.current_chart_view == "plan":
            new_y = int(self.shifts_left_value.text())
            for i in range(min(int(self.startPicket + self.position_multiplyer * self.static_line_position), int(self.currentPosition)),
                  max(int(self.startPicket + self.position_multiplyer * self.static_line_position), int(self.currentPosition)), 1):
                self.strelograph_top_line_series.replace(i, i, new_y)
                print(i, new_y)
            self.plan_points.append([min(self.__options.start_picket.meters + self.static_line_position, self.currentPosition),
                                     self.__restrictions['segments'][0]['shifting_left'] ])
            self.plan_points.append([min(self.__options.start_picket.meters + self.static_line_position, self.currentPosition), new_y])
            self.plan_points.append([max(self.__options.start_picket.meters + self.static_line_position, self.currentPosition), new_y])
            self.plan_points.append([max(self.__options.start_picket.meters + self.static_line_position, self.currentPosition),
                                     self.__restrictions['segments'][0]['shifting_left'] ])
            plan_left_segments = self.divide_data(self.__restrictions['segments'][0]['shifting_left'], self.plan_points)
            self.plan_segments.append(plan_left_segments[-1])
            self.plan_pool = cycle(self.plan_segments)
            if not self.unsavedChanges:
                self.unsavedChanges = True
            # else:
            #     self.__rangeError(self.__restrictions['segments'][0]['shifting_right'],
            #                       self.__restrictions['segments'][0]['shifting_left'])
            self.shifts_left_value.clear()
            self.setFocus()

    # -50 нижняя
    def __handleLineEditRightPlan(self):
        if self.current_chart_view == "plan":
            new_y = int(self.shifts_right_value.text())
            for i in range(min(int(self.__options.start_picket.meters + self.static_line_position), int(self.currentPosition)),
                max(int(self.__options.start_picket.meters + self.static_line_position), int(self.currentPosition)), 1):
                    self.strelograph_bottom_line_series.replace(i, i, new_y)
            self.plan_points.append([min(self.__options.start_picket.meters + self.static_line_position, self.currentPosition), self.__restrictions['segments'][0]['shifting_right'] ])
            self.plan_points.append([min(self.__options.start_picket.meters + self.static_line_position, self.currentPosition), new_y])
            self.plan_points.append([max(self.__options.start_picket.meters + self.static_line_position, self.currentPosition), new_y])
            self.plan_points.append([max(self.__options.start_picket.meters + self.static_line_position, self.currentPosition), self.__restrictions['segments'][0]['shifting_right'] ])
            plan_right_segments = self.divide_data(self.__restrictions['segments'][0]['shifting_right'], self.plan_points)
            self.plan_segments.append(plan_right_segments[-1])
            self.plan_pool = cycle(self.plan_segments)
            if not self.unsavedChanges:
                self.unsavedChanges = True
            # else:
            #     self.__rangeError(self.__restrictions['segments'][0]['shifting_right'],
            #                       self.__restrictions['segments'][0]['shifting_left'])
            self.shifts_right_value.clear()
            self.setFocus()

    ###########################   Level   ##########################################

    def __levelWidget(self):
        vbox = QVBoxLayout()
        widget = QWidget()
        widget.setProperty("sensorWidgetBox", True)
        widget.setLayout(vbox)
        #self.level_btn = QPushButton("Уровень")
        self.buttons.append(self.level_btn)
        self.level_btn.setStyleSheet(focus_style)
        self.level_btn.clicked.connect(self.__handle_level_btn)
        self.level_lbl_value1 = QLabel("---")
        #self.level_lbl_value2 = QLabel("---")
        #self.level_lbl_value3 = QLabel("---")
        self.level_lbl_value1.setObjectName("sensorsValue")
        #self.level_lbl_value2.setObjectName("sensorsValue")
        #self.level_lbl_value3.setObjectName("sensorsValue")
        # hbox_values = QHBoxLayout()
        # hbox_values.addWidget(self.level_lbl_value1)
        # hbox_values.addWidget(self.level_lbl_value2)
        # hbox_values.addWidget(self.level_lbl_value3)
        vbox_values = QVBoxLayout()
        vbox_values.addWidget(QLabel("Маятник рабочий"))
        vbox_values.addWidget(self.level_lbl_value1)
        #vbox_values.addWidget(self.level_lbl_value2)
        #vbox_values.addWidget(self.level_lbl_value3)
        vbox.addWidget(self.level_btn)
        vbox.addLayout(vbox_values)
        return widget

    def __handle_level_btn(self):
        sender = self.sender()
        for btn in self.buttons:
            if btn is sender:
                btn.setStyleSheet("background-color: blue")
            else:
                btn.setStyleSheet(focus_style)
        self.chart_view_strelograph_empty_chart.setStyleSheet("")
        self.chart_view_profile_empty_chart.setStyleSheet("")
        self.chart_view_speed_empty_chart.setStyleSheet("")
        self.chart_view_situation_empty_chart.setStyleSheet("")
        #
        self.plan_btn.setFocusPolicy(Qt.NoFocus)
        self.profile_btn.setFocusPolicy(Qt.NoFocus)
        self.speed_btn.setFocusPolicy(Qt.NoFocus)
        self.situation_btn.setFocusPolicy(Qt.NoFocus)
        #
        self.level_btn.setFocusPolicy(Qt.NoFocus)
        self.lifting_right_value.setFocusPolicy(Qt.NoFocus)
        self.lifting_left_value.setFocusPolicy(Qt.NoFocus)
        self.shifts_right_value.setFocusPolicy(Qt.NoFocus)
        self.shifts_left_value.setFocusPolicy(Qt.NoFocus)
        self.setFocus()

    ####################################    Profile   #################################
    def __profileWidget(self):
        vbox = QVBoxLayout()
        widget = QWidget()
        widget.setProperty("sensorWidgetBox", True)
        widget.setLayout(vbox)
        self.buttons.append(self.profile_btn)
        self.profile_btn.setStyleSheet(focus_style)
        self.profile_btn.clicked.connect(self.__handle_profile_btn)
        self.profile_restriction_top = QLabel("---")
        self.profile_restriction_top.setObjectName("sensorsValue")
        self.profile_restriction_top.setMaximumHeight(20)
        self.profile_restriction_bottom = QLabel("---")
        self.profile_restriction_bottom.setObjectName("sensorsValue")
        self.profile_restriction_bottom.setMaximumHeight(20)
        self.lbl_profile_value1 = QLabel("---")
        self.lbl_profile_value2 = QLabel("---")
        self.lbl_profile_value1.setMaximumHeight(20)
        self.lbl_profile_value2.setMaximumHeight(20)
        self.lbl_profile_value1.setObjectName("sensorsValue")
        self.lbl_profile_value2.setObjectName("sensorsValue")
        lifting_right_hbox = QHBoxLayout()
        lifting_left_hbox = QHBoxLayout()
        lifting_right_lbl = QLabel("Правая")
        self.lifting_right_value = QLineEdit()
        self.lifting_right_value.setFocusPolicy(Qt.NoFocus)
        self.lifting_right_value.setStyleSheet(focus_style)
        self.lifting_right_value.setFont(QFont('Arial', 12))
        self.lifting_right_value.setValidator(QIntValidator(self.__restrictions['segments'][0]['raising_lbound'] + 1,
                                                            self.__restrictions['segments'][0]['raising_ubound'] - 1, self))
            #profile_range_min + profile_range * 0.05,profile_range_max - profile_range * 0.05, self))
        self.lifting_right_value.returnPressed.connect(self.__handleLineEditLiftingRight)  # каждое нажатие
        lifting_left_lbl = QLabel("Левая")
        self.lifting_left_value = QLineEdit()
        self.lifting_left_value.setFocusPolicy(Qt.NoFocus)
        self.lifting_left_value.setStyleSheet(focus_style)
        self.lifting_left_value.setFont(QFont('Arial', 12))
        self.lifting_left_value.setValidator(QIntValidator(self.__restrictions['segments'][0]['raising_lbound'] + 1,
                                                            self.__restrictions['segments'][0]['raising_ubound'] - 1, self))
            #profile_range_min + profile_range * 0.05, profile_range_max - profile_range * 0.05, self))
        self.lifting_left_value.returnPressed.connect(self.__handleLineEditLiftingLeft)  # каждое нажатие
        self.lifting_right_value.setObjectName("sensorsValue")
        self.lifting_left_value.setObjectName("sensorsValue")
        lifting_right_hbox.addWidget(lifting_right_lbl, 1)
        lifting_right_hbox.addWidget(self.lifting_right_value, 1)
        lifting_left_hbox.addWidget(lifting_left_lbl, 1)
        lifting_left_hbox.addWidget(self.lifting_left_value, 1)
        vbox_values = QVBoxLayout()
        vbox_values.addWidget(QLabel("Левая"))
        vbox_values.addWidget(self.lbl_profile_value1)
        vbox_values.addWidget(self.lbl_profile_value2)
        vbox_values.addWidget(QLabel("Правая"))
        vbox.addWidget(self.profile_btn)
        vbox.addStretch(1)
        vbox.addLayout(vbox_values)
        vbox.addStretch(1)
        vbox.addWidget(self.profile_restriction_top)
        vbox.addLayout(lifting_right_hbox)
        vbox.addLayout(lifting_left_hbox)
        vbox.addWidget(self.profile_restriction_bottom)
        return widget

    def __handle_profile_btn(self):
        sender = self.sender()
        for btn in self.buttons:
            if btn is sender:
                btn.setStyleSheet("background-color: blue")
            else:
                btn.setStyleSheet(focus_style)
        self.chart_view_strelograph_empty_chart.setStyleSheet("")
        self.chart_view_profile_empty_chart.setStyleSheet("border:13px solid blue; border-left: none; border-top: none; border-bottom: none;")
        self.chart_view_speed_empty_chart.setStyleSheet("")
        self.chart_view_situation_empty_chart.setStyleSheet("")
        self.chart_view_sagging_chart.setStyleSheet("")
        self.current_chart_view = "profile"
        #
        self.chart_view_profile_empty_chart.chart().addSeries(self.vertical_static_line_series_profile)
        self.vertical_static_line_series_profile.attachAxis(self.chart_view_profile_empty_chart.chart().axisX())
        self.vertical_static_line_series_profile.attachAxis(self.chart_view_profile_empty_chart.chart().axisY())
        #
        self.level_btn.setFocusPolicy(Qt.NoFocus)
        self.profile_btn.setFocusPolicy(Qt.NoFocus)
        self.speed_btn.setFocusPolicy(Qt.NoFocus)
        self.situation_btn.setFocusPolicy(Qt.NoFocus)
        self.plan_btn.setFocusPolicy(Qt.NoFocus)
        #
        self.lifting_right_value.setFocusPolicy(Qt.StrongFocus)
        self.lifting_left_value.setFocusPolicy(Qt.StrongFocus)
        self.shifts_right_value.setFocusPolicy(Qt.NoFocus)
        self.shifts_left_value.setFocusPolicy(Qt.NoFocus)
        self.speed_pass_value.setFocusPolicy(Qt.NoFocus)
        self.speed_gruz_value.setFocusPolicy(Qt.NoFocus)
        self.setFocus()

    def __handleLineEditLiftingRight(self):
        if self.current_chart_view == "profile":
            new_y = int(self.lifting_right_value.text())
            for i in range( min(int(self.__options.start_picket.meters + self.static_line_position), int(self.currentPosition)),
                    max(int(self.__options.start_picket.meters + self.static_line_position), int(self.currentPosition)), 1):
                self.lifting_top_line_series.replace(i, i, new_y)
            self.profile_points.append([min(self.__options.start_picket.meters + self.static_line_position, self.currentPosition),
                 self.__restrictions['segments'][0]['raising_ubound']])
            self.profile_points.append([min(self.__options.start_picket.meters + self.static_line_position, self.currentPosition), new_y])
            self.profile_points.append([max(self.__options.start_picket.meters + self.static_line_position, self.currentPosition), new_y])
            self.profile_points.append([max(self.__options.start_picket.meters + self.static_line_position, self.currentPosition),
                 self.__restrictions['segments'][0]['raising_ubound']])
            profile_right_segments = self.divide_data(self.__restrictions['segments'][0]['raising_ubound'], self.profile_points)
            self.profile_segments.append(profile_right_segments[-1])
            self.profile_pool = cycle(self.profile_segments)
            if not self.unsavedChanges:
                self.unsavedChanges = True
            self.lifting_right_value.clear()
            self.setFocus()

    def __handleLineEditLiftingLeft(self):
        if self.current_chart_view == "profile":
            new_y = int(self.lifting_left_value.text())
            for i in range(
                        min(int(self.__options.start_picket.meters + self.static_line_position), int(self.currentPosition)),
                        max(int(self.__options.start_picket.meters + self.static_line_position), int(self.currentPosition)),
                        1):
                self.lifting_bottom_line_series.replace(i, i, new_y)
            self.profile_points.append(
                [min(self.__options.start_picket.meters + self.static_line_position, self.currentPosition),
                 self.__restrictions['segments'][0]['raising_lbound']])
            self.profile_points.append(
                   [min(self.__options.start_picket.meters + self.static_line_position, self.currentPosition), new_y])
            self.profile_points.append(
                    [max(self.__options.start_picket.meters + self.static_line_position, self.currentPosition), new_y])
            self.profile_points.append(
                    [max(self.__options.start_picket.meters + self.static_line_position, self.currentPosition),
                 self.__restrictions['segments'][0]['raising_lbound']])
            profile_right_segments = self.divide_data(self.__restrictions['segments'][0]['raising_lbound'],
                                                          self.profile_points)
            self.profile_segments.append(profile_right_segments[-1])
            self.profile_pool = cycle(self.profile_segments)
            if not self.unsavedChanges:
                    self.unsavedChanges = True
            self.lifting_left_value.clear()
            self.setFocus()

    ####################################    Speed   #################################
    def __speedWidget(self):
        vbox = QVBoxLayout()
        widget = QWidget()
        widget.setProperty("sensorWidgetBox", True)
        widget.setLayout(vbox)
        #self.speed_btn = QPushButton("Скорость")
        self.buttons.append(self.speed_btn)
        self.speed_btn.setStyleSheet(focus_style)
        self.speed_btn.clicked.connect(self.__handle_speed_btn)
        lbl_gruz = QLabel("Груз.")
        lbl_pass = QLabel("Пасс.")
        self.speed_pass_value = QLineEdit()                      #speed_gruz_value
        self.speed_pass_value.setFocusPolicy(Qt.NoFocus)
        self.speed_pass_value.setStyleSheet(focus_style)
        self.speed_pass_value.setFont(QFont('Arial', 12))
        self.speed_pass_value.setValidator(QIntValidator(0, 999, self))
        #self.speed_pass_value.returnPressed.connect(lambda: self.__handleLineEditSpeedPass(self.speed_pass_value.text()))
        self.speed_pass_value.returnPressed.connect(self.__handleLineEditSpeedPass)
        self.speed_gruz_value = QLineEdit()
        self.speed_gruz_value.setFocusPolicy(Qt.NoFocus)
        self.speed_gruz_value.setStyleSheet(focus_style)
        self.speed_gruz_value.setFont(QFont('Arial', 12))
        self.speed_gruz_value.setValidator(QIntValidator(0, 999, self))
        #self.speed_gruz_value.returnPressed.connect(self.__handleLineEditSpeedGruz)  # каждое нажатие
        #self.speed_gruz_value.returnPressed.connect(lambda: self.__handleLineEditSpeedGruz(self.speed_gruz_value.text()))
        self.speed_gruz_value.returnPressed.connect(self.__handleLineEditSpeedGruz)
        self.speed_restriction_pass = QLabel("---")
        self.speed_restriction_pass.setObjectName("sensorsValue")
        self.speed_restriction_pass.setMaximumHeight(20)
        self.speed_restriction_gruz = QLabel("---")
        self.speed_restriction_gruz.setObjectName("sensorsValue")
        self.speed_restriction_gruz.setMaximumHeight(20)
        hbox_speed_gruz = QHBoxLayout()
        hbox_speed_pass = QHBoxLayout()
        hbox_speed_pass.addWidget(lbl_pass, 1)
        hbox_speed_pass.addWidget(self.speed_pass_value, 1)
        hbox_speed_pass.addWidget(self.speed_restriction_pass, 1)
        hbox_speed_gruz.addWidget(lbl_gruz, 1)
        hbox_speed_gruz.addWidget(self.speed_gruz_value, 1)
        hbox_speed_gruz.addWidget(self.speed_restriction_gruz, 1)
        vbox.addWidget(self.speed_btn)
        vbox.addLayout(hbox_speed_pass)
        vbox.addLayout(hbox_speed_gruz)
        vbox.addStretch(1)
        return widget

    def __handle_speed_btn(self):
        sender = self.sender()
        for btn in self.buttons:
            if btn is sender:
                btn.setStyleSheet("background-color: blue")
            else:
                btn.setStyleSheet(focus_style)
        self.chart_view_strelograph_empty_chart.setStyleSheet("")
        self.chart_view_profile_empty_chart.setStyleSheet("")
        self.chart_view_sagging_chart.setStyleSheet("")
        #self.chart_view_speed_empty_chart.setStyleSheet("border:7px solid blue;")
        self.chart_view_speed_empty_chart.setStyleSheet(
            "border:13px solid blue; border-left: none; border-top: none; border-bottom: none;")
        self.chart_view_situation_empty_chart.setStyleSheet("")
        self.current_chart_view = "speed"
        self.chart_view_speed_empty_chart.chart().addSeries(self.vertical_static_line_series_speed)
        self.vertical_static_line_series_speed.attachAxis(self.chart_view_speed_empty_chart.chart().axisX())
        self.vertical_static_line_series_speed.attachAxis(self.chart_view_speed_empty_chart.chart().axisY())
        #
        self.plan_btn.setFocusPolicy(Qt.NoFocus)
        self.level_btn.setFocusPolicy(Qt.NoFocus)
        self.profile_btn.setFocusPolicy(Qt.NoFocus)
        self.speed_btn.setFocusPolicy(Qt.NoFocus)
        self.situation_btn.setFocusPolicy(Qt.NoFocus)
        #
        self.speed_pass_value.setFocusPolicy(Qt.StrongFocus)
        self.speed_gruz_value.setFocusPolicy(Qt.StrongFocus)
        self.lifting_right_value.setFocusPolicy(Qt.NoFocus)
        self.lifting_left_value.setFocusPolicy(Qt.NoFocus)
        self.setFocus()

    def __handleLineEditSpeedPass(self):
        if self.current_chart_view == "speed":
            new_y = int(self.speed_pass_value.text())
            for i in range(
                        min(int(self.__options.start_picket.meters + self.static_line_position), int(self.currentPosition)),
                        max(int(self.__options.start_picket.meters + self.static_line_position), int(self.currentPosition)),
                        1):
                    self.speed_series_pass.replace(i, i, new_y)
            self.speed_points.append(
                    [min(self.__options.start_picket.meters + self.static_line_position, self.currentPosition),
                     self.__restrictions['segments'][0]['v_pass']])
            self.speed_points.append(
                    [min(self.__options.start_picket.meters + self.static_line_position, self.currentPosition), new_y])
            self.speed_points.append(
                    [max(self.__options.start_picket.meters + self.static_line_position, self.currentPosition), new_y])
            self.speed_points.append(
                    [max(self.__options.start_picket.meters + self.static_line_position, self.currentPosition),
                     self.__restrictions['segments'][0]['v_pass']])
            speed_pass_segments = self.divide_data(self.__restrictions['segments'][0]['v_pass'], self.speed_points)
            self.speed_segments.append(speed_pass_segments[-1])
            self.speed_pool = cycle(self.speed_segments)
            if not self.unsavedChanges:
                self.unsavedChanges = True
            self.speed_pass_value.clear()
            self.setFocus()

    def __handleLineEditSpeedGruz(self):
        if self.current_chart_view == "speed":
            new_y = int(self.speed_gruz_value.text())
            for i in range( min(int(self.__options.start_picket.meters + self.static_line_position), int(self.currentPosition)),
                    max(int(self.__options.start_picket.meters + self.static_line_position), int(self.currentPosition)), 1):
                self.speed_series_gruz.replace(i, i, new_y)
            self.speed_points.append([min(self.__options.start_picket.meters + self.static_line_position, self.currentPosition),
                 self.__restrictions['segments'][0]['v_gruz']])
            self.speed_points.append([min(self.__options.start_picket.meters + self.static_line_position, self.currentPosition), new_y])
            self.speed_points.append([max(self.__options.start_picket.meters + self.static_line_position, self.currentPosition), new_y])
            self.speed_points.append([max(self.__options.start_picket.meters + self.static_line_position, self.currentPosition),
                 self.__restrictions['segments'][0]['v_gruz']])
            speed_gruz_segments = self.divide_data(self.__restrictions['segments'][0]['v_gruz'], self.speed_points)
            self.speed_segments.append(speed_gruz_segments[-1])
            self.speed_pool = cycle(self.speed_segments)
            if not self.unsavedChanges:
                self.unsavedChanges = True
            self.speed_gruz_value.clear()
            self.setFocus()

    ####################################    Situation  ??? ###############################
    def __situationWidget(self):
        vbox = QVBoxLayout()
        widget = QWidget()
        widget.setProperty("sensorWidgetBox", True)
        widget.setLayout(vbox)
        #self.situation_btn = QPushButton("Ситуация")
        self.buttons.append(self.situation_btn)
        self.situation_btn.setStyleSheet(focus_style)
        self.situation_btn.clicked.connect(self.__handle_situation_btn)
        lbl_left = QLabel("Левый")
        lbl_right = QLabel("Правый")
        lbl_nature = QLabel("Натурные")
        lbl_value1 = QLabel("---")
        lbl_value2 = QLabel("---")
        lbl_value1.setObjectName("sensorsValue")
        lbl_value2.setObjectName("sensorsValue")
        hbox_values = QHBoxLayout()
        hbox_values.addWidget(lbl_value1)
        hbox_values.addWidget(lbl_value2)
        vbox.addWidget(self.situation_btn)
        #vbox.addWidget(lbl_left)
        #vbox.addWidget(lbl_right)
        #vbox.addWidget(lbl_nature)
        #vbox.addLayout(hbox_values)
        vbox.addStretch(1)
        return widget

    def __handle_situation_btn(self):
        sender = self.sender()
        for btn in self.buttons:
            if btn is sender:
                btn.setStyleSheet("background-color: blue")
            else:
                btn.setStyleSheet(focus_style)
        self.chart_view_strelograph_empty_chart.setStyleSheet("")
        self.chart_view_profile_empty_chart.setStyleSheet("")
        self.chart_view_speed_empty_chart.setStyleSheet("")
        self.chart_view_sagging_chart.setStyleSheet("")
        #
        self.plan_btn.setFocusPolicy(Qt.NoFocus)
        self.level_btn.setFocusPolicy(Qt.NoFocus)
        self.profile_btn.setFocusPolicy(Qt.NoFocus)
        self.speed_btn.setFocusPolicy(Qt.NoFocus)
        self.situation_btn.setFocusPolicy(Qt.StrongFocus)
        #
        self.speed_pass_value.setFocusPolicy(Qt.NoFocus)
        self.speed_gruz_value.setFocusPolicy(Qt.NoFocus)
        self.setFocus()

    #####################################  Save #######################################################
    def __saveResult(self):
        shifting_left_values_x, shifting_left_values_y, shifting_right_values_x, shifting_right_values_y = [], [], [], []
        ubound_values_x, ubound_values_y, lbound_values_x, lbound_values_y = [], [], [], []
        v_pass_values_x, v_pass_values_y, v_gruz_values_x, v_gruz_values_y = [], [], [], []
        _restrictions = copy.deepcopy(self.__restrictions)                     # deep copy для экспериментов
        if self.plan_segments:
            for segment in self.plan_segments:
                if segment[0][1] == self.__restrictions['segments'][0]['shifting_left']:      # 50
                    shifting_left_values_x.append([segment[1][0], segment[2][0]])
                    shifting_left_values_y.append([segment[1][1], segment[2][1]])
                elif segment[0][1] == self.__restrictions['segments'][0]['shifting_right']:    # -50
                    shifting_right_values_x.append([segment[1][0], segment[2][0]])
                    shifting_right_values_y.append([segment[1][1], segment[2][1]])
        if self.profile_segments:
            for segment in self.profile_segments:
                if segment[0][1] == self.__restrictions['segments'][0]['raising_ubound']:      # 60
                    ubound_values_x.append([segment[1][0], segment[2][0]])
                    ubound_values_y.append([segment[1][1], segment[2][1]])
                elif segment[0][1] == self.__restrictions['segments'][0]['raising_lbound']:    # 15
                    lbound_values_x.append([segment[1][0], segment[2][0]])
                    lbound_values_y.append([segment[1][1], segment[2][1]])
        if self.speed_segments:
            for segment in self.speed_segments:
                if segment[0][1] == self.__restrictions['segments'][0]['v_pass']:      # 120
                    v_pass_values_x.append([segment[1][0], segment[2][0]])
                    v_pass_values_y.append([segment[1][1], segment[2][1]])
                elif segment[0][1] == self.__restrictions['segments'][0]['v_gruz']:    # 80
                    v_gruz_values_x.append([segment[1][0], segment[2][0]])
                    v_gruz_values_y.append([segment[1][1], segment[2][1]])
        shifting_right = dict()
        if shifting_right_values_x and shifting_right_values_y:
            shifting_right = {"shifting_right": {
                "x": shifting_right_values_x,
                "y": shifting_right_values_y
            }}
        # #
        shifting_left = dict()
        if shifting_left_values_x and shifting_left_values_y:
            shifting_left = {"shifting_left": {
                "x": shifting_left_values_x,
                "y": shifting_left_values_y
            }}
        # ########################################################################################
        raising_ubound = dict()
        if ubound_values_x and ubound_values_y:
            raising_ubound = {"raising_ubound": {
                "x": ubound_values_x,
                "y": ubound_values_y
            }}
        # #
        raising_lbound = dict()
        if lbound_values_x and lbound_values_y:
            raising_lbound = {"raising_lbound": {
                "x": lbound_values_x,
                "y": lbound_values_y
            }}
        # #########################################################################################
        v_gruz = dict()
        if v_gruz_values_x and v_gruz_values_y:
            v_gruz = {"v_gruz": {
                "x": v_gruz_values_x,
                "y": v_gruz_values_y
            }}
        v_pass=dict()
        if v_pass_values_x and v_pass_values_y:
            v_pass = {"v_pass": {
                "x": v_pass_values_x,
                "y": v_pass_values_y
            }}
        #
        result=dict()
        if shifting_right:
            result['shifting_right'] = shifting_right['shifting_right']
        if shifting_left:
            result['shifting_left'] = shifting_left['shifting_left']
        if raising_ubound:
            result['raising_ubound'] = raising_ubound['raising_ubound']
        if raising_lbound:
            result['raising_lbound'] = raising_lbound['raising_lbound']
        if v_gruz:
            result['v_gruz'] = v_gruz['v_gruz']
        if v_pass:
            result['v_pass'] = v_pass['v_pass']

        # рабочий вариант
        self.__restrictions["segments"].append(result)
        # тестовый вариант
        # with open('/home/boris/Рабочий стол/__restrictions.json', 'w', encoding='utf-8') as f:
        #     _restrictions["segments"].append(result)
        #     json.dump(_restrictions, f, ensure_ascii=False, indent=4)
        #
        if self.unsavedChanges:
            self.unsavedChanges = False

    #####################################  Quit #######################################################
    def __quitView(self):
        if self.unsavedChanges:
            msg = QMessageBox(self)
            msg.setText("Есть несохранённые изменения.\n Сохранить и выйти?")
            buttonAccept = msg.addButton("Да", QMessageBox.YesRole)
            buttonCancel = msg.addButton("Нет", QMessageBox.RejectRole)
            msg.setDefaultButton(buttonAccept)
            msg.exec()
            if msg.clickedButton() == buttonCancel:
                self.detailedRestrictionsSignal.emit('close')              #  выход без сохранения
            elif msg.clickedButton() == buttonAccept:
                self.__saveResult()
                self.detailedRestrictionsSignal.emit('close')               # сохранить и выйти
        else:
            self.detailedRestrictionsSignal.emit('close')

    #####################################  Справка #######################################################
    def __openReference(self):
        msg = QMessageBox(self)
        msg.setText("'Выбор позиции': с помощью стрелок [влево/вправо] переместите вертикальную фиолетовую линию в нужную позицию.\n\n"
                    "'Установка начала ограничения': в нужной позиции нажмите кнопку [D], появится вертикальная зелёная линия. \n\n"            
                    "'Установка конца ограничения': переместите фиолетовую линию с помощью стрелок [ВЛЕВО/ВПРАВО].\n\n"
                    "'Выбор секции': используйте клавишу [TAB] для перехода между кнопками. Для входа в секцию на выбранной кнопке нажмите [ПРОБЕЛ]\n\n"
                    "'Ввод значения ограничения': нажмите [TAB] для перехода в окно ввода значения, введите число и нажмите [ENTER]. \n\n"
                    "'Выбор сегмента для удаления': клавишей [BACKSPACE] можно перемещаться по всем изменениям в текущей секции."
                    "'Удаление выбранного сегмента': клавиша [DELETE].\n\n"
                    "'Выход из секции': клавиша [Escape]\n\n"
                    "'Доступ к кнопкам 'Справка', 'Сохранить', 'Выйти'': через клавиши F2, F3, F4 соответственно или мышью.")
        msg.setStyleSheet("QMessageBox {font: 20px; background-color: #fefefe;}")
        msg.exec()

    #
    def __rangeError(self, range0: int, range1: int):
        msg = QMessageBox(self)
        msg.setText("Диапазон значений {0} - {1}".format(range0, range1))
        buttonAccept = msg.addButton("Ok", QMessageBox.YesRole)
        msg.setDefaultButton(buttonAccept)
        msg.exec()




