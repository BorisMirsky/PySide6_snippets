
from PySide6.QtWidgets import (QWidget, QListWidget, QVBoxLayout, QApplication,QPushButton,QSpinBox,QComboBox,QStackedLayout,
                               QHBoxLayout, QGridLayout, QLabel, QFileDialog,QMessageBox, QGroupBox)
from PySide6.QtGui import QFont, QIcon, QShortcut, Qt, QPen, QPainter, QImage, QPixmap, QColor, QBrush
from PySide6.QtCharts import QChartView, QLineSeries, QAreaSeries, QVXYModelMapper
from PySide6.QtCore import Qt, QTimer, QDateTime, QCoreApplication, QPointF, QMargins, Signal, QObject, QEvent
import sys
from domain.dto.Travelling import PicketDirection, LocationVector1D
from operating.states.program_task_calculation.ProgramTaskCalculationState import ProgramTaskCalculationSuccessState
from domain.models.AbstractPositionedTableModel import AbstractPositionedTableModel
from domain.calculations.plan_model import TrackProjectModel, TrackProjectType
from domain.dto.Workflow import ProgramTaskCalculationResultDto
from presentation.models.PicketPositionedTableModel import PicketPositionedTableModel
from domain.models.StepIndexedDataFramePositionedModel import StepIndexedDataFramePositionedModel, \
    ReducedStepIndexedPositionedModel
from presentation.ui.gui.common.viewes.TableDataChartsView import DynamicLineSeries, HorizontalChart
from ....viewes.Infopanel import InfopanelFirst, InfopanelSecond
from domain.models.VerticalLineModel import VerticalLineModel
from ..Speed.LevelSpeedWindow import SpeedMainWidget
#from .....common.viewes.CircliBusyIndicator import CircliBusyIndicator
from ..Reconstruction.LevelReconstructionWindow import LevelReconstructionWidget
from presentation.ui.gui.common.viewes.LabelOnChart import LabelOnParent2
from presentation.ui.gui.common.elements.Base import setWindowTitle
from presentation.ui.gui.common.viewes.WindowTitle import  Window

import math
import pandas



focus_style = "QWidget:focus { border: 3px solid #FF0000; border-radius: 5px; background-color: white}"


class LevelView(QWidget):
    def __init__(self, calculation_result:ProgramTaskCalculationResultDto,
                 parent: QWidget = None,
                 window: Window = None):
        super().__init__(parent)
        self.__calculation_result = calculation_result
        self.__currentView: QWidget = None
        self.__layout: QStackedLayout = QStackedLayout()
        self.__layout.setStackingMode(QStackedLayout.StackingMode.StackOne)
        self.__window = window
        self.setLayout(self.__layout)
        #
        self.levelMain = LevelMainWidget(self.__calculation_result)
        self.__openLevelMain()
        self.setLayout(self.__layout)

    def __clearCurrentView(self):
        if self.__currentView: # is not None
            self.__currentView = None

    def update_calculation_result(self, data):
        self.__calculation_result = data

    def __openLevelMain(self):
        self.__clearCurrentView()
        self.__currentView = self.levelMain
        self.__currentView.openLevelReconstructionSignal.connect(self.__openLevelReconstruction)
        # self.__currentView.openPlanShiftsSignal.connect(self.__openPlanShifts)
        self.__layout.addWidget(self.__currentView)
        self.__layout.setCurrentWidget(self.__currentView)
        #setWindowTitle(self, "ВНР")
        self.__window.setTitle("ВНР")

    def __openLevelReconstruction(self):
        self.__clearCurrentView()
        self.__currentView = LevelReconstructionWidget(self.__calculation_result)
        self.__currentView.closeLevelReconstructionSignal.connect(self.__openLevelMain)
        self.__currentView.passDataSignal.connect(self.levelMain.rerenderCharts)
        self.__currentView.updateCalculationResultSignal.connect(self.update_calculation_result)
        self.__layout.addWidget(self.__currentView)
        self.__layout.setCurrentWidget(self.__currentView)
        #setWindowTitle(self, "ВНР > Переустройство")
        self.__window.setTitle("ВНР > Переустройство")

    # def __openPlanLevelSpeed(self):
    #     self.__clearCurrentView()
    #     self.__currentView = SpeedMainWidget(self.__state)
    #     self.__currentView.closeLevelSpeedSignal.connect(self.__openLevelMain)
    #     self.__currentView.passDataSignal.connect(self.levelMain.rerenderCharts)
    #     self.__layout.addWidget(self.__currentView)
    #     self.__layout.setCurrentWidget(self.__currentView)


class LevelMainWidget(QWidget):
    passDataSignal = Signal(TrackProjectModel)
    levelMainSignal = Signal(str)                      # close this view
    openLevelReconstructionSignal = Signal(int)
    openLevelSpeedSignal = Signal(int)
    updateCalculationResultSignal = Signal(ProgramTaskCalculationResultDto)
    skip_coefficient = 0.002

    def __init__(self, calculation_result:ProgramTaskCalculationResultDto,
                 #state: ProgramTaskCalculationSuccessState,
                 parent: QWidget = None):
        super().__init__(parent)
        #self.__state = state
        self.__calculation_result = calculation_result
        # self.programTaskModel: AbstractPositionedTableModel = StepIndexedDataFramePositionedModel(self.__calculation_result.calculated_task.data.columns, self.__calculation_result.calculated_task.step, self)
        # self.programTaskModel.reset(self.__calculation_result.calculated_task.step, self.__calculation_result.calculated_task.data)
        self.programTaskModel = ReducedStepIndexedPositionedModel(
            step=self.__calculation_result.calculated_task.step,
            data=self.__calculation_result.calculated_task.data,
            parent=self,
        )
        self.options: ProgramTaskCalculationResultDto = self.__calculation_result.options
        self.__programTaskByPicketModel = PicketPositionedTableModel(self.options.picket_direction, self.options.start_picket.meters)
        self.__programTaskByPicketModel.setSourceModel(self.programTaskModel)
        self.position_multiplyer: int = self.options.picket_direction.multiplier()
        position_range: tuple[LocationVector1D, LocationVector1D] = self.programTaskModel.minmaxPosition()
        self.position_min: float = self.position_multiplyer * position_range[0].meters + self.options.start_picket.meters
        self.position_max: float = self.position_multiplyer * position_range[1].meters + self.options.start_picket.meters
        rangeX: tuple[float, float] = (self.position_min, self.position_max)
        #self.plan_model = TrackPlanProjectModel(self.__state.calculation_result().base.track_split_plan,
        #                                        self.__state.calculation_result().base.plan)
        self.plan_model = TrackProjectModel.create(TrackProjectType.Level, self.__calculation_result)
        self.zoomFactor = 10
        self.zoomValue = 0
        self.motion_step = 1
        #
        self.counter = 0
        self.updatedData: TrackProjectModel = None
        self.startPicket = self.__calculation_result.options.start_picket.meters
        self.currentPicket = self.__calculation_result.options.start_picket.meters
        self.model = VerticalLineModel(self.options.start_picket.meters, rangeX, accValue=True)
        #
        self.corrections_max, self.corrections_min = None, None
        self.__prof_delta_values(self.__calculation_result.calculated_task.data['vozv_delta'])
        #
        grid = QGridLayout()
        infopanel_first = InfopanelFirst(self.__calculation_result)
        infopanel_second = InfopanelSecond(self.__calculation_result)
        #title_window = LabelOnParent2('ВНР. Главная', 500, 0, 250, 40, infopanel_first)
        #title_window.setWordWrap(True)
        #title_window.setStyleSheet("background-color:yellow;border:1px solid black;padding:5px;")
        grid.addWidget(infopanel_first, 0, 0, 1, 10)
        grid.addWidget(infopanel_second, 1, 0, 1, 10)
        #
        # #=============================================== Charts ===================================================
        self.vertical_line_series1 = QLineSeries()
        self.vertical_line_series1.setPen(QPen(Qt.GlobalColor.magenta, 2))
        self.lineMapper1 = QVXYModelMapper(self)
        self.lineMapper1.setXColumn(0)
        self.lineMapper1.setYColumn(1)
        self.lineMapper1.setSeries(self.vertical_line_series1)
        self.lineMapper1.setModel(self.model)
        #
        self.vertical_line_series2 = QLineSeries()
        self.vertical_line_series2.setPen(QPen(Qt.GlobalColor.magenta, 2))
        self.lineMapper2 = QVXYModelMapper(self)
        self.lineMapper2.setXColumn(0)
        self.lineMapper2.setYColumn(1)
        self.lineMapper2.setSeries(self.vertical_line_series2)
        self.lineMapper2.setModel(self.model)
        #
        self.vertical_line_series3 = QLineSeries()
        self.vertical_line_series3.setPen(QPen(Qt.GlobalColor.magenta, 2))
        self.lineMapper3 = QVXYModelMapper(self)
        self.lineMapper3.setXColumn(0)
        self.lineMapper3.setYColumn(1)
        self.lineMapper3.setSeries(self.vertical_line_series3)
        self.lineMapper3.setModel(self.model)
        #
        self.vertical_line_series4 = QLineSeries()
        self.vertical_line_series4.setPen(QPen(Qt.GlobalColor.magenta, 2))
        self.lineMapper4 = QVXYModelMapper(self)
        self.lineMapper4.setXColumn(0)
        self.lineMapper4.setYColumn(1)
        self.lineMapper4.setSeries(self.vertical_line_series4)
        self.lineMapper4.setModel(self.model)
        #
        self.vertical_line_series5 = QLineSeries()
        self.vertical_line_series5.setPen(QPen(Qt.GlobalColor.magenta, 2))
        self.lineMapper5 = QVXYModelMapper(self)
        self.lineMapper5.setXColumn(0)
        self.lineMapper5.setYColumn(1)
        self.lineMapper5.setSeries(self.vertical_line_series5)
        self.lineMapper5.setModel(self.model)

        ################################################################################################
        charts_vbox = QVBoxLayout()
        column_name = ['vozv_fact', 'vozv_prj']
        chart_value_range0: (float, float) = self.programTaskModel.minmaxValueByColumn(column_name[0])
        chart_value_range1: (float, float) = self.programTaskModel.minmaxValueByColumn(column_name[1])
        chart_value_range = (
        min(chart_value_range0[0], chart_value_range1[0]), max(chart_value_range0[1], chart_value_range1[1]))
        chart_value_range_length = chart_value_range[1] - chart_value_range[0]
        chart_value_min: float = chart_value_range[0] - 0.05 * chart_value_range_length
        chart_value_max: float = chart_value_range[1] + 0.05 * chart_value_range_length
        self.series0 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                         self.programTaskModel.modelColumnIndexAtName(column_name[0]),
                                         QCoreApplication.translate(
                                             'Lining trip/process/view/charts/program task', column_name[0]))
        self.series1 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                         self.programTaskModel.modelColumnIndexAtName(column_name[1]),
                                         QCoreApplication.translate(
                                             'Lining trip/process/view/charts/program task', column_name[1]))
        self.series0.setPen(QPen(QColor("#2f8af0"), 2))
        self.series1.setPen(QPen(QColor("red"), 2))
        self.chart1 = HorizontalChart((self.position_min, self.position_max),
                                      self.options.picket_direction == PicketDirection.Backward,
                                      (chart_value_min, chart_value_max), False,
                                      series0=[self.series0], series1=[self.series1],
                                      x_tick=100,  y_tick=10,
                                      title="Уровень, мм",
                                      xMinorTickCount=9, yMinorTickCount=1,
                                      xGridLineColor="gray", yGridLineColor="gray",
                                      xMinorGridLineColor="gray", yMinorGridLineColor="gray",
                                      levelBoundaryLine1='pass', levelBoundaryLine2='pass')
        self.chart1.legend().hide()
        self.chart1.layout().setContentsMargins(0, 0, 0, 0)
        self.chart1.setMargins(QMargins(0, 0, 0, 0))
        self.chart1.axes(Qt.Orientation.Horizontal)[0].setGridLineVisible(True)
        self.chart1.axes(Qt.Orientation.Vertical)[0].setGridLineVisible(True)
        self.chart1.addSeries(self.vertical_line_series1)
        self.vertical_line_series1.attachAxis(self.chart1.axisX())
        self.vertical_line_series1.attachAxis(self.chart1.axisY())
        self.chart_view1 = QChartView(self.chart1)
        self.chart_view1.chart().setBackgroundBrush(QBrush("black"))
        self.chart_view1.setRenderHint(QPainter.Antialiasing)
        self.chart_view1.setFocusPolicy(Qt.NoFocus)
        charts_vbox.addWidget(self.chart_view1, 2)

        column_name = ['vozv_delta']
        chart_value_range: (float, float) = self.programTaskModel.minmaxValueByColumn(column_name[0])
        chart_value_range_length = chart_value_range[1] - chart_value_range[0]
        chart_value_min: float = chart_value_range[0] - 0.05 * chart_value_range_length
        chart_value_max: float = chart_value_range[1] + 0.05 * chart_value_range_length
        self.series3 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                         self.programTaskModel.modelColumnIndexAtName(column_name[0]),
                                         QCoreApplication.translate(
                                             'Lining trip/process/view/charts/program task', column_name[0]))
        self.series3.setPen(QPen(QColor("#2f8af0"), 2))
        self.chart2 = HorizontalChart((self.position_min, self.position_max),
                                      self.options.picket_direction == PicketDirection.Backward,
                                      (chart_value_min, chart_value_max), False,
                                      series0=[self.series3],
                                      x_tick=100, y_tick=10, title="Исправл., мм",
                                      xMinorTickCount=9, yMinorTickCount=1,
                                      xGridLineColor="gray", yGridLineColor="gray",
                                      xMinorGridLineColor="gray", yMinorGridLineColor="gray")
        self.chart2.legend().hide()
        self.chart2.layout().setContentsMargins(0, 0, 0, 0)
        self.chart2.setMargins(QMargins(0, 0, 0, 0))
        self.chart2.axes(Qt.Orientation.Horizontal)[0].setGridLineVisible(True)
        self.chart2.axes(Qt.Orientation.Vertical)[0].setGridLineVisible(True)
        self.chart2.addSeries(self.vertical_line_series2)
        self.vertical_line_series2.attachAxis(self.chart2.axisX())
        self.vertical_line_series2.attachAxis(self.chart2.axisY())
        self.chart_view2 = QChartView(self.chart2)
        self.chart_view2.chart().setBackgroundBrush(QBrush("black"))
        self.chart_view2.setRenderHint(QPainter.Antialiasing)
        self.chart_view2.setFocusPolicy(Qt.NoFocus)
        charts_vbox.addWidget(self.chart_view2, 1)

        column_name = ['a_nepog_fact', 'a_nepog_prj']
        chart_value_range0: (float, float) = self.programTaskModel.minmaxValueByColumn(column_name[0])
        chart_value_range1: (float, float) = self.programTaskModel.minmaxValueByColumn(column_name[1])
        chart_value_range = (min(chart_value_range0[0], chart_value_range1[0], 0.7, -0.7),
                             max(chart_value_range0[1], chart_value_range1[1], 0.7, -0.7))
        chart_value_range_length = chart_value_range[1] - chart_value_range[0]
        chart_value_min: float = chart_value_range[0] - 0.05 * chart_value_range_length
        chart_value_max: float = chart_value_range[1] + 0.05 * chart_value_range_length
        self.series4 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                         self.programTaskModel.modelColumnIndexAtName(column_name[0]),
                                         QCoreApplication.translate(
                                             'Lining trip/process/view/charts/program task', column_name[0]))
        self.series5 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                         self.programTaskModel.modelColumnIndexAtName(column_name[1]),
                                         QCoreApplication.translate(
                                             'Lining trip/process/view/charts/program task', column_name[1]))
        self.series4.setPen(QPen(QColor("#2f8af0"), 2))
        self.series5.setPen(QPen(QColor("red"), 2))
        self.chart3 = HorizontalChart((self.position_min, self.position_max),
                                      self.options.picket_direction == PicketDirection.Backward,
                                      (chart_value_min, chart_value_max), False,                                 # chart_value_max
                                      series0=[self.series4], series1=[self.series5],
                                      x_tick=100, y_tick=10, title='Анеп, м/с\u00B2',
                                      xMinorTickCount=9, yMinorTickCount=1,
                                      xGridLineColor="gray", yGridLineColor="gray",
                                      xMinorGridLineColor="gray", yMinorGridLineColor="gray",
                                      levelBoundaryLine1=0.7, levelBoundaryLine2=-0.7)
        self.chart3.legend().hide()
        self.chart3.layout().setContentsMargins(0, 0, 0, 0)
        self.chart3.setMargins(QMargins(0, 0, 0, 0))
        self.chart3.axes(Qt.Orientation.Horizontal)[0].setGridLineVisible(True)
        self.chart3.axes(Qt.Orientation.Vertical)[0].setGridLineVisible(True)
        self.chart3.addSeries(self.vertical_line_series3)
        self.vertical_line_series3.attachAxis(self.chart3.axisX())
        self.vertical_line_series3.attachAxis(self.chart3.axisY())
        self.chart_view3 = QChartView(self.chart3)
        self.chart_view3.chart().setBackgroundBrush(QBrush("black"))
        self.chart_view3.setRenderHint(QPainter.Antialiasing)
        self.chart_view3.setFocusPolicy(Qt.NoFocus)
        charts_vbox.addWidget(self.chart_view3, 1)

        column_name = ['psi_prj', 'psi_fact']
        chart_value_range0: (float, float) = self.programTaskModel.minmaxValueByColumn(column_name[0])
        chart_value_range1: (float, float) = self.programTaskModel.minmaxValueByColumn(column_name[1])
        chart_value_range = (
        min(chart_value_range0[0], chart_value_range1[0], 0.7), max(chart_value_range0[1], chart_value_range1[1], 0.7))
        chart_value_range_length = chart_value_range[1] - chart_value_range[0]
        chart_value_min: float = chart_value_range[0] - 0.05 * chart_value_range_length
        chart_value_max: float = chart_value_range[1] + 0.05 * chart_value_range_length
        self.series6 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                         self.programTaskModel.modelColumnIndexAtName(column_name[0]),
                                         QCoreApplication.translate(
                                             'Lining trip/process/view/charts/program task', column_name[0]))
        self.series7 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                         self.programTaskModel.modelColumnIndexAtName(column_name[1]),
                                         QCoreApplication.translate(
                                             'Lining trip/process/view/charts/program task', column_name[1]))
        self.series6.setPen(QPen(QColor("red"), 2))
        self.series7.setPen(QPen(QColor("#2f8af0"), 2))
        self.chart4 = HorizontalChart((self.position_min, self.position_max),
                                      self.options.picket_direction == PicketDirection.Backward,
                                      (chart_value_min, chart_value_max), False,
                                      series0=[self.series6], series1=[self.series7],
                                      x_tick=100, y_tick=10, title=(chr(936) + ' (Пси)' + ' м/c\u00B3'),
                                      xMinorTickCount=9, yMinorTickCount=1,
                                      xGridLineColor="gray", yGridLineColor="gray",
                                      xMinorGridLineColor="gray", yMinorGridLineColor="gray",
                                      levelBoundaryLine1=0.7, levelBoundaryLine2='pass')
        self.chart4.legend().hide()
        self.chart4.layout().setContentsMargins(0, 0, 0, 0)
        self.chart4.setMargins(QMargins(0, 0, 0, 0))
        self.chart4.axes(Qt.Orientation.Horizontal)[0].setGridLineVisible(True)
        self.chart4.axes(Qt.Orientation.Vertical)[0].setGridLineVisible(True)
        self.chart4.addSeries(self.vertical_line_series4)
        self.vertical_line_series4.attachAxis(self.chart4.axisX())
        self.vertical_line_series4.attachAxis(self.chart4.axisY())
        self.chart_view4 = QChartView(self.chart4)
        self.chart_view4.chart().setBackgroundBrush(QBrush("black"))
        self.chart_view4.setRenderHint(QPainter.Antialiasing)
        self.chart_view4.setFocusPolicy(Qt.NoFocus)
        charts_vbox.addWidget(self.chart_view4, 1)

        column_name = ['v_wheel_fact', 'v_wheel_prj']
        chart_value_range0: (float, float) = self.programTaskModel.minmaxValueByColumn(column_name[0])
        chart_value_range1: (float, float) = self.programTaskModel.minmaxValueByColumn(column_name[1])
        chart_value_range = (
        min(chart_value_range0[0], chart_value_range1[0], 35), max(chart_value_range0[1], chart_value_range1[1], 35))
        chart_value_range_length = chart_value_range[1] - chart_value_range[0]
        chart_value_min: float = chart_value_range[0] - 0.05 * chart_value_range_length
        chart_value_max: float = chart_value_range[1] + 0.05 * chart_value_range_length
        self.series8 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                         self.programTaskModel.modelColumnIndexAtName(column_name[0]),
                                         QCoreApplication.translate(
                                             'Lining trip/process/view/charts/program task', column_name[0]))
        self.series9 = DynamicLineSeries(self.__programTaskByPicketModel, 0,
                                         self.programTaskModel.modelColumnIndexAtName(column_name[1]),
                                         QCoreApplication.translate(
                                             'Lining trip/process/view/charts/program task', column_name[1]))
        self.series8.setPen(QPen(QColor("#2f8af0"), 2))
        self.series9.setPen(QPen(QColor("red"), 2))
        self.chart5 = HorizontalChart((self.position_min, self.position_max),
                                      self.options.picket_direction == PicketDirection.Backward,
                                      (chart_value_min, chart_value_max), False,
                                      series0=[self.series8], series1=[self.series9],
                                      x_tick=100, y_tick=10, title="Fv, мм/м",
                                      xMinorTickCount=9, yMinorTickCount=1,
                                      xGridLineColor="gray", yGridLineColor="gray",
                                      xMinorGridLineColor="gray", yMinorGridLineColor="gray",
                                      levelBoundaryLine1=35, levelBoundaryLine2='pass')
        self.chart5.legend().hide()
        self.chart5.layout().setContentsMargins(0, 0, 0, 0)
        self.chart5.setMargins(QMargins(0, 0, 0, 0))
        self.chart5.axes(Qt.Orientation.Horizontal)[0].setGridLineVisible(True)
        self.chart5.axes(Qt.Orientation.Vertical)[0].setGridLineVisible(True)
        self.chart5.addSeries(self.vertical_line_series5)
        self.vertical_line_series5.attachAxis(self.chart5.axisX())
        self.vertical_line_series5.attachAxis(self.chart5.axisY())
        self.chart_view5 = QChartView(self.chart5)
        self.chart_view5.chart().setBackgroundBrush(QBrush("black"))
        self.chart_view5.setRenderHint(QPainter.Antialiasing)
        self.chart_view5.setFocusPolicy(Qt.NoFocus)
        charts_vbox.addWidget(self.chart_view5, 1)
        self.installEventFilter(self)
        #=================================================================================
        grid.addLayout(charts_vbox, 2, 0, 8, 9)
        rcw = self.__rightColumnWidget()
        grid.addLayout(rcw, 2, 9, 8, 1)
        self.setWindowTitle("Calculation.Level.Main")
        self.setLayout(grid)
        self.setFocus()

    def rerenderCharts(self, data):
        self.updatedData = data
        self.series1.clear()
        self.series3.clear()
        self.series5.clear()
        self.series6.clear()
        self.series9.clear()
        self.new_plan_model = data
        self.new_plan_model.data['new_vozv_delta'] = self.new_plan_model.data.loc[:,'vozv_prj'] - self.new_plan_model.data.loc[:, 'vozv_fact']

        startPicket = self.options.start_picket.meters
        total_steps = self.new_plan_model.data.shape[0]
        skip = round(self.skip_coefficient * total_steps)
        for i in range(0, total_steps):
            if i % skip == 0:
                self.series1.append(startPicket, self.new_plan_model.data.loc[:, 'vozv_prj'][i])
                self.series3.append(startPicket, self.new_plan_model.data.loc[:, 'new_vozv_delta'][i])
                self.series5.append(startPicket, self.new_plan_model.data.loc[:, 'a_nepog_prj'][i])
                self.series6.append(startPicket, self.new_plan_model.data.loc[:, 'psi_prj'][i])
                self.series9.append(startPicket, self.new_plan_model.data.loc[:, 'v_wheel_prj'][i])
            startPicket += self.plan_model.step * self.position_multiplyer

        self.chart_view1.update()
        self.chart_view2.update()
        self.chart_view3.update()
        self.chart_view4.update()
        self.chart_view5.update()
        #
        chart1Min = min(0, self.new_plan_model.data.loc[:, 'vozv_prj'].min(),
                        self.new_plan_model.data.loc[:, 'vozv_fact'].min())
        chart1Max = max(0, self.new_plan_model.data.loc[:, 'vozv_prj'].max(),
                        self.new_plan_model.data.loc[:, 'vozv_fact'].max())
        chart1Padding = (chart1Max - chart1Min) * 0.05
        self.chart_view1.chart().axisY().setRange(chart1Min - chart1Padding, chart1Max + chart1Padding)
        y_tick1 = self.set_axis_ticks_step(math.fabs((chart1Min - chart1Padding) - (chart1Max + chart1Padding)))
        if type(y_tick1) == float:
            self.chart_view1.chart().axisY().setLabelFormat("%2g")
        else:
            self.chart_view1.chart().axisY().setLabelFormat("%d")
        self.chart_view1.chart().axisY().setTickInterval(y_tick1)
        #
        #
        chart2Min = min(0, self.new_plan_model.data.loc[:, 'new_vozv_delta'].min())
        chart2Max = max(0, self.new_plan_model.data.loc[:, 'new_vozv_delta'].max())
        chart2Padding = (chart2Max - chart2Min) * 0.05
        self.chart_view2.chart().axisY().setRange(chart2Min - chart2Padding, chart2Max + chart2Padding)
        y_tick2 = self.set_axis_ticks_step(math.fabs((chart2Min - chart2Padding) - (chart2Max + chart2Padding)))
        if type(y_tick2) == float:
            self.chart_view2.chart().axisY().setLabelFormat("%2g")
        else:
            self.chart_view2.chart().axisY().setLabelFormat("%d")
        self.chart_view2.chart().axisY().setTickInterval(y_tick2)
        #
        chart3Min = min(0, self.new_plan_model.data.loc[:, 'a_nepog_fact'].min(), 0.7, -0.7,
                        self.new_plan_model.data.loc[:, 'a_nepog_prj'].min())
        chart3Max = max(0, self.new_plan_model.data.loc[:, 'a_nepog_fact'].max(), 0.7, -0.7,
                        self.new_plan_model.data.loc[:, 'a_nepog_prj'].max())
        chart3Padding = (chart3Max - chart3Min) * 0.05
        self.chart_view3.chart().axisY().setRange(chart3Min - chart3Padding, chart3Max + chart3Padding)
        y_tick3 = self.set_axis_ticks_step(math.fabs((chart3Min - chart3Padding) - (chart3Max + chart3Padding)))
        #print('level main y_tick3 rerender ', y_tick3, math.fabs((chart3Min - chart3Padding) - (chart3Max + chart3Padding)), sep=', ')
        if type(y_tick3) == float:
            self.chart_view3.chart().axisY().setLabelFormat("%2g")
        else:
            self.chart_view3.chart().axisY().setLabelFormat("%d")
        self.chart_view3.chart().axisY().setTickInterval(y_tick3)
        self.chart_view3.chart().axisY().setRange(chart3Min - chart3Padding, chart3Max + chart3Padding)
        #
        chart4Min = min(0, self.new_plan_model.data.loc[:, 'psi_prj'].min(),
                        self.new_plan_model.data.loc[:, 'psi_fact'].min())
        chart4Max = max(0, self.new_plan_model.data.loc[:, 'psi_prj'].max(),
                        self.new_plan_model.data.loc[:, 'psi_fact'].max())
        chart4Padding = (chart4Max - chart4Min) * 0.05
        self.chart_view4.chart().axisY().setRange(chart4Min - chart4Padding, chart4Max + chart4Padding)
        y_tick4 = self.set_axis_ticks_step(math.fabs((chart4Min - chart4Padding) - (chart4Max + chart4Padding)))
        self.chart_view4.chart().axisY().setTickInterval(y_tick4)
        if type(y_tick4) == float:
            self.chart_view4.chart().axisY().setLabelFormat("%2g")
        else:
            self.chart_view4.chart().axisY().setLabelFormat("%d")
        #
        chart5Min = min(0, self.new_plan_model.data.loc[:, 'v_wheel_fact'].min(),
                        self.new_plan_model.data.loc[:, 'v_wheel_prj'].min())
        chart5Max = max(0, self.new_plan_model.data.loc[:, 'v_wheel_fact'].max(),
                        self.new_plan_model.data.loc[:, 'v_wheel_prj'].max())
        chart5Padding = (chart5Max - chart5Min) * 0.05
        self.chart_view5.chart().axisY().setRange(chart5Min - chart5Padding, chart5Max + chart5Padding)
        y_tick5 = self.set_axis_ticks_step(math.fabs((chart5Min - chart5Padding) - (chart5Max + chart5Padding)))
        self.chart_view5.chart().axisY().setTickInterval(y_tick5)
        if type(y_tick5) == float:
            self.chart_view5.chart().axisY().setLabelFormat("%2g")
        else:
            self.chart_view5.chart().axisY().setLabelFormat("%d")
        #
        min_max_corrections = self.__prof_delta_values(self.new_plan_model.data['new_vozv_delta'])
        self.corrections_min, self.corrections_max = min_max_corrections[0], min_max_corrections[1]
        self.corrections_min_value.setNum(round(self.corrections_min))
        self.corrections_max_value.setNum(round(self.corrections_max))


    # нахождение min & max Исправления
    def __prof_delta_values(self, datacolumn: pandas.Series):
        self.corrections_min = round(datacolumn.min())
        self.corrections_max = round(datacolumn.max())
        return (self.corrections_min, self.corrections_max)


    # количество тиков на оси в зависимости от диапазона
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
        elif 5000 < position:
            y_tick = 2000
        if (position / y_tick) < 2:
            y_tick = (y_tick / 2)
        return y_tick

    def eventFilter(self, watched: QObject, event: QEvent):
        if event.type() == QEvent.Type.Show:
            self.setFocus()
        if event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Left:
                self.model.shiftLine(self.position_multiplyer * self.motion_step * -1)
                self.__returnData(self.motion_step * -1)
            elif event.key() == Qt.Key.Key_Right:
                self.model.shiftLine(self.position_multiplyer * self.motion_step)
                self.__returnData(self.motion_step)
            elif event.key() == Qt.Key.Key_Escape:
                self.__escape_button()
        return False

    # установка значений в окна
    def __returnData(self, i:int):
        self.currentPicket += self.position_multiplyer * i
        idx = math.fabs(int((self.currentPicket -
                             self.__calculation_result.options.start_picket.meters) * self.position_multiplyer / self.plan_model.step))
        self.point_number_label_value.setNum(round(self.currentPicket))
        if self.updatedData:
            self.fact_label_value.setNum(round(self.updatedData.data['vozv_fact'][idx], 3))
            self.prj_label_value.setNum(round(self.updatedData.data['vozv_prj'][idx], 3))
            self.anep_label_value_fact.setNum(round(self.updatedData.data['a_nepog_fact'][idx], 3))
            self.psi_label_value_fact.setNum(round(self.updatedData.data['psi_fact'][idx], 3))
            self.fv_label_value_fact.setNum(round(self.updatedData.data['v_wheel_fact'][idx], 3))
            self.anep_label_value_prj.setNum(round(self.updatedData.data['a_nepog_prj'][idx], 3))
            self.psi_label_value_prj.setNum(round(self.updatedData.data['psi_prj'][idx], 3))
            self.fv_label_value_prj.setNum(round(self.updatedData.data['v_wheel_prj'][idx], 3))
        else:
            self.fact_label_value.setNum(round(self.__calculation_result.calculated_task.data['vozv_fact'][idx], 3))
            self.prj_label_value.setNum(round(self.__calculation_result.calculated_task.data['vozv_prj'][idx], 3))
            self.anep_label_value_fact.setNum(round(self.__calculation_result.calculated_task.data['a_nepog_fact'][idx], 3))
            self.psi_label_value_fact.setNum(round(self.__calculation_result.calculated_task.data['psi_fact'][idx], 3))
            self.fv_label_value_fact.setNum(round(self.__calculation_result.calculated_task.data['v_wheel_fact'][idx], 3))
            self.anep_label_value_prj.setNum(round(self.__calculation_result.calculated_task.data['a_nepog_prj'][idx], 3))
            self.psi_label_value_prj.setNum(round(self.__calculation_result.calculated_task.data['psi_prj'][idx], 3))
            self.fv_label_value_prj.setNum(round(self.__calculation_result.calculated_task.data['v_wheel_prj'][idx], 3))

    def __getDataByPicket(self, col_name: str, picket: float) -> int:
        idx = self.__programTaskByPicketModel.getIndexByPicket(picket)
        return self.__calculation_result.calculated_task.data[col_name][idx]

    def __rightColumnWidget(self):
        vbox = QVBoxLayout()
        groupbox_top = QGroupBox()
        groupbox_vlayout = QVBoxLayout()
        groupbox_top.setLayout(groupbox_vlayout)
        groupbox_top.setTitle("Редактирование")
        groupbox_top.setStyleSheet("QGroupBox:title{margin-top: -10px}")
        self.reconstraction_button = QPushButton("Переустройство")
        self.reconstraction_button.setStyleSheet(focus_style)
        self.reconstraction_button.setProperty("optionsWindowPushButton", True)
        self.speed_button = QPushButton("Скорость")
        self.speed_button.setProperty("optionsWindowPushButton", True)
        groupbox_vlayout.addWidget(self.reconstraction_button)
        #groupbox_vlayout.addWidget(self.speed_button)
        self.reconstraction_button.clicked.connect(self.__handleReconstractionButton)
        self.speed_button.clicked.connect(self.__handleSpeedButton)
        self.results_button = QPushButton("Результаты")
        self.settings_button = QPushButton("Установки")
        self.escape_button = QPushButton("Выход (ESC)")
        self.escape_button.setStyleSheet(focus_style)
        self.escape_button.setProperty("optionsWindowPushButton", True)
        self.results_button.clicked.connect(self.__results_button)
        self.settings_button.clicked.connect(self.__settings_button)
        self.escape_button.clicked.connect(self.__escape_button)
        self.buttons = []
        self.buttons.append(self.reconstraction_button)
        self.buttons.append(self.speed_button)
        self.buttons.append(self.results_button)
        self.buttons.append(self.settings_button)
        self.buttons.append(self.escape_button)
        #
        # min & max values
        groupbox_min_max = QGroupBox()
        groupbox_min_max_layout = QVBoxLayout()
        groupbox_min_max.setLayout(groupbox_min_max_layout)
        value_style = "font: bold; font-size: 13pt; color:black; background-color:white"
        label_style = "font-size: 13pt;color:black;"
        corrections_min_label = QLabel("Исправл. min")
        corrections_min_label.setStyleSheet(label_style)
        #
        self.corrections_min_value = QLabel(str(round((self.corrections_min))))
        self.corrections_min_value.setStyleSheet(value_style)
        corrections_max_label = QLabel("Исправл. max")
        corrections_max_label.setStyleSheet(label_style)
        self.corrections_max_value = QLabel(str(round((self.corrections_max))))
        self.corrections_max_value.setStyleSheet(value_style)
        groupbox_min_max_layout.addWidget(corrections_min_label)
        groupbox_min_max_layout.addWidget(self.corrections_min_value)
        groupbox_min_max_layout.addWidget(corrections_max_label)
        groupbox_min_max_layout.addWidget(self.corrections_max_value)
        #
        vbox1 = QVBoxLayout()
        hbox1 = QHBoxLayout()
        hbox2 = QHBoxLayout()
        #
        groupbox_speed = QGroupBox()
        groupbox_speed_layout = QHBoxLayout()
        groupbox_speed.setLayout(groupbox_speed_layout)
        speed_label = QLabel("Скорость")
        speed_label.setStyleSheet(" font: bold; font-size: 12pt;")
        self.speed_sb = QComboBox()   #QSpinBox()
        self.speed_sb.setStyleSheet(focus_style)
        self.speed_sb.addItem(str(self.options.restrictions['segments'][0]['v_gruz']))    # 80
        self.speed_sb.addItem(str(self.options.restrictions['segments'][0]['v_pass']))    # 120
        font = self.speed_sb.font()
        font.setPointSize(18)
        self.speed_sb.setFont(font)
        groupbox_speed_layout.addWidget(speed_label)
        groupbox_speed_layout.addWidget(self.speed_sb)
        #
        value_style = "font: bold; font-size: 12pt;color:white;background-color:black"
        point_number_label = QLabel("Текущее\n положение")
        point_number_label.setStyleSheet("font: bold; font-size: 12pt;color:black")
        self.point_number_label_value = QLabel(str(self.options.start_picket.meters))
        self.point_number_label_value.setStyleSheet(value_style)
        hbox1.addWidget(point_number_label)
        hbox1.addWidget(self.point_number_label_value)
        #
        groupbox_bottom = QGroupBox()
        groupbox_bottom_layout = QVBoxLayout()
        groupbox_bottom.setLayout(groupbox_bottom_layout)
        groupbox_bottom_layout_hbox1 = QHBoxLayout()
        fact_label = QLabel("Натура")
        fact_label.setStyleSheet("font: bold; font-size: 12pt;color:blue")
        self.fact_label_value = QLabel(str(self.__getDataByPicket('vozv_fact', self.options.start_picket.meters)))
        self.fact_label_value.setStyleSheet(value_style)
        groupbox_bottom_layout_hbox1.addWidget(fact_label)
        groupbox_bottom_layout_hbox1.addWidget(self.fact_label_value)
        groupbox_bottom_layout_hbox2 = QHBoxLayout()
        prj_label = QLabel("Проект")
        prj_label.setStyleSheet("font: bold; font-size: 12pt;color:red")
        self.prj_label_value = QLabel(str(self.__getDataByPicket('vozv_prj', self.options.start_picket.meters)))
        self.prj_label_value.setStyleSheet(value_style)
        groupbox_bottom_layout_hbox2.addWidget(prj_label)
        groupbox_bottom_layout_hbox2.addWidget(self.prj_label_value)
        groupbox_bottom_layout.addLayout(groupbox_bottom_layout_hbox1)
        groupbox_bottom_layout.addLayout(groupbox_bottom_layout_hbox2)
        #
        corrections_label = QLabel("Исправл.")
        corrections_label.setStyleSheet(" font: bold; font-size: 12pt;")  # font: bold;
        self.corrections_label_value = QLabel(str(0))
        self.corrections_label_value.setStyleSheet(value_style)
        hbox2.addWidget(corrections_label)
        hbox2.addWidget(self.corrections_label_value)
        groupbox_bottom.setStyleSheet("background-color:white")
        vbox1.addLayout(hbox1)
        vbox1.addWidget(groupbox_bottom)
        vbox1.addLayout(hbox2)
        #
        groupbox_bottom1 = QGroupBox()
        groupbox_bottom1_layout = QVBoxLayout()
        groupbox_bottom1.setLayout(groupbox_bottom1_layout)
        groupbox_bottom1_layout_hbox1 = QHBoxLayout()
        anep_label = QLabel("Анеп")
        anep_label.setStyleSheet("font: bold; font-size: 12pt;color:blue")
        self.anep_label_value_fact = QLabel(str(self.__getDataByPicket('a_nepog_fact', self.options.start_picket.meters)))
        self.anep_label_value_fact.setStyleSheet(value_style)
        groupbox_bottom1_layout_hbox1.addWidget(anep_label)
        groupbox_bottom1_layout_hbox1.addWidget(self.anep_label_value_fact)
        groupbox_bottom1_layout_hbox2 = QHBoxLayout()
        psi_label = QLabel(chr(936) + ' (Пси)')
        psi_label.setStyleSheet("font: bold; font-size: 12pt;color:blue")
        self.psi_label_value_fact = QLabel(str(self.__getDataByPicket('psi_fact', self.options.start_picket.meters)))
        self.psi_label_value_fact.setStyleSheet(value_style)
        groupbox_bottom1_layout_hbox2.addWidget(psi_label)
        groupbox_bottom1_layout_hbox2.addWidget(self.psi_label_value_fact)
        groupbox_bottom1_layout.addLayout(groupbox_bottom1_layout_hbox1)
        groupbox_bottom1_layout.addLayout(groupbox_bottom1_layout_hbox2)
        groupbox_bottom1_layout_hbox3 = QHBoxLayout()
        fv_label = QLabel("Fv.")
        fv_label.setStyleSheet("font: bold; font-size: 12pt;color:blue")
        self.fv_label_value_fact = QLabel(str(self.__getDataByPicket('v_wheel_fact', self.options.start_picket.meters)))
        self.fv_label_value_fact.setStyleSheet(value_style)
        groupbox_bottom1_layout_hbox3.addWidget(fv_label)
        groupbox_bottom1_layout_hbox3.addWidget(self.fv_label_value_fact)
        groupbox_bottom1_layout.addLayout(groupbox_bottom1_layout_hbox3)
        #######################################################################
        groupbox_bottom2 = QGroupBox()
        groupbox_bottom2_layout = QVBoxLayout()
        groupbox_bottom2.setLayout(groupbox_bottom2_layout)
        groupbox_bottom2_layout_hbox1 = QHBoxLayout()
        anep_label = QLabel("Анеп")
        anep_label.setStyleSheet("font: bold; font-size: 12pt;color:red")
        self.anep_label_value_prj = QLabel(str(self.__getDataByPicket('a_nepog_prj', self.options.start_picket.meters)))
        self.anep_label_value_prj.setStyleSheet(value_style)
        groupbox_bottom2_layout_hbox1.addWidget(anep_label)
        groupbox_bottom2_layout_hbox1.addWidget(self.anep_label_value_prj)
        groupbox_bottom2_layout_hbox2 = QHBoxLayout()
        psi_label = QLabel(chr(936) + ' (Пси)')
        psi_label.setStyleSheet("font: bold; font-size: 12pt;color:red")
        self.psi_label_value_prj = QLabel(str(self.__getDataByPicket('psi_prj', self.options.start_picket.meters)))
        self.psi_label_value_prj.setStyleSheet(value_style)
        groupbox_bottom2_layout_hbox2.addWidget(psi_label)
        groupbox_bottom2_layout_hbox2.addWidget(self.psi_label_value_prj)
        groupbox_bottom2_layout.addLayout(groupbox_bottom2_layout_hbox1)
        groupbox_bottom2_layout.addLayout(groupbox_bottom2_layout_hbox2)
        groupbox_bottom2_layout_hbox3 = QHBoxLayout()
        fv_label = QLabel("Fv.")
        fv_label.setStyleSheet("font: bold; font-size: 12pt;color:red")
        self.fv_label_value_prj = QLabel(str(self.__getDataByPicket('v_wheel_prj', self.options.start_picket.meters)))
        self.fv_label_value_prj.setStyleSheet(value_style)
        groupbox_bottom2_layout_hbox3.addWidget(fv_label)
        groupbox_bottom2_layout_hbox3.addWidget(self.fv_label_value_prj)
        groupbox_bottom2_layout.addLayout(groupbox_bottom2_layout_hbox3)
        #
        #self.installEventFilter(self)
        ##########################################
        vbox.addWidget(groupbox_top)
        vbox.addStretch(1)
        vbox.addWidget(groupbox_min_max)
        #vbox.addWidget(self.results_button)
        #vbox.addStretch(1)
        #vbox.addWidget(self.settings_button)
        vbox.addStretch(5)
        vbox.addWidget(self.escape_button)
        vbox.addStretch(1)
        vbox.addWidget(groupbox_speed)
        vbox.addLayout(vbox1)
        vbox.addWidget(groupbox_bottom1)
        vbox.addWidget(groupbox_bottom2)
        return vbox
        # ======================= Окраска нажатой кнопки ==================================

    def __handleReconstractionButton(self):
        self.openLevelReconstructionSignal.emit(self.currentPicket)

    def __handleSpeedButton(self):
        self.openLevelSpeedSignal.emit(self.currentPicket)

    def __results_button(self):
        pass

    def __settings_button(self):
        pass

    def __escape_button(self):
        if self.updatedData:
            self.passDataSignal.emit(self.updatedData)
        self.levelMainSignal.emit('close')


