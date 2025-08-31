from PySide6.QtWidgets import (QWidget, QListWidget, QVBoxLayout, QApplication,QGroupBox,QPushButton,QStackedLayout,
                               QHBoxLayout, QGridLayout, QLabel, QFileDialog,QMessageBox,QStyle)
from PySide6.QtGui import QFont, QIcon, QShortcut, Qt, QPen, QPainter, QImage, QPixmap, QColor, QBrush
from PySide6.QtCharts import QChartView, QLineSeries, QAreaSeries, QVXYModelMapper
from PySide6.QtCore import Qt, QTimer, QDateTime, QCoreApplication, QPointF, QMargins, Signal
from presentation.models.PicketPositionedTableModel import PicketPositionedTableModel
from presentation.ui.gui.common.viewes.TableDataChartsView import DynamicLineSeries, AbstractChartOrientationMixin, HorizontalChart
from domain.dto.Travelling import PicketDirection, LocationVector1D
from operating.states.program_task_calculation.ProgramTaskCalculationState import ProgramTaskCalculationSuccessState
from operating.states.lining.ApplicationLiningState import LiningProcessState
from domain.models.AbstractPositionedTableModel import AbstractPositionedTableModel
from domain.models.StepIndexedDataFramePositionedModel import StepIndexedDataFramePositionedModel
from domain.calculations.plan_model import TrackProjectModel, TrackPlanProjectModel, TrackProjectType  #, TrackProfileProjectModel
from domain.calculations.progtask import machine_task_from_base_data_new
from domain.dto.Workflow import ProgramTaskCalculationResultDto, ProgramTaskCalculationOptionsDto, ProgramTaskBaseData
from ......utils.store.workflow.zip.Dto import ProgramTaskCalculationResultDto_to_archive
from ...viewes.Infopanel import InfopanelFirst, InfopanelSecond
from ...viewes.LabelOnChart import LabelOnParent
from ..Plan.PlanMain.PlanMainWindow import PlanView
from ..Level.LevelMain.LevelMainWindow import LevelView
from ..Profile.ProfileMain.ProfileMainWindow import ProfileView
from typing import Optional, List
import sys
import os
import zipfile
import math
from functools import partial



focus_style = "QPushButton:focus { border: 3px solid #FF0000; border-radius: 5px; background-color: white; color: black;}"


# Общий stacked класс для всего Переустройства. Пустой, принимает представления.
class ProgramTaskCalculationSuccessView(QWidget):
    def __init__(self, state: ProgramTaskCalculationSuccessState,
                 parent: QWidget = None):
        super().__init__(parent)
        self.__state = state
        self.__calculation_result = self.__state.calculation_result()
        self.__layout: QStackedLayout = QStackedLayout()
        self.__layout.setStackingMode(QStackedLayout.StackingMode.StackOne)
        self.__currentView: QWidget = None
        self.reconstruction = ReconstructionMain(self.__state, parent=self)
        self.reconstruction.updateCalculationResultSignal.connect(self.__updateCalculationResult)
        self.__openReconstructionView()
        self.setLayout(self.__layout)

    def __updateCalculationResult(self, data:ProgramTaskCalculationResultDto):
        self.__calculation_result = data

    def __clearCurrentView(self):
        if self.__currentView:
            self.__currentView = None

    def __openReconstructionView(self):
        self.__clearCurrentView()
        self.__currentView = self.reconstruction
        self.__currentView.openPlanSignal.connect(self.__openPlanView)
        self.__currentView.openLevelSignal.connect(self.__openLevelView)
        self.__currentView.openProfileSignal.connect(self.__openProfileView)
        self.__layout.addWidget(self.__currentView)
        self.__layout.setCurrentWidget(self.__currentView)
        self.setWindowTitle("Main Reconstruction Window")

    def __openPlanView(self):
        self.__clearCurrentView()
        self.__currentView = PlanView(self.__calculation_result)
        self.__currentView.planMain.planMainSignal.connect(self.__openReconstructionView)
        self.__currentView.planMain.passDataSignal.connect(self.reconstruction.rerenderCharts)
        self.__layout.addWidget(self.__currentView)
        self.__layout.setCurrentWidget(self.__currentView)

    def __openLevelView(self):
        self.__clearCurrentView()
        self.__currentView = LevelView(self.__calculation_result)
        self.__currentView.levelMain.levelMainSignal.connect(self.__openReconstructionView)
        self.__currentView.levelMain.passDataSignal.connect(self.reconstruction.rerenderCharts)
        self.__layout.addWidget(self.__currentView)
        self.__layout.setCurrentWidget(self.__currentView)

    def __openProfileView(self):
        self.__clearCurrentView()
        self.__currentView = ProfileView(self.__calculation_result)
        self.__currentView.profileMain.profileMainSignal.connect(self.__openReconstructionView)
        self.__currentView.profileMain.passDataSignal.connect(self.reconstruction.rerenderCharts)
        #  ...lifting...
        self.__layout.addWidget(self.__currentView)
        self.__layout.setCurrentWidget(self.__currentView)



# Главное окно переустройства
class ReconstructionMain(QWidget):
    openPlanSignal = Signal(str)
    openLevelSignal = Signal(str)
    openProfileSignal = Signal(str)
    updateCalculationResultSignal = Signal(ProgramTaskCalculationResultDto)
    def __init__(self, state: ProgramTaskCalculationSuccessState, parent: QWidget = None):
        super().__init__(parent)
        self.__state = state
        self.__calculation_result = self.__state.calculation_result()
        programTaskModel = StepIndexedDataFramePositionedModel(self.__calculation_result.calculated_task.data.columns,
                                                               self.__calculation_result.calculated_task.step, self)
        programTaskModel.reset(self.__calculation_result.calculated_task.step,
                               self.__calculation_result.calculated_task.data)
        self.options: ProgramTaskCalculationResultDto = self.__calculation_result.options
        self.__programTaskByPicketModel = PicketPositionedTableModel(self.options.picket_direction,  self.options.start_picket.meters)
        self.__programTaskByPicketModel.setSourceModel(programTaskModel)
        self.position_multiplyer: int = self.options.picket_direction.multiplier()
        position_range: tuple[LocationVector1D, LocationVector1D] = programTaskModel.minmaxPosition()
        position_min: float = self.position_multiplyer * position_range[0].meters + self.options.start_picket.meters
        position_max: float = self.position_multiplyer * position_range[1].meters + self.options.start_picket.meters
        # #=============================================== Charts ===================================================
        charts_vbox = QVBoxLayout()
        #
        column_name = ['plan_fact','plan_prj']
        chart_value_range0: (float, float) = programTaskModel.minmaxValueByColumn(column_name[0])
        chart_value_range1: (float, float) = programTaskModel.minmaxValueByColumn(column_name[1])
        chart_value_range = (
                min(chart_value_range0[0], chart_value_range1[0]), max(chart_value_range0[1], chart_value_range1[1]))
        chart_value_range_length = chart_value_range[1] - chart_value_range[0]
        chart_value_min: float = chart_value_range[0] - 0.05 * chart_value_range_length
        chart_value_max: float = chart_value_range[1] + 0.05 * chart_value_range_length
        self.series0 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                         programTaskModel.modelColumnIndexAtName(column_name[0]),
                                         QCoreApplication.translate(
                                             'Lining trip/process/view/charts/program task', column_name[0]))
        self.series0.setPen(QPen(QColor("#2f8af0"), 2))
        self.series1 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                         programTaskModel.modelColumnIndexAtName(column_name[1]),
                                         QCoreApplication.translate(
                                             'Lining trip/process/view/charts/program task', column_name[1]))
        self.series1.setPen(QPen(QColor("red"), 2))
        vertical_chart_title = "Стрелы изгиба, мм"
        self.chart1 = HorizontalChart((position_min, position_max),
                                self.options.picket_direction == PicketDirection.Backward,
                                (chart_value_min, chart_value_max), False,
                                series0=[self.series0], series1=[self.series1],
                                x_tick=100,  y_tick=10,
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
        chart_value_min: float = chart_value_range[0] - 0.05 * chart_value_range_length
        chart_value_max: float = chart_value_range[1] + 0.05 * chart_value_range_length
        self.series2 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                         programTaskModel.modelColumnIndexAtName(column_name[0]),
                                         QCoreApplication.translate(
                                             'Lining trip/process/view/charts/program task', column_name[0]))
        self.series2.setPen(QPen(QColor("#2f8af0"), 2))
        self.chart2 = HorizontalChart((position_min, position_max),
                                      self.options.picket_direction == PicketDirection.Backward,
                                      (chart_value_min, chart_value_max), False,
                                      series0=[self.series2],
                                      x_tick=100, y_tick=10,
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
        column_name = ['vozv_fact', 'vozv_prj']
        chart_value_range0: (float, float) = programTaskModel.minmaxValueByColumn(column_name[0])
        chart_value_range1: (float, float) = programTaskModel.minmaxValueByColumn(column_name[1])
        chart_value_range = (
            min(chart_value_range0[0], chart_value_range1[0]), max(chart_value_range0[1], chart_value_range1[1]))
        chart_value_range_length = chart_value_range[1] - chart_value_range[0]
        chart_value_min: float = chart_value_range[0] - 0.05 * chart_value_range_length
        chart_value_max: float = chart_value_range[1] + 0.05 * chart_value_range_length
        self.series3 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                         programTaskModel.modelColumnIndexAtName(column_name[0]),
                                         QCoreApplication.translate(
                                             'Lining trip/process/view/charts/program task', column_name[0]))
        self.series4 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                         programTaskModel.modelColumnIndexAtName(column_name[1]),
                                         QCoreApplication.translate(
                                             'Lining trip/process/view/charts/program task', column_name[1]))
        self.series3.setPen(QPen(QColor("#2f8af0"), 2))
        self.series4.setPen(QPen(QColor("red"), 2))
        vertical_chart_title = "ВНР, мм"
        is_y_zero_axe_visible_value = True
        self.chart3 = HorizontalChart((position_min, position_max),
                                      self.options.picket_direction == PicketDirection.Backward,
                                      (chart_value_min, chart_value_max), False,
                                      series0=[self.series3], series1=[self.series4],
                                      x_tick=100, y_tick=10,
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
        column_name = ['prof_fact_left', 'prof_prj']
        chart_value_range0: (float, float) = programTaskModel.minmaxValueByColumn(column_name[0])
        chart_value_range1: (float, float) = programTaskModel.minmaxValueByColumn(column_name[1])
        chart_value_range = (
            min(chart_value_range0[0], chart_value_range1[0]), max(chart_value_range0[1], chart_value_range1[1]))
        chart_value_range_length = chart_value_range[1] - chart_value_range[0]
        chart_value_min: float = chart_value_range[0] - 0.05 * chart_value_range_length
        chart_value_max: float = chart_value_range[1] + 0.05 * chart_value_range_length
        self.series5 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                         programTaskModel.modelColumnIndexAtName(column_name[0]),
                                         QCoreApplication.translate(
                                             'Lining trip/process/view/charts/program task', column_name[0]))
        self.series6 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                         programTaskModel.modelColumnIndexAtName(column_name[1]),
                                         QCoreApplication.translate(
                                             'Lining trip/process/view/charts/program task', column_name[1]))
        self.series5.setPen(QPen(QColor("#2f8af0"), 2))
        self.series6.setPen(QPen(QColor("red"), 2))
        vertical_chart_title = "Стрелы, мм"
        is_y_zero_axe_visible_value = True
        self.chart4 = HorizontalChart((position_min, position_max),
                                      self.options.picket_direction == PicketDirection.Backward,
                                      (chart_value_min, chart_value_max), False,
                                      series0=[self.series5], series1=[self.series6],
                                      x_tick=100, y_tick=10,
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
        chart_value_min: float = chart_value_range[0] - 0.05 * chart_value_range_length
        chart_value_max: float = chart_value_range[1] + 0.05 * chart_value_range_length
        self.series7 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                         programTaskModel.modelColumnIndexAtName(column_name[0]),
                                         QCoreApplication.translate(
                                             'Lining trip/process/view/charts/program task', column_name[0]))
        self.series7.setPen(QPen(QColor("#2f8af0"), 2))
        self.chart5 = HorizontalChart((position_min, position_max),
                                      self.options.picket_direction == PicketDirection.Backward,
                                      (chart_value_min, chart_value_max), False,
                                      series0=[self.series7],
                                      x_tick=100, y_tick=10,
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

        #===================================================================================
        grid_widget = QWidget()
        grid = QGridLayout()
        grid_widget.setLayout(grid)
        infopanel_first = InfopanelFirst(self.__calculation_result)
        infopanel_second = InfopanelSecond(self.__calculation_result)
        grid.addWidget(infopanel_first, 0, 0, 1, 7)
        grid.addWidget(infopanel_second, 1, 0, 1, 7)
        grid.addLayout(charts_vbox, 2, 1, 7, 1)
        self.lcw = self.__leftColumnWidget()
        grid.addLayout(self.lcw, 2, 0, 7, 1)
        self.setFocus()
        self.setLayout(grid)

    def __warningMessage(self):
        msg = QMessageBox(self)
        msg.setText("Ответственность за применение \n изменённого программного задания \n лежит на операторе рихтовочной машины.")
        msg.setStyleSheet("background-color: #f80606;")
        msg.setWindowTitle("Предупреждение!")
        buttonAccept = msg.addButton("Ok", QMessageBox.YesRole)
        msg.exec()

     # Игорь
    def rerenderCharts(self, model:TrackProjectModel):
        if 'plan_prj' in model.data.columns and len(model.data['plan_prj'].dropna()) > 0:
            self.rerenderPlanCharts(model)
            self.rerenderLevelCharts(model)
        if 'prof_prj' in model.data.columns and len(model.data['prof_prj'].dropna()) > 0:
            self.rerenderProfileCharts(model)

    # перерисовка графиков Плана
    def rerenderPlanCharts(self, model:TrackProjectModel):
        self.series1.clear()
        self.series2.clear()
        new_plan_model = model
        startPicket = self.options.start_picket.meters
        scale = 6
        for i in range(0, new_plan_model.data.shape[0], 1):
            if i % scale == 0:
                self.series1.append(startPicket, new_plan_model.data.loc[:, 'plan_prj'][i])
            self.series2.append(startPicket, new_plan_model.data.loc[:, 'plan_delta'][i])
            startPicket += self.__calculation_result.base.step.meters * self.position_multiplyer
        self.chart_view1.update()
        self.chart_view2.update()
        #
        chart1Min = min(0, new_plan_model.data.loc[:, 'plan_prj'].min(),
                        new_plan_model.data.loc[:, 'plan_fact'].min())
        chart1Max = max(0, new_plan_model.data.loc[:, 'plan_prj'].max(),
                        new_plan_model.data.loc[:, 'plan_fact'].max())
        chart1Padding = (chart1Max - chart1Min) * 0.05
        self.chart_view1.chart().axisY().setRange(chart1Min - chart1Padding, chart1Max + chart1Padding)
        y_tick1 = self.set_axis_ticks_step(round(math.fabs((chart1Min - chart1Padding) - (chart1Max + chart1Padding))))
        if type(y_tick1) == float:
            self.chart_view1.chart().axisY().setLabelFormat("%2g")
        else:
            self.chart_view1.chart().axisY().setLabelFormat("%d")
        self.chart_view1.chart().axisY().setTickInterval(y_tick1)
        #
        chart2Min = min(0, new_plan_model.data.loc[:, 'plan_delta'].min())
        chart2Max = max(0, new_plan_model.data.loc[:, 'plan_delta'].max())
        chart2Padding = (chart2Max - chart2Min) * 0.05
        self.chart_view2.chart().axisY().setRange(chart2Min - chart2Padding, chart2Max + chart2Padding)
        y_tick2 = self.set_axis_ticks_step(round(math.fabs((chart2Min - chart2Padding) - (chart2Max + chart2Padding))))
        if type(y_tick2) == float:
            self.chart_view2.chart().axisY().setLabelFormat("%2g")
        else:
            self.chart_view2.chart().axisY().setLabelFormat("%d")
        self.chart_view2.chart().axisY().setTickInterval(y_tick2)
        #
        self.update_plan(model)

    # перерисовка графиков ВНР
    def rerenderLevelCharts(self, model:TrackProjectModel):
        self.series4.clear()
        new_plan_model = model
        startPicket = self.options.start_picket.meters
        scale = 6
        for i in range(0, new_plan_model.data.shape[0], 1):
            if i % scale == 0:
                self.series4.append(startPicket, new_plan_model.data.loc[:, 'vozv_prj'][i])
            startPicket += self.__calculation_result.base.step.meters * self.position_multiplyer
        self.chart_view3.update()
        chart1Min = min(0, new_plan_model.data.loc[:, 'vozv_prj'].min(), new_plan_model.data.loc[:, 'vozv_fact'].min())
        chart1Max = max(0, new_plan_model.data.loc[:, 'vozv_prj'].max(), new_plan_model.data.loc[:, 'vozv_fact'].max())
        chart1Padding = (chart1Max - chart1Min) * 0.05
        self.chart_view3.chart().axisY().setRange(chart1Min - chart1Padding, chart1Max + chart1Padding)
        y_tick1 = self.set_axis_ticks_step(round(math.fabs((chart1Min - chart1Padding) - (chart1Max + chart1Padding))))
        if type(y_tick1) == float:
            self.chart_view3.chart().axisY().setLabelFormat("%2g")
        else:
            self.chart_view3.chart().axisY().setLabelFormat("%d")
        self.chart_view3.chart().axisY().setTickInterval(y_tick1)
        #
        self.update_level(model)

    # перерисовка графиков Profile
    def rerenderProfileCharts(self, model: TrackProjectModel):
        self.series6.clear()
        self.series7.clear()
        new_plan_model = model
        startPicket = self.options.start_picket.meters
        scale = 6
        for i in range(0, new_plan_model.data.shape[0], 1):
            if i % scale == 0:
                self.series6.append(startPicket, new_plan_model.data.loc[:, 'prof_prj'][i])
                self.series7.append(startPicket, new_plan_model.data.loc[:, 'prof_delta'][i])
            startPicket += self.__calculation_result.base.step.meters  * self.position_multiplyer                                                           #       !
        self.chart_view4.update()
        self.chart_view5.update()
        #
        chart1Min = min(0, new_plan_model.data.loc[:, 'prof_prj'].min(),
                        new_plan_model.data.loc[:, 'prof_fact'].min())
        chart1Max = max(0, new_plan_model.data.loc[:, 'prof_prj'].max(),
                        new_plan_model.data.loc[:, 'prof_fact'].max())
        chart1Padding = (chart1Max - chart1Min) * 0.05
        self.chart_view4.chart().axisY().setRange(chart1Min - chart1Padding, chart1Max + chart1Padding)
        y_tick1 = self.set_axis_ticks_step(round(math.fabs((chart1Min - chart1Padding) - (chart1Max + chart1Padding))))
        if type(y_tick1) == float:
            self.chart_view4.chart().axisY().setLabelFormat("%2g")
        else:
            self.chart_view4.chart().axisY().setLabelFormat("%d")
        self.chart_view4.chart().axisY().setTickInterval(y_tick1)
        #
        chart2Min = min(0, new_plan_model.data.loc[:, 'prof_delta'].min())
        chart2Max = max(0, new_plan_model.data.loc[:, 'prof_delta'].max())
        chart2Padding = (chart2Max - chart2Min) * 0.05
        self.chart_view5.chart().axisY().setRange(chart2Min - chart2Padding, chart2Max + chart2Padding)
        y_tick2 = self.set_axis_ticks_step(round(math.fabs((chart2Min - chart2Padding) - (chart2Max + chart2Padding))))
        if type(y_tick2) == float:
            self.chart_view5.chart().axisY().setLabelFormat("%2g")
        else:
            self.chart_view5.chart().axisY().setLabelFormat("%d")
        self.chart_view5.chart().axisY().setTickInterval(y_tick2)
        #
        self.update_profile(model)

    def update_plan(self, plan: TrackProjectModel):
        # Базовое программное задание
        # В базовом программном задании устанавливаем новый план (из переустройства)
        # Профиль копируем из исходного.
        base = ProgramTaskBaseData(
            measurements_processed=self.__calculation_result.base.measurements_processed,
            detailed_restrictions=self.__calculation_result.base.detailed_restrictions,
            plan=plan.data,
            prof=self.__calculation_result.base.prof,
            alc_plan=None,
            alc_level=None,
            track_split_plan=plan.track_split,
            track_split_prof=self.__calculation_result.base.track_split_prof,
            step=self.__calculation_result.base.step
        )
        self.__calculation_result = ProgramTaskCalculationResultDto(
            options=self.options,
            base=base,
            calculated_task=machine_task_from_base_data_new(base),
            # Пересчитываем машинное программное задание из базового
            summary=base.track_split_plan)
        self.updateCalculationResultSignal.emit(self.__calculation_result)

    def update_level(self, level: TrackProjectModel):
        self.update_plan(level)
        self.updateCalculationResultSignal.emit(self.__calculation_result)

    def update_profile(self, prof: TrackProjectModel):
        base = ProgramTaskBaseData(
            measurements_processed=self.__calculation_result.base.measurements_processed,
            detailed_restrictions=self.__calculation_result.base.detailed_restrictions,
            plan=self.__calculation_result.base.plan,
            prof=prof.data,
            alc_plan=None,
            alc_level=None,
            track_split_plan=self.__calculation_result.base.track_split_plan,
            track_split_prof=prof.track_split,
            step=self.__calculation_result.base.step
        )
        self.__calculation_result = ProgramTaskCalculationResultDto(
            options=self.options,
            base=base,
            calculated_task=machine_task_from_base_data_new(base),
            summary=base.track_split_plan)
        self.updateCalculationResultSignal.emit(self.__calculation_result)


    # количество тиков на оси в зависимости от диапазона (position)
    def set_axis_ticks_step(self, position):
        y_tick = 1
        if 0 < position < 0.5:
            y_tick = 0.1
        elif 0.5 < position < 1:
            y_tick = 0.2
        elif 1 < position < 5:
            y_tick = 1
        elif 5 < position < 10:
            y_tick = 2
        elif 10 < position < 50:
            y_tick = 10
        elif 50 < position < 100:
            y_tick = 20
        elif 100 < position < 500:
            y_tick = 100
        elif 500 < position < 1000:
            y_tick = 200
        elif 1000 < position < 5000:
            y_tick = 1000
        elif 5000 < position < 10000:
            y_tick = 2000
        elif 10000 < position < 50000:
            y_tick = 10000
        elif 50000 < position < 100000:
            y_tick = 20000
        elif 100000 < position:
            y_tick = 50000
        if (position / y_tick) < 2:
            y_tick = (y_tick / 2)
        return y_tick


    def __saveResult(self):
        preffered_name: str = f'{self.options.measuring_trip.options.track_title}__{QDateTime.currentDateTime().toString("dd_MM_yyyy_hh_mm")}.apt'
        saveFile = QFileDialog.getSaveFileName(self, QCoreApplication.translate('Program task calculation/success/view',
                                                                                'Select save program task file'),
                                               preffered_name, '*.apt')[0]
        if saveFile is None or len(saveFile) == 0:
            return
        elif not saveFile.endswith('.apt'):
            saveFile += '.apt'
        try:
            ProgramTaskCalculationResultDto_to_archive(zipfile.ZipFile(saveFile, 'w'), self.__calculation_result)
        except Exception as error:
            QMessageBox.critical(self,
                                 QCoreApplication.translate('Program task calculation/success/view', 'Saving error'),
                                 str(error))
            os.remove(saveFile)


    def __escapeView(self):
        if QMessageBox.question(self, QCoreApplication.translate('Program task calculation/success/finish message box', 'Quit'),
        QCoreApplication.translate('Program task calculation/success/finish message box', 'Do you really want to go out?')) == QMessageBox.StandardButton.No:
            return
        self.__state.finish.emit()


    def __leftColumnWidget(self):
        vbox = QVBoxLayout()
        groupbox_top = QGroupBox()
        groupbox_top_vlayout = QVBoxLayout()
        groupbox_top.setLayout(groupbox_top_vlayout)
        self.plan_button = QPushButton("План")
        self.plan_button.setProperty("optionsWindowPushButton", True)
        self.plan_button.setFixedWidth(100)
        self.plan_button.setStyleSheet(focus_style)
        self.level_button = QPushButton("Уровень")
        self.level_button.setProperty("optionsWindowPushButton", True)
        self.level_button.setFixedWidth(100)
        self.level_button.setStyleSheet(focus_style)
        self.profile_button = QPushButton("Профиль")
        self.profile_button.setProperty("optionsWindowPushButton", True)
        self.profile_button.setFixedWidth(100)
        self.profile_button.setStyleSheet(focus_style)
        self.plan_button.clicked.connect(self.__plan_button)
        self.level_button.clicked.connect(self.__level_button)
        self.profile_button.clicked.connect(self.__profile_button)
        self.plan_green, self.plan_yellow, self.plan_red = True, False, False
        self.level_green, self.level_yellow, self.level_red = True, False, False
        self.profile_green, self.profile_yellow, self.profile_re = True, False, False
        groupbox_top_hlayout1 = QHBoxLayout()
        groupbox_top_hlayout2 = QHBoxLayout()
        groupbox_top_hlayout3 = QHBoxLayout()
        self.img1 = QLabel(self)
        # if self.plan_green:
        #     self.pixmap1 = QPixmap('./Data/green_narrow1')
        # elif self.plan_yellow:
        #     self.pixmap1 = QPixmap('./Data/yellow_narrow1')
        # elif self.plan_red:
        #     self.pixmap1 = QPixmap('./Data/red_narrow1')
        #
        self.abs_path = os.path.dirname(os.path.abspath(__file__))
        #
        self.img1 = QLabel(self)
        self.pixmap1 = QPixmap(os.path.join(self.abs_path, 'Data/green_narrow1.png'))
        self.img1.setPixmap(self.pixmap1)
        img2 = QLabel(self)
        pixmap2 = QPixmap(os.path.join(self.abs_path, 'Data/green_narrow2.png'))
        img2.setPixmap(pixmap2)
        img3 = QLabel(self)
        pixmap3 = QPixmap(os.path.join(self.abs_path, 'Data/green_narrow3.png'))
        img3.setPixmap(pixmap3)
        groupbox_top_hlayout1.addWidget(self.img1)
        groupbox_top_hlayout1.addWidget(self.plan_button)
        groupbox_top_hlayout2.addWidget(img2)
        groupbox_top_hlayout2.addWidget(self.level_button)
        groupbox_top_hlayout3.addWidget(img3)
        groupbox_top_hlayout3.addWidget(self.profile_button)
        groupbox_top_vlayout.addLayout(groupbox_top_hlayout1)
        groupbox_top_vlayout.addLayout(groupbox_top_hlayout2)
        groupbox_top_vlayout.addLayout(groupbox_top_hlayout3)
        self.results_button = QPushButton("Результаты")
        self.results_button.setStyleSheet(focus_style)
        self.settings_button = QPushButton("Установки")
        self.settings_button.setStyleSheet(focus_style)
        self.print_button = QPushButton("Печать")
        self.print_button.setStyleSheet(focus_style)
        self.save_button = QPushButton("Сохранить")
        self.save_button.setProperty("optionsWindowPushButton", True)
        self.save_button.setStyleSheet(focus_style)
        self.escape_button = QPushButton("Выход (ESC)")
        self.escape_button.setProperty("optionsWindowPushButton", True)
        self.escape_button.setStyleSheet(focus_style)
        self.results_button.clicked.connect(self.__results_button)
        self.settings_button.clicked.connect(self.__settings_button)
        self.print_button.clicked.connect(self.__print_button)
        self.save_button.clicked.connect(self.__saveResult)
        self.escape_button.clicked.connect(self.__escapeView)
        #
        groupbox_left_bottom = QGroupBox()
        groupbox_left_bottom_layout = QVBoxLayout()
        groupbox_left_bottom.setLayout(groupbox_left_bottom_layout)
        groupbox_left_bottom_layout_hbox1 = QHBoxLayout()
        fact_label = QLabel("Пикетаж")
        groupbox_left_bottom_layout_hbox1.addWidget(fact_label)
        groupbox_left_bottom_layout_hbox2 = QHBoxLayout()
        km_value_label = QLabel("")
        km_value_label.setStyleSheet("font-size:10pt; color:white; background-color:black")
        km_label = QLabel("КМ")
        m_value_label = QLabel("")
        m_value_label.setStyleSheet("font-size:10pt; color:white; background-color:black")
        m_label = QLabel("М")
        groupbox_left_bottom_layout_hbox2.addWidget(km_value_label)
        groupbox_left_bottom_layout_hbox2.addWidget(km_label)
        groupbox_left_bottom_layout_hbox2.addWidget(m_value_label)
        groupbox_left_bottom_layout_hbox2.addWidget(m_label)
        groupbox_left_bottom_layout_hbox3 = QHBoxLayout()
        scale_label = QLabel("Масштаб")
        scale_value_label = QLabel("1")
        scale_value_label.setStyleSheet("font-size:10pt; color:white; background-color:black")
        groupbox_left_bottom_layout_hbox3.addWidget(scale_label)
        groupbox_left_bottom_layout_hbox3.addWidget(scale_value_label)
        groupbox_left_bottom_layout.addLayout(groupbox_left_bottom_layout_hbox1)
        groupbox_left_bottom_layout.addLayout(groupbox_left_bottom_layout_hbox2)
        groupbox_left_bottom_layout.addLayout(groupbox_left_bottom_layout_hbox3)
        # список для хранения кнопок, нужен для изменения цвета нажатой кнопки
        self.buttons = []
        self.buttons.append(self.print_button)
        self.buttons.append(self.plan_button)
        self.buttons.append(self.profile_button)
        self.buttons.append(self.results_button)
        self.buttons.append(self.settings_button)
        self.buttons.append(self.save_button)
        self.buttons.append(self.escape_button)
        self.buttons.append(self.level_button)
        #
        vbox.addWidget(groupbox_top)
        #vbox.addStretch(1)
        #vbox.addWidget(self.results_button)
        #vbox.addStretch(1)
        #vbox.addWidget(self.settings_button)
        #vbox.addStretch(1)
        #vbox.addWidget(self.print_button)
        vbox.addStretch(5)
        vbox.addWidget(self.save_button)
        vbox.addWidget(self.escape_button)
        #vbox.addWidget(groupbox_left_bottom)                    # Не показываем блок Масштаб + км, м
        vbox.addStretch(1)
        return vbox

        # ============================ Меняем цвет бирюлек + добавляем окно на график ===============================================

    def keyPressEvent(self, keyEvent):
            key = keyEvent.key()
            if key == Qt.Key_Z:
                # self.pixmap1 = QPixmap('./Data/yellow_narrow1')
                self.pixmap1 = QPixmap(os.path.join(self.abs_path, 'Data/yellow_narrow1.png'))
                self.img1.setPixmap(self.pixmap1)
                self.plan_red = False
                self.plan_yellow = True
                self.plan_green = False
            elif key == Qt.Key_X:
                # self.pixmap1 = QPixmap('./Data/red_narrow1')
                self.pixmap1 = QPixmap(os.path.join(self.abs_path, 'Data/red_narrow1.png'))
                self.img1.setPixmap(self.pixmap1)
                self.plan_red = True
                self.plan_yellow = False
                self.plan_green = False
            elif key == Qt.Key_C:
                self.pixmap1 = QPixmap(os.path.join(self.abs_path, 'Data/green_narrow1.png'))
                # self.pixmap1 = QPixmap('./Data/green_narrow1')
                self.img1.setPixmap(self.pixmap1)
                self.plan_red = False
                self.plan_yellow = False
                self.plan_green = True
            elif key == Qt.Key.Key_Escape:
                self.__escapeView()

    # ======================= кнопки ==================================
    def __plan_button(self):
        self.openPlanSignal.emit('open')

    def __level_button(self):
        self.openLevelSignal.emit('open')

    def __profile_button(self):
        self.openProfileSignal.emit('open')

    def __results_button(self):
        pass

    def __settings_button(self):
        pass

    def __print_button(self):
        pass

    def __escape_button(self):
        pass
