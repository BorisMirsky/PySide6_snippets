from PySide6.QtWidgets import (QWidget, QListWidget, QVBoxLayout, QApplication,QGroupBox,QPushButton,QStackedLayout,
                               QHBoxLayout, QGridLayout, QLabel, QFileDialog,QMessageBox,QStyle)
from PySide6.QtGui import QFont, QIcon, QShortcut, Qt, QPen, QPainter, QImage, QPixmap, QColor, QBrush
from PySide6.QtCharts import QChartView, QLineSeries, QAreaSeries, QVXYModelMapper
from PySide6.QtCore import Qt, QTimer, QDateTime, QCoreApplication, QPointF, QMargins, Signal, QObject, QEvent
from presentation.models.PicketPositionedTableModel import PicketPositionedTableModel
from presentation.ui.gui.common.viewes.TableDataChartsView import DynamicLineSeries, AbstractChartOrientationMixin, HorizontalChart
from domain.dto.Travelling import PicketDirection, LocationVector1D
from domain.dto.Workflow import LiningTripResultDto
from operating.states.program_task_calculation.ProgramTaskCalculationState import ProgramTaskCalculationSuccessState
from operating.states.lining.ApplicationLiningState import LiningProcessState
from domain.models.AbstractPositionedTableModel import AbstractPositionedTableModel
from domain.models.StepIndexedDataFramePositionedModel import StepIndexedDataFramePositionedModel
from domain.calculations.plan_model import TrackProjectModel, TrackPlanProjectModel, TrackProjectType
from domain.calculations.progtask import machine_task_from_base_data_new
from domain.calculations.helpers import change_machine_chord_to_sym_chord_10
from domain.dto.Workflow import ProgramTaskCalculationResultDto, ProgramTaskCalculationOptionsDto, ProgramTaskBaseData
from ..program_task_calculation.viewes.Infopanel import InfopanelFirst, InfopanelSecond
from presentation.ui.gui.common.viewes.LabelOnChart import LabelOnParent, LabelOnParent2
from ..common.viewes.MarkersChart import MarkersChart
from presentation.ui.gui.common.viewes.WindowTitle import Window
from typing import Optional, List
import sys
import os
import zipfile
import copy
import pandas as pd

focus_style = "QWidget:focus { border: 3px solid #FF0000; border-radius: 5px; background-color: white}"






class ShowLiningResult(QWidget):
    def __init__(self, data: LiningTripResultDto, parent: QWidget = None):
        super().__init__(parent)
        self.__data = data
        self.options: ProgramTaskCalculationResultDto = self.__data.options
        self.calculated_task_data_copy = copy.deepcopy(self.options.program_task.calculated_task.data)
        for col in ['strelograph_work', 'pendulum_work', 'sagging_left']:
            self.calculated_task_data_copy[col] = self.__data.measurements.data[col]
        # Стрелограф
        strelograf = change_machine_chord_to_sym_chord_10(
            measurements=self.__data.measurements.data.strelograph_work,
            back_chord=self.__data.options.program_task.options.measuring_trip.machine_parameters['back_horde_plan'],
            front_chord=self.__data.options.program_task.options.measuring_trip.machine_parameters['front_horde_plan'],
        )
        strelograf_transformed = pd.Series(strelograf)    # [:1000] - test!
        # обработка несоответствия размерностей
        if self.calculated_task_data_copy.shape[0] > strelograf_transformed.shape[0]:
            self.calculated_task_data_copy['strelograf_work_transformed'] = strelograf_transformed
            # Ignored NaN, Inf, or -Inf value
        elif self.calculated_task_data_copy.shape[0] < strelograf_transformed.shape[0]:
            self.calculated_task_data_copy['strelograf_work_transformed'] = strelograf_transformed[:self.calculated_task_data_copy.shape[0]]
        else:
            self.calculated_task_data_copy['strelograf_work_transformed'] = strelograf_transformed

        # Просадки
        sagging_left = change_machine_chord_to_sym_chord_10(
            measurements=self.__data.measurements.data.sagging_left,
            back_chord=self.__data.options.program_task.options.measuring_trip.machine_parameters['back_horde_prof'],
            front_chord=self.__data.options.program_task.options.measuring_trip.machine_parameters['front_horde_prof'],
        )
        sagging_left_transformed = pd.Series(sagging_left)
        # обработка несоответствия размерностей
        if self.calculated_task_data_copy.shape[0] > sagging_left_transformed.shape[0]:
            self.calculated_task_data_copy['sagging_left_transformed'] = sagging_left_transformed   # Ignored NaN, Inf, or -Inf value
        elif self.calculated_task_data_copy.shape[0] < sagging_left_transformed.shape[0]:
            self.calculated_task_data_copy['sagging_left_transformed'] = sagging_left_transformed[:self.calculated_task_data_copy.shape[0]]
        else:
            self.calculated_task_data_copy['sagging_left_transformed'] = sagging_left_transformed

        programTaskModel = StepIndexedDataFramePositionedModel(
            columns=self.calculated_task_data_copy.columns,
            step=self.options.program_task.calculated_task.step,
            parent=self )
        programTaskModel.reset(self.options.program_task.calculated_task.step,  self.calculated_task_data_copy)
        self.__programTaskByPicketModel = PicketPositionedTableModel(self.options.picket_direction,  self.options.start_picket.meters)
        self.__programTaskByPicketModel.setSourceModel(programTaskModel)
        position_multiplyer: int = self.options.picket_direction.multiplier()
        position_range: tuple[LocationVector1D, LocationVector1D] = programTaskModel.minmaxPosition()
        position_min: float = position_multiplyer * position_range[0].meters + self.options.start_picket.meters
        position_max: float = position_multiplyer * position_range[1].meters + self.options.start_picket.meters
        #=============================================== Charts ===================================================
        charts_vbox = QVBoxLayout()
        column_name = ['plan_fact', 'plan_prj', 'strelograf_work_transformed']
        chart_value_range0: (float, float) = programTaskModel.minmaxValueByColumn(column_name[0])
        chart_value_range1: (float, float) = programTaskModel.minmaxValueByColumn(column_name[1])
        chart_value_range2: (float, float) = programTaskModel.minmaxValueByColumn(column_name[2])
        chart_value_range = (
                     min(chart_value_range0[0], chart_value_range1[0], chart_value_range2[0]),
                     max(chart_value_range0[1], chart_value_range1[1], chart_value_range2[1]))
        chart_value_range_length = chart_value_range[1] - chart_value_range[0]
        chart_value_min: float = chart_value_range[0] - 0.00001 - 0.05 * chart_value_range_length
        chart_value_max: float = chart_value_range[1] + 1.00001 + 0.05 * chart_value_range_length
        self.series0 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                         programTaskModel.modelColumnIndexAtName(column_name[0]),
                                         QCoreApplication.translate(
                                             'Lining trip/process/view/charts/program task', column_name[0]))
        self.series1 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                         programTaskModel.modelColumnIndexAtName(column_name[1]),
                                         QCoreApplication.translate(
                                             'Lining trip/process/view/charts/program task', column_name[1]))
        self.series2 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                         programTaskModel.modelColumnIndexAtName(column_name[2]),
                                         QCoreApplication.translate(
                                             'Lining trip/process/view/charts/program task', column_name[2]))
        self.series0.setPen(QPen(QColor("cyan"), 2))
        self.series1.setPen(QPen(QColor("red"), 2))
        self.series2.setPen(QPen(QColor("yellow"), 2))
        vertical_chart_title = "Стрелы изгиба, мм"
        self.chart1 = HorizontalChart((position_min, position_max),
                                 self.options.picket_direction == PicketDirection.Backward,
                                 (chart_value_min, chart_value_max), False,
                                 series0=[self.series0], series1=[self.series1], series2=[self.series2],
                                 x_tick=100,  # y_tick=20,
                                 title=vertical_chart_title,
                                 xMinorTickCount=9, yMinorTickCount=1,
                                 xGridLineColor="gray", yGridLineColor="gray",
                                 xMinorGridLineColor="gray", yMinorGridLineColor="gray",
                                 is_y_zero_axe_visible=False)
        self.chart_view1 = QChartView(self.chart1)
        horizontal_chart_title = LabelOnParent('План', self.chart_view1)
        horizontal_chart_title.setStyleSheet("color:white;font:bold 20px;")
        self.chart_view1.setFocusPolicy(Qt.NoFocus)
        self.chart_view1.chart().setBackgroundBrush(QBrush("black"))
        self.chart_view1.setRenderHint(QPainter.Antialiasing)
        self.chart1.legend().hide()
        self.chart1.layout().setContentsMargins(0, 0, 0, 0)
        self.chart1.setMargins(QMargins(0, 0, 0, 0))
        self.chart1.axes(Qt.Orientation.Horizontal)[0].setGridLineVisible(True)
        self.chart1.axes(Qt.Orientation.Vertical)[0].setGridLineVisible(True)
        charts_vbox.addWidget(self.chart_view1, 2)
        #
        column_name = ['plan_delta']
        chart_value_range: (float, float) = programTaskModel.minmaxValueByColumn(column_name[0])
        chart_value_range_length = chart_value_range[1] - chart_value_range[0]
        chart_value_min: float = chart_value_range[0] - 0.00001 - 0.05 * chart_value_range_length
        chart_value_max: float = chart_value_range[1] + 1.00001 + 0.05 * chart_value_range_length
        self.series3 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                         programTaskModel.modelColumnIndexAtName(column_name[0]),
                                         QCoreApplication.translate(
                                             'Lining trip/process/view/charts/program task', column_name[0]))
        self.chart2 = HorizontalChart((position_min, position_max),
                                      self.options.picket_direction == PicketDirection.Backward,
                                      (chart_value_min, chart_value_max), False,
                                      series0=[self.series3],
                                      x_tick=100,  # y_tick=20,
                                      title="Сдвиги, мм",
                                      xMinorTickCount=9, yMinorTickCount=1,
                                      xGridLineColor="gray", yGridLineColor="gray",
                                      xMinorGridLineColor="gray", yMinorGridLineColor="gray",
                                      is_y_zero_axe_visible=True)
        self.chart_view2 = QChartView(self.chart2)
        self.chart_view2.setFocusPolicy(Qt.NoFocus)
        self.chart_view2.chart().setBackgroundBrush(QBrush("black"))
        self.chart_view2.setRenderHint(QPainter.Antialiasing)
        self.chart2.legend().hide()
        self.chart2.layout().setContentsMargins(0, 0, 0, 0)
        self.chart2.setMargins(QMargins(0, 0, 0, 0))
        self.chart2.axes(Qt.Orientation.Horizontal)[0].setGridLineVisible(True)
        self.chart2.axes(Qt.Orientation.Vertical)[0].setGridLineVisible(True)
        charts_vbox.addWidget(self.chart_view2, 1)
        #
        column_name = ['vozv_fact', 'vozv_prj', 'pendulum_work']
        chart_value_range0: (float, float) = programTaskModel.minmaxValueByColumn(column_name[0])
        chart_value_range1: (float, float) = programTaskModel.minmaxValueByColumn(column_name[1])
        chart_value_range2: (float, float) = programTaskModel.minmaxValueByColumn(column_name[2])
        chart_value_range = (
            min(chart_value_range0[0], chart_value_range1[0], chart_value_range2[0]),
            max(chart_value_range0[1], chart_value_range1[1], chart_value_range2[1]))
        chart_value_range_length = chart_value_range[1] - chart_value_range[0]
        chart_value_min: float = chart_value_range[0] - 0.00001 - 0.05 * chart_value_range_length
        chart_value_max: float = chart_value_range[1] + 1.00001 + 0.05 * chart_value_range_length
        self.series4 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                         programTaskModel.modelColumnIndexAtName(column_name[0]),
                                         QCoreApplication.translate(
                                             'Lining trip/process/view/charts/program task', column_name[0]))
        self.series5 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                         programTaskModel.modelColumnIndexAtName(column_name[1]),
                                         QCoreApplication.translate(
                                             'Lining trip/process/view/charts/program task', column_name[1]))
        self.series6 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                         programTaskModel.modelColumnIndexAtName(column_name[2]),
                                         QCoreApplication.translate(
                                             'Lining trip/process/view/charts/program task', column_name[2]))
        self.series4.setPen(QPen(QColor("cyan"), 2))
        self.series5.setPen(QPen(QColor("red"), 2))
        self.series6.setPen(QPen(QColor("yellow"), 2))
        vertical_chart_title = "ВНР, мм"
        is_y_zero_axe_visible_value = True
        self.chart3 = HorizontalChart((position_min, position_max),
                                      self.options.picket_direction == PicketDirection.Backward,
                                      (chart_value_min, chart_value_max), False,
                                      series0=[self.series4], series1=[self.series5], series2=[self.series6],
                                      x_tick=100,  # y_tick=20,
                                      title=vertical_chart_title,
                                      xMinorTickCount=9, yMinorTickCount=1,
                                      xGridLineColor="gray", yGridLineColor="gray",
                                      xMinorGridLineColor="gray", yMinorGridLineColor="gray",
                                      is_y_zero_axe_visible=is_y_zero_axe_visible_value)
        self.chart_view3 = QChartView(self.chart3)
        self.horizontal_chart_title = LabelOnParent('Уровень', self.chart_view3)
        self.horizontal_chart_title.setStyleSheet("color:white;font:bold 20px;")
        self.chart_view3.setFocusPolicy(Qt.NoFocus)
        self.chart_view3.chart().setBackgroundBrush(QBrush("black"))
        self.chart_view3.setRenderHint(QPainter.Antialiasing)
        self.chart3.legend().hide()
        self.chart3.layout().setContentsMargins(0, 0, 0, 0)
        self.chart3.setMargins(QMargins(0, 0, 0, 0))
        self.chart3.axes(Qt.Orientation.Horizontal)[0].setGridLineVisible(True)
        self.chart3.axes(Qt.Orientation.Vertical)[0].setGridLineVisible(True)
        charts_vbox.addWidget(self.chart_view3, 1)
        #
        column_name = ['prof_fact_left', 'prof_prj', 'sagging_left_transformed']
        chart_value_range0: (float, float) = programTaskModel.minmaxValueByColumn(column_name[0])
        chart_value_range1: (float, float) = programTaskModel.minmaxValueByColumn(column_name[1])
        chart_value_range2: (float, float) = programTaskModel.minmaxValueByColumn(column_name[2])
        chart_value_range = (
            min(chart_value_range0[0], chart_value_range1[0], chart_value_range2[0]),
            max(chart_value_range0[1], chart_value_range1[1], chart_value_range2[1]))
        chart_value_range_length = chart_value_range[1] - chart_value_range[0]
        chart_value_min: float = chart_value_range[0] - 0.00001 - 0.05 * chart_value_range_length
        chart_value_max: float = chart_value_range[1] + 1.00001 + 0.05 * chart_value_range_length
        self.series7 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                         programTaskModel.modelColumnIndexAtName(column_name[0]),
                                         QCoreApplication.translate(
                                             'Lining trip/process/view/charts/program task', column_name[0]))
        self.series8 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                         programTaskModel.modelColumnIndexAtName(column_name[1]),
                                         QCoreApplication.translate(
                                             'Lining trip/process/view/charts/program task', column_name[1]))
        self.series9 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                         programTaskModel.modelColumnIndexAtName(column_name[2]),
                                         QCoreApplication.translate(
                                             'Lining trip/process/view/charts/program task', column_name[2]))
        self.series7.setPen(QPen(QColor("cyan"), 2))
        self.series8.setPen(QPen(QColor("red"), 2))
        self.series9.setPen(QPen(QColor("yellow"), 2))
        vertical_chart_title = "Стрелы, мм"
        is_y_zero_axe_visible_value = True
        self.chart4 = HorizontalChart((position_min, position_max),
                                      self.options.picket_direction == PicketDirection.Backward,
                                      (chart_value_min, chart_value_max), False,
                                      series0=[self.series7], series1=[self.series8], series2=[self.series9], #series3=[self.series10],
                                      x_tick=100,  # y_tick=20,
                                      title=vertical_chart_title,
                                      xMinorTickCount=9, yMinorTickCount=1,
                                      xGridLineColor="gray", yGridLineColor="gray",
                                      xMinorGridLineColor="gray", yMinorGridLineColor="gray",
                                      is_y_zero_axe_visible=is_y_zero_axe_visible_value)
        self.chart_view4 = QChartView(self.chart4)
        self.horizontal_chart_title = LabelOnParent('Профиль', self.chart_view4)
        self.horizontal_chart_title.setStyleSheet("color:white;font:bold 20px;")
        self.chart_view4.setFocusPolicy(Qt.NoFocus)
        self.chart_view4.chart().setBackgroundBrush(QBrush("black"))
        self.chart_view4.setRenderHint(QPainter.Antialiasing)
        self.chart4.legend().hide()
        self.chart4.layout().setContentsMargins(0, 0, 0, 0)
        self.chart4.setMargins(QMargins(0, 0, 0, 0))
        self.chart4.axes(Qt.Orientation.Horizontal)[0].setGridLineVisible(True)
        self.chart4.axes(Qt.Orientation.Vertical)[0].setGridLineVisible(True)
        charts_vbox.addWidget(self.chart_view4, 1)
        #
        column_name = ['prof_delta']
        chart_value_range: (float, float) = programTaskModel.minmaxValueByColumn(column_name[0])
        chart_value_range_length = chart_value_range[1] - chart_value_range[0]
        chart_value_min: float = chart_value_range[0] - 0.00001 - 0.05 * chart_value_range_length
        chart_value_max: float = chart_value_range[1] + 1.00001 + 0.05 * chart_value_range_length
        self.series7 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                         programTaskModel.modelColumnIndexAtName(column_name[0]),
                                         QCoreApplication.translate(
                                             'Lining trip/process/view/charts/program task', column_name[0]))
        self.chart5 = HorizontalChart((position_min, position_max),
                                      self.options.picket_direction == PicketDirection.Backward,
                                      (chart_value_min, chart_value_max), False,
                                      series0=[self.series7],
                                      x_tick=100,  # y_tick=20,
                                      title="Подъёмки, мм",
                                      xMinorTickCount=9, yMinorTickCount=1,
                                      xGridLineColor="gray", yGridLineColor="gray",
                                      xMinorGridLineColor="gray", yMinorGridLineColor="gray",
                                      is_y_zero_axe_visible=True)
        self.chart_view5 = QChartView(self.chart5)
        self.chart_view5.setFocusPolicy(Qt.NoFocus)
        self.chart_view5.chart().setBackgroundBrush(QBrush("black"))
        self.chart_view5.setRenderHint(QPainter.Antialiasing)
        self.chart5.legend().hide()
        self.chart5.layout().setContentsMargins(0, 0, 0, 0)
        self.chart5.setMargins(QMargins(0, 0, 0, 0))
        self.chart5.axes(Qt.Orientation.Horizontal)[0].setGridLineVisible(True)
        self.chart5.axes(Qt.Orientation.Vertical)[0].setGridLineVisible(True)
        charts_vbox.addWidget(self.chart_view5, 1)
    
        self.chart6 = MarkersChart(title="Ситуация",  options = self.options.program_task.options, parent=self).getChart()
        charts_vbox.addWidget(self.chart6, 1)

        self.installEventFilter(self)
        grid = QGridLayout()
        infopanel_first = InfopanelFirst(self.__data)
        infopanel_second = InfopanelSecond(self.__data)
        #title_window = LabelOnParent2('Результаты выправки', 500, 0, 250, 40, infopanel_first)
        #title_window.setWordWrap(True)
        #title_window.setStyleSheet("background-color:yellow;border:1px solid black;padding:5px;")
        self.__window = Window('Результаты выправки')
        grid.addWidget(infopanel_first, 0, 0, 1, 7)
        grid.addWidget(infopanel_second, 1, 0, 1, 7)
        grid.addLayout(charts_vbox, 2, 1, 7, 1)
        self.lcw = self.__leftColumnWidget()
        grid.addLayout(self.lcw, 2, 0, 7, 1)
        self.__window.addLayout(grid, 1)
        self.setLayout(self.__window)

    def eventFilter(self, watched: QObject, event: QEvent):
        if event.type() == QEvent.Type.Show:
            self.setFocus()
        if event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Escape:
                self.close()
                #self.__escapeView()
        return False


    def __escapeView(self):
        if QMessageBox.question(self, QCoreApplication.translate('Program task calculation/success/finish message box', 'Quit'),
        QCoreApplication.translate('Program task calculation/success/finish message box', 'Do you really want to go out?')) == QMessageBox.StandardButton.No:
            return
        #self.__data.finish.emit()
        self.close()
    #
    def __leftColumnWidget(self):
        vbox = QVBoxLayout()
        self.escape_button = QPushButton("Выход (ESC)")
        self.escape_button.setProperty("optionsWindowPushButton", True)
        #self.escape_button.setStyleSheet(focus_style)
        self.escape_button.clicked.connect(self.__escapeView)
        vbox.addStretch(5)
        vbox.addWidget(self.escape_button)
        vbox.addStretch(1)
        return vbox
